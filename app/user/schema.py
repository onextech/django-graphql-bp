import graphene
from app.graphql.utils import DjangoPkInterface, Operations
from app.user.forms import CreateUserForm, UpdateUserForm
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql.execution.base import ResolveInfo


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        interfaces = (graphene.relay.Node, DjangoPkInterface)
        filter_fields = ['email', 'is_active']


class UserAccess(Operations.MutationAccess):
    @classmethod
    def get_model_from_input(cls, info: ResolveInfo, input: dict) -> User:
        return User.objects.get(pk=input.get('pk'))

    @classmethod
    def get_model_from_instance(cls, info: ResolveInfo, input: dict) -> User:
        return cls.get_instance(info, input)

    @classmethod
    def check_user_access(cls, info: ResolveInfo, input: dict, user: User):
        if not user.pk == info.context.user.pk:
            Operations.raise_forbidden_access_error()

    @classmethod
    def check_access(cls, info: ResolveInfo, input: dict):
        """ Only authorized user who is in staff or shop staff """
        if not info.context.user.is_authenticated:
            Operations.raise_unathorized_error()

        if not info.context.user.is_staff:
            if cls.is_create or cls.is_update:
                user_input = cls.get_model_from_input(info, input)
                cls.check_user_access(info, input, user_input)

            if cls.is_update or cls.is_delete:
                user_instance = cls.get_model_from_instance(info, input)
                cls.check_user_access(info, input, user_instance)


class CreateUser(Operations.MutationCreate, graphene.relay.ClientIDMutation):
    form = CreateUserForm
    is_create = True
    node = graphene.Field(UserNode)

    class Input:
        email = graphene.String(required=True)
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)

    @classmethod
    def after_save(cls, info: ResolveInfo, input: dict, form: CreateUserForm) -> 'CreateUser':
        form.instance.is_current_user = True
        return cls.validation_success(form)


class UpdateUser(Operations.MutationUpdate, UserAccess, graphene.relay.ClientIDMutation):
    form = UpdateUserForm
    is_update = True
    model = User
    node = graphene.Field(UserNode)

    class Input:
        pk = graphene.Int(required=True)
        email = graphene.String()
        is_active = graphene.Boolean()
        first_name = graphene.String()
        last_name = graphene.String()
        username = graphene.String()


class DeleteUser(Operations.MutationDelete, UserAccess, graphene.relay.ClientIDMutation):
    is_delete = True
    model = User
    node = graphene.Field(UserNode)

    class Input:
        pk = graphene.Int(required=True)

    @classmethod
    def delete(cls, info: ResolveInfo, input: dict, instance: User):
        instance.is_active = False
        instance.save()


class Query:
    current_user = graphene.Field(UserNode)
    users = DjangoFilterConnectionField(UserNode)

    def resolve_current_user(self, args: dict, context: WSGIRequest, info: ResolveInfo) -> User:
        return UserNode.get_node(context.user.id, context, info)

    def resolve_users(self, args, context, info) -> [User]:
        if context.user.is_staff:
            return User.objects.all()

        raise PermissionError('403 Forbidden Access')


class Mutation:
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()