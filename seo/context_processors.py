"""
SEO Context Processor for Ritham Tours & Travels
Provides global SEO data to all templates
"""

from django.conf import settings

def seo_context(request):
    """Add global SEO context to all templates"""
    return {
        'site_seo': {
            'site_name': getattr(settings, 'COMPANY_NAME', 'Ritham Tours & Travels'),
            'site_url': getattr(settings, 'SITE_URL', 'https://rithamtravels.in'),
            'site_domain': getattr(settings, 'SITE_DOMAIN', 'https://rithamtravels.in'),
            'default_og_image': '/static/admin/img/logo/logo_ritham.png',
            'company_name': getattr(settings, 'COMPANY_NAME', 'Ritham Tours & Travels'),
            'company_phone': getattr(settings, 'COMPANY_PHONE', '+91 97871 10763'),
            'company_email': getattr(settings, 'COMPANY_EMAIL', 'rithamtravels@gmail.com'),
            'company_address': getattr(settings, 'COMPANY_ADDRESS', 'Coimbatore, Tamil Nadu, India'),
            'twitter_handle': '@rithamtravels',
            'facebook_app_id': getattr(settings, 'FACEBOOK_APP_ID', ''),
            'google_analytics_id': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
            'google_site_verification': getattr(settings, 'GOOGLE_SITE_VERIFICATION', ''),
        }
    }