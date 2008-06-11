from django_sqlalchemy.test import *
from django_sqlalchemy.backend import metadata
from django.db.models.manager import EmptyManager

class AnonymousUser(object):
    id = None
    username = ''
    is_staff = False
    is_active = False
    is_superuser = False
    groups = EmptyManager()

    def __unicode__(self):
        return 'AnonymousUser'


a = AnonymousUser()


class TestEmptyManager(object):
    def setup(self):
        pass

    def test_should_return_empty_manager(self):
        assert_list_same([], a.groups.all())
