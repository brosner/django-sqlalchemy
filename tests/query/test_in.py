from django_sqlalchemy.test import *
from apps.blog.models import Category

class TestIn(object):
    def setup(self):
        Category.__table__.insert().execute({'name': 'Python'}, 
            {'name': 'PHP'}, {'name': 'Ruby'}, {'name': 'Smalltalk'}, 
            {'name': 'CSharp'}, {'name': 'Modula'}, {'name': 'Algol'},
            {'name': 'Forth'}, {'name': 'Pascal'})

    def test_should_find_all_values_in_list(self):
        assert 3 == Category.objects.filter(name__in=['Forth', 'Ruby', 'Python']).count()

    def test_should_ignore_values_not_in_field(self):
        assert 1 == Category.objects.filter(name__in=['Brainf**k', 'Smalltalk', 'FACTOR']).count()

    def test_should_ignore_duplicate_values(self):
        assert 2 == Category.objects.filter(name__in=['Modula', 'Smalltalk', 'Modula']).count()
    
    def test_should_not_find_items_regardless_of_case(self):
        category = Category.objects.filter(name__in=['SmAlLtAlK'])
        assert 0 == category.count()
