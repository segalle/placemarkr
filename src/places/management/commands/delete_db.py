from django.core.management.base import BaseCommand, CommandError
from places.models import Place, Dataset

class Command(BaseCommand):
    args = ''
    help = 'Imports places from json file to "place" table'
    
    def handle(self, *args, **options):
        Place.objects.all().delete()
        Dataset.objects.all().delete()
        