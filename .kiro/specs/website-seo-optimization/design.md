# Design Document

## Overview

This design implements a comprehensive SEO meta tags system for Ritham Tours & Travels website using Django's template system. The solution provides a centralized, maintainable approach to SEO optimization with dynamic content generation and proper social media integration.

## Architecture

### Template-Based Architecture

The SEO system uses Django's template inheritance and inclusion system:

```
templates/
├── base.html (includes seo_meta.html)
├── seo/
│   ├── seo_meta.html (main meta tags template)
│   ├── og_tags.html (Open Graph specific tags)
│   ├── twitter_tags.html (Twitter Card tags)
│   └── schema_org.html (Structured data)
└── [page_templates] (override meta context)
```

### Context-Driven Design

Each page provides SEO context through Django views:

```python
seo_context = {
    'title': 'Page Title',
    'description': 'Page description',
    'keywords': 'keyword1, keyword2',
    'og_image': 'path/to/image.jpg',
    'page_type': 'website|article|product',
    'schema_data': {...}
}
```

## Components and Interfaces

### 1. SEO Context Processor

**Purpose**: Provides global SEO data to all templates

**Interface**:
```python
def seo_context(request):
    return {
        'site_name': 'Ritham Tours & Travels',
        'site_url': 'https://rithamtravels.in',
        'default_og_image': '/static/admin/img/logo/logo_ritham.png',
        'company_info': {...}
    }
```

### 2. SEO Template Tags

**Purpose**: Generate dynamic meta content

**Interface**:
```python
@register.simple_tag
def seo_title(page_title, site_name):
    return f"{page_title} | {site_name}"

@register.simple_tag  
def seo_description(description, max_length=160):
    return truncate_description(description, max_length)

@register.simple_tag
def absolute_url(relative_url, request):
    return request.build_absolute_uri(relative_url)
```

### 3. Meta Tags Template Component

**Purpose**: Centralized meta tags rendering

**Template Structure**:
```html
<!-- seo/seo_meta.html -->
{% load seo_tags %}

<!-- Basic Meta Tags -->
<title>{% seo_title page_title site_name %}</title>
<meta name="description" content="{% seo_description page_description %}">
<meta name="keywords" content="{{ page_keywords }}">

<!-- Open Graph Tags -->
{% include 'seo/og_tags.html' %}

<!-- Twitter Cards -->
{% include 'seo/twitter_tags.html' %}

<!-- Schema.org -->
{% include 'seo/schema_org.html' %}
```

### 4. View Mixin for SEO

**Purpose**: Standardize SEO context in views

**Interface**:
```python
class SEOMixin:
    seo_title = None
    seo_description = None
    seo_keywords = None
    seo_og_image = None
    
    def get_seo_context(self):
        return {
            'page_title': self.get_seo_title(),
            'page_description': self.get_seo_description(),
            'page_keywords': self.get_seo_keywords(),
            'og_image': self.get_seo_og_image(),
        }
```

## Data Models

### SEO Configuration Model

```python
class SEOConfig(models.Model):
    """Global SEO configuration"""
    site_name = models.CharField(max_length=100)
    default_title = models.CharField(max_length=60)
    default_description = models.TextField(max_length=160)
    default_keywords = models.TextField()
    default_og_image = models.ImageField()
    google_analytics_id = models.CharField(max_length=20, blank=True)
    google_search_console_code = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "SEO Configuration"
```

### Page-Specific SEO Model

```python
class PageSEO(models.Model):
    """Page-specific SEO overrides"""
    url_pattern = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=60)
    description = models.TextField(max_length=160)
    keywords = models.TextField()
    og_image = models.ImageField(blank=True)
    schema_type = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = "Page SEO"
```

## Correctness Properties

Now I'll analyze the acceptance criteria for testability:

<function_calls>
<invoke name="prework">
<parameter name="featureName">website-seo-optimization

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Essential Meta Tags Presence
*For any* rendered page, the HTML output should contain title, description, keywords, viewport, charset, and robots meta tags
**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

