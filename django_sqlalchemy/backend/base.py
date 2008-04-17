
from django.conf import settings
from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseOperations, util

try:
    from sqlalchemy import create_engine, MetaData, exceptions
    from sqlalchemy.sql import operators
except ImportError, e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Error loading sqlalchemy module: %s" % e)

from sqlalchemy.orm import scoped_session, sessionmaker

# We are implementing all fields as non unicode types.  We are then 
# converting all strings to unicode in and out of all fields. 
# This gets rid of the unicode whining and follows Django's approach
# to unicode handling.
engine = create_engine(settings.DJANGO_SQLALCHEMY_DBURI, convert_unicode=True)
engine.echo = getattr(settings, 'DJANGO_SQLALCHEMY_ECHO', False)

Session = scoped_session(sessionmaker(
    bind=engine, transactional=True))

# default metadata
metadata = MetaData(bind=engine)

DatabaseError = Exception
IntegrityError = Exception

class DatabaseFeatures(BaseDatabaseFeatures):
    pass

class DatabaseOperations(BaseDatabaseOperations):
    def quote_name(self, name):
        return metadata.bind.dialect.identifier_preparer.quote_identifier(name)

class ConnectionProxy(object):
    """
    Provides a proxy between what Django expects as a connection and SQLAlchemy.
    """
    def __init__(self, session, connection):
        pass

class DatabaseWrapper(BaseDatabaseWrapper):
    features = DatabaseFeatures()
    ops = DatabaseOperations()
    
    def _cursor(self, settings):
        from sqlalchemy.databases.sqlite import SQLiteDialect
        conn = Session.connection()
        kwargs = {}
        if isinstance(conn.engine.dialect, SQLiteDialect,):
            from django.db.backends.sqlite3.base import SQLiteCursorWrapper
            kwargs['factory'] = SQLiteCursorWrapper
        return conn.connection.cursor(**kwargs)
