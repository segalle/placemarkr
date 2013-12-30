# coding: utf-8

from places.models import Place, Dataset
from django.contrib.auth.models import User
from collections import Counter
from geocoding.models import geo_code
from django.db.utils import IntegrityError
import json


def create_dataset(name, in_places, user_id):
    messages = []
    try:
        # if the dataset already exists
        ds = Dataset.objects.get(name=name)
        return messages
    except Dataset.DoesNotExist:
        pass
    ds = Dataset()
    ds.owner = User.objects.get(id=user_id)
    ds.name = name
    ds.save()
    for i in in_places:
        try:
            place = Place.objects.get(vendor_id=i['id'])
            if place.data == json.dumps(i):
                messages.append("place id #%s already exist... skipping" % i["id"])
            else:
                place.data = json.dumps(i)
                place.save()
        except Place.DoesNotExist:
            place = Place()
            place.vendor_id = i["id"]
            place.data = json.dumps(i)
            place.dataset = ds
            place.save()
            messages.append("place id #%s added" % i["id"])
    return messages

def create_markers(places):
    counter = Counter()
    #places = dataset.places.objects.all()
   
    for place in places:

        data = json.loads(place.data)
        geo_result = geo_code(data['address'], data['city'])

        if geo_result["status"] != "OK":
            counter[geo_result["status"]] +=1
            continue

        for l in geo_result["results"]:
            marker = Placemark()
            marker.place = place
            marker.city = data['city']
            marker.address = data['address']
            location = l["geometry"]["location"]
            marker.lat = location["lat"]
            marker.lng = location["lng"]
            try:
                marker.save()
                counter["Newly added"] += 1
            except IntegrityError:
                counter["Already exist"] += 1
    return counter
        
        
    