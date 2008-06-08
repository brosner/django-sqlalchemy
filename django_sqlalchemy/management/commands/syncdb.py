from optparse import make_option
from django.core.management.base import NoArgsCommand

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

        # TODO: create after_create listeners for all tables, capture
        # who got created and then use that in a post sync signal

        metadata.create_all()
        session.commit()

        verbosity = int(options.get('verbosity', 1))
        interactive = options.get('interactive')

        # Send the post_syncdb signal, so individual apps can do whatever they need
        # to do at this point.
        # emit_post_sync_signal(created_models, verbosity, interactive)

        # load fixtures
        call_command('loaddata', 'initial_data', verbosity=verbosity)
