from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField


class Enquiry(models.Model):
    ENQUIRY_TYPE_CHOICES = (
        ('general', 'General'),
        ('booking', 'Booking'),
        ('package', 'Package'),
        ('payment', 'Payment'),
        ('cancellation', 'Cancellation'),
    )
    
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = PhoneNumberField()
    enquiry_type = models.CharField(max_length=50, choices=ENQUIRY_TYPE_CHOICES, default='general')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'enquiries'
        ordering = ['-created_at']
        verbose_name_plural = 'Enquiries'
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class Testimonial(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='testimonial')
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    review = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)  # Auto-approved by default
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'testimonials'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.rating} stars"


class Promotion(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='promotions/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'promotions'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

