import django_graphql_bp.user.schema, graphene
from graphene_django.debug import DjangoDebug


class UserQueries(
    django_graphql_bp.user.schema.Query,
    graphene.ObjectType
):
    node = graphene.relay.Node.Field()
    root = graphene.Field(lambda: UserQueries)
    debug = graphene.Field(DjangoDebug, name='__debug')

    hello = graphene.String(name=graphene.Argument(graphene.String, default_value="stranger"))

    def resolve_hello(self, args, context, info):
        return 'Hello ' + args['name']

    def resolve_root(self, args, context, info):
        """
        Re-expose the root query object. Workaround for the issue in Relay:
        https://github.com/facebook/relay/issues/112
        """
        return UserQueries()


class UserMutations(
    django_graphql_bp.user.schema.Mutation,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=UserQueries, mutation=UserMutations)
