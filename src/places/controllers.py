# coding: utf-8

from places.models import Place, Dataset, Placemark
from django.contrib.auth.models import User
from collections import Counter
from geocoding.models import geo_code
from django.db.utils import IntegrityError
import json, csv, codecs, cStringIO
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

        try:
            place.vendor_id = p["id"]
            place.address = p["address"]
            place.city = p["city"]
            #place.title = p["title"]
        except KeyError:
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
    