import types
from django.conf import settings

__all__ = 'parse_db_uri', 'db_url', 'db_label'

def parse_db_uri():
    """
    Parse the dburi and pull out the full dburi and the label only
    """    
    db_url = getattr(settings, 'DJANGO_SQLALCHEMY_DBURI', "sqlite://")
    db_label = db_url[:db_url.index(':')]
    return (db_url, db_label)
db_url, db_label = parse_db_uri()

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
