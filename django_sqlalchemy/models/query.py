
from django.db.models.query import QuerySet
from django.db.models.sql.constants import ORDER_PATTERN

from sqlalchemy.orm import attributes
from sqlalchemy.orm.query import _ColumnEntity
from sqlalchemy.sql import operators

from django_sqlalchemy.models import query_utils as utils

class SQLAlchemyQuerySet(QuerySet):
    """
    A SQLAlchemy implementation of the Django QuerySet class
    """    
    def __init__(self, model=None, query=None):
        self.model = model
        self.query = query or self.model.query

    def __and__(self, other):
        combined = self._clone()
        combined.query.combine(other.query, sql.AND)
        return combined

    def __or__(self, other):
        combined = self._clone()
        combined.query.combine(other.query, sql.OR)
        return combined

    def __repr__(self):
        return repr(self.query.all())

    def __len__(self):
        return self.query.count()

    def __iter__(self):
        return self.iterator()
    
    def __getitem__(self, k):
        # TODO: with 0.5 SA executes this immediately, Django doesn't
        return self.query.__getitem__(k)

    ####################################
    # METHODS THAT DO DATABASE QUERIES #
    ####################################

    def iterator(self):
        """
        An iterator over the results from applying this QuerySet to the
        database.
        """
        return iter(self.query)

    def count(self):
        """
        Performs a SELECT COUNT() and returns the number of records as an
        integer.

        If the queryset is already cached (i.e. self._result_cache is set) this
        simply returns the length of the cached results set to avoid multiple
        SELECT COUNT(*) calls.
        """
        return self.query.count()

    def get(self, *args, **kwargs):
        """
        Performs the query and returns a single object matching the given
        keyword arguments.
        """
        obj = list(self.filter(*args, **kwargs).query[0:2])
        
        count = len(obj)
        if count == 1:
            return obj[0]
        elif count == 0:
            raise self.model.DoesNotExist("%s matching query does not exist."
                % self.model._meta.object_name)
        else:
            raise self.model.MultipleObjectsReturned("get() returned more than one %s -- it returned %s! Lookup parameters were %s"
                % (self.model._meta.object_name, count, kwargs))

    def first(self):
        """
        Return the first result of the underlying ``Query`` or None if the result doesn't contain any row.
        This results in an execution of the underlying query.
        """
        return self.query.first()

    def create(self, **kwargs):
        """
        Create a new object with the given kwargs, saving it to the database
        and returning the created object.
        """
        obj = self.model(**kwargs)
        obj.save()
        return obj

    def get_or_create(self, **kwargs):
        """
        Looks up an object with the given kwargs, creating one if necessary.
        Returns a tuple of (object, created), where created is a boolean
        specifying whether an object was created.
        """
        assert kwargs, \
                'get_or_create() must be passed at least one keyword argument'
        defaults = kwargs.pop('defaults', {})
        try:
            return self.get(**kwargs), False
        except self.model.DoesNotExist:
            try:
                params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
                params.update(defaults)
                obj = self.model(**params)
                obj.save()
                return obj, True
            except IntegrityError, e:
                return self.get(**kwargs), False

    def latest(self, field_name=None):
        """
        Returns the latest object, according to the model's 'get_latest_by'
        option or optional given field_name.
        """
        latest_by = field_name or self.model._meta.get_latest_by
        assert bool(latest_by), "latest() requires either a field_name parameter or 'get_latest_by' in the model"
        return self.order_by('-%s' % latest_by).first()

    def in_bulk(self, id_list):
        """
        Returns a dictionary mapping each of the given IDs to the object with
        that ID.
        """
        assert isinstance(id_list, (tuple,  list)), \
                "in_bulk() must be provided with a list of IDs."
        if not id_list:
            return {}
        qs = self.filter(**{'pk__in': id_list})
        return dict([(obj._get_pk_val(), obj) for obj in qs.iterator()])

    def delete(self):
        """
        Deletes the records in the current QuerySet.
        """
        # this approach although hackish results in one less
        # query, the select. This is more optimized than
        # Django's default. Hopefully it won't pressent a
        # problem.
        self.model.__table__.delete(self.query.compile()._whereclause).execute()
    delete.alters_data = True

    def update(self, **kwargs):
        """
        Updates all elements in the current QuerySet, setting all the given
        fields to the appropriate values.
        """
        values = self._parse_update_values(**kwargs)
        self.model.__table__.update(self.query.compile()._whereclause, values).execute()
    update.alters_data = True

    ##################################################
    # PUBLIC METHODS THAT RETURN A QUERYSET SUBCLASS #
    ##################################################

    def values(self, *fields):
        """
        Returns a list of dicts with only the columns specified. This works
        by wrapping the SQLAlchemyQuerySet in a SQLAlchemyValuesQuerySet
        that modifies the setup and iterator behavior.
        """
        from django_sqlalchemy.models.query import SQLAlchemyValuesQuerySet
        return self._clone(klass=SQLAlchemyValuesQuerySet, setup=True, _fields=fields)

    def values_list(self, *fields, **kwargs):
        """
        Returns a list of tuples for each of the fields specified.  This
        works by wrapping the SQLAlchemyQuerySet in a 
        SQLAlchemyValuesListQuerySet that modifies the iterator behavior.
        The flat option is only available with one column and flattens
        out the tuples into a simple list.
        """
        flat = kwargs.pop('flat', False)
        if kwargs:
            raise TypeError('Unexpected keyword arguments to values_list: %s'
                    % (kwargs.keys(),))
        if flat and len(fields) > 1:
            raise TypeError("'flat' is not valid when values_list is called with more than one field.")
        from django_sqlalchemy.models.query import SQLAlchemyValuesListQuerySet
        return self._clone(klass=SQLAlchemyValuesListQuerySet, setup=True, flat=flat,
                _fields=fields)

    def dates(self, field_name, kind, order='ASC'):
        """
        TODO: Need to map dates
        Returns a list of datetime objects representing all available dates
        for the given field_name, scoped to 'kind'.
        """
        assert kind in ("month", "year", "day"), \
                "'kind' must be one of 'year', 'month' or 'day'."
        assert order in ('ASC', 'DESC'), \
                "'order' must be either 'ASC' or 'DESC'."
        # Let the FieldDoesNotExist exception propagate.
        field = self.model._meta.get_field(field_name, many_to_many=False)
        assert isinstance(field, DateField), "%r isn't a DateField." \
                % field_name
        return self._clone(klass=DateQuerySet, setup=True, _field=field,
                _kind=kind, _order=order)

    ##################################################################
    # PUBLIC METHODS THAT ALTER ATTRIBUTES AND RETURN A NEW QUERYSET #
    ##################################################################

    def all(self):
        """
        Returns a new QuerySet that is a copy of the current one. This allows a
        QuerySet to proxy for a model manager in some cases.
        """
        return self._clone()

    def filter(self, *args, **kwargs):
        """
        Returns a new QuerySet instance with the args ANDed to the existing
        set.
        """
        return self._filter_or_exclude(False, *args, **kwargs)

    def exclude(self, *args, **kwargs):
        """
        Returns a new QuerySet instance with NOT (args) ANDed to the existing
        set.
        """
        return self._filter_or_exclude(True, *args, **kwargs)

    def _filter_or_exclude(self, exclude, *args, **kwargs):
        """
        This does the actual filtering, either combined filtering or 
        excluding depending on the exclude flag.
        """
        from django_sqlalchemy.models import query_utils
        return query_utils.parse_filter(self, exclude, **kwargs)

    def complex_filter(self, filter_obj):
        """
        TODO:need to map complex_filter
        Returns a new QuerySet instance with filter_obj added to the filters.
        filter_obj can be a Q object (or anything with an add_to_query()
        method) or a dictionary of keyword lookup arguments.

        This exists to support framework features such as 'limit_choices_to',
        and usually it will be more natural to use other methods.
        """
        if isinstance(filter_obj, Q) or hasattr(filter_obj, 'add_to_query'):
            return self._filter_or_exclude(None, filter_obj)
        else:
            return self._filter_or_exclude(None, **filter_obj)

    def options(self, *args):
        """Return a new QuerySet object, applying the given list of
        SQLAlchemy MapperOptions.
        """
        obj = self._clone()
        obj.query.options(*args)
        return obj

    def select_related(self, *fields, **kwargs):
        """
        TODO:need to map select_related
        Returns a new QuerySet instance that will select related objects. If
        fields are specified, they must be ForeignKey fields and only those
        related objects are included in the selection.
        """
        depth = kwargs.pop('depth', 0)
        if kwargs:
            raise TypeError('Unexpected keyword arguments to select_related: %s'
                    % (kwargs.keys(),))
        obj = self._clone()
        if fields:
            if depth:
                raise TypeError('Cannot pass both "depth" and fields to select_related()')
            obj.query.add_select_related(fields)
        else:
            obj.query.select_related = True
        if depth:
            obj.query.max_depth = depth
        return obj

    def order_by(self, *field_names):
        """
        Returns a new QuerySet instance with the ordering changed.
        These items are either field names (not column names) --
        possibly with a direction prefix ('-' or '?') -- or ordinals,
        corresponding to column positions in the 'select' list.
        """
        obj = self._clone()
        # django likes to clear the ordering, not sure why, because
        # this is inconsistent with the filter approach
        obj.query._order_by = False
        errors = []
        for item in field_names:
            if not ORDER_PATTERN.match(item):
                errors.append(item)
        if errors:
            raise FieldError('Invalid order_by arguments: %s' % errors)
        from django_sqlalchemy.models import query_utils
        return query_utils.parse_order_by(obj, *field_names)
    
    def distinct(self, true_or_false=True):
        """
        Returns a new QuerySet instance that will select only distinct results.
        """
        clone = self._clone()
        clone.query._distinct = true_or_false
        return clone

    def extra(self, select=None, where=None, params=None, tables=None,
            order_by=None):
        """
        TODO:need to map extra
        Add extra SQL fragments to the query.
        """
        assert self.query.can_filter(), \
                "Cannot change a query once a slice has been taken"
        clone = self._clone()
        if select:
            clone.query.extra_select.update(select)
        if where:
            clone.query.extra_where.extend(where)
        if params:
            clone.query.extra_params.extend(params)
        if tables:
            clone.query.extra_tables.extend(tables)
        if order_by:
            clone.query.extra_order_by = order_by
        return clone

    def reverse(self):
        """
        Reverses the ordering of the queryset.
        """
        clone = self._clone()
        for field in clone.query._order_by:
            if field.modifier == operators.desc_op: 
                field.modifier = operators.asc_op
            else:
                field.modifier = operators.desc_op
        return clone

    ###################
    # PRIVATE METHODS #
    ###################

    def _parse_update_values(self, **kwargs):
        from django.db.models.base import Model
        values = {}
        for name, val in kwargs.iteritems():
            field, model, direct, m2m = self.model._meta.get_field_by_name(name)
            if not direct or m2m:
                raise FieldError('Cannot update model field %r (only non-relations and foreign keys permitted).' % field)
            if field.rel and isinstance(val, Model):
                val = val.pk

            values[field.column] = val
        return values

    def _clone(self, klass=None, setup=False, **kwargs):
        if klass is None:
            klass = self.__class__
        c = klass(model=self.model, query=self.query._clone())
        c.__dict__.update(kwargs)
        if setup and hasattr(c, '_setup_query'):
            c._setup_query()
        return c


class SQLAlchemyValuesQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        self.field_names = []
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
            self.field_names = list(self._fields) + self.field_names            
        else:
            # Default to all fields.
            self.field_names = [f.attname for f in self.model._meta.fields]

        field_names = utils.fields_to_sa_columns(self, *self.field_names)
        self.query = self.query.values(*field_names)

class SQLAlchemyValuesListQuerySet(SQLAlchemyValuesQuerySet):
    def iterator(self):
        if self.flat and len(self._fields) == 1:
            for row in iter(self.query):
                yield row[0]
        else:
            for row in iter(self.query):
                yield row
