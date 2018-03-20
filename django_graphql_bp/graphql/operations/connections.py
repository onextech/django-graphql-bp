import graphene
from graphql.execution.base import ResolveInfo


class CountableConnection(graphene.Connection):
    total_count = graphene.Int()

    class Meta:
        abstract = True

    def resolve_total_count(self, info: ResolveInfo, **input: dict):
        return self.iterable.count()
