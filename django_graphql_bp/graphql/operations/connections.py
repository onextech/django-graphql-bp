import graphene


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
