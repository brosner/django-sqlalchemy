from django_sqlalchemy.test import *
from django_sqlalchemy.backend import session
from apps.blog.models import Category, Post
from apps.events.models import VenueInfo, Event

class TestOneToMany(object):
    def setup(self):
        Category.__table__.insert().execute({'name': 'Python'}, 
            {'name': 'PHP'}, {'name': 'Ruby'}, {'name': 'Smalltalk'}, 
            {'name': 'CSharp'}, {'name': 'Modula'}, {'name': 'Algol'},
            {'name': 'Forth'}, {'name': 'Pascal'})

        c = Category.query.filter_by(name='Ruby').one()
        Post.__table__.insert().execute({'body': 'Riding the rails to profitability', 'category_id': c.id},
            {'body': 'Big pimpin in the Rails Ghetto', 'category_id': c.id},
            {'body': 'Has Many Bugs Through Rails', 'category_id': c.id})
        c = Category.query.filter_by(name='Python').one()
        Post.__table__.insert().execute({'body': 'Why it is pronounced Jango and not DJ-Ango.', 'category_id': c.id},
            {'body': 'Intermediate Models - Will they ever happen?', 'category_id': c.id})

        session.add_all([
            VenueInfo(name='Rock and Roll Palace', address='123 Main St.', phone='408-123-4567'), 
            VenueInfo(name='The Big and Mighty', address='555 Fifth Third St.', phone='502-555-1212')])

        v = VenueInfo.query.filter_by(name='Rock and Roll Palace').one()
        session.add_all([
            Event(name='Molly and the Malones', venue_info_id=v.id, body='A rocking Irish shindig.'),
            Event(name='Johnny Bee Good', venue_info_id=v.id, body='Classic rock covers all done up in a bumblebee tuna outfit.'),
            Event(name='JoJo Rock Show', venue_info_id=v.id, body='Fem rock, rocking you hard.')])
        
        v = VenueInfo.query.filter_by(name='The Big and Mighty').one()
        session.add_all([
            Event(name='Piggy Elk and the Elkhorns', venue_info_id=v.id, body='Quintet of big band sound.'),
            Event(name='Cello Nightly', venue_info_id=v.id, body='Smooth classics by Jim Nightly.')])
    
    def test_should_add_fk_item(self):
        c = Category.objects.get(name="Ruby")
        p = Post.objects.get(pk=2)
        p.category = c
        p.save()
        assert_equal(c.name, p.category.name)

    def test_should_reference_related_table_items(self):
        c = Category.objects.get(name="Python")
        assert_equal(2, c.post_set.count())
        assert_equal(['Intermediate Models - Will they ever happen?',
                      'Why it is pronounced Jango and not DJ-Ango.'], 
                     [p.body for p in c.post_set.order_by('body')])

    def test_should_get_related_item(self):
        p = Post.objects.get(body='Has Many Bugs Through Rails')
        assert_equal(Category.objects.get(name='Ruby'), p.category)
    
    def test_should_query_across_related_item(self):
        p = Post.objects.filter(category__name__icontains='r')
        assert_equal(3, p.count())

    def test_should_query_across_related_item_with_different_naming(self):
        e = Event.objects.filter(venue_info__pk=2)
        assert_equal(2, e.count())
