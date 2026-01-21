from django.core.management.base import BaseCommand
from tours.models import City, Route
import math

class Command(BaseCommand):
    help = 'Populate basic route distances between cities'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--sample-coordinates',
            action='store_true',
            help='Add sample coordinates to cities',
        )
    
    def handle(self, *args, **options):
        if options['sample_coordinates']:
            self.add_sample_coordinates()
        
        self.populate_routes()
        
    def add_sample_coordinates(self):
        """Add sample coordinates for major Indian cities"""
        city_coordinates = {
            'Coimbatore': (11.0168, 76.9558),
            'Chennai': (13.0827, 80.2707),
            'Bangalore': (12.9716, 77.5946),
            'Mysore': (12.2958, 76.6394),
            'Ooty': (11.4064, 76.6932),
            'Kodaikanal': (10.2381, 77.4892),
            'Madurai': (9.9252, 78.1198),
            'Trichy': (10.7905, 78.7047),
            'Salem': (11.6643, 78.1460),
            'Erode': (11.3410, 77.7172),
            'Tirupur': (11.1085, 77.3411),
            'Kochi': (9.9312, 76.2673),
            'Munnar': (10.0889, 77.0595),
            'Thekkady': (9.5916, 77.1700),
            'Alleppey': (9.4981, 76.3388),
            'Trivandrum': (8.5241, 76.9366),
        }
        
        updated_count = 0
        for city_name, (lat, lon) in city_coordinates.items():
            try:
                city = City.objects.get(name__icontains=city_name)
                city.latitude = lat
                city.longitude = lon
                city.save()
                updated_count += 1
                self.stdout.write(f"Updated coordinates for {city.name}: {lat}, {lon}")
            except City.DoesNotExist:
                self.stdout.write(f"City '{city_name}' not found in database")
            except City.MultipleObjectsReturned:
                self.stdout.write(f"Multiple cities found for '{city_name}'")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated coordinates for {updated_count} cities')
        )
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance using Haversine formula"""
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in kilometers
        r = 6371
        return c * r
    
    def populate_routes(self):
        """Create routes between cities with coordinates"""
        cities_with_coords = City.objects.filter(
            latitude__isnull=False, 
            longitude__isnull=False
        )
        
        created_count = 0
        
        for from_city in cities_with_coords:
            for to_city in cities_with_coords:
                if from_city != to_city:
                    # Check if route already exists
                    if not Route.objects.filter(
                        from_city=from_city, 
                        to_city=to_city
                    ).exists():
                        
                        # Calculate distance
                        distance = self.haversine_distance(
                            float(from_city.latitude), float(from_city.longitude),
                            float(to_city.latitude), float(to_city.longitude)
                        )
                        
                        # Create route
                        Route.objects.create(
                            from_city=from_city,
                            to_city=to_city,
                            distance=round(distance, 2)
                        )
                        
                        created_count += 1
                        self.stdout.write(
                            f"Created route: {from_city.name} -> {to_city.name} ({distance:.2f} km)"
                        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} routes')
        )