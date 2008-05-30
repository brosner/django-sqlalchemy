from django.db import models

class Reporter(models.Model):
    username = models.CharField(max_length=32)
    
class Source(models.Model):
    codename = models.CharField(max_length=32, null=False, default="Deep Throat")

    class Meta:
        db_table = "sources"
    
class Article(models.Model):
    sources = models.ManyToManyField(Source, related_name="stories")
    author = models.ForeignKey(Reporter, related_name="stories")
    content = models.TextField()

    class Meta:
        db_table = "articles"
