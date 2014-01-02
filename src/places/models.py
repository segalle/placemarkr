from django.contrib.auth.models import User
from django.db import models
import datetime
import json
from django.template.defaultfilters import slugify

class Dataset(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User)
    slug = models.SlugField()
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Dataset, self).save(*args, **kwargs)

class Place(models.Model):
    vendor_id = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    dataset = models.ForeignKey(Dataset, related_name="places")
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
            geometry_dic["coordinates"] = [placemark.lng, placemark.lat]

            feature_dic = {}
            feature_dic["properties"] = json.loads(self.data)
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
        if leading != None:
            print "Leading placemark was found for location #%s" % self.id
        else:
            print "No leading location for location #%s" % self.id
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
        
