"""
SEO Template Tags for Ritham Tours & Travels
Provides template tags for generating SEO meta content
"""

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.conf import settings
import re

register = template.Library()

@register.simple_tag
def seo_title(page_title, site_name=None):
    """Generate SEO-optimized page title"""
    if not site_name:
        site_name = getattr(settings, 'COMPANY_NAME', 'Ritham Tours & Travels')
    
    if not page_title:
        return site_name
    
    # Ensure title is within SEO limits (50-60 characters)
    full_title = f"{page_title} | {site_name}"
    if len(full_title) > 60:
        # Truncate page title to fit within limit
        max_page_title = 60 - len(f" | {site_name}")
        if max_page_title > 0:
            page_title = page_title[:max_page_title-3] + "..."
            full_title = f"{page_title} | {site_name}"
        else:
            full_title = site_name
    
    return escape(full_title)

@register.simple_tag
def seo_description(description, max_length=160):
    """Generate SEO-optimized meta description"""
    if not description:
        return "Ritham Tours & Travels - Your trusted travel partner for tours, cab bookings, and travel packages across India. Book now for the best travel experience."
    
    # Clean and truncate description
    description = re.sub(r'\s+', ' ', str(description).strip())
    
    if len(description) > max_length:
        # Find last complete word within limit
        truncated = description[:max_length-3]
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:  # Only truncate at word boundary if it's not too short
            description = description[:last_space] + "..."
        else:
            description = truncated + "..."
    
    return escape(description)

@register.simple_tag
def seo_keywords(keywords):
    """Generate SEO keywords meta tag content"""
    if not keywords:
        return "tours, travel, cab booking, tour packages, ritham tours, travel agency, india tours"
    
    # Clean and format keywords
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(',') if k.strip()]
    
    # Limit to reasonable number of keywords
    keywords = keywords[:10]
    return escape(', '.join(keywords))

@register.simple_tag(takes_context=True)
def absolute_url(context, relative_url):
    """Convert relative URL to absolute URL using production domain"""
    if not relative_url:
        return ""
    
    # Always use production domain from settings
    site_url = getattr(settings, 'SITE_URL', 'https://rithamtravels.in')
    if relative_url.startswith('/'):
        return f"{site_url}{relative_url}"
    else:
        return f"{site_url}/{relative_url}"

@register.simple_tag(takes_context=True)
def og_image_url(context, image_path=None):
    """Generate absolute URL for Open Graph image using production domain"""
    if not image_path:
        # Use default logo
        image_path = '/static/admin/img/logo/logo_ritham.png'
    
    return absolute_url(context, image_path)

@register.simple_tag
def clean_text(text):
    """Clean text for use in meta tags"""
    if not text:
        return ""
    
    # Remove HTML tags and extra whitespace
    text = re.sub(r'<[^>]+>', '', str(text))
    text = re.sub(r'\s+', ' ', text)
    return escape(text.strip())

@register.simple_tag
def page_type_to_og_type(page_type):
    """Convert page type to Open Graph type"""
    type_mapping = {
        'home': 'website',
        'article': 'article',
        'blog': 'article',
        'product': 'product',
        'tour': 'product',
        'booking': 'website',
        'contact': 'website',
    }
    return type_mapping.get(page_type, 'website')

@register.simple_tag(takes_context=True)
def seo_debug(context):
    """Debug SEO context - only works in DEBUG mode"""
    if not getattr(settings, 'DEBUG', False):
        return ""
    
    seo_context = context.get('seo', {})
    site_seo = context.get('site_seo', {})
    
    debug_info = {
        'seo_context': seo_context,
        'site_seo': site_seo,
    }
    
    import json
    return mark_safe(f"<!-- SEO DEBUG: {json.dumps(debug_info, indent=2)} -->")


@register.simple_tag
def seo_breadcrumbs(*breadcrumbs):
    """Generate breadcrumb data for SEO"""
    breadcrumb_list = []
    for i, (name, url) in enumerate(breadcrumbs):
        breadcrumb_list.append({
            'name': name,
            'url': url,
            'position': i + 1
        })
    return breadcrumb_list