# coding: utf-8

from places.models import Place, Dataset, Placemark
from django.contrib.auth.models import User
from collections import Counter
from geocoding.models import geo_code
from django.db.utils import IntegrityError
import json
from django.contrib import messages

def delete_dataset(ds):
    for place in ds.places.all():
        Place.delete(place)
    Dataset.delete(ds)

def create_dataset(request,name, in_places, user_id):
    try:
        # if the dataset already exists
        ds = Dataset.objects.get(name=name)
        messages.error(request, "שם המאגר קיים במערכת")
        return False
    except Dataset.DoesNotExist:
        pass
    ds = Dataset()
    ds.owner = User.objects.get(id=user_id)
    ds.name = name
    ds.save()
    
    for p in in_places:
        place = Place()
        place.vendor_id = p["id"]
        place.address = p["address"]
        place.city = p["city"]
        try:
            place.title = p["title"]
        except KeyError:
            delete_dataset(ds)
            messages.error(request, "שדה ה-title חסר עבור id=" + str(place.vendor_id))
            return False
        place.data = json.dumps(p)
        place.dataset = ds
        place.save()

    messages.success(request, "המאגר נוסף בהצלחה")
    return True

def create_markers(places):
    counter = Counter()
   
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
        
        
    