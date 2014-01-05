# coding: utf-8

from controllers import create_dataset, create_markers
from places.forms import UploadFileForm, UserCreateForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import *
from django.shortcuts import render, get_object_or_404, render_to_response, \
    redirect
from django.template import RequestContext
from fileHandler import handleUploadedFile
from places.models import Place, Placemark, Vote, Dataset
import json
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import get_messages


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
                return HttpResponseRedirect('/user/' + user.username)
    context = {'registration_form' : UserCreateForm() }
    return render(request, 'login.html', context)


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required(login_url='/login/')
def home(request):
    username = request.user.username
    return userHomepage(request, username)

@login_required(login_url='/login/')
def place(request, id):
    
    place = get_object_or_404(Place, id=int(id))
    # place = Place.objects.get(id=int(id))
    
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
def userHomepage(request, username):
    urlUser = get_object_or_404(User, username=username)
    places = Place.objects.all()
    userDatasets = Dataset.objects.filter(owner=urlUser)
    context = {'urlUser': urlUser,
               'places': places,
               'userDatasets' : userDatasets}
    return render(request, 'home.html', context)

@login_required(login_url='/login/')
def datasetDetails(request, username, datasetSlug):
    urlUser = get_object_or_404(User, username=username)
    dataset = get_object_or_404(Dataset, slug=datasetSlug)
    context = {'urlUser': urlUser,
               'places': dataset.places.all(),
               'dataset' : dataset}
    return render(request, 'userDataset.html', context)

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
        return HttpResponseNotAllowed("Wrong request method")
    
    if Placemark.objects.filter(place__id=request.POST['place'], address=request.POST['address'], city=request.POST['city'], lat=request.POST['lat'], lng=request.POST['lng']).exists():
        return HttpResponse("exists")
    
    newplacemark = Placemark();
    newplacemark.place_id = int(request.POST['place'])
    newplacemark.city = request.POST['city']
    newplacemark.address = request.POST['address']
    newplacemark.lat = float(request.POST['lat'])
    newplacemark.lng = float(request.POST['lng'])
    newplacemark.save()

    newvote = Vote()
    newvote.placemark = newplacemark
    newvote.user = request.user
    newvote.positive = 'True'
    newvote.save()
    
    return HttpResponse(newplacemark.id)

@login_required(login_url='/login/')
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Opens the file and sends it
            # TODO - handle UTF-8 BOM??
            data = handleUploadedFile(request.FILES['file'], form.cleaned_data['file_type'])
            title = form.cleaned_data['title']
            if create_dataset(request, title, data, request.user.id):
                ds = Dataset.objects.get(name=title)
                places = ds.places.all()
                counter = create_markers(places)
            
    else:
        form = UploadFileForm()
    
    messages = get_messages(request)
    response_data = {}
    for message in messages:
        response_data['tags'] = message.tags
        response_data['message'] = message.message
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def register(request):
    if request.method == 'POST':
        registration_form = UserCreateForm(request.POST)
        if registration_form.is_valid():
            new_user = registration_form.save()
            new_user = authenticate(username=request.POST['username'],
                                    password=request.POST['password1'])
            login(request, new_user)
            return HttpResponseRedirect('/user/' + new_user.username)
    context = {'registration_form' : UserCreateForm() }
    return render(request, 'login.html', context)
     
