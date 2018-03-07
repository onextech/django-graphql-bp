import json, random
from django_graphql_bp.graphql.operations import FORBIDDEN_ACCESS_ERROR, UNAUTHORIZED_ERROR
from django_graphql_bp.graphql.tests import constructors
from django_graphql_bp.user.forms import CreateUserForm
from django_graphql_bp.user.models import User
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from django.http import HttpRequest
from django.test import TestCase
from django.utils.module_loading import import_string
from graphene import Schema
from graphene.test import Client


class OperationTestCase(TestCase):
    def get_data(self, context: HttpRequest, args: dict):
        if context is None:
            context = self.get_context_value()

        if args is None:
            args = {}

        return context, args

    def assert_operation_errors(self, result: dict):
        self.assertTrue('errors' in result.keys(), 'Check if mutation has returned any errors')

    def assert_operation_no_errors(self, result: dict):
        self.assertFalse('errors' in result.keys(), 'Check if mutation has not returned any errors')

    def assert_raised_error(self, result: dict, error_message: str):
        self.assert_operation_errors(result)
        self.assertEqual(result['errors'][0]['message'], error_message, 'Check if "' + error_message + '" among errors')

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
        :param files: {key => name of file from settings.TEST_FILES_FOLDER folder)} e.g. {'image': 'picture.png'}
        :type files: dict | None
        """
        if files is None:
            files = {}

        context = HttpRequest()
        context.user = user
        context.FILES = {}

        test_files_folder = settings.PROJECT_ROOT + '/' + settings.TEST_FILES_FOLDER + '/'

        for key, file in files.items():
            file = open(test_files_folder + file, 'rb')
            context.FILES.update({key: SimpleUploadedFile(file.name, file.read())})

        return context

    def get_forbidden_access_message(self) -> str:
        return FORBIDDEN_ACCESS_ERROR

    def get_is_test_offline(self) -> bool:
        return settings.TEST_OFFLINE

    def get_operation_field_value(self, result: dict, operation_name: str, attribute_name: str):
        return result['data'][operation_name][attribute_name]

    def get_random_price(self) -> float:
        return float(round(random.uniform(0.01, 9.99), 2))

    def get_random_qunatity(self) -> int:
        return int(round(random.uniform(1, 10)))

    def get_schema(self) -> Schema:
        return import_string(settings.GRAPHENE['SCHEMA'])

    def get_unauthorized_message(self) -> str:
        return UNAUTHORIZED_ERROR

    def get_user_email(self, username) -> str:
        return settings.TEST_EMAIL_USERNAME + '+' + username + '@' + settings.TEST_EMAIL_DOMAIN


class MutationTestCase(OperationTestCase):
    model_class = None  # implement to use CRUD tests

    def assert_multiple_validation_error(self, result: dict, field_name: str, error_message: str):
        self.assert_operation_no_errors(result)
        self.assertFalse(
            self.get_operation_field_value(result, self.get_mutation().get_name(), 'ok'),
            'Check if mutation returned ok = False')
        errors = self.get_operation_field_value(result, self.get_mutation().get_name(), 'validationErrors')
        self.assertEqual(
            json.loads(errors)[field_name][0], error_message,
            'Check if "' + error_message + '" among validation errors')

    def assert_success(self, result: dict):
        self.assert_operation_no_errors(result)
        self.assertTrue(
            self.get_operation_field_value(result, self.get_mutation().get_name(), 'ok'),
            'Check if mutation returned ok = True')

    def assert_validation_error(self, result: dict, field_name: str, error_message: str):
        self.assert_operation_no_errors(result)
        self.assertFalse(
            self.get_operation_field_value(result, self.get_mutation().get_name(), 'ok'),
            'Check if mutation returned ok = False')
        errors = self.get_operation_field_value(result, self.get_mutation().get_name(), 'validationErrors')
        self.assertEqual(
            json.loads(errors)[field_name][0]['message'],
            error_message, 'Check if "' + error_message + '" among validation errors')

    def create_success_test(self, context: HttpRequest = None, args: dict = None):
        count = self.model_class.objects.count()
        context, args = self.get_data(context, args)
        result = Client(self.get_schema()).execute(self.get_mutation(**args).get_result(), context_value=context)
        self.assert_success(result)
        self.assertEqual(
            self.model_class.objects.count(), count + 1, 'Check if ' + self.model_class.__name__ + ' has been created')
        return result

    def create_raised_error_test(self, error_message: str, context: HttpRequest = None, args: dict = None):
        count = self.model_class.objects.count()
        context, args = self.get_data(context, args)
        result = Client(self.get_schema()).execute(self.get_mutation(**args).get_result(), context_value=context)
        self.assert_raised_error(result, error_message)
        self.assertEqual(
            self.model_class.objects.count(), count, 'Check if ' + self.model_class.__name__ + ' has not been created')
        return result

    def create_validation_error_test(self, field: str, error_message: str, context: HttpRequest = None,
                                     args: dict = None):
        count = self.model_class.objects.count()
        context, args = self.get_data(context, args)
        result = Client(self.get_schema()).execute(self.get_mutation(**args).get_result(), context_value=context)
        self.assert_validation_error(result, field, error_message)
        self.assertEqual(
            self.model_class.objects.count(), count, 'Check if ' + self.model_class.__name__ + ' has not been created')
        return result

    def delete_success_test(self, context: HttpRequest = None, args: dict = None):
        count = self.model_class.objects.count()
        context, args = self.get_data(context, args)
        result = Client(self.get_schema()).execute(self.get_mutation(**args).get_result(), context_value=context)
        self.assert_success(result)
        self.assertEqual(
            self.model_class.objects.count(), count - 1, 'Check if ' + self.model_class.__name__ + ' has been removed')
        return result

    def delete_raised_error_test(self, error_message: str, context: HttpRequest = None, args: dict = None):
        count = self.model_class.objects.count()
        context, args = self.get_data(context, args)
        result = Client(self.get_schema()).execute(self.get_mutation(**args).get_result(), context_value=context)
        self.assert_raised_error(result, error_message)
        self.assertEqual(
            self.model_class.objects.count(), count, 'Check if ' + self.model_class.__name__ + ' has not been removed')
        return result

    def get_attribute_value(self, model: models.Model, attribute: str):
        value = getattr(model, attribute)

        if type(value) is ImageFieldFile:
            value = str(value)

        return value

    def get_mutation(self, **kwargs: dict) -> constructors.Mutation:
        raise NotImplementedError('Function get_mutation for MutationTestCase class should be implemented.')

    def get_node_attribute_value(self, result: dict, attribute_name: str):
        return self.get_operation_field_value(result, self.get_mutation().get_name(), 'node')[attribute_name]

    def update_success_test(self, model: models.Model, attribute: str, context: HttpRequest = None, args: dict = None):
        count = self.model_class.objects.count()
        context, args = self.get_data(context, args)
        result = Client(self.get_schema()).execute(self.get_mutation(**args).get_result(), context_value=context)
        self.assert_success(result)
        self.assertEqual(
            self.model_class.objects.count(), count, 'Check if ' + self.model_class.__name__ + ' has not been created')
        self.assertNotEqual(
            self.get_attribute_value(self.model_class.objects.get(pk=model.pk), attribute),
            self.get_attribute_value(model, attribute),
            'Check if ' + model.__class__.__name__ + '.' + attribute + ' has been updated')
        return result

    def update_raised_error_test(self, model: models.Model, attribute: str, error_message: str,
                                 context: HttpRequest = None, args: dict = None):
        count = self.model_class.objects.count()
        context, args = self.get_data(context, args)
        result = Client(self.get_schema()).execute(self.get_mutation(**args).get_result(), context_value=context)
        self.assert_raised_error(result, error_message)
        self.assertEqual(
            self.model_class.objects.count(), count, 'Check if ' + self.model_class.__name__ + ' has not been created')
        self.assertEqual(
            self.get_attribute_value(self.model_class.objects.get(pk=model.pk), attribute),
            self.get_attribute_value(model, attribute),
            'Check if ' + model.__class__.__name__ + '.' + attribute + ' has not been updated')
        return result


class QueryTestCase(OperationTestCase):
    model_class = None  # implement for collection_success_test

    def assert_field_equal(self, result: dict, operation_name: str, field_name: str, value) -> None:
        self.assertEqual(
            self.get_operation_field_value(result, operation_name, field_name), value,
            'Check if data.' + field_name + ' = ' + str(value))

    def collection_success_test(self, context: HttpRequest = None, expected_count: int = None, args: dict = None):
        if expected_count is None:
            expected_count = self.model_class.objects.count()

        context, args = self.get_data(context, args)
        result = Client(self.get_schema()).execute(self.get_query(**args).get_result(), context_value=context)
        self.assert_operation_no_errors(result)
        edges = self.get_operation_field_value(result, self.get_query().get_name(), 'edges')
        self.assertEqual(len(edges), expected_count, 'Check if query has returned full set.')

    def get_query(self, **kwargs: dict) -> constructors.Query:
        raise NotImplementedError('Function get_query for QueryTestCase class should be implemented.')

    def raised_error_test(self, error_message: str, context: HttpRequest = None, args: dict = None):
        context, args = self.get_data(context, args)
        result = Client(self.get_schema()).execute(self.get_query(**args).get_result(), context_value=context)
        self.assert_raised_error(result, error_message)