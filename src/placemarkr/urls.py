from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'places.views.home', name='home'),
    url(r'^place/(?P<id>\d+)/$', 'places.views.place', name='place'),
    url(r'^login/$', 'places.views.login_user', name='login_user'),
    url(r'^logout/$', 'places.views.logout_user', name='logout_user'),
    # url(r'^placemarkr/', include('placemarkr.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'', include(places.urls , namespace='places'))
)
