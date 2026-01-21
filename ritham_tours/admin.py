"""
Custom Admin Site Configuration for Travel Users
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class TravelsAdminSite(AdminSite):
    """
    Custom admin site for travel users with relaxed permissions
    """
    site_header = _('Ritham Tours - Travel Management')
    site_title = _('Travel Admin')
    index_title = _('Travel Dashboard')
    
    def has_permission(self, request):
        """
        Allow access to travel users (user_type='travels') even if not superuser
        """
        return request.user.is_active and (
            request.user.is_staff or 
            (hasattr(request.user, 'user_type') and request.user.user_type == 'travels')
        )


# Create custom admin site instance
travels_admin_site = TravelsAdminSite(name='travels_admin')
