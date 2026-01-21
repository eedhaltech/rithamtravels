"""
URL configuration for ritham_tours project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Customize admin site
admin.site.site_header = 'Ritham Tours & Travels Administration'
admin.site.site_title = 'Ritham Tours Admin'
admin.site.index_title = 'Welcome to Ritham Tours Administration'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('bookings.urls')),
    path('api/', include('tours.urls')),
    path('api/', include('vehicles.urls')),
    path('api/', include('blog.urls')),
    path('', include('accounts.urls')),
    path('', include('bookings.urls')),
    path('', include('tours.urls')),
    path('', include('blog.urls')),
    path('', include('enquiries.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

