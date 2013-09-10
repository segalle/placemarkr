from django.contrib.auth.models import User
from django.db import models
import datetime
import json


class Place(models.Model):
    vendor_id = models.CharField(max_length=50, unique=True)
    data = models.TextField()

    def __unicode__(self):
        return self.data
    
    @property
    def data_as_dict(self):
        return json.loads(self.data)


class Placemark(models.Model):
    place = models.ForeignKey(Place, related_name='placemarks')
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    lat = models.FloatField()
    lng = models.FloatField()
    user = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        unique_together = (("place", "city", "address", "lat", "lng"),)

class Vote(models.Model):
    placemark = models.ForeignKey(Placemark, related_name='votes')
    created_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    positive = models.BooleanField();

    class Meta:
        unique_together = (('placemark', 'user'),)