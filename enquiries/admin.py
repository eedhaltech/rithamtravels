from django.contrib import admin
from .models import Enquiry, Testimonial, Promotion


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'enquiry_type', 'subject', 'is_resolved', 'created_at')
    list_filter = ('enquiry_type', 'is_resolved', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_per_page = 25
    readonly_fields = ('created_at',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'is_featured', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_featured', 'is_approved')
    list_per_page = 25
    readonly_fields = ('created_at',)


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at', 'expires_at')
    list_filter = ('is_active',)
    list_per_page = 25
    readonly_fields = ('created_at',)

