from django_sqlalchemy.test import *
from apps.blog.models import Category, Post

class TestOneToMany(object):
    def setup(self):
        Category.__table__.insert().execute({'name': 'Python'}, 
            {'name': 'PHP'}, {'name': 'Ruby'}, {'name': 'Smalltalk'}, 
            {'name': 'CSharp'}, {'name': 'Modula'}, {'name': 'Algol'},
            {'name': 'Forth'}, {'name': 'Pascal'})
        
        c = Category.query.filter_by(name='Ruby').one()
        Post.__table__.insert().execute({'body': 'Riding the rails to profitability', 'category_id': c.id},
            {'body': 'Big pimpin in the Rails Ghetto', 'category_id': c.id},
            {'body': 'Has Many Bugs Through Rails', 'category_id': c.id},)
        c = Category.query.filter_by(name='Python').one()
        Post.__table__.insert().execute({'body': 'Why it is pronounced Jango and not DJ-Ango.', 'category_id': c.id},
            {'body': 'Intermediate Models - Will they ever happen?', 'category_id': c.id},)

    def test_referencing_related_table(self):
        c = Category.objects.get(name="Python")
        assert_equal(2, c.post_set.count())
        assert_equal(['Why it is pronounced Jango and not DJ-Ango.', 'Intermediate Models - Will they ever happen?'], [p.body for p in c.post_set.all()])

    def test_should_add_fk_item(self):
        c = Category.objects.get(name="Ruby")
        p = Post.objects.get(pk=2)
        p.category = c
        p.save()
        assert_equal(c.name, p.category.name)

