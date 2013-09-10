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

    def export_feature(self):
        placemark = self.get_leading_placemark()
        if placemark != None:

            geometry_dic = {}
            geometry_dic["type"] = "Point"
            geometry_dic["coordinates"] = [placemark.lng, placemark.lng]

            feature_dic = {}
            feature_dic["properties"] = self.data
            feature_dic["type"] = "Feature"
            feature_dic["geometry"] = geometry_dic

        return feature_dic

    def get_leading_placemark(self):
        leading = None
        maxscore = 0
        for p in Placemark.objects.filter(place=self):
            counter = 0
            votes = Vote.objects.filter(placemark=p)

            for v in votes:
                if v.positive == True:
                    counter += 1
                else:
                    counter -= 1

            if leading != None:
                if counter >= 0 and counter >= maxscore:
                    leading = p
                    maxscore = counter
            else:
                if counter >= 0:
                    leading = p
                    maxscore = counter
        print leading
        return leading


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