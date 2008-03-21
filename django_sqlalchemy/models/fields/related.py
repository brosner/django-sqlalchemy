
from django.db import models
from django_sqlalchemy.backend import metadata, Session
from django_sqlalchemy.models import Field

import sqlalchemy as sa

class ForeignKey(models.ForeignKey):
    def __init__(self, to, *args, **kwargs):
        self.sa_column = None   
        models.ForeignKey.__init__(self, to, *args, **kwargs)
    
    def create_column(self):
        # ForeignKey will be shadowed by the class inside of this method.
        fk_primary = list(self.rel.to.__table__.primary_key)[0]
        self.sa_column = sa.Column('%s_%s' % (
            self.rel.to._meta.object_name.lower(),
            self.rel.to._meta.pk.name), 
                             fk_primary.type, sa.ForeignKey(fk_primary))
        return self.sa_column

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
        # m2m field needs to know the model it belongs too for create_column
        # to work properly.
        self.model = cls
    