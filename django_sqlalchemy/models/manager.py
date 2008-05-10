
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

from django_sqlalchemy.utils import MixIn
from django.db.models import Manager

def _patch():
    """Patch Django's internals."""
    MixIn(Manager, DjangoSQLAlchemyManager)
_patch()
