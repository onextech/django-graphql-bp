"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
from setuptools import setup, find_packages


setup(
    name='django_graphql_bp',
    version='1.2.5',
    description='Boiler plate for API projects based on Django 2 &amp; graphql (graphene) 2',
    url='https://github.com/onextech/django-graphql-bp',
    author='Artsem Stalavitski',
    author_email='a.stalavitski@gmail.com',
    license='MIT',
    keywords='django graphene graphql boilerplate crud user authentication',
    packages=find_packages(),
    install_requires=[
        'boto3>=1.5',
        'django>=2.0',
        'django-autoslug-iplweb==1.9.4.dev0',
        'django-filter>=1.1',
        'django-storages>=1.6',
        'django-uuid-upload-path>=1.0',
        'graphene-django>=2.0',
        'pillow>=5.0',
        'psycopg2>=2.7'
    ],
    python_requires='>=3'
)