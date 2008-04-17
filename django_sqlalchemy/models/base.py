
from django.db import models

from sqlalchemy.schema import Table, SchemaItem, Column, MetaData
from sqlalchemy.orm import synonym as _orm_synonym, mapper, comparable_property
from sqlalchemy.orm.interfaces import MapperProperty
from sqlalchemy.orm.properties import PropertyLoader, ColumnProperty
from sqlalchemy import util, exceptions

from django_sqlalchemy.backend import metadata, Session
from django_sqlalchemy.models import *
from django_sqlalchemy.models.manager import SQLAlchemyManager

import types

__all__ = ['Model', 'ModelBase', 'synonym_for', 'comparable_using',
           'declared_synonym']

def is_base(cls):
    """
    Scan bases classes to see if any is an instance of ModelBase. If we
    don't find any, it means the current entity is a base class (like 
    the 'Model' class).
    """
    for base in cls.__bases__:
        if isinstance(base, ModelBase):
            return False
    return True

class ModelBase(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        try:
            parents = [b for b in bases if issubclass(b, Model)]
            if not parents:
                return type.__new__(cls, name, bases, attrs)
        except NameError:
            # 'Model' isn't defined yet, meaning we're looking at Django's own
            # Model class, defined below.
            return type.__new__(cls, name, bases, attrs)
        new_class = super(ModelBase, cls).__new__(cls, name, bases, attrs)
        # HACK: this does not seem ideal. this is a fix for qs-rf r7426 which
        # removed per-backend QuerySet classes. here we use a custom manager
        # to use our queryset, but this is not nice to existing third party
        # apps that don't care about django-sqlachemy.
        if type(new_class._default_manager) is models.Manager:
            model = new_class._default_manager.model
            new_class._default_manager = SQLAlchemyManager()
            new_class._default_manager.model = model
            new_class.objects = new_class._default_manager
        return new_class
    
    def __init__(cls, classname, bases, dict_):
        if hasattr(cls, "__table__"):
            return None
        
        if '_decl_class_registry' in cls.__dict__:
            return type.__init__(cls, classname, bases, dict_)
        
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
        if isinstance(cls._meta.pk, models.AutoField):
            # we need to add in the django-sqlalchemy version of the AutoField
            # because the one that Django adds will not work for our purposes.
            auto_field = AutoField(verbose_name='ID', primary_key=True, auto_created=True)
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
                if isinstance(field, models.AutoField):
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
            mapper_args['inherits'] = inherits
        
        # declarative allows you to specify a mapper as well
        if hasattr(cls, '__mapper_cls__'):
            mapper_cls = util.unbound_method_to_callable(cls.__mapper_cls__)
        else:
            mapper_cls = mapper
        cls.__mapper__ = mapper_cls(cls, table, properties=our_stuff, **mapper_args)
        
        # add the SA Query class onto our model class for easy querying
        cls.query = Session.query_property()
        return type.__init__(cls, classname, bases, dict_)
    
    def __setattr__(cls, key, value):
        """
        This sets up a setter that allows adding columns to the class after the 
        attributes.
        """
        if '__mapper__' in cls.__dict__:
            if isinstance(value, Column):
                _undefer_column_name(key, value)
                cls.__table__.append_column(value)
                cls.__mapper__.add_property(key, value)
            elif isinstance(value, MapperProperty):
                cls.__mapper__.add_property(key, _deferred_relation(cls, value))
            else:
                type.__setattr__(cls, key, value)
        else:
            type.__setattr__(cls, key, value)

def _deferred_relation(cls, prop):
    """
    If quoted names are used this does the lookup to the defined class
    """
    if isinstance(prop, PropertyLoader) and isinstance(prop.argument, basestring):
        arg = prop.argument
        def return_cls():
            try:
                return cls._decl_class_registry[arg]
            except KeyError:
                raise exceptions.InvalidRequestError("When compiling mapper %s, could not locate a declarative class named %r.  Consider adding this property to the %r class after both dependent classes have been defined." % (prop.parent, arg, prop.parent.class_))
        prop.argument = return_cls

    return prop

def synonym_for(name, map_column=False):
    """Decorator, make a Python @property a query synonym for a column.

    A decorator version of [sqlalchemy.orm#synonym()].  The function being
    decorated is the 'descriptor', otherwise passes its arguments through
    to synonym()::

      @synonym_for('col')
      @property
      def prop(self):
          return 'special sauce'

    The regular ``synonym()`` is also usable directly in a declarative
    setting and may be convenient for read/write properties::

      prop = synonym('col', descriptor=property(_read_prop, _write_prop))

    """
    def decorate(fn):
        return _orm_synonym(name, map_column=map_column, descriptor=fn)
    return decorate


def comparable_using(comparator_factory):
    """Decorator, allow a Python @property to be used in query criteria.

    A decorator front end to [sqlalchemy.orm#comparable_property()], passes
    throgh the comparator_factory and the function being decorated::

      @comparable_using(MyComparatorType)
      @property
      def prop(self):
          return 'special sauce'

    The regular ``comparable_property()`` is also usable directly in a
    declarative setting and may be convenient for read/write properties::

      prop = comparable_property(MyComparatorType)
    """
    def decorate(fn):
        return comparable_property(comparator_factory, fn)
    return decorate

def declarative_base(engine=None, metadata=None, mapper=None):
    lcl_metadata = metadata or MetaData()
    if engine:
        lcl_metadata.bind = engine
    class Base(object):
        __metaclass__ = DeclarativeMeta
        metadata = lcl_metadata
        if mapper:
            __mapper_cls__ = mapper
        _decl_class_registry = {}
        def __init__(self, **kwargs):
            for k in kwargs:
                if not hasattr(type(self), k):
                    raise TypeError('%r is an invalid keyword argument for %s' %
                                    (k, type(self).__name__))
                setattr(self, k, kwargs[k])
    return Base

def _undefer_column_name(key, column):
    if column.key is None:
        column.key = key
    if column.name is None:
        column.name = key

class Model(models.Model):
    '''
    The base class for all entities    
    '''
    __metaclass__ = ModelBase
    
    metadata = metadata
    _decl_class_registry = {}
    
    def __init__(self, **kwargs):
        for k in kwargs:
            if not hasattr(type(self), k):
                raise TypeError('%r is an invalid keyword argument for %s' %
                                (k, type(self).__name__))
            setattr(self, k, kwargs[k])
        return super(Model, self).__init__(**kwargs)
    
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
