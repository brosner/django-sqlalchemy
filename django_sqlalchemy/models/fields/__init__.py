from django.db import models as dmodels
from django.db.models.fields import NOT_PROVIDED
from django.conf import settings

from sqlalchemy import Column
from sqlalchemy.orm import deferred, synonym
from sqlalchemy.types import *

from django_sqlalchemy import utils

class DSField(dmodels.Field):
    sa_column = None

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

utils.MixIn(dmodels.Field, DSField, include_private=False)

class DSAutoField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.AutoField)
    
    def __init__(self, *args, **kwargs):
        self._original.__init__(self, *args, **kwargs)
    
    def sa_column_kwargs(self):
        kwargs = dict(primary_key=True)
        base = super(DSAutoField, self).sa_column_kwargs()
        base.update(kwargs)
        return base
    
    def sa_column_type(self):
        return Integer()

class DSBooleanField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.BooleanField)

    def __init__(self, *args, **kwargs):
        models.BooleanField.__init__(self, *args, **kwargs)
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return Boolean()
    
class DSCharField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.CharField)
    
    def sa_column_type(self):
        return String(length=self.max_length)

class DSCommaSeparatedIntegerField(dmodels.CharField, DSCharField):
    __metaclass__ = utils.ClassReplacer(dmodels.CommaSeparatedIntegerField)

    def __init__(self, *args, **kwargs):
        CharField.__init__(self, *args, **kwargs)
    
class DSDateField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.DateField)

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
        base = super(DSDateField, self).sa_column_kwargs()
        base.update(kwargs)
        return base
    
    def sa_column_type(self):
        return Date()

class DSDateTimeField(dmodels.DateField, DSDateField):
    __metaclass__ = utils.ClassReplacer(dmodels.DateTimeField)

    def __init__(self, *args, **kwargs):
        DateField.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return DateTime()

class DSDecimalField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.DecimalField)

    def __init__(self, *args, **kwargs):
        models.DecimalField.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                           name=kwargs.get('name', None), 
                                           max_digits=kwargs.get('max_digits', None), 
                                           decimal_places=kwargs.get('decimal_places', None), **kwargs)
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_kwargs(self):
        kwargs = dict(precision=self.decimal_places, length=self.max_digits)
        base = super(DSDecimalField, self).sa_column_kwargs()
        base.update(kwargs)
        return base

    def sa_column_type(self):
        return Numeric()

class DSEmailField(dmodels.CharField, DSCharField):
    __metaclass__ = utils.ClassReplacer(dmodels.EmailField)

    def __init__(self, *args, **kwargs):
        models.EmailField.__init__(self,  *args, **kwargs)
        CharField.__init__(self, *args, **kwargs)
    
class DSFileField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.FileField)

    def __init__(self, *args, **kwargs):
        models.FileField.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                        name=kwargs.get('name', None), 
                                        upload_to=kwargs.get('upload_to', ''), **kwargs)
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return String(length=self.max_length)

class DSFilePathField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.FilePathField)

    def __init__(self, *args, **kwargs):
        models.FilePathField.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                            name=kwargs.get('name', None), 
                                            path=kwargs.get('path', ''), 
                                            match=kwargs.get('match', None), 
                                            recursive=kwargs.get('recursive', False), **kwargs)
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return String(length=self.max_length)

class DSFloatField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.FloatField)

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return Float()

class DSImageField(dmodels.FileField, DSFileField):
    __metaclass__ = utils.ClassReplacer(dmodels.ImageField)

    def __init__(self, *args, **kwargs):
        models.ImageField.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                        name=kwargs.get('name', None), 
                                        width_field=kwargs.get('width_field', ''), 
                                        height_field=kwargs.get('height_field', None), **kwargs)
        FileField.__init__(self, *args, **kwargs)

class DSIntegerField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.IntegerField)

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return Integer()

class DSIPAddressField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.IPAddressField)

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return String(length=self.max_length)

class DSNullBooleanField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.NullBooleanField)

    def __init__(self, *args, **kwargs):
        models.NullBooleanField.__init__(self, *args, **kwargs)
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return Boolean()

class DSPhoneNumberField(dmodels.IntegerField, DSIntegerField):
    __metaclass__ = utils.ClassReplacer(dmodels.PhoneNumberField)

    def __init__(self, *args, **kwargs):
        IntegerField.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        ''' This is a bit odd because in Django the PhoneNumberField descends
            from an IntegerField in a hacky way of getting around not 
            providing a max_length.  The database backends enforce the
            length as a varchar(20).
        '''
        return String(length=20)

class DSPositiveIntegerField(dmodels.IntegerField, DSIntegerField):
    __metaclass__ = utils.ClassReplacer(dmodels.PositiveIntegerField)

    def __init__(self, *args, **kwargs):
        IntegerField.__init__(self, *args, **kwargs)

class DSPositiveSmallIntegerField(dmodels.IntegerField, DSIntegerField):
    __metaclass__ = utils.ClassReplacer(dmodels.PositiveSmallIntegerField)

    def __init__(self, *args, **kwargs):
        IntegerField.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return SmallInteger()

class DSSlugField(dmodels.CharField, DSCharField):
    __metaclass__ = utils.ClassReplacer(dmodels.SlugField)

    def __init__(self, *args, **kwargs):
        #FIXME: the metaclass for Fields gets called before the __init__ for
        #       SlugField, so the max_length fixup errors out before max_length
        #       has a chance to be set.  This problem occurs for all fields.
        kwargs['max_length'] = kwargs.pop('max_length', 50)        
        models.SlugField.__init__(self, *args, **kwargs)
        CharField.__init__(self, *args, **kwargs)

class DSSmallIntegerField(dmodels.IntegerField, DSIntegerField):
    __metaclass__ = utils.ClassReplacer(dmodels.SmallIntegerField)

    def __init__(self, *args, **kwargs):
        IntegerField.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return SmallInteger()

class DSTextField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.TextField)

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return Text()

class DSTimeField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.TimeField)

    def __init__(self, *args, **kwargs):
        models.TimeField.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                        name=kwargs.get('name', None), 
                                        auto_now=kwargs.get('auto_now', False), 
                                        auto_now_add=kwargs.get('auto_now_add', False), **kwargs)
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return Time()

class DSURLField(dmodels.CharField, DSCharField):
    __metaclass__ = utils.ClassReplacer(dmodels.URLField)

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.pop('max_length', 200)
        models.URLField.__init__(self, verbose_name=kwargs.pop('verbose_name', None), 
                                       name=kwargs.pop('name', None), 
                                       verify_exists=kwargs.pop('verify_exists', True), **kwargs)
        CharField.__init__(self, *args, **kwargs)

class DSUSStateField(dmodels.Field, DSField):
    __metaclass__ = utils.ClassReplacer(dmodels.USStateField)

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return String(length=2)

class DSXMLField(dmodels.TextField, DSTextField):
    __metaclass__ = utils.ClassReplacer(dmodels.XMLField)

    def __init__(self, *args, **kwargs):
        models.XMLField.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                       name=kwargs.get('name', None), 
                                       schema_path=kwargs.get('schema_path', None), **kwargs)
        TextField.__init__(self, *args, **kwargs)

class DSOrderingField(dmodels.IntegerField, DSIntegerField):
    __metaclass__ = utils.ClassReplacer(dmodels.OrderingField)

    def __init__(self, *args, **kwargs):
        OrderingField.__init__(self, *args, **kwargs)
        IntegerField.__init__(self, *args, **kwargs)
