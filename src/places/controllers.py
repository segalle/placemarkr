# coding: utf-8

from places.models import Place, Dataset, Placemark
from django.contrib.auth.models import User
from collections import Counter
from geocoding.models import geo_code
from django.db.utils import IntegrityError
import json, csv, codecs, cStringIO
from django.contrib import messages
import requests
from StringIO import StringIO
from PIL import Image
from django.core.files.base import ContentFile
import re

def delete_dataset(ds):
    for place in ds.places.all():
        Place.delete(place)
    Dataset.delete(ds)

def create_dataset(request, name, description, in_places, user_id):
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
    ds.description = description
    ds.save()

    for p in in_places:
        place = Place()

        try:
            place.vendor_id = p["id"]
        
            place.address = p["address"].strip()
            place.city = p["city"].strip()
            place.title = p["title"].strip()
        except KeyError, ex:
            print ex
            delete_dataset(ds)
            messages.error(request, "אחד השדות הדרושים חסר. וודא כי כל הרשומות מכילות את השדות: id, address, city, title")
            return False
        place.data = json.dumps(p)
        place.dataset = ds
        place.save()

    messages.success(request, "המאגר נוסף בהצלחה")
    return True

def create_markers(places):
    counter = Counter()
    # TODO - change to regex

    blacklist = [u'מס.',u"מס'",u'א' ,u'ב' ,u'ג' ,u'ד',u"א'",u"ב'",u"ג'",u"ד'",u"ה'",u"רח'",u"רח"]

    for place in places:

        data = json.loads(place.data)

        address = re.sub('([\d]+)([\S]*)','\g<1>',data['address'])

        clean_address = ' '.join([x for x in address.split() if x not in blacklist])
        geo_result = geo_code(clean_address, data['city'])
        city_result = geo_code(data['city'], data['city'])

        if city_result["status"] == "OK":
            city_location = city_result["results"][0]["geometry"]["location"]

        if geo_result["status"] != "OK":
            counter[geo_result["status"]] +=1
            print "geo_result status of place id " + str(place.id) + "was " + geo_result["status"]
            continue

        for l in geo_result["results"]:
            location = l["geometry"]["location"]
            if location == city_location:
                counter["Failed"] += 1
                continue
            marker = Placemark()
            marker.place = place
            marker.city = data['city']
            marker.address = clean_address

            marker.lat = location["lat"]
            marker.lng = location["lng"]
            
            payload = {"size": "240x240", "location": clean_address + " " + data['city'], "sensor": "false"}
            print payload
            r = requests.get("http://maps.googleapis.com/maps/api/streetview", params=payload)
            print r.url
            input_file = StringIO(r.content)
            output_file = StringIO()
            img = Image.open(input_file)
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(output_file, "JPEG")
            try:
                marker.save()
                counter["Newly added"] += 1
                marker.image.save(str(marker.id) + ".jpg", ContentFile(output_file.getvalue()), save=True)
            except IntegrityError:
                counter["Already exist"] += 1

    return counter
        

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") if isinstance(s, unicode) else s for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
    