"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
from setuptools import setup, find_packages


setup(
    name='django-graphql-bp',
    version='0.0.1',
    description='Boiler plate for API projects based on Django 2 &amp; graphql (graphene) 2',
    url='https://github.com/onextech/django-graphql-bp',
    author='Artsem Stalavitski',
    author_email='a.stalavitski@gmail.com',
    license='MIT',
    keywords='django graphene graphql boilerplate crud user authentication',

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages(),  # Required
    install_requires=[
       'django>=2.0',
       'django-filter>=1.1',
        'graphene-django>=2.0',
        'psycopg2>=2.7'
    ],
    python_requires='>=3'
)