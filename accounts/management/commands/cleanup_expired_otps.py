from django.core.management.base import BaseCommand
from accounts.services.otp_service import OTPService


class Command(BaseCommand):
    help = 'Clean up expired OTPs and old attempt logs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Delete attempt logs older than this many days (default: 7)',
        )

    def handle(self, *args, **options):
        days = options['days']
        
        # Clean up expired OTPs
        expired_count = OTPService.cleanup_expired_otps()
        self.stdout.write(
            self.style.SUCCESS(f'Cleaned up {expired_count} expired OTPs')
        )
        
        # Clean up old attempt logs
        from django.utils import timezone
        from datetime import timedelta
        from accounts.models import OTPAttemptLog
        
        cutoff_date = timezone.now() - timedelta(days=days)
        old_logs_count = OTPAttemptLog.objects.filter(
            created_at__lt=cutoff_date
        ).count()
        
        OTPAttemptLog.objects.filter(created_at__lt=cutoff_date).delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Cleaned up {old_logs_count} old attempt logs (older than {days} days)')
        )
        
        self.stdout.write(
            self.style.SUCCESS('OTP cleanup completed successfully!')
        )