from nose.tools import *
from django_sqlalchemy.test import testing
from apps.blog.models import Category

class TestFirst(object):
    def setup(self):
        Category.__table__.insert().execute({'name': 'Python'}, 
            {'name': 'PHP'}, {'name': 'Ruby'}, {'name': 'Smalltalk'}, 
            {'name': 'CSharp'}, {'name': 'Modula'}, {'name': 'Algol'},
            {'name': 'Forth'}, {'name': 'Pascal'})

    def test_should_return_first_item_of_all(self):
        assert_equal(u'Python', Category.objects.all().first().name)
        
    def test_should_return_first_item_of_filter(self):
        assert_equal(u'Smalltalk', Category.objects.filter(name__contains='a').first().name)

    def test_should_return_none_when_called_on_empty_queryset(self):
        assert_equal(None, Category.objects.filter(name='foo').first())
    
    @raises(AttributeError)
    def test_should_raise_exception_after_a_get(self):
        Category.objects.get(name='Modula').first()
    
    def test_should_return_first_item_following_a_slice(self):
        assert_equal(u'Modula', Category.objects.filter(name__contains='a')[2:].first().name)
