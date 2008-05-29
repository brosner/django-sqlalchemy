
from django.db.models.base import ModelBase, Model
from django.db.models import AutoField

from sqlalchemy.ext.declarative import DeclarativeMeta, _deferred_relation, synonym_for, comparable_using, declarative_base, _undefer_column_name
from sqlalchemy.schema import Table, Column, MetaData
from sqlalchemy.orm import synonym as _orm_synonym, mapper, comparable_property
from sqlalchemy.orm.interfaces import MapperProperty
from sqlalchemy.orm.properties import PropertyLoader, ColumnProperty
from sqlalchemy import util, exceptions
from sqlalchemy.sql import util as sql_util

from django_sqlalchemy.backend import metadata, Session
from django_sqlalchemy.models import *

import types

__all__ = ['DjangoSQLAlchemyModel', 'declarative_base', 
           'synonym_for', 'comparable_using', 'instrument_declarative']

def add_django_sqlalchemy_overrides(cls):
    def save(self):
        """
        Save the current instance. We force a flush so it mimics Django's 
        behavior.
        """
        obj = Session.save_or_update(self)
        Session.commit()
        return obj
    
    def update(self, *args, **kwargs):
        """
        Updates direct against the database
        """
        obj = Session.update(self, *args, **kwargs)
        Session.commit()
        return obj
        
    def delete(self):
        """
        Deletes the current instance
        """
        obj = Session.delete(self)
        Session.commit()
        return obj
    setattr(cls, 'save', save)
    setattr(cls, 'update', update)
    setattr(cls, 'delete', delete)

def instrument_declarative(cls, registry, metadata):
    """Given a class, configure the class declaratively,
    using the given registry (any dictionary) and MetaData object.
    This operation does not assume any kind of class hierarchy.
    
    """
    if '_decl_class_registry' in cls.__dict__:
        raise exceptions.InvalidRequestError("Class %r already has been instrumented declaratively" % cls)
    cls._decl_class_registry = registry
    cls.metadata = metadata
    _as_declarative(cls, cls.__name__, cls.__dict__)
    
def _as_declarative(cls, classname, dict_):
    cls._decl_class_registry[classname] = cls

    # this sets up our_stuff which reads in the attributes and converts
    # them to SA columns, etc...
    our_stuff = util.OrderedDict()

    # just here to handle SA declarative, not needed for Django
    for k in dict_:
        value = dict_[k]
        if (isinstance(value, tuple) and len(value) == 1 and
            isinstance(value[0], (Column, MapperProperty))):
            util.warn("Ignoring declarative-like tuple value of attribute "
                      "%s: possibly a copy-and-paste error with a comma "
                      "left at the end of the line?" % k)
            continue
        if not isinstance(value, (Column, MapperProperty)):
            continue
        prop = _deferred_relation(cls, value)
        our_stuff[k] = prop

    # Django will *always* have set the pk before we get here. Check if
    # it is a Django AutoField so we can override it with our own. This
    # will allow for a custom primary key to just work.
    if isinstance(cls._meta.pk, AutoField):
        # we need to add in the django-sqlalchemy version of the AutoField
        # because the one that Django adds will not work for our purposes.
        auto_field = DSAutoField(verbose_name='ID', primary_key=True, auto_created=True)
        # this might seem redundant but without it the name is not set 
        # for SA
        auto_field.name = "id"
        # Call set_attributes_from_name as it normally only gets called
        # during Django's metaclass.
        auto_field.set_attributes_from_name(auto_field.name)
        # HACK: we need to force the use of our AutoField over Django's
        # AutoField.
        cls._meta.pk = auto_field
        for i, field in enumerate(cls._meta.fields):
            if isinstance(field, AutoField):
                cls._meta.fields[i] = auto_field
    for field in cls._meta.fields + cls._meta.many_to_many:
        sa_field = field.create_column()
        # A ManyToManyField will return None for the column as it does
        # not need a column.
        if sa_field is not None:
            # this allows us to build up more complex structures
            if isinstance(sa_field, dict):
                our_stuff.update(sa_field)
            else:
                our_stuff[sa_field.name] = sa_field

    # set up attributes in the order they were created
    our_stuff.sort(lambda x, y: cmp(our_stuff[x]._creation_order,
                                    our_stuff[y]._creation_order))

    table = None
    tablename = cls._meta.db_table

    # this is to support SA's declarative to support declaring a Table
    if '__table__' not in cls.__dict__:
        # this is just to support SA's declarative of allowing the
        # specification of the table name using this syntax
        if '__tablename__' in cls.__dict__:
            tablename = cls.__tablename__

        # SA supports autoloading the model from database, but that will
        # not work for Django. We're leaving this here just for future
        # consideration.
        autoload = cls.__dict__.get('__autoload__')
        if autoload:
            table_kw = {'autoload': True}
        else:
            table_kw = {}

        # this allows us to pick up only the Column types for our table
        # definition.
        cols = []
        for key, c in our_stuff.iteritems():
            if isinstance(c, ColumnProperty):
                for col in c.columns:
                    if isinstance(col, Column) and col.table is None:
                        _undefer_column_name(key, col)
                        cols.append(col)
            elif isinstance(c, Column):
                _undefer_column_name(key, c)
                cols.append(c)
        cls.__table__ = table = Table(tablename, cls.metadata,
                                      *cols, **table_kw)
    else:
        table = cls.__table__

    mapper_args = getattr(cls, '__mapper_args__', {})
    if 'inherits' not in mapper_args:
        inherits = cls.__mro__[1]
        inherits = cls._decl_class_registry.get(inherits.__name__, None)
        if inherits:
            mapper_args['inherits'] = inherits
            if not mapper_args.get('concrete', False) and table:
                # figure out the inherit condition with relaxed rules
                # about nonexistent tables, to allow for ForeignKeys to
                # not-yet-defined tables (since we know for sure that our
                # parent table is defined within the same MetaData)
                mapper_args['inherit_condition'] = sql_util.join_condition(
                    inherits.__table__, table,
                    ignore_nonexistent_tables=True)

    # declarative allows you to specify a mapper as well
    if hasattr(cls, '__mapper_cls__'):
        mapper_cls = util.unbound_method_to_callable(cls.__mapper_cls__)
    else:
        mapper_cls = mapper

    cls.__mapper__ = mapper_cls(cls, table, properties=our_stuff,
                                **mapper_args)
    cls.query = Session.query_property()

