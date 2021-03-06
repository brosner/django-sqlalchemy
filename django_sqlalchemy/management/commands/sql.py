from cStringIO import StringIO
from sqlalchemy import create_engine
from django.core.management.base import AppCommand, CommandError
from django.conf import settings
from django_sqlalchemy.management import sql

class Command(AppCommand):
    def handle_app(self, app, **options):
        # TODO: figure why this import *has* to be here. it is probably a
        # python related thing i don't fully understand yet.
        from django_sqlalchemy.backend import metadata
        buf = StringIO()
        def buffer_output(s, p=""):
            return buf.write(s + p)
        engine = create_engine(settings.DJANGO_SQLALCHEMY_DBURI,
            strategy="mock",
            executor=buffer_output)
        sql.create(engine, app)
        # the sql printed may *not* be the exact sql SQLAlchemy uses. i bet
        # it is pretty close.
        print buf.getvalue()
