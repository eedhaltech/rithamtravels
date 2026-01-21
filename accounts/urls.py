from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('customer/signup/', views.CustomerSignupView.as_view(), name='customer_signup_api'),
    path('travels/signup/', views.TravelsSignupView.as_view(), name='travels_signup_api'),
    path('customer/login/', views.customer_login, name='customer_login_api'),
    path('travels/login/', views.travels_login, name='travels_login_api'),
    path('api/logout/', views.logout, name='logout_api'),
    
    # Forgot Password API endpoints
    path('forgot-password/send-otp/', views.forgot_password_send_otp, name='forgot_password_send_otp'),
    path('forgot-password/verify-otp/', views.forgot_password_verify_otp, name='forgot_password_verify_otp'),
    path('forgot-password/otp-status/', views.get_otp_status, name='get_otp_status'),
    
    # Template views
    path('customer-login/', views.CustomerLoginView.as_view(), name='customer_login'),
    path('travels-login/', views.TravelsLoginView.as_view(), name='travels_login'),
    path('customer-signup/', views.CustomerSignupPageView.as_view(), name='customer_signup'),
    path('travels-signup/', views.TravelsSignupPageView.as_view(), name='travels_signup'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('travels-dashboard/', views.travels_dashboard, name='travels_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    
    # Travel Dashboard Management URLs
    path('travels-dashboard/vehicles/', views.travels_vehicles_list, name='travels_vehicles_list'),
    path('travels-dashboard/vehicles/add/', views.travels_vehicle_add, name='travels_vehicle_add'),
    path('travels-dashboard/vehicles/<int:vehicle_id>/edit/', views.travels_vehicle_edit, name='travels_vehicle_edit'),
    path('travels-dashboard/vehicles/<int:vehicle_id>/delete/', views.travels_vehicle_delete, name='travels_vehicle_delete'),
    path('travels-dashboard/bookings/', views.travels_bookings_list, name='travels_bookings_list'),
    path('travels-dashboard/bookings/<int:booking_id>/', views.travels_booking_detail, name='travels_booking_detail'),
    path('travels-dashboard/payments/', views.travels_payments_list, name='travels_payments_list'),
    path('travels-dashboard/payments/<int:payment_id>/update/', views.travels_payment_update, name='travels_payment_update'),
    
    # City Management URLs
    path('travels-dashboard/cities/', views.travels_cities_list, name='travels_cities_list'),
    path('travels-dashboard/cities/add/', views.travels_city_add, name='travels_city_add'),
    path('travels-dashboard/cities/<int:city_id>/edit/', views.travels_city_edit, name='travels_city_edit'),
    path('travels-dashboard/cities/<int:city_id>/delete/', views.travels_city_delete, name='travels_city_delete'),
    path('travels-dashboard/cities/<int:city_id>/local-areas/', views.travels_local_areas_list, name='travels_local_areas_list'),
    path('travels-dashboard/cities/<int:city_id>/local-areas/add/', views.travels_local_area_add, name='travels_local_area_add'),
    path('travels-dashboard/local-areas/<int:area_id>/delete/', views.travels_local_area_delete, name='travels_local_area_delete'),
    # Package Management URLs
    path('travels-dashboard/packages/', views.travels_packages_list, name='travels_packages_list'),
    path('travels-dashboard/packages/add/', views.travels_package_add, name='travels_package_add'),
    path('travels-dashboard/packages/<int:package_id>/edit/', views.travels_package_edit, name='travels_package_edit'),
    path('travels-dashboard/packages/<int:package_id>/delete/', views.travels_package_delete, name='travels_package_delete'),
    
    # Settings Management URLs
    path('travels-dashboard/settings/', views.travels_settings, name='travels_settings'),
    path('travels-dashboard/settings/api/', views.travels_settings_api, name='travels_settings_api'),
]

