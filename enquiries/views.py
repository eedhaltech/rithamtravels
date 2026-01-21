from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from .models import Enquiry, Testimonial, Promotion
from django.core.mail import send_mail
from django.conf import settings
import requests
import json


class ContactUsView(TemplateView):
    template_name = 'enquiries/contact_us.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testimonials'] = Testimonial.objects.filter(is_approved=True, is_featured=True)[:3]
        context['promotions'] = Promotion.objects.filter(is_active=True)[:3]
        return context


class TestimonialsView(TemplateView):
    template_name = 'enquiries/testimonials.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all approved testimonials
        testimonials = Testimonial.objects.filter(is_approved=True)
        context['testimonials'] = testimonials
        
        # Calculate statistics
        total_reviews = testimonials.count()
        context['total_reviews'] = total_reviews
        
        # Calculate average rating
        if total_reviews > 0:
            from django.db.models import Avg
            avg_rating = testimonials.aggregate(Avg('rating'))['rating__avg']
            context['average_rating'] = round(avg_rating, 1) if avg_rating else 0
            
            # Calculate rating distribution
            rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for testimonial in testimonials:
                rating_counts[testimonial.rating] = rating_counts.get(testimonial.rating, 0) + 1
            
            context['rating_counts'] = rating_counts
            
            # Calculate percentages
            rating_percentages = {}
            for rating, count in rating_counts.items():
                rating_percentages[rating] = round((count / total_reviews) * 100) if total_reviews > 0 else 0
            context['rating_percentages'] = rating_percentages
            
            # Calculate 4 & 5-star percentage
            four_star_count = rating_counts.get(4, 0)
            five_star_count = rating_counts.get(5, 0)
            high_rating_percentage = round(((four_star_count + five_star_count) / total_reviews) * 100) if total_reviews > 0 else 0
            context['high_rating_percentage'] = high_rating_percentage
        else:
            context['average_rating'] = 0
            context['rating_counts'] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            context['rating_percentages'] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            context['high_rating_percentage'] = 0
        
        # Estimate happy customers (can be based on bookings or a multiplier)
        # For now, use a reasonable multiplier of reviews
        context['happy_customers'] = max(total_reviews * 10, 100)  # At least 100
        
        # Show customer reviews count only if >= 200
        context['show_customer_count'] = total_reviews >= 200000
        
        # Check if current user can submit a review
        if self.request.user.is_authenticated:
            context['user_can_review'] = not Testimonial.objects.filter(user=self.request.user).exists()
            context['user_has_reviewed'] = Testimonial.objects.filter(user=self.request.user).exists()
        else:
            context['user_can_review'] = False
            context['user_has_reviewed'] = False
            
        return context


