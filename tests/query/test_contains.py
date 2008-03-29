from django_sqlalchemy.test import *
from apps.blog.models import Category

class TestContains(object):
    def setup(self):
        Category.__table__.insert().execute({'name': 'Python'}, 
            {'name': 'PHP'}, {'name': 'Ruby'}, {'name': 'Smalltalk'}, 
            {'name': 'CSharp'}, {'name': 'Modula'}, {'name': 'Algol'},
            {'name': 'Forth'}, {'name': 'Pascal'})

    @fails_on('sqlite')
    def test_should_contain_string_in_name(self):
        assert 4 == Category.objects.filter(name__contains='a').count()
        assert 1 == Category.objects.filter(name__contains='A').count()

    @fails_on_everything_except('sqlite')
    def test_should_contain_string_in_name_on_sqlite(self):
        assert 5 == Category.objects.filter(name__contains='a').count()
        assert 5 == Category.objects.filter(name__contains='A').count()

    def test_should_contain_string_in_name_regardless_of_case(self):
        assert 5 == Category.objects.filter(name__icontains='a').count()
        assert 5 == Category.objects.filter(name__icontains='A').count()
    
    def test_should_contain_string_at_beginning(self):
        category = Category.objects.filter(name__contains='Sma')
        assert 1 == category.count()
        assert_equal(u'Smalltalk', category[0].name)
    
    def test_should_contain_string_at_end(self):
        category = Category.objects.filter(name__contains='arp')
        assert 1 == category.count()
        assert_equal(u'CSharp', category[0].name)
