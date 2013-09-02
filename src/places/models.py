from django.db import models
import datetime


class Place(models.Model):
    vendor_id = models.CharField(max_length=50, unique=True)
    data = models.TextField()

    def __unicode__(self):
        return self.data


class Placemark(models.Model):
    place = models.ForeignKey(Place)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    lat = models.FloatField()
    lng = models.FloatField()

    class Meta:
        unique_together = (("place", "city", "address", "lat", "lng"),)

    def __unicode__(self):
        return self.unique_together