### Property 2: Open Graph Tags Completeness
*For any* page rendered, the HTML should include og:title, og:description, og:image, og:type, og:url, og:site_name, and og:locale tags
**Validates: Requirements 2.1, 2.3, 2.4**

### Property 3: Default Logo Usage
*For any* page without a specific OG image, the system should use the company logo as the og:image value
**Validates: Requirements 2.2, 6.1**

### Property 4: Image Override Behavior
*For any* page with a specific image defined, that image should be used instead of the default logo in og:image
**Validates: Requirements 2.5, 6.5**

### Property 5: Twitter Card Tags Presence
*For any* rendered page, the HTML should contain twitter:card, twitter:site, twitter:creator, twitter:title, twitter:description, and twitter:image tags
**Validates: Requirements 3.1, 3.3, 3.4**

### Property 6: Twitter Card Type Consistency
*For any* page rendered, the twitter:card meta tag should have the value "summary_large_image"
**Validates: Requirements 3.2**

### Property 7: Page-Specific Meta Content
*For any* booking page, tour package page, or blog post, the meta tags should contain content specific to that page type and instance
**Validates: Requirements 4.2, 4.3, 4.4**

### Property 8: Schema Markup Presence
*For any* rendered page, the HTML should contain JSON-LD script tags with Organization and LocalBusiness schema markup
**Validates: Requirements 5.1, 5.2**

### Property 9: Conditional Schema Markup
*For any* tour package page, the HTML should include Product schema; for any blog article page, the HTML should include Article schema
**Validates: Requirements 5.3, 5.4**

### Property 10: Absolute URL Format
*For any* og:image or twitter:image URL, it should be an absolute URL containing the full domain
**Validates: Requirements 6.4**

### Property 11: Template Override Functionality
*For any* page that defines custom meta information, those custom values should override the default values in the rendered HTML
**Validates: Requirements 7.2**

### Property 12: Meta Content Length Validation
*For any* generated meta description, it should be between 150-160 characters; for any page title, it should be between 50-60 characters
**Validates: Requirements 8.2, 8.3**

### Property 13: Fallback Value Usage
*For any* page missing meta information, the system should use appropriate fallback values instead of empty or null values
**Validates: Requirements 7.5**

### Property 14: HTML Validation
*For any* rendered page, all meta tags should be properly formatted valid HTML
**Validates: Requirements 8.1**

### Property 15: Tracking Code Integration
*For any* page when analytics is configured, the HTML should contain Google Analytics tracking code and Search Console verification meta tag
**Validates: Requirements 10.1, 10.2**

### Property 16: Canonical URL Presence
*For any* rendered page, the HTML should contain a canonical link tag with the proper URL
**Validates: Requirements 10.5**

## Error Handling

### Meta Tag Validation
- Invalid HTML characters in meta content are escaped
- Overly long titles and descriptions are truncated with ellipsis
- Missing required fields use fallback values
- Invalid image URLs fall back to default logo

### Template Error Handling
- Missing template context gracefully degrades to defaults
- Template tag errors are logged but don't break page rendering
- Invalid schema data is omitted rather than causing errors

### Image Handling
- Non-existent images fall back to default logo
- Invalid image formats are validated before use
- Image dimension validation with fallback to default

## Testing Strategy

### Unit Testing
- Test individual template tags with various inputs
- Validate meta tag generation functions
- Test SEO context processor with different configurations
- Verify image validation and fallback logic

### Property-Based Testing
- Generate random page contexts and verify all required meta tags are present
- Test meta tag content validation with various input lengths and formats
- Verify template override functionality with random override combinations
- Test schema markup generation with different page types

### Integration Testing
- Test complete page rendering with SEO meta tags
- Verify social media sharing preview functionality
- Test search engine crawler compatibility
- Validate structured data markup with Google's testing tools

### Configuration
- Use Django's testing framework for template rendering tests
- Implement property-based tests using Hypothesis library
- Each property test should run minimum 100 iterations
- Tag each test with feature reference: **Feature: website-seo-optimization, Property N: [property_text]**