from django.contrib import admin
from .models import Booking, Payment, BookingRoute, GSTRate, ExtraPayment, NotificationRecord, NotificationTemplate


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_number', 'name', 'phone', 'trip_type', 'status', 'total_amount', 'notification_count', 'created_at')
    list_filter = ('status', 'trip_type', 'payment_type')
    search_fields = ('booking_number', 'name', 'email', 'phone')
    readonly_fields = ('booking_number', 'created_at', 'updated_at', 'notification_count', 'last_notification_sent')
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('booking_number', 'user', 'vehicle', 'status')
        }),
        ('Guest Details', {
            'fields': ('name', 'email', 'phone', 'flight_train_no', 'landmark', 'adults', 'children')
        }),
        ('Trip Details', {
            'fields': ('pickup_address', 'drop_address', 'pickup_city', 'pickup_date', 'pickup_time', 
                      'drop_date', 'drop_time', 'trip_type', 'total_days', 'total_distance', 'multicity_routes')
        }),
        ('Payment Information', {
            'fields': ('payment_type', 'total_amount', 'advance_amount', 'special_instructions')
        }),
        ('Notification Tracking', {
            'fields': ('notification_preferences', 'notification_count', 'last_notification_sent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'status', 'razorpay_payment_id', 'created_at')
    list_filter = ('status',)
    search_fields = ('booking__booking_number', 'razorpay_payment_id')


@admin.register(BookingRoute)
class BookingRouteAdmin(admin.ModelAdmin):
    list_display = ('booking', 'from_location', 'to_location', 'distance', 'date', 'order')


@admin.register(GSTRate)
class GSTRateAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'gst_percentage', 'is_active', 'effective_from', 'effective_to', 'created_at')
    list_filter = ('service_type', 'is_active', 'effective_from')
    search_fields = ('service_type', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    date_hierarchy = 'effective_from'


@admin.register(ExtraPayment)
class ExtraPaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'description', 'is_paid', 'added_by', 'added_at')
    list_filter = ('is_paid', 'added_at', 'payment_date')
    search_fields = ('booking__booking_number', 'description', 'added_by__username')
    readonly_fields = ('added_at',)
    ordering = ('-added_at',)
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('booking', 'amount', 'description', 'notes')
        }),
        ('Payment Status', {
            'fields': ('is_paid', 'payment_date', 'payment_method')
        }),
        ('Tracking', {
            'fields': ('added_by', 'added_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(NotificationRecord)
class NotificationRecordAdmin(admin.ModelAdmin):
    list_display = ('booking', 'notification_type', 'channel', 'recipient', 'status', 'sent_at', 'retry_count')
    list_filter = ('notification_type', 'channel', 'status', 'sent_at')
    search_fields = ('booking__booking_number', 'recipient', 'template_used')
    readonly_fields = ('sent_at', 'delivered_at', 'opened_at', 'clicked_at')
    ordering = ('-sent_at',)
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('booking', 'notification_type', 'channel', 'recipient', 'template_used')
        }),
        ('Status Tracking', {
            'fields': ('status', 'sent_at', 'delivered_at', 'opened_at', 'clicked_at', 'retry_count')
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['resend_notifications', 'mark_as_delivered']
    
    def resend_notifications(self, request, queryset):
        """Admin action to resend failed notifications"""
        from .services.notification_service import notification_orchestrator
        
        resent_count = 0
        for notification in queryset.filter(status='failed'):
            try:
                result = notification_orchestrator.resend_notification(notification.id)
                if result['success']:
                    resent_count += 1
            except Exception as e:
                self.message_user(request, f"Error resending notification {notification.id}: {str(e)}", level='ERROR')
        
        self.message_user(request, f"Successfully resent {resent_count} notifications.")
    
    resend_notifications.short_description = "Resend selected failed notifications"
    
    def mark_as_delivered(self, request, queryset):
        """Admin action to mark notifications as delivered"""
        updated = queryset.filter(status='sent').update(status='delivered')
        self.message_user(request, f"Marked {updated} notifications as delivered.")
    
    mark_as_delivered.short_description = "Mark selected notifications as delivered"


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'channel', 'is_active', 'is_default', 'created_at')
    list_filter = ('template_type', 'channel', 'is_active', 'is_default', 'created_at')
    search_fields = ('name', 'template_type', 'channel')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('template_type', 'channel', 'name')
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'template_type', 'channel', 'is_active', 'is_default')
        }),
        ('Template Content', {
            'fields': ('subject_template', 'body_template')
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        """Set created_by when saving"""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

