from setuptools import setup, find_packages

setup(
    name='NoseDjangoSQLAlchemy',
    version='0.1',
    author='Michael Trier',
    author_email = 'mtrier@gmail.com',
    description = 'nose plugin for easy testing of the django-sqlalchemy project.',
    install_requires='nose>=0.10',
    url = "http://gitorious.org/projects/django-sqlalchemy/",
    license = 'New BSD',
    packages = find_packages(exclude=['tests']),
    zip_safe = False,
    include_package_data = True,
    entry_points = {
        'nose.plugins': [
            'django-sqlalchemy = nose_django_sqlalchemy.plugin:NoseDjangoSQLAlchemy',
            ]
        }
    )

