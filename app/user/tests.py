from app.graphql.tests import GraphqlTestCase, Mutation, Query
from app.graphql.api import schema
from django.contrib.auth.models import User
from graphene.test import Client


class SchemaTestCase(GraphqlTestCase):
    def setUp(self):
        super(SchemaTestCase, self).setUp()

    def get_create_user_mutation(self) -> Mutation:
        return Mutation('createUser', {'ok': ''}, {
            'email': self.get_user_email('get_create_user_mutation'),
            'password': 'get_create_user_mutation'
        })

    def get_current_user_query(self) -> Query:
        return Query('currentUser', {
            'companyMemberships': {
                'edges': {
                    'node': {
                        'pk': '',
                        'points': '',
                        'availableRewards': {
                            'edges': {
                                'node': {
                                    'pk': ''
                                }
                            }
                        }
                    }
                }
            }
        })

    # test createUser migration
    def test_create_user(self):
        count = User.objects.count()
        mutation = self.get_create_user_mutation()
        result = Client(schema).execute(
            mutation.get_result(), context_value=self.get_context_value())
        self.assert_mutation_success(result, mutation.get_name())
        self.assertEqual(User.objects.count(), count + 1, 'Check if user has been created')