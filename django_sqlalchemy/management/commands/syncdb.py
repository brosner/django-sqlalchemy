from optparse import make_option
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django_sqlalchemy.utils import CreationSniffer

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--verbosity', action='store', dest='verbosity', default='1',
            type='choice', choices=['0', '1', '2'],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'),
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
    )
    help = "Create the database tables for all apps in INSTALLED_APPS whose tables haven't already been created."

    def handle_noargs(self, **options):
        from django_sqlalchemy.backend import metadata, session
        from django.core.management import call_command
        from django.core.management.sql import emit_post_sync_signal

        # Import the 'management' module within each installed app, to register
        # dispatcher events.
        for app_name in settings.INSTALLED_APPS:
            try:
                __import__(app_name + '.management', {}, {}, [''])
            except ImportError, exc:
                if not exc.args[0].startswith('No module named management'):
                    raise

        # set up table listeners
        sniffer = CreationSniffer()
        for table in metadata.tables.values(): 
            table.append_ddl_listener('after-create', sniffer) 

        metadata.create_all()
        session.commit()

        verbosity = int(options.get('verbosity', 1))
        interactive = options.get('interactive')

        # Send the post_syncdb signal, so individual apps can do whatever they need
        # to do at this point.
        emit_post_sync_signal(sniffer.models, verbosity, interactive)

        # load fixtures
        call_command('loaddata', 'initial_data', verbosity=verbosity)
