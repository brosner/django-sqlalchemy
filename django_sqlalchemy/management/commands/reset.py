from django.core.management.base import AppCommand, CommandError
from optparse import make_option
from django_sqlalchemy.management import sql

class Command(AppCommand):
    option_list = AppCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
    )
    help = "Executes ``sqlreset`` for the given app(s) in the current database."
    args = '[appname ...]'

    output_transaction = True

    def handle_app(self, app, **options):
        from django.conf import settings
        from sqlalchemy import create_engine
        app_name = app.__name__.split('.')[-2]
        if options.get('interactive'):
            confirm = raw_input("""
You have requested a database reset.
This will IRREVERSIBLY DESTROY any data for
the "%s" application in the database "%s".
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: """ % (app_name, settings.DJANGO_SQLALCHEMY_DBURI))
        else:
            confirm = 'yes'
        
        if confirm == 'yes':
            try:
                from django_sqlalchemy.backend import metadata
                engine = create_engine(settings.DJANGO_SQLALCHEMY_DBURI)
                sql.reset(engine, app)
                sql.create(engine, app)
            except Exception, e:
                raise CommandError("""Error: %s couldn't be reset. Possible reasons:
  * The database isn't running or isn't configured correctly.
  * At least one of the database tables doesn't exist.
  * The SQL was invalid.
Hint: Look at the output of 'django-admin.py sqlreset %s'. That's the SQL this command wasn't able to run.
The full error: %s""" % (app_name, app_name, e))
        else:
            print "Reset cancelled."
