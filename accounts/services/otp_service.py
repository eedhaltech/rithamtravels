"""
Comprehensive OTP Service for secure password reset functionality
"""
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from accounts.models import User, PasswordResetOTP, OTPAttemptLog

logger = logging.getLogger(__name__)


class OTPService:
    """Service class for handling OTP operations"""
    
    # Rate limiting settings
    MAX_OTP_REQUESTS_PER_HOUR = 5
    MAX_OTP_REQUESTS_PER_DAY = 10
    RATE_LIMIT_COOLDOWN = 300  # 5 minutes cooldown after max attempts
    
    @classmethod
    def get_client_ip(cls, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @classmethod
    def get_user_agent(cls, request):
        """Get user agent from request"""
        return request.META.get('HTTP_USER_AGENT', '')[:500]  # Limit length
    
    @classmethod
    def check_rate_limit(cls, user, ip_address):
        """Check if user/IP has exceeded rate limits"""
        # Check per-user rate limit
        user_key = f"otp_requests_user_{user.id}"
        user_requests = cache.get(user_key, 0)
        
        # Check per-IP rate limit
        ip_key = f"otp_requests_ip_{ip_address}"
        ip_requests = cache.get(ip_key, 0)
        
        # Check if user is in cooldown
        cooldown_key = f"otp_cooldown_{user.id}"
        if cache.get(cooldown_key):
            return False, "Too many failed attempts. Please try again in 5 minutes."
        
        if user_requests >= cls.MAX_OTP_REQUESTS_PER_HOUR:
            return False, "Too many OTP requests. Please try again later."
        
        if ip_requests >= cls.MAX_OTP_REQUESTS_PER_DAY:
            return False, "Too many OTP requests from this location. Please try again tomorrow."
        
        return True, None
    
    @classmethod
    def increment_rate_limit(cls, user, ip_address):
        """Increment rate limit counters"""
        user_key = f"otp_requests_user_{user.id}"
        ip_key = f"otp_requests_ip_{ip_address}"
        
        # Increment user counter (1 hour expiry)
        current_user_count = cache.get(user_key, 0)
        cache.set(user_key, current_user_count + 1, 3600)
        
        # Increment IP counter (24 hour expiry)
        current_ip_count = cache.get(ip_key, 0)
        cache.set(ip_key, current_ip_count + 1, 86400)
    
    @classmethod
    def send_otp(cls, user, user_type, request):
        """Send OTP to user's email"""
        try:
            ip_address = cls.get_client_ip(request)
            user_agent = cls.get_user_agent(request)
            
            # Check rate limits
            rate_limit_ok, rate_limit_msg = cls.check_rate_limit(user, ip_address)
            if not rate_limit_ok:
                return False, rate_limit_msg
            
            # Invalidate existing OTPs
            PasswordResetOTP.objects.filter(
                user=user, 
                is_used=False
            ).update(is_used=True)
            
            # Create new OTP
            otp_instance = PasswordResetOTP.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Send email
            success = cls._send_otp_email(user, otp_instance, user_type)
            
            if success:
                # Increment rate limit counters
                cls.increment_rate_limit(user, ip_address)
                
                logger.info(f"OTP sent successfully to {user.email} (Type: {user_type})")
                return True, f"OTP sent successfully to your email address for {user_type.title()} account"
            else:
                # Mark OTP as used if email failed
                otp_instance.mark_as_used()
                return False, "Failed to send OTP email. Please try again."
                
        except Exception as e:
            logger.error(f"Error sending OTP to {user.email}: {str(e)}")
            return False, "An error occurred while sending OTP. Please try again."
    
    @classmethod
    def _send_otp_email(cls, user, otp_instance, user_type):
        """Send OTP email with HTML template"""
        try:
            user_type_display = 'Customer' if user_type == 'customer' else 'Travels Admin'
            
            # Prepare context for email template
            context = {
                'user': user,
                'otp': otp_instance.otp,
                'user_type_display': user_type_display,
                'expires_in_minutes': 10,
                'company_name': 'Ritham Tours & Travels'
            }
            
            # Render HTML email
            html_message = render_to_string('emails/otp_email.html', context)
            plain_message = strip_tags(html_message)
            
            subject = f'Password Reset OTP - Ritham Tours & Travels ({user_type_display})'
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send OTP email to {user.email}: {str(e)}")
            return False
    
    @classmethod
    def verify_otp(cls, user, otp_code, request):
        """Verify OTP code"""
        ip_address = cls.get_client_ip(request)
        user_agent = cls.get_user_agent(request)
        
        # Find the most recent valid OTP
        otp_instance = PasswordResetOTP.objects.filter(
            user=user,
            is_used=False
        ).order_by('-created_at').first()
        
        # Log the attempt
        attempt_log = OTPAttemptLog.objects.create(
            user=user,
            otp_instance=otp_instance,
            attempted_otp=otp_code,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not otp_instance:
            attempt_log.failure_reason = "No active OTP"
            attempt_log.save()
            return False, "No active OTP found. Please request a new one."
        
        if otp_instance.is_expired():
            attempt_log.failure_reason = "OTP expired"
            attempt_log.save()
            otp_instance.mark_as_used()
            return False, "OTP has expired. Please request a new one."
        
        if otp_instance.is_max_attempts_reached():
            attempt_log.failure_reason = "Max attempts reached"
            attempt_log.save()
            otp_instance.mark_as_used()
            # Set cooldown
            cooldown_key = f"otp_cooldown_{user.id}"
            cache.set(cooldown_key, True, cls.RATE_LIMIT_COOLDOWN)
            return False, "Maximum verification attempts reached. Please request a new OTP."
        
        # Increment attempts
        otp_instance.increment_attempts()
        
        if otp_instance.otp != otp_code:
            attempt_log.failure_reason = "Invalid OTP"
            attempt_log.save()
            
            remaining_attempts = otp_instance.max_attempts - otp_instance.attempts
            if remaining_attempts > 0:
                return False, f"Invalid OTP. {remaining_attempts} attempts remaining."
            else:
                otp_instance.mark_as_used()
                # Set cooldown
                cooldown_key = f"otp_cooldown_{user.id}"
                cache.set(cooldown_key, True, cls.RATE_LIMIT_COOLDOWN)
                return False, "Invalid OTP. Maximum attempts reached. Please request a new OTP."
        
        # OTP is valid
        otp_instance.mark_as_used()
        attempt_log.is_successful = True
        attempt_log.save()
        
        logger.info(f"OTP verified successfully for {user.email}")
        return True, "OTP verified successfully"
    
    @classmethod
    def get_otp_status(cls, user):
        """Get current OTP status for user"""
        otp_instance = PasswordResetOTP.objects.filter(
            user=user,
            is_used=False
        ).order_by('-created_at').first()
        
        if not otp_instance:
            return {
                'has_active_otp': False,
                'time_remaining': 0,
                'attempts_remaining': 0
            }
        
        return {
            'has_active_otp': otp_instance.is_valid_for_verification(),
            'time_remaining': otp_instance.time_remaining(),
            'attempts_remaining': max(0, otp_instance.max_attempts - otp_instance.attempts),
            'is_expired': otp_instance.is_expired(),
            'max_attempts_reached': otp_instance.is_max_attempts_reached()
        }
    
    @classmethod
    def cleanup_expired_otps(cls):
        """Clean up expired OTPs (can be run as a periodic task)"""
        expired_count = PasswordResetOTP.objects.filter(
            expires_at__lt=timezone.now()
        ).update(is_used=True)
        
        logger.info(f"Cleaned up {expired_count} expired OTPs")
        return expired_count