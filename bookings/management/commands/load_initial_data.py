from django.core.management.base import BaseCommand
from vehicles.models import Vehicle
from tours.models import City, Route, LocalArea, SightseeingSpot, TourPackage
from blog.models import BlogPost
from enquiries.models import Testimonial, Promotion


class Command(BaseCommand):
    help = 'Load initial test data for the application'

    def handle(self, *args, **options):
        self.stdout.write('Loading initial data...')
        
        # Create Vehicles
        vehicles_data = [
            {'name': 'Swift Dzire', 'fare_per_km': 16, 'driver_charge_per_day': 500, 'min_km_per_day': 250},
            {'name': 'Etios', 'fare_per_km': 15, 'driver_charge_per_day': 500, 'min_km_per_day': 250},
            {'name': 'Innova', 'fare_per_km': 18, 'driver_charge_per_day': 500, 'min_km_per_day': 250},
            {'name': 'Innova Crysta', 'fare_per_km': 22, 'driver_charge_per_day': 600, 'min_km_per_day': 250},
            {'name': 'Corolla Altis', 'fare_per_km': 28, 'driver_charge_per_day': 600, 'min_km_per_day': 250},
            {'name': 'Innova Hycross', 'fare_per_km': 27, 'driver_charge_per_day': 600, 'min_km_per_day': 250},
            {'name': 'Traveller 12 Seater', 'fare_per_km': 24, 'driver_charge_per_day': 700, 'min_km_per_day': 250, 'max_seats': 12},
            {'name': 'Traveller 17 Seater', 'fare_per_km': 27, 'driver_charge_per_day': 700, 'min_km_per_day': 250, 'max_seats': 17},
        ]
        
        for v_data in vehicles_data:
            Vehicle.objects.get_or_create(name=v_data['name'], defaults=v_data)
        
        self.stdout.write(self.style.SUCCESS('Created vehicles'))
        
        # Create Cities
        cities_data = [
            {'name': 'Coimbatore', 'description': 'Gateway to the Nilgiris'},
            {'name': 'Ooty', 'description': 'Queen of Hill Stations'},
            {'name': 'Kodaikanal', 'description': 'Princess of Hill Stations'},
            {'name': 'Munnar', 'description': 'Tea Capital of South India'},
            {'name': 'Yercaud', 'description': 'Jewel of the South'},
            {'name': 'Madurai', 'description': 'City of Temples'},
            {'name': 'Rameshwaram', 'description': 'Sacred Island'},
            {'name': 'Kanyakumari', 'description': 'Land\'s End'},
            {'name': 'Tanjore', 'description': 'Cultural Capital'},
            {'name': 'Mysore', 'description': 'City of Palaces'},
            {'name': 'Chennai', 'description': 'Gateway to South India'},
        ]
        
        cities = {}
        for c_data in cities_data:
            city, created = City.objects.get_or_create(name=c_data['name'], defaults=c_data)
            cities[c_data['name']] = city
        
        self.stdout.write(self.style.SUCCESS('Created cities'))
        
        # Create Routes
        routes_data = [
            {'from': 'Coimbatore', 'to': 'Ooty', 'distance': 90},
            {'from': 'Coimbatore', 'to': 'Kodaikanal', 'distance': 175},
            {'from': 'Coimbatore', 'to': 'Munnar', 'distance': 160},
            {'from': 'Coimbatore', 'to': 'Madurai', 'distance': 235},
            {'from': 'Coimbatore', 'to': 'Chennai', 'distance': 495},
        ]
        
        for r_data in routes_data:
            Route.objects.get_or_create(
                from_city=cities[r_data['from']],
                to_city=cities[r_data['to']],
                defaults={'distance': r_data['distance']}
            )
        
        self.stdout.write(self.style.SUCCESS('Created routes'))
        
        # Create Local Areas
        coimbatore = cities.get('Coimbatore')
        if coimbatore:
            areas = ['RS Puram', 'Gandhipuram', 'Saibaba Colony', 'Singanallur', 'Sitra']
            for area in areas:
                LocalArea.objects.get_or_create(city=coimbatore, name=area)
        
        self.stdout.write(self.style.SUCCESS('Created local areas'))
        
        # Create Sightseeing Spots
        sightseeing_data = [
            {'city': 'Ooty', 'spots': ['Botanical Gardens', 'Rose Garden', 'Ooty Lake', 'Doddabetta Peak']},
            {'city': 'Kodaikanal', 'spots': ['Kodaikanal Lake', 'Coaker\'s Walk', 'Bear Shola Falls', 'Pillar Rocks']},
            {'city': 'Munnar', 'spots': ['Tea Gardens', 'Mattupetty Dam', 'Eravikulam National Park', 'Top Station']},
        ]
        
        for data in sightseeing_data:
            city = cities.get(data['city'])
            if city:
                for spot_name in data['spots']:
                    SightseeingSpot.objects.get_or_create(
                        city=city,
                        name=spot_name,
                        defaults={'description': f'Popular tourist spot in {data["city"]}'}
                    )
        
        self.stdout.write(self.style.SUCCESS('Created sightseeing spots'))
        
        # Create Tour Packages
        packages_data = [
            {'name': 'Ooty Weekend Getaway', 'days': 2, 'price_per_vehicle': 5000},
            {'name': 'Kodaikanal Hill Station Tour', 'days': 3, 'price_per_vehicle': 7500},
            {'name': 'Munnar Tea Estate Tour', 'days': 2, 'price_per_vehicle': 6000},
            {'name': 'South Tamil Nadu Temple Tour', 'days': 5, 'price_per_vehicle': 15000},
            {'name': 'Nilgiris Complete Tour', 'days': 4, 'price_per_vehicle': 12000},
        ]
        
        for p_data in packages_data:
            package, created = TourPackage.objects.get_or_create(
                name=p_data['name'],
                defaults={
                    'days': p_data['days'],
                    'price_per_vehicle': p_data['price_per_vehicle'],
                    'description': f'{p_data["name"]} - {p_data["days"]} days tour package',
                    'is_active': True
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Created tour packages'))
        
        # Create Blog Posts
        blog_posts = [
            {
                'title': 'Top 10 Places to Visit in Ooty',
                'slug': 'top-10-places-visit-ooty',
                'content': 'Ooty, also known as Udhagamandalam, is a beautiful hill station...',
                'excerpt': 'Discover the most beautiful places in Ooty that you must visit.',
            },
            {
                'title': 'Best Time to Visit Kodaikanal',
                'slug': 'best-time-visit-kodaikanal',
                'content': 'Kodaikanal is a year-round destination, but certain months offer better weather...',
                'excerpt': 'Find out the best time to plan your Kodaikanal trip.',
            },
            {
                'title': 'Munnar Tea Gardens: A Complete Guide',
                'slug': 'munnar-tea-gardens-guide',
                'content': 'Munnar is famous for its sprawling tea estates that create a mesmerizing green landscape...',
                'excerpt': 'Everything you need to know about visiting tea gardens in Munnar.',
            },
            {
                'title': 'Road Trip Safety Tips for Hill Stations',
                'slug': 'road-trip-safety-tips',
                'content': 'Planning a road trip to hill stations? Here are essential safety tips...',
                'excerpt': 'Important safety tips for your next hill station road trip.',
            },
            {
                'title': 'Budget-Friendly Tour Packages in South India',
                'slug': 'budget-friendly-tour-packages',
                'content': 'Explore South India without breaking the bank with these affordable packages...',
                'excerpt': 'Discover budget-friendly tour options for exploring South India.',
            },
            {
                'title': 'Family-Friendly Destinations in Tamil Nadu',
                'slug': 'family-friendly-destinations',
                'content': 'Tamil Nadu offers numerous destinations perfect for family vacations...',
                'excerpt': 'Best places in Tamil Nadu to visit with your family.',
            },
        ]
        
        for post_data in blog_posts:
            BlogPost.objects.get_or_create(
                slug=post_data['slug'],
                defaults={
                    'title': post_data['title'],
                    'content': post_data['content'] * 5,  # Longer content
                    'excerpt': post_data['excerpt'],
                    'is_published': True
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Created blog posts'))
        
        # Create Sample Testimonials
        testimonials = [
            {'name': 'Rajesh Kumar', 'rating': 5, 'review': 'Excellent service! The driver was professional and the vehicle was in great condition.'},
            {'name': 'Priya S', 'rating': 5, 'review': 'Had a wonderful trip to Ooty. Everything was well organized.'},
            {'name': 'Suresh Nair', 'rating': 4, 'review': 'Good experience overall. Would recommend for family trips.'},
        ]
        
        for t_data in testimonials:
            Testimonial.objects.get_or_create(
                name=t_data['name'],
                defaults={
                    'rating': t_data['rating'],
                    'review': t_data['review'],
                    'is_approved': True,
                    'is_featured': True
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Created testimonials'))
        
        # Create Promotions
        promotions = [
            {
                'title': 'Early Bird Discount',
                'description': 'Book 30 days in advance and get 15% off on all packages.',
            },
            {
                'title': 'Weekend Special',
                'description': 'Special rates for weekend bookings. Limited time offer!',
            },
        ]
        
        for p_data in promotions:
            Promotion.objects.get_or_create(
                title=p_data['title'],
                defaults={
                    'description': p_data['description'],
                    'is_active': True
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Created promotions'))
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded all initial data!'))

