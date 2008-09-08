from django_sqlalchemy.test import *
from django_sqlalchemy.backend import session
from apps.events.models import Owner, VenueInfo, Event

class TestValues(object):
    def setup(self):
        session.add_all([
            Owner(name='Luiji Roscoe', phone='557-895-9687'), 
            Owner(name='Jeffrey Gross-Bach'),
            Owner(name='Luiji Rosso', phone='557-895-9687')])

        session.add_all([
            VenueInfo(name='Rock and Roll Palace', address='123 Main St.', phone='408-123-4567', owner=Owner.query.get(1)), 
            VenueInfo(name='The Big and Mighty', address='555 Fifth Third St.', phone='502-555-1212', owner=Owner.query.get(2)),
            VenueInfo(name='The Mighty and Big', address='545 Fifth Third St.', phone='502-505-2121', owner=Owner.query.get(2))])

        v = VenueInfo.query.filter_by(name='Rock and Roll Palace').one()
        session.add_all([
            Event(name='Molly and the Malones', venue_info_id=v.id, body='A rocking Irish shindig.'),
            Event(name='Johnny Bee Good', venue_info_id=v.id, body='Classic rock covers all done up in a bumblebee tuna outfit.'),
            Event(name='JoJo Rock Show', venue_info_id=v.id, body='Fem rock, rocking you hard.')])
        
        v = VenueInfo.query.filter_by(name='The Big and Mighty').one()
        session.add_all([
            Event(name='Piggy Elk and the Elkhorns', venue_info_id=v.id, body='Quintet of big band sound.'),
            Event(name='Cello Nightly', venue_info_id=v.id, body='Smooth classics by Jim Nightly.')])

        v = VenueInfo.query.filter_by(name='The Mighty and Big').one()
        session.add_all([
            Event(name='Johnny Come Lately', venue_info_id=v.id, body='A Kegle Performance Piece'),
            Event(name='Headbangers Ball', venue_info_id=v.id, body='Dress up or not, but come rockin.')])

    def test_should_return_values_from_table(self):
        assert_equal([{'name': u'Luiji Roscoe'}, 
                      {'name': u'Jeffrey Gross-Bach'}, 
                      {'name': u'Luiji Rosso'}], list(Owner.objects.values('name')))

    def test_should_return_multiple_values_from_table(self):
        assert_equal([{'id': 1, 'name': u'Luiji Roscoe'}, 
                      {'id': 2, 'name': u'Jeffrey Gross-Bach'}, 
                      {'id': 3, 'name': u'Luiji Rosso'}], list(Owner.objects.values('id', 'name')))

    def test_should_maintain_order_of_specified_values(self):
        assert_equal([{'name': u'Luiji Roscoe', 'id': 1}, 
                      {'name': u'Jeffrey Gross-Bach', 'id': 2}, 
                      {'name': u'Luiji Rosso', 'id': 3}], list(Owner.objects.values('name', 'id')))

    def test_should_return_values_of_foreign_key_item(self):
        assert_equal([{'name': u'Luiji Roscoe', 'id': 1}, 
                      {'name': u'Jeffrey Gross-Bach', 'id': 2}, 
                      {'name': u'Luiji Rosso', 'id': 3}], list(VenueInfo.objects.values('owner')))

    def test_should_return_values_from_foreign_tables(self):
        pass

    def test_should_return_only_distinct_values(self):
        assert_equal(2, Owner.objects.values('phone').distinct().count())

    def test_should_return_field_id_in_values(self):
        assert_contains('owner_id', list(VenueInfo.objects.values()[0]))

    def test_should_return_field_id_if_specified_explicitely(self):
        assert_equal([{'owner_id': 1}, {'owner_id': 2}, {'owner_id': 2}], 
                     list(VenueInfo.objects.values('owner_id')))

    def test_should_return_field_name_if_specified_explicitely(self):
        assert_equal([{'owner': 1}, {'owner': 2}, {'owner': 2}], 
                     list(VenueInfo.objects.values('owner')))


"""
# Create something with a duplicate 'name' so that we can test multi-column
# cases (which require some tricky SQL transformations under the covers).
>>> xx = Item(name='four', created=time1, creator=a2, note=n1)
>>> xx.save()
>>> Item.objects.exclude(name='two').values('creator', 'name').distinct().count()
4
>>> Item.objects.exclude(name='two').extra(select={'foo': '%s'}, select_params=(1,)).values('creator', 'name', 'foo').distinct().count()
4
>>> Item.objects.exclude(name='two').extra(select={'foo': '%s'}, select_params=(1,)).values('creator', 'name').distinct().count()
4

>>> qs = Ranking.objects.extra(select={'good': 'case when rank > 2 then 1 else 0 end'})
>>> [o.good for o in qs.extra(order_by=('-good',))] == [True, False, False]
True
>>> qs.extra(order_by=('-good', 'id'))
[<Ranking: 3: a1>, <Ranking: 2: a2>, <Ranking: 1: a3>]

# Despite having some extra aliases in the query, we can still omit them in a
# values() query.
>>> qs.values('id', 'rank').order_by('id')
[{'id': 1, 'rank': 2}, {'id': 2, 'rank': 1}, {'id': 3, 'rank': 3}]

Ordering columns must be included in the output columns. Note that this means
results that might otherwise be distinct are not (if there are multiple values
in the ordering cols), as in this example. This isn't a bug; it's a warning to
be careful with the selection of ordering columns.

>>> Note.objects.values('misc').distinct().order_by('note', '-misc')
[{'misc': u'foo'}, {'misc': u'bar'}, {'misc': u'foo'}]

"""
