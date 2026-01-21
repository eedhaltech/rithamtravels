from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import City, LocalArea, Route, SightseeingSpot, TourPackage, Tariff
from vehicles.models import Vehicle
import json
import datetime as dt


@api_view(['GET'])
@permission_classes([AllowAny])
def cities_api(request):
    """API endpoint to get all active cities"""
    cities = City.objects.filter(is_active=True).values('id', 'name')
    return Response(list(cities))


@api_view(['GET'])
@permission_classes([AllowAny])
def city_sightseeing_api(request, city_id):
    """API endpoint to get city sightseeing data"""
    try:
        city = City.objects.get(id=city_id, is_active=True)
        return Response({
            'city_id': city.id,
            'city_name': city.name,
            'tourist_places': city.get_tourist_places_list(),
            'sightseeing_kilometers': float(city.sightseeing_kilometers)
        })
    except City.DoesNotExist:
        return Response({'error': 'City not found'}, status=404)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def vehicles_api(request):
    """API endpoint to get available vehicles with pricing"""
    from vehicles.models import Vehicle
    
    print(f"Vehicles API called with method: {request.method}")
    
    # Get trip data from request (handle both GET and POST)
    if request.method == 'POST':
        trip_data = request.data
        print(f"POST data: {trip_data}")
    else:
        trip_data = request.GET
        print(f"GET data: {trip_data}")
    
    print(f"Trip data: {trip_data}")
    trip_type = trip_data.get('trip_type', 'round')
    total_distance = float(trip_data.get('total_distance', 0))
    total_days = int(trip_data.get('total_days', 1))
    
    # Get all available vehicles
    vehicles = Vehicle.objects.filter(is_available=True, is_active=True)
    print(f"Found {vehicles.count()} vehicles")
    
    vehicle_list = []
    for vehicle in vehicles:
        # Calculate total amount based on trip type
        if trip_type == 'round':
            # For round trip: use day-based calculation
            # Total Vehicle Fee = Number of Days × Vehicle Fee
            # Total Driver Fee = Number of Days × Driver Fee
            # Total Amount = Total Vehicle Fee + Total Driver Fee
            vehicle_fee = total_days * float(vehicle.per_day_fee)
            driver_charge = total_days * float(vehicle.driver_charge_per_day)
            total_amount = vehicle_fee + driver_charge
            
            calculation_details = f"{total_days} Day(s) (Vehicle Fee + Driver Fee)"
        elif trip_type == 'multicity':
            # For multicity: use specific formula
            # Total Vehicle Fee = Number of Days × Vehicle Fee
            # Total Driver Fee = Number of Days × Driver Fee
            # Chargeable Kilometers = Total Kilometers − (Number of Days × Vehicle Free KMs per Day)
            # Extra Kilometer Charge = Chargeable Kilometers × Fare per KM
            # Total Amount = Total Vehicle Fee + Total Driver Fee + Extra Kilometer Charge
            vehicle_fee = total_days * float(vehicle.per_day_fee)
            driver_charge = total_days * float(vehicle.driver_charge_per_day)
            free_km_total = total_days * vehicle.min_km_per_day
            chargeable_km = max(0, total_distance - free_km_total)
            extra_km_charge = chargeable_km * float(vehicle.fare_per_km)
            total_amount = vehicle_fee + driver_charge + extra_km_charge
            
            if chargeable_km > 0:
                calculation_details = f"{total_days} Day(s) + {chargeable_km:.0f} Extra KM"
            else:
                calculation_details = f"{total_days} Day(s) + No Extra KM"
        elif trip_type == 'local':
            # For local trips: use hour-based calculation with optional distance charges
            # Get selected hours from request, default to minimum hours
            selected_hours = int(trip_data.get('selected_hours', vehicle.min_hours_local or 3))
            
            # Calculate hour-based charges
            min_hours = vehicle.min_hours_local or 3
            min_hours_fee = float(vehicle.min_hours_fee_local or 0)
            fare_per_hour = float(vehicle.fare_per_hour or 0)
            max_included_distance = vehicle.max_distance_min_hours or 30
            fare_per_km_local = float(vehicle.fare_per_km_local or 0)
            
            # Base amount from hours
            if selected_hours <= min_hours:
                # Use minimum hours fee
                total_amount = min_hours_fee
                calculation_details = f"{selected_hours} Hours (Min. Hours Fee)"
            else:
                # Minimum hours fee + additional hours
                extra_hours = selected_hours - min_hours
                total_amount = min_hours_fee + (extra_hours * fare_per_hour)
                calculation_details = f"{min_hours} Hours (Min. Fee) + {extra_hours} Hours (₹{fare_per_hour}/hr)"
            
            # Add distance-based charges if distance exceeds included KM
            if total_distance > max_included_distance:
                extra_distance = total_distance - max_included_distance
                extra_distance_charge = extra_distance * fare_per_km_local
                total_amount += extra_distance_charge
                
                if selected_hours <= min_hours:
                    calculation_details = f"{selected_hours} Hours (Min. Fee) + {extra_distance:.1f} Extra KM"
                else:
                    calculation_details = f"{min_hours} Hours (Min. Fee) + {extra_hours} Hours (₹{fare_per_hour}/hr) + {extra_distance:.1f} Extra KM"
        else:
            # For other trip types: use distance-based calculation
            min_distance = vehicle.min_km_per_day * total_days
            actual_distance = max(total_distance, min_distance)
            distance_charge = actual_distance * float(vehicle.fare_per_km)
            driver_charge = total_days * float(vehicle.driver_charge_per_day)
            vehicle_day_charge = total_days * float(vehicle.per_day_fee)
            total_amount = distance_charge + driver_charge + vehicle_day_charge
            
            calculation_details = f"{actual_distance:.0f} KM + {total_days} Day(s)"
        
        # Prepare vehicle data
        vehicle_data = {
            'id': vehicle.id,
            'name': vehicle.name,
            'description': vehicle.description or '',
            'image': vehicle.image.url if vehicle.image else None,
            'seating_info': f"{vehicle.max_seats} Seater",
            'fuel_type': vehicle.get_fuel_type_display(),
            'ac_type': vehicle.get_ac_type_display(),
            'category': 'Premium' if vehicle.fare_per_km > 15 else 'Standard',
            'min_km_per_day': vehicle.min_km_per_day,
            'fare_per_km': float(vehicle.fare_per_km),
            'driver_charge_per_day': float(vehicle.driver_charge_per_day),
            'per_day_fee': float(vehicle.per_day_fee),
            # Local trip fields
            'fare_per_hour': float(vehicle.fare_per_hour),
            'min_hours_local': vehicle.min_hours_local,
            'min_hours_fee_local': float(vehicle.min_hours_fee_local),
            'max_distance_min_hours': vehicle.max_distance_min_hours,
            'fare_per_km_local': float(vehicle.fare_per_km_local),
            'total_amount': round(total_amount, 2),
            'calculation_details': calculation_details
        }
        
        vehicle_list.append(vehicle_data)
    
    # If no vehicles found, create sample data
    if not vehicle_list:
        print("No vehicles found in database, creating sample data")
        vehicle_list = [
            {
                'id': 1,
                'name': 'Toyota Innova',
                'description': 'Comfortable 7-seater SUV',
                'image': None,
                'seating_info': '7 Seater',
                'fuel_type': 'Diesel',
                'ac_type': 'AC',
                'category': 'Premium',
                'min_km_per_day': 250,
                'fare_per_km': 15.0,
                'driver_charge_per_day': 500.0,
                'total_amount': round((max(total_distance, 250 * total_days) * 15.0) + (total_days * 500.0), 2),
                'calculation_details': f"{max(total_distance, 250 * total_days):.0f} KM + {total_days} Day(s)"
            },
            {
                'id': 2,
                'name': 'Maruti Swift Dzire',
                'description': 'Compact sedan for city travel',
                'image': None,
                'seating_info': '4 Seater',
                'fuel_type': 'Petrol',
                'ac_type': 'AC',
                'category': 'Standard',
                'min_km_per_day': 200,
                'fare_per_km': 12.0,
                'driver_charge_per_day': 400.0,
                'total_amount': round((max(total_distance, 200 * total_days) * 12.0) + (total_days * 400.0), 2),
                'calculation_details': f"{max(total_distance, 200 * total_days):.0f} KM + {total_days} Day(s)"
            },
            {
                'id': 3,
                'name': 'Mahindra Scorpio',
                'description': 'Rugged SUV for long trips',
                'image': None,
                'seating_info': '8 Seater',
                'fuel_type': 'Diesel',
                'ac_type': 'AC',
                'category': 'Premium',
                'min_km_per_day': 300,
                'fare_per_km': 18.0,
                'driver_charge_per_day': 600.0,
                'total_amount': round((max(total_distance, 300 * total_days) * 18.0) + (total_days * 600.0), 2),
                'calculation_details': f"{max(total_distance, 300 * total_days):.0f} KM + {total_days} Day(s)"
            }
        ]
    
    # Sort by total amount
    vehicle_list.sort(key=lambda x: x['total_amount'])
    
    return Response({
        'vehicles': vehicle_list,
        'trip_summary': {
            'type': trip_type,
            'distance': total_distance,
            'days': total_days
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def tour_packages_api(request):
    """API endpoint to get tour packages available for a given city"""
    city_id = request.GET.get('city_id')
    try:
        if city_id:
            packages = TourPackage.objects.filter(is_active=True, cities__id=city_id).distinct()
        else:
            packages = TourPackage.objects.filter(is_active=True)

        package_list = [
            {
                'id': p.id,
                'name': p.name,
                'days': p.days,
                'price_per_person': float(p.price_per_person) if p.price_per_person else None,
                'price_per_vehicle': float(p.price_per_vehicle) if p.price_per_vehicle else None,
            }
            for p in packages
        ]

        return Response({'packages': package_list})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def tour_packages_by_days_api(request):
    """API endpoint to get tour packages available for a specific number of days"""
    days = request.GET.get('days')
    try:
        if not days:
            return Response({'error': 'Days parameter is required'}, status=400)
        
        days = int(days)
        packages = TourPackage.objects.filter(is_active=True, days=days)

        package_list = [
            {
                'id': p.id,
                'name': p.name,
                'days': p.days,
                'price_per_person': float(p.price_per_person) if p.price_per_person else None,
                'price_per_vehicle': float(p.price_per_vehicle) if p.price_per_vehicle else None,
                'cities': [city.name for city in p.cities.all()]
            }
            for p in packages
        ]

        return Response({'packages': package_list})
    except ValueError:
        return Response({'error': 'Invalid days parameter'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


from seo.mixins import HomeSEOMixin


class HomeView(HomeSEOMixin, TemplateView):
    template_name = 'tours/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = City.objects.filter(is_active=True)
        context['tour_packages'] = TourPackage.objects.filter(is_active=True)[:8]
        return context


class TourPlannerView(TemplateView):
    template_name = 'tours/tour_planner.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cities = City.objects.filter(is_active=True)
        vehicles = Vehicle.objects.filter(is_available=True)
        
        context['cities'] = cities
        context['vehicles'] = vehicles
        context['tour_packages'] = TourPackage.objects.filter(is_active=True)[:5]
        
        # Add JSON-serializable data for JavaScript
        context['cities_json'] = [
            {'id': city.id, 'name': city.name}
            for city in cities
        ]
        context['vehicles_json'] = [
            {
                'id': vehicle.id,
                'name': vehicle.name,
                'min_km_per_day': float(vehicle.min_km_per_day),
                'fare_per_km': float(vehicle.fare_per_km),
                'driver_charge_per_day': float(vehicle.driver_charge_per_day)
            }
            for vehicle in vehicles
        ]
        
        return context


class TourInfoView(TemplateView):
    template_name = 'tours/tour_info.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get parameters from URL
        trip_type = self.request.GET.get('trip_type')
        pickup_city_id = self.request.GET.get('pickup_city')
        pickup_date = self.request.GET.get('pickup_date')
        drop_date = self.request.GET.get('drop_date')
        pickup_time = self.request.GET.get('pickup_time')
        pickup_time_period = self.request.GET.get('pickup_time_period')
        trip_basis = self.request.GET.get('trip_basis')
        
        # Process trip information
        context['trip_type'] = trip_type
        context['pickup_date'] = pickup_date
        context['drop_date'] = drop_date
        context['pickup_time'] = pickup_time
        context['pickup_time_period'] = pickup_time_period
        context['trip_basis'] = trip_basis
        
        # Get pickup city
        if pickup_city_id:
            try:
                pickup_city = City.objects.get(id=pickup_city_id)
                context['pickup_city'] = pickup_city.name
                context['pickup_city_obj'] = pickup_city
                context['pickup_city_id'] = int(pickup_city_id)  # Add pickup city ID for JavaScript
            except City.DoesNotExist:
                context['pickup_city'] = None
                context['pickup_city_obj'] = None
                context['pickup_city_id'] = None
        else:
            context['pickup_city_id'] = None
        
        # Set display values
        if trip_type == 'round':
            context['trip_title'] = 'Round Trip Information'
            context['trip_type_display'] = 'Round Trip'
        elif trip_type == 'multicity':
            context['trip_title'] = 'Multi-City Trip Information'
            context['trip_type_display'] = 'Multi-City Tour'
        else:
            context['trip_title'] = 'Trip Information'
            context['trip_type_display'] = trip_type.title() if trip_type else 'Unknown'
        
        context['trip_basis_display'] = 'Day Basis' if trip_basis == 'day' else 'KM Basis'
        
        # Handle multicity routes
        if trip_type == 'multicity':
            routes = []
            multicity_dates = self.request.GET.getlist('multicity_date[]')
            multicity_from = self.request.GET.getlist('multicity_from[]')
            multicity_to = self.request.GET.getlist('multicity_to[]')
            multicity_distance = self.request.GET.getlist('multicity_distance[]')
            
            # Debug: Print received data
            print(f"Multicity data received:")
            print(f"  Dates: {multicity_dates}")
            print(f"  From: {multicity_from}")
            print(f"  To: {multicity_to}")
            print(f"  Distances: {multicity_distance}")
            
            for i in range(len(multicity_dates)):
                if i < len(multicity_from) and i < len(multicity_to):
                    try:
                        # Parse from location (city_X or area_X)
                        from_value = multicity_from[i]
                        from_city_id = None
                        if from_value.startswith('city_'):
                            from_city_id = from_value.replace('city_', '')
                            from_city = City.objects.get(id=from_city_id)
                            from_name = from_city.name
                        elif from_value.startswith('area_'):
                            from_area_id = from_value.replace('area_', '')
                            from_area = LocalArea.objects.get(id=from_area_id)
                            from_name = from_area.name
                            from_city_id = str(from_area.city.id)  # Set city ID for areas
                        else:
                            # Fallback for direct ID
                            from_city_id = from_value
                            from_city = City.objects.get(id=from_value)
                            from_name = from_city.name
                        
                        # Parse to location (city_X or area_X)
                        to_value = multicity_to[i]
                        to_city_id = None
                        if to_value.startswith('city_'):
                            to_city_id = to_value.replace('city_', '')
                            to_city = City.objects.get(id=to_city_id)
                            to_name = to_city.name
                        elif to_value.startswith('area_'):
                            to_area_id = to_value.replace('area_', '')
                            to_area = LocalArea.objects.get(id=to_area_id)
                            to_name = to_area.name
                            to_city_id = str(to_area.city.id)  # Set city ID for areas
                        else:
                            # Fallback for direct ID
                            to_city_id = to_value
                            to_city = City.objects.get(id=to_value)
                            to_name = to_city.name
                        
                        distance = multicity_distance[i] if i < len(multicity_distance) else '0'
                        
                        routes.append({
                            'date': multicity_dates[i],
                            'from_name': from_name,
                            'to_name': to_name,
                            'from_value': from_value,
                            'to_value': to_value,
                            'from_city_id': from_city_id,
                            'to_city_id': to_city_id,
                            'distance': distance
                        })
                    except (City.DoesNotExist, LocalArea.DoesNotExist, ValueError) as e:
                        print(f"Error processing route {i}: {e}")
                        continue
            
            context['routes'] = routes
            
            # Calculate totals for multicity
            if routes:
                total_distance = sum(float(route['distance']) for route in routes if route['distance'])
                context['total_distance'] = total_distance
                context['total_routes'] = len(routes)
                
                # Calculate total days
                if multicity_dates:
                    dates = [dt.datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in multicity_dates if date_str]
                    if dates:
                        min_date = min(dates)
                        max_date = max(dates)
                        total_days = (max_date - min_date).days + 1
                        context['total_days'] = total_days
                        context['start_date'] = min_date.strftime('%Y-%m-%d')
                        context['end_date'] = max_date.strftime('%Y-%m-%d')
                        
                        # Format dates for display
                        context['start_date_display'] = min_date.strftime('%B %d, %Y')
                        context['end_date_display'] = max_date.strftime('%B %d, %Y')
                
                # Check if it's a circular route
                if len(routes) >= 2:
                    first_from = routes[0]['from_value']
                    last_to = routes[-1]['to_value']
                    context['is_circular'] = (first_from == last_to)
                    
                # Get unique cities/areas visited
                visited_locations = set()
                for route in routes:
                    visited_locations.add(route['from_name'])
                    visited_locations.add(route['to_name'])
                context['visited_locations'] = list(visited_locations)
                context['total_locations'] = len(visited_locations)
                
                print(f"Processed {len(routes)} routes, total distance: {total_distance} KM")
        
        # Handle round trip
        elif trip_type == 'round' and pickup_date and drop_date:
            pickup_dt = dt.datetime.strptime(pickup_date, '%Y-%m-%d').date()
            drop_dt = dt.datetime.strptime(drop_date, '%Y-%m-%d').date()
            context['total_days'] = (drop_dt - pickup_dt).days + 1
        
        # Handle local trip
        elif trip_type == 'local':
            context['trip_title'] = 'Local Trip Information'
            context['trip_type_display'] = 'Local Trip'
            
            # Get local area information
            local_area_id = self.request.GET.get('local_area')
            if local_area_id:
                try:
                    local_area = LocalArea.objects.get(id=local_area_id)
                    context['local_area'] = local_area.name
                    context['local_area_obj'] = local_area
                except LocalArea.DoesNotExist:
                    context['local_area'] = None
                    context['local_area_obj'] = None
            
            # Local trips are typically single day
            context['total_days'] = 1
            context['trip_basis_display'] = 'Hour Basis'
        
        # Handle one way trips
        elif trip_type in ['oneway_fixed', 'oneway_km']:
            if trip_type == 'oneway_fixed':
                context['trip_title'] = 'One Way Drop - Fixed Rate'
                context['trip_type_display'] = 'One Way Drop (Fixed)'
            else:
                context['trip_title'] = 'One Way Drop - KM Basis'
                context['trip_type_display'] = 'One Way Drop (KM Basis)'
            
            # Get from and to cities
            from_city_id = self.request.GET.get('from_city')
            to_city_id = self.request.GET.get('to_city')
            
            if from_city_id:
                try:
                    from_city = City.objects.get(id=from_city_id)
                    context['from_city'] = int(from_city_id)  # Ensure it's an integer
                    context['from_city_obj'] = {
                        'id': from_city.id,
                        'name': from_city.name,
                        'latitude': float(from_city.latitude) if from_city.latitude else None,
                        'longitude': float(from_city.longitude) if from_city.longitude else None
                    }
                except City.DoesNotExist:
                    context['from_city'] = None
                    context['from_city_obj'] = None
            
            if to_city_id:
                try:
                    to_city = City.objects.get(id=to_city_id)
                    context['to_city'] = int(to_city_id)  # Ensure it's an integer
                    context['to_city_obj'] = {
                        'id': to_city.id,
                        'name': to_city.name,
                        'latitude': float(to_city.latitude) if to_city.latitude else None,
                        'longitude': float(to_city.longitude) if to_city.longitude else None
                    }
                except City.DoesNotExist:
                    context['to_city'] = None
                    context['to_city_obj'] = None
            
            # One way trips are single day
            context['total_days'] = 1
            context['trip_basis_display'] = 'Fixed Rate' if trip_type == 'oneway_fixed' else 'KM Basis'
        
        # Handle tour packages
        elif trip_type == 'tour':
            context['trip_title'] = 'Tour Package Information'
            context['trip_type_display'] = 'Tour Package'
            
            # Get package information
            package_type_id = self.request.GET.get('package_type')
            days = self.request.GET.get('days')
            
            if package_type_id:
                try:
                    from tours.models import TourPackage
                    package = TourPackage.objects.get(id=package_type_id)
                    context['package_type'] = package.name
                    context['package_obj'] = package
                except:
                    context['package_type'] = None
                    context['package_obj'] = None
            
            if days:
                context['total_days'] = int(days)
            else:
                context['total_days'] = 1
            
            context['trip_basis_display'] = 'Package Basis'
        
        return context


class TariffView(TemplateView):
    template_name = 'tours/tariff.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tariff_type = self.request.GET.get('type', 'local_hour')
        context['tariff_type'] = tariff_type
        context['tariffs'] = Tariff.objects.filter(tariff_type=tariff_type, is_active=True)
        context['cities'] = City.objects.filter(is_active=True)
        return context


class TariffLocalHourView(TemplateView):
    template_name = 'tours/tariff_local_hour.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Load tariff data from database
        context['tariffs'] = Tariff.objects.filter(
            tariff_type='local_hour', 
            is_active=True
        ).select_related('vehicle').order_by('base_price')
        
        # Load popular tour packages for sidebar
        context['popular_plans'] = TourPackage.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5]
        
        # Load testimonials for sidebar
        from enquiries.models import Testimonial
        context['testimonials'] = Testimonial.objects.filter(
            is_approved=True, 
            is_featured=True
        )[:3]
        
        # Load promotions for sidebar
        from enquiries.models import Promotion
        context['promotions'] = Promotion.objects.filter(
            is_active=True
        )[:3]
        
        return context


class TariffOutstationDayView(TemplateView):
    template_name = 'tours/tariff_outstation_day.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Load tariff data from database
        context['tariffs'] = Tariff.objects.filter(
            tariff_type='outstation_day', 
            is_active=True
        ).select_related('vehicle').order_by('base_price')
        
        # Load popular tour packages for sidebar
        context['popular_plans'] = TourPackage.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5]
        
        # Load testimonials for sidebar
        from enquiries.models import Testimonial
        context['testimonials'] = Testimonial.objects.filter(
            is_approved=True, 
            is_featured=True
        )[:3]
        
        # Load promotions for sidebar
        from enquiries.models import Promotion
        context['promotions'] = Promotion.objects.filter(
            is_active=True
        )[:3]
        
        return context


class TariffOutstationKmView(TemplateView):
    template_name = 'tours/tariff_outstation_km.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Load tariff data from database
        context['tariffs'] = Tariff.objects.filter(
            tariff_type='outstation_km', 
            is_active=True
        ).select_related('vehicle').order_by('base_price')
        
        # Load popular tour packages for sidebar
        context['popular_plans'] = TourPackage.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5]
        
        # Load testimonials for sidebar
        from enquiries.models import Testimonial
        context['testimonials'] = Testimonial.objects.filter(
            is_approved=True, 
            is_featured=True
        )[:3]
        
        # Load promotions for sidebar
        from enquiries.models import Promotion
        context['promotions'] = Promotion.objects.filter(
            is_active=True
        )[:3]
        
        return context


class TariffOnewayFixedView(TemplateView):
    template_name = 'tours/tariff_oneway_fixed.html'


class TariffOnewayKmView(TemplateView):
    template_name = 'tours/tariff_oneway_km.html'


@api_view(['GET'])
@permission_classes([AllowAny])
def get_local_areas(request):
    city_id = request.GET.get('city_id')
    if city_id:
        areas = LocalArea.objects.filter(city_id=city_id).values('id', 'name')
        return Response({
            'local_areas': list(areas),
            'city_id': city_id
        })
    return Response({'local_areas': [], 'city_id': None})


import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

@api_view(['GET'])
@permission_classes([AllowAny])
def get_route_distance(request):
    from_city_id = request.GET.get('from_city_id')
    to_city_id = request.GET.get('to_city_id')
    from_area_id = request.GET.get('from_area_id')
    to_area_id = request.GET.get('to_area_id')
    
    # Get actual city IDs if areas are provided
    if from_area_id:
        try:
            from_area = LocalArea.objects.get(id=from_area_id)
            from_city_id = from_area.city_id
        except LocalArea.DoesNotExist:
            pass
    
    if to_area_id:
        try:
            to_area = LocalArea.objects.get(id=to_area_id)
            to_city_id = to_area.city_id
        except LocalArea.DoesNotExist:
            pass
    
    if from_city_id and to_city_id:
        try:
            # First check if route exists in database (check both directions)
            route = None
            try:
                # Try the direct route first
                route = Route.objects.get(from_city_id=from_city_id, to_city_id=to_city_id)
            except Route.DoesNotExist:
                # Try the reverse route
                try:
                    route = Route.objects.get(from_city_id=to_city_id, to_city_id=from_city_id)
                except Route.DoesNotExist:
                    pass
            
            if route:
                return Response({
                    'distance': float(route.distance),
                    'one_way_fixed_rate': float(route.one_way_fixed_rate) if route.one_way_fixed_rate else None,
                    'source': 'database'
                })
        except Exception as e:
            # If there's any error with database lookup, fall through to calculation
            pass
        
        # Calculate using Haversine formula if no database route found
        try:
            from_city = City.objects.get(id=from_city_id)
            to_city = City.objects.get(id=to_city_id)
            
            # Get area objects if needed
            from_area = None
            to_area = None
            
            if from_area_id:
                from_area = LocalArea.objects.get(id=from_area_id)
            
            if to_area_id:
                to_area = LocalArea.objects.get(id=to_area_id)
            
            # Handle missing coordinates with fallbacks
            def get_fallback_coordinates(city, area=None):
                """Get coordinates with fallbacks for missing data"""
                if area and area.latitude and area.longitude:
                    return float(area.latitude), float(area.longitude)
                elif city.latitude and city.longitude:
                    return float(city.latitude), float(city.longitude)
                else:
                    # Default coordinates for major Tamil Nadu cities if missing
                    city_defaults = {
                        'coimbatore': (11.0168, 76.9558),
                        'chennai': (13.0827, 80.2707),
                        'madurai': (9.9252, 78.1198),
                        'salem': (11.6643, 78.1460),
                        'trichy': (10.7905, 78.7047),
                        'ooty': (11.4064, 76.6932),
                        'kodaikanal': (10.2381, 77.4892),
                        'munnar': (10.0889, 77.0595),
                        'yercaud': (11.7753, 78.2186),
                        'rameshwaram': (9.2876, 79.3129),
                        'kanyakumari': (8.0883, 77.5385),
                        'tanjore': (10.7870, 79.1378),
                        'mysore': (12.2958, 76.6394),
                        'ariyalur': (11.1401, 79.0747)
                    }
                    city_name_lower = city.name.lower()
                    return city_defaults.get(city_name_lower, (11.0168, 76.9558))  # Default to Coimbatore
            
            # Get coordinates with fallbacks
            from_lat, from_lon = get_fallback_coordinates(from_city, from_area if from_area_id else None)
            to_lat, to_lon = get_fallback_coordinates(to_city, to_area if to_area_id else None)
            
            # Calculate distance (now always possible with fallbacks)
            distance = haversine_distance(from_lat, from_lon, to_lat, to_lon)
            
            # Round to 2 decimal places
            distance = round(distance, 2)
            
            # Determine source based on whether we used fallbacks
            used_fallback = False
            if from_area_id and (not from_area.latitude or not from_area.longitude):
                used_fallback = True
            if not from_city.latitude or not from_city.longitude:
                used_fallback = True
            if to_area_id and (not to_area.latitude or not to_area.longitude):
                used_fallback = True
            if not to_city.latitude or not to_city.longitude:
                used_fallback = True
            
            source = 'estimated' if used_fallback else 'calculated'
            
            return Response({
                'distance': distance,
                'one_way_fixed_rate': None,
                'source': source,
                'message': f'Distance {source}: {distance} km'
            })
                
        except (City.DoesNotExist, LocalArea.DoesNotExist) as e:
            return Response({
                'distance': None,
                'one_way_fixed_rate': None,
                'source': 'error',
                'message': 'Location not found.'
            })
    
    return Response({
        'error': 'Missing parameters',
        'received_params': {
            'from_city_id': from_city_id,
            'to_city_id': to_city_id,
            'from_area_id': from_area_id,
            'to_area_id': to_area_id
        }
    }, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def calculate_booking_amount(request):
    try:
        data = request.data
        vehicle_id = data.get('vehicle_id')
        trip_type = data.get('trip_type')
        total_distance = float(data.get('total_distance', 0))
        total_days = int(data.get('total_days', 1))
        
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        if trip_type == 'round':
            # Round Trip: Day-based calculation
            # Total Vehicle Fee = Number of Days × Vehicle Fee
            # Total Driver Fee = Number of Days × Driver Fee
            # Total Amount = Total Vehicle Fee + Total Driver Fee
            vehicle_fee = vehicle.per_day_fee * total_days
            driver_charge = vehicle.driver_charge_per_day * total_days
            total_amount = vehicle_fee + driver_charge
            fare_amount = vehicle_fee
            
        elif trip_type in ['outstation', 'multicity', 'tour']:
            if trip_type == 'multicity':
                # Multicity: Day-based + Extra KM charges
                # Total Vehicle Fee = Number of Days × Vehicle Fee
                # Total Driver Fee = Number of Days × Driver Fee
                # Chargeable Kilometers = Total Kilometers − (Number of Days × Vehicle Free KMs per Day)
                # Extra Kilometer Charge = Chargeable Kilometers × Fare per KM
                # Total Amount = Total Vehicle Fee + Total Driver Fee + Extra Kilometer Charge
                vehicle_fee = vehicle.per_day_fee * total_days
                driver_charge = vehicle.driver_charge_per_day * total_days
                free_km_total = total_days * vehicle.min_km_per_day
                chargeable_km = max(0, total_distance - free_km_total)
                extra_km_charge = chargeable_km * vehicle.fare_per_km
                total_amount = vehicle_fee + driver_charge + extra_km_charge
                fare_amount = vehicle_fee + extra_km_charge
            else:
                # Day basis calculation with distance for other trip types
                min_km_per_day = vehicle.min_km_per_day
                actual_km_per_day = max(total_distance / total_days, min_km_per_day)
                
                total_km = actual_km_per_day * total_days
                fare_amount = total_km * vehicle.fare_per_km
                driver_charge = vehicle.driver_charge_per_day * total_days
                vehicle_day_charge = vehicle.per_day_fee * total_days
                total_amount = fare_amount + driver_charge + vehicle_day_charge
            
        elif trip_type == 'local':
            # Hour basis - this would depend on tariff
            hours = int(data.get('hours', 8))
            # Use tariff if available, otherwise default calculation
            total_amount = hours * 500  # Default hourly rate
            fare_amount = 0
            driver_charge = 0
            
        elif trip_type == 'oneway':
            # KM basis for one way
            total_amount = total_distance * vehicle.fare_per_km
            fare_amount = total_amount
            driver_charge = 0
        
        return Response({
            'total_amount': round(total_amount, 2),
            'fare_amount': round(fare_amount if 'fare_amount' in locals() else 0, 2),
            'driver_charge': round(driver_charge if 'driver_charge' in locals() else 0, 2),
            'total_distance': total_distance,
            'total_days': total_days
        })
    except Exception as e:
        return Response({'error': str(e)}, status=400)


# Destination Views
class OotyView(TemplateView):
    template_name = 'tours/ooty.html'


class KodaikanalView(TemplateView):
    template_name = 'tours/kodaikanal.html'


class MunnarView(TemplateView):
    template_name = 'tours/munnar.html'


class CoorgView(TemplateView):
    template_name = 'tours/coorg.html'


class MysoreView(TemplateView):
    template_name = 'tours/mysore.html'


class YercaudView(TemplateView):
    template_name = 'tours/yercaud.html'


class WayanadView(TemplateView):
    template_name = 'tours/wayanad.html'


class AboutUsView(TemplateView):
    template_name = 'about_us.html'

