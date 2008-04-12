from django.db import models
from django.db.models.fields import NOT_PROVIDED
from django_sqlalchemy.backend import metadata, Session
from django_sqlalchemy.models import Field
from django_sqlalchemy.models.related import WrappedDynaLoader

import sqlalchemy as sa
from sqlalchemy import orm 

# class ForeignRelatedObjectsDescriptor(models.ForeignRelatedObjectsDescriptor):
#     # This class provides the functionality that makes the related-object
#     # managers available as attributes on a model class, for fields that have
#     # multiple "remote" values and have a ForeignKey pointed at them by
#     # some other model. In the example "poll.choice_set", the choice_set
#     # attribute is a ForeignRelatedObjectsDescriptor instance.
#     
#     def __get__(self, instance, instance_type=None):
#         if instance is None:
#             raise AttributeError, "Manager must be accessed via instance"
# 
#         rel_field = self.related.field
#         rel_model = self.related.model
# 
#         # Dynamically create a class that subclasses the related
#         # model's default manager.
#         superclass = self.related.model._default_manager.__class__
# 
#         class RelatedManager(superclass):
#             def get_query_set(self):
#                 return superclass.get_query_set(self).filter(**(self.core_filters))
# 
#             def add(self, *objs):
#                 for obj in objs:
#                     setattr(obj, rel_field.name, instance)
#                     obj.save()
#             add.alters_data = True
# 
#             def create(self, **kwargs):
#                 new_obj = self.model(**kwargs)
#                 self.add(new_obj)
#                 return new_obj
#             create.alters_data = True
# 
#             # remove() and clear() are only provided if the ForeignKey can have a value of null.
#             if rel_field.null:
#                 def remove(self, *objs):
#                     val = getattr(instance, rel_field.rel.get_related_field().attname)
#                     for obj in objs:
#                         # Is obj actually part of this descriptor set?
#                         if getattr(obj, rel_field.attname) == val:
#                             setattr(obj, rel_field.name, None)
#                             obj.save()
#                         else:
#                             raise rel_field.rel.to.DoesNotExist, "%r is not related to %r." % (obj, instance)
#                 remove.alters_data = True
# 
#                 def clear(self):
#                     for obj in self.all():
#                         setattr(obj, rel_field.name, None)
#                         obj.save()
#                 clear.alters_data = True
# 
#         manager = RelatedManager()
#         manager.core_filters = {'%s__pk' % rel_field.name: getattr(instance, rel_field.rel.get_related_field().attname)}
#         manager.model = self.related.model
# 
#         return manager
# 
#     def __set__(self, instance, value):
#         if instance is None:
#             raise AttributeError, "Manager must be accessed via instance"
# 
#         manager = self.__get__(instance)
#         # If the foreign key can support nulls, then completely clear the related set.
#         # Otherwise, just move the named objects into the set.
#         if self.related.field.null:
#             manager.clear()
#         manager.add(*value)

class ForeignKey(models.ForeignKey, Field):
    def __init__(self, to, *args, **kwargs):
        self.relation = kwargs.pop('relation', None)   
        models.ForeignKey.__init__(self, to, *args, **kwargs)
    
    def create_column(self):
        # try to get the ForeignKey using the SA Column.  If it doesn't work 
        # then it's likely a self-referential situation and then just build
        # up the quoted name.        
        options = self.rel.to._meta
        
        try:
            fk_primary = list(self.rel.to.__table__.primary_key)[0]
        except:
            fk_primary = '%s.%s' % (options.db_table, options.pk.name)

        #TODO: this should be refactored because the same logic is in the 
        #      Field __init__
        kwargs = dict(nullable=self.null,
                      index=True, unique=self.unique)
        if self.default is not NOT_PROVIDED:
            kwargs["default"] = self.default
        if self.primary_key:
            kwargs["primary_key"] = True
        
        self.sa_column = sa.Column(self.db_column or self.attname, 
                            options.pk.sa_column_type().__class__, 
                            sa.ForeignKey(fk_primary), **kwargs)
        self.sa_rel_column = self.relation or orm.relation(self.rel.to)
        # self.sa_rel_column = self.relation or orm.relation(self.rel.to, 
        #                                           backref=orm.backref(self.related_name, 
        #                                           lazy='dynamic'))
        
        # self.sa_rel_column = self.relation or orm.relation(self.rel.to, 
        #                                                   backref=orm.backref(self.related_name, 
        #                                                   strategy_class=WrappedDynaLoader))
        
        # self.sa_rel_column = orm.relation(self.rel.to, 
        #                                   primaryjoin=users_table.c.user_id==addresses_table.c.user_id, 
        #                                   foreign_keys=[addresses_table.c.user_id])
        return { self.sa_column.name: self.sa_column, 
                 options.object_name.lower(): self.sa_rel_column }

    def contribute_to_related_class(self, cls, related):
        # fk field needs to know the related_name it belongs to 
        # for create_column to work properly.
        super(ForeignKey, self).contribute_to_related_class(cls, related)
        self.related = related
        self.related_name = related.get_accessor_name()

class ManyToManyField(models.ManyToManyField, Field):
    def __init__(self, to, *args, **kwargs):
        super(self.__class__, self).__init__(to, *args, **kwargs)

    def add(self, *args, **kwargs):
        super(self.__class__, self).add(self, *args, **kwargs)
        Session.commit()
    
    def create_column(self):
        # m2m fields do not have a column
        self.sa_column = None
        self.__table__ = sa.Table(self.m2m_db_table(), metadata,
            sa.Column(self.m2m_column_name(), self.model._meta.pk.sa_column.type),
            sa.Column(self.m2m_reverse_name(), self.rel.to._meta.pk.sa_column.type))
        return self.sa_column
    
    def contribute_to_class(self, cls, name):
        super(ManyToManyField, self).contribute_to_class(cls, name)
        # m2m field needs to know the model it belongs to for create_column
        # to work properly.
        self.model = cls
    
