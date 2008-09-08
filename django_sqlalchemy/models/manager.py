
from django_sqlalchemy.models.query import SQLAlchemyQuerySet

class DjangoSQLAlchemyManager(object):
    """
    A custom Manager for using the SQLAlchemyQuerySet instead of the default
    one with Django.
    """
    def get_query_set(self):
        return SQLAlchemyQuerySet(self.model)

    def first(self):
        return self.get_query_set().first()

    def options(self, *args):
        return self.get_query_set().options(*args)

    def _insert(self, values, **kwargs):
        """ TODO: I think we can implement this by passing it to SA directly. """
        return True
    
    def _update(self, values, **kwargs):
        """ TODO: I think we can implement this by passing it to SA directly. """
        return True

from django_sqlalchemy.utils import MixIn
from django.db.models import Manager

def _patch():
    """Patch Django's internals."""
    MixIn(Manager, DjangoSQLAlchemyManager, include_private=False)
_patch()
