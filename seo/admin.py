"""
Django Admin Configuration for SEO Models
Provides user-friendly interface for managing SEO settings
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import SEOConfig, PageSEO, SEORedirect


@admin.register(SEOConfig)
class SEOConfigAdmin(admin.ModelAdmin):
    """Admin interface for global SEO configuration"""
    
    list_display = [
        'site_name',
        'is_active',
        'has_analytics',
        'has_verification',
        'updated_at'
    ]
    
    list_filter = ['is_active', 'created_at', 'updated_at']
    
    search_fields = ['site_name', 'site_description']
    
    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'site_description', 'site_keywords', 'is_active')
        }),
        ('Social Media', {
            'fields': ('facebook_app_id', 'twitter_handle'),
            'classes': ('collapse',)
        }),
        ('Analytics & Verification', {
            'fields': ('google_analytics_id', 'google_site_verification'),
            'classes': ('collapse',)
        }),
        ('Images', {
            'fields': ('default_og_image',),
            'classes': ('collapse',)
        }),
        ('Advanced', {
            'fields': ('robots_txt_content',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def has_analytics(self, obj):
        """Check if Google Analytics is configured"""
        return bool(obj.google_analytics_id)
    has_analytics.boolean = True
    has_analytics.short_description = 'Analytics'
    
    def has_verification(self, obj):
        """Check if Google verification is configured"""
        return bool(obj.google_site_verification)
    has_verification.boolean = True
    has_verification.short_description = 'Verified'
    
    def save_model(self, request, obj, form, change):
        """Ensure only one active configuration"""
        if obj.is_active:
            SEOConfig.objects.filter(is_active=True).exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(PageSEO)
class PageSEOAdmin(admin.ModelAdmin):
    """Admin interface for page-specific SEO overrides"""
    
    list_display = [
        'page_name',
        'page_path',
        'page_type',
        'has_custom_title',
        'has_custom_description',
        'has_og_image',
        'is_active',
        'updated_at'
    ]
    
    list_filter = [
        'page_type',
        'is_active',
        'twitter_card_type',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'page_name',
        'page_path',
        'title',
        'description',
        'keywords'
    ]
    
    fieldsets = (
        ('Page Information', {
            'fields': ('page_name', 'page_path', 'page_type', 'is_active')
        }),
        ('Basic SEO', {
            'fields': ('title', 'description', 'keywords'),
            'description': 'Leave blank to use defaults'
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image', 'og_image_alt'),
            'classes': ('collapse',)
        }),
        ('Twitter Card', {
            'fields': ('twitter_card_type',),
            'classes': ('collapse',)
        }),
        ('Advanced SEO', {
            'fields': ('canonical_url', 'robots', 'schema_type'),
            'classes': ('collapse',)
        }),
        ('Article Fields', {
            'fields': ('article_section', 'published_time', 'modified_time'),
            'classes': ('collapse',),
            'description': 'For blog posts and articles'
        }),
        ('Product Fields', {
            'fields': ('product_price', 'product_currency', 'product_availability'),
            'classes': ('collapse',),
            'description': 'For tour packages and products'
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def has_custom_title(self, obj):
        """Check if page has custom title"""
        return bool(obj.title)
    has_custom_title.boolean = True
    has_custom_title.short_description = 'Custom Title'
    
    def has_custom_description(self, obj):
        """Check if page has custom description"""
        return bool(obj.description)
    has_custom_description.boolean = True
    has_custom_description.short_description = 'Custom Desc'
    
    def has_og_image(self, obj):
        """Check if page has Open Graph image"""
        return bool(obj.og_image)
    has_og_image.boolean = True
    has_og_image.short_description = 'OG Image'
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form based on page type"""
        form = super().get_form(request, obj, **kwargs)
        
        # Add help text based on page type
        if obj and obj.page_type == 'tour':
            form.base_fields['title'].help_text = "e.g., 'Goa Tour Package - 3 Days 2 Nights'"
            form.base_fields['description'].help_text = "Describe the tour highlights and what's included"
        elif obj and obj.page_type == 'blog':
            form.base_fields['title'].help_text = "e.g., 'Top 10 Places to Visit in Kerala'"
            form.base_fields['description'].help_text = "Brief summary of the blog post content"
        
        return form


@admin.register(SEORedirect)
class SEORedirectAdmin(admin.ModelAdmin):
    """Admin interface for SEO redirects"""
    
    list_display = [
        'old_path',
        'new_path',
        'redirect_type',
        'is_active',
        'created_at'
    ]
    
    list_filter = ['redirect_type', 'is_active', 'created_at']
    
    search_fields = ['old_path', 'new_path']
    
    fields = ['old_path', 'new_path', 'redirect_type', 'is_active']
    
    def get_readonly_fields(self, request, obj=None):
        """Make old_path readonly when editing"""
        if obj:  # Editing existing object
            return ['old_path', 'created_at']
        return ['created_at']


# Custom admin site configuration
admin.site.site_header = "Ritham Tours & Travels - SEO Management"
admin.site.site_title = "SEO Admin"
admin.site.index_title = "SEO Configuration"