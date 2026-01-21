from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog.models import BlogPost

User = get_user_model()


class Command(BaseCommand):
    help = 'Fix blog posts without authors by assigning them to admin user'

    def handle(self, *args, **options):
        # Get or create an admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'rithamtravels@gmail.com',
                'first_name': 'Admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created admin user: {admin_user.username}')
            )
        
        # Update blog posts without authors
        posts_without_author = BlogPost.objects.filter(author__isnull=True)
        count = posts_without_author.count()
        
        if count > 0:
            posts_without_author.update(author=admin_user)
            self.stdout.write(
                self.style.SUCCESS(f'Updated {count} blog posts with admin author')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('All blog posts already have authors')
            )
        
        # Show summary
        total_posts = BlogPost.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'Total blog posts: {total_posts}')
        )