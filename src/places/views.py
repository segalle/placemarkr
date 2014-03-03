# coding: utf-8

from controllers import create_dataset, create_markers, UnicodeWriter
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.http import *
from django.shortcuts import render, get_object_or_404
from fileHandler import handleUploadedFile
from places.forms import UploadFileForm, UserCreateForm
from places.models import Place, Placemark, Vote, Dataset
import hashlib
import json
import urllib
from django.utils.timesince import timesince
# import code for encoding urls and generating md5 hashes

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
    return render(request, 'account\signup.html', context)


@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def place(request, id):
    
    place = get_object_or_404(Place, id=int(id))
    dataset = get_object_or_404(Dataset, id=place.dataset.id)

    ids = [k['id'] for k in dataset.places.values('id')]

    currIndex = ids.index(place.id)
    try:
        nextPlaceId = ids[currIndex + 1]
    except IndexError:
        nextPlaceId = 0

    prevPlaceId = 0 if currIndex == 0 else ids[currIndex - 1]


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
                'next_place' : nextPlaceId,
                'prev_place' : prevPlaceId,
               'place': place,
               'placemarks': json.dumps(l),
               'id': id,
               }
    return render(request, 'place.html', context)

@login_required
def placeVotingTable(request, id):
    place = get_object_or_404(Place, id=int(id))
    datasetsSearch = [dict([("username", vote.user.username),
                            ("first_name", vote.user.first_name),
                            ("last_name", vote.user.last_name),
                            ("date", timesince(vote.created_on))]) for pm in place.placemarks.all() for vote in pm.votes.all()]
    return HttpResponse(json.dumps(datasetsSearch), content_type="application/json")

@login_required
def userHomepage(request, username):
    urlUser = get_object_or_404(User, username=username)
    places = Place.objects.all()
    userDatasets = Dataset.objects.filter(owner=urlUser)
    
    # Set your variables here
    default = "http://www.example.com/default.jpg"
    size = 100
     
    # construct the url
    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(urlUser.email.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode({'d':default, 's':str(size)})
    
    context = {'urlUser': urlUser,
               'places': places,
               'userDatasets' : userDatasets,
                'gravatar_url' : gravatar_url,
                }
    return render(request, 'userHomepage.html', context)

@login_required
def datasetsList(request, username):
    urlUser = get_object_or_404(User, username=username)
    userDatasets = Dataset.objects.filter(owner=urlUser)
    response_data = [dict([("name", dataset.name), ("description", dataset.description), ("id", dataset.id), ("numOfPlaces", dataset.places.count())]) for dataset in userDatasets]
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@login_required # maybe not?
def getDatasets(request):
    allDatasets = Dataset.objects.all()
    response_data = [dict([("name", dataset.name), 
                           ("id", dataset.id), 
                           ("username",dataset.owner.username),
                           ("first_name",dataset.owner.first_name),
                           ("last_name",dataset.owner.last_name),
                           ("user_url",reverse('userHomepage', args=(dataset.owner.username,))),
                           ("numOfPlaces", dataset.places.count())]) for dataset in allDatasets]
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
def search(request):
    datasetsSearch = [dict([("url", reverse('datasetDetails', args=(dataset.id,))),
                            ("name", dataset.name),
                            ("value", dataset.name),
                            ("type", "מאגר"),
                            ("description","מכיל " + str(dataset.places.count()) + " רשומות"),
                            ("tokens",[dataset.name])]) for dataset in Dataset.objects.all()]
    usersSearch = [dict([("url", reverse('userHomepage', args=(user.username,))),
                         ("name", user.first_name + " " + user.last_name),
                         ("value", user.first_name + " " + user.last_name),
                         ("type", "משתמש"), 
                         ("description",user.username),
                         ("tokens",[user.first_name,user.last_name, user.username])]) for user in User.objects.all()]
    searchResults = datasetsSearch + usersSearch
    return HttpResponse(json.dumps(searchResults), content_type="application/json")

@login_required
def datasetDetails(request, id):
    dataset = get_object_or_404(Dataset, id=id)
    context = {'urlUser': request.user,
               'places': dataset.places.all(),
               'dataset' : dataset}
    return render(request, 'userDataset.html', context)

@login_required
def datasetList(request, id):
    dataset = get_object_or_404(Dataset, id=id)
    context = {'urlUser': request.user,
               'places': dataset.places.extra(select={'int_vendor_id': 'CAST(vendor_id AS INTEGER)'},order_by=['int_vendor_id']),
               'dataset' : dataset}
    return render(request, 'datasetList.html', context)

@login_required
def datasetAlbum(request, id):
    dataset = get_object_or_404(Dataset, id=id)
    context = {'urlUser': request.user,
               'places': dataset.places.extra(select={'int_vendor_id': 'CAST(vendor_id AS INTEGER)'},order_by=['int_vendor_id']),
               'dataset' : dataset}
    return render(request, 'datasetAlbum.html', context)

@login_required
def datasetMap(request, id):
    dataset = get_object_or_404(Dataset, id=id)
    context = {'urlUser': request.user,
               'places': dataset.places.all(),
               'dataset' : dataset}
    return render(request, 'datasetMap.html', context)

@login_required
def datasetJson(request, id):
    dataset = get_object_or_404(Dataset, id=id)
#     places = [dict([("vendor_id", place.vendor_id),
#                             ("title", place.title),
#                             ("address", place.address),
#                             ("city", place.city),
#                             ("lat",place.lat()),
#                             ("lng",place.lng()),
#                             ("numberOfPlacemarks",place.placemarks.count()),
#                             ("numberOfVotes",sum([pm.votes.count() for pm in place.placemarks.all()]))]) for place in dataset.places.all()]
    places = [place.serialize_place() for place in dataset.places.all()]
    
    return HttpResponse(json.dumps(places), content_type="application/json")

@login_required
def exportDataset(request, id, type):
    dataset = get_object_or_404(Dataset, id=id)
    places = dataset.places.all()
    if type == "csv":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(dataset.name.encode('utf-8'))

        writer = UnicodeWriter(response)
        writer.writerow(['id','title','address','city','lat','lng'])
        for place in places:
            ps = place.get_leading_placemark()
            if ps:
                writer.writerow([place.vendor_id, place.title, place.address, place.city, ps.lat, ps.lng])
    elif type == "geojson":
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="{0}.json"'.format(dataset.name.encode('utf-8'))

        geo_json = { "type": "FeatureCollection",
                     "features": []}

        for place in places:
            ps = place.get_leading_placemark()
            if ps:
                geo_json["features"].append(
                    {"type": "Feature",
                    "properties": {
                        "id":  place.vendor_id,
                        "title" : place.title,
                        "address" : place.address,
                        "city" : place.city,
                        },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [ps.lng,ps.lat] }})
        response.write(unicode(json.dumps(geo_json, ensure_ascii=False)))
    else:
        return datasetDetails(request, id)
    return response


@login_required
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


@login_required
def addplacemark(request):
    
    if not request.method == 'POST':
        return HttpResponseNotAllowed("Wrong request method")
    
    if Placemark.objects.filter(place__id=request.POST['place'], address=request.POST['address'], city=request.POST['city'], lat=request.POST['lat'], lng=request.POST['lng']).exists():
        return HttpResponse("exists")
    
    newplacemark = Placemark()
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

@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Opens the file and sends it
            # TODO - handle UTF-8 BOM??
            data = handleUploadedFile(request.FILES['file'], form.cleaned_data['file_type'])
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            if create_dataset(request, title, description, data, request.user.id):
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


     
