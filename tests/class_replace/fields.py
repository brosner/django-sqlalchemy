"""
Utilities for providing backwards compatibility for the maxlength argument,
which has been replaced by max_length. See ticket #2101.
"""

from warnings import warn

def get_maxlength(self):
    return self.max_length

def set_maxlength(self, value):
    self.max_length = value

def legacy_maxlength(max_length, maxlength):
    """
    Consolidates max_length and maxlength, providing backwards compatibilty
    for the legacy "maxlength" argument.

    If one of max_length or maxlength is given, then that value is returned.
    If both are given, a TypeError is raised. If maxlength is used at all, a
    deprecation warning is issued.
    """
    if maxlength is not None:
        warn("maxlength is deprecated. Use max_length instead.", DeprecationWarning, stacklevel=3)
        if max_length is not None:
            raise TypeError("Field cannot take both the max_length argument and the legacy maxlength argument.")
        max_length = maxlength
    return max_length

def remove_maxlength(func):
    """
    A decorator to be used on a class's __init__ that provides backwards
    compatibilty for the legacy "maxlength" keyword argument, i.e.
        name = models.CharField(maxlength=20)

    It does this by changing the passed "maxlength" keyword argument
    (if it exists) into a "max_length" keyword argument.
    """
    def inner(self, *args, **kwargs):
        max_length = kwargs.get('max_length', None)
        # pop maxlength because we don't want this going to __init__.
        maxlength = kwargs.pop('maxlength', None)
        max_length = legacy_maxlength(max_length, maxlength)
        # Only set the max_length keyword argument if we got a value back.
        if max_length is not None:
            kwargs['max_length'] = max_length
        func(self, *args, **kwargs)
    return inner

class LegacyMaxlength(type):
    """
    Metaclass for providing backwards compatibility support for the
    "maxlength" keyword argument.
    """
    def __init__(cls, name, bases, attrs):
        super(LegacyMaxlength, cls).__init__(name, bases, attrs)
        # Decorate the class's __init__ to remove any maxlength keyword.
        cls.__init__ = remove_maxlength(cls.__init__)
        # Support accessing and setting to the legacy maxlength attribute.
        cls.maxlength = property(get_maxlength, set_maxlength)

import types

class MethodContainer(object):
    pass

def unbound_method_to_callable(func_or_cls):
    """Adjust the incoming callable such that a 'self' argument is not required."""

    if isinstance(func_or_cls, types.MethodType) and not func_or_cls.im_self:
        return func_or_cls.im_func
    else:
        return func_or_cls

class ClassReplacer(object):    
    def __init__(self, klass, metaclass=None):
        self.klass = klass
        self.metaclass = metaclass
    
    def __call__(self, name, bases, attrs):
        for n, v in attrs.items():
            if n in ("__class__", "__bases__", "__module__"):
                continue
            if n == "__metaclass__" and self.metaclass:
                setattr(self.klass, "__metaclass__", self.metaclass(self.klass.__class__.__name__, (), {}))
            else:
                # if the attribute exists in the original class then stuff it in the _original inner class 
                if hasattr(self.klass, n):
                    if not hasattr(self.klass, "_original"):
                        setattr(self.klass, "_original", MethodContainer())
                    member = unbound_method_to_callable(getattr(self.klass, n))
                    setattr(self.klass._original, n, member)
                # add the attribute to the original class
                setattr(self.klass, n, v)
        return self.klass

def MixIn(klass, mixin, include_private=True, ancestor=False):
    if ancestor:
        if mixin not in klass.__bases__:
            klass.__bases__ = (mixin,) + klass.__bases__
    else:
        # Recursively traverse the mix-in ancestor
        # classes in order to support inheritance
        bases = list(mixin.__bases__)
        bases.reverse()
        for base in bases:
            MixIn(klass, base, include_private, ancestor)
        # Install the mix-in methods into the class
        for name in dir(mixin):
            if name in ("__class__", "__bases__", "__module__", "__dict__"):
                continue
            if include_private and name in ("__init__", "__new__", "__metaclass__") or not name.startswith('__'):
                member = getattr(mixin, name)
                if type(member) is types.MethodType:
                    member = member.im_func
                setattr(klass, name, member)

import sys


class Field(object):
    # Provide backwards compatibility for the maxlength attribute and
    # argument for this class and all subclasses.
    __metaclass__ = LegacyMaxlength

    def __init__(self, db_column=None):
        print "In Field.__init__"
        self.db_column = db_column
    
    def methodtest(self):
        print "Field.methodtest"

class AutoField(Field):
    def __init__(self, *args, **kwargs):
        print "In AutoField.__init__"        
        Field.__init__(self, *args, **kwargs)

    def method4(self):
        """docstring for method4"""
        print "AutoField.method4"

######################################################################################################

class MyField(Field):
    # __metaclass__ = ClassReplacer(Field)
    
    sa_column = 3
        
    def method2(self):
        return "I'm in your codz, stealing your methodz."

    def method3(self):
        return self.db_column

    def get_sa_column(self):
        return self.sa_column
    
    def sa_column_type(self):
        raise NotImplementedError()

MixIn(Field, MyField, include_private=False)

class MyAutoField(MyField, Field):
    __metaclass__ = ClassReplacer(AutoField)
    
    def __init__(self, *args, **kwargs):
        print "In MyAutoField.__init__"
        self._original.__init__(self, *args, **kwargs)
    
    def sa_column_type(self):
        return Integer()

    def method4(self):
        """docstring for method4"""
        print "MyAutoField.method4"

# MixIn(AutoField, MyAutoField, ancestor=True)
a = AutoField()
b = AutoField()
b.sa_column = 4

# MixIn(ModelBase, MyModelBase)
# MixIn(Model, MyModel)
