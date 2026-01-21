"""
Django Management Command for SEO Validation
Validates SEO implementation across all pages
"""

from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from django.urls import reverse, NoReverseMatch
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Context, Template
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin


class Command(BaseCommand):
    help = 'Validate SEO implementation across all pages'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='Validate specific URL path (e.g., /about/)',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['text', 'json'],
            default='text',
            help='Output format',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed validation results',
        )
    
    def handle(self, *args, **options):
        self.client = Client()
        self.verbose = options['verbose']
        self.format = options['format']
        
        if options['url']:
            results = self.validate_url(options['url'])
            self.output_results([results])
        else:
            results = self.validate_all_pages()
            self.output_results(results)
    
    def validate_url(self, url_path):
        """Validate SEO for a specific URL"""
        try:
            response = self.client.get(url_path)
            if response.status_code != 200:
                return {
                    'url': url_path,
                    'status': 'error',
                    'message': f'HTTP {response.status_code}',
                    'issues': []
                }
            
            return self.analyze_response(url_path, response)
        
        except Exception as e:
            return {
                'url': url_path,
                'status': 'error',
                'message': str(e),
                'issues': []
            }
    
    def validate_all_pages(self):
        """Validate SEO for all known pages"""
        urls_to_test = [
            '/',
            '/about/',
            '/contact/',
            '/tours/',
            '/blog/',
            '/booking-status/',
            '/testimonials/',
        ]
        
        results = []
        for url in urls_to_test:
            result = self.validate_url(url)
            results.append(result)
        
        return results
    
    def analyze_response(self, url_path, response):
        """Analyze HTTP response for SEO issues"""
        content = response.content.decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        
        issues = []
        warnings = []
        
        # Check title tag
        title_tag = soup.find('title')
        if not title_tag:
            issues.append("Missing <title> tag")
        elif not title_tag.get_text().strip():
            issues.append("Empty <title> tag")
        elif len(title_tag.get_text()) > 60:
            warnings.append(f"Title too long ({len(title_tag.get_text())} chars, recommended: ≤60)")
        
        # Check meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            issues.append("Missing meta description")
        elif not meta_desc.get('content', '').strip():
            issues.append("Empty meta description")
        elif len(meta_desc.get('content', '')) > 160:
            warnings.append(f"Meta description too long ({len(meta_desc.get('content', ''))} chars, recommended: ≤160)")
        
        # Check meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if not meta_keywords:
            warnings.append("Missing meta keywords")
        
        # Check canonical URL
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if not canonical:
            warnings.append("Missing canonical URL")
        
        # Check Open Graph tags
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        og_description = soup.find('meta', attrs={'property': 'og:description'})
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        og_url = soup.find('meta', attrs={'property': 'og:url'})
        
        if not og_title:
            issues.append("Missing Open Graph title")
        if not og_description:
            issues.append("Missing Open Graph description")
        if not og_image:
            issues.append("Missing Open Graph image")
        if not og_url:
            issues.append("Missing Open Graph URL")
        
        # Check Twitter Card tags
        twitter_card = soup.find('meta', attrs={'name': 'twitter:card'})
        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
        twitter_description = soup.find('meta', attrs={'name': 'twitter:description'})
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        
        if not twitter_card:
            warnings.append("Missing Twitter Card type")
        if not twitter_title:
            warnings.append("Missing Twitter Card title")
        if not twitter_description:
            warnings.append("Missing Twitter Card description")
        if not twitter_image:
            warnings.append("Missing Twitter Card image")
        
        # Check structured data
        json_ld_scripts = soup.find_all('script', attrs={'type': 'application/ld+json'})
        if not json_ld_scripts:
            warnings.append("Missing structured data (JSON-LD)")
        else:
            # Validate JSON-LD syntax
            for script in json_ld_scripts:
                try:
                    json.loads(script.get_text())
                except json.JSONDecodeError:
                    issues.append("Invalid JSON-LD structured data")
        
        # Check robots meta tag
        robots = soup.find('meta', attrs={'name': 'robots'})
        if not robots:
            warnings.append("Missing robots meta tag")
        
        # Check viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            issues.append("Missing viewport meta tag")
        
        # Check for duplicate meta tags
        meta_tags = soup.find_all('meta')
        seen_names = {}
        seen_properties = {}
        
        for meta in meta_tags:
            name = meta.get('name')
            prop = meta.get('property')
            
            if name:
                if name in seen_names:
                    warnings.append(f"Duplicate meta name='{name}'")
                seen_names[name] = True
            
            if prop:
                if prop in seen_properties:
                    warnings.append(f"Duplicate meta property='{prop}'")
                seen_properties[prop] = True
        
        # Check heading structure
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        h1_count = len(soup.find_all('h1'))
        
        if h1_count == 0:
            issues.append("Missing H1 tag")
        elif h1_count > 1:
            warnings.append(f"Multiple H1 tags found ({h1_count})")
        
        # Check image alt attributes
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        if images_without_alt:
            warnings.append(f"{len(images_without_alt)} images missing alt attributes")
        
        # Determine overall status
        if issues:
            status = 'error'
        elif warnings:
            status = 'warning'
        else:
            status = 'success'
        
        return {
            'url': url_path,
            'status': status,
            'title': title_tag.get_text() if title_tag else None,
            'meta_description': meta_desc.get('content') if meta_desc else None,
            'issues': issues,
            'warnings': warnings,
            'stats': {
                'title_length': len(title_tag.get_text()) if title_tag else 0,
                'description_length': len(meta_desc.get('content')) if meta_desc else 0,
                'h1_count': h1_count,
                'total_headings': len(headings),
                'images_count': len(images),
                'images_without_alt': len(images_without_alt),
                'json_ld_count': len(json_ld_scripts),
            }
        }
    
    def output_results(self, results):
        """Output validation results"""
        if self.format == 'json':
            self.stdout.write(json.dumps(results, indent=2))
            return
        
        # Text format output
        total_pages = len(results)
        success_count = len([r for r in results if r['status'] == 'success'])
        warning_count = len([r for r in results if r['status'] == 'warning'])
        error_count = len([r for r in results if r['status'] == 'error'])
        
        self.stdout.write(self.style.SUCCESS(f"\n=== SEO Validation Report ==="))
        self.stdout.write(f"Total pages: {total_pages}")
        self.stdout.write(self.style.SUCCESS(f"✓ Success: {success_count}"))
        self.stdout.write(self.style.WARNING(f"⚠ Warnings: {warning_count}"))
        self.stdout.write(self.style.ERROR(f"✗ Errors: {error_count}"))
        
        for result in results:
            self.output_page_result(result)
        
        # Summary
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"\n❌ SEO validation failed with {error_count} errors"))
        elif warning_count > 0:
            self.stdout.write(self.style.WARNING(f"\n⚠️  SEO validation completed with {warning_count} warnings"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\n✅ All pages passed SEO validation!"))
    
    def output_page_result(self, result):
        """Output result for a single page"""
        url = result['url']
        status = result['status']
        
        if status == 'success':
            icon = "✓"
            style = self.style.SUCCESS
        elif status == 'warning':
            icon = "⚠"
            style = self.style.WARNING
        else:
            icon = "✗"
            style = self.style.ERROR
        
        self.stdout.write(f"\n{style(icon)} {url}")
        
        if result.get('title'):
            self.stdout.write(f"  Title: {result['title'][:80]}{'...' if len(result['title']) > 80 else ''}")
        
        if self.verbose and result.get('stats'):
            stats = result['stats']
            self.stdout.write(f"  Stats: Title({stats['title_length']}), Desc({stats['description_length']}), H1({stats['h1_count']}), JSON-LD({stats['json_ld_count']})")
        
        # Show issues
        for issue in result.get('issues', []):
            self.stdout.write(self.style.ERROR(f"    ✗ {issue}"))
        
        # Show warnings (only in verbose mode or if no issues)
        if self.verbose or not result.get('issues'):
            for warning in result.get('warnings', []):
                self.stdout.write(self.style.WARNING(f"    ⚠ {warning}"))