from app.graphql.api import schema
from app.graphql.tests import GraphqlTestCase, Mutation, Query
from app.user.models import User
from graphene.test import Client


class SchemaTestCase(GraphqlTestCase):
    def setUp(self):
        super(SchemaTestCase, self).setUp()
        self.user = self.create_test_user('user', {'username': 'user'})
        self.user2 = self.create_test_user('user2', {'username': 'user2'})
        self.staff = self.create_test_user('staff', {'username': 'staff'})
        self.staff.is_staff = True
        self.staff.save()

    def get_create_user_mutation(self) -> Mutation:
        return Mutation('createUser', {'ok': '', 'validationErrors': ''}, {
            'email': self.get_user_email('createUser'),
            'password1': 'get_create_user_mutation',
            'password2': 'get_create_user_mutation'
        })

    def get_update_user_mutation(self) -> Mutation:
        return Mutation('updateUser', {'ok': '', 'validationErrors': ''}, {
            'pk': self.user.pk,
            'email': self.user.email,
            'name': 'get_create_user_mutation'
        })

    def get_delete_user_mutation(self) -> Mutation:
        return Mutation('deleteUser', {
            'ok': '',
            'node': {
                'isActive': ''
            }
        }, {'pk': self.user.pk})

    def get_login_user_mutation(self) -> Mutation:
        return Mutation('loginUser', {'ok': ''}, {'email': self.user.email, 'password': 'userpassword'})

    def get_logout_user_mutation(self) -> Mutation:
        return Mutation('logoutUser', {'ok': ''}, {})

    def get_current_user_query(self) -> Query:
        return Query('currentUser', {
            'pk': ''
        })

    # test createUser migration
    def test_create_user(self):
        self.create_mutation_success_test(User, self.get_create_user_mutation())

    # test updateUser migration
    def test_update_user_by_unauthorized_user(self):
        self.update_mutation_raised_error_test(
            User, self.get_update_user_mutation(), self.user, 'name', self.get_unauthorized_message())

    def test_update_user_by_not_owner(self):
        self.update_mutation_raised_error_test(
            User, self.get_update_user_mutation(), self.user, 'name', self.get_forbidden_access_message(),
            self.get_context_value(self.user2))

    def test_update_user_by_owner(self):
        self.update_mutation_success_test(
            User, self.get_update_user_mutation(), self.user, 'name', self.get_context_value(self.user))

    def test_update_user_by_staff(self):
        self.update_mutation_success_test(
            User, self.get_update_user_mutation(), self.user, 'name', self.get_context_value(self.staff))

    # test deleteUser migration
    def test_delete_user_by_unauthorized_user(self):
        self.update_mutation_raised_error_test(
            User, self.get_delete_user_mutation(), self.user, 'is_active', self.get_unauthorized_message())

    def test_delete_user_by_not_owner(self):
        self.update_mutation_raised_error_test(
            User, self.get_delete_user_mutation(), self.user, 'is_active', self.get_forbidden_access_message(),
            self.get_context_value(self.user2))

    def test_delete_user_by_owner(self):
        self.update_mutation_success_test(
            User, self.get_delete_user_mutation(), self.user, 'is_active', self.get_context_value(self.user))
    
    def test_delete_user_by_staff(self):
        self.update_mutation_success_test(
            User, self.get_delete_user_mutation(), self.user, 'is_active', self.get_context_value(self.staff))

    # test loginUser mutation
    def test_log_in(self):
        mutation = self.get_login_user_mutation()
        result = Client(schema).execute(mutation.get_result(), context_value=self.get_context_value())
        # TODO cannot test sessions with graphql schema?

    # test logoutUser mutation
    def test_logout_in(self):
        mutation = self.get_logout_user_mutation()
        result = Client(schema).execute(mutation.get_result(), context_value=self.get_context_value(self.user))
        # TODO cannot test sessions with graphql schema?

    # test currentUser query
    def test_current_user_by_unauthorized_user(self):
        query = self.get_current_user_query()
        result = Client(schema).execute(query.get_result(), context_value=self.get_context_value())
        self.assertIsNone(result['data'][query.get_name()], 'Check if user is not logged in')

    def test_current_user_by_authorized_user(self):
        query = self.get_current_user_query()
        result = Client(schema).execute(query.get_result(), context_value=self.get_context_value(self.user))
        self.assertIsNotNone(result['data'][query.get_name()], 'Check if user is logged in')
        self.assertEqual(
            self.get_operation_field_value(result, query.get_name(), 'pk'), self.user.pk,
            'Check if logged in user is correct')