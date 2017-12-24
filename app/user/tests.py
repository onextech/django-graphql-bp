from app.graphql.tests import GraphqlTestCase
from app.graphql.api import schema
from django.contrib.auth.models import User
from graphene.test import Client


class SchemaTestCase(GraphqlTestCase):
    def setUp(self):
        super(SchemaTestCase, self).setUp()

    def get_create_user_mutation(self) -> str:
        return '''
            mutation createUser { 
                createUser(input: {
                    email: "''' + self.get_user_email('get_create_user_mutation') + '''",
                    password: "get_create_user_mutation"
                }) {
                    ok
                }
            }
            '''

    # test createUser migration
    def test_create_user(self):
        count = User.objects.count()
        result = Client(schema).execute(
            self.get_create_user_mutation(), context_value=self.get_context_value())
        print(result)
        self.assert_mutation_success(result, 'createUser')
        self.assertEqual(User.objects.count(), count + 1, 'Check if user has been created')