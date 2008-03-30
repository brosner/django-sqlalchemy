
from django_sqlalchemy.backend import metadata, Session
from django_sqlalchemy.models import *
from django.db import models
from sqlalchemy import *
from sqlalchemy.schema import Table, SchemaItem, Column, MetaData
from sqlalchemy.orm import synonym as _orm_synonym, mapper, relation
from sqlalchemy.orm.interfaces import MapperProperty
from sqlalchemy.orm.properties import PropertyLoader

__all__ = ['Model', 'declarative_base', 'declared_synonym']

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
        
        return super(ModelBase, cls).__new__(cls, name, bases, attrs)
    
    def __init__(cls, classname, bases, dict_):
        if '_decl_class_registry' in cls.__dict__:
            return type.__init__(cls, classname, bases, dict_)
        
        cls._decl_class_registry[classname] = cls
        our_stuff = []
        
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
                if isinstance(sa_field, list):
                    our_stuff.extend(sa_field)
                else:
                    our_stuff.append(sa_field)
        
        # SA supports autoloading the model from database, but that will
        # not work for Django. We're leaving this here just for future
        # consideration.
        autoload = cls.__dict__.get('__autoload__')
        if autoload:
            table_kw = {'autoload': True}
        else:
            table_kw = {}
        
        cls.__table__ = table = Table(cls._meta.db_table, cls.metadata, *our_stuff, **table_kw)
        
        inherits = cls.__mro__[1]
        inherits = cls._decl_class_registry.get(inherits.__name__, None)
        mapper_args = getattr(cls, '__mapper_args__', {})
        
        cls.__mapper__ = mapper(cls, table, inherits=inherits, properties=dict([(f.name, f) for f in our_stuff]), **mapper_args)
        # add the SA Query class onto our model class for easy querying
        cls.query = Session.query_property()
        return type.__init__(cls, classname, bases, dict_)
    
    def __setattr__(cls, key, value):
        if '__mapper__' in cls.__dict__:
            if isinstance(value, Column):
                cls.__table__.append_column(value)
                cls.__mapper__.add_property(key, value)
            elif isinstance(value, MapperProperty):
                cls.__mapper__.add_property(key, _deferred_relation(cls, value))
            elif isinstance(value, declared_synonym):
                value._setup(cls, key, None)
            else:
                type.__setattr__(cls, key, value)
        else:
            type.__setattr__(cls, key, value)

def _deferred_relation(cls, prop):
    if isinstance(prop, PropertyLoader) and isinstance(prop.argument, basestring):
        arg = prop.argument
        def return_cls():
            return cls._decl_class_registry[arg]
        prop.argument = return_cls

    return prop

class declared_synonym(object):
    def __init__(self, prop, name, mapperprop=None):
        self.prop = prop
        self.name = name
        self.mapperprop = mapperprop
        
    def _setup(self, cls, key, init_dict):
        prop = self.mapperprop or getattr(cls, self.name)
        prop = _deferred_relation(cls, prop)
        setattr(cls, key, self.prop)
        if init_dict is not None:
            init_dict[self.name] = prop
            init_dict[key] = _orm_synonym(self.name)
        else:
            setattr(cls, self.name, prop)
            setattr(cls, key, _orm_synonym(self.name))

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
