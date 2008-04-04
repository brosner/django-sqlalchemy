from sqlalchemy import *
from sqlalchemy.orm import *

from sqlalchemy.orm.dynamic import DynaLoader, DynamicAttributeImpl
from sqlalchemy.orm.attributes import AttributeImpl

from django.db.models.fields.related import ForeignRelatedObjectsDescriptor

class WrappedDynaLoader(DynaLoader):
    """wrapper for Dynaloader strategy.
    
    Here, we just hook the "_register_attribute" call and set up
    our own "impl" class for the descriptor that's placed on the mapped
    class.  This is the part where the "attribute instrumentation" 
    branch provides a more "public" way of changing how instrumentation
    is configured.
    """
    def _register_attribute(self, *args, **kwargs):
        kwargs['impl_class'] = WrappedDynamicAttributeImpl
        return DynaLoader._register_attribute(self, *args, **kwargs)


class WrappedDynamicAttributeImpl(AttributeImpl):
    """wrapper for DynamicAttributeImpl.
    
    We use a wrapper and not a subclass so that the underlying DynamicAttributeImpl 
    can refer to itself and get the "unwrapped" behavior.    
    """
    def __init__(self, *args, **kwargs):
        self.wrapped = DynamicAttributeImpl(*args, **kwargs)
        
    def get(self, state, passive=False):
        ret = self.wrapped.get(state, passive=passive)
        if isinstance(ret, Query):
            return WrappedQuery(ret)
        else:
            return ret

# wrap all DynamicAttributeImpl methods on 
# WrappedDynamicAttributeImpl    
def _method_wrapper(name):
    def wrap(self, *args, **kwargs):
        return getattr(self.wrapped, name)(*args, **kwargs)
    wrap.__name__ = name  # setting __name__ doesn't work in py2.3; wrap in a try/except if needed
    return wrap
    
for name in [k for k in dir(DynamicAttributeImpl) if not k.startswith('_') and k not in WrappedDynamicAttributeImpl.__dict__]:
    setattr(WrappedDynamicAttributeImpl, name, _method_wrapper(name))
    

class WrappedQuery(object):
    """this is a 'fake' Query wrapper - replace this with your own."""
    def __init__(self, query):
        self.query = query
    
    def __iter__(self):
            return iter(self.query)
        
    def __getitem__(self, key):
        return self.query.__getitem__(key)
        
    def filter(self, crit):
        return WrappedQuery(self.query.filter(crit))


if __name__ == '__main__':
    # sample usage

    engine = create_engine('sqlite://')
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base(engine=engine)

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(Text)
        addresses = relation("Address", backref='user', strategy_class=WrappedDynaLoader)
    
    class Address(Base):
        __tablename__ = 'addresses'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.id'))
        email = Column(Text)
    
    Base.metadata.create_all()    
    sess = create_session()
    
    u1 = User(name='ed', addresses=[Address(email='foo'), Address(email='bar')])
    sess.save(u1)
    sess.flush()
    sess.clear()
    
    u1 = sess.query(User).get(u1.id)
    assert isinstance(u1.addresses, WrappedQuery)
    assert u1.addresses[0].email == 'foo'
    a = Address(email='bat', user=u1)
    sess.flush()
    assert u1.addresses.filter(Address.email=='bat')[0] is a