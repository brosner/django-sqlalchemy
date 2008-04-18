from django.db.models.loading import get_models
from sqlalchemy import create_engine
from django_sqlalchemy.backend import metadata, Session

def reset(engine, app):
    metadata.drop_all(engine, tables=_get_tables_for_app(app))
    Session.commit()

def create(engine, app):
    metadata.create_all(engine, tables=_get_tables_for_app(app))
    Session.commit()

def _get_tables_for_app(app):
    tables = []
    for model in get_models(app):
        tables.append(model.__table__)
        tables.extend([f.__table__ for f in model._meta.local_many_to_many])
    return tables
