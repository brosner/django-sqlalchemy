import datetime
from django_sqlalchemy.test import *
from apps.blog.models import Category, Post

class TestYear(object):
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
        Post.__table__.insert().execute({'id': 5, 'body': 'Intermediate Models - Will they ever happen?', 'category_id': c.id})

    def test_should_find_all_values_in_year(self):
        posts = Post.objects.filter(created_at__year=2007).order_by('id')
        assert 2 == posts.count()
        assert_equal([1, 2], [p.id for p in posts])

    def test_should_find_all_values_in_year_with_default(self):
        posts = Post.objects.filter(created_at__year=2008).order_by('id')
        if 2008 == datetime.date.today().year:
            assert 3 == posts.count()
            assert_equal([3, 4, 5], [p.id for p in posts])
        else:
            assert 2 == posts.count()
            assert_equal([3, 4], [p.id for p in posts])

    def test_should_find_all_values_excluded_from_year(self):
        posts = Post.objects.exclude(created_at__year=2007).order_by('id')
        assert 3 == posts.count()
        assert_equal([3, 4, 5], [p.id for p in posts])

    def test_should_find_all_values_excluded_from_year_with_default(self):
        posts = Post.objects.exclude(created_at__year=2008).order_by('id')
        if 2008 == datetime.date.today().year:
            assert 2 == posts.count()
            assert_equal([1, 2], [p.id for p in posts])
        else:
            assert 3 == posts.count()
            assert_equal([1, 2, 5], [p.id for p in posts])
