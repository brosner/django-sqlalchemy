from django_sqlalchemy.test import *
from apps.blog.models import Category

class TestReverse(object):
    def setup(self):
        Category.__table__.insert().execute({'name': 'Python'}, 
            {'name': 'PHP'}, {'name': 'Ruby'}, {'name': 'Smalltalk'}, 
            {'name': 'CSharp'}, {'name': 'Modula'}, {'name': 'Algol'},
            {'name': 'Forth'}, {'name': 'Pascal'})

    def test_should_change_to_desc_order_from_asc(self):
        c1 = Category.objects.order_by('name')
        assert_equal([u'Smalltalk', u'Ruby', u'Python', u'Pascal', u'PHP', 
                      u'Modula', u'Forth', u'CSharp', u'Algol'], 
                     [c.name for c in c1.reverse()])

        c2 = Category.objects.order_by('name').filter(name__icontains='r')
        assert_equal([u'Ruby', u'Forth', u'CSharp'], 
                     [c.name for c in c2.reverse()])

    def test_should_change_to_asc_order_from_desc(self):
        c1 = Category.objects.order_by('-name')
        assert_equal([u'Algol', u'CSharp', u'Forth', u'Modula', u'PHP', 
                      u'Pascal', u'Python', u'Ruby', u'Smalltalk'], 
                     [c.name for c in c1.reverse()])

        c2 = Category.objects.order_by('-name').filter(name__icontains='r')
        assert_equal([u'CSharp', u'Forth', u'Ruby'], 
                     [c.name for c in c2.reverse()])

    def test_should_keep_same_order_when_reverse_twice(self):
        c1 = Category.objects.order_by('name').filter(name__icontains='r')
        assert_equal([u'CSharp', u'Forth', u'Ruby'], 
                     [c.name for c in c1.reverse().reverse()])

        c2 = Category.objects.order_by('-name').filter(name__icontains='r')
        assert_equal([u'Ruby', u'Forth', u'CSharp'], 
                     [c.name for c in c2.reverse().reverse()])

    def test_should_work_with_a_slice(self):
        c1 = Category.objects.order_by('name').reverse()
        assert_equal([u'Smalltalk', u'Ruby', u'Python'], 
                     [c.name for c in c1[:3]])

        c2 = Category.objects.order_by('-name').reverse()
        assert_equal([u'Algol', u'CSharp', u'Forth'], 
                     [c.name for c in c2[:3]])
        