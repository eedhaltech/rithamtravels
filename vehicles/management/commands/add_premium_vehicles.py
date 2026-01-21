from django.core.management.base import BaseCommand
from vehicles.models import Vehicle


class Command(BaseCommand):
    help = 'Add premium vehicles including BMW and Audi'

    def handle(self, *args, **options):
        vehicles_data = [
            # BMW Vehicles
            {
                'name': 'BMW 3 Series',
                'description': 'Luxury sedan with premium comfort and advanced features',
                'max_seats': 4,
                'luggage_capacity': '2 Large + 2 Small',
                'fuel_type': 'petrol',
                'ac_type': 'ac',
                'fare_per_km': 35.0,
                'driver_charge_per_day': 800.0,
                'per_day_fee': 3500.0,
                'min_km_per_day': 250,
                'fare_per_hour': 450.0,
                'min_hours_local': 4,
                'min_hours_fee_local': 1800.0,
                'max_distance_min_hours': 40,
                'fare_per_km_local': 35.0,
            },
            {
                'name': 'BMW 5 Series',
                'description': 'Executive luxury sedan with spacious interior and premium amenities',
                'max_seats': 4,
                'luggage_capacity': '3 Large + 2 Small',
                'fuel_type': 'petrol',
                'ac_type': 'ac',
                'fare_per_km': 45.0,
                'driver_charge_per_day': 1000.0,
                'per_day_fee': 4500.0,
                'min_km_per_day': 250,
                'fare_per_hour': 550.0,
                'min_hours_local': 4,
                'min_hours_fee_local': 2200.0,
                'max_distance_min_hours': 40,
                'fare_per_km_local': 45.0,
            },
            {
                'name': 'BMW X3',
                'description': 'Luxury SUV with all-terrain capability and premium comfort',
                'max_seats': 5,
                'luggage_capacity': '3 Large + 3 Small',
                'fuel_type': 'diesel',
                'ac_type': 'ac',
                'fare_per_km': 40.0,
                'driver_charge_per_day': 900.0,
                'per_day_fee': 4000.0,
                'min_km_per_day': 250,
                'fare_per_hour': 500.0,
                'min_hours_local': 4,
                'min_hours_fee_local': 2000.0,
                'max_distance_min_hours': 40,
                'fare_per_km_local': 40.0,
            },
            # Audi Vehicles
            {
                'name': 'Audi A4',
                'description': 'Premium luxury sedan with cutting-edge technology and comfort',
                'max_seats': 4,
                'luggage_capacity': '2 Large + 2 Small',
                'fuel_type': 'petrol',
                'ac_type': 'ac',
                'fare_per_km': 38.0,
                'driver_charge_per_day': 850.0,
                'per_day_fee': 3800.0,
                'min_km_per_day': 250,
                'fare_per_hour': 480.0,
                'min_hours_local': 4,
                'min_hours_fee_local': 1920.0,
                'max_distance_min_hours': 40,
                'fare_per_km_local': 38.0,
            },
            {
                'name': 'Audi A6',
                'description': 'Executive luxury sedan with sophisticated design and premium features',
                'max_seats': 4,
                'luggage_capacity': '3 Large + 2 Small',
                'fuel_type': 'petrol',
                'ac_type': 'ac',
                'fare_per_km': 48.0,
                'driver_charge_per_day': 1100.0,
                'per_day_fee': 4800.0,
                'min_km_per_day': 250,
                'fare_per_hour': 600.0,
                'min_hours_local': 4,
                'min_hours_fee_local': 2400.0,
                'max_distance_min_hours': 40,
                'fare_per_km_local': 48.0,
            },
            {
                'name': 'Audi Q5',
                'description': 'Luxury SUV with quattro all-wheel drive and premium interior',
                'max_seats': 5,
                'luggage_capacity': '3 Large + 3 Small',
                'fuel_type': 'diesel',
                'ac_type': 'ac',
                'fare_per_km': 42.0,
                'driver_charge_per_day': 950.0,
                'per_day_fee': 4200.0,
                'min_km_per_day': 250,
                'fare_per_hour': 520.0,
                'min_hours_local': 4,
                'min_hours_fee_local': 2080.0,
                'max_distance_min_hours': 40,
                'fare_per_km_local': 42.0,
            },
            # Additional Premium Vehicles
            {
                'name': 'Mercedes-Benz C-Class',
                'description': 'Luxury sedan with elegant design and advanced safety features',
                'max_seats': 4,
                'luggage_capacity': '2 Large + 2 Small',
                'fuel_type': 'petrol',
                'ac_type': 'ac',
                'fare_per_km': 36.0,
                'driver_charge_per_day': 800.0,
                'per_day_fee': 3600.0,
                'min_km_per_day': 250,
                'fare_per_hour': 460.0,
                'min_hours_local': 4,
                'min_hours_fee_local': 1840.0,
                'max_distance_min_hours': 40,
                'fare_per_km_local': 36.0,
            },
            {
                'name': 'Mercedes-Benz E-Class',
                'description': 'Executive luxury sedan with superior comfort and technology',
                'max_seats': 4,
                'luggage_capacity': '3 Large + 2 Small',
                'fuel_type': 'petrol',
                'ac_type': 'ac',
                'fare_per_km': 46.0,
                'driver_charge_per_day': 1000.0,
                'per_day_fee': 4600.0,
                'min_km_per_day': 250,
                'fare_per_hour': 580.0,
                'min_hours_local': 4,
                'min_hours_fee_local': 2320.0,
                'max_distance_min_hours': 40,
                'fare_per_km_local': 46.0,
            },
            {
                'name': 'Jaguar XF',
                'description': 'British luxury sedan with distinctive design and performance',
                'max_seats': 4,
                'luggage_capacity': '2 Large + 2 Small',
                'fuel_type': 'petrol',
                'ac_type': 'ac',
                'fare_per_km': 44.0,
                'driver_charge_per_day': 950.0,
                'per_day_fee': 4400.0,
                'min_km_per_day': 250,
                'fare_per_hour': 560.0,
                'min_hours_local': 4,
                'min_hours_fee_local': 2240.0,
                'max_distance_min_hours': 40,
                'fare_per_km_local': 44.0,
            },
            {
                'name': 'Volvo XC90',
                'description': 'Luxury SUV with 7-seater capacity and advanced safety features',
                'max_seats': 7,
                'luggage_capacity': '4 Large + 4 Small',
                'fuel_type': 'diesel',
                'ac_type': 'ac',
                'fare_per_km': 38.0,
                'driver_charge_per_day': 900.0,
                'per_day_fee': 3800.0,
                'min_km_per_day': 250,
                'fare_per_hour': 480.0,
                'min_hours_local': 4,
                'min_hours_fee_local': 1920.0,
                'max_distance_min_hours': 40,
                'fare_per_km_local': 38.0,
            },
            # Additional Standard Vehicles
            {
                'name': 'Toyota Camry Hybrid',
                'description': 'Eco-friendly luxury sedan with hybrid technology',
                'max_seats': 4,
                'luggage_capacity': '2 Large + 2 Small',
                'fuel_type': 'hybrid',
                'ac_type': 'ac',
                'fare_per_km': 28.0,
                'driver_charge_per_day': 700.0,
                'per_day_fee': 2800.0,
                'min_km_per_day': 250,
                'fare_per_hour': 350.0,
                'min_hours_local': 4,
                'min_hours_fee_local': 1400.0,
                'max_distance_min_hours': 40,
                'fare_per_km_local': 28.0,
            },
            {
                'name': 'Honda City',
                'description': 'Comfortable sedan with good fuel efficiency and modern features',
                'max_seats': 4,
                'luggage_capacity': '2 Large + 1 Small',
                'fuel_type': 'petrol',
                'ac_type': 'ac',
                'fare_per_km': 16.0,
                'driver_charge_per_day': 500.0,
                'per_day_fee': 1600.0,
                'min_km_per_day': 250,
                'fare_per_hour': 200.0,
                'min_hours_local': 3,
                'min_hours_fee_local': 600.0,
                'max_distance_min_hours': 30,
                'fare_per_km_local': 16.0,
            },
        ]

        created_count = 0
        updated_count = 0

        for vehicle_data in vehicles_data:
            vehicle, created = Vehicle.objects.get_or_create(
                name=vehicle_data['name'],
                defaults=vehicle_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created vehicle: {vehicle.name}')
                )
            else:
                # Update existing vehicle with new data
                for key, value in vehicle_data.items():
                    setattr(vehicle, key, value)
                vehicle.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated vehicle: {vehicle.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {created_count + updated_count} vehicles '
                f'({created_count} created, {updated_count} updated)'
            )
        )