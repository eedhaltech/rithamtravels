from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.cache import cache
import random
import string


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('travels', 'Travels Admin'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Make email required and unique for authentication
    email = models.EmailField(unique=True)
    
    # Use email as the username field for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    # Add phone property for backward compatibility
    @property
    def phone(self):
        return self.phone_number
    
    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"


class PasswordResetOTP(models.Model):
    """Model to store OTP for password reset with enhanced security"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.otp:
            # Generate cryptographically secure 6-digit OTP
            self.otp = ''.join(random.choices(string.digits, k=6))
        if not self.expires_at:
            # 10 minutes expiry
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def is_max_attempts_reached(self):
        """Check if maximum attempts have been reached"""
        return self.attempts >= self.max_attempts
    
    def increment_attempts(self):
        """Increment attempt counter"""
        self.attempts += 1
        self.save(update_fields=['attempts'])
    
    def is_valid_for_verification(self):
        """Check if OTP is valid for verification"""
        return not self.is_used and not self.is_expired() and not self.is_max_attempts_reached()
    
    def mark_as_used(self):
        """Mark OTP as used"""
        self.is_used = True
        self.save(update_fields=['is_used'])
    
    def time_remaining(self):
        """Get remaining time in seconds"""
        if self.is_expired():
            return 0
        return int((self.expires_at - timezone.now()).total_seconds())
    
    def __str__(self):
        return f"OTP for {self.user.email} - {'Used' if self.is_used else 'Active'}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_used', 'expires_at']),
            models.Index(fields=['created_at']),
        ]


class OTPAttemptLog(models.Model):
    """Log all OTP verification attempts for security monitoring"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_instance = models.ForeignKey(PasswordResetOTP, on_delete=models.CASCADE, null=True, blank=True)
    attempted_otp = models.CharField(max_length=6)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    is_successful = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        status = "Success" if self.is_successful else f"Failed ({self.failure_reason})"
        return f"OTP attempt for {self.user.email} - {status}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]


class CustomerProfile(models.Model):
    """Customer profile for additional customer information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Customer Profile"


class TravelsProfile(models.Model):
    """Travels admin profile for business information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='travels_profile')
    company_name = models.CharField(max_length=255, default="Ritham Tours & Travels")
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    business_address = models.TextField(blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.company_name}"


class SystemSettings(models.Model):
    """System-wide configuration settings"""
    
    # Payment Settings
    upi_payments_enabled = models.BooleanField(
        default=False,  # Set to OFF by default to exclude from booking calculations
        help_text="Enable/disable UPI payment option on booking page"
    )
    razorpay_enabled = models.BooleanField(
        default=True,
        help_text="Enable/disable Razorpay online payments"
    )
    default_payment_method = models.CharField(
        max_length=20,
        choices=[
            ('upi', 'UPI Payment'),
            ('driver', 'Pay Driver'),
            ('office', 'Pay at Office'),
        ],
        default='driver',
        help_text="Default payment method when UPI is disabled"
    )
    
    # Booking Settings
    advance_payment_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=20.00,
        help_text="Percentage of total amount for advance payment"
    )
    booking_cancellation_enabled = models.BooleanField(
        default=True,
        help_text="Allow customers to cancel bookings"
    )
    auto_booking_confirmation = models.BooleanField(
        default=False,
        help_text="Automatically confirm bookings without admin approval"
    )
    
    # Communication Settings
    sms_notifications_enabled = models.BooleanField(
        default=True,
        help_text="Send SMS notifications for booking updates"
    )
    email_notifications_enabled = models.BooleanField(
        default=True,
        help_text="Send email notifications for booking updates"
    )
    whatsapp_notifications_enabled = models.BooleanField(
        default=True,
        help_text="Send WhatsApp notifications for booking updates"
    )
    
    # Business Settings
    gst_enabled = models.BooleanField(
        default=False,  # Set to OFF by default to exclude from booking calculations
        help_text="Apply GST to bookings"
    )
    hill_station_charges_enabled = models.BooleanField(
        default=True,
        help_text="Apply hill station charges to applicable destinations"
    )
    dynamic_pricing_enabled = models.BooleanField(
        default=False,
        help_text="Enable dynamic pricing based on demand and season"
    )
    
    # Website Settings
    maintenance_mode = models.BooleanField(
        default=False,
        help_text="Put website in maintenance mode"
    )
    online_booking_enabled = models.BooleanField(
        default=True,
        help_text="Allow online bookings (disable for phone-only bookings)"
    )
    show_vehicle_images = models.BooleanField(
        default=True,
        help_text="Display vehicle images on booking page"
    )
    
    # Contact Information
    primary_phone = models.CharField(
        max_length=15,
        default="+91 97871 10763",
        help_text="Primary contact phone number"
    )
    secondary_phone = models.CharField(
        max_length=15,
        blank=True,
        help_text="Secondary contact phone number"
    )
    email_address = models.EmailField(
        default="rithamtravels@gmail.com",
        help_text="Primary contact email address"
    )
    whatsapp_number = models.CharField(
        max_length=15,
        default="+91 97871 10763",
        help_text="WhatsApp contact number"
    )
    
    # Social Media
    facebook_url = models.URLField(
        blank=True,
        default="https://www.facebook.com/share/1G4KuLPscB/",
        help_text="Facebook page URL"
    )
    instagram_url = models.URLField(
        blank=True,
        default="https://www.instagram.com/rithamtoursandtravels",
        help_text="Instagram profile URL"
    )
    youtube_url = models.URLField(
        blank=True,
        default="https://youtube.com/@rithamtoursandtravels?si=rJulxr_AG9qUCaqI",
        help_text="YouTube channel URL"
    )
    linkedin_url = models.URLField(
        blank=True,
        default="https://www.linkedin.com/in/krishna-moorthy-9879689b/?originalSubdomain=in",
        help_text="LinkedIn profile URL"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="User who last updated the settings"
    )
    
    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        return f"System Settings (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"
    
    @classmethod
    def get_settings(cls):
        """Get or create system settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion of settings
        pass