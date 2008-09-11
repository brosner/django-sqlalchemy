from django.db import models
from django.db.models.fields import NOT_PROVIDED
from django.conf import settings

from sqlalchemy import Column
from sqlalchemy.orm import deferred, synonym
from sqlalchemy.types import *

from django_sqlalchemy import utils

class DSField(models.Field):
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

utils.MixIn(models.Field, DSField, include_private=False)

class DSAutoField(models.Field, DSField):
    __metaclass__ = utils.ClassReplacer(models.AutoField)
    
    def sa_column_kwargs(self):
        kwargs = dict(primary_key=True)
        base = super(DSAutoField, self).sa_column_kwargs()
        base.update(kwargs)
        return base
    
    def sa_column_type(self):
        return Integer()

class DSBooleanField(models.Field, DSField):
    __metaclass__ = utils.ClassReplacer(models.BooleanField)

    def sa_column_type(self):
        return Boolean()
    
class DSCharField(models.Field, DSField):
    __metaclass__ = utils.ClassReplacer(models.CharField)
    
    def sa_column_type(self):
        return String(length=self.max_length)

class DSCommaSeparatedIntegerField(models.CharField, DSCharField):
    __metaclass__ = utils.ClassReplacer(models.CommaSeparatedIntegerField)
    
class DSDateField(models.Field, DSField):
    __metaclass__ = utils.ClassReplacer(models.DateField)

    def __init__(self, verbose_name=None, name=None, auto_now=False, auto_now_add=False, **kwargs):
        self.onupdate = kwargs.pop('onupdate', None)
        self._original.__init__(self, verbose_name=verbose_name, 
                                        name=name, 
                                        auto_now=auto_now, 
                                        auto_now_add=auto_now_add, **kwargs)
    
    def sa_column_kwargs(self):
        # TODO: can't handle init in inherited classes
        # need to handle auto_now and auto_now_add
        # kwargs = dict(onupdate=self.onupdate)
        base = super(DSDateField, self).sa_column_kwargs()
        # base.update(kwargs)
        return base
    
    def sa_column_type(self):
        return Date()

class DSDateTimeField(DSDateField):
    __metaclass__ = utils.ClassReplacer(models.DateTimeField)

    def sa_column_type(self):
        return DateTime()

class DSDecimalField(models.Field, DSField):
    __metaclass__ = utils.ClassReplacer(models.DecimalField)

    def __init__(self, *args, **kwargs):
        self._original.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                           name=kwargs.get('name', None), 
                                           max_digits=kwargs.get('max_digits', None), 
                                           decimal_places=kwargs.get('decimal_places', None), **kwargs)    
    def sa_column_kwargs(self):
        kwargs = dict(precision=self.decimal_places, length=self.max_digits)
        base = super(DSDecimalField, self).sa_column_kwargs()
        base.update(kwargs)
        return base

    def sa_column_type(self):
        return Numeric()

class DSEmailField(models.CharField, DSCharField):
    __metaclass__ = utils.ClassReplacer(models.EmailField)
    
#class DSFileField(models.Field, DSField):
    #__metaclass__ = utils.ClassReplacer(models.FileField)

    #def __init__(self, *args, **kwargs):
        #self._original.FileField.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                        #name=kwargs.get('name', None), 
                                        #upload_to=kwargs.get('upload_to', ''), **kwargs)    
    #def sa_column_type(self):
        #return String(length=self.max_length)

class DSFilePathField(models.Field, DSField):
    __metaclass__ = utils.ClassReplacer(models.FilePathField)

    def __init__(self, *args, **kwargs):
        self._original.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                            name=kwargs.get('name', None), 
                                            path=kwargs.get('path', ''), 
                                            match=kwargs.get('match', None), 
                                            recursive=kwargs.get('recursive', False), **kwargs)

    def sa_column_type(self):
        return String(length=self.max_length)

class DSFloatField(models.Field, DSField):
    __metaclass__ = utils.ClassReplacer(models.FloatField)

    def sa_column_type(self):
        return Float()

#class DSImageField(models.FileField, DSFileField):
    #__metaclass__ = utils.ClassReplacer(models.ImageField)

    ## def __init__(self, *args, **kwargs):
    ##     self._original.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
    ##                                     name=kwargs.get('name', None), 
    ##                                     width_field=kwargs.get('width_field', ''), 
    ##                                     height_field=kwargs.get('height_field', None), **kwargs)

class DSIntegerField(models.Field, DSField):
    __metaclass__ = utils.ClassReplacer(models.IntegerField)

    def sa_column_type(self):
        return Integer()

class DSIPAddressField(models.Field, DSField):
    __metaclass__ = utils.ClassReplacer(models.IPAddressField)

    def sa_column_type(self):
        return String(length=self.max_length)

class DSNullBooleanField(models.Field, DSField):
    __metaclass__ = utils.ClassReplacer(models.NullBooleanField)

    def sa_column_type(self):
        return Boolean()

class DSPositiveIntegerField(models.IntegerField, DSIntegerField):
    __metaclass__ = utils.ClassReplacer(models.PositiveIntegerField)

class DSPositiveSmallIntegerField(models.IntegerField, DSIntegerField):
    __metaclass__ = utils.ClassReplacer(models.PositiveSmallIntegerField)

    def sa_column_type(self):
        return SmallInteger()

class DSSlugField(models.CharField, DSCharField):
    __metaclass__ = utils.ClassReplacer(models.SlugField)

    # def __init__(self, *args, **kwargs):
    #     #FIXME: the metaclass for Fields gets called before the __init__ for
    #     #       SlugField, so the max_length fixup errors out before max_length
    #     #       has a chance to be set.  This problem occurs for all fields.
    #     # kwargs['max_length'] = kwargs.pop('max_length', 50)
    #     self._original.__init__(self, *args, **kwargs)

class DSSmallIntegerField(models.IntegerField, DSIntegerField):
    __metaclass__ = utils.ClassReplacer(models.SmallIntegerField)

    def sa_column_type(self):
        return SmallInteger()

class DSTextField(models.Field, DSField):
    __metaclass__ = utils.ClassReplacer(models.TextField)

    def sa_column_type(self):
        return Text()

class DSTimeField(models.Field, DSField):
    __metaclass__ = utils.ClassReplacer(models.TimeField)

    def __init__(self, *args, **kwargs):
        self._original.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
                                        name=kwargs.get('name', None), 
                                        auto_now=kwargs.get('auto_now', False), 
                                        auto_now_add=kwargs.get('auto_now_add', False), **kwargs)

    def sa_column_type(self):
        return Time()

class DSURLField(models.CharField, DSCharField):
    __metaclass__ = utils.ClassReplacer(models.URLField)

    # def __init__(self, *args, **kwargs):
    #     kwargs['max_length'] = kwargs.pop('max_length', 200)
    #     self._original.__init__(self, verbose_name=kwargs.pop('verbose_name', None), 
    #                                    name=kwargs.pop('name', None), 
    #                                    verify_exists=kwargs.pop('verify_exists', True), **kwargs)

class DSXMLField(models.TextField, DSTextField):
    __metaclass__ = utils.ClassReplacer(models.XMLField)

    # def __init__(self, *args, **kwargs):
    #     self._original.__init__(self, verbose_name=kwargs.get('verbose_name', None), 
    #                                    name=kwargs.get('name', None), 
    #                                    schema_path=kwargs.get('schema_path', None), **kwargs)

