import datetime
from django_sqlalchemy.test import *
from apps.blog.models import Category, Post

class TestRange(object):
    def setup(self):
        Category.__table__.insert().execute(
            {'id': 1, 'name': 'Python'}, 
            {'id': 2, 'name': 'PHP'}, 
            {'id': 3, 'name': 'Ruby'}, 
            {'id': 4, 'name': 'Smalltalk'}, 
            {'id': 5, 'name': 'CSharp'}, 
            {'id': 6, 'name': 'Modula'}, 
            {'id': 7, 'name': 'Algol'},
            {'id': 8, 'name': 'Forth'}, 
            {'id': 9, 'name': 'Pascal'})
        c = Category.query.filter_by(name='Ruby').one()
        Post.__table__.insert().execute(
            {'id': 1, 'body': 'Riding the rails to profitability', 'category_id': c.id, 'created_at': datetime.date(2007, 11, 10)},
            {'id': 2, 'body': 'Big pimpin in the Rails Ghetto', 'category_id': c.id, 'created_at': datetime.date(2007, 12, 31)},
            {'id': 3, 'body': 'Has Many Bugs Through Rails', 'category_id': c.id, 'created_at': datetime.date(2008, 04, 10)})
        c = Category.query.filter_by(name='Python').one()
        Post.__table__.insert().execute(
            {'id': 4, 'body': 'Why it is pronounced Jango and not DJ-Ango.', 'category_id': c.id, 'created_at': datetime.date(2008, 3, 5)})
        Post.__table__.insert().execute(
            {'id': 5, 'body': 'Intermediate Models - Will they ever happen?', 'category_id': c.id})

    def test_should_find_all_values_in_range(self):
        categories = Category.objects.filter(id__range=(3, 6)).order_by('id')
        assert 4 == categories.count()
        assert_equal(['Ruby', 'Smalltalk', 'CSharp', 'Modula'], [c.name for c in categories])

    def test_should_find_all_values_excluded_from_range(self):
        categories = Category.objects.exclude(pk__range=(3, 8)).order_by('id')
        assert 3 == categories.count()
        assert_equal(['Python', 'PHP', 'Pascal'], [c.name for c in categories])

    def test_should_ignore_values_not_in_range(self):
        categories = Category.objects.filter(id__range=(8, 12)).order_by('id')
        assert 2 == categories.count()
        assert_equal(['Forth', 'Pascal'], [c.name for c in categories])

    def test_should_return_single_item_if_range_is_same(self):
        categories = Category.objects.filter(id__range=(8, 8)).order_by('id')
        assert 1 == categories.count()
        assert_equal(['Forth'], [c.name for c in categories])

    def test_should_return_empty_if_end_range_is_before_start_range(self):
        categories = Category.objects.filter(id__range=(4, 2)).order_by('id')
        assert 0 == categories.count()
        assert_equal([], [c.name for c in categories])

    def test_should_find_all_values_in_date_range(self):
        startdate = datetime.date(2007, 8, 4)
        enddate = datetime.date(2008, 3, 18)
        posts = Post.objects.filter(created_at__range=(startdate, enddate)).order_by('id')
        assert 3 == posts.count()
        assert_equal([1, 2, 4], [p.id for p in posts])
