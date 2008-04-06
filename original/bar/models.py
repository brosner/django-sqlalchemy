
from django.db import models

class Tag(models.Model):
    tag = models.CharField(max_length=10, primary_key=True)

class Product(models.Model):
    name = models.CharField(max_length=18, primary_key=True)
    tags = models.ManyToManyField(Tag)
    
