"""
SEO View Mixins for Ritham Tours & Travels
Provides standardized SEO context for views
"""

from django.conf import settings
from django.utils import timezone


class SEOMixin:
    """
    Mixin to add SEO context to views
    Provides standardized SEO data generation for different page types
    """
    
    # Default SEO values - can be overridden in views
    seo_title = ""
    seo_description = ""
    seo_keywords = ""
    seo_page_type = "website"
    seo_og_image = None
    seo_canonical_url = None
    seo_robots = "index, follow"
    
    def get_seo_title(self):
        """Get the SEO title for the page"""
        return self.seo_title
    
    def get_seo_description(self):
        """Get the SEO description for the page"""
        return self.seo_description
    
    def get_seo_keywords(self):
        """Get the SEO keywords for the page"""
        return self.seo_keywords
    
    def get_seo_page_type(self):
        """Get the page type for Open Graph"""
        return self.seo_page_type
    
    def get_seo_og_image(self):
        """Get the Open Graph image URL"""
        return self.seo_og_image
    
    def get_seo_canonical_url(self):
        """Get the canonical URL for the page"""
        if self.seo_canonical_url:
            return self.seo_canonical_url
        return self.request.get_full_path()
    
    def get_seo_robots(self):
        """Get the robots meta tag content"""
        return self.seo_robots
    
    def get_seo_context(self):
        """
        Generate complete SEO context for the template
        Override this method for complex SEO data generation
        """
        return {
            'title': self.get_seo_title(),
            'description': self.get_seo_description(),
            'keywords': self.get_seo_keywords(),
            'page_type': self.get_seo_page_type(),
            'og_image': self.get_seo_og_image(),
            'canonical_url': self.get_seo_canonical_url(),
            'robots': self.get_seo_robots(),
        }
    
    def get_context_data(self, **kwargs):
        """Add SEO context to template context"""
        context = super().get_context_data(**kwargs)
        context['seo'] = self.get_seo_context()
        return context


class HomeSEOMixin(SEOMixin):
    """SEO mixin specifically for home page"""
    
    seo_title = "Ritham Tours & Travels - Your Trusted Travel Partner"
    seo_description = "Discover India with Ritham Tours & Travels. Professional travel agency offering customized tour packages, reliable cab bookings, and complete travel solutions. Book your perfect journey today!"
    seo_keywords = "tours, travel, cab booking, tour packages, ritham tours, travel agency, india tours, coimbatore travel, tamil nadu tours, travel planning"
    seo_page_type = "website"
    seo_canonical_url = "/"


class BlogSEOMixin(SEOMixin):
    """SEO mixin for blog pages"""
    
    seo_page_type = "article"
    seo_keywords = "travel blog, tour guides, travel tips, india travel, ritham tours blog"
    
    def get_seo_context(self):
        context = super().get_seo_context()
        # Add article-specific context
        context.update({
            'article_section': 'Travel',
            'published_time': getattr(self.object, 'created_at', None) if hasattr(self, 'object') else None,
            'modified_time': getattr(self.object, 'updated_at', None) if hasattr(self, 'object') else None,
        })
        return context


class TourSEOMixin(SEOMixin):
    """SEO mixin for tour package pages"""
    
    seo_page_type = "product"
    seo_keywords = "tour package, travel package, india tour, customized tour, ritham tours"
    
    def get_seo_context(self):
        context = super().get_seo_context()
        # Add product-specific context
        if hasattr(self, 'object') and self.object:
            context.update({
                'product_price': getattr(self.object, 'price', None),
                'product_availability': 'https://schema.org/InStock',
            })
        return context


class ContactSEOMixin(SEOMixin):
    """SEO mixin for contact page"""
    
    seo_title = "Contact Ritham Tours & Travels - Get in Touch"
    seo_description = "Contact Ritham Tours & Travels for travel bookings, tour packages, and travel inquiries. Available 24/7 for your travel needs. Call +91 97871 10763 or email us."
    seo_keywords = "contact ritham tours, travel booking contact, tour package inquiry, travel agency contact, coimbatore travel contact"
    seo_page_type = "contact"
    seo_canonical_url = "/contact/"


class BookingSEOMixin(SEOMixin):
    """SEO mixin for booking pages"""
    
    seo_title = "Book Your Travel - Ritham Tours & Travels"
    seo_description = "Book your perfect travel experience with Ritham Tours & Travels. Easy online booking for tour packages, cab services, and customized travel solutions."
    seo_keywords = "book travel, online booking, tour booking, cab booking, travel reservation, ritham tours booking"
    seo_page_type = "website"
    
    def get_seo_robots(self):
        """Booking pages should not be indexed by search engines"""
        return "noindex, nofollow"


class TariffSEOMixin(SEOMixin):
    """SEO mixin for tariff pages"""
    
    seo_title = "Travel Tariff & Pricing - Ritham Tours & Travels"
    seo_description = "Check transparent pricing and tariff for tour packages, cab bookings, and travel services. Competitive rates with no hidden charges. Get instant quotes."
    seo_keywords = "travel tariff, tour package pricing, cab fare, travel cost, ritham tours pricing, transparent pricing"
    seo_page_type = "website"


class TestimonialSEOMixin(SEOMixin):
    """SEO mixin for testimonials page"""
    
    seo_title = "Customer Testimonials - Ritham Tours & Travels"
    seo_description = "Read genuine customer reviews and testimonials about Ritham Tours & Travels. Discover why travelers trust us for their perfect journey experiences."
    seo_keywords = "customer reviews, testimonials, travel reviews, ritham tours reviews, customer feedback, travel experiences"
    seo_page_type = "website"