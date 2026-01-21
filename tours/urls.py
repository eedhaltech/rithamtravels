from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('tour-planner/', views.TourPlannerView.as_view(), name='tour_planner'),
    path('tour-info/<str:city_slug>/', views.TourInfoView.as_view(), name='tour_info'),
    path('tour-info/', views.TourInfoView.as_view(), name='tour_info_default'),
    path('tariff/', views.TariffView.as_view(), name='tariff'),
    path('tariff/local-hour/', views.TariffLocalHourView.as_view(), name='tariff_local_hour'),
    path('tariff/outstation-day/', views.TariffOutstationDayView.as_view(), name='tariff_outstation_day'),
    path('tariff/outstation-km/', views.TariffOutstationKmView.as_view(), name='tariff_outstation_km'),
    path('tariff/oneway-fixed/', views.TariffOnewayFixedView.as_view(), name='tariff_oneway_fixed'),
    path('tariff/oneway-km/', views.TariffOnewayKmView.as_view(), name='tariff_oneway_km'),
    
    # Destination Pages
    path('destinations/ooty/', views.OotyView.as_view(), name='ooty'),
    path('destinations/kodaikanal/', views.KodaikanalView.as_view(), name='kodaikanal'),
    path('destinations/munnar/', views.MunnarView.as_view(), name='munnar'),
    path('destinations/coorg/', views.CoorgView.as_view(), name='coorg'),
    path('destinations/mysore/', views.MysoreView.as_view(), name='mysore'),
    path('destinations/yercaud/', views.YercaudView.as_view(), name='yercaud'),
    path('destinations/wayanad/', views.WayanadView.as_view(), name='wayanad'),
    
    # About Us Page
    path('about-us/', views.AboutUsView.as_view(), name='about_us'),
    
    # API endpoints
    path('api/cities/', views.cities_api, name='cities_api'),
    path('api/cities/<int:city_id>/sightseeing/', views.city_sightseeing_api, name='city_sightseeing_api'),
    path('api/vehicles/', views.vehicles_api, name='vehicles_api'),
    path('api/tour-packages/', views.tour_packages_api, name='tour_packages_api'),
    path('api/tour-packages-by-days/', views.tour_packages_by_days_api, name='tour_packages_by_days_api'),
    path('api/local-areas/', views.get_local_areas, name='get_local_areas'),
    path('api/route-distance/', views.get_route_distance, name='get_route_distance'),
    path('api/calculate-amount/', views.calculate_booking_amount, name='calculate_booking_amount'),
]

