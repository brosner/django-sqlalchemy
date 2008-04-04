from django.db.models.query import QuerySet
from sqlalchemy.orm.query import _ColumnEntity

class SQLAlchemyValuesQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        super(SQLAlchemyValuesQuerySet, self).__init__(*args, **kwargs)

    def __repr__(self):
        #FIXME: this causes a count query because of the dumb implementation
        # of len
        return repr(list(self))

    def iterator(self):
        for row in iter(self.query):
            yield dict(zip(self.field_names, row))

    def _setup_query(self):
        """
        Constructs the field_names list that the values query will be
        retrieving.

        Called by the _clone() method after initialising the rest of the
        instance.
        """
        if self._fields:
            # do something here to get around SA _values limitation
            field_names = [c.column for c in self.query._entities if isinstance(c, _ColumnEntity)] + list(self._fields) 
        else:
            # Default to all fields.
            field_names = [f.attname for f in self.model._meta.fields]

        self.query = self.query._values(*field_names)
        self.field_names = field_names

class SQLAlchemyValuesListQuerySet(SQLAlchemyValuesQuerySet):
    def iterator(self):
        if self.flat and len(self._fields) == 1:
            for row in iter(self.query):
                yield row[0]
        else:
            for row in iter(self.query):
                yield row
