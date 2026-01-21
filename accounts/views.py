from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from tours.models import City, LocalArea
from tours.models import TourPackage
from .models import User, PasswordResetOTP, OTPAttemptLog
from .services.otp_service import OTPService
from .serializers import (
    UserSerializer, CustomerSignupSerializer, TravelsSignupSerializer
)


class CustomerSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomerSignupSerializer


class TravelsSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = TravelsSignupSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def customer_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if email and password:
        # Authenticate using email instead of username
        user = authenticate(request, username=email, password=password)
        if user and user.user_type == 'customer':
            # Session-based login for template access
            auth_login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials or not a customer account'}, 
                       status=status.HTTP_401_UNAUTHORIZED)
    return Response({'error': 'Email and password required'}, 
                   status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def travels_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if email and password:
        # Authenticate using email instead of username
        user = authenticate(request, username=email, password=password)
        if user and user.user_type == 'travels':
            # Session-based login for template access
            auth_login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials or not a travels account'}, 
                       status=status.HTTP_401_UNAUTHORIZED)
    return Response({'error': 'Email and password required'}, 
                   status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def forgot_password_send_otp(request):
    """Send OTP to user's email for password reset"""
    email = request.data.get('email')
    user_type = request.data.get('user_type')  # 'customer' or 'travels'
    
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not user_type or user_type not in ['customer', 'travels']:
        return Response({'error': 'Valid user type is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        
        # Check if user type matches the login page
        if user.user_type != user_type:
            if user_type == 'customer':
                return Response({
                    'error': 'This email is registered as a travels admin account. Please use the travels login page.'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'error': 'This email is registered as a customer account. Please use the customer login page.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Use OTP service to send OTP
        success, message = OTPService.send_otp(user, user_type, request)
        
        if success:
            return Response({
                'message': message,
                'email': email,
                'user_type': user_type
            })
        else:
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except User.DoesNotExist:
        return Response({
            'error': f'No account found with this email address for {user_type} login. Please check your email or sign up for a new account.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def forgot_password_verify_otp(request):
    """Verify OTP and reset password"""
    email = request.data.get('email')
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')
    
    if not all([email, otp, new_password]):
        return Response({
            'error': 'Email, OTP, and new password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate password strength
    if len(new_password) < 8:
        return Response({
            'error': 'Password must be at least 8 characters long'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        
        # Use OTP service to verify OTP
        success, message = OTPService.verify_otp(user, otp, request)
        
        if success:
            # Reset password
            user.set_password(new_password)
            user.save()
            
            return Response({
                'message': 'Password reset successfully. You can now login with your new password.'
            })
        else:
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except User.DoesNotExist:
        return Response({
            'error': 'Invalid email address'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_otp_status(request):
    """Get OTP status for a user"""
    email = request.GET.get('email')
    
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        status_info = OTPService.get_otp_status(user)
        return Response(status_info)
        
    except User.DoesNotExist:
        return Response({
            'has_active_otp': False,
            'time_remaining': 0,
            'attempts_remaining': 0
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        # Also logout from session
        auth_logout(request)
        return Response({'message': 'Successfully logged out'})
    except Exception as e:
        # Even if token blacklist fails, logout from session
        auth_logout(request)
        return Response({'message': 'Successfully logged out'})


def logout_view(request):
    """Template-based logout view - handles both GET and POST"""
    if request.method == 'POST':
        # Clear session
        auth_logout(request)
        # Redirect to home with success message
        from django.contrib import messages
        messages.success(request, 'You have been logged out successfully.')
        return redirect('home')
    else:
        # For GET requests, redirect to home (prevents 401 error)
        return redirect('home')


# Template Views
class CustomerLoginView(TemplateView):
    template_name = 'accounts/customer_login.html'


class TravelsLoginView(TemplateView):
    template_name = 'accounts/travels_login.html'


class CustomerSignupPageView(TemplateView):
    template_name = 'accounts/customer_signup.html'


class TravelsSignupPageView(TemplateView):
    template_name = 'accounts/travels_signup.html'


@login_required
def customer_dashboard(request):
    if request.user.user_type != 'customer':
        return redirect('travels_dashboard')
    from bookings.models import Booking
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'accounts/customer_dashboard.html', {'bookings': bookings})


@login_required
def travels_dashboard(request):
    """Travel Admin Dashboard - Only accessible to travel admin users"""
    # Strict access control - only travel admin users
    if not request.user.is_authenticated:
        return redirect('travels_login')
    
    if request.user.user_type != 'travels':
        # Deny access to customers and other user types
        if request.user.user_type == 'customer':
            return redirect('customer_dashboard')
        # For any other user type, redirect to home
        return redirect('home')
    
    from bookings.models import Booking, Payment
    from vehicles.models import Vehicle
    from accounts.models import User
    from tours.models import City, LocalArea
    
    # Dashboard statistics
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    cancelled_bookings = Booking.objects.filter(status='cancelled').count()
    total_vehicles = Vehicle.objects.count()
    active_vehicles = Vehicle.objects.filter(is_active=True, is_available=True).count()
    total_customers = User.objects.filter(user_type='customer').count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    total_cities = City.objects.count()
    active_cities = City.objects.filter(is_active=True).count()
    total_local_areas = LocalArea.objects.count()
    
    # Recent bookings
    recent_bookings = Booking.objects.all().order_by('-created_at')[:10]
    
    # Pending bookings for quick action
    pending_bookings_list = Booking.objects.filter(status='pending').order_by('-created_at')[:5]
    
    context = {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_vehicles': total_vehicles,
        'active_vehicles': active_vehicles,
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'total_cities': total_cities,
        'active_cities': active_cities,
        'total_local_areas': total_local_areas,
        'recent_bookings': recent_bookings,
        'pending_bookings_list': pending_bookings_list,
    }
    return render(request, 'accounts/travels_dashboard.html', context)


@login_required
def travels_cities_list(request):
    """City Management - List all cities"""
    if not request.user.is_authenticated or request.user.user_type != 'travels':
        return redirect('travels_login')
    
    cities = City.objects.all().order_by('name')
    context = {
        'cities': cities,
    }
    return render(request, 'travels/cities_list.html', context)


@login_required
def travels_city_add(request):
    """Add new city"""
    if not request.user.is_authenticated or request.user.user_type != 'travels':
        return redirect('travels_login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        image = request.FILES.get('image')
        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()
        tourist_places = request.POST.get('tourist_places', '').strip()
        sightseeing_kilometers = request.POST.get('sightseeing_kilometers', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        if name:
            try:
                city_data = {
                    'name': name,
                    'description': description,
                    'image': image,
                    'tourist_places': tourist_places,
                    'is_active': is_active
                }
                
                # Add coordinates if provided
                if latitude and longitude:
                    try:
                        city_data['latitude'] = float(latitude)
                        city_data['longitude'] = float(longitude)
                    except ValueError:
                        messages.error(request, 'Invalid latitude or longitude format!')
                        return render(request, 'travels/city_add.html')
                
                # Add sightseeing kilometers if provided
                if sightseeing_kilometers:
                    try:
                        city_data['sightseeing_kilometers'] = float(sightseeing_kilometers)
                    except ValueError:
                        messages.error(request, 'Invalid sightseeing kilometers format!')
                        return render(request, 'travels/city_add.html')
                else:
                    city_data['sightseeing_kilometers'] = 0
                
                # Add hill station fields
                is_hill_station = request.POST.get('is_hill_station') == 'on'
                city_data['is_hill_station'] = is_hill_station
                
                if is_hill_station:
                    hill_station_charge = request.POST.get('hill_station_charge', '').strip()
                    if hill_station_charge:
                        try:
                            city_data['hill_station_charge'] = float(hill_station_charge)
                        except ValueError:
                            messages.error(request, 'Invalid hill station charge format!')
                            return render(request, 'travels/city_add.html')
                    else:
                        city_data['hill_station_charge'] = 750.0  # Default charge
                else:
                    city_data['hill_station_charge'] = 750.0  # Default charge even for non-hill stations
                
                city = City.objects.create(**city_data)
                messages.success(request, f'City "{name}" added successfully!')
                return redirect('travels_cities_list')
            except Exception as e:
                messages.error(request, f'Error adding city: {str(e)}')
        else:
            messages.error(request, 'City name is required!')
    
    return render(request, 'travels/city_add.html')


@login_required
def travels_city_edit(request, city_id):
    """Edit existing city"""
    if not request.user.is_authenticated or request.user.user_type != 'travels':
        return redirect('travels_login')
    
    try:
        city = City.objects.get(id=city_id)
    except City.DoesNotExist:
        messages.error(request, 'City not found!')
        return redirect('travels_cities_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        image = request.FILES.get('image')
        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()
        tourist_places = request.POST.get('tourist_places', '').strip()
        sightseeing_kilometers = request.POST.get('sightseeing_kilometers', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        if name:
            try:
                city.name = name
                city.description = description
                if image:
                    city.image = image
                city.tourist_places = tourist_places
                city.is_active = is_active
                
                # Update coordinates
                if latitude and longitude:
                    try:
                        city.latitude = float(latitude)
                        city.longitude = float(longitude)
                    except ValueError:
                        messages.error(request, 'Invalid latitude or longitude format!')
                        return render(request, 'travels/city_edit.html', {'city': city})
                else:
                    city.latitude = None
                    city.longitude = None
                
                # Update sightseeing kilometers
                if sightseeing_kilometers:
                    try:
                        city.sightseeing_kilometers = float(sightseeing_kilometers)
                    except ValueError:
                        messages.error(request, 'Invalid sightseeing kilometers format!')
                        return render(request, 'travels/city_edit.html', {'city': city})
                else:
                    city.sightseeing_kilometers = 0
                
                # Update hill station fields
                is_hill_station = request.POST.get('is_hill_station') == 'on'
                city.is_hill_station = is_hill_station
                
                if is_hill_station:
                    hill_station_charge = request.POST.get('hill_station_charge', '').strip()
                    if hill_station_charge:
                        try:
                            city.hill_station_charge = float(hill_station_charge)
                        except ValueError:
                            messages.error(request, 'Invalid hill station charge format!')
                            return render(request, 'travels/city_edit.html', {'city': city})
                    else:
                        city.hill_station_charge = 750.0  # Default charge
                else:
                    # Keep existing charge even if not a hill station
                    if not city.hill_station_charge:
                        city.hill_station_charge = 750.0
                
                city.save()
                messages.success(request, f'City "{name}" updated successfully!')
                return redirect('travels_cities_list')
            except Exception as e:
                messages.error(request, f'Error updating city: {str(e)}')
        else:
            messages.error(request, 'City name is required!')
    
    context = {
        'city': city,
    }
    return render(request, 'travels/city_edit.html', context)


@login_required
def travels_city_delete(request, city_id):
    """Delete city"""
    if not request.user.is_authenticated or request.user.user_type != 'travels':
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    try:
        city = City.objects.get(id=city_id)
        city_name = city.name
        city.delete()
        return JsonResponse({'success': True, 'message': f'City "{city_name}" deleted successfully!'})
    except City.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'City not found!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error deleting city: {str(e)}'})


@login_required
def travels_local_areas_list(request, city_id):
    """Local Areas Management for a specific city"""
    if not request.user.is_authenticated or request.user.user_type != 'travels':
        return redirect('travels_login')
    
    try:
        city = City.objects.get(id=city_id)
    except City.DoesNotExist:
        messages.error(request, 'City not found!')
        return redirect('travels_cities_list')
    
    local_areas = LocalArea.objects.filter(city=city).order_by('name')
    context = {
        'city': city,
        'local_areas': local_areas,
    }
    return render(request, 'travels/local_areas_list.html', context)


@login_required
def travels_local_area_add(request, city_id):
    """Add new local area to a city"""
    if not request.user.is_authenticated or request.user.user_type != 'travels':
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    try:
        city = City.objects.get(id=city_id)
    except City.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'City not found!'})
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()
        
        if name:
            try:
                # Check if local area already exists
                if LocalArea.objects.filter(city=city, name__iexact=name).exists():
                    return JsonResponse({'success': False, 'message': f'Local area "{name}" already exists in {city.name}!'})
                
                # Create local area
                local_area_data = {
                    'city': city,
                    'name': name
                }
                
                # Add coordinates if provided
                if latitude and longitude:
                    try:
                        local_area_data['latitude'] = float(latitude)
                        local_area_data['longitude'] = float(longitude)
                    except ValueError:
                        return JsonResponse({'success': False, 'message': 'Invalid latitude or longitude format!'})
                
                local_area = LocalArea.objects.create(**local_area_data)
                
                return JsonResponse({
                    'success': True, 
                    'message': f'Local area "{name}" added successfully!',
                    'local_area': {
                        'id': local_area.id,
                        'name': local_area.name,
                        'latitude': str(local_area.latitude) if local_area.latitude else None,
                        'longitude': str(local_area.longitude) if local_area.longitude else None
                    }
                })
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error adding local area: {str(e)}'})
        else:
            return JsonResponse({'success': False, 'message': 'Local area name is required!'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def travels_local_area_delete(request, area_id):
    """Delete local area"""
    if not request.user.is_authenticated or request.user.user_type != 'travels':
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    try:
        local_area = LocalArea.objects.get(id=area_id)
        area_name = local_area.name
        local_area.delete()
        return JsonResponse({'success': True, 'message': f'Local area "{area_name}" deleted successfully!'})
    except LocalArea.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Local area not found!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error deleting local area: {str(e)}'})


# Travel Dashboard Management Views
@login_required
def travels_vehicles_list(request):
    """List all vehicles for travel admin"""
    if request.user.user_type != 'travels':
        return redirect('home')
    
    from vehicles.models import Vehicle
    vehicles = Vehicle.objects.all().order_by('-created_at')
    
    context = {
        'vehicles': vehicles,
    }
    return render(request, 'travels/vehicles_list.html', context)


@login_required
def travels_vehicle_add(request):
    """Add new vehicle for travel admin"""
    if request.user.user_type != 'travels':
        return redirect('home')
    
    if request.method == 'POST':
        from vehicles.models import Vehicle
        try:
            vehicle = Vehicle.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                max_seats=int(request.POST.get('max_seats', 4)),
                luggage_capacity=request.POST.get('luggage_capacity', ''),
                fuel_type=request.POST.get('fuel_type', 'petrol'),
                ac_type=request.POST.get('ac_type', 'ac'),
                fare_per_km=float(request.POST.get('fare_per_km', 0)),
                driver_charge_per_day=float(request.POST.get('driver_charge_per_day', 0)),
                per_day_fee=float(request.POST.get('per_day_fee', 0)),
                min_km_per_day=int(request.POST.get('min_km_per_day', 250)),
                # Local trip pricing fields
                fare_per_hour=float(request.POST.get('fare_per_hour', 0)),
                min_hours_local=int(request.POST.get('min_hours_local', 3)),
                min_hours_fee_local=float(request.POST.get('min_hours_fee_local', 0)),
                max_distance_min_hours=int(request.POST.get('max_distance_min_hours', 30)),
                fare_per_km_local=float(request.POST.get('fare_per_km_local', 0)),
                is_available=request.POST.get('is_available') == 'on',
                is_active=request.POST.get('is_active') == 'on',
            )
            
            # Handle image upload
            if 'image' in request.FILES:
                vehicle.image = request.FILES['image']
                vehicle.save()
            
            from django.contrib import messages
            messages.success(request, f'Vehicle "{vehicle.name}" added successfully!')
            return redirect('travels_vehicles_list')
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error adding vehicle: {str(e)}')
    
    return render(request, 'travels/vehicle_form.html', {'action': 'Add'})


@login_required
def travels_vehicle_edit(request, vehicle_id):
    """Edit vehicle for travel admin"""
    if request.user.user_type != 'travels':
        return redirect('home')
    
    from vehicles.models import Vehicle
    from django.shortcuts import get_object_or_404
    
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if request.method == 'POST':
        try:
            vehicle.name = request.POST.get('name')
            vehicle.description = request.POST.get('description', '')
            vehicle.max_seats = int(request.POST.get('max_seats', 4))
            vehicle.luggage_capacity = request.POST.get('luggage_capacity', '')
            vehicle.fuel_type = request.POST.get('fuel_type', 'petrol')
            vehicle.ac_type = request.POST.get('ac_type', 'ac')
            vehicle.fare_per_km = float(request.POST.get('fare_per_km', 0))
            vehicle.driver_charge_per_day = float(request.POST.get('driver_charge_per_day', 0))
            vehicle.per_day_fee = float(request.POST.get('per_day_fee', 0))
            vehicle.min_km_per_day = int(request.POST.get('min_km_per_day', 250))
            # Local trip pricing fields
            vehicle.fare_per_hour = float(request.POST.get('fare_per_hour', 0))
            vehicle.min_hours_local = int(request.POST.get('min_hours_local', 3))
            vehicle.min_hours_fee_local = float(request.POST.get('min_hours_fee_local', 0))
            vehicle.max_distance_min_hours = int(request.POST.get('max_distance_min_hours', 30))
            vehicle.fare_per_km_local = float(request.POST.get('fare_per_km_local', 0))
            vehicle.is_available = request.POST.get('is_available') == 'on'
            vehicle.is_active = request.POST.get('is_active') == 'on'
            
            # Handle image upload
            if 'image' in request.FILES:
                vehicle.image = request.FILES['image']
            
            vehicle.save()
            
            from django.contrib import messages
            messages.success(request, f'Vehicle "{vehicle.name}" updated successfully!')
            return redirect('travels_vehicles_list')
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error updating vehicle: {str(e)}')
    
    context = {
        'vehicle': vehicle,
        'action': 'Edit'
    }
    return render(request, 'travels/vehicle_form.html', context)


@login_required
def travels_vehicle_delete(request, vehicle_id):
    """Delete vehicle for travel admin"""
    if request.user.user_type != 'travels':
        return redirect('home')
    
    from vehicles.models import Vehicle
    from django.shortcuts import get_object_or_404
    
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    vehicle_name = vehicle.name
    vehicle.delete()
    
    from django.contrib import messages
    messages.success(request, f'Vehicle "{vehicle_name}" deleted successfully!')
    return redirect('travels_vehicles_list')


@login_required
def travels_bookings_list(request):
    """List all bookings for travel admin"""
    if request.user.user_type != 'travels':
        return redirect('home')
    
    from bookings.models import Booking
    
    status_filter = request.GET.get('status', '')
    bookings = Booking.objects.all().order_by('-created_at')
    
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    context = {
        'bookings': bookings,
        'status_filter': status_filter,
    }
    return render(request, 'travels/bookings_list.html', context)


@login_required
def travels_booking_detail(request, booking_id):
    """View and edit booking details for travel admin"""
    if request.user.user_type != 'travels':
        return redirect('home')
    
    from bookings.models import Booking
    from django.shortcuts import get_object_or_404
    
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        try:
            booking.status = request.POST.get('status')
            booking.special_instructions = request.POST.get('special_instructions', '')
            booking.save()
            
            from django.contrib import messages
            messages.success(request, f'Booking {booking.booking_number} updated successfully!')
            return redirect('travels_bookings_list')
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error updating booking: {str(e)}')
    
    context = {
        'booking': booking,
    }
    return render(request, 'travels/booking_detail.html', context)


@login_required
def travels_payments_list(request):
    """List all payments for travel admin"""
    if request.user.user_type != 'travels':
        return redirect('home')
    
    from bookings.models import Payment
    
    payments = Payment.objects.all().select_related('booking').order_by('-created_at')
    
    context = {
        'payments': payments,
    }
    return render(request, 'travels/payments_list.html', context)


@login_required
def travels_payment_update(request, payment_id):
    """Update payment status for travel admin"""
    if request.user.user_type != 'travels':
        return redirect('home')
    
    from bookings.models import Payment
    from django.shortcuts import get_object_or_404
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        try:
            payment.status = request.POST.get('status')
            payment.save()
            
            from django.contrib import messages
            messages.success(request, f'Payment status updated successfully!')
            return redirect('travels_payments_list')
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error updating payment: {str(e)}')
    
    context = {
        'payment': payment,
    }
    return render(request, 'travels/payment_update.html', context)


@login_required
def travels_packages_list(request):
    """List all tour packages for travel admin"""
    if request.user.user_type != 'travels':
        return redirect('home')

    packages = TourPackage.objects.all().order_by('-created_at')
    context = {
        'packages': packages,
    }
    return render(request, 'travels/packages_list.html', context)


@login_required
def travels_package_add(request):
    """Add new tour package with comprehensive tour planner"""
    if request.user.user_type != 'travels':
        return redirect('home')

    from django.contrib import messages
    from tours.models import City, TourPackage
    import json

    if request.method == 'POST':
        try:
            # Basic package details
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            days = int(request.POST.get('days', 1))
            pickup_city_id = request.POST.get('pickup_city') or None
            price_per_person = request.POST.get('price_per_person') or None
            price_per_vehicle = request.POST.get('price_per_vehicle') or 0
            vehicle_type = request.POST.get('vehicle_type', '')
            city_ids = request.POST.getlist('cities')
            
            # Hotel details
            include_hotel = request.POST.get('include_hotel') == '1'
            hotel_details = None
            if include_hotel:
                hotel_details = {
                    'name': request.POST.get('hotel_name', ''),
                    'city': request.POST.get('hotel_city', ''),
                    'checkin': request.POST.get('hotel_checkin', ''),
                    'checkout': request.POST.get('hotel_checkout', ''),
                    'room_type': request.POST.get('hotel_room_type', '')
                }
            
            # Day-wise itinerary - collect all day data dynamically
            day_wise_itinerary = []
            day_number = 1
            
            while True:
                pickup_time = request.POST.get(f'day_{day_number}_pickup_time')
                if not pickup_time:  # No more days
                    break
                    
                day_data = {
                    'day': day_number,
                    'pickup_time': pickup_time,
                    'pickup_location': request.POST.get(f'day_{day_number}_pickup_location', ''),
                    'places_to_visit': request.POST.get(f'day_{day_number}_places_to_visit', ''),
                    'route_description': request.POST.get(f'day_{day_number}_route_description', ''),
                    'notes': request.POST.get(f'day_{day_number}_notes', '')
                }
                day_wise_itinerary.append(day_data)
                day_number += 1

            # Create package
            pkg = TourPackage.objects.create(
                name=name,
                description=description,
                days=days,
                pickup_city_id=pickup_city_id,
                price_per_person=float(price_per_person) if price_per_person else None,
                price_per_vehicle=float(price_per_vehicle),
                vehicle_type=vehicle_type,
                include_hotel=include_hotel,
                hotel_details=hotel_details,
                day_wise_itinerary=day_wise_itinerary,
                is_active=True
            )
            
            if city_ids:
                pkg.cities.set(city_ids)
                
            messages.success(request, f'Tour package "{pkg.name}" created successfully!')
            return redirect('travels_packages_list')
            
        except Exception as e:
            messages.error(request, f'Error creating package: {str(e)}')

    # Get data for form
    cities = City.objects.filter(is_active=True).order_by('name')
    package_choices = TourPackage.PACKAGE_TYPE_CHOICES
    
    # Prepare template-friendly data
    template_package = None
    if request.method == 'GET':
        # For GET requests, create empty package structure
        template_package = {
            'name': '',
            'description': '',
            'days': '',
            'pickup_city_id': '',
            'price_per_vehicle': '',
            'price_per_person': '',
            'vehicle_type': '',
            'include_hotel': False,
            'hotel_details': {
                'name': '',
                'city': '',
                'checkin': '',
                'checkout': '',
                'room_type': ''
            },
            'day_wise_itinerary': [],
            'cities': {'all': []}
        }
    
    context = {
        'action': 'Add',
        'cities': cities,
        'package_choices': package_choices,
        'package': template_package
    }
    return render(request, 'travels/tour_planner.html', context)


@login_required
def travels_package_edit(request, package_id):
    """Edit tour package with comprehensive tour planner"""
    if request.user.user_type != 'travels':
        return redirect('home')

    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    from tours.models import City, TourPackage
    import json

    pkg = get_object_or_404(TourPackage, id=package_id)

    if request.method == 'POST':
        try:
            # Basic package details
            pkg.name = request.POST.get('name')
            pkg.description = request.POST.get('description', '')
            pkg.days = int(request.POST.get('days', pkg.days))
            pickup_city_id = request.POST.get('pickup_city') or None
            pkg.pickup_city_id = pickup_city_id
            price_per_person = request.POST.get('price_per_person') or None
            pkg.price_per_person = float(price_per_person) if price_per_person else None
            pkg.price_per_vehicle = float(request.POST.get('price_per_vehicle', pkg.price_per_vehicle))
            pkg.vehicle_type = request.POST.get('vehicle_type', '')
            city_ids = request.POST.getlist('cities')
            
            # Hotel details
            pkg.include_hotel = request.POST.get('include_hotel') == '1'
            hotel_details = None
            if pkg.include_hotel:
                hotel_details = {
                    'name': request.POST.get('hotel_name', ''),
                    'city': request.POST.get('hotel_city', ''),
                    'checkin': request.POST.get('hotel_checkin', ''),
                    'checkout': request.POST.get('hotel_checkout', ''),
                    'room_type': request.POST.get('hotel_room_type', '')
                }
            pkg.hotel_details = hotel_details
            
            # Day-wise itinerary - collect all day data dynamically
            day_wise_itinerary = []
            day_number = 1
            
            while True:
                pickup_time = request.POST.get(f'day_{day_number}_pickup_time')
                if not pickup_time:  # No more days
                    break
                    
                day_data = {
                    'day': day_number,
                    'pickup_time': pickup_time,
                    'pickup_location': request.POST.get(f'day_{day_number}_pickup_location', ''),
                    'places_to_visit': request.POST.get(f'day_{day_number}_places_to_visit', ''),
                    'route_description': request.POST.get(f'day_{day_number}_route_description', ''),
                    'notes': request.POST.get(f'day_{day_number}_notes', '')
                }
                day_wise_itinerary.append(day_data)
                day_number += 1
            
            pkg.day_wise_itinerary = day_wise_itinerary
            pkg.save()
            
            if city_ids:
                pkg.cities.set(city_ids)
                
            messages.success(request, f'Tour package "{pkg.name}" updated successfully!')
            return redirect('travels_packages_list')
            
        except Exception as e:
            messages.error(request, f'Error updating package: {str(e)}')

    # Get data for form
    cities = City.objects.filter(is_active=True).order_by('name')
    package_choices = TourPackage.PACKAGE_TYPE_CHOICES
    
    # Prepare template-friendly data
    template_package = {
        'name': pkg.name,
        'description': pkg.description,
        'days': pkg.days,
        'pickup_city_id': pkg.pickup_city_id,
        'price_per_vehicle': pkg.price_per_vehicle,
        'price_per_person': pkg.price_per_person,
        'vehicle_type': pkg.vehicle_type,
        'include_hotel': pkg.include_hotel,
        'hotel_details': pkg.hotel_details or {
            'name': '',
            'city': '',
            'checkin': '',
            'checkout': '',
            'room_type': ''
        },
        'day_wise_itinerary': pkg.day_wise_itinerary or [],
        'cities': {'all': list(pkg.cities.all())},
        'nights': pkg.nights
    }
    
    context = {
        'action': 'Edit',
        'cities': cities,
        'package_choices': package_choices,
        'package': template_package,
        'original_package': pkg  # Keep original for city checking
    }
    return render(request, 'travels/tour_planner.html', context)


@login_required
def travels_package_delete(request, package_id):
    """Delete a tour package"""
    if request.user.user_type != 'travels':
        return JsonResponse({'success': False, 'message': 'Unauthorized'})

    try:
        pkg = TourPackage.objects.get(id=package_id)
        name = pkg.name
        pkg.delete()
        return JsonResponse({'success': True, 'message': f'Package "{name}" deleted successfully!'})
    except TourPackage.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Package not found!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error deleting package: {str(e)}'})



@login_required
def travels_settings(request):
    """System Settings Management for travel admin"""
    if request.user.user_type != 'travels':
        return redirect('home')
    
    from .models import SystemSettings
    from django.contrib import messages
    
    # Get or create settings instance
    settings = SystemSettings.get_settings()
    
    if request.method == 'POST':
        try:
            # Payment Settings
            settings.upi_payments_enabled = request.POST.get('upi_payments_enabled') == 'on'
            settings.razorpay_enabled = request.POST.get('razorpay_enabled') == 'on'
            settings.default_payment_method = request.POST.get('default_payment_method', 'driver')
            
            # Booking Settings
            advance_percentage = request.POST.get('advance_payment_percentage', '20.00')
            try:
                settings.advance_payment_percentage = float(advance_percentage)
            except ValueError:
                settings.advance_payment_percentage = 20.00
            
            settings.booking_cancellation_enabled = request.POST.get('booking_cancellation_enabled') == 'on'
            settings.auto_booking_confirmation = request.POST.get('auto_booking_confirmation') == 'on'
            
            # Communication Settings
            settings.sms_notifications_enabled = request.POST.get('sms_notifications_enabled') == 'on'
            settings.email_notifications_enabled = request.POST.get('email_notifications_enabled') == 'on'
            settings.whatsapp_notifications_enabled = request.POST.get('whatsapp_notifications_enabled') == 'on'
            
            # Business Settings
            settings.gst_enabled = request.POST.get('gst_enabled') == 'on'
            settings.hill_station_charges_enabled = request.POST.get('hill_station_charges_enabled') == 'on'
            settings.dynamic_pricing_enabled = request.POST.get('dynamic_pricing_enabled') == 'on'
            
            # Website Settings
            settings.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
            settings.online_booking_enabled = request.POST.get('online_booking_enabled') == 'on'
            settings.show_vehicle_images = request.POST.get('show_vehicle_images') == 'on'
            
            # Contact Information
            settings.primary_phone = request.POST.get('primary_phone', settings.primary_phone)
            settings.secondary_phone = request.POST.get('secondary_phone', '')
            settings.email_address = request.POST.get('email_address', settings.email_address)
            settings.whatsapp_number = request.POST.get('whatsapp_number', settings.whatsapp_number)
            
            # Social Media
            settings.facebook_url = request.POST.get('facebook_url', '')
            settings.instagram_url = request.POST.get('instagram_url', '')
            settings.youtube_url = request.POST.get('youtube_url', '')
            settings.linkedin_url = request.POST.get('linkedin_url', '')
            
            # Set updated by
            settings.updated_by = request.user
            settings.save()
            
            messages.success(request, 'System settings updated successfully!')
            return redirect('travels_settings')
            
        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')
    
    context = {
        'settings': settings,
    }
    return render(request, 'travels/settings.html', context)


@login_required
def travels_settings_api(request):
    """API endpoint to get current settings for frontend"""
    if request.user.user_type != 'travels':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    from .models import SystemSettings
    
    settings = SystemSettings.get_settings()
    
    return JsonResponse({
        'upi_payments_enabled': settings.upi_payments_enabled,
        'razorpay_enabled': settings.razorpay_enabled,
        'default_payment_method': settings.default_payment_method,
        'advance_payment_percentage': float(settings.advance_payment_percentage),
        'booking_cancellation_enabled': settings.booking_cancellation_enabled,
        'auto_booking_confirmation': settings.auto_booking_confirmation,
        'sms_notifications_enabled': settings.sms_notifications_enabled,
        'email_notifications_enabled': settings.email_notifications_enabled,
        'whatsapp_notifications_enabled': settings.whatsapp_notifications_enabled,
        'gst_enabled': settings.gst_enabled,
        'hill_station_charges_enabled': settings.hill_station_charges_enabled,
        'dynamic_pricing_enabled': settings.dynamic_pricing_enabled,
        'maintenance_mode': settings.maintenance_mode,
        'online_booking_enabled': settings.online_booking_enabled,
        'show_vehicle_images': settings.show_vehicle_images,
        'primary_phone': settings.primary_phone,
        'secondary_phone': settings.secondary_phone,
        'email_address': settings.email_address,
        'whatsapp_number': settings.whatsapp_number,
        'facebook_url': settings.facebook_url,
        'instagram_url': settings.instagram_url,
        'youtube_url': settings.youtube_url,
        'linkedin_url': settings.linkedin_url,
    })