from nose.tools import *
from django_sqlalchemy.test import testing
from apps.blog.models import Category

class TestCount(object):
    def setup(self):
        Category.__table__.insert().execute({'name': 'Python'}, 
            {'name': 'PHP'}, {'name': 'Ruby'}, {'name': 'Smalltalk'}, 
            {'name': 'CSharp'}, {'name': 'Modula'}, {'name': 'Algol'},
            {'name': 'Forth'}, {'name': 'Pascal'})

    def test_should_get_zero_count_on_no_items(self):
        assert 0 == Category.objects.filter(name='Assembler').count()
        
    def test_should_get_count_on_filter(self):
        assert 1 == Category.objects.filter(name='Pascal').count()

    def test_should_get_count_on_an_and_filter(self):
        assert 1 == Category.objects.filter(name__contains='o', name__startswith='P').count()
    
    def test_should_get_count_on_all_items(self):
        assert 9 == Category.objects.all().count()
    
    @raises(AttributeError)
    def test_should_raise_exception_on_get_count(self):
        assert 1 == Category.objects.get(name='Python').count()
