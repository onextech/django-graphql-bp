import graphene
from app.graphql.utils import DjangoPkInterface, Meta, Operations
from app.user.forms import UserCreationForm
from django.conf import settings
from django.contrib.auth import get_user_model, forms
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql.execution.base import ResolveInfo


class UserNode(DjangoObjectType):
    class Meta:
        model = get_user_model()
        interfaces = (graphene.relay.Node, DjangoPkInterface)
        filter_fields = ['email', 'is_active']

    @classmethod
    def get_node(cls, id, context, info):
        """
        To prevent confidential user information from being
        queried externally. Only the user or an admin can
        make queries on a user node.
        """
        user = super(UserNode, cls).get_node(id, context, info)
        if (context.user.id and user.id == context.user.id) or context.user.is_staff:
            return user
        else:
            return None

    def resolve_current_enquiry(self, args, context, info):
        """
        :type args: dict
        :type context: django.core.handlers.wsgi.WSGIRequest
        :type info: graphql.execution.base.ResolveInfo
        :rtype: saleor.enquiry.models.Enquiry | None
        """
        return self.enquiries.filter(is_submitted=False).first()

    def resolve_past_enquiries(self, args, context, info):
        """
        :type args: dict
        :type context: django.core.handlers.wsgi.WSGIRequest
        :type info: graphql.execution.base.ResolveInfo
        :rtype: list[saleor.enquiry.models.Enquiry]
        """
        return self.enquiries.filter(is_submitted=True).all()


class UserMeta(Meta):
    # @TODO find a way to inherit Input fields
    fields = {
        'email': graphene.String(required=True),
        'password': graphene.String(required=True)
    }


class CreateUser(Operations.MutationCreate, graphene.relay.ClientIDMutation):
    form = UserCreationForm
    node = graphene.Field(UserNode)

    class Input:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    @classmethod
    def after_save(cls, input: dict, context: WSGIRequest, form: UserCreationForm) -> Operations.MutationCreate:
        form.instance.is_current_user = True
        return cls.validation_success(form)


class Query:
    current_user = graphene.Field(UserNode)
    users = DjangoFilterConnectionField(UserNode)

    def resolve_current_user(self, args: dict, context: WSGIRequest, info: ResolveInfo) -> User:
        return UserNode.get_node(context.user.id, context, info)

    def resolve_users(self, args, context, info) -> [User]:
        if context.user.is_staff:
            return get_user_model().objects.all()

        raise PermissionError('403 Forbidden Access')


class Mutation:
    create_user = CreateUser.Field()