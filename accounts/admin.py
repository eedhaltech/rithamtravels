from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, CustomerProfile, TravelsProfile, SystemSettings, PasswordResetOTP, OTPAttemptLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'user_type', 'phone', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional Info', {'fields': ('user_type', 'address')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'phone_number'),
        }),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'created_at')


@admin.register(TravelsProfile)
class TravelsProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'gst_number', 'created_at')


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'upi_payments_enabled', 'default_payment_method', 'updated_at', 'updated_by')
    list_filter = ('upi_payments_enabled', 'razorpay_enabled', 'maintenance_mode', 'online_booking_enabled')
    
    fieldsets = (
        ('Payment Settings', {
            'fields': ('upi_payments_enabled', 'razorpay_enabled', 'default_payment_method')
        }),
        ('Booking Settings', {
            'fields': ('advance_payment_percentage', 'booking_cancellation_enabled', 'auto_booking_confirmation')
        }),
        ('Communication Settings', {
            'fields': ('sms_notifications_enabled', 'email_notifications_enabled', 'whatsapp_notifications_enabled')
        }),
        ('Business Settings', {
            'fields': ('gst_enabled', 'hill_station_charges_enabled', 'dynamic_pricing_enabled')
        }),
        ('Website Settings', {
            'fields': ('maintenance_mode', 'online_booking_enabled', 'show_vehicle_images')
        }),
        ('Contact Information', {
            'fields': ('primary_phone', 'secondary_phone', 'email_address', 'whatsapp_number')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'youtube_url', 'linkedin_url')
        }),
        ('Metadata', {
            'fields': ('updated_by',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not SystemSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of settings
        return False
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'created_at', 'expires_at', 'is_used', 'attempts', 'ip_address')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'user__username', 'otp', 'ip_address')
    readonly_fields = ('otp', 'created_at', 'expires_at', 'ip_address', 'user_agent')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('OTP Information', {
            'fields': ('user', 'otp', 'created_at', 'expires_at', 'is_used')
        }),
        ('Security', {
            'fields': ('attempts', 'max_attempts', 'ip_address', 'user_agent')
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing


@admin.register(OTPAttemptLog)
class OTPAttemptLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'attempted_otp', 'is_successful', 'failure_reason', 'ip_address', 'created_at')
    list_filter = ('is_successful', 'failure_reason', 'created_at')
    search_fields = ('user__email', 'user__username', 'attempted_otp', 'ip_address')
    readonly_fields = ('user', 'otp_instance', 'attempted_otp', 'ip_address', 'user_agent', 'is_successful', 'failure_reason', 'created_at')
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing

