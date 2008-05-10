from django.db import models

class CategoryManager(models.Manager):
    def get_query_set(self):
        return super(CategoryManager, self).get_query_set().filter(active=True)
