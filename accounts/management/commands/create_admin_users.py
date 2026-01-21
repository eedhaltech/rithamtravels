from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import TravelsProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create admin users for travels dashboard'

    def handle(self, *args, **options):
        admin_users = [
            {
                'email': 'admin@rithamtravels.in',
                'username': 'admin_ritham',
                'first_name': 'Admin',
                'last_name': 'Ritham',
                'password': 'jan@2026'
            },
            {
                'email': 'info@rithamtravels.in',
                'username': 'info_ritham',
                'first_name': 'Info',
                'last_name': 'Ritham',
                'password': 'jan@2026'
            }
        ]

        for user_data in admin_users:
            email = user_data['email']
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'User with email {email} already exists. Updating password...')
                )
                user = User.objects.get(email=email)
                user.set_password(user_data['password'])
                user.user_type = 'travels'
                user.is_staff = True
                user.is_active = True
                user.save()
            else:
                # Create new user
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=email,
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    user_type='travels',
                    is_staff=True,
                    is_active=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created admin user: {email}')
                )

            # Create or update travels profile
            travels_profile, created = TravelsProfile.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': 'Ritham Tours & Travels',
                    'business_address': 'Coimbatore, Tamil Nadu, India'
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created travels profile for: {email}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Travels profile already exists for: {email}')
                )

        self.stdout.write(
            self.style.SUCCESS('\nAdmin users setup completed!')
        )
        self.stdout.write('Login credentials:')
        for user_data in admin_users:
            self.stdout.write(f'  Email: {user_data["email"]}')
            self.stdout.write(f'  Password: {user_data["password"]}')
            self.stdout.write('')