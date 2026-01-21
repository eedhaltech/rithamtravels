from django.db import models


class Vehicle(models.Model):
    FUEL_TYPE_CHOICES = (
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('cng', 'CNG'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    )
    
    AC_CHOICES = (
        ('ac', 'AC'),
        ('non_ac', 'Non-AC'),
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    
    # Seating and capacity
    max_seats = models.IntegerField(default=4, help_text="Maximum passenger seats (excluding driver)")
    luggage_capacity = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., 2 Large + 2 Small")
    
    # Vehicle specifications
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default='petrol')
    ac_type = models.CharField(max_length=10, choices=AC_CHOICES, default='ac')
    
    # Pricing (base rates)
    fare_per_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    driver_charge_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    per_day_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Vehicle per day fee")
    min_km_per_day = models.IntegerField(default=250)
    
    # Local trip pricing
    fare_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Hourly rate for local trips")
    min_hours_local = models.IntegerField(default=3, help_text="Minimum hours for local trips")
    min_hours_fee_local = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Minimum hours fee for local trips")
    max_distance_min_hours = models.IntegerField(default=30, help_text="Maximum distance covered in minimum hours")
    fare_per_km_local = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Extra KM rate for local trips when distance exceeds included KM")
    
    # Availability
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, help_text="Show in listings")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicles'
        ordering = ['fare_per_km']
    
    def __str__(self):
        return self.name
    
    @property
    def seating_info(self):
        """Returns formatted seating information"""
        return f"{self.max_seats} + 1 Driver"
    
    @property
    def display_name(self):
        """Returns vehicle name with AC/Non-AC info"""
        ac_label = "AC" if self.ac_type == 'ac' else "Non-AC"
        return f"{self.name} ({ac_label})"


class VehicleTariff(models.Model):
    TRIP_TYPE_CHOICES = (
        ('oneway', 'One Way Drop'),
        ('round_trip', 'Round Trip'),
        ('outstation', 'Out Station'),
        ('local', 'Local Trip'),
    )
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='vehicle_tariffs')
    trip_type = models.CharField(max_length=20, choices=TRIP_TYPE_CHOICES)
    
    # Pricing options
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Additional charges
    driver_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    night_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Additional charge for night trips")
    toll_charges = models.BooleanField(default=True, help_text="Toll charges applicable")
    
    # Conditions
    min_km = models.IntegerField(default=0, help_text="Minimum kilometers")
    min_hours = models.IntegerField(default=0, help_text="Minimum hours")
    min_days = models.IntegerField(default=1, help_text="Minimum days")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicle_tariffs'
        unique_together = ['vehicle', 'trip_type']
        ordering = ['vehicle', 'trip_type']
    
    def __str__(self):
        return f"{self.vehicle.name} - {self.get_trip_type_display()}"

