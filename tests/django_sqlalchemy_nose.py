"""
nose plugin for easy testing of django-sqlalchemy. Sets up a test
database (or schema) and installs apps from test settings file before tests
are run, and tears the test database (or schema) down after all tests are run.
"""
__author = 'Michael Trier'
__version__ = '0.0'

import atexit
import logging
import os, sys
import re

from nose.plugins import Plugin
import nose.case

# Force settings.py pointer
# search the current working directory and all parent directories to find
# the settings file
from nose.importer import add_path
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
def get_SETTINGS_PATH():
    cwd = os.getcwd()
    while cwd:
        if 'settings.py' in os.listdir(cwd):
            break
        cwd = os.path.split(cwd)[0]
        if cwd == '/':
            return None
    return cwd
SETTINGS_PATH = get_SETTINGS_PATH()

log = logging.getLogger('nose.plugins.djangosqlalchemynose')

class DjangoSQLAlchemyNose(Plugin):
    """
    Enable to set up django test environment before running all tests, and
    tear it down after all tests. If the django database engine in use is not
    sqlite3, one or both of --django-test-db or django-test-schema must be
    specified.

    Note that your django project must be on PYTHONPATH for the settings file
    to be loaded. The plugin will help out by placing the nose working dir
    into sys.path if it isn't already there, unless the -P
    (--no-path-adjustment) argument is set.
    """
    name = 'django'

    def configure(self, options, conf):
        Plugin.configure(self, options, conf)
        self.verbosity = conf.verbosity

    def begin(self):
        """Create the test database and schema, if needed, and switch the
        connection over to that database. Then call install() to install
        all apps listed in the loaded settings module.
        """
        # Add the working directory (and any package parents) to sys.path
        # before trying to import django modules; otherwise, they won't be
        # able to find project.settings if the working dir is project/ or
        # project/..

        if not SETTINGS_PATH:
            sys.stderr.write("Can't find Django settings file!\n")
            # short circuit if no settings file can be found
            return

        if self.conf.addPaths:
            map(add_path, self.conf.where)

        add_path(SETTINGS_PATH)
        sys.path.append(SETTINGS_PATH)
        import settings
        settings.DEBUG = False # I have no idea why Django does this, but it does
        from django.core import mail
        self.mail = mail
        from django.conf import settings
        from django.core import management
        from django.test.utils import setup_test_environment
        from django.test.utils import create_test_db

        self.old_db = settings.DATABASE_NAME

        # setup the test env for each test case
        setup_test_environment()
        create_test_db(verbosity=self.verbosity)

        # exit the setup phase and let nose do it's thing
            
    def beforeTest(self, test):

        if not SETTINGS_PATH:
            # short circuit if no settings file can be found
            return

        from django.core.management import call_command
        call_command('reset', verbosity=0, interactive=False)

        if isinstance(test, nose.case.Test) and \
            isinstance(test.test, nose.case.MethodTestCase) and \
            hasattr(test.context, 'fixtures'):
                # We have to use this slightly awkward syntax due to the fact
                # that we're using *args and **kwargs together.
                call_command('loaddata', *test.context.fixtures, **{'verbosity': 0}) 
        self.mail.outbox = []

    def finalize(self, result=None):
        """
        Clean up any created database and schema.
        """
        if not SETTINGS_PATH:
            # short circuit if no settings file can be found
            return

        from django.test.utils import teardown_test_environment
        from django.test.utils import destroy_test_db
        #destroy_test_db(self.old_db, verbosity=self.verbosity)   
        #teardown_test_environment()