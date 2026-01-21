from django.core.management.base import BaseCommand
from tours.models import City


class Command(BaseCommand):
    help = 'Mark cities as hill stations and set their charges'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Marking hill stations...'))
        
        # Define hill stations with their charges
        hill_stations = {
            'Ooty': 750.0,
            'Kodaikanal': 750.0,
            'Munnar': 750.0,
            'Yercaud': 750.0,
            'Coorg': 750.0,
            'Wayanad': 750.0,
        }
        
        updated_count = 0
        
        for city_name, charge in hill_stations.items():
            try:
                city = City.objects.get(name=city_name)
                city.is_hill_station = True
                city.hill_station_charge = charge
                city.save()
                
                self.stdout.write(f'✓ Marked {city_name} as hill station (Rs. {charge})')
                updated_count += 1
                
            except City.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠ City "{city_name}" not found'))
        
        self.stdout.write(self.style.SUCCESS(f'\nUpdated {updated_count} hill stations'))
        
        # Show all hill stations
        hill_stations_in_db = City.objects.filter(is_hill_station=True)
        self.stdout.write(f'\nCurrent hill stations in database:')
        for city in hill_stations_in_db:
            self.stdout.write(f'  - {city.name}: Rs. {city.hill_station_charge}')