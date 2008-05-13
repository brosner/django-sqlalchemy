from django.db import models
from django.db.models.fields import NOT_PROVIDED
from django.conf import settings
from django.utils.maxlength import LegacyMaxlength

from sqlalchemy import Column
from sqlalchemy.orm import deferred, synonym
from sqlalchemy.types import *

from django_sqlalchemy import utils

class KillTheFInMaxLength(LegacyMaxlength):
    def __init__(cls, name, bases, attrs):
        pass

    
class Field(models.Field):
    __metaclass__ = KillTheFInMaxLength
    
    # def __init__(self, *args, **kwargs):        
    #     self.sa_column = None
    #     models.Field.__init__(self, **kwargs)
        
    def create_column(self):
        kwargs = dict(key=self.column, nullable=self.null,
                index=self.db_index, unique=self.unique)
        if self.default is not NOT_PROVIDED:
            kwargs["default"] = self.default
        if self.primary_key:
            kwargs["primary_key"] = True
        
        kwargs.update(self.sa_column_kwargs())
        
        self.sa_column = Column(self.db_column or self.name, self.sa_column_type(), 
                *self.sa_column_args(),
                **kwargs)
        return self.sa_column
        
    def sa_column_type(self):
        raise NotImplementedError
    
    def sa_column_args(self):
        return tuple()
    
    def sa_column_kwargs(self):        
        return dict()

utils.MixIn(models.Field, Field)    
utils.MixIn(LegacyMaxlength, KillTheFInMaxLength)    

class AutoField(models.AutoField, Field):
    def __init__(self, *args, **kwargs):
        models.AutoField.__init__(self, *args, **kwargs)
        Field.__init__(self, *args, **kwargs)

    def sa_column_kwargs(self):
        kwargs = dict(primary_key=True)
        base = super(AutoField, self).sa_column_kwargs()
        base.update(kwargs)
        return base
    
    def sa_column_type(self):
        return Integer()

utils.MixIn(models.AutoField, AutoField)

class BooleanField(Field):
    def __init__(self, *args, **kwargs):
        models.BooleanField.__init__(self, *args, **kwargs)
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return Boolean()
    
class CharField(models.CharField):
    def sa_column_type(self):
        return String(length=self.max_length)

utils.MixIn(models.CharField, Field)

class CommaSeparatedIntegerField(CharField):
    def __init__(self, *args, **kwargs):
        CharField.__init__(self, *args, **kwargs)
    
class DateField(Field):
    def __init__(self, verbose_name=None, name=None, auto_now=False, auto_now_add=False, **kwargs):
        self.onupdate = kwargs.pop('onupdate', None)
        models.DateField.__init__(self, verbose_name=verbose_name, 
                                        name=name, 
                                        auto_now=auto_now, 
                                        auto_now_add=auto_now_add, **kwargs)
        Field.__init__(self, verbose_name=None, name=None, **kwargs)
    
    def sa_column_kwargs(self):
        # need to handle auto_now and auto_now_add
        kwargs = dict(onupdate=self.onupdate)
        base = super(DateField, self).sa_column_kwargs()
        base.update(kwargs)
        return base
    
    def sa_column_type(self):
        return Date()

class DateTimeField(DateField):
    def __init__(self, *args, **kwargs):
        DateField.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return DateTime()

class DecimalField(Field):
    def __init__(self, *args, **kwargs):
        models.DecimalField.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                           name=kwargs.get('name', None), 
                                           max_digits=kwargs.get('max_digits', None), 
                                           decimal_places=kwargs.get('decimal_places', None), **kwargs)
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_kwargs(self):
        kwargs = dict(precision=self.decimal_places, length=self.max_digits)
        base = super(DecimalField, self).sa_column_kwargs()
        base.update(kwargs)
        return base

    def sa_column_type(self):
        return Numeric()

class EmailField(CharField):
    def __init__(self, *args, **kwargs):
        models.EmailField.__init__(self,  *args, **kwargs)
        CharField.__init__(self, *args, **kwargs)
    
class FileField(Field):
    def __init__(self, *args, **kwargs):
        models.FileField.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                        name=kwargs.get('name', None), 
                                        upload_to=kwargs.get('upload_to', ''), **kwargs)
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return String(length=self.max_length)

class FilePathField(Field):
    def __init__(self, *args, **kwargs):
        models.FilePathField.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                            name=kwargs.get('name', None), 
                                            path=kwargs.get('path', ''), 
                                            match=kwargs.get('match', None), 
                                            recursive=kwargs.get('recursive', False), **kwargs)
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return String(length=self.max_length)

class FloatField(Field):
    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return Float()

class ImageField(FileField):
    def __init__(self, *args, **kwargs):
        models.ImageField.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                        name=kwargs.get('name', None), 
                                        width_field=kwargs.get('width_field', ''), 
                                        height_field=kwargs.get('height_field', None), **kwargs)
        FileField.__init__(self, *args, **kwargs)

class IntegerField(Field):
    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return Integer()

class IPAddressField(Field):
    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return String(length=self.max_length)

class NullBooleanField(Field):
    def __init__(self, *args, **kwargs):
        models.NullBooleanField.__init__(self, *args, **kwargs)
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return Boolean()

class PhoneNumberField(IntegerField):
    def __init__(self, *args, **kwargs):
        IntegerField.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        ''' This is a bit odd because in Django the PhoneNumberField descends
            from an IntegerField in a hacky way of getting around not 
            providing a max_length.  The database backends enforce the
            length as a varchar(20).
        '''
        return String(length=20)

class PositiveIntegerField(IntegerField):
    def __init__(self, *args, **kwargs):
        IntegerField.__init__(self, *args, **kwargs)

class PositiveSmallIntegerField(IntegerField):
    def __init__(self, *args, **kwargs):
        IntegerField.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return SmallInteger()

class SlugField(CharField):
    def __init__(self, *args, **kwargs):
        #FIXME: the metaclass for Fields gets called before the __init__ for
        #       SlugField, so the max_length fixup errors out before max_length
        #       has a chance to be set.  This problem occurs for all fields.
        kwargs['max_length'] = kwargs.pop('max_length', 50)        
        models.SlugField.__init__(self, *args, **kwargs)
        CharField.__init__(self, *args, **kwargs)

class SmallIntegerField(IntegerField):
    def __init__(self, *args, **kwargs):
        IntegerField.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return SmallInteger()

class TextField(Field):
    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return Text()

class TimeField(Field):
    def __init__(self, *args, **kwargs):
        models.TimeField.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                        name=kwargs.get('name', None), 
                                        auto_now=kwargs.get('auto_now', False), 
                                        auto_now_add=kwargs.get('auto_now_add', False), **kwargs)
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return Time()

class URLField(CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.pop('max_length', 200)
        models.URLField.__init__(self, verbose_name=kwargs.pop('verbose_name', None), 
                                       name=kwargs.pop('name', None), 
                                       verify_exists=kwargs.pop('verify_exists', True), **kwargs)
        CharField.__init__(self, *args, **kwargs)

class USStateField(Field):
    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return String(length=2)

class XMLField(TextField):
    def __init__(self, *args, **kwargs):
        models.XMLField.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                       name=kwargs.get('name', None), 
                                       schema_path=kwargs.get('schema_path', None), **kwargs)
        TextField.__init__(self, *args, **kwargs)

class OrderingField(IntegerField):
    def __init__(self, *args, **kwargs):
        OrderingField.__init__(self, *args, **kwargs)
        IntegerField.__init__(self, *args, **kwargs)
