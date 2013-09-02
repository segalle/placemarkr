from django.db import models
import requests
import json

class CacheItem(models.Model):
    locality = models.CharField(max_length = 200)
    address = models.CharField(max_length = 200)
    result = models.TextField()

    class Meta:
        unique_together = (('locality', 'address'),)


def geo_code(address, locality):
    try:
        return json.loads(CacheItem.objects.get(address=address, locality=locality).result)
    except CacheItem.DoesNotExist:
        payload = {"components": u"locality:{0}".format(locality), "address": address, "sensor": "false"}
        r = requests.get("http://maps.googleapis.com/maps/api/geocode/json", params=payload)
        print "geocoding"
        if r.status_code != 200:
            raise Exception("Http error #%d : %s" % (r.status_code, r.url))
        CacheItem.objects.create(address=address, locality=locality, result=r.text)
        return r.json()
