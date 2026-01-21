import random
import string
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Booking, Payment, BookingRoute
from django.db.models import Sum
from vehicles.models import Vehicle
from tours.models import City
from .utils import send_booking_confirmation_email, send_booking_whatsapp, send_admin_notification
import razorpay
from django.conf import settings
import json


def generate_booking_number():
    return ''.join(random.choices(string.digits, k=8))


class BookingPageView(TemplateView):
    template_name = 'bookings/booking.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from vehicles.models import Vehicle
        from django.conf import settings
        context['vehicles'] = Vehicle.objects.filter(is_available=True)
        context['RAZORPAY_KEY_ID'] = settings.RAZORPAY_KEY_ID
        return context


class BookingStatusView(TemplateView):
    template_name = 'bookings/booking_status.html'


@api_view(['GET'])
@permission_classes([AllowAny])
def get_booking_summary(request):
    """Get dynamic booking summary data based on URL parameters"""
    try:
        # Get parameters from request
        trip_type = request.GET.get('trip_type')
        pickup_city_id = request.GET.get('pickup_city')
        pickup_date = request.GET.get('pickup_date')
        drop_date = request.GET.get('drop_date')
        vehicle_id = request.GET.get('vehicle_id')
        amount = request.GET.get('amount')
        trip_basis = request.GET.get('trip_basis', 'day')
        
        # Get sightseeing data
        selected_sightseeing = request.GET.getlist('sightseeing[]')
        sightseeing_cities = request.GET.getlist('sightseeing_cities[]')
        sightseeing_details = request.GET.get('sightseeing_details')  # JSON string
        
        response_data = {
            'trip_type': trip_type,
            'pickup_date': pickup_date,
            'drop_date': drop_date,
            'amount': amount,
            'trip_basis': trip_basis,
            'routes': [],
            'sightseeing': [],
            'vehicle_details': {},
            'calculation_details': {}
        }
        
        # Get pickup city details
        if pickup_city_id:
            try:
                from tours.models import City
                pickup_city = City.objects.get(id=pickup_city_id)
                response_data['pickup_city'] = {
                    'id': pickup_city.id,
                    'name': pickup_city.name,
                    'tourist_places': pickup_city.get_tourist_places_list(),
                    'sightseeing_km': float(pickup_city.sightseeing_kilometers)
                }
            except City.DoesNotExist:
                response_data['pickup_city'] = None
        
        # Get vehicle details
        if vehicle_id:
            try:
                vehicle = Vehicle.objects.get(id=vehicle_id)
                response_data['vehicle_details'] = {
                    'id': vehicle.id,
                    'name': vehicle.display_name,
                    'max_seats': vehicle.max_seats,
                    'fare_per_km': float(vehicle.fare_per_km),
                    'driver_charge_per_day': float(vehicle.driver_charge_per_day),
                    'per_day_fee': float(vehicle.per_day_fee),
                    'min_km_per_day': vehicle.min_km_per_day,
                    'fare_per_hour': float(vehicle.fare_per_hour),
                    'min_hours_local': vehicle.min_hours_local
                }
            except Vehicle.DoesNotExist:
                response_data['vehicle_details'] = {}
        
        # Calculate trip details based on trip type
        if trip_type == 'multicity':
            # Handle multicity trips
            multicity_dates = request.GET.getlist('multicity_date[]')
            multicity_from = request.GET.getlist('multicity_from[]')
            multicity_to = request.GET.getlist('multicity_to[]')
            multicity_distances = request.GET.getlist('multicity_distance[]')
            
            if multicity_dates and multicity_from and multicity_to:
                # Calculate actual number of unique days
                unique_dates = list(set(multicity_dates))
                total_days = len(unique_dates)
                total_distance = sum(float(d) for d in multicity_distances if d)
                
                response_data['total_days'] = total_days
                response_data['total_distance'] = total_distance
                
                # Create routes for multicity
                routes = []
                date_to_day_map = {}
                day_counter = 1
                
                # Create a mapping of dates to day numbers
                for date in sorted(set(multicity_dates)):
                    date_to_day_map[date] = day_counter
                    day_counter += 1
                
                for i in range(len(multicity_from)):
                    if i < len(multicity_to) and i < len(multicity_dates):
                        # Get city/area names
                        from_name = get_location_name(multicity_from[i])
                        to_name = get_location_name(multicity_to[i])
                        distance = float(multicity_distances[i]) if i < len(multicity_distances) else 0
                        
                        # Use the mapped day number based on date
                        day_number = date_to_day_map[multicity_dates[i]]
                        
                        routes.append({
                            'day': day_number,
                            'route_sequence': i + 1,  # Add sequence for same-day routes
                            'from_name': from_name,
                            'to_name': to_name,
                            'distance': distance,
                            'date': multicity_dates[i],
                            'from_id': multicity_from[i],
                            'to_id': multicity_to[i],
                            'to_city_id': get_city_id_from_location(multicity_to[i])  # For hill station calculation
                        })
                
                response_data['routes'] = routes
                
                # Add sightseeing based on selected options
                if sightseeing_details:
                    try:
                        import json
                        sightseeing_data = json.loads(sightseeing_details)
                        response_data['sightseeing'] = sightseeing_data
                    except:
                        response_data['sightseeing'] = []
                else:
                    response_data['sightseeing'] = []
                
                # Calculate multicity pricing
                if amount and vehicle_id:
                    total_amount = float(amount)
                    vehicle = Vehicle.objects.get(id=vehicle_id)
                    
                    per_day_rent = float(vehicle.per_day_fee)
                    driver_per_day = float(vehicle.driver_charge_per_day)
                    free_km_per_day = vehicle.min_km_per_day
                    fare_per_km = float(vehicle.fare_per_km)
                    
                    total_rent = per_day_rent * total_days
                    total_driver = driver_per_day * total_days
                    total_free_km = free_km_per_day * total_days
                    
                    # Calculate hill station charges
                    hill_charges = 0
                    hill_stations_visited = set()
                    
                    # Get routes from multicity data to identify hill stations
                    if 'routes' in response_data:
                        for route in response_data['routes']:
                            # Check if destination city is a hill station
                            try:
                                to_city_id = route.get('to_city_id')
                                if to_city_id:
                                    city = City.objects.get(id=to_city_id)
                                    if city.is_hill_station and city.name not in hill_stations_visited:
                                        hill_charges += float(city.hill_station_charge)
                                        hill_stations_visited.add(city.name)
                            except City.DoesNotExist:
                                pass
                    
                    # Calculate extra km
                    extra_km = max(0, total_distance - total_free_km)
                    extra_km_cost = extra_km * fare_per_km
                    
                    # Estimate permit charges
                    base_cost = total_rent + total_driver + extra_km_cost + hill_charges
                    permit_charges = max(0, total_amount - base_cost)
                    
                    # Calculate GST only if enabled in system settings
                    from accounts.models import SystemSettings
                    system_settings = SystemSettings.get_settings()
                    
                    if system_settings.gst_enabled:
                        from .models import GSTRate
                        gst_rate = GSTRate.get_current_gst_rate('transport')
                        
                        # Calculate base amount (without GST) and GST amount
                        subtotal = total_rent + total_driver + extra_km_cost + hill_charges + permit_charges
                        gst_amount = (subtotal * gst_rate) / 100
                        total_with_gst = subtotal + gst_amount
                    else:
                        # GST is disabled
                        gst_rate = 0
                        subtotal = total_rent + total_driver + extra_km_cost + hill_charges + permit_charges
                        gst_amount = 0
                        total_with_gst = subtotal
                    
                    response_data['calculation_details'] = {
                        'total_days': total_days,
                        'per_day_rent': per_day_rent,
                        'driver_per_day': driver_per_day,
                        'free_km_per_day': free_km_per_day,
                        'total_free_km': total_free_km,
                        'total_rent': total_rent,
                        'total_driver': total_driver,
                        'extra_km': int(extra_km),
                        'extra_km_cost': extra_km_cost,
                        'fare_per_km': fare_per_km,
                        'total_distance': total_distance,
                        'hill_charges': hill_charges,
                        'hill_stations_visited': list(hill_stations_visited),
                        'permit_charges': permit_charges,
                        'subtotal': subtotal,
                        'gst_rate': gst_rate,
                        'gst_amount': gst_amount,
                        'total_amount': total_with_gst,
                        'trip_basis': 'multicity'
                    }
        
        elif trip_type == 'local':
            # Handle local trips
            local_area = request.GET.get('local_area')
            pickup_time = request.GET.get('pickup_time')
            pickup_time_period = request.GET.get('pickup_time_period')
            
            response_data['total_days'] = 1
            response_data['local_area'] = local_area
            response_data['pickup_time'] = pickup_time
            response_data['pickup_time_period'] = pickup_time_period
            
            # Create route for local trip
            if pickup_city_id:
                pickup_city = City.objects.get(id=pickup_city_id)
                local_area_name = get_local_area_name(local_area) if local_area else 'Local Area'
                
                response_data['routes'] = [
                    {
                        'day': 1,
                        'from_name': pickup_city.name,
                        'to_name': f'{pickup_city.name} - {local_area_name}',
                        'distance': float(pickup_city.sightseeing_kilometers) if pickup_city.sightseeing_kilometers else 30,
                        'date': pickup_date
                    }
                ]
                
                # Add sightseeing for local trips
                if sightseeing_details:
                    try:
                        import json
                        sightseeing_data = json.loads(sightseeing_details)
                        response_data['sightseeing'] = sightseeing_data
                    except:
                        # Fallback to default city sightseeing
                        if pickup_city.tourist_places:
                            response_data['sightseeing'] = [
                                {
                                    'location': f"{pickup_city.name} Local Sight Seeing",
                                    'distance': f"{pickup_city.sightseeing_kilometers} Kms",
                                    'details': pickup_city.tourist_places
                                }
                            ]
                elif pickup_city.tourist_places:
                    response_data['sightseeing'] = [
                        {
                            'location': f"{pickup_city.name} Local Sight Seeing",
                            'distance': f"{pickup_city.sightseeing_kilometers} Kms",
                            'details': pickup_city.tourist_places
                        }
                    ]
            
            # Calculate local trip pricing
            if amount and vehicle_id:
                total_amount = float(amount)
                vehicle = Vehicle.objects.get(id=vehicle_id)
                
                fare_per_hour = float(vehicle.fare_per_hour)
                min_hours = vehicle.min_hours_local
                min_hours_fee = float(vehicle.min_hours_fee_local)
                max_distance_min_hours = vehicle.max_distance_min_hours
                fare_per_km_local = float(vehicle.fare_per_km_local)
                
                # Calculate based on amount
                if total_amount <= min_hours_fee:
                    estimated_hours = min_hours
                    hour_cost = min_hours_fee
                    extra_km_cost = 0
                    extra_km = 0
                else:
                    # Check if it's extra hours or extra km
                    extra_amount = total_amount - min_hours_fee
                    
                    # Try to calculate as extra hours first
                    extra_hours = extra_amount / fare_per_hour if fare_per_hour > 0 else 0
                    
                    # Or as extra km
                    extra_km = extra_amount / fare_per_km_local if fare_per_km_local > 0 else 0
                    
                    # Use the more reasonable calculation
                    if extra_hours <= 8:  # If less than 8 extra hours, assume it's hour-based
                        estimated_hours = min_hours + extra_hours
                        hour_cost = total_amount
                        extra_km_cost = 0
                        extra_km = 0
                    else:  # Otherwise, assume it's km-based
                        estimated_hours = min_hours
                        hour_cost = min_hours_fee
                        extra_km_cost = extra_amount
                        extra_km = extra_km
                
                # Calculate GST only if enabled in system settings
                from accounts.models import SystemSettings
                system_settings = SystemSettings.get_settings()
                
                if system_settings.gst_enabled:
                    from .models import GSTRate
                    gst_rate = GSTRate.get_current_gst_rate('transport')
                    
                    # Calculate base amount (without GST) and GST amount
                    subtotal = hour_cost + extra_km_cost
                    gst_amount = (subtotal * gst_rate) / 100
                    total_with_gst = subtotal + gst_amount
                else:
                    # GST is disabled
                    gst_rate = 0
                    subtotal = hour_cost + extra_km_cost
                    gst_amount = 0
                    total_with_gst = subtotal
                
                response_data['calculation_details'] = {
                    'total_hours': int(estimated_hours),
                    'min_hours': min_hours,
                    'min_hours_fee': min_hours_fee,
                    'hour_cost': hour_cost,
                    'max_distance_min_hours': max_distance_min_hours,
                    'extra_km': int(extra_km),
                    'extra_km_cost': extra_km_cost,
                    'fare_per_km_local': fare_per_km_local,
                    'fare_per_hour': fare_per_hour,
                    'subtotal': subtotal,
                    'gst_rate': gst_rate,
                    'gst_amount': gst_amount,
                    'total_amount': total_with_gst,
                    'trip_basis': 'local'
                }
        
        elif trip_type == 'round' and pickup_date and drop_date:
            from datetime import datetime
            try:
                pickup_dt = datetime.strptime(pickup_date, '%Y-%m-%d')
                drop_dt = datetime.strptime(drop_date, '%Y-%m-%d')
                total_days = (drop_dt - pickup_dt).days + 1
                
                response_data['total_days'] = total_days
                
                # For round trip, create a simple route structure
                if pickup_city_id:
                    pickup_city = City.objects.get(id=pickup_city_id)
                    response_data['routes'] = [
                        {
                            'day': 1,
                            'from_name': pickup_city.name,
                            'to_name': 'Destination (Round Trip)',
                            'distance': 0,  # Will be calculated based on total amount
                            'date': pickup_date
                        }
                    ]
                    
                    # Add sightseeing for pickup city
                    if sightseeing_details:
                        try:
                            import json
                            sightseeing_data = json.loads(sightseeing_details)
                            response_data['sightseeing'] = sightseeing_data
                        except:
                            # Fallback to default city sightseeing
                            if pickup_city.tourist_places:
                                response_data['sightseeing'] = [
                                    {
                                        'location': f"{pickup_city.name} Local Sight Seeing",
                                        'distance': f"{pickup_city.sightseeing_kilometers} Kms",
                                        'details': pickup_city.tourist_places
                                    }
                                ]
                    elif pickup_city.tourist_places:
                        response_data['sightseeing'] = [
                            {
                                'location': f"{pickup_city.name} Local Sight Seeing",
                                'distance': f"{pickup_city.sightseeing_kilometers} Kms",
                                'details': pickup_city.tourist_places
                            }
                        ]
                
                # Calculate breakdown if amount is provided
                if amount and vehicle_id:
                    total_amount = float(amount)
                    vehicle = Vehicle.objects.get(id=vehicle_id)
                    
                    if trip_basis == 'day':
                        # Day basis calculation
                        per_day_rent = float(vehicle.per_day_fee)
                        driver_per_day = float(vehicle.driver_charge_per_day)
                        free_km_per_day = vehicle.min_km_per_day
                        fare_per_km = float(vehicle.fare_per_km)
                        
                        total_rent = per_day_rent * total_days
                        total_driver = driver_per_day * total_days
                        total_free_km = free_km_per_day * total_days
                        
                        # Estimate extra km based on remaining amount
                        base_cost = total_rent + total_driver
                        remaining_amount = total_amount - base_cost
                        extra_km = max(0, remaining_amount / fare_per_km) if fare_per_km > 0 else 0
                        extra_km_cost = extra_km * fare_per_km
                        
                        # Calculate GST only if enabled in system settings
                        from accounts.models import SystemSettings
                        system_settings = SystemSettings.get_settings()
                        
                        if system_settings.gst_enabled:
                            from .models import GSTRate
                            gst_rate = GSTRate.get_current_gst_rate('transport')
                            
                            # Calculate base amount (without GST) and GST amount
                            permit_charges = max(0, total_amount - total_rent - total_driver - extra_km_cost)
                            subtotal = total_rent + total_driver + extra_km_cost + permit_charges
                            gst_amount = (subtotal * gst_rate) / 100
                            total_with_gst = subtotal + gst_amount
                        else:
                            # GST is disabled
                            gst_rate = 0
                            permit_charges = max(0, total_amount - total_rent - total_driver - extra_km_cost)
                            subtotal = total_rent + total_driver + extra_km_cost + permit_charges
                            gst_amount = 0
                            total_with_gst = subtotal
                        
                        response_data['calculation_details'] = {
                            'total_days': total_days,
                            'per_day_rent': per_day_rent,
                            'driver_per_day': driver_per_day,
                            'free_km_per_day': free_km_per_day,
                            'total_free_km': total_free_km,
                            'total_rent': total_rent,
                            'total_driver': total_driver,
                            'extra_km': int(extra_km),
                            'extra_km_cost': extra_km_cost,
                            'fare_per_km': fare_per_km,
                            'total_distance': total_free_km + extra_km,
                            'hill_charges': 0,  # Can be calculated based on destinations
                            'permit_charges': permit_charges,
                            'subtotal': subtotal,
                            'gst_rate': gst_rate,
                            'gst_amount': gst_amount,
                            'total_amount': total_with_gst
                        }
                    else:
                        # Hour basis calculation
                        fare_per_hour = float(vehicle.fare_per_hour)
                        min_hours = vehicle.min_hours_local
                        driver_per_day = float(vehicle.driver_charge_per_day)
                        
                        # Estimate hours based on amount
                        estimated_hours = max(min_hours, total_amount / fare_per_hour) if fare_per_hour > 0 else min_hours
                        hour_cost = estimated_hours * fare_per_hour
                        
                        # Calculate GST only if enabled in system settings
                        from accounts.models import SystemSettings
                        system_settings = SystemSettings.get_settings()
                        
                        if system_settings.gst_enabled:
                            from .models import GSTRate
                            gst_rate = GSTRate.get_current_gst_rate('transport')
                            
                            # Calculate base amount (without GST) and GST amount
                            subtotal = hour_cost + driver_per_day
                            gst_amount = (subtotal * gst_rate) / 100
                        else:
                            # GST is disabled
                            gst_rate = 0
                            subtotal = hour_cost + driver_per_day
                            gst_amount = 0
                        total_with_gst = subtotal + gst_amount
                        
                        response_data['calculation_details'] = {
                            'total_hours': int(estimated_hours),
                            'min_hours': min_hours,
                            'fare_per_hour': fare_per_hour,
                            'hour_cost': hour_cost,
                            'driver_charges': driver_per_day,
                            'subtotal': subtotal,
                            'gst_rate': gst_rate,
                            'gst_amount': gst_amount,
                            'total_amount': total_with_gst,
                            'trip_basis': 'hour'
                        }
            except (ValueError, City.DoesNotExist, Vehicle.DoesNotExist) as e:
                print(f"Error calculating trip details: {e}")
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching booking summary: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def get_location_name(location_id):
    """Helper function to get location name from city or area ID"""
    try:
        from tours.models import City, LocalArea
        
        if location_id.startswith('city_'):
            city_id = location_id.replace('city_', '')
            city = City.objects.get(id=city_id)
            return city.name
        elif location_id.startswith('area_'):
            area_id = location_id.replace('area_', '')
            area = LocalArea.objects.get(id=area_id)
            return f"{area.city.name} - {area.name}"
        else:
            # Try as direct city ID
            try:
                city = City.objects.get(id=location_id)
                return city.name
            except:
                return location_id
    except:
        return location_id


