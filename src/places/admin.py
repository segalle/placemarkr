from django.contrib import admin
from places.models import Dataset,Place,Placemark,Vote
from geocoding.models import CacheItem


class PlaceInline(admin.TabularInline):
    model = Place
    extra = 3
    
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")
   
    inlines = [PlaceInline]
   
class PlacemarkInline(admin.TabularInline):
    model = Placemark
    extra = 3
   
class PlaceAdmin(admin.ModelAdmin):
	list_display = ("vendor_id","title")
	
	inlines = [PlacemarkInline]
	
class VoteInline(admin.TabularInline):
    model = Vote
    extra = 3

class PlacemarkAdmin(admin.ModelAdmin):
    list_display = ("place","city","address","lat","lng")

    inlines = [VoteInline]

class CacheAdmin(admin.ModelAdmin):
    list_display = ("locality","address","result")
	
admin.site.register(Dataset,DatasetAdmin)	
admin.site.register(Place,PlaceAdmin)
admin.site.register(Placemark,PlacemarkAdmin)
admin.site.register(CacheItem,CacheAdmin)