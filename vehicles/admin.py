from django.contrib import admin
from .models import Vehicle, VehicleTariff


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_seats', 'ac_type', 'fuel_type', 'fare_per_km', 'per_day_fee', 'is_available', 'is_active', 'created_at')
    list_filter = ('is_available', 'is_active', 'ac_type', 'fuel_type')
    search_fields = ('name', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'image')
        }),
        ('Seating & Capacity', {
            'fields': ('max_seats', 'luggage_capacity')
        }),
        ('Specifications', {
            'fields': ('fuel_type', 'ac_type')
        }),
        ('Pricing', {
            'fields': ('fare_per_km', 'driver_charge_per_day', 'per_day_fee', 'min_km_per_day')
        }),
        ('Availability', {
            'fields': ('is_available', 'is_active')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VehicleTariff)
class VehicleTariffAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'trip_type', 'base_price', 'price_per_km', 'price_per_day', 'is_active', 'created_at')
    list_filter = ('trip_type', 'is_active', 'vehicle')
    search_fields = ('vehicle__name',)
    fieldsets = (
        ('Vehicle & Trip Type', {
            'fields': ('vehicle', 'trip_type')
        }),
        ('Pricing', {
            'fields': ('base_price', 'price_per_km', 'price_per_day', 'price_per_hour', 'driver_charge', 'night_charge', 'toll_charges')
        }),
        ('Conditions', {
            'fields': ('min_km', 'min_hours', 'min_days')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
