from django_sqlalchemy.test import *
from apps.blog.models import Category

class TestCreate(object):
    def setup(self):
        self.c = self.create_category()

    def test_should_create_a_new_record(self):        
        assert_equal('Python', self.c.name)
        assert_equal(1, Category.objects.count())
        
    def test_should_assign_the_pk(self):
        assert_not_none(self.c.pk)        

    @testing.future
    def test_should_set_the_date_default(self):
        assert_not_none(self.c.created_at)
    
    def test_should_create_duplicates(self):        
        c2 = self.create_category()
        assert_equal(c2.name, self.c.name)
        assert_equal(2, Category.objects.count())
        assert_not_equal(c2, self.c)

    def create_category(self, **options):
        return Category.objects.create(**dict({'name': 'Python'}, **options))
