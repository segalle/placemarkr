from django.db import models
from django.contrib import auth
import datetime


class Place(models.Model):
    vendor_id = models.CharField(max_length=50, unique=True)
    data = models.TextField()

    def __unicode__(self):
        return self.data


class Placemark(models.Model):
    place = models.ForeignKey(Place, related_name='placemarks')
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    lat = models.FloatField()
    lng = models.FloatField()

    class Meta:
        unique_together = (("place", "city", "address", "lat", "lng"),)

class Vote(models.Model):
    placemark = models.ForeignKey(Placemark, related_name='votes')
    created_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(auth.models.User)
    possitive = models.BooleanField();

    class Meta:
        unique_together = (('placemark', 'user'),)