def get_city_id_from_location(location_id):
    """Helper function to get city ID from city or area ID"""
    try:
        from tours.models import City, LocalArea
        
        if location_id.startswith('city_'):
            city_id = location_id.replace('city_', '')
            return int(city_id)
        elif location_id.startswith('area_'):
            area_id = location_id.replace('area_', '')
            area = LocalArea.objects.get(id=area_id)
            return area.city.id
        else:
            # Try as direct city ID
            try:
                return int(location_id)
            except:
                return None
    except:
        return None


def get_local_area_name(area_id):
    """Helper function to get local area name"""
    try:
        from tours.models import LocalArea
        area = LocalArea.objects.get(id=area_id)
        return area.name
    except:
        return f"Area {area_id}"


@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request):
    try:
        data = request.data
        booking_number = generate_booking_number()
        
        # Ensure booking number is unique
        while Booking.objects.filter(booking_number=booking_number).exists():
            booking_number = generate_booking_number()
        
        vehicle_id = data.get('vehicle_id')
        vehicle = None
        if vehicle_id:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        
        booking = Booking.objects.create(
            booking_number=booking_number,
            user=request.user if request.user.is_authenticated else None,
            vehicle=vehicle,
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            flight_train_no=data.get('flight_train_no', ''),
            landmark=data.get('landmark', ''),
            adults=int(data.get('adults', 1)),
            children=int(data.get('children', 0)),
            pickup_address=data.get('pickup_address'),
            drop_address=data.get('drop_address'),
            pickup_city=data.get('pickup_city'),
            pickup_date=data.get('pickup_date'),
            pickup_time=data.get('pickup_time'),
            drop_date=data.get('drop_date'),
            drop_time=data.get('drop_time'),
            trip_type=data.get('trip_type'),
            total_days=int(data.get('total_days', 1)),
            total_distance=float(data.get('total_distance', 0)),
            multicity_routes=data.get('multicity_routes', []),
            payment_type=data.get('payment_type'),
            total_amount=float(data.get('total_amount', 0)),
            advance_amount=float(data.get('advance_amount', 0)),
            special_instructions=data.get('special_instructions', ''),
        )
        
        # Create routes for multi-city
        routes = data.get('routes', [])
        for idx, route in enumerate(routes):
            BookingRoute.objects.create(
                booking=booking,
                from_location=route.get('from'),
                to_location=route.get('to'),
                distance=float(route.get('distance', 0)),
                date=route.get('date'),
                order=idx
            )
        
        # Send notifications
        send_booking_confirmation_email(booking)
        send_booking_whatsapp(booking)
        send_admin_notification(booking)
        
        return Response({
            'booking_number': booking.booking_number,
            'message': 'Booking created successfully'
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_booking_status(request, booking_number):
    try:
        booking = Booking.objects.get(booking_number=booking_number)
        payments = Payment.objects.filter(booking=booking)
        
        return Response({
            'booking': {
                'booking_number': booking.booking_number,
                'name': booking.name,
                'email': booking.email,
                'phone': str(booking.phone),
                'trip_type': booking.trip_type,
                'status': booking.status,
                'pickup_address': booking.pickup_address,
                'drop_address': booking.drop_address,
                'pickup_date': booking.pickup_date,
                'pickup_time': booking.pickup_time,
                'total_amount': float(booking.total_amount),
                'vehicle': booking.vehicle.name if booking.vehicle else None,
            },
            'payments': [
                {
                    'amount': float(p.amount),
                    'status': p.status,
                    'created_at': p.created_at
                } for p in payments
            ]
        })
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_razorpay_order(request):
    try:
        amount = float(request.data.get('amount', 0))
        booking_number = request.data.get('booking_number')
        
        if not booking_number:
            return Response({'error': 'Booking number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if amount <= 0:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if Razorpay is configured
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            return Response({'error': 'Razorpay is not configured'}, status=status.HTTP_400_BAD_REQUEST)
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order_data = {
            'amount': int(amount * 100),  # Convert to paise
            'currency': 'INR',
            'receipt': booking_number,
        }
        order = client.order.create(data=order_data)
        
        return Response({
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency']
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_http_methods(["POST"])
def razorpay_callback(request):
    try:
        data = json.loads(request.body)
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')
        booking_number = data.get('booking_number')
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Verify signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        try:
            client.utility.verify_payment_signature(params_dict)
            booking = Booking.objects.get(booking_number=booking_number)
            
            payment = Payment.objects.create(
                booking=booking,
                razorpay_order_id=order_id,
                razorpay_payment_id=payment_id,
                razorpay_signature=signature,
                amount=booking.advance_amount or booking.total_amount,
                status='completed'
            )
            
            booking.status = 'confirmed'
            booking.save()
            
            return JsonResponse({'status': 'success', 'message': 'Payment successful'})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def booking_confirmation(request, booking_number):
    booking = get_object_or_404(Booking, booking_number=booking_number)
    payments = Payment.objects.filter(booking=booking)
    return render(request, 'bookings/booking_confirmation.html', {
        'booking': booking,
        'payments': payments
    })


class PaymentPageView(TemplateView):
    template_name = 'bookings/payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['RAZORPAY_KEY_ID'] = settings.RAZORPAY_KEY_ID
        return context


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_booking_for_payment(request):
    """Validate booking number and return outstanding amount"""
    try:
        booking_number = request.data.get('booking_number')
        if not booking_number:
            return Response({'error': 'Booking number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            booking = Booking.objects.get(booking_number=booking_number)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate total paid amount
        total_paid = Payment.objects.filter(
            booking=booking,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        outstanding_amount = float(booking.total_amount) - float(total_paid)
        
        return Response({
            'exists': True,
            'booking_number': booking.booking_number,
            'name': booking.name,
            'email': booking.email,
            'phone': str(booking.phone),
            'total_amount': float(booking.total_amount),
            'total_paid': float(total_paid),
            'outstanding_amount': outstanding_amount,
            'status': booking.status
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def process_payment(request):
    """Process payment with Razorpay"""
    try:
        data = request.data
        booking_number = data.get('booking_number')
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        amount = float(data.get('amount', 0))
        captcha = data.get('captcha')
        captcha_code = data.get('captcha_code')
        
        # Validate captcha
        if captcha != captcha_code:
            return Response({'error': 'Invalid captcha code'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate booking
        try:
            booking = Booking.objects.get(booking_number=booking_number)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate outstanding amount
        total_paid = Payment.objects.filter(
            booking=booking,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        outstanding_amount = float(booking.total_amount) - float(total_paid)
        
        # Validate amount
        if amount <= 0:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        if amount > outstanding_amount:
            return Response({
                'error': f'Amount cannot exceed outstanding amount of ₹{outstanding_amount:.2f}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create Razorpay order
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            return Response({'error': 'Razorpay is not configured'}, status=status.HTTP_400_BAD_REQUEST)
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order_data = {
            'amount': int(amount * 100),  # Convert to paise
            'currency': 'INR',
            'receipt': f"{booking_number}_{random.randint(1000, 9999)}",
            'notes': {
                'booking_number': booking_number,
                'name': name,
                'email': email,
                'phone': phone
            }
        }
        order = client.order.create(data=order_data)
        
        # Create pending payment record
        payment = Payment.objects.create(
            booking=booking,
            razorpay_order_id=order['id'],
            amount=amount,
            status='pending'
        )
        
        return Response({
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'key': settings.RAZORPAY_KEY_ID,
            'payment_id': payment.id,
            'booking_number': booking_number
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_http_methods(["POST"])
def payment_success(request):
    """Handle successful payment"""
    try:
        data = json.loads(request.body) if request.body else request.POST
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')
        payment_record_id = data.get('payment_id')
        
        if not all([payment_id, order_id, signature, payment_record_id]):
            return JsonResponse({'status': 'error', 'message': 'Missing payment details'}, status=400)
        
        # Get payment record
        try:
            payment = Payment.objects.get(id=payment_record_id, razorpay_order_id=order_id)
        except Payment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Payment record not found'}, status=404)
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Verify signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        try:
            client.utility.verify_payment_signature(params_dict)
            
            # Update payment record
            payment.razorpay_payment_id = payment_id
            payment.razorpay_signature = signature
            payment.status = 'completed'
            payment.save()
            
            # Update booking status
            booking = payment.booking
            total_paid = Payment.objects.filter(
                booking=booking,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            if float(total_paid) >= float(booking.total_amount):
                booking.status = 'confirmed'
            else:
                booking.status = 'confirmed'  # Still confirmed for partial payment
            booking.save()
            
            # Send notifications
            from .utils import send_payment_confirmation_email, send_payment_whatsapp
            send_payment_confirmation_email(payment)
            send_payment_whatsapp(payment)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Payment successful',
                'payment_id': payment_id,
                'booking_number': booking.booking_number,
                'amount': float(payment.amount)
            })
        except razorpay.errors.SignatureVerificationError:
            payment.status = 'failed'
            payment.save()
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def payment_success_page(request):
    """Display payment success page"""
    payment_id = request.GET.get('payment_id')
    booking_number = request.GET.get('booking_number')
    
    context = {}
    if payment_id:
        try:
            payment = Payment.objects.get(razorpay_payment_id=payment_id, status='completed')
            context['payment'] = payment
            context['booking'] = payment.booking
        except Payment.DoesNotExist:
            pass
    
    if booking_number:
        try:
            booking = Booking.objects.get(booking_number=booking_number)
            context['booking'] = booking
            payments = Payment.objects.filter(booking=booking, status='completed').order_by('-created_at')
            context['payments'] = payments
            if payments.exists():
                context['payment'] = payments.first()
        except Booking.DoesNotExist:
            pass
    
    return render(request, 'bookings/payment_success.html', context)


class CancellationPageView(TemplateView):
    template_name = 'bookings/cancellation.html'


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_booking_for_cancellation(request):
    """Verify booking for cancellation"""
    try:
        booking_number = request.data.get('booking_number')
        mobile = request.data.get('mobile')
        email = request.data.get('email')
        
        if not all([booking_number, mobile, email]):
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            booking = Booking.objects.get(booking_number=booking_number)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verify mobile and email
        if str(booking.phone) != str(mobile) or booking.email.lower() != email.lower():
            return Response({'error': 'Mobile number or email does not match'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already cancelled
        if booking.status == 'cancelled':
            return Response({'error': 'Booking is already cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate payments
        payments = Payment.objects.filter(booking=booking, status='completed')
        total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate cancellation charges (10% of total amount)
        cancellation_charge_percent = 10
        cancellation_charges = float(booking.total_amount) * (cancellation_charge_percent / 100)
        refundable_amount = float(total_paid) - cancellation_charges
        final_refund = max(0, refundable_amount)  # Cannot be negative
        
        return Response({
            'exists': True,
            'booking': {
                'booking_number': booking.booking_number,
                'name': booking.name,
                'email': booking.email,
                'phone': str(booking.phone),
                'trip_type': booking.get_trip_type_display(),
                'pickup_address': booking.pickup_address,
                'drop_address': booking.drop_address,
                'pickup_date': booking.pickup_date,
                'pickup_time': booking.pickup_time,
                'total_amount': float(booking.total_amount),
                'status': booking.status,
                'vehicle': booking.vehicle.name if booking.vehicle else None,
            },
            'payments': [
                {
                    'id': p.id,
                    'amount': float(p.amount),
                    'status': p.status,
                    'razorpay_payment_id': p.razorpay_payment_id,
                    'created_at': p.created_at
                } for p in payments
            ],
            'total_paid': float(total_paid),
            'cancellation_charges': cancellation_charges,
            'refundable_amount': refundable_amount,
            'final_refund': final_refund
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_cancellation(request):
    """Confirm booking cancellation and process refund"""
    try:
        booking_number = request.data.get('booking_number')
        reason = request.data.get('reason', '')
        
        if not booking_number:
            return Response({'error': 'Booking number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            booking = Booking.objects.get(booking_number=booking_number)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if booking.status == 'cancelled':
            return Response({'error': 'Booking is already cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate refund
        payments = Payment.objects.filter(booking=booking, status='completed')
        total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
        cancellation_charges = float(booking.total_amount) * 0.10
        final_refund = max(0, float(total_paid) - cancellation_charges)
        
        # Update booking status
        booking.status = 'cancelled'
        booking.special_instructions = f"Cancellation Reason: {reason}\n\n{booking.special_instructions or ''}"
        booking.save()
        
        # Process refunds for online payments
        refunded_payments = []
        remaining_refund = final_refund
        
        for payment in payments:
            if payment.razorpay_payment_id and remaining_refund > 0:
                try:
                    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                    refund_amount = min(float(payment.amount), remaining_refund)
                    
                    if refund_amount > 0:
                        refund = client.payment.refund(payment.razorpay_payment_id, {
                            'amount': int(refund_amount * 100)  # Convert to paise
                        })
                        
                        payment.status = 'refunded'
                        payment.save()
                        refunded_payments.append({
                            'payment_id': payment.razorpay_payment_id,
                            'refund_id': refund.get('id'),
                            'amount': refund_amount
                        })
                        remaining_refund -= refund_amount
                except Exception as e:
                    # Log error but continue
                    print(f"Refund error for payment {payment.id}: {e}")
        
        # Update final_refund to reflect actual refunded amount
        final_refund = final_refund - remaining_refund
        
        # Send cancellation confirmation
        from .utils import send_cancellation_confirmation_email, send_cancellation_whatsapp
        send_cancellation_confirmation_email(booking, final_refund, refunded_payments)
        send_cancellation_whatsapp(booking, final_refund)
        
        return Response({
            'status': 'success',
            'message': 'Booking cancelled successfully',
            'booking_number': booking.booking_number,
            'refund_amount': final_refund,
            'refunded_payments': refunded_payments
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OnlineCabBookingView(TemplateView):
    template_name = 'bookings/online_cab_booking.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from vehicles.models import Vehicle
        from tours.models import City, TourPackage
        from enquiries.models import Testimonial, Promotion
        from django.conf import settings
        
        # Vehicles with all details
        context['vehicles'] = Vehicle.objects.filter(is_available=True, is_active=True).order_by('fare_per_km')
        context['cities'] = City.objects.filter(is_active=True)
        context['RAZORPAY_KEY_ID'] = settings.RAZORPAY_KEY_ID
        
        # Right sidebar widgets
        context['popular_plans'] = TourPackage.objects.filter(is_active=True)[:5]
        context['tour_packages'] = TourPackage.objects.filter(is_active=True)[:5]
        context['testimonials'] = Testimonial.objects.filter(is_approved=True, is_featured=True)[:5]
        context['promotions'] = Promotion.objects.filter(is_active=True)[:5]
        
        return context


@api_view(['POST'])
@permission_classes([AllowAny])
def create_online_booking(request):
    """Create booking from online cab booking form"""
    try:
        data = request.data
        booking_number = generate_booking_number()
        
        # Ensure booking number is unique
        while Booking.objects.filter(booking_number=booking_number).exists():
            booking_number = generate_booking_number()
        
        vehicle_id = data.get('vehicle_id')
        if not vehicle_id:
            return Response({'error': 'Please select a vehicle'}, status=status.HTTP_400_BAD_REQUEST)
        
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        # For online cab booking, we don't calculate amount upfront
        # The amount will be determined by the admin based on actual distance/time
        total_amount = 0.00  # No amount calculation for online cab booking
        
        payment_type = data.get('payment_type')
        advance_amount = 0  # No advance payment for online cab booking
        
        # Get pickup city name if ID is provided
        pickup_city_name = ""
        pickup_city_id = data.get('pickup_city')
        if pickup_city_id:
            try:
                from tours.models import City
                city = City.objects.get(id=pickup_city_id)
                pickup_city_name = city.name
            except City.DoesNotExist:
                pickup_city_name = ""
        
        booking = Booking.objects.create(
            booking_number=booking_number,
            user=request.user if request.user.is_authenticated else None,
            vehicle=vehicle,
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            flight_train_no=data.get('flight_train_no', ''),
            landmark=data.get('landmark', ''),
            adults=int(data.get('adults', 1)),
            children=int(data.get('children', 0)),
            pickup_address=data.get('pickup_address'),
            drop_address=data.get('drop_address'),
            pickup_city=pickup_city_name,  # Store city name instead of ID
            pickup_date=data.get('pickup_date'),
            pickup_time=data.get('pickup_time'),
            drop_date=data.get('drop_date'),
            drop_time=data.get('drop_time'),
            trip_type='online_cab',  # Online Cab Booking trip type
            total_days=1,
            total_distance=0,
            payment_type=payment_type,
            total_amount=total_amount,
            advance_amount=advance_amount,
            special_instructions=data.get('special_instructions', ''),
        )
        # For online cab booking, no online payment processing needed
        # Payment will be handled as per selected method (driver/office)
        
        # Send notifications
        send_booking_confirmation_email(booking)
        send_booking_whatsapp(booking)
        send_admin_notification(booking)
        
        return Response({
            'booking_number': booking_number,
            'payment_type': payment_type,
            'message': 'Online cab booking request submitted successfully. Our team will contact you shortly with fare details and confirmation.'
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



# WhatsApp Webhook and Booking Details Views

@csrf_exempt
@require_http_methods(["GET", "POST"])
def whatsapp_webhook(request):
    """
    WhatsApp Cloud API webhook endpoint
    Handles webhook verification (GET) and incoming events (POST)
    """
    from .services.whatsapp_service import whatsapp_service
    import logging
    
    logger = logging.getLogger(__name__)
    
    if request.method == 'GET':
        # Webhook verification
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        logger.info(f"WhatsApp webhook verification attempt: mode={mode}, token={token}")
        
        # Verify the webhook
        verified_challenge = whatsapp_service.verify_webhook(mode, token, challenge)
        
        if verified_challenge:
            logger.info("WhatsApp webhook verified successfully")
            return JsonResponse({'challenge': verified_challenge}, status=200)
        else:
            logger.warning("WhatsApp webhook verification failed")
            return JsonResponse({'error': 'Verification failed'}, status=403)
    
    elif request.method == 'POST':
        # Handle incoming webhook events
        try:
            webhook_data = json.loads(request.body)
            logger.info(f"Received WhatsApp webhook: {json.dumps(webhook_data, indent=2)}")
            
            # Process the webhook event
            result = whatsapp_service.process_webhook_event(webhook_data)
            
            if result['success']:
                return JsonResponse({'status': 'success'}, status=200)
            else:
                logger.error(f"Webhook processing failed: {result.get('error')}")
                return JsonResponse({'status': 'error', 'message': result.get('error')}, status=400)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook request")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def booking_details(request, booking_id):
    """
    Display booking details page
    This is the page customers access via the booking details link
    """
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        payments = Payment.objects.filter(booking=booking).order_by('-created_at')
        routes = BookingRoute.objects.filter(booking=booking).order_by('order')
        
        # Calculate payment summary
        total_paid = payments.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        remaining_amount = booking.total_amount - total_paid
        
        context = {
            'booking': booking,
            'payments': payments,
            'routes': routes,
            'total_paid': total_paid,
            'remaining_amount': remaining_amount,
            'payment_percentage': (total_paid / booking.total_amount * 100) if booking.total_amount > 0 else 0,
        }
        
        return render(request, 'bookings/booking_details.html', context)
        
    except Exception as e:
        return render(request, 'bookings/booking_not_found.html', {
            'error': str(e),
            'booking_id': booking_id
        })


# Manual notification trigger for testing
@api_view(['POST'])
@permission_classes([AllowAny])
def trigger_booking_notification(request):
    """
    Manually trigger booking notifications for testing
    """
    from .signals import send_booking_notification_manually
    
    try:
        booking_id = request.data.get('booking_id')
        force_send = request.data.get('force_send', False)
        
        if not booking_id:
            return Response({'error': 'booking_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        result = send_booking_notification_manually(booking_id, force_send)
        
        if result['success']:
            return Response({
                'message': 'Notifications sent successfully',
                'result': result
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result.get('error', 'Unknown error'),
                'result': result
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Service status endpoint for monitoring
@api_view(['GET'])
@permission_classes([AllowAny])
def notification_service_status(request):
    """
    Get status of notification services (WhatsApp and Email)
    """
    from .services.notification_service import notification_service
    
    try:
        status_info = notification_service.get_service_status()
        return Response(status_info, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)