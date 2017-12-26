from app.graphql.tests import GraphqlTestCase, Mutation, Query
from django.contrib.auth.models import User


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
            'firstName': 'get_create_user_mutation'
        })

    def get_delete_user_mutation(self) -> Mutation:
        return Mutation('deleteUser', {
            'ok': '',
            'node': {
                'isActive': ''
            }
        }, {'pk': self.user.pk})

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
        self.create_mutation_success_test(User, self.get_create_user_mutation())

    # test updateUser migration
    def test_update_user_by_unauthorized_user(self):
        self.update_mutation_raised_error_test(
            User, self.get_update_user_mutation(), self.user, 'first_name', self.get_unauthorized_message())

    def test_update_user_by_not_owner(self):
        self.update_mutation_raised_error_test(
            User, self.get_update_user_mutation(), self.user, 'first_name', self.get_forbidden_access_message(),
            self.get_context_value(self.user2))

    def test_update_user_by_owner(self):
        self.update_mutation_success_test(
            User, self.get_update_user_mutation(), self.user, 'first_name', self.get_context_value(self.user))

    def test_update_user_by_staff(self):
        self.update_mutation_success_test(
            User, self.get_update_user_mutation(), self.user, 'first_name', self.get_context_value(self.staff))

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