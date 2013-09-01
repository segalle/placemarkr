from django.core.management.base import BaseCommand, CommandError
from places.models import Place , PlaceMarker
import json
import os

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
        for i in result:
            try:
                marker = PlaceMarker()
                marker.city = i['city']
                marker.address = i['address']
                marker.place = Place.objects.get(vendor_id=i['id'])
                marker.lat = i['lat']
                marker.lng = i['lng']
                marker.save()
                print "%s ,%s saved successfully" %(marker.address ,marker.city ) 
            except Place.DoesNotExist:
                print "%s place id doesn't exist" % i['id']