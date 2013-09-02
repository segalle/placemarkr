from django.http.response import HttpResponse
from django.shortcuts import render
from places.models import Place, Placemark


def home(request):
    places = Place.objects.all()
    all = []
    for place in places:
        sum = {}
        sum['id'] = place.vendor_id
        sum['num_marker'] = Placemark.objects.filter(place= place).count()
        all.append(sum)
    context ={'all' : all}
    return render(request, 'home.html', context )