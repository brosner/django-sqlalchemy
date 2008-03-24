from django.db.models.loading import get_models
from sqlalchemy import create_engine
from django_sqlalchemy.backend import metadata

def reset(engine, app):
    tables = []
    for model in get_models(app):
        tables.append(model.__table__)
        tables.extend([f.__table__ for f in model._meta.local_many_to_many])
    metadata.drop_all(engine, tables=tables)


def create(engine, app):
    tables = []
    for model in get_models(app):
        tables.append(model.__table__)
        tables.extend([f.__table__ for f in model._meta.local_many_to_many])
    metadata.create_all(engine, tables=tables)

