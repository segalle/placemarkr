# coding: utf-8

from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import *
from django.shortcuts import render, get_object_or_404, render_to_response, \
    redirect
from django.template import RequestContext
from places.models import Place, Placemark, Vote
import json
from fileHandler import handleUploadedFile

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

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()
    file_type = forms.ChoiceField(choices=(('csv','csv'),('json','json')), required=True, widget=forms.RadioSelect)
    
    def is_valid(self):
        # run the parent validation first
        
        valid = super(UploadFileForm, self).is_valid()
        
        if not valid:
            return valid
        if not self.cleaned_data['file'].name.endswith(self.cleaned_data['file_type']):
            self._errors['bad_file'] = "File does not match the chosen format"
            return False
        
        return True

def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Opens the file and sends it
            # TODO - handle UTF-8 BOM??
            data = handleUploadedFile(request.FILES['file'], form.cleaned_data['file_type'])
            return render(request, 'dataset.html', {'data' : data })
    else:
        form = UploadFileForm()
        
    return render(request, 'upload.html', {
        'form': form,
    })
    #return render_to_response('upload.html', {'form': form})