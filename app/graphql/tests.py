import json, random
from app.user.forms import UserCreationForm
from app.graphql.utils import Operations
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest
from django.test import TestCase


class GraphqlTestCase(TestCase):
    def assert_raised_error(self, result: dict, error_message: str):
        self.assert_operation_errors(result)
        self.assertEqual(result['errors'][0]['message'], error_message, 'Check if "' + error_message + '" among errors')

    def assert_mutation_success(self, result: dict, operation_name: str):
        self.assert_operation_no_errors(result)
        self.assertTrue(self.get_operation_field_value(result, operation_name, 'ok'),
                        'Check if mutation returned ok = True')

    def assert_mutation_validation_error(self, result: dict, operation_name: str, field_name: str, error_message: str):
        self.assert_operation_no_errors(result)
        self.assertFalse(
            self.get_operation_field_value(result, operation_name, 'ok'), 'Check if mutation returned ok = False')
        self.assertEqual(
            json.loads(
                self.get_operation_field_value(result, operation_name, 'validationErrors'))[field_name][0]['message'],
            error_message, 'Check if "' + error_message + '" among validation errors')

    def assert_mutation_multiple_validation_error(self, result: dict, operation_name: str, field_name: str, error_message: str):
        self.assert_operation_no_errors(result)
        self.assertFalse(
            self.get_operation_field_value(result, operation_name, 'ok'), 'Check if mutation returned ok = False')
        self.assertEqual(
            json.loads(self.get_operation_field_value(result, operation_name, 'validationErrors'))[field_name][0],
            error_message, 'Check if "' + error_message + '" among validation errors')

    def assert_operation_no_errors(self, result: dict):
        self.assertFalse('errors' in result.keys(), 'Check if mutation has not returned any errors')

    def assert_operation_errors(self, result: dict):
        self.assertTrue('errors' in result.keys(), 'Check if mutation has returned any errors')

    def assert_query_field_equal(self, result: dict, operation_name: str, field_name: str, value) -> None:
        self.assertEqual(self.get_operation_field_value(result, operation_name, field_name), value,
                         'Check if data.' + field_name + ' = ' + str(value))

    def create_test_user(self, username, attributes: dict) -> User:
        attributes['email'] = self.get_user_email(username)
        attributes['password'] = username
        form = UserCreationForm(attributes)
        form.save()
        return form.instance

    def get_context_value(self, user=AnonymousUser(), files=None) -> HttpRequest:
        """
        :type user: User | AnonymousUser
        :param files: Filename of file from saleor.graphql.test_files folder e.g. "members_sheet.csv"
        :type files: dict | None
        """
        if files is None:
            files = {}

        context = HttpRequest()
        context.user = user
        context.FILES = {}

        test_files_folder = settings.PROJECT_ROOT + '/saleor/graphql/test_files/'

        for key, file in files.items():
            context.FILES.update({key: UploadedFile(open(test_files_folder + file, 'rb'))})

        return context

    def get_forbidden_access_message(self) -> str:
        return Operations.FORBIDDEN_ACCESS_ERROR

    def get_is_test_offline(self) -> bool:
        return settings.TEST_OFFLINE

    def get_unauthorized_message(self) -> str:
        return Operations.UNAUTHORIZED_ERROR

    def get_mutation_node_attribute_value(self, result: dict, operation_name: str, attribute_name: str):
        return self.get_operation_field_value(result, operation_name, 'node')[attribute_name]

    def get_operation_field_value(self, result: dict, operation_name: str, attribute_name: str):
        return result['data'][operation_name][attribute_name]

    def get_random_price(self) -> str:
        return str(round(random.uniform(0.01, 9.99), 2))

    def get_random_qunatity(self) -> int:
        return int(round(random.uniform(1, 10)))

    def get_user_email(self, username) -> str:
        return settings.TEST_EMAIL_USERNAME + '+' + username + '@' + settings.TEST_EMAIL_DOMAIN
