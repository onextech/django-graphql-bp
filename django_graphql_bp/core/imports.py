from django.conf import settings
from graphene_django import DjangoObjectType
from django.utils.module_loading import import_string


def get_user_node() -> DjangoObjectType:
    return import_string(settings.USER_NODE)


UserNode = get_user_node()
