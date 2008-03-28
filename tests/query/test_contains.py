from nose.tools import *
from django_sqlalchemy.test import testing
from apps.blog.models import Category

class TestContains(object):
    def setup(self):
        Category.__table__.insert().execute({'name': 'Python'}, 
            {'name': 'PHP'}, {'name': 'Ruby'}, {'name': 'Smalltalk'}, 
            {'name': 'CSharp'}, {'name': 'Modula'}, {'name': 'Algol'},
            {'name': 'Forth'}, {'name': 'Pascal'})

    @testing.fails_on('sqlite')
    def test_simple_contains(self):
        """
        Do a simple contains test without relationships
        """
        assert 4 == Category.objects.filter(name__contains='a').count()
        assert 1 == Category.objects.filter(name__contains='A').count()

    @testing.fails_on_everything_except('sqlite')
    def test_simple_contains_sqlite(self):
        """
        Do a simple contains test without relationships. Special
        case for sqlite because it does not respect case
        """
        assert 5 == Category.objects.filter(name__contains='a').count()
        assert 5 == Category.objects.filter(name__contains='A').count()

    def test_simple_icontains(self):
        """
        Do a simple icontains test without relationships
        """
        assert 5 == Category.objects.filter(name__icontains='a').count()
        assert 5 == Category.objects.filter(name__icontains='A').count()
    
    def test_simple_contains_at_beginning(self):
        """
        Do a simple contains test with the string at the beginning
        """
        category = Category.objects.filter(name__contains='Sma')
        assert 1 == category.count()
        assert_equal(u'Smalltalk', category[0].name)
    
    def test_simple_contains_at_end(self):
        """
        Do a simple contains test with the string at the beginning
        """
        category = Category.objects.filter(name__contains='arp')
        assert 1 == category.count()
        assert_equal(u'CSharp', category[0].name)
