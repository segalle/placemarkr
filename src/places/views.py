from django.http import *
from django.shortcuts import render, get_object_or_404
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
    
    place = get_object_or_404(Place, id=int(id))
    #place = Place.objects.get(id=int(id))
    
    l = []
    for pm in place.placemarks.all():
        try:
            vote = Vote.objects.get(placemark=pm, user=request.user)
        except Vote.DoesNotExist:
            vote = None
        l.append(
             {
              'id': pm.id,
              'city': pm.city,
              'address': pm.address,
              'lat': pm.lat,
              'lng': pm.lng,
              'vote': vote.positive if vote else None
             }
        )
    context = {
               'place': place,
               'placemarks': json.dumps(l),
               'id': id,
               }
    return render(request, 'place.html', context)


@login_required(login_url='/login/')
def vote(request):
    if not request.method == 'POST':
        return HttpResponse("Wrong request method")
    placemark = Placemark.objects.get(id=int(request.POST['id']))
    if Vote.objects.filter(user=request.user, placemark=placemark).exists():
        currentvote = Vote.objects.get(user=request.user, placemark=placemark)
        currentvote.positive = request.POST['positive'] == 'True'
        currentvote.save()
        return HttpResponse("Updated")
    newvote = Vote()
    newvote.placemark = placemark
    newvote.user = request.user
    newvote.positive = request.POST['positive'] == 'True'
    newvote.save()
    return HttpResponse("OK")


@login_required(login_url='/login/')
def addplacemark(request):
    if not request.method == 'POST':
        return HttpResponse("Wrong request method")
    if Placemark.objects.filter(place__id=request.POST['place'], address=request.POST['address'], city=request.POST['city'], lat=request.POST['lat'], lng=request.POST['lng']).exists():
        return HttpResponse("exists")
    newplacemark = Placemark();
    newplacemark.place_id = int(request.POST['place'])
    newplacemark.city = request.POST['city']
    newplacemark.address = request.POST['address']
    newplacemark.lat = float(request.POST['lat'])
    newplacemark.lng = float(request.POST['lng'])
    newplacemark.save()
    return HttpResponse("OK")
