from django.db import models


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='cities/', blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    tourist_places = models.TextField(blank=True, null=True, help_text="Enter tourist places separated by commas")
    sightseeing_kilometers = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total sightseeing distance in kilometers")
    is_hill_station = models.BooleanField(default=False, help_text="Mark as true if this is a hill station (charges Rs. 750 per visit)")
    hill_station_charge = models.DecimalField(max_digits=10, decimal_places=2, default=750.0, help_text="Hill station charge per visit")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'cities'
        verbose_name_plural = 'Cities'
    
    def __str__(self):
        return self.name
    
    def get_tourist_places_list(self):
        """Return tourist places as a list"""
        if self.tourist_places:
            return [place.strip() for place in self.tourist_places.split(',') if place.strip()]
        return []


class LocalArea(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='local_areas')
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    
    class Meta:
        db_table = 'local_areas'
        unique_together = ['city', 'name']
    
    def __str__(self):
        return f"{self.city.name} - {self.name}"


class Route(models.Model):
    from_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='routes_from')
    to_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='routes_to')
    distance = models.DecimalField(max_digits=10, decimal_places=2)  # in km
    one_way_fixed_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    class Meta:
        db_table = 'routes'
        unique_together = ['from_city', 'to_city']
    
    def __str__(self):
        return f"{self.from_city.name} to {self.to_city.name} - {self.distance} km"


class SightseeingSpot(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='sightseeing_spots')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='sightseeing/', blank=True, null=True)
    
    class Meta:
        db_table = 'sightseeing_spots'
    
    def __str__(self):
        return f"{self.city.name} - {self.name}"


class TourPackage(models.Model):
    PACKAGE_TYPE_CHOICES = (
        (1, '1 Day'),
        (2, '2 Days'),
        (3, '3 Days'),
        (4, '4 Days'),
        (5, '5 Days'),
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='tour_packages/', blank=True, null=True)
    days = models.IntegerField(choices=PACKAGE_TYPE_CHOICES)
    pickup_city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='pickup_packages')
    cities = models.ManyToManyField(City, related_name='tour_packages')
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_per_vehicle = models.DecimalField(max_digits=10, decimal_places=2)
    vehicle_type = models.CharField(max_length=255, blank=True, null=True, help_text="Recommended vehicle type")
    
    # Hotel booking options
    include_hotel = models.BooleanField(default=False, help_text="Include hotel booking in package")
    hotel_details = models.JSONField(blank=True, null=True, help_text="Hotel booking details - {name, city, checkin, checkout, room_type}")
    
    # Day-wise itinerary
    day_wise_itinerary = models.JSONField(blank=True, null=True, help_text="Day-wise tour plan - [{day, pickup_time, pickup_location, places_to_visit, route_description, notes}]")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Legacy fields for backward compatibility
    itinerary = models.JSONField(blank=True, null=True)
    hotel_info = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'tour_packages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_days_display()}"
    
    @property
    def nights(self):
        """Calculate nights from days"""
        return max(0, self.days - 1)
    
    @property
    def duration_display(self):
        """Display duration as 'X Days Y Nights'"""
        if self.days == 1:
            return "1 Day"
        return f"{self.days} Days {self.nights} Nights"
    
    def get_cities_list(self):
        """Get list of cities covered in the package"""
        return list(self.cities.values_list('name', flat=True))
    
    def get_day_wise_plan(self):
        """Get structured day-wise itinerary"""
        if self.day_wise_itinerary:
            return self.day_wise_itinerary
        return []
    
    def get_hotel_info(self):
        """Get hotel booking information"""
        if self.include_hotel and self.hotel_details:
            return self.hotel_details
        return None


class Tariff(models.Model):
    TARIFF_TYPE_CHOICES = (
        ('local_hour', 'Local Tariff - Hour Basis'),
        ('outstation_day', 'Out Station - Day Basis'),
        ('outstation_km', 'Out Station - Km Basis'),
        ('oneway_fixed', 'One Way Dropping (Fixed)'),
        ('oneway_km', 'One Way Dropping (Km Basis)'),
    )
    
    tariff_type = models.CharField(max_length=50, choices=TARIFF_TYPE_CHOICES)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='tariffs', blank=True, null=True)
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, related_name='tariffs')
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    min_hours = models.IntegerField(default=4, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tariffs'
    
    def __str__(self):
        return f"{self.get_tariff_type_display()} - {self.vehicle.name}"

