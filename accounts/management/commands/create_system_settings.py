from django.core.management.base import BaseCommand
from accounts.models import SystemSettings


class Command(BaseCommand):
    help = 'Create initial system settings with default values'

    def handle(self, *args, **options):
        # Get or create system settings
        settings, created = SystemSettings.objects.get_or_create(pk=1)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created initial system settings')
            )
        else:
            self.stdout.write(
                self.style.WARNING('System settings already exist')
            )
        
        # Display current settings
        self.stdout.write('\nCurrent System Settings:')
        self.stdout.write(f'UPI Payments Enabled: {settings.upi_payments_enabled}')
        self.stdout.write(f'Default Payment Method: {settings.default_payment_method}')
        self.stdout.write(f'Advance Payment Percentage: {settings.advance_payment_percentage}%')
        self.stdout.write(f'GST Enabled: {settings.gst_enabled}')
        self.stdout.write(f'Hill Station Charges Enabled: {settings.hill_station_charges_enabled}')
        self.stdout.write(f'Online Booking Enabled: {settings.online_booking_enabled}')
        self.stdout.write(f'Primary Phone: {settings.primary_phone}')
        self.stdout.write(f'Email Address: {settings.email_address}')
        
        self.stdout.write(
            self.style.SUCCESS('\nSystem settings are ready!')
        )