from django.db.models.query import ValuesQuerySet

class SQLAlchemyValuesQuerySet(ValuesQuerySet):
    def __init__(self, *args, **kwargs):
        super(SQLAlchemyValuesQuerySet, self).__init__(*args, **kwargs)

    def __iter__(self):
        return self.iterator()

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
            field_names = list(self._fields)            
        else:
            # Default to all fields.
            field_names = [f.attname for f in self.model._meta.fields]

        self.query._values(*field_names)
        self.field_names = field_names

class SQLAlchemyValuesListQuerySet(SQLAlchemyValuesQuerySet):
    def __iter__(self):
        return self.iterator()
    
    def iterator(self):
        import pdb
        pdb.set_trace()
        if self.flat and len(self._fields) == 1:
            for row in iter(self.query):
                yield row[0]
        else:
            for row in iter(self.query):
                yield row

    def _clone(self, *args, **kwargs):
        clone = super(SQLAlchemyValuesListQuerySet, self)._clone(*args, **kwargs)
        clone.flat = self.flat
        return clone