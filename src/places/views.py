from django.db.models.aggregates import Count
from django.http.response import HttpResponse
from django.shortcuts import render
from places.models import Place, Placemark


def home(request):
    places = Place.objects.all()
    context = {'places' : places}
    return render(request, 'home.html', context)

def place(request, id):
    place = Place.objects.get(pk=id)
    context = {'place' : place}
    return render(request, 'place.html', context)