from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import GSTRate


class Command(BaseCommand):
    help = 'Create initial GST rate data'

    def handle(self, *args, **options):
        # Create GST rates
        gst_rates = [
            {
                'service_type': 'transport',
                'gst_percentage': 18.00,
                'description': 'GST for transport services including cab bookings, tours, and travel packages',
                'effective_from': timezone.now().date(),
                'is_active': True
            },
            {
                'service_type': 'accommodation',
                'gst_percentage': 12.00,
                'description': 'GST for accommodation services',
                'effective_from': timezone.now().date(),
                'is_active': True
            },
            {
                'service_type': 'tour_package',
                'gst_percentage': 18.00,
                'description': 'GST for tour packages and travel services',
                'effective_from': timezone.now().date(),
                'is_active': True
            },
            {
                'service_type': 'general',
                'gst_percentage': 18.00,
                'description': 'GST for general services',
                'effective_from': timezone.now().date(),
                'is_active': True
            }
        ]

        created_count = 0
        for rate_data in gst_rates:
            gst_rate, created = GSTRate.objects.get_or_create(
                service_type=rate_data['service_type'],
                effective_from=rate_data['effective_from'],
                defaults=rate_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created GST rate: {gst_rate.get_service_type_display()} - {gst_rate.gst_percentage}%'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'GST rate already exists: {gst_rate.get_service_type_display()} - {gst_rate.gst_percentage}%'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} GST rates')
        )