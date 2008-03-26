"""
nose plugin for easy testing of the django-sqlalchemy project.
"""
__author = 'Michael Trier'
__version__ = '0.1'

import atexit
import logging
import os, sys
import re

from nose.plugins import Plugin
from nose.util import tolist
import nose.case

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

log = logging.getLogger('nose.plugins.django_sqlalchemy')

class NoseDjangoSQLAlchemy(Plugin):
    """
    Enable to set up django test environment before running all tests, and
    tear it down after all tests. 
    """
    name = 'django-sqlalchemy'

    def add_options(self, parser, env=os.environ):
        # keep copy so we can make our setting in the env we were passed
        self.env = env
        Plugin.add_options(self, parser, env)
        parser.add_option('--django-settings', action='store',
                          dest='django_settings', default=None,
                          help="Set module as the DJANGO_SETTINGS_MODULE"
                          " environment variable.")
        
    def configure(self, options, conf):
        Plugin.configure(self, options, conf)
        conf.exclude = map(re.compile, tolist(r'^(manage\.py|.*settings\.py|apps)$'))
        
        if options.django_settings and self.env is not None:
            self.env['DJANGO_SETTINGS_MODULE'] = options.django_settings
        
        self.verbosity = conf.verbosity

    def begin(self):
        if not SETTINGS_PATH:
            sys.stderr.write("Can't find Django settings file!\n")
            return

        if self.conf.addPaths:
            map(add_path, self.conf.where)

        add_path(SETTINGS_PATH)
        sys.path.append(SETTINGS_PATH)
        import settings
        settings.DEBUG = False
        from django.core import mail
        self.mail = mail
        from django.test.utils import setup_test_environment

        # setup the test env for each test case
        setup_test_environment()
            
    def beforeTest(self, test):

        if not SETTINGS_PATH:
            return
        
        from django.core.management import call_command
        call_command('flush', verbosity=0, interactive=False)
        
        if isinstance(test, nose.case.Test) and \
            isinstance(test.test, nose.case.MethodTestCase) and \
            hasattr(test.context, 'fixtures'):
                call_command('loaddata', *test.context.fixtures, **{'verbosity': 0}) 
        self.mail.outbox = []

    def finalize(self, result=None):
        """
        Clean up any created database and schema.
        """
        if not SETTINGS_PATH:
            return
        