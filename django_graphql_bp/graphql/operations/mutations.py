import graphene, re
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django_graphql_bp.graphql.operations import raise_forbidden_access_error, raise_unathorized_error
from graphql.execution.base import ResolveInfo


class MutationAbstract:
    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    def check_access(cls, info: ResolveInfo, input: dict):
        pass

    @classmethod
    def get_context_file_by_name(cls, context: WSGIRequest, name: str) -> InMemoryUploadedFile:
        files = cls.get_context_files_by_name(context, name)

        if not len(files):
            raise PermissionError('Spreadsheet file should be posted under "{}" name.'.format(name))

        return files.pop()

    @classmethod
    def get_context_files_by_name(cls, context: WSGIRequest, name: str) -> [InMemoryUploadedFile]:
        files = []
        expression = re.compile(name + '.[0-9]+.originFileObj')

        for key, file in context.FILES.items():
            if expression.match(key):
                files.append(file)

        return files

    @classmethod
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input: dict) -> 'MutationAbstract':
        cls.check_access(info, input)
        cls.validate_required_attributes()
        return cls()

    @classmethod
    def get_file_extension(cls, file: InMemoryUploadedFile, allowed_extension=None) -> str:
        """
        :param allowed_extension: set list of allowed extensions if validation required
        :type allowed_extension: list | None
        """
        filename = file.name
        extension = filename.split('.')[-1]

        if allowed_extension and extension not in allowed_extension:
            raise NameError('File extension should be: {}.'.format(', '.join(allowed_extension)))

        return extension

    @classmethod
    def validate_required_attribute(cls, attribute: str, base_type: object):
        if getattr(cls, attribute) is None:
            raise ValidationError(
                'Attribute %s is required and should be an instance of class %s' % (attribute, type(base_type)))

    @classmethod
    def validate_required_attributes(cls):
        pass


class MutationAccess(MutationAbstract):
    is_create = False
    is_update = False
    is_delete = False
    model = None

    @classmethod
    def get_model_from_input(cls, info: ResolveInfo, input: dict) -> models.Model:
        return cls.model.objects.get(pk=input.get('pk'))

    @classmethod
    def get_model_from_instance(cls, info: ResolveInfo, input: dict) -> models.Model:
        return cls.get_instance(info, input)

    @classmethod
    def check_access(cls, info: ResolveInfo, input: dict):
        """ Only authorized user who is in staff """
        if not info.context.user.is_authenticated:
            raise_unathorized_error()

        if not info.context.user.is_staff:
            raise_forbidden_access_error()


class MutationCreate(MutationAbstract):
    validation_errors = graphene.String()

    form = None  # Set form of django.forms.ModelForm type
    node = None  # Set node of graphene.Field(graphene_django.DjangoObjectType)

    @classmethod
    def validation_error(cls, form: forms.ModelForm) -> 'MutationCreate':
        return cls(ok=False, node=form.instance, validation_errors=form.errors.as_json())

    @classmethod
    def validation_success(cls, form: forms.ModelForm) -> 'MutationCreate':
        return cls(ok=True, node=form.instance)

    @classmethod
    def get_instance(cls, info: ResolveInfo, input: dict):
        return None

    @classmethod
    def validate_required_attributes(cls):
        cls.validate_required_attribute('form', forms.ModelForm)

    @classmethod
    def before_save(cls, info: ResolveInfo, input: dict, form: forms.ModelForm) -> bool:
        return True

    @classmethod
    def save(cls, info: ResolveInfo, input: dict, form: forms.ModelForm):
        form.save()

    @classmethod
    def after_save(cls, info: ResolveInfo, input: dict, form: forms.ModelForm) -> 'MutationCreate':
        return cls.validation_success(form)

    @classmethod
    def validate_and_save_form(cls, info: ResolveInfo, input: dict, form: forms.ModelForm) -> 'MutationCreate':
        if form.is_valid() and cls.before_save(info, input, form):
            cls.save(info, input, form)
            return cls.after_save(info, input, form)
        else:
            return cls.validation_error(form)

    @classmethod
    def get_form(cls, info: ResolveInfo, input: dict) -> forms.ModelForm:
        instance = cls.get_instance(info, input)
        return cls.form(input, info.context.FILES, instance=instance)

    @classmethod
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input: dict) -> 'MutationCreate':
        super(MutationCreate, cls).mutate_and_get_payload(root, info, **input)
        cls.validate_required_attributes()
        return cls.validate_and_save_form(info, input, cls.get_form(info, input))


class MutationUpdate(MutationCreate):
    model = None  # Set model of django.db.models.Model type

    @classmethod
    def validate_required_attributes(cls):
        cls.validate_required_attribute('form', forms.ModelForm)
        cls.validate_required_attribute('model', models.Model)

    @classmethod
    def get_instance(cls, info: ResolveInfo, input: dict) -> models.Model:
        return cls.model.objects.get(pk=input.get('pk'))


class MutationDelete(MutationAbstract):
    instance = None
    model = None  # Set model of django.db.models.Model type
    node = None  # Set node of graphene.Field(graphene_django.DjangoObjectType)
    pk = graphene.Int()  # Need to return pk for client UI to update cache

    @classmethod
    def validate_required_attributes(cls):
        cls.validate_required_attribute(attribute='model', base_type=models.Model)

    @classmethod
    def get_instance(cls, info: ResolveInfo, input: dict) -> models.Model:
        return cls.model.objects.get(pk=input.get('pk'))

    @classmethod
    def after_delete(cls, info: ResolveInfo, input: dict, instance: models.Model) -> 'MutationDelete':
        return cls(ok=True, pk=input.get('pk'), node=instance)

    @classmethod
    def delete(cls, info: ResolveInfo, input: dict, instance: models.Model):
        instance.delete()

    @classmethod
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input: dict) -> 'MutationDelete':
        super(MutationDelete, cls).mutate_and_get_payload(root, info, **input)
        instance = cls.get_instance(info, input)
        cls.delete(info, input, instance)
        return cls.after_delete(info, input, instance)


class MutationSoftDelete(MutationDelete):
    is_deleted_attribute = 'is_deleted'

    @classmethod
    def delete(cls, info: ResolveInfo, input: dict, instance: models.Model):
        setattr(instance, cls.is_deleted_attribute, True)
        instance.save()
