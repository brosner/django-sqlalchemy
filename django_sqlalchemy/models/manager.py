
from django.db import models
from django_sqlalchemy.models.query import SQLAlchemyQuerySet

class Manager(models.Manager):
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