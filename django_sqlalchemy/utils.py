import types
from django.conf import settings
from django.core.management.sql import installed_models

__all__ = 'parse_db_uri', 'db_url', 'db_label', 'CreationSniffer'

class CreationSniffer(object): 
    def __init__(self): 
        self.tables = set() 

    def __call__(self, event, table, bind): 
        self.tables.add(table)

    @property
    def models(self):
        return installed_models([table.name for table in self.tables]) 


def parse_db_uri():
    """
    Parse the dburi and pull out the full dburi and the label only
    """    
    db_url = getattr(settings, 'DJANGO_SQLALCHEMY_DBURI', "sqlite://")
    db_label = db_url[:db_url.index(':')]
    return (db_url, db_label)
db_url, db_label = parse_db_uri()


def unbound_method_to_callable(func_or_cls):
    """Adjust the incoming callable such that a 'self' argument is not required."""
    if isinstance(func_or_cls, types.MethodType) and not func_or_cls.im_self:
        return func_or_cls.im_func
    else:
        return func_or_cls


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


class MethodContainer(object):
    pass


class ClassReplacer(object):    
    def __init__(self, klass, metaclass=None):
        self.klass = klass
        self.metaclass = metaclass
    
    def __call__(self, name, bases, attrs):
        for n, v in attrs.iteritems():
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
