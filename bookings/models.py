from django.db import models
from accounts.models import User
from vehicles.models import Vehicle
from phonenumber_field.modelfields import PhoneNumberField


class Booking(models.Model):
    BOOKING_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    TRIP_TYPE_CHOICES = (
        ('outstation', 'Out Station'),
        ('local', 'Local'),
        ('oneway', 'One Way'),
        ('tour', 'Tour Package'),
        ('multicity', 'Multi City'),
        ('online_cab', 'Online Cab Booking'),
    )
    
    PAYMENT_TYPE_CHOICES = (
        ('upi', 'UPI'),
        ('driver', 'Driver'),
        ('office', 'Office'),
    )
    
    booking_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Guest Details
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = PhoneNumberField()
    flight_train_no = models.CharField(max_length=100, blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)
    
    # Location & Timing
    pickup_address = models.TextField()
    drop_address = models.TextField()
    pickup_city = models.CharField(max_length=255)
    pickup_date = models.DateField()
    pickup_time = models.TimeField(null=True, blank=True)
    drop_date = models.DateField(null=True, blank=True)
    drop_time = models.TimeField(null=True, blank=True)
    
    # Trip Details
    trip_type = models.CharField(max_length=20, choices=TRIP_TYPE_CHOICES)
    total_days = models.IntegerField(default=1)
    total_distance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Multi-city details (JSON field for flexibility)
    multicity_routes = models.JSONField(default=list, blank=True)
    
    # Payment Details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_instructions = models.TextField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notification-related fields
    notification_preferences = models.JSONField(default=dict, blank=True)
    last_notification_sent = models.DateTimeField(null=True, blank=True)
    notification_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.booking_number} - {self.name}"
    
    # Properties for notification services compatibility
    @property
    def customer_name(self):
        """Alias for name field"""
        return self.name
    
    @property
    def customer_email(self):
        """Alias for email field"""
        return self.email
    
    @property
    def customer_phone(self):
        """Alias for phone field"""
        return self.phone
    
    @property
    def drop_city(self):
        """Create a mock city object for drop location"""
        class MockCity:
            def __init__(self, name):
                self.name = name
        
        # Extract city from drop_address or use pickup_city
        return MockCity(self.pickup_city)  # Simplified for now
    
    def get_notification_context(self):
        """Generate context for notification templates"""
        from django.utils import timezone
        
        context = {
            'booking': self,
            'booking_number': self.booking_number,
            'customer_name': self.name,
            'customer_email': self.email,
            'customer_phone': str(self.phone),
            'pickup_city': self.pickup_city,
            'pickup_date': self.pickup_date,
            'pickup_time': self.pickup_time,
            'drop_date': self.drop_date,
            'drop_time': self.drop_time,
            'pickup_address': self.pickup_address,
            'drop_address': self.drop_address,
            'trip_type': self.get_trip_type_display(),
            'total_days': self.total_days,
            'total_distance': self.total_distance,
            'total_amount': self.total_amount,
            'advance_amount': self.advance_amount,
            'status': self.get_status_display(),
            'status_code': self.status,
            'payment_type': self.get_payment_type_display(),
            'adults': self.adults,
            'children': self.children,
            'vehicle': self.vehicle,
            'special_instructions': self.special_instructions,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'current_time': timezone.now(),
        }
        
        # Add multicity routes if available
        if self.multicity_routes:
            context['multicity_routes'] = self.multicity_routes
        
        return context
    
    def calculate_final_bill(self):
        """Calculate final bill including extra payments"""
        from decimal import Decimal
        
        # Get all extra payments for this booking
        extra_payments = self.extra_payments.filter(is_paid=False)
        extra_amount = sum(payment.amount for payment in extra_payments)
        
        # Convert to Decimal for consistent calculations
        total_amount = Decimal(str(self.total_amount))
        advance_amount = Decimal(str(self.advance_amount))
        extra_amount = Decimal(str(extra_amount))
        
        # Calculate remaining amount (total - advance)
        remaining_amount = total_amount - advance_amount
        
        # Calculate final total
        final_total = total_amount + extra_amount
        outstanding_balance = remaining_amount + extra_amount
        
        # Get GST rate
        gst_rate = GSTRate.get_current_gst_rate('transport')
        gst_rate_decimal = Decimal(str(gst_rate))
        
        base_amount = final_total / (1 + (gst_rate_decimal / 100))
        gst_amount = final_total - base_amount
        
        return {
            'original_amount': total_amount,
            'advance_paid': advance_amount,
            'remaining_amount': remaining_amount,
            'extra_payments': extra_payments,
            'extra_amount': extra_amount,
            'base_amount': base_amount,
            'gst_rate': gst_rate,
            'gst_amount': gst_amount,
            'final_total': final_total,
            'outstanding_balance': outstanding_balance,
            'payment_breakdown': {
                'advance': advance_amount,
                'remaining': remaining_amount,
                'extra': extra_amount,
                'total_due': outstanding_balance
            }
        }


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment - {self.booking.booking_number}"


