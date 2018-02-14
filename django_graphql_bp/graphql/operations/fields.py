import graphene
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models.query import QuerySet
from functools import partial
from graphene_django.filter import DjangoFilterConnectionField


class OptionsInput(graphene.InputObjectType):
    key = graphene.Int(required=True)
    value = graphene.String(required=True)


class ConnectionSearchVector:
    vector = None

    @classmethod
    def apply(cls, query: str, qs: QuerySet) -> QuerySet:
        if query:
            search_query = SearchQuery('')

            for query_word in query.split():
                search_query = search_query | SearchQuery(query_word)

            if cls.vector is None:
                raise NotImplementedError('Attribute "vector" of type dict must be implemented.')

            vector = None

            for field, weight in cls.vector.items():
                if not vector:
                    vector = SearchVector(field, weight=weight)
                else:
                    vector += SearchVector(field, weight=weight)

            if vector:
                qs = qs.annotate(search=vector, rank=SearchRank(vector, search_query)).filter(search=search_query)\
                    .order_by('-rank')

        return qs


class SearchConnectionField(DjangoFilterConnectionField):
    def __init__(self, type: type, fields=None, extra_filter_meta=None, filterset_class: type = None,
                 search_vector_class: ConnectionSearchVector = None, *args, **kwargs):
        self.search_vector_class = search_vector_class
        super(SearchConnectionField, self).__init__(
            type, fields, None, extra_filter_meta, filterset_class, *args, **kwargs)

    @classmethod
    def apply_filters(cls, args: dict, qs: QuerySet) -> QuerySet:
        pk = args.get('pk', None)

        if pk:
            qs = qs.filter(pk=pk)

        return qs

    @classmethod
    def apply_search(cls, args: dict, qs: QuerySet, search_vector_class: ConnectionSearchVector) -> QuerySet:
        query = args.get('query', '')

        if search_vector_class:
            qs = search_vector_class.apply(query, qs)

        return qs

    @classmethod
    def apply_sort(cls, args: dict, qs: QuerySet) -> QuerySet:
        order = args.get('sort')

        if order:
            qs = qs.order_by(order)

        return qs

    @classmethod
    def connection_resolver(cls, resolver, connection, default_manager, max_limit, enforce_first_or_last,
                            filterset_class, filtering_args, search_vector_class, root, info, **args):
        qs = cls.get_query_set(args, default_manager, filterset_class, filtering_args)
        qs = cls.apply_filters(args, qs)
        qs = cls.apply_search(args, qs, search_vector_class)
        qs = cls.apply_sort(args, qs)
        return super(DjangoFilterConnectionField, cls).connection_resolver(
            resolver, connection, qs, max_limit, enforce_first_or_last, root, info, **args)

    def get_resolver(self, parent_resolver):
        return partial(
            self.connection_resolver,
            parent_resolver,
            self.type,
            self.get_manager(),
            self.max_limit,
            self.enforce_first_or_last,
            self.filterset_class,
            self.filtering_args,
            self.search_vector_class
        )

    @classmethod
    def get_query_set(cls, args: dict, default_manager, filterset_class: type, filtering_args: dict) -> QuerySet:
        filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
        return filterset_class(data=filter_kwargs, queryset=default_manager.get_queryset()).qs
