from django.template.defaultfilters import slugify
from django_sqlalchemy import models
import managers

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    # parent = models.ForeignKey('self', null=True, blank=True, db_column='parent_id', related_name='children')
    active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    
    objects = managers.CategoryManager()
    
    def __unicode__(self):
        return self.name

    def save(self):
        slug = slugify(self.name)
        super(Category, self).save()