# def is_base(cls):
#     """
#     Scan bases classes to see if any is an instance of ModelBase. If we
#     don't find any, it means the current entity is a base class (like 
#     the 'Model' class).
#     """
#     for base in cls.__bases__:
#         if isinstance(base, DjangoSQLAlchemyModelBase):
#             return False
#     return True

# class DjangoSQLAlchemyModelBase(ModelBase):
#     __metaclass__ = ClassReplacer(ModelBase)
#     # def __new__(cls, name, bases, attrs):
#     #     try:
#     #         parents = [b for b in bases if issubclass(b, DjangoSQLAlchemyModel)]
#     #         if not parents:
#     #             return type.__new__(cls, name, bases, attrs)
#     #     except NameError:
#     #         # 'DjangoSQLAlchemyModel' isn't defined yet, meaning we're looking 
#     #         # at Django-SQLAlchemy's own DjangoSQLAlchemyModel class, defined 
#     #         # below.
#     #         return type.__new__(cls, name, bases, attrs)
#     #     new_class = super(DjangoSQLAlchemyModelBase, cls).__new__(cls, name, bases, attrs)
#     #     # HACK: this does not seem ideal. this is a fix for qs-rf r7426 which
#     #     # removed per-backend QuerySet classes. here we use a custom manager
#     #     # to use our queryset, but this is not nice to existing third party
#     #     # apps that don't care about django-sqlachemy.
#     #     # if type(new_class._default_manager) is models.Manager:
#     #     #             model = new_class._default_manager.model
#     #     #             new_class._default_manager = Manager()
#     #     #             new_class._default_manager.model = model
#     #     #             new_class.objects = new_class._default_manager
#     #     return new_class
#     
#     def __init__(cls, classname, bases, dict_):
#         if hasattr(cls, "__table__"):
#             return None
#         
#         if '_decl_class_registry' in cls.__dict__:
#             return type.__init__(cls, classname, bases, dict_)
#         
#         cls._decl_class_registry[classname] = cls
#         
#         # this sets up our_stuff which reads in the attributes and converts
#         # them to SA columns, etc...
#         our_stuff = util.OrderedDict()
#         
#         # just here to handle SA declarative, not needed for Django
#         for k in dict_:
#             value = dict_[k]
#             if (isinstance(value, tuple) and len(value) == 1 and
#                 isinstance(value[0], (Column, MapperProperty))):
#                 util.warn("Ignoring declarative-like tuple value of attribute "
#                           "%s: possibly a copy-and-paste error with a comma "
#                           "left at the end of the line?" % k)
#                 continue
#             if not isinstance(value, (Column, MapperProperty)):
#                 continue
#             prop = _deferred_relation(cls, value)
#             our_stuff[k] = prop
#         
#         # Django will *always* have set the pk before we get here. Check if
#         # it is a Django AutoField so we can override it with our own. This
#         # will allow for a custom primary key to just work.
#         if isinstance(cls._meta.pk, AutoField):
#             # we need to add in the django-sqlalchemy version of the AutoField
#             # because the one that Django adds will not work for our purposes.
#             auto_field = DSAutoField(verbose_name='ID', primary_key=True, auto_created=True)
#             # this might seem redundant but without it the name is not set 
#             # for SA
#             auto_field.name = "id"
#             # Call set_attributes_from_name as it normally only gets called
#             # during Django's metaclass.
#             auto_field.set_attributes_from_name(auto_field.name)
#             # HACK: we need to force the use of our AutoField over Django's
#             # AutoField.
#             cls._meta.pk = auto_field
#             for i, field in enumerate(cls._meta.fields):
#                 if isinstance(field, AutoField):
#                     cls._meta.fields[i] = auto_field
#         for field in cls._meta.fields + cls._meta.many_to_many:
#             sa_field = field.create_column()
#             # A ManyToManyField will return None for the column as it does
#             # not need a column.
#             if sa_field is not None:
#                 # this allows us to build up more complex structures
#                 if isinstance(sa_field, dict):
#                     our_stuff.update(sa_field)
#                 else:
#                     our_stuff[sa_field.name] = sa_field
#         
#         table = None
#         tablename = cls._meta.db_table
#         
#         # this is to support SA's declarative to support declaring a Table
#         if '__table__' not in cls.__dict__:
#             # this is just to support SA's declarative of allowing the
#             # specification of the table name using this syntax
#             if '__tablename__' in cls.__dict__:
#                 tablename = cls.__tablename__
#             
#             # SA supports autoloading the model from database, but that will
#             # not work for Django. We're leaving this here just for future
#             # consideration.
#             autoload = cls.__dict__.get('__autoload__')
#             if autoload:
#                 table_kw = {'autoload': True}
#             else:
#                 table_kw = {}
#             # this allows us to pick up only the Column types for our table
#             # definition.
#             cols = []
#             for key, c in our_stuff.iteritems():
#                 if isinstance(c, ColumnProperty):
#                     for col in c.columns:
#                         if isinstance(col, Column) and col.table is None:
#                             _undefer_column_name(key, col)
#                             cols.append(col)
#                 elif isinstance(c, Column):
#                     _undefer_column_name(key, c)
#                     cols.append(c)
#             cls.__table__ = table = Table(tablename, cls.metadata,
#                                           *cols, **table_kw)
#         else:
#             table = cls.__table__
#         
#         mapper_args = getattr(cls, '__mapper_args__', {})
#         if 'inherits' not in mapper_args:
#             inherits = cls.__mro__[1]
#             inherits = cls._decl_class_registry.get(inherits.__name__, None)
#             mapper_args['inherits'] = inherits
#         
#         # declarative allows you to specify a mapper as well
#         if hasattr(cls, '__mapper_cls__'):
#             mapper_cls = util.unbound_method_to_callable(cls.__mapper_cls__)
#         else:
#             mapper_cls = mapper
#         cls.__mapper__ = mapper_cls(cls, table, properties=our_stuff, **mapper_args)
#         
#         # add the SA Query class onto our model class for easy querying
#         cls.query = Session.query_property()
#         return type.__init__(cls, classname, bases, dict_)
#     
#     def __setattr__(cls, key, value):
#         """
#         This sets up a setter that allows adding columns to the class after the 
#         attributes.
#         """
#         if '__mapper__' in cls.__dict__:
#             if isinstance(value, Column):
#                 _undefer_column_name(key, value)
#                 cls.__table__.append_column(value)
#                 cls.__mapper__.add_property(key, value)
#             elif isinstance(value, MapperProperty):
#                 cls.__mapper__.add_property(key, _deferred_relation(cls, value))
#             else:
#                 type.__setattr__(cls, key, value)
#         else:
#             type.__setattr__(cls, key, value)

class DjangoSQLAlchemyModel(object):
    def __init__(self, *args, **kwargs):
        object.__init__(self, *args, **kwargs)

    '''
    The base class for all entities    
    '''
    def save(self):
        """
        Save the current instance. We force a flush so it mimics Django's 
        behavior.
        """
        obj = Session.save_or_update(self)
        Session.commit()
        return obj
    
    def update(self, *args, **kwargs):
        """
        Updates direct against the database
        """
        obj = Session.update(self, *args, **kwargs)
        Session.commit()
        return obj
        
    def delete(self):
        """
        Deletes the current instance
        """
        obj = Session.delete(self)
        Session.commit()
        return obj

from django_sqlalchemy.utils import MixIn

def _patch():
    """Patch Django's internals."""
    MixIn(Model, DjangoSQLAlchemyModel)
# _patch()
