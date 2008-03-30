from django_sqlalchemy.test import *
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned 
from apps.blog.models import Category

class TestGet(object):
    def setup(self):
        Category.__table__.insert().execute({'name': 'Python'}, 
            {'name': 'PHP'}, {'name': 'Ruby'}, {'name': 'Smalltalk'}, 
            {'name': 'CSharp'}, {'name': 'Modula'}, {'name': 'Algol'},
            {'name': 'Forth'}, {'name': 'Pascal'})

    def test_should_get_on_pk(self):
        assert_equal(u'Python', Category.objects.get(pk=1).name)
        
    def test_should_get_on_id(self):
        assert_equal(u'PHP', Category.objects.get(id=2).name)

    def test_should_get_on_value(self):
        assert_equal(u'Modula', Category.objects.get(name='Modula').name)

    def test_should_use_preexisting_filter(self):
        # this is different from SA which ignores preexisting filters
        category = Category.objects.get(pk=7)
        category2 = Category.objects.filter(pk__gt=6).get(pk=7)
        assert category2 is category
        assert category2.id == category.id

    @raises(ObjectDoesNotExist)    
    def test_should_use_preexisting_filter_and_raise_accordingly(self):
        Category.objects.filter(pk=9).get(pk=7)
    
    @raises(ObjectDoesNotExist)
    def test_should_raise_exception_when_no_items_returned(self):
        Category.objects.get(name='Foo')
    
    @raises(MultipleObjectsReturned)
    def test_should_raise_exception_when_more_than_one_item_is_returned(self):
        Category.objects.get(name__contains='a')
