from django.core.management.base import BaseCommand, CommandError
from places.models import Place
import json
import os


class Command(BaseCommand):
    args = '<filename>'
    help = 'Exports Places and Markers to one full json file'

    def handle(self, *args, **options):

        if len(args) <= 0:
            raise CommandError('please specify file name')

        if not os.path.exists(args[0]):
            raise CommandError("file %s doesn't exist" % args[0])

        fullgeojson = {"type": "FeatureCollection", "features": []}
        fullgeojson["features"] = [Place.export_feature(p) for p in Place.objects.all() if Place.export_feature(p) != None]

        fullpath = os.path.join(args[0], 'full.geojson')
 
        with open(fullpath, 'w') as f:
            json.dump(fullgeojson, f, indent=4)

        print "Geojson was created successfuly"
