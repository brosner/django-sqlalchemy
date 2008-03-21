
from django_sqlalchemy import models

class Tag(models.Model):
    tag = models.CharField(max_length=10)

class Product(models.Model):
    name = models.CharField(max_length=18)
    tags = models.ManyToManyField(Tag)
    
