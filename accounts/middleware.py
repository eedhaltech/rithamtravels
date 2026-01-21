"""
Middleware for handling travel user permissions
"""
from django.utils.deprecation import MiddlewareMixin


class TravelUserPermissionMiddleware(MiddlewareMixin):
    """
    Middleware to ensure travel users have staff access for admin panel
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            # Check if user is a travel user
            if hasattr(request.user, 'user_type') and request.user.user_type == 'travels':
                # Ensure they have staff access
                if not request.user.is_staff:
                    request.user.is_staff = True
                    request.user.save(update_fields=['is_staff'])
        return None
