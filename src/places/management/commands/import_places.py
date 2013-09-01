from django.core.management.base import BaseCommand, CommandError
from places.models import Place
import os
import json

class Command(BaseCommand):
    args = '<filename>'
    help = 'Imports places from json file to "place" table'

    def handle(self, *args, **options):
        if len(args) <= 0:
            raise CommandError('please specify file name')
        if not os.path.exists(args[0]):
            raise CommandError("file %s doesn't exist" % args[0])
        with open(args[0], 'r') as f:
            result = json.load(f)
        for i in result:
            try:
                place = Place.objects.get(vendor_id=i['id'])
                print place
            except Place.DoesNotExist:
                place = Place()
                place.vendor_id = i["id"]
                place.data = json.dumps(i)
                place.save()
                print "place id #%s added" %i["id"]: