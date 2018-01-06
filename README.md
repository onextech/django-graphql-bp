django-graphql-bp
=======
##### Boiler plate for API projects based on Django 2 &amp; graphql (graphene) 2

---
# Requirments
- python: 3.5+
- pip: 9.0+
- postgress: 9.5+
---

# Configuration
##### Settings and Environment variables

1) [Postgress database](https://docs.djangoproject.com/en/2.0/ref/settings/#databases):
    
    Environment vasriables:
    - DB_NAME - database name;
    - DB_USER - database username;
    - DB_PASSWORD - database user's password;
    - DB_HOST - database host;
    - DB_PORT - database port.

    In config file:
    ``` python
    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ['DB_NAME'],
                'USER': os.environ['DB_USER'],
                'PASSWORD': os.environ['DB_PASSWORD'],
                'HOST': os.environ['DB_HOST'],
                'PORT': os.environ['DB_PORT'],
            }
        }
    ```

2) Test e-mailbox:
    Email address wherewhere tests will spam with emails.

    Environment variables:
    - TEST_EMAIL_USERNAME - email username;
    - TEST_EMAIL_DOMAIN - email domain;

   Where email have following structure *TEST_EMAIL_USERNAME@TEST_EMAIL_DOMAIN*. For example test@gmail.com: TEST_EMAIL_USERNAME="test" and TEST_EMAIL_DOMAIN="gmail.com".

    In config file:
    ``` python
    TEST_EMAIL_USERNAME = os.environ.get('TEST_EMAIL_USERNAME')
    TEST_EMAIL_DOMAIN = os.environ.get('TEST_EMAIL_DOMAIN')
    ```

3) Custom user model:
    In config file:

    ``` python
    INSTALLED_APPS = [
        ...
        'django_graphql_bp.user',
        ...
    ]
    
    AUTH_USER_MODEL = 'user.User'
    ```
    **This User model will be used instead of standard django.contrib.auth.models.User**
    
4) Graphql:
    In config file:
    
    ``` python
    INSTALLED_APPS = [
        ...
        'graphene_django',
        ...
    ]
    # Path to root directory of the project
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    GRAPHENE = {
        # where Schema class is located
        'SCHEMA': 'app.graphql.api.schema' 
    }
    ```
    

---

# Installation
1) Package:
    To install run:
    
    ```
    # pip install django-graphql-bp
    ```
    Or add django-graphql-bp package to your requirements and run from there.
    **If you are using virtual environment, make sure that you are activated it before run.**
    Package will install following packages:
    - django 2.0+
    - django-filter 1.1+
    - graphene-django 2.0+
    - psycopg2 2.7+
    
2) Database migrations:
    Use standard django migration to install custom user model:
    ```
    # ./manage.py migrate
    ```

3) Url for graphql:
    In urls.py:
    ``` python
    from django.views.decorators.csrf import csrf_exempt
    from graphene_django.views import GraphQLView
    
    urlpatterns = [
        path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    ]
    ```
    
4) Schema
    To use all User's operations from package need to extend Queries and Mutations from UserQueries and UserMutations from django_graphql_bp.graphql.api.
    api.py file example:
    
    ``` python
    import graphene
    from django_graphql_bp.graphql.api import UserQueries, UserMutations


    class Queries(UserQueries):
        pass


    class Mutations(UserMutations):
        pass

    schema = graphene.Schema(query=Queries, mutation=Mutations)
    ```

    *Location of api.py file has been set up at Configuration #4*
---

5) Tests:
    To enable tests for all User's operations from package need to create extend UserSchemaTestCase in tests.py file.
    test.py example:
    
    ``` python
    from app.graphql.api import schema
    from django_graphql_bp.user.tests import SchemaTestCase as UserSchemaTestCase
    from graphene import Schema
    
    
    class SchemaTestCase(UserSchemaTestCase):
        def get_schema(self) -> Schema:
            return schema
    ```
    
    *get_schema allow tests use Schema from application instead of Schema from package*
    

# Usage

