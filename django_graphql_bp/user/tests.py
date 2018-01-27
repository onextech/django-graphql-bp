from django_graphql_bp.graphql.tests import constructors, cases
from django_graphql_bp.user.models import User
from graphene.test import Client


class UserTestCase(cases.OperationTestCase):
    model_class = User

    def setUp(self):
        super(UserTestCase, self).setUp()
        self.user = self.create_test_user('user', {'username': 'user'})
        self.user2 = self.create_test_user('user2', {'username': 'user2'})
        self.staff = self.create_test_user('staff', {'username': 'staff'})
        self.staff.is_staff = True
        self.staff.save()


class CreateUserTestCase(UserTestCase, cases.MutationTestCase):
    def get_mutation(self) -> constructors.Mutation:
        return constructors.Mutation('createUser', {'ok': '', 'validationErrors': ''}, {
            'email': self.get_user_email('createUser'),
            'password1': 'get_create_user_mutation',
            'password2': 'get_create_user_mutation'
        })

    def test_create_user(self):
        self.create_success_test()


class UpdateUserTestCase(UserTestCase, cases.MutationTestCase):
    def get_mutation(self) -> constructors.Mutation:
        return constructors.Mutation('updateUser', {'ok': '', 'validationErrors': ''}, {
            'pk': self.user.pk,
            'email': self.user.email,
            'name': 'get_create_user_mutation'
        })

    def test_update_user_by_unauthorized_user(self):
        self.update_raised_error_test(self.user, 'name', self.get_unauthorized_message())

    def test_update_user_by_not_owner(self):
        self.update_raised_error_test(
            self.user, 'name', self.get_forbidden_access_message(), self.get_context_value(self.user2))

    def test_update_user_by_owner(self):
        self.update_success_test(self.user, 'name', self.get_context_value(self.user))

    def test_update_user_by_staff(self):
        self.update_success_test(self.user, 'name', self.get_context_value(self.staff))


class DeleteUserTestCase(UserTestCase, cases.MutationTestCase):
    def get_mutation(self) -> constructors.Mutation:
        return constructors.Mutation('deleteUser', {'ok': '', 'node': {'isActive': ''}}, {'pk': self.user.pk})

    def test_delete_user_by_unauthorized_user(self):
        self.update_raised_error_test(self.user, 'is_active', self.get_unauthorized_message())

    def test_delete_user_by_not_owner(self):
        self.update_raised_error_test(
            self.user, 'is_active', self.get_forbidden_access_message(), self.get_context_value(self.user2))

    def test_delete_user_by_owner(self):
        self.update_success_test(self.user, 'is_active', self.get_context_value(self.user))

    def test_delete_user_by_staff(self):
        self.update_success_test(self.user, 'is_active', self.get_context_value(self.staff))


class LoginUserTestCase(UserTestCase, cases.MutationTestCase):
    def get_mutation(self) -> constructors.Mutation:
        return constructors.Mutation('loginUser', {'ok': ''}, {'email': self.user.email, 'password': 'userpassword'})

    def test_log_in(self):
        mutation = self.get_mutation()
        result = Client(self.get_schema()).execute(mutation.get_result(), context_value=self.get_context_value())
        # TODO cannot test sessions with graphql schema?


class LogoutUserTestCase(UserTestCase, cases.MutationTestCase):
    def get_mutation(self) -> constructors.Mutation:
        return constructors.Mutation('logoutUser', {'ok': ''}, {})

    def test_logout_in(self):
        mutation = self.get_mutation()
        result = Client(
            self.get_schema()).execute(mutation.get_result(), context_value=self.get_context_value(self.user))
        # TODO cannot test sessions with graphql schema?


class CurrentUserTestCase(UserTestCase, cases.QueryTestCase):
    def get_query(self) -> constructors.Query:
        return constructors.Query('currentUser', {'pk': ''})

    def test_current_user_by_unauthorized_user(self):
        query = self.get_query()
        result = Client(self.get_schema()).execute(query.get_result(), context_value=self.get_context_value())
        self.assertIsNone(result['data'][query.get_name()], 'Check if user is not logged in')

    def test_current_user_by_authorized_user(self):
        query = self.get_query()
        result = Client(self.get_schema()).execute(query.get_result(), context_value=self.get_context_value(self.user))
        self.assertIsNotNone(result['data'][query.get_name()], 'Check if user is logged in')
        self.assertEqual(
            self.get_operation_field_value(result, query.get_name(), 'pk'), self.user.pk,
            'Check if logged in user is correct')


class UsersTestCase(UserTestCase, cases.QueryTestCase):
    def get_query(self) -> constructors.Query:
        return constructors.Query('users', {
            'edges': {
                'node': {
                    'pk': ''
                }
            }
        })

    def test_users_by_unauthorized_user(self):
        self.raised_error_test(self.get_forbidden_access_message())

    def test_users_by_not_staff(self):
        self.raised_error_test(self.get_forbidden_access_message(), self.get_context_value(self.user))

    def test_users_by_staff(self):
        self.collection_success_test(self.get_context_value(self.staff))