import types

class MethodContainer(object):
    pass

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
                setattr(self.klass, "_original", MethodContainer())
                if hasattr(self.klass, n):
                    setattr(self.klass._original, n, getattr(self.klass, n))
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
            MixIn(klass, base)
        # Install the mix-in methods into the class
        for name in dir(mixin):
            if name in ("__class__", "__bases__", "__module__", ):
                continue
            if include_private and name in ("__init__", "__new__", "__metaclass__") or not name.startswith('__'):
                setattr(klass, "_original", MethodContainer())
                if hasattr(klass, name):
                    setattr(klass._original, name, getattr(klass, name))
                member = getattr(mixin, name)
                if type(member) is types.MethodType:
                    member = member.im_func
                setattr(klass, name, member)

import sys

# django.db.models.base.ModelBase
class ModelBase(type):
    def __new__(cls, name, bases, attrs):
        print name
        print "ModelBase.__new__ called"                  
        newclass = super(ModelBase, cls).__new__(cls, name, bases, attrs)
        setattr(newclass, "test_ref", 2)
        return newclass

    def add_to_class(cls, name, value):
        print "ModelBase.add_to_class called"

# django.db.models.base.Model
class Model(object):
    __metaclass__ = ModelBase

    def __init__(self):
        print "Model.__init__ called"
    
    def method1(self):
        print "Model.method1 called"

######################################################################################################

def print_dynamic(self):
    print "dynamic method"

# django_sqlalchemy.models.base.ModelBase
class MyModelBase(ModelBase):  
    # def __new__(cls, name, bases, attrs):
        # try:
        #             parents = [b for b in bases if issubclass(b, MyModel)]
        #             if not parents:
        #                 return type.__new__(cls, name, bases, attrs)
        #         except NameError:
        #             return type.__new__(cls, name, bases, attrs)
        #         return cls._original.__new__(cls, name, bases, attrs)
            
    def __init__(cls, name, bases, attrs):
        setattr(cls, "method_dynamic", print_dynamic)
        print name
        print "MyModelBase.__init__ called"
        cls.test_ref = 4

# django_sqlalchemy.models.base.Model        
class MyModel(Model):
    __metaclass__ = MyModelBase
    
    def __test_method__(self):
        print "Test private method"
    
    def method2(self):
        print "MyModel.method2 called"

MixIn(ModelBase, MyModelBase)
MixIn(Model, MyModel)

######################################################################################################

class Category(Model):
    name = "Blah"
    
    def save(self):
        print "Category.save called"


