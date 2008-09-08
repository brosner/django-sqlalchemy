from django_sqlalchemy.test import *
from django_sqlalchemy.backend import metadata
from django.db import connection
from apps.blog.models import Category
from apps.news.models import Article

class TestIntrospection(object):
    def setup(self):
        self.im = connection.introspection
        self.cursor = connection.cursor()
        
    def test_should_get_table_list(self):
        table_list = self.im.get_table_list(self.cursor)
        assert_not_equal(len(table_list), 0)
        assert_true(Category.__table__.name in table_list)
        assert_true(Article.__table__.name in table_list)

    def test_should_get_table_description(self):
        table_description = self.im.get_table_description(self.cursor, Category.__table__.name)
        assert_not_none(table_description)
        assert_true(len(table_description) > 0)
        assert_equal(table_description[0][0], 'id')

    def test_should_get_relations(self):
        relations = self.im.get_relations(self.cursor, Article.__table__.name)
        assert_not_none(relations)
        assert_true(len(relations.items()) > 0)
        first_relation = relations.values()[0]
        assert_equal(first_relation[1], 'news_reporter')

    def test_should_get_indexes(self):
        indexes = self.im.get_indexes(self.cursor, Article.__table__.name)
        assert_not_none(indexes)
        assert_true(len(indexes.items()) > 0)
        assert_not_none(indexes.get('id'))
        assert_true(indexes['id']['primary_key'])
