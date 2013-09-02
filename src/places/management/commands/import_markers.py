from django.core.management.base import BaseCommand, CommandError
from places.models import Place, Placemark
import json
import os
from django.db.utils import IntegrityError
from geocoding.models import geo_code
from collections import Counter


class Command(BaseCommand):
    args = '<filename>'
    help = 'Imports placemarkers from json file to "PlaceMarkers" table'

    def handle(self, *args, **options):

        if len(args) <= 0:
            raise CommandError('please specify file name')

        if not os.path.exists(args[0]):
            raise CommandError("file %s doesn't exist" % args[0])

        with open(args[0], 'r') as f:
            result = json.load(f)
        counter = Counter()
        try:
            for i in result:
    
                try:
                    place = Place.objects.get(vendor_id=i['id'])
                except Place.DoesNotExist:
                    print "%s place id doesn't exist" % i['id']
                    counter["badid"] += 1
                    continue
    
                counter["Valid locations"] += 1
                geo_result = geo_code(i['address'], i['city'])
    
                if geo_result["status"] != "OK":
                    counter[geo_result["status"]] +=1
                    continue
    
                print "results for: %s ,%s" % (i['address'], i['city'])
    
                for l in geo_result["results"]:
                    marker = Placemark()
                    marker.place = place
                    marker.city = i['city']
                    marker.address = i['address']
                    location = l["geometry"]["location"]
                    marker.lat = location["lat"]
                    marker.lng = location["lng"]
                    try:
                        marker.save()
                        counter["Newly added"] += 1
                        print "\t %f ,%f saved successfully" % (marker.lat, marker.lng)
                    except IntegrityError:
                        counter["Already exist"] += 1
                        print "\t %f ,%f record is not unique" % (marker.lat, marker.lng)
                        continue
                
            print "import markers completed"
        finally:
            for k, v in counter.items():
                print k, v