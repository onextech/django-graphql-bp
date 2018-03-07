import graphene
from django_graphql_bp.graphql.operations import fields, interfaces, mutations, raise_forbidden_access_error, \
    raise_unathorized_error
from django_graphql_bp.user.forms import CreateUserForm, UpdateUserForm
from django_graphql_bp.user.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo


class UserNode(DjangoObjectType):
    class Meta:
        exclude_fields = ['password']
        filter_fields = ['email', 'is_active']
        interfaces = (graphene.relay.Node, interfaces.DjangoPkInterface)
        model = User


class UserAccess(mutations.MutationAccess):
    model = User

    @classmethod
    def check_user_access(cls, info: ResolveInfo, input: dict, user: User):
        if not user.pk == info.context.user.pk:
            raise_forbidden_access_error()

    @classmethod
    def check_access(cls, info: ResolveInfo, input: dict):
        """ Only authorized user who is in staff or owner """
        if not info.context.user.is_authenticated:
            raise_unathorized_error()

        if not info.context.user.is_staff:
            if cls.is_create or cls.is_update:
                user_input = cls.get_model_from_input(info, input)
                cls.check_user_access(info, input, user_input)

            if cls.is_update or cls.is_delete:
                user_instance = cls.get_model_from_instance(info, input)
                cls.check_user_access(info, input, user_instance)


class CreateUser(mutations.MutationCreate, graphene.relay.ClientIDMutation):
    form = CreateUserForm
    node = graphene.Field(UserNode)

    class Input:
        email = graphene.String(required=True)
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)

    @classmethod
    def after_save(cls, info: ResolveInfo, input: dict, form: CreateUserForm) -> 'CreateUser':
        form.instance.is_current_user = True
        return cls.validation_success(form)


class UpdateUser(mutations.MutationUpdate, UserAccess, graphene.relay.ClientIDMutation):
    form = UpdateUserForm
    is_update = True
    model = User
    node = graphene.Field(UserNode)

    class Input:
        pk = graphene.Int(required=True)
        email = graphene.String()
        is_active = graphene.Boolean()
        name = graphene.String()


class DeleteUser(mutations.MutationDelete, UserAccess, graphene.relay.ClientIDMutation):
    is_delete = True
    model = User
    node = graphene.Field(UserNode)

    class Input:
        pk = graphene.Int(required=True)

    @classmethod
    def delete(cls, info: ResolveInfo, input: dict, instance: User):
        instance.is_active = False
        instance.save()


class LoginUser(mutations.MutationAbstract, graphene.relay.ClientIDMutation):
    node = graphene.Field(UserNode)
    validation_errors = graphene.String()

    form = AuthenticationForm

    class Input:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    @classmethod
    def validation_error(cls, form: AuthenticationForm) -> 'LoginUser':
        return cls(ok=False, node=form.get_user(), validation_errors=form.errors.as_json())

    @classmethod
    def validation_success(cls, form: AuthenticationForm) -> 'LoginUser':
        return cls(ok=True, node=form.get_user())

    @classmethod
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input: dict) -> 'LoginUser':
        super(LoginUser, cls).mutate_and_get_payload(root, info, **input)
        form = AuthenticationForm(info.context, data={
            'username': input.get(User.USERNAME_FIELD, '').lower(),
            'password': input.get('password')
        })

        if form.is_valid():
            login(info.context, form.get_user())
            return cls.validation_success(form)
        else:
            return cls.validation_error(form)


class LogoutUser(mutations.MutationAccess, graphene.relay.ClientIDMutation):
    node = graphene.Field(UserNode)
    validation_errors = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input: dict) -> 'LogoutUser':
        user = info.context.user

        if user.is_authenticated:
            logout(info.context)
        else:
            user = None

        return cls(ok=True, node=user)


class Query:
    current_user = graphene.Field(UserNode)
    users = fields.SearchConnectionField(UserNode)

    def resolve_current_user(self, info: ResolveInfo, **input: dict) -> User:
        return UserNode.get_node(info, info.context.user.id)

    def resolve_users(self, info: ResolveInfo, **input: dict) -> [User]:
        if info.context.user.is_staff:
            return User.objects.all()

        raise_forbidden_access_error()


class Mutation:
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()

    login_user = LoginUser.Field()
    logout_user = LogoutUser.Field()