class BookingRoute(models.Model):
    """For multi-city bookings"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='routes')
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    distance = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'booking_routes'
        ordering = ['order']


class GSTRate(models.Model):
    """Model to store GST rates for different services"""
    
    SERVICE_TYPES = (
        ('transport', 'Transport Services'),
        ('accommodation', 'Accommodation'),
        ('tour_package', 'Tour Package'),
        ('general', 'General Services'),
    )
    
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES, default='transport')
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField()
    effective_to = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gst_rates'
        ordering = ['-effective_from']
        verbose_name = 'GST Rate'
        verbose_name_plural = 'GST Rates'
    
    def __str__(self):
        return f"{self.get_service_type_display()} - {self.gst_percentage}% GST"
    
    @classmethod
    def get_current_gst_rate(cls, service_type='transport'):
        """Get current active GST rate for a service type"""
        from django.utils import timezone
        today = timezone.now().date()
        
        try:
            gst_rate = cls.objects.filter(
                service_type=service_type,
                is_active=True,
                effective_from__lte=today
            ).filter(
                models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=today)
            ).first()
            
            return float(gst_rate.gst_percentage) if gst_rate else 18.0
        except:
            return 18.0


class ExtraPayment(models.Model):
    """Model for additional charges added after trip completion"""
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='extra_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'extra_payments'
        ordering = ['-added_at']
        verbose_name = 'Extra Payment'
        verbose_name_plural = 'Extra Payments'
    
    def __str__(self):
        return f"Extra Payment - {self.booking.booking_number} - ₹{self.amount}"


class NotificationRecord(models.Model):
    """Model to track notification delivery status"""
    
    NOTIFICATION_TYPES = (
        ('booking_confirmation', 'Booking Confirmation'),
        ('admin_notification', 'Admin Notification'),
        ('status_update', 'Status Update'),
        ('final_bill', 'Final Bill'),
        ('payment_reminder', 'Payment Reminder'),
        ('trip_completion', 'Trip Completion'),
    )
    
    CHANNELS = (
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
    )
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='notification_records')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    channel = models.CharField(max_length=20, choices=CHANNELS)
    recipient = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    template_used = models.CharField(max_length=100, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'notification_records'
        ordering = ['-sent_at']
        verbose_name = 'Notification Record'
        verbose_name_plural = 'Notification Records'
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.booking.booking_number} - {self.get_channel_display()}"
    
    def mark_delivered(self):
        """Mark notification as delivered"""
        from django.utils import timezone
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at'])
    
    def mark_opened(self):
        """Mark notification as opened"""
        from django.utils import timezone
        self.status = 'opened'
        self.opened_at = timezone.now()
        self.save(update_fields=['status', 'opened_at'])
    
    def mark_clicked(self):
        """Mark notification as clicked"""
        from django.utils import timezone
        self.status = 'clicked'
        self.clicked_at = timezone.now()
        self.save(update_fields=['status', 'clicked_at'])
    
    def mark_failed(self, error_message):
        """Mark notification as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save(update_fields=['status', 'error_message', 'retry_count'])


class NotificationTemplate(models.Model):
    """Model for managing notification templates"""
    
    TEMPLATE_TYPES = (
        ('booking_confirmation', 'Booking Confirmation'),
        ('admin_notification', 'Admin Notification'),
        ('status_update', 'Status Update'),
        ('final_bill', 'Final Bill'),
        ('payment_reminder', 'Payment Reminder'),
        ('trip_completion', 'Trip Completion'),
    )
    
    CHANNELS = (
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
    )
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    channel = models.CharField(max_length=20, choices=CHANNELS)
    subject_template = models.CharField(max_length=255, blank=True, null=True)
    body_template = models.TextField()
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'notification_templates'
        ordering = ['template_type', 'channel', 'name']
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
        unique_together = ['template_type', 'channel', 'is_default']
    
    def __str__(self):
        return f"{self.get_template_type_display()} - {self.get_channel_display()} - {self.name}"

