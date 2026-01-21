from django.core.management.base import BaseCommand
from tours.models import Tariff
from vehicles.models import Vehicle


class Command(BaseCommand):
    help = 'Create initial tariff data for all tariff types'

    def handle(self, *args, **options):
        # Local hour tariff data
        local_hour_tariffs = [
            {'vehicle_name': 'Swift Dzire', 'base_price': 600, 'price_per_hour': 150, 'min_hours': 4},
            {'vehicle_name': 'Etios', 'base_price': 640, 'price_per_hour': 160, 'min_hours': 4},
            {'vehicle_name': 'Innova', 'base_price': 1000, 'price_per_hour': 250, 'min_hours': 4},
            {'vehicle_name': 'Innova Crysta', 'base_price': 1200, 'price_per_hour': 300, 'min_hours': 4},
            {'vehicle_name': 'Innova Hycross', 'base_price': 1200, 'price_per_hour': 300, 'min_hours': 4},
            {'vehicle_name': 'Corolla Altis', 'base_price': 1200, 'price_per_hour': 300, 'min_hours': 4},
            {'vehicle_name': 'Traveller 12 Seater', 'base_price': 1600, 'price_per_hour': 400, 'min_hours': 4},
            {'vehicle_name': 'Traveller 17 Seater', 'base_price': 2000, 'price_per_hour': 500, 'min_hours': 4},
        ]

        # Outstation day basis tariff data (using price_per_hour as price_per_day and min_hours as min_days)
        outstation_day_tariffs = [
            {'vehicle_name': 'Swift Dzire', 'base_price': 2500, 'price_per_hour': 2500, 'min_hours': 1},
            {'vehicle_name': 'Etios', 'base_price': 2600, 'price_per_hour': 2600, 'min_hours': 1},
            {'vehicle_name': 'Innova', 'base_price': 4000, 'price_per_hour': 4000, 'min_hours': 1},
            {'vehicle_name': 'Innova Crysta', 'base_price': 4500, 'price_per_hour': 4500, 'min_hours': 1},
            {'vehicle_name': 'Innova Hycross', 'base_price': 4500, 'price_per_hour': 4500, 'min_hours': 1},
            {'vehicle_name': 'Corolla Altis', 'base_price': 4500, 'price_per_hour': 4500, 'min_hours': 1},
            {'vehicle_name': 'Traveller 12 Seater', 'base_price': 6000, 'price_per_hour': 6000, 'min_hours': 1},
            {'vehicle_name': 'Traveller 17 Seater', 'base_price': 7500, 'price_per_hour': 7500, 'min_hours': 1},
        ]

        # Outstation km basis tariff data (using price_per_hour as price_per_km and min_hours as min_km)
        outstation_km_tariffs = [
            {'vehicle_name': 'Swift Dzire', 'base_price': 3000, 'price_per_hour': 12, 'min_hours': 250},
            {'vehicle_name': 'Etios', 'base_price': 3250, 'price_per_hour': 13, 'min_hours': 250},
            {'vehicle_name': 'Innova', 'base_price': 4500, 'price_per_hour': 18, 'min_hours': 250},
            {'vehicle_name': 'Innova Crysta', 'base_price': 5000, 'price_per_hour': 20, 'min_hours': 250},
            {'vehicle_name': 'Innova Hycross', 'base_price': 5000, 'price_per_hour': 20, 'min_hours': 250},
            {'vehicle_name': 'Corolla Altis', 'base_price': 5000, 'price_per_hour': 20, 'min_hours': 250},
            {'vehicle_name': 'Traveller 12 Seater', 'base_price': 6250, 'price_per_hour': 25, 'min_hours': 250},
            {'vehicle_name': 'Traveller 17 Seater', 'base_price': 7500, 'price_per_hour': 30, 'min_hours': 250},
        ]

        total_created = 0

        # Create local hour tariffs
        total_created += self.create_tariffs('local_hour', local_hour_tariffs)
        
        # Create outstation day tariffs
        total_created += self.create_tariffs('outstation_day', outstation_day_tariffs)
        
        # Create outstation km tariffs
        total_created += self.create_tariffs('outstation_km', outstation_km_tariffs)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {total_created} total tariff records')
        )

    def create_tariffs(self, tariff_type, tariff_data_list):
        created_count = 0
        
        self.stdout.write(f'\n--- Creating {tariff_type} tariffs ---')
        
        for tariff_data in tariff_data_list:
            try:
                vehicle = Vehicle.objects.get(name=tariff_data['vehicle_name'])
                
                # Check if tariff already exists
                existing_tariff = Tariff.objects.filter(
                    tariff_type=tariff_type,
                    vehicle=vehicle
                ).first()
                
                if not existing_tariff:
                    Tariff.objects.create(
                        tariff_type=tariff_type,
                        vehicle=vehicle,
                        base_price=tariff_data['base_price'],
                        price_per_hour=tariff_data['price_per_hour'],
                        min_hours=tariff_data['min_hours'],
                        description=f"{tariff_type.replace('_', ' ').title()} tariff for {vehicle.display_name}",
                        is_active=True
                    )
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created {tariff_type} tariff for {vehicle.display_name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'- {tariff_type} tariff already exists for {vehicle.display_name}')
                    )
                    
            except Vehicle.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'✗ Vehicle not found: {tariff_data["vehicle_name"]}')
                )
        
        self.stdout.write(f'Created {created_count} {tariff_type} tariff records')
        return created_count