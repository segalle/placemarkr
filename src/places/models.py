from django.contrib.auth.models import User
from django.db import models
import datetime
import json
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.conf import settings

class Dataset(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User)
    description = models.CharField(max_length=100)
    slug = models.SlugField()
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Dataset, self).save(*args, **kwargs)

class Place(models.Model):
    vendor_id = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    dataset = models.ForeignKey(Dataset, related_name="places")
    data = models.TextField()

    def __unicode__(self):
        return self.title

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
    
    def lat(self):
        placemark = self.get_leading_placemark()
        if placemark:
            return placemark.lat
        return None
        
    def lng(self):
        placemark = self.get_leading_placemark()
        if placemark:
            return placemark.lng
        return None
        
    def number_of_votes(self):
        return sum([pm.votes.count() for pm in self.placemarks.all()])
    
    def serialize_place(self):
        res = dict(vendor_id=self.vendor_id, 
                   title=self.title, 
                   address=self.address, 
                   city=self.city,
                   numberOfPlacemarks=self.placemarks.count(),
                   url=reverse('place', args=(self.id,)),
                   numberOfVotes=self.number_of_votes())
        placemark = self.get_leading_placemark()
        if placemark is not None:
            res['imageUrl'] = "../../" + placemark.image.url
        lat, lng = self.lat(), self.lng()
        if lat is not None:
            res['lat'] = lat
        if lng is not None:
            res['lng'] = lng
        return res

class Placemark(models.Model):
    place = models.ForeignKey(Place, related_name='placemarks')
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    lat = models.FloatField()
    lng = models.FloatField()
    user = models.ForeignKey(User, null=True, blank=True)
    image = models.ImageField(upload_to='streetview', blank=True, default=settings.MEDIA_URL + 'streetview/default.png')

    class Meta:
        unique_together = (("place", "city", "address", "lat", "lng"),)

    def __unicode__(self):
        return self.place.title

class Vote(models.Model):
    placemark = models.ForeignKey(Placemark, related_name='votes')
    created_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    positive = models.BooleanField();

    class Meta:
        unique_together = (('placemark', 'user'),)
        
