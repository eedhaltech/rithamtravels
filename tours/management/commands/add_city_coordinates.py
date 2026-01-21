from django.core.management.base import BaseCommand
from tours.models import City


class Command(BaseCommand):
    help = 'Add latitude and longitude coordinates to cities for better mapping and distance calculations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding coordinates to cities...'))
        
        # City coordinates (latitude, longitude)
        city_coordinates = {
            'Coimbatore': (11.0168, 76.9558),
            'Ooty': (11.4064, 76.6932),
            'Kodaikanal': (10.2381, 77.4892),
            'Munnar': (10.0889, 77.0595),
            'Yercaud': (11.7753, 78.2186),
            'Chennai': (13.0827, 80.2707),
            'Madurai': (9.9252, 78.1198),
            'Mysore': (12.2958, 76.6394),
            'Kanyakumari': (8.0883, 77.5385),
            'Rameshwaram': (9.2876, 79.3129),
            'Tanjore': (10.7870, 79.1378),
            'Thanjavur': (10.7870, 79.1378),  # Same as Tanjore
            'Ariyalur': (11.1401, 79.0747),
            'Salem': (11.6643, 78.1460),
            'Trichy': (10.7905, 78.7047),
            'Tirunelveli': (8.7139, 77.7567),
            'Coorg': (12.3375, 75.8069),  # Madikeri
            'Wayanad': (11.6854, 76.1320),  # Kalpetta
            'Pondicherry': (11.9416, 79.8083),
            'Vellore': (12.9165, 79.1325),
            'Kumbakonam': (10.9601, 79.3788),
            'Tirupur': (11.1085, 77.3411)
        }
        
        updated_count = 0
        
        for city_name, (lat, lng) in city_coordinates.items():
            try:
                city = City.objects.get(name=city_name)
                
                # Only update if coordinates are missing or zero
                if not city.latitude or not city.longitude or city.latitude == 0 or city.longitude == 0:
                    city.latitude = lat
                    city.longitude = lng
                    city.save()
                    updated_count += 1
                    self.stdout.write(f'✓ Updated coordinates for {city_name}: ({lat}, {lng})')
                else:
                    self.stdout.write(f'  {city_name} already has coordinates')
                    
            except City.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠ City not found: {city_name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nUpdated coordinates for {updated_count} cities'))