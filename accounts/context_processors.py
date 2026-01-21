from .models import SystemSettings


def system_settings(request):
    """
    Context processor to make system settings available in all templates
    """
    try:
        settings = SystemSettings.get_settings()
        return {
            'system_settings': settings
        }
    except Exception as e:
        # Return default settings if there's an error
        print(f"Context processor error: {e}")  # Debug print
        # Create a simple object with default values
        class DefaultSettings:
            upi_payments_enabled = False  # Set to OFF by default
            default_payment_method = 'driver'
            advance_payment_percentage = 20.0
            gst_enabled = False  # Set to OFF by default
            hill_station_charges_enabled = True
            online_booking_enabled = True
            show_vehicle_images = True
            primary_phone = '+91 97871 10763'
            email_address = 'rithamtravels@gmail.com'
            whatsapp_number = '+91 97871 10763'
        
        return {
            'system_settings': DefaultSettings()
        }