@api_view(['POST'])
@permission_classes([AllowAny])
def create_enquiry(request):
    try:
        enquiry = Enquiry.objects.create(
            name=request.data.get('name'),
            email=request.data.get('email'),
            phone=request.data.get('phone'),
            enquiry_type=request.data.get('enquiry_type', 'general'),
            subject=request.data.get('subject'),
            message=request.data.get('message')
        )
        
        # Send email notification to multiple admin addresses
        try:
            # Admin email addresses
            admin_emails = [
                'info@rithamtravels.in',
                'admin@rithamtravels.in'
            ]
            
            # Also include settings-based company email if different
            company_email = getattr(settings, 'COMPANY_EMAIL', None)
            if company_email and company_email not in admin_emails:
                admin_emails.append(company_email)
            
            # Create detailed email content
            email_subject = f'New Contact Enquiry: {enquiry.subject}'
            email_message = f"""
New Contact Enquiry Received

Customer Details:
Name: {enquiry.name}
Email: {enquiry.email}
Phone: {enquiry.phone}
Enquiry Type: {enquiry.get_enquiry_type_display()}

Subject: {enquiry.subject}

Message:
{enquiry.message}

---
Submitted on: {enquiry.created_at.strftime('%d %B %Y at %I:%M %p')}
Enquiry ID: {enquiry.id}

Please respond to the customer at: {enquiry.email}
            """.strip()
            
            send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                admin_emails,
                fail_silently=False,
            )
            
            print(f"Enquiry notification sent to: {', '.join(admin_emails)}")
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            # Don't fail the enquiry creation if email fails
            pass
        
        return Response({'message': 'Enquiry submitted successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def create_testimonial(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Debug: Print user info
        print(f"User: {request.user}")
        print(f"Is authenticated: {request.user.is_authenticated}")
        print(f"User type: {type(request.user)}")
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You must be logged in to submit a review'}, status=401)
        
        # Check if user already has a testimonial
        if Testimonial.objects.filter(user=request.user).exists():
            return JsonResponse({'error': 'You have already submitted a review. Each user can only submit one review.'}, status=400)
        
        # Get form data
        rating = request.POST.get('rating', 5)
        review = request.POST.get('review', '').strip()
        
        # Validation
        if not review:
            return JsonResponse({'error': 'Review is required'}, status=400)
        if not rating:
            return JsonResponse({'error': 'Rating is required'}, status=400)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid rating value'}, status=400)
        
        # Use user's name and email from their account
        testimonial = Testimonial.objects.create(
            user=request.user,
            name=request.user.get_full_name() or request.user.username,
            email=request.user.email,
            rating=rating,
            review=review,
            is_approved=True  # Auto-approve testimonials
        )
        
        return JsonResponse({
            'message': 'Thank you for your review! It has been published successfully.',
            'testimonial_id': testimonial.id
        }, status=201)
        
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)


@csrf_exempt
def update_testimonial(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You must be logged in to edit a review'}, status=401)
        
        # Get user's testimonial
        try:
            testimonial = Testimonial.objects.get(user=request.user)
        except Testimonial.DoesNotExist:
            return JsonResponse({'error': 'You have not submitted a review yet'}, status=404)
        
        # Get form data
        rating = request.POST.get('rating', testimonial.rating)
        review = request.POST.get('review', '').strip()
        
        # Validation
        if not review:
            return JsonResponse({'error': 'Review is required'}, status=400)
        if not rating:
            return JsonResponse({'error': 'Rating is required'}, status=400)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid rating value'}, status=400)
        
        # Update testimonial
        testimonial.rating = rating
        testimonial.review = review
        testimonial.save()
        
        return JsonResponse({
            'message': 'Your review has been updated successfully!',
            'testimonial_id': testimonial.id
        }, status=200)
        
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)


@csrf_exempt
def get_user_testimonial(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You must be logged in'}, status=401)
        
        # Get user's testimonial
        try:
            testimonial = Testimonial.objects.get(user=request.user)
            return JsonResponse({
                'testimonial': {
                    'id': testimonial.id,
                    'rating': testimonial.rating,
                    'review': testimonial.review,
                    'created_at': testimonial.created_at.isoformat()
                }
            }, status=200)
        except Testimonial.DoesNotExist:
            return JsonResponse({'error': 'No testimonial found'}, status=404)
        
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)


# Policy Page Views
class TermsConditionsView(TemplateView):
    template_name = 'enquiries/terms_conditions.html'


class CancelRefundPolicyView(TemplateView):
    template_name = 'enquiries/cancel_refund_policy.html'


class PrivacyPolicyView(TemplateView):
    template_name = 'enquiries/privacy_policy.html'


class ShippingPolicyView(TemplateView):
    template_name = 'enquiries/shipping_policy.html'


class DisclaimerPolicyView(TemplateView):
    template_name = 'enquiries/disclaimer_policy.html'


class RazorpayPrivacyPolicyView(TemplateView):
    template_name = 'enquiries/razorpay_privacy_policy.html'


@api_view(['GET'])
@permission_classes([AllowAny])
def google_reviews_api(request):
    """
    Fetch Google Reviews using Google Places API
    
    Environment Variables Required:
    - GOOGLE_PLACES_API_KEY: Your Google Places API key
    - GOOGLE_PLACE_ID: Your business Place ID
    
    To get your Place ID:
    1. Go to https://developers.google.com/maps/documentation/places/web-service/place-id
    2. Search for your business
    3. Copy the Place ID
    
    To get API Key:
    1. Go to Google Cloud Console
    2. Enable Places API
    3. Create credentials (API Key)
    4. Restrict the key to Places API
    """
    
    # Get API credentials from settings
    api_key = getattr(settings, 'GOOGLE_PLACES_API_KEY', '')
    place_id = getattr(settings, 'GOOGLE_PLACE_ID', '')
    
    # Check if API credentials are configured
    if not api_key or not place_id:
        return JsonResponse({
            'success': False,
            'error': 'Google API credentials not configured',
            'message': 'Please set GOOGLE_PLACES_API_KEY and GOOGLE_PLACE_ID in your environment variables'
        })
    
    try:
        # Google Places API endpoint for place details
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        
        params = {
            'place_id': place_id,
            'fields': 'name,rating,user_ratings_total,reviews',
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') == 'OK':
            place_data = data.get('result', {})
            
            # Extract reviews
            reviews = place_data.get('reviews', [])
            
            # Process reviews
            processed_reviews = []
            for review in reviews:
                processed_reviews.append({
                    'author_name': review.get('author_name', 'Anonymous'),
                    'rating': review.get('rating', 5),
                    'text': review.get('text', ''),
                    'time': review.get('time', 0),
                    'profile_photo_url': review.get('profile_photo_url', ''),
                    'relative_time_description': review.get('relative_time_description', '')
                })
            
            # Calculate rating breakdown
            rating_breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for review in reviews:
                rating = review.get('rating', 5)
                if rating in rating_breakdown:
                    rating_breakdown[rating] += 1
            
            return JsonResponse({
                'success': True,
                'rating': place_data.get('rating', 4.8),
                'total_reviews': place_data.get('user_ratings_total', 0),
                'reviews': processed_reviews,
                'rating_breakdown': rating_breakdown,
                'place_name': place_data.get('name', 'Ritham Tours & Travels')
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch reviews from Google',
                'details': data.get('error_message', 'Unknown error'),
                'status': data.get('status', 'UNKNOWN_ERROR')
            })
            
    except requests.exceptions.Timeout:
        return JsonResponse({
            'success': False,
            'error': 'Request timeout',
            'message': 'Google API request timed out. Please try again.'
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'success': False,
            'error': 'Network error',
            'message': 'Failed to connect to Google API.',
            'details': str(e)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Server error while fetching reviews',
            'details': str(e)
        })

