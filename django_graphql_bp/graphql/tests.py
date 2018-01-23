import json, random
from django_graphql_bp.graphql.api import schema
from django_graphql_bp.graphql.utils import Operations
from django_graphql_bp.user.forms import CreateUserForm
from django_graphql_bp.user.models import User
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.http import HttpRequest
from django.test import TestCase
from graphene import Schema
from graphene.test import Client


class Operation:
    type = None

    def __init__(self, name, output: dict, input: dict = None):
        self.name = name
        self.output = output
        self.input = input

    def get_output_result(self, output, spaces: int = 2) -> str:
        result = ' { \n'
        spaces_string = ' ' * spaces

        for field, value in output.items():
            if type(value) is dict:
                result += spaces_string + '  ' + field + self.get_output_result(value, spaces + 2)
            else:
                result += spaces_string + '  ' + field + '\n'

        result += spaces_string + '} \n'
        return result

    def get_input_result(self) -> str:
        result = ''

        if self.input is not None:
            result += '(input: { \n'

            for field, value in self.input.items():
                if type(value) is str:
                    value = '"' + value + '"'

                if type(value) is list:
                    value = str(value).replace('\'', '"')

                result += '    ' + field + ': ' + str(value) + '\n'

            result += '  })'

        return result

    def get_name(self) -> str:
        return self.name

    def get_result(self) -> str:
        result = self.type + ' ' + self.name + ' { \n'
        result += '  ' + self.name
        result += self.get_input_result()
        result += self.get_output_result(self.output)
        result += '}'
        return result


class Query(Operation):
    type = 'query'


class Mutation(Operation):
    type = 'mutation'


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
        attributes['password1'] = username + 'password'
        attributes['password2'] = username + 'password'
        form = CreateUserForm(attributes)
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

    def get_mutation_node_attribute_value(self, result: dict, operation_name: str, attribute_name: str):
        return self.get_operation_field_value(result, operation_name, 'node')[attribute_name]

    def get_operation_field_value(self, result: dict, operation_name: str, attribute_name: str):
        return result['data'][operation_name][attribute_name]

    def get_random_price(self) -> str:
        return str(round(random.uniform(0.01, 9.99), 2))

    def get_random_qunatity(self) -> int:
        return int(round(random.uniform(1, 10)))

    def get_schema(self) -> Schema:
        return schema

    def get_unauthorized_message(self) -> str:
        return Operations.UNAUTHORIZED_ERROR

    def get_user_email(self, username) -> str:
        return settings.TEST_EMAIL_USERNAME + '+' + username + '@' + settings.TEST_EMAIL_DOMAIN

    def create_mutation_success_test(self, model_class: models.Model, mutation: Mutation, context: HttpRequest = None):
        count = model_class.objects.count()

        if context is None:
            context = self.get_context_value()

        result = Client(self.get_schema()).execute(mutation.get_result(), context_value=context)
        self.assert_mutation_success(result, mutation.get_name())
        self.assertEqual(
            model_class.objects.count(), count + 1, 'Check if ' + model_class.__name__ + ' has been created')
        return result

    def create_mutation_raised_error_test(self, model_class: models.Model, mutation: Mutation, error_message: str,
                                          context: HttpRequest = None):
        count = model_class.objects.count()

        if context is None:
            context = self.get_context_value()

        result = Client(self.get_schema()).execute(mutation.get_result(), context_value=context)
        self.assert_raised_error(result, error_message)
        self.assertEqual(
            model_class.objects.count(), count, 'Check if ' + model_class.__name__ + ' has not been created')
        return result

    def create_mutation_validation_error_test(self, model_class: models.Model, mutation: Mutation, field: str,
                                              error_message: str, context: HttpRequest = None):
        count = model_class.objects.count()

        if context is None:
            context = self.get_context_value()

        result = Client(self.get_schema()).execute(mutation.get_result(), context_value=context)
        self.assert_mutation_validation_error(result, mutation.get_name(), field, error_message)
        self.assertEqual(
            model_class.objects.count(), count, 'Check if ' + model_class.__name__ + ' has not been created')
        return result

    def update_mutation_success_test(self, model_class: models.Model, mutation: Mutation, model: models.Model,
                                     attribute: str, context: HttpRequest = None):
        count = model_class.objects.count()

        if context is None:
            context = self.get_context_value()

        result = Client(self.get_schema()).execute(mutation.get_result(), context_value=context)
        self.assert_mutation_success(result, mutation.get_name())
        self.assertEqual(
            model_class.objects.count(), count, 'Check if ' + model_class.__name__ + ' has not been created')
        self.assertNotEqual(
            getattr(model_class.objects.get(pk=model.pk), attribute),
            getattr(model, attribute), 'Check if ' + model.__class__.__name__ + '.' + attribute + ' has been updated')
        return result

    def update_mutation_raised_error_test(self, model_class: models.Model, mutation: Mutation, model: models.Model,
                                          attribute: str, error_message: str, context: HttpRequest = None):
        count = model_class.objects.count()

        if context is None:
            context = self.get_context_value()

        result = Client(self.get_schema()).execute(mutation.get_result(), context_value=context)
        self.assert_raised_error(result, error_message)
        self.assertEqual(
            model_class.objects.count(), count, 'Check if ' + model_class.__name__ + ' has not been created')
        self.assertEqual(
            getattr(model_class.objects.get(pk=model.pk), attribute),
            getattr(model, attribute),
            'Check if ' + model.__class__.__name__ + '.' + attribute + ' has not been updated')
        return result

    def delete_mutation_success_test(self, model_class: models.Model, mutation: Mutation, context: HttpRequest = None):
        count = model_class.objects.count()

        if context is None:
            context = self.get_context_value()

        result = Client(self.get_schema()).execute(mutation.get_result(), context_value=context)
        self.assert_mutation_success(result, mutation.get_name())
        self.assertEqual(
            model_class.objects.count(), count - 1, 'Check if ' + model_class.__name__ + ' has been removed')
        return result

    def delete_mutation_raised_error_test(self, model_class: models.Model, mutation: Mutation, error_message: str,
                                          context: HttpRequest = None):
        count = model_class.objects.count()

        if context is None:
            context = self.get_context_value()

        result = Client(self.get_schema()).execute(mutation.get_result(), context_value=context)
        self.assert_raised_error(result, error_message)
        self.assertEqual(
            model_class.objects.count(), count, 'Check if ' + model_class.__name__ + ' has not been removed')
        return result

    def query_raised_error_test(self, query: Query, error_message: str, context: HttpRequest = None):
        if context is None:
            context = self.get_context_value()

        result = Client(self.get_schema()).execute(query.get_result(), context_value=context)
        self.assert_raised_error(result, error_message)

    def query_collection_success_test(self, query: Query, model_class: models.Model, context: HttpRequest = None):
        if context is None:
            context = self.get_context_value()

        result = Client(self.get_schema()).execute(query.get_result(), context_value=context)
        self.assert_operation_no_errors(result)
        edges = self.get_operation_field_value(result, query.get_name(), 'edges')
        self.assertEqual(len(edges), model_class.objects.count(), 'Check if query has returned full set.')