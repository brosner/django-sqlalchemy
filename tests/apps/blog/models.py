import datetime
from django_sqlalchemy import models

class Category(models.Model):
    name = models.CharField(max_length=32)
    
class Post(models.Model):
    created_at = models.DateTimeField(default=datetime.datetime.now)
    category = models.ForeignKey(Category)
    body = models.TextField()
    is_draft = models.BooleanField(default=False)
