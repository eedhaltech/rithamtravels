from django.apps import AppConfig


class EnquiriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'enquiries'
    
    def ready(self):
        """Import signals when the app is ready"""
        import enquiries.signals

