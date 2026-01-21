"""
SEO Models for Ritham Tours & Travels
Provides database-driven SEO configuration and page-specific overrides
"""

from django.db import models
from django.core.validators import MaxLengthValidator
from django.utils import timezone


class SEOConfig(models.Model):
    """
    Global SEO configuration model
    Stores site-wide SEO settings that can be managed through Django admin
    """
    
    # Site Information
    site_name = models.CharField(
        max_length=100,
        default="Ritham Tours & Travels",
        help_text="Site name used in titles and meta tags"
    )
    
    site_description = models.TextField(
        max_length=160,
        default="Professional travel agency offering tours, cab bookings, and travel packages across India. Your trusted travel partner for memorable experiences.",
        help_text="Default site description (max 160 characters)"
    )
    
    site_keywords = models.TextField(
        default="tours, travel, cab booking, tour packages, ritham tours, travel agency, india tours",
        help_text="Default site keywords (comma-separated)"
    )
    
    # Social Media
    facebook_app_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Facebook App ID for Open Graph"
    )
    
    twitter_handle = models.CharField(
        max_length=50,
        default="@rithamtravels",
        help_text="Twitter handle (include @)"
    )
    
    # Analytics and Verification
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Google Analytics tracking ID (GA4)"
    )
    
    google_site_verification = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Search Console verification code"
    )
    
    # Default Images
    default_og_image = models.ImageField(
        upload_to='seo/og_images/',
        blank=True,
        null=True,
        help_text="Default Open Graph image (1200x630px recommended)"
    )
    
    # SEO Settings
    robots_txt_content = models.TextField(
        blank=True,
        help_text="Custom robots.txt content"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Active configuration
    is_active = models.BooleanField(
        default=True,
        help_text="Mark as active to use this configuration"
    )
    
    class Meta:
        verbose_name = "SEO Configuration"
        verbose_name_plural = "SEO Configurations"
        ordering = ['-is_active', '-updated_at']
    
    def __str__(self):
        return f"SEO Config - {self.site_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one active configuration
        if self.is_active:
            SEOConfig.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_config(cls):
        """Get the active SEO configuration"""
        try:
            return cls.objects.filter(is_active=True).first()
        except cls.DoesNotExist:
            return None


class PageSEO(models.Model):
    """
    Page-specific SEO overrides
    Allows customization of SEO meta tags for specific pages or URL patterns
    """
    
    PAGE_TYPES = [
        ('website', 'Website'),
        ('article', 'Article'),
        ('blog', 'Blog Post'),
        ('product', 'Product'),
        ('tour', 'Tour Package'),
        ('contact', 'Contact Page'),
        ('about', 'About Page'),
        ('service', 'Service Page'),
    ]
    
    # Page Identification
    page_path = models.CharField(
        max_length=255,
        unique=True,
        help_text="URL path (e.g., '/about/', '/tours/goa/')"
    )
    
    page_name = models.CharField(
        max_length=100,
        help_text="Human-readable page name for admin"
    )
    
    page_type = models.CharField(
        max_length=20,
        choices=PAGE_TYPES,
        default='website',
        help_text="Page type for structured data"
    )
    
    # SEO Meta Tags
    title = models.CharField(
        max_length=60,
        blank=True,
        help_text="Page title (max 60 characters, leave blank to use default)"
    )
    
    description = models.TextField(
        max_length=160,
        blank=True,
        help_text="Meta description (max 160 characters, leave blank to use default)"
    )
    
    keywords = models.TextField(
        blank=True,
        help_text="Page-specific keywords (comma-separated, leave blank to use default)"
    )
    
    # Open Graph
    og_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="Open Graph title (leave blank to use page title)"
    )
    
    og_description = models.TextField(
        max_length=160,
        blank=True,
        help_text="Open Graph description (leave blank to use meta description)"
    )
    
    og_image = models.ImageField(
        upload_to='seo/og_images/',
        blank=True,
        null=True,
        help_text="Open Graph image (1200x630px recommended)"
    )
    
    og_image_alt = models.CharField(
        max_length=100,
        blank=True,
        help_text="Alt text for Open Graph image"
    )
    
    # Twitter Card
    twitter_card_type = models.CharField(
        max_length=20,
        choices=[
            ('summary', 'Summary'),
            ('summary_large_image', 'Summary Large Image'),
            ('app', 'App'),
            ('player', 'Player'),
        ],
        default='summary_large_image',
        help_text="Twitter Card type"
    )
    
    # Advanced SEO
    canonical_url = models.URLField(
        blank=True,
        help_text="Canonical URL (leave blank to use current page URL)"
    )
    
    robots = models.CharField(
        max_length=50,
        default='index, follow',
        help_text="Robots meta tag content"
    )
    
    # Schema.org Data
    schema_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Schema.org type (e.g., 'LocalBusiness', 'Article')"
    )
    
    # Article-specific fields
    article_section = models.CharField(
        max_length=50,
        blank=True,
        help_text="Article section (for blog posts)"
    )
    
    published_time = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Article published time"
    )
    
    modified_time = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Article modified time"
    )
    
    # Product-specific fields
    product_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Product price (for tour packages)"
    )
    
    product_currency = models.CharField(
        max_length=3,
        default='INR',
        help_text="Product currency code"
    )
    
    product_availability = models.CharField(
        max_length=50,
        default='https://schema.org/InStock',
        help_text="Product availability status"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Enable SEO overrides for this page"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Page SEO"
        verbose_name_plural = "Page SEO Overrides"
        ordering = ['page_path']
    
    def __str__(self):
        return f"{self.page_name} ({self.page_path})"
    
    def get_effective_title(self):
        """Get the effective title (custom or default)"""
        return self.title or self.page_name
    
    def get_effective_description(self):
        """Get the effective description (custom or default)"""
        if self.description:
            return self.description
        
        # Generate default description based on page type
        if self.page_type == 'tour':
            return f"Book {self.page_name} tour package with Ritham Tours & Travels. Best prices and excellent service guaranteed."
        elif self.page_type == 'blog':
            return f"Read about {self.page_name} - travel tips and guides from Ritham Tours & Travels."
        else:
            return f"{self.page_name} - Ritham Tours & Travels"
    
    def get_effective_keywords(self):
        """Get the effective keywords (custom or default)"""
        if self.keywords:
            return self.keywords
        
        # Generate default keywords based on page type
        base_keywords = "ritham tours, travel, tours"
        if self.page_type == 'tour':
            return f"{base_keywords}, tour package, {self.page_name.lower()}"
        elif self.page_type == 'blog':
            return f"{base_keywords}, travel blog, travel tips"
        else:
            return base_keywords
    
    @classmethod
    def get_page_seo(cls, path):
        """Get SEO data for a specific page path"""
        try:
            return cls.objects.filter(page_path=path, is_active=True).first()
        except cls.DoesNotExist:
            return None


class SEORedirect(models.Model):
    """
    SEO Redirects for URL management
    Handles 301 redirects for SEO purposes
    """
    
    old_path = models.CharField(
        max_length=255,
        unique=True,
        help_text="Old URL path to redirect from"
    )
    
    new_path = models.CharField(
        max_length=255,
        help_text="New URL path to redirect to"
    )
    
    redirect_type = models.CharField(
        max_length=3,
        choices=[
            ('301', 'Permanent (301)'),
            ('302', 'Temporary (302)'),
        ],
        default='301',
        help_text="Type of redirect"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Enable this redirect"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "SEO Redirect"
        verbose_name_plural = "SEO Redirects"
        ordering = ['old_path']
    
    def __str__(self):
        return f"{self.old_path} → {self.new_path} ({self.redirect_type})"