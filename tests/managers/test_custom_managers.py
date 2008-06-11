from django_sqlalchemy.test import *
from django_sqlalchemy.backend import metadata
from django.db import models

# An example of a custom manager called "objects".

class PersonManager(models.Manager):
    def get_fun_people(self):
        return self.filter(fun=True)

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    fun = models.BooleanField()
    objects = PersonManager()

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

# An example of a custom manager that sets get_query_set().

class PublishedBookManager(models.Manager):
    def get_query_set(self):
        return super(PublishedBookManager, self).get_query_set().filter(is_published=True)

class Book(models.Model):
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=30)
    is_published = models.BooleanField()
    published_objects = PublishedBookManager()
    authors = models.ManyToManyField(Person, related_name='books')

    def __unicode__(self):
        return self.title

# An example of providing multiple custom managers.

class FastCarManager(models.Manager):
    def get_query_set(self):
        return super(FastCarManager, self).get_query_set().filter(top_speed__gt=150)

class Car(models.Model):
    name = models.CharField(max_length=10)
    mileage = models.IntegerField()
    top_speed = models.IntegerField(help_text="In miles per hour.")
    cars = models.Manager()
    fast_cars = FastCarManager()

    def __unicode__(self):
        return self.name

metadata.create_all()

p1 = Person(first_name='Bugs', last_name='Bunny', fun=True)
p1.save()
p2 = Person(first_name='Droopy', last_name='Dog', fun=False)
p2.save()

b1 = Book(title='How to program', author='Rodney Dangerfield', is_published=True)
b1.save()
b2 = Book(title='How to be smart', author='Albert Einstein', is_published=False)
b2.save()

c1 = Car(name='Corvette', mileage=21, top_speed=180)
c1.save()
c2 = Car(name='Neon', mileage=31, top_speed=100)
c2.save()

class TestCustomManager(object):
    def setup(self):
        pass

    def test_should_see_custom_manager_method(self):
        assert_list_same([p1], Person.objects.get_fun_people())

    def test_should_extend_default_manager(self):
        assert_instance_of(PublishedBookManager, p2.books)

    @raises(AttributeError)
    def test_should_not_contain_a_default_manager_if_custom_provided(self):
        Book.objects

    def test_should_extend_default_manager_with_related_manager(self):
        assert_instance_of(PersonManager, b2.authors)

    def test_should_only_return_published_objects(self):
        assert_list_same([b1], Book.published_objects.all())

    def test_should_order_by(self):
        assert_list_same([c1, c2], Car.cars.order_by('name'))
        assert_list_same([c1], Car.fast_cars.all())

    def test_should_return_default_manager_as_first_manager_in_class(self):
        assert_list_same([c1, c2], Car._default_manager.order_by('name'))
