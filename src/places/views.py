from django.db.models.aggregates import Count
from django.http import *
from django.shortcuts import render
from places.models import Place, Placemark, Vote
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext


def login_user(request):
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
    return render_to_response('login.html', context_instance=RequestContext(request))


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required(login_url='/login/')
def home(request):
    places = Place.objects.all()
    context = {'places': places}
    return render(request, 'home.html', context)


@login_required(login_url='/login/')
def place(request, id):
    l = []
    for p in Placemark.objects.all():
        l.append(
             {
              'id': p.place.id,
              'city': p.city,
              'address': p.address,
              'lat': p.lat,
              'lng': p.lng
             }
        )
    context = {
               'placemarks': json.dumps(l),
               'id': id,
               }
    return render(request, 'place.html', context)

@login_required(login_url='/login/')
def savevote(request, id):
    if request.user.is_authenticated():
        newvote = Vote()
        newvote.placemark = Vote.placemark
        newvote.user = request.user.username
        newvote.possitive = request.possitive
        return "ok"
    return "error"