from django.core.management.base import BaseCommand
from accounts.models import SystemSettings


class Command(BaseCommand):
    help = 'Initialize SystemSettings with proper default values'

    def handle(self, *args, **options):
        # Get or create the settings instance
        settings = SystemSettings.get_settings()
        
        # Display current settings
        self.stdout.write(self.style.SUCCESS('Current SystemSettings:'))
        self.stdout.write(f'  GST Enabled: {settings.gst_enabled}')
        self.stdout.write(f'  UPI Payments Enabled: {settings.upi_payments_enabled}')
        self.stdout.write(f'  Default Payment Method: {settings.default_payment_method}')
        
        # Ensure GST is OFF by default
        if settings.gst_enabled:
            settings.gst_enabled = False
            settings.save()
            self.stdout.write(self.style.WARNING('GST setting was ON, changed to OFF'))
        else:
            self.stdout.write(self.style.SUCCESS('GST setting is already OFF'))
        
        # Ensure UPI is OFF by default
        if settings.upi_payments_enabled:
            settings.upi_payments_enabled = False
            settings.save()
            self.stdout.write(self.style.WARNING('UPI setting was ON, changed to OFF'))
        else:
            self.stdout.write(self.style.SUCCESS('UPI setting is already OFF'))
        
        # Set default payment method to driver when UPI is off
        if settings.default_payment_method != 'driver':
            settings.default_payment_method = 'driver'
            settings.save()
            self.stdout.write(self.style.WARNING('Default payment method changed to "driver"'))
        else:
            self.stdout.write(self.style.SUCCESS('Default payment method is already "driver"'))
        
        self.stdout.write(self.style.SUCCESS('\nSystemSettings initialized successfully!'))
        self.stdout.write(self.style.SUCCESS('You can now test the GST toggle on /travels-dashboard/settings/'))