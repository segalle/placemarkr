from django.core.management.base import BaseCommand, CommandError
from places.models import Place
import os
import json

class Command(BaseCommand):
    args = '<filename>'
    help = 'Imports places from json file to "place" table'

    def handle(self, *args, **options):
        if len(args) > 0:
            if os.path.exists(args[0]):
                with open(args[0], 'r') as f:
                    result = json.load(f)
                for i in result:
                    place = Place()
                    place.vendor_id = i["id"]
                    place.data = i
                    place.save()
            else:
                print "file %s doesn't exist" % args[0]
        else:
            print "please specify file name"