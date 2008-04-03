import datetime
from django_sqlalchemy import models

class Category(models.Model):
    name = models.CharField(max_length=32)

    def __unicode__(self):
        return self.name

class Post(models.Model):
    created_at = models.DateTimeField(default=datetime.datetime.now)
    category = models.ForeignKey(Category)
    body = models.TextField()
    is_draft = models.BooleanField(default=False)

    def __unicode__(self):
        return self.body