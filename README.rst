Boiler plate for API projects based on Django 2 & graphql (graphene) 2
======================================================================
===========
Requirments
===========
- python: 3.5+
- pip: 9.0+
- postgress: 9.5+

----

============
Installation
============
To install run:

    ``# pip install django-graphql-bp``

Or add django-graphql-bp package to your requirements and run from there.

**If you are using virtual environment, make sure that you are activated it before run.**

Package will install following packages:

- django 2.0+
- django-filter 1.1+
- graphene-django 2.0+

----

=============
Configuration
=============

Settings and Environment variables
**********************************

Environment variables for `postgress database <https://docs.djangoproject.com/en/2.0/ref/settings/#databases>`_:

- DB_NAME - database name;
- DB_USER - database username;
- DB_PASSWORD - database user's password;
- DB_HOST - database host;
- DB_PORT - database port.

Environment variables for test mail box (where tests will be spamming with emails):

- TEST_EMAIL_USERNAME - email username;
- TEST_EMAIL_DOMAIN - email domain;

Where email have following structure *TEST_EMAIL_USERNAME@TEST_EMAIL_DOMAIN*. For example test@gmail.com: TEST_EMAIL_USERNAME="test" and TEST_EMAIL_DOMAIN="gmail.com".


