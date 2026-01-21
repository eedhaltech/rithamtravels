"""
Django Management Command to extract HTML head content
"""

from django.core.management.base import BaseCommand
from django.test import Client
from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = 'Extract HTML head content for SEO verification'
    
    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='URL path to extract head from')
    
    def handle(self, *args, **options):
        client = Client()
        url = options['url']
        
        try:
            response = client.get(url)
            if response.status_code != 200:
                self.stdout.write(f"Error: HTTP {response.status_code}")
                return
            
            content = response.content.decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            
            head = soup.find('head')
            if head:
                # Pretty print the head content
                self.stdout.write(str(head.prettify()))
            else:
                self.stdout.write("No <head> tag found")
                
        except Exception as e:
            self.stdout.write(f"Error: {str(e)}")