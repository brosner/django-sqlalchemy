from django_sqlalchemy.test import *
from apps.categories.models import Category

class TestIsNull(object):
    """
    The models we are using in this test is a self referential category model.
    Also it contains a custom manager that overrides the default get_query_set
    to only return active items.
    """
    
    def setup(self):
        Category.__table__.insert().execute(
            {'name': 'Python', 'description': 'We got your whitespace.'}, 
            {'name': 'PHP', 'description': 'What is a namespace?'}, 
            {'name': 'Ruby', 'description': 'Spankin the monkey patch'}, 
            {'name': 'Smalltalk', 'description': 'No symbol left unturned'}, 
            {'name': 'CSharp'}, 
            {'name': 'Modula', 'active': False}, 
            {'name': 'Algol', 'active': False})

    def test_should_find_all_items_where_field_is_null(self):
        categories = Category.objects.filter(description__isnull=True).order_by('name')
        assert_equal(['CSharp'], [c.name for c in categories])
        assert 1 == categories.count()
    
    def test_should_find_all_items_where_field_is_not_null(self):
        categories = Category.objects.exclude(description__isnull=True).order_by('name')
        assert_equal(['Python', 'PHP', 'Ruby', 'Smalltalk'], [c.name for c in categories])
        assert 4 == categories.count()

    def test_should_find_all_items_where_field_is_equal_to_none(self):
        categories = Category.objects.filter(description=None).order_by('name')
        assert_equal(['CSharp'], [c.name for c in categories])
        assert 1 == categories.count()
    
    def test_should_find_all_items_where_field_is_not_equal_to_none(self):
        categories = Category.objects.exclude(description=None).order_by('name')
        assert_equal(['Python', 'PHP', 'Ruby', 'Smalltalk'], [c.name for c in categories])
        assert 4 == categories.count()

    # def test_should_find_all_items_where_fk_is_null(self):
    #     assert 3 == Category.objects.filter(name__in=['Forth', 'Ruby', 'Python']).count()
    # 
    # def test_should_find_all_items_where_fk_is_not_null(self):
    #     assert 1 == Category.objects.filter(name__in=['Brainf**k', 'Smalltalk', 'FACTOR']).count()

# >>> Tag.objects.filter(parent__isnull=True).order_by('name')
# [<Tag: t1>]
# >>> Tag.objects.exclude(parent__isnull=True).order_by('name')
# [<Tag: t2>, <Tag: t3>, <Tag: t4>, <Tag: t5>]
