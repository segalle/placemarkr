from django.shortcuts import render
from places.models import Place


def home(request):
    places = Place.objects.all()
    context ={'places' : places}
    return render(request, 'home.html', context )