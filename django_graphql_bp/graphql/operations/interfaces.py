import graphene
from graphql.execution.base import ResolveInfo


class DjangoPkInterface(graphene.Interface):
    """
    Exposes the Django model primary key
    """
    pk = graphene.Int(description='Primary key')

    def resolve_pk(self, info: ResolveInfo, **input: dict) -> int:
        return self.pk
