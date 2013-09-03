from django.db.models.aggregates import Count
from django.http import *
from django.shortcuts import render
from places.models import Place, Placemark
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response,redirect
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
    context = {'places' : places}
    return render(request, 'home.html', context)

@login_required(login_url='/login/')
def place(request, id):
    place = Place.objects.get(pk=id)
    placemarks = place.placemarks.iterator()
    context = {
               'place' : place,
               }
    return render(request, 'place.html', context)

