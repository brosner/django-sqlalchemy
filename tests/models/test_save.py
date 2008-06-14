from django_sqlalchemy.test import *
from apps.categories.models import Category

class TestSave(object):
    def setup(self):
        Category.__table__.insert().execute(
            {'name': 'PHP', 'slug': 'php', 'description': 'What is a namespace?'}, 
            {'name': 'Ruby', 'slug': 'ruby', 'description': 'Spankin the monkey patch'}, 
            {'name': 'Smalltalk', 'slug': 'smalltalk', 'description': 'No symbol left unturned'}, 
            {'name': 'CSharp', 'slug': 'csharp'})

    def test_should_call_save(self):
        category = Category(name='Python', slug='python', description='We got your whitespace.')
        category.save()
        c = Category.objects.get(name='Python')
        assert_equal(c.name, category.name)

    def test_should_call_overriden_save(self):
        category = Category(name='Python', description='We got your whitespace.')
        category.save()
        assert_equal('python', category.slug)
