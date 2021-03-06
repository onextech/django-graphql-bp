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
    # Test email of the next structure: TEST_EMAIL_USERNAME@TEST_EMAIL_DOMAIN
    TEST_EMAIL_USERNAME = os.environ.get('TEST_EMAIL_USERNAME')
    TEST_EMAIL_DOMAIN = os.environ.get('TEST_EMAIL_DOMAIN')
    ```

3) User app:

    In config file:

    ``` python
    INSTALLED_APPS = [
        ...
        'django_graphql_bp.user',
        ...
    ]
    
    # Custom User model
    AUTH_USER_MODEL = 'user.User'
    ```
    **This User model will be used instead of standard django.contrib.auth.models.User.**
    
4) Article app (optional):
    In config file:

    ``` python
    INSTALLED_APPS = [
        ...
        'django_graphql_bp.article',
        ...
    ]
    ```
    **Configure it only if willing to use article app's featurues.**

    
5) Graphql:

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
    
6) AWS S3 storage (optional):

    Environment variables:
    - AWS_ACCESS_KEY_ID - [Access Key ID from AWS ](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys);
    - AWS_SECRET_ACCESS_KEY - [Secret Access Key from AWS ](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys);
    - AWS_STORAGE_BUCKET_NAME - name of backet in AWS S3 account;
    - AWS_MEDIA_BUCKET_NAME - name of backet in AWS S3 account;
    - AWS_QUERYSTRING_AUTH - set string 'False' to override default.

    In config file:
    
    ``` python
    # Amazon S3 configuration
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_MEDIA_BUCKET_NAME = os.environ.get('AWS_MEDIA_BUCKET_NAME')
    AWS_QUERYSTRING_AUTH = ast.literal_eval(os.environ.get('AWS_QUERYSTRING_AUTH'))
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    
    # Django file storage
    DEFAULT_FILE_STORAGE = 'django_graphql_bp.core.storages.S3MediaStorage'
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
    - boto3 1.5+
    - django 2.0+
    - django-filter 1.1+
    - graphene-django 2.0+
    - pillow 5.0+
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
    
4) Schema:

    To use all User's operations from package need to extend Queries and Mutations from UserQueries and UserMutations from django_graphql_bp.graphql.api.
    api.py file example:
    
    ``` python
    import graphene
    import django_graphql_bp.article.schema # required to use article operations
    import django_graphql_bp.user.schema
    
    
    class Queries(
        django_graphql_bp.article.schema.Query, # required to use article queries
        django_graphql_bp.user.schema.Query,
        graphene.ObjectType
    ):
        pass
    
    
    class Mutations(
        django_graphql_bp.article.schema.Mutation, # required to use article mutations
        django_graphql_bp.user.schema.Mutation,
        graphene.ObjectType
    ):
        pass
    
    
    schema = graphene.Schema(query=Queries, mutation=Mutations)
    ```

    *Location of api.py file has been set up at Configuration #5*

5) Tests
    To enable tests for all User's and Article's operations from package.
test.py example:

    ``` python
    from django_graphql_bp.article.tests import * # to enable Article tests
    from django_graphql_bp.user.tests import * # to enable User tests
    ```
    
    *get_schema allow tests use Schema from application instead of Schema from package*
---

# Usage
1) Common:

    List of common usages:
    
    1. ok (bool) - boolean success flag for mutations that not threw any exceptions.
    
    2. node (object) - object related to certain Django model contains all fields and relations that wasn't excluded.
    
    3. validationErrors (object) - JSON object with validation errors of following structure:
        ``` javascript
        {
            fieldname1: [
                {code: "error code 1", message: "error message 1"}, 
                ...
            ], 
            ...
        }
        ```
    
    4. edges (object) - array object of nodes (Usage #2):
        ``` javascript
        {
            node {
                // node data
            }
        }
        ```

    4. errors - array of error objects of following structure:
    
        ``` javascript
        [
            {
              "message": "error message",
              "locations": [
                {
                  "line": (int), // line of error
                  "column": (int)  // column of error
                }
              ]
            }
        ]
        ```

2) CRUD mutations:

    coming soon...

3) User operations:

    1. Create mutation:
        ``` javascript
        mutation {
          createUser(input: {
            email: "email@email.com"
            password1: "password"
            password2: "password"
          }) {
            ok
            node {
              pk
            }
            validationErrors
          }
        }
        ```
        
        Access:
        - guest;
        - any user;
        
        Input:
        - email (required) - string;
        - password (required) - string.
        
        Output:
        - ok - Usage #1.1;
        - node - User object (with password field excluded) - Usage #1.2;
        - validationErrors - Usage #1.3.

    2. Update mutation:
        ``` javascript
        mutation {
          updateUser(input: {
            pk: 1
            email: "email@email.com"
            name: "name"
            isActive: true
          }) {
            ok
            node {
              pk
            }
            validationErrors
          }
        }
        ```
        
        Access:
        - user to own record;
        - staff user.
        
        Input:
        - pk (required) - int;
        - email (optional) - string;
        - name (optional) - string;
        - isActive (optional) - bool.
        
        Output:
        - ok - Usage #1.1;
        - node - User object (with password field excluded) - Usage #1.2;
        - validationErrors - Usage #1.3.

    3. Delete mutation:
        ``` javascript
        mutation {
          deleteUser(input: {
            pk: 1
          }) {
            ok
            node {
              pk
            }
          }
        }
        ```
        
        Access:
        - user to own record;
        - staff user.
        
        Input:
        - pk (required) - int.
        
        Output:
        - ok - Usage #1.1;
        - node - User object (with password field excluded) - Usage #1.2.
    
    4. Login mutation:
        ``` javascript
        mutation {
          loginUser(input: {
            email: "email@email.com"
            password: "password"
          }) {
            ok
            node {
              pk
            }
            validationErrors
          }
        }
        ```
        
        Access:
        - guest;
        - any user.
        
        Input:
        - email (required) - string;
        - password (required) - string.
        
        Output:
        - ok - Usage #1.1;
        - node - User object (with password field excluded) - Usage #1.2;
        - validationErrors - Usage #1.3.
        
    5. Logout mutation:
        ``` javascript
        mutation {
          logoutUser(input: {}) {
            ok
            node {
              pk
            }
          }
        }
        ```
        
        Access:
        - guest;
        - any user.
        
        Input:
        - None
        
        Output:
        
        - ok - Usage #1.1;
        - node - User object (with password field excluded) - Usage #1.2.
        
    6. Current user query:
        ``` javascript
        query {
          currentUser {
            pk
          }
        }
        ```
        
        Access:
        - guest;
        - any user.
        
        Output:
        - node - User object (with password field excluded) - Usage #1.2.    
        
    7. Users query:
        ``` javascript
        query {
          users {
            edges {
              node {
                pk
              }
            }
          }
        }
        ```
        
        Access:
        - staff member.
        
        Output:
        - edges - of User objects - Usage #1.4.