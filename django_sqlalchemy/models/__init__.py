import sqlalchemy
from sqlalchemy import *
from sqlalchemy.types import *
from django_sqlalchemy.models.fields import *
from django_sqlalchemy.models.fields.related import DSForeignKey, DSManyToManyField
from django.conf import settings
from django_sqlalchemy.models.base import instrument_declarative, add_django_sqlalchemy_overrides
from django_sqlalchemy.models.manager import DjangoSQLAlchemyManager
from django_sqlalchemy.backend import metadata

__all__ = ['DSField', 'DSAutoField', 'DSCharField', 'DSPhoneNumberField'] + \
           sqlalchemy.types.__all__

from django.dispatch import dispatcher
from django.db.models import signals

reg = {}

def instrument_models(sender):
    instrument_declarative(sender, reg, metadata)
    add_django_sqlalchemy_overrides(sender)

dispatcher.connect(instrument_models, signal=signals.class_prepared)
