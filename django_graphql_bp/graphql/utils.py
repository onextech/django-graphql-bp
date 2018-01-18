import graphene, re
from django import forms
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django_filters import Filter, FilterSet
from functools import partial
from graphql.execution.base import ResolveInfo
from graphene_django.filter import DjangoFilterConnectionField


class DjangoPkInterface(graphene.Interface):
    """
    Exposes the Django model primary key
    """
    pk = graphene.Int(description='Primary key')

    def resolve_pk(self, info: ResolveInfo, **input: dict) -> int:
        return self.pk


class IntegerFilter(Filter):
    field_class = forms.IntegerField


class PkFilter(FilterSet):
    pk = IntegerFilter()


def sort_qs(model, args):
    """
    Adds `order_by`/sorting to a resolver
    :type model: django.models.Model
    :type args: dict
    :return: QuerySet
    """
    qs = model.objects.all()
    sort = args.get('sort')
    if sort:
        qs = qs.order_by(sort)
    return qs


def countable_connection_for_type(_type):
    """
    Implements totalCount field via Relay's built-in connections
    https://github.com/graphql-python/graphene-django/issues/162
    :param _type:
    :return:
    """

    class Connection(graphene.Connection):
        total_count = graphene.Int()

        class Meta:
            name = _type._meta.name + 'Connection'
            node = _type

        def resolve_total_count(self, args, context, info):
            return self.length

    return Connection


class ConnectionSearchVector:
    vector = None

    @classmethod
    def apply(cls, query: str, qs: QuerySet) -> QuerySet:
        if query:
            search_query = SearchQuery('')

            for query_word in query.split():
                search_query = search_query | SearchQuery(query_word)

            if cls.vector is None:
                raise NotImplementedError('Attribute "vector" of type dict must be implemented.')

            vector = None

            for field, weight in cls.vector.items():
                if not vector:
                    vector = SearchVector(field, weight=weight)
                else:
                    vector += SearchVector(field, weight=weight)

            if vector:
                qs = qs.annotate(search=vector, rank=SearchRank(vector, search_query)).filter(search=search_query)\
                    .order_by('-rank')

        return qs


class SearchConnectionField(DjangoFilterConnectionField):
    def __init__(self, type: type, fields=None, extra_filter_meta=None, filterset_class: type = None,
                 search_vector_class: ConnectionSearchVector = None, *args, **kwargs):
        self.search_vector_class = search_vector_class
        super(SearchConnectionField, self).__init__(
            type, fields, None, extra_filter_meta, filterset_class, *args, **kwargs)

    @classmethod
    def apply_search(cls, args: dict, qs: QuerySet, search_vector_class: ConnectionSearchVector) -> QuerySet:
        query = args.get('query', '')

        if search_vector_class:
            qs = search_vector_class.apply(query, qs)

        return qs

    @classmethod
    def apply_sort(cls, args: dict, qs: QuerySet) -> QuerySet:
        order = args.get('sort')

        if order:
            qs = qs.order_by(order)

        return qs

    @classmethod
    def connection_resolver(cls, resolver, connection, default_manager, max_limit, enforce_first_or_last,
                            filterset_class, filtering_args, search_vector_class, root, info, **args):
        qs = cls.get_query_set(args, default_manager, filterset_class, filtering_args)
        qs = cls.apply_search(args, qs, search_vector_class)
        qs = cls.apply_sort(args, qs)
        return super(DjangoFilterConnectionField, cls).connection_resolver(
            resolver, connection, qs, max_limit, enforce_first_or_last, root, info, **args)

    def get_resolver(self, parent_resolver):
        return partial(
            self.connection_resolver,
            parent_resolver,
            self.type,
            self.get_manager(),
            self.max_limit,
            self.enforce_first_or_last,
            self.filterset_class,
            self.filtering_args,
            self.search_vector_class
        )

    @classmethod
    def get_query_set(cls, args: dict, default_manager, filterset_class: type, filtering_args: dict) -> QuerySet:
        filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
        return filterset_class(data=filter_kwargs, queryset=default_manager.get_queryset()).qs


class Operations:
    FORBIDDEN_ACCESS_ERROR = '403 Forbidden Access'
    UNAUTHORIZED_ERROR = '401 Unauthorized'

    @staticmethod
    def raise_forbidden_access_error():
        raise PermissionError(Operations.FORBIDDEN_ACCESS_ERROR)

    @staticmethod
    def raise_unathorized_error():
        raise PermissionError(Operations.UNAUTHORIZED_ERROR)

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
        def mutate_and_get_payload(cls, root, info: ResolveInfo, **input: dict) -> 'Operations.MutationAbstract':
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
                Operations.raise_unathorized_error()

            if not info.context.user.is_staff:
                Operations.raise_forbidden_access_error()

    class MutationCreate(MutationAbstract):
        validation_errors = graphene.String()

        form = None  # Set form of django.forms.ModelForm type
        node = None  # Set node of graphene.Field(graphene_django.DjangoObjectType)

        @classmethod
        def validation_error(cls, form: ModelForm) -> 'Operations.MutationCreate':
            return cls(ok=False, node=form.instance, validation_errors=form.errors.as_json())

        @classmethod
        def validation_success(cls, form: ModelForm) -> 'Operations.MutationCreate':
            return cls(ok=True, node=form.instance)

        @classmethod
        def get_instance(cls, info: ResolveInfo, input: dict):
            return None

        @classmethod
        def validate_required_attributes(cls):
            cls.validate_required_attribute('form', forms.ModelForm)

        @classmethod
        def before_save(cls, info: ResolveInfo, input: dict, form: ModelForm) -> bool:
            return True

        @classmethod
        def save(cls, info: ResolveInfo, input: dict, form: ModelForm):
            form.save()

        @classmethod
        def after_save(cls, info: ResolveInfo, input: dict, form: ModelForm) -> 'Operations.MutationCreate':
            return cls.validation_success(form)

        @classmethod
        def validate_and_save_form(cls, info: ResolveInfo, input: dict, form: ModelForm) -> 'Operations.MutationCreate':
            if form.is_valid() and cls.before_save(info, input, form):
                cls.save(info, input, form)
                return cls.after_save(info, input, form)
            else:
                return cls.validation_error(form)

        @classmethod
        def get_form(cls, info: ResolveInfo, input: dict) -> ModelForm:
            instance = cls.get_instance(info, input)
            return cls.form(input, info.context.FILES, instance=instance)

        @classmethod
        def mutate_and_get_payload(cls, root, info: ResolveInfo, **input: dict) -> 'Operations.MutationCreate':
            super(Operations.MutationCreate, cls).mutate_and_get_payload(root, info, **input)
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
        def after_delete(cls, info: ResolveInfo, input: dict, instance: models.Model):
            """
            :rtype: Operations.MutationDelete
            """
            return cls(ok=True, pk=input.get('pk'), node=instance)

        @classmethod
        def delete(cls, info: ResolveInfo, input: dict, instance: models.Model):
            instance.delete()

        @classmethod
        def mutate_and_get_payload(cls, root, info: ResolveInfo, **input: dict) -> 'Operations.MutationDelete':
            super(Operations.MutationDelete, cls).mutate_and_get_payload(root, info, **input)
            instance = cls.get_instance(info, input)
            cls.delete(info, input, instance)
            return cls.after_delete(info, input, instance)

    class MutationSoftDelete(MutationDelete):
        is_deleted_attribute = 'is_deleted'

        @classmethod
        def delete(cls, info: ResolveInfo, input: dict, instance: models.Model):
            setattr(instance, cls.is_deleted_attribute, True)
            instance.save()
