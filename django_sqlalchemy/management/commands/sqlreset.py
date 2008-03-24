from cStringIO import StringIO
from django.core.management.base import AppCommand, CommandError
from django.conf import settings
from django_sqlalchemy.management import sql

class Command(AppCommand):
    help = "Prints the DROP TABLE SQL, then the CREATE TABLE SQL, for the given app name(s)."

    output_transaction = True

    def handle_app(self, app, **options):
        from django_sqlalchemy.backend import metadata
        from sqlalchemy import create_engine
        buf = StringIO()
        def buffer_output(s, p=""):
            return buf.write(s + p)
        engine = create_engine(settings.DJANGO_SQLALCHEMY_DBURI,
            strategy="mock",
            executor=buffer_output)
        sql.reset(engine, app)
        sql.create(engine, app)
        # the sql printed may *not* be the exact sql SQLAlchemy uses. i bet
        # it is pretty close.
        print buf.getvalue()
