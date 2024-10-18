from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from fuel_route.data.models import FuelStationModel

@admin.register(FuelStationModel)
class FuelStationAdmin(OSMGeoAdmin):
    list_display = ('truckstop_name', 'city', 'state', 'retail_price')
    list_filter = ('state',)
    search_fields = ('truckstop_name', 'city', 'state')