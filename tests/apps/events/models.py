import datetime
from django.db import models

class VenueInfo(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.PhoneNumberField(blank=True)

class Event(models.Model):
    name = models.CharField(max_length=100)
    venue_info = models.ForeignKey(VenueInfo)
    event_date = models.DateField(default=datetime.date.today)
    body = models.TextField()
    
    def __unicode__(self):
        return self.body
