import app.user.schema, graphene
from graphene_django.debug import DjangoDebug


class Queries(
    app.user.schema.Query,
    graphene.ObjectType
):
    node = graphene.relay.Node.Field()
    root = graphene.Field(lambda: Queries)
    debug = graphene.Field(DjangoDebug, name='__debug')

    hello = graphene.String(name=graphene.Argument(graphene.String, default_value="stranger"))

    def resolve_hello(self, args, context, info):
        return 'Hello ' + args['name']

    def resolve_root(self, args, context, info):
        """
        Re-expose the root query object. Workaround for the issue in Relay:
        https://github.com/facebook/relay/issues/112
        """
        return Queries()


class Mutations(
    app.user.schema.Mutation,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Queries, mutation=Mutations)
