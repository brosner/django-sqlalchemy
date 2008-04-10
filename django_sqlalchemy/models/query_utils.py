import operator

from django.db.models.sql.constants import *
from django.core.exceptions import FieldError
from django.utils.functional import curry
from sqlalchemy.sql import func, desc, asc

QUERY_TERMS_MAPPING = {
    'exact': operator.eq, 
    'iexact': operator.eq, 
    'gt': operator.gt, 
    'gte': operator.ge, 
    'lt': operator.lt, 
    'lte': operator.le
}

def _lookup_query_expression(lookup_type, field, value):
    if lookup_type in QUERY_TERMS_MAPPING:
        return curry(QUERY_TERMS_MAPPING[lookup_type], field, value)
    elif lookup_type == 'contains':
        return curry(field.like, '%%%s%%' % value)
    elif lookup_type == 'icontains':
        return curry(field.ilike, '%%%s%%' % value)
    elif lookup_type == 'in':
        return curry(field.in_, value)
    elif lookup_type == 'startswith':        
        return curry(field.like, '%s%%' % value)
    elif lookup_type == 'like':        
        return curry(field.like, '%s' % value)
    elif lookup_type == 'ilike':        
        return curry(field.ilike, '%s' % value)    
    elif lookup_type == 'istartswith':
        return curry(field.ilike, '%s%%' % value)
    elif lookup_type == 'endswith':
        return curry(field.like, '%%%s' % value)
    elif lookup_type == 'iendswith':
        return curry(field.ilike, '%%%s' % value)
    elif lookup_type == 'range':
        raise NotImplementedError()
    elif lookup_type == 'year':        
        raise NotImplementedError()
    elif lookup_type == 'month':
        raise NotImplementedError()
    elif lookup_type == 'day':
        raise NotImplementedError()
    elif lookup_type == 'search':
        raise NotImplementedError()
    elif lookup_type == 'regex':
        raise NotImplementedError()
    elif lookup_type == 'iregex':
        raise NotImplementedError()
    elif lookup_type == 'isnull': 
        if value:
            return curry(operator.eq, field, None)
        else:
            return curry(operator.ne, field, None)
    else:
        return None
        
def lookup_attname(meta, value):
    """
    This looks up the correct attribute name if the attribute is the
    pk attribute.
    """
    if value == 'pk':
        return meta.pk.attname
    else:
        field, model, direct, m2m = meta.get_field_by_name(value)
        return field.attname

def parse_filter(queryset, exclude, **kwargs):
    """
    Add a single filter to the query. The 'filter_expr' is a pair:
    (filter_string, value). E.g. ('name__contains', 'fred')
    
    If 'negate' is True, this is an exclude() filter. If 'trim' is True, we
    automatically trim the final join group (used internally when
    constructing nested queries).
    """
    
    query = queryset._clone()
    
    for filter_expr in [(k, v) for k, v in kwargs.items()]:
        arg, value = filter_expr
        parts = arg.split(LOOKUP_SEP)
        if not parts:
            raise FieldError("Cannot parse keyword query %r" % arg)
    
        # Work out the lookup type and remove it from 'parts', if necessary.
        if len(parts) == 1 or parts[-1] not in QUERY_TERMS:
            lookup_type = 'exact'
        else:
            lookup_type = parts.pop()
                
        if callable(value):
            value = value()
        
        # handle joins
        if len(parts) > 1:
            # break out the relationships from the lookup field
            fks = parts[0:-1]
            field = parts[-1]
            # add in the joins
            query.query = query.query.join(fks)
            # query.query.join([queryset.model._meta.get_field(f).attname for f in fks])
            # add in the parts which is always related to the last join point
            parts = [queryset.model._meta.get_field(fks[-1]).rel.to, field]
        else:
            parts = [queryset.model] + parts
        
        field = reduce(lambda x, y: getattr(x, lookup_attname(parts[0]._meta, y)), parts)
        op = _lookup_query_expression(lookup_type, field, value)
        expression = op()
        if exclude:
            expression = ~(expression)
        query.query = query.query.filter(expression)
    return query

def parse_order_by(queryset, *field_names):
    """
    TODO:add support for related fields
    Parse the order_by clause and return the modified query. 
    This does not consider related tables at this time.
    """
    for field in field_names:
        if field == '?':
            queryset.query = queryset.query.order_by(func.random())
            continue
        if isinstance(field, int):
            if field < 0:
                order = desc
                field = -field
            else:
                order = asc
            queryset.query = queryset.query.order_by(order(field))
            continue
        # evaluate the descending condition
        if '-' in field:
            order = desc
            field = field[1:]
        else:
            order = asc
        # old school django style for related fields
        if '.' in field:
            #TODO: this is not accurate
            queryset.query = queryset.query.order_by(order(condition))
        else:
            # normal order by
            #TODO: handle the join situation
            parts = [queryset.model] + field.split(LOOKUP_SEP)            
            condition = reduce(lambda x, y: getattr(x, y), parts)        
            queryset.query = queryset.query.order_by(order(condition))
    return queryset
