from django.contrib import admin
from .models import City, LocalArea, Route, SightseeingSpot, TourPackage, Tariff


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_attractions_count', 'get_local_areas_count', 'sightseeing_kilometers', 'is_hill_station', 'hill_station_charge', 'has_coordinates', 'is_active')
    list_filter = ('is_active', 'is_hill_station')
    search_fields = ('name', 'tourist_places')
    fields = ('name', 'description', 'image', 'latitude', 'longitude', 'tourist_places', 'sightseeing_kilometers', 'is_hill_station', 'hill_station_charge', 'is_active')
    
    def get_attractions_count(self, obj):
        if obj.tourist_places:
            return len([place.strip() for place in obj.tourist_places.split(',') if place.strip()])
        return 0
    get_attractions_count.short_description = 'Attractions'
    
    def get_local_areas_count(self, obj):
        return obj.local_areas.count()
    get_local_areas_count.short_description = 'Local Areas'
    
    def has_coordinates(self, obj):
        return bool(obj.latitude and obj.longitude)
    has_coordinates.boolean = True
    has_coordinates.short_description = 'Has Coordinates'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add help text for tourist_places field
        if 'tourist_places' in form.base_fields:
            form.base_fields['tourist_places'].widget.attrs.update({
                'rows': 4,
                'placeholder': 'Enter tourist places separated by commas, e.g.:\nAlleppey Beach, Ambalapuzha Sree Krishna Temple, Chavaran Bhawan'
            })
        return form


@admin.register(LocalArea)
class LocalAreaAdmin(admin.ModelAdmin):
    list_display = ('city', 'name', 'has_coordinates')
    list_filter = ('city',)
    search_fields = ('name', 'city__name')
    
    def has_coordinates(self, obj):
        return bool(obj.latitude and obj.longitude)
    has_coordinates.boolean = True
    has_coordinates.short_description = 'Has Coordinates'


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('from_city', 'to_city', 'distance', 'one_way_fixed_rate')
    list_filter = ('from_city', 'to_city')


@admin.register(SightseeingSpot)
class SightseeingSpotAdmin(admin.ModelAdmin):
    list_display = ('city', 'name')
    list_filter = ('city',)


@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'days', 'price_per_vehicle', 'is_active')
    list_filter = ('days', 'is_active')
    filter_horizontal = ('cities',)


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('tariff_type', 'vehicle', 'base_price', 'is_active')
    list_filter = ('tariff_type', 'is_active')

