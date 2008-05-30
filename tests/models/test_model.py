from django.db import models

from apps.blog.models import Post

class TestModel(object):
    def test_manager(self):
        assert type(Post._default_manager) is models.Manager
