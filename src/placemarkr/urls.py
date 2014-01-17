from django.conf.urls import patterns, include, url
from django.contrib import admin
from places import views

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'places.views.home', name='home'),
    url(r'^place/(?P<id>\d+)/$', 'places.views.place', name='place'),
    url(r'^login/$', 'places.views.login_user', name='login_user'),
    url(r'^logout/$', 'places.views.logout_user', name='logout_user'),
    #(r'^account/logout/$', 'django.contrib.auth.views.logout',
    # {'next_page': '/'}),
    url(r'^vote/$', 'places.views.vote', name='vote'),
    url(r'^addplacemark/$', 'places.views.addplacemark', name='addplacemark'),
    # ex: /user/itay
    url(r'^user/(?P<username>\w+)/$', 'places.views.userHomepage', name='userHomepage'),
    url(r'^user/(?P<username>\w+)/datasetsList.json/$', 'places.views.datasetsList', name='datasetsList'),
    # ex: /user/itay/my-first-dataset
    url(r'^user/(?P<username>\w+)/(?P<id>\d+)/$', 'places.views.datasetDetails', name='datasetDetails'),
    #url(r'^datasets/(?P<id>\d+)/$', 'places.views.datasetDetails', name='datasetDetails'),
    # url(r'^placemarkr/', include('placemarkr.foo.urls')),

    url(r'^dataset/export/(?P<id>\d+)/$', 'places.views.exportDataset', name='exportDataset'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'', include(places.urls , namespace='places'))
    url(r'^upload/', views.upload, name='upload'),
    url(r'^register/', views.register, name='register'),
    url(r'^account/', include('allauth.urls')),
)
