from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseOperations, BaseDatabaseValidation, util

from django_sqlalchemy import utils

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

session = scoped_session(sessionmaker(bind=engine))

# default metadata
metadata = MetaData(bind=engine)

DatabaseError = Exception
IntegrityError = Exception

class DatabaseFeatures(BaseDatabaseFeatures):
    pass

class DatabaseOperations(BaseDatabaseOperations):
    def quote_name(self, name):
        return metadata.bind.dialect.identifier_preparer.quote_identifier(name)

class DatabaseWrapper(BaseDatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        self.metadata = metadata
        self.features = DatabaseFeatures()
        self.ops = DatabaseOperations()
        #self.client = DatabaseClient()
        #self.creation = DatabaseCreation(self)
        from django_sqlalchemy.backend.introspection import DatabaseIntrospection
        self.introspection = DatabaseIntrospection(self)
        self.validation = BaseDatabaseValidation()
   
    def _cursor(self, settings):
        from sqlalchemy.databases.sqlite import SQLiteDialect
        conn = session.connection()
        kwargs = {}
        if isinstance(conn.engine.dialect, SQLiteDialect,):
            from django.db.backends.sqlite3.base import SQLiteCursorWrapper
            kwargs['factory'] = SQLiteCursorWrapper
        return conn.connection.cursor(**kwargs)

def get_sqlalchemy_backend():
    """
    Loads up the sqlalchemy specific backend overrides for Django.
    """
    try:        
        _import_path = 'django_sqlalchemy.backend'
        backend = __import__('%s%s' % (_import_path, utils.db_label), {}, {}, [''])
    except ImportError, e:
        raise ImproperlyConfigured, "%r isn't an available database backend." % utils.db_label
