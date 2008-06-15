from django_sqlalchemy.test import *
from apps.categories.models import Category

"""
The models we are using in this test is a self referential category model.
Also it contains a custom manager that overrides the default get_query_set
to only return active items.
"""

class TestIsNull(object):    
    def setup(self):
        Category.__table__.insert().execute(
            {'name': 'Python', 'slug': 'python', 'description': 'We got your whitespace.'}, 
            {'name': 'PHP', 'slug': 'php', 'description': 'What is a namespace?'}, 
            {'name': 'Ruby', 'slug': 'ruby', 'description': 'Spankin the monkey patch'}, 
            {'name': 'Smalltalk', 'slug': 'smalltalk', 'description': 'No symbol left unturned'}, 
            {'name': 'CSharp', 'slug': 'csharp'})
        Category.__table__.insert().execute(
            {'name': 'Modula', 'slug': 'modula', 'active': False},
            {'name': 'Algol', 'slug': 'algol', 'active': False})
        # Category.__table__.insert().execute(
        #             {'name': 'Django', 'slug': 'django', 'description': 'For perfectionists', 'parent': 1}, 
        #             {'name': 'Pylons', 'slug': 'pylons', 'parent': 1}, 
        #             {'name': 'Turbo Gears', 'slug': 'turbo-gears', 'description': 'Just like Turbo Pylons', 'parent': 1}, 
        #             {'name': 'Cake', 'slug': 'cake', 'description': 'Have it and eat it too', 'parent': 2}, 
        #             {'name': 'Merb', 'slug': 'merb', 'description': 'Because it is not Rails', 'parent': 3}) 

    def test_should_find_all_items_where_field_is_null(self):
        categories = Category.objects.filter(description__isnull=True).order_by('name')
        assert_equal(['CSharp'], [c.name for c in categories])
        assert 1 == categories.count()
    
    def test_should_find_all_items_where_field_is_not_null(self):
        categories = Category.objects.exclude(description__isnull=True).order_by('name')
        assert_equal(['PHP', 'Python', 'Ruby', 'Smalltalk'], [c.name for c in categories])
        assert 4 == categories.count()

    def test_should_find_all_items_where_field_is_equal_to_none(self):
        categories = Category.objects.filter(description=None).order_by('name')
        assert_equal(['CSharp'], [c.name for c in categories])
        assert 1 == categories.count()
    
    def test_should_find_all_items_where_field_is_not_equal_to_none(self):
        categories = Category.objects.exclude(description=None).order_by('name')
        assert_equal(['PHP', 'Python', 'Ruby', 'Smalltalk'], [c.name for c in categories])
        assert 4 == categories.count()

    @testing.future
    def test_should_find_all_related_items_where_field_is_null(self):
        categories = Category.objects.filter(parent__description__isnull=True).order_by('name')
        assert_equal(['CSharp'], [c.name for c in categories])
        assert 1 == categories.count()
