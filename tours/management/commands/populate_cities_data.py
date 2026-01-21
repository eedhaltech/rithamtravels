from django.core.management.base import BaseCommand
from tours.models import City, LocalArea


class Command(BaseCommand):
    help = 'Populate cities with comprehensive data including local areas and sightseeing information'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting cities data population...'))
        
        # Define comprehensive city data
        cities_data = {
            # Existing cities with enhanced data
            'Coimbatore': {
                'tourist_places': 'Marudamalai Temple, VOC Park, Brookefields Mall, Gass Forest Museum, Perur Pateeswarar Temple, Black Thunder, Kovai Kutralam Falls, Siruvani Waterfalls, Monkey Falls, Velliangiri Hills',
                'sightseeing_kilometers': 50.0,
                'local_areas': ['RS Puram', 'Gandhipuram', 'Saibaba Colony', 'Singanallur', 'Sitra', 'Peelamedu', 'Vadavalli', 'Kuniyamuthur', 'Thudiyalur', 'Kalapatti']
            },
            'Ooty': {
                'tourist_places': 'Botanical Gardens, Ooty Lake, Doddabetta Peak, Rose Garden, Tea Gardens, Nilgiri Mountain Railway, Government Museum, Pykara Falls, Emerald Lake, Avalanche Lake',
                'sightseeing_kilometers': 40.0,
                'local_areas': ['Charring Cross', 'Commercial Street', 'Upper Bazaar', 'Lower Bazaar', 'Fernhill', 'Coonoor Road', 'Mysore Road', 'Wellington']
            },
            'Kodaikanal': {
                'tourist_places': 'Kodai Lake, Bryant Park, Coakers Walk, Pillar Rocks, Silver Cascade Falls, Bear Shola Falls, Kurinji Andavar Temple, Pine Forest, Guna Caves, Dolphin Nose',
                'sightseeing_kilometers': 35.0,
                'local_areas': ['Anna Salai', 'Observatory Road', 'Lake Road', 'Coakers Walk', 'Seven Roads Junction', 'Bus Stand Area', 'Hospital Road', 'Bazaar Road']
            },
            'Munnar': {
                'tourist_places': 'Tea Museum, Mattupetty Dam, Echo Point, Kundala Lake, Top Station, Eravikulam National Park, Rose Gardens, Anamudi Peak, Chinnar Wildlife Sanctuary, Attukal Waterfalls',
                'sightseeing_kilometers': 45.0,
                'local_areas': ['Old Munnar', 'New Munnar', 'Mattupetty', 'Kundala', 'Top Station Road', 'Pallivasal', 'Chinnakanal', 'Suryanelli']
            },
            'Yercaud': {
                'tourist_places': 'Yercaud Lake, Lady\'s Seat, Gent\'s Seat, Killiyur Falls, Pagoda Point, Servarayan Temple, Rose Garden, Bear\'s Cave, Botanical Garden, Anna Park',
                'sightseeing_kilometers': 25.0,
                'local_areas': ['Lake Area', 'Main Bazaar', 'Salem-Yercaud Road', 'Montfort School Road', 'Temple Road', 'Grange', 'Norton Bungalow']
            },
            'Chennai': {
                'tourist_places': 'Marina Beach, Fort St. George, Kapaleeshwarar Temple, Government Museum, Santhome Cathedral, Elliot\'s Beach, Mahabalipuram, Dakshinachitra, Phoenix MarketCity, Express Avenue Mall',
                'sightseeing_kilometers': 60.0,
                'local_areas': ['Adyar', 'Marina Beach', 'T. Nagar', 'Anna Nagar', 'Velachery', 'OMR', 'Egmore', 'Mylapore', 'Nungambakkam', 'Guindy']
            },
            'Madurai': {
                'tourist_places': 'Meenakshi Amman Temple, Thirumalai Nayakkar Palace, Gandhi Memorial Museum, Alagar Hills, Pazhamudhir Solai, Samanar Hills, Vandiyur Mariamman Teppakulam, Koodal Azhagar Temple',
                'sightseeing_kilometers': 35.0,
                'local_areas': ['Meenakshi Temple Area', 'Anna Nagar', 'K.K. Nagar', 'Goripalayam', 'Tallakulam', 'Sellur', 'Vilangudi', 'Thiruparankundram']
            },
            'Mysore': {
                'tourist_places': 'Mysore Palace, Chamundi Hills, Brindavan Gardens, St. Philomena\'s Church, Jaganmohan Palace, Karanji Lake, Mysore Zoo, Lalitha Mahal, Railway Museum, Devaraja Market',
                'sightseeing_kilometers': 40.0,
                'local_areas': ['Sayyaji Rao Road', 'Ashoka Road', 'JLB Road', 'Nazarbad', 'Chamundipuram', 'Kuvempunagar', 'Vijayanagar', 'Hebbal']
            },
            'Kanyakumari': {
                'tourist_places': 'Vivekananda Rock Memorial, Thiruvalluvar Statue, Kanyakumari Beach, Bhagavathy Amman Temple, Gandhi Memorial, Sunset Point, Wax Museum, Padmanabhapuram Palace',
                'sightseeing_kilometers': 20.0,
                'local_areas': ['Beach Road', 'Main Bazaar', 'Sannathi Street', 'North Car Street', 'South Car Street', 'Kovalam Road']
            },
            'Rameshwaram': {
                'tourist_places': 'Ramanathaswamy Temple, Dhanushkodi, Adam\'s Bridge, Agni Theertham, Gandhamadhana Parvatham, Five-faced Hanuman Temple, Jada Tirtham, Kothandaramaswamy Temple',
                'sightseeing_kilometers': 30.0,
                'local_areas': ['Temple Area', 'Bus Stand Road', 'Dhanushkodi Road', 'North Street', 'South Street', 'East Car Street', 'West Car Street']
            },
            'Tanjore': {
                'tourist_places': 'Brihadeeswarar Temple, Tanjore Palace, Saraswathi Mahal Library, Art Gallery, Schwartz Church, Sivaganga Park, Sangeetha Mahal, Royal Museum',
                'sightseeing_kilometers': 25.0,
                'local_areas': ['Big Temple Area', 'Palace Road', 'Gandhi Road', 'Trichy Road', 'Medical College Road', 'Anna Salai', 'Kutchery Road']
            },
            'Ariyalur': {
                'tourist_places': 'Gangaikonda Cholapuram, Darasuram Temple, Airavatesvara Temple, Fossil Park, Ariyalur Museum, Sendurai Lake, Jayankondam, Kumbakonam nearby temples',
                'sightseeing_kilometers': 40.0,
                'local_areas': ['Main Bazaar', 'Bus Stand Area', 'Collectorate Road', 'Jayankondam Road', 'Sendurai Road', 'Udayarpalayam Road']
            },
            
            # New cities to add
            'Salem': {
                'tourist_places': 'Mettur Dam, Kiliyur Falls, Shevaroy Hills, Kottai Mariamman Temple, Salem Steel Plant, Sugavaneswarar Temple, Sankagiri Fort, Botanical Garden, Anna Park, Kurumbapatti Zoological Park',
                'sightseeing_kilometers': 45.0,
                'local_areas': ['Junction', 'Fairlands', 'Five Roads', 'Ammapet', 'Suramangalam', 'Hasthampatti', 'Kondalampatti', 'Shevapet']
            },
            'Trichy': {
                'tourist_places': 'Rock Fort Temple, Srirangam Temple, Jambukeswarar Temple, Kallanai Dam, Mukkombu, St. Joseph Church, Government Museum, Puliyancholai Falls, Samayapuram Temple',
                'sightseeing_kilometers': 50.0,
                'local_areas': ['Cantonment', 'Thillai Nagar', 'K.K. Nagar', 'Srirangam', 'Golden Rock', 'Puthur', 'Woraiyur', 'Manachanallur Road']
            },
            'Tirunelveli': {
                'tourist_places': 'Nellaiappar Temple, Courtallam Falls, Manimuthar Falls, Agasthiyar Falls, Kalakkad Wildlife Sanctuary, Krishnapuram Venkatachalapathy Temple, Sankaran Kovil, Tenkasi',
                'sightseeing_kilometers': 60.0,
                'local_areas': ['Town Area', 'Junction', 'Palayamkottai', 'Melapalayam', 'Vannarpet', 'High Ground', 'Reddiarpatti', 'Tirunelveli Junction']
            },
            'Coorg': {
                'tourist_places': 'Abbey Falls, Raja\'s Seat, Omkareshwara Temple, Dubare Elephant Camp, Talakaveri, Bhagamandala, Iruppu Falls, Namdroling Monastery, Coffee Plantations, Mandalpatti',
                'sightseeing_kilometers': 55.0,
                'local_areas': ['Madikeri Town', 'Raja\'s Seat Road', 'Abbey Falls Road', 'Bhagamandala Road', 'Talakaveri Road', 'Kushalnagar', 'Somwarpet', 'Virajpet']
            },
            'Wayanad': {
                'tourist_places': 'Chembra Peak, Soochipara Falls, Edakkal Caves, Banasura Sagar Dam, Pookode Lake, Thirunelli Temple, Kuruva Island, Muthanga Wildlife Sanctuary, Lakkidi View Point',
                'sightseeing_kilometers': 70.0,
                'local_areas': ['Kalpetta', 'Sultan Bathery', 'Mananthavady', 'Vythiri', 'Meppadi', 'Ambalavayal', 'Pulpally', 'Panamaram']
            },
            'Pondicherry': {
                'tourist_places': 'French Quarter, Auroville, Aurobindo Ashram, Paradise Beach, Promenade Beach, Bharathi Park, Pondicherry Museum, Sacred Heart Church, Manakula Vinayagar Temple',
                'sightseeing_kilometers': 30.0,
                'local_areas': ['White Town', 'French Quarter', 'Tamil Quarter', 'Boulevard', 'Mission Street', 'Nehru Street', 'Goubert Avenue', 'Auroville Road']
            },
            'Vellore': {
                'tourist_places': 'Vellore Fort, Golden Temple, Jalakandeswarar Temple, Government Museum, Amirthi Zoological Park, Yelagiri Hills, Jalagamparai Falls, Ratnagiri Murugan Temple',
                'sightseeing_kilometers': 40.0,
                'local_areas': ['Fort Area', 'Katpadi', 'Bagayam', 'Saidapet', 'Kosapet', 'Officer Line', 'Thottapalayam', 'CMC Campus']
            },
            'Thanjavur': {
                'tourist_places': 'Brihadeeswarar Temple, Thanjavur Palace, Saraswathi Mahal Library, Art Gallery, Schwartz Church, Sivaganga Park, Sangeetha Mahal, Royal Museum, Punnainallur Mariamman Temple',
                'sightseeing_kilometers': 30.0,
                'local_areas': ['Big Temple Area', 'Palace Road', 'Gandhi Road', 'Trichy Road', 'Medical College Road', 'Anna Salai', 'Kutchery Road', 'East Main Street']
            },
            'Kumbakonam': {
                'tourist_places': 'Adi Kumbeswarar Temple, Sarangapani Temple, Mahamaham Tank, Nageswaran Temple, Ramaswamy Temple, Chakrapani Temple, Uppiliappan Temple, Darasuram Temple',
                'sightseeing_kilometers': 25.0,
                'local_areas': ['Big Bazaar Street', 'TSR Big Street', 'Sarangapani Street', 'Mahamaham Tank Area', 'Nageswaran Koil Street', 'Ayyavoo Naidu Street', 'Kumbakonam Head Post Office']
            },
            'Tirupur': {
                'tourist_places': 'Tirupur Kumaran Memorial, Noyyal River, Avinashi Temple, Udumalpet, Dharapuram, Kangeyam, Textile Showrooms, Thirumoorthy Hills, Amaravathi Dam',
                'sightseeing_kilometers': 35.0,
                'local_areas': ['Kumaran Road', 'Avinashi Road', 'Palladam Road', 'Dharapuram Road', 'Kangeyam Road', 'Udumalpet Road', 'Textile Area', 'SIDCO Industrial Estate']
            }
        }
        
        # Process each city
        for city_name, city_data in cities_data.items():
            try:
                # Get or create city
                city, created = City.objects.get_or_create(
                    name=city_name,
                    defaults={
                        'tourist_places': city_data['tourist_places'],
                        'sightseeing_kilometers': city_data['sightseeing_kilometers'],
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Created new city: {city_name}'))
                else:
                    # Update existing city if it has missing data
                    updated = False
                    if not city.tourist_places:
                        city.tourist_places = city_data['tourist_places']
                        updated = True
                    if city.sightseeing_kilometers == 0:
                        city.sightseeing_kilometers = city_data['sightseeing_kilometers']
                        updated = True
                    
                    if updated:
                        city.save()
                        self.stdout.write(self.style.WARNING(f'✓ Updated existing city: {city_name}'))
                    else:
                        self.stdout.write(f'  City {city_name} already has complete data')
                
                # Add local areas
                existing_areas = set(city.local_areas.values_list('name', flat=True))
                new_areas = set(city_data['local_areas']) - existing_areas
                
                for area_name in new_areas:
                    LocalArea.objects.get_or_create(
                        city=city,
                        name=area_name
                    )
                
                if new_areas:
                    self.stdout.write(f'  ✓ Added {len(new_areas)} local areas to {city_name}')
                
                # Show summary for this city
                total_areas = city.local_areas.count()
                self.stdout.write(f'  📍 {city_name}: {len(city_data["tourist_places"].split(", "))} attractions, {total_areas} local areas, {city_data["sightseeing_kilometers"]} km')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error processing {city_name}: {str(e)}'))
        
        # Final summary
        total_cities = City.objects.count()
        total_areas = LocalArea.objects.count()
        cities_with_sightseeing = City.objects.exclude(tourist_places__isnull=True).exclude(tourist_places='').count()
        
        self.stdout.write(self.style.SUCCESS('\n=== FINAL SUMMARY ==='))
        self.stdout.write(f'Total Cities: {total_cities}')
        self.stdout.write(f'Total Local Areas: {total_areas}')
        self.stdout.write(f'Cities with Sightseeing Data: {cities_with_sightseeing}/{total_cities}')
        self.stdout.write(self.style.SUCCESS('Cities data population completed successfully!'))