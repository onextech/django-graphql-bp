import graphene
from django_graphql_bp.graphql.operations import interfaces
from django_graphql_bp.user.models import User
from graphene_django import DjangoObjectType


class UserNode(DjangoObjectType):
    class Meta:
        exclude_fields = ['password']
        filter_fields = ['email', 'is_active']
        interfaces = (graphene.relay.Node, interfaces.DjangoPkInterface)
        model = User
