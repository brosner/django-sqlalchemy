from django.db.models.loading import get_models
from django.core.management.sql import custom_sql_for_model
from sqlalchemy import create_engine
from django_sqlalchemy.backend import metadata, session

def reset(engine, app):
    metadata.drop_all(engine, tables=_get_tables_for_app(app))
    session.commit()

def create(engine, app):
    metadata.create_all(engine, tables=_get_tables_for_app(app))
    session.commit()

def _get_tables_for_app(app):
    tables = []
    for model in get_models(app):
        tables.append(model.__table__)
        tables.extend([f.__table__ for f in model._meta.local_many_to_many])
    return tables

def process_custom_sql(models, verbosity):
    # TODO: complete this
    # install custom sql for the specified models
    for model in models:
        custom_sql = custom_sql_for_model(model)
        if custom_sql:
            if verbosity >= 1:
                print "Installing custom SQL for %s.%s model" % (app_name, model._meta.object_name)
            try:
                for sql in custom_sql:
                    cursor.execute(sql)
            except Exception, e:
                sys.stderr.write("Failed to install custom SQL for %s.%s model: %s" % \
                                    (app_name, model._meta.object_name, e))
                transaction.rollback_unless_managed()
            else:
                transaction.commit_unless_managed()
