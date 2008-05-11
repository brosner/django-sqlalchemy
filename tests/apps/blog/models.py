import datetime
from django.db import models

class Category(models.Model):
    # name = models.CharField(max_length=32)

    def __unicode__(self):
        return self.name

# class Post(models.Model):
#     created_at = models.DateField(default=datetime.date.today)
#     category = models.ForeignKey(Category)
#     body = models.TextField()
#     is_draft = models.BooleanField(default=False)
# 
#     def __unicode__(self):
#         return self.body