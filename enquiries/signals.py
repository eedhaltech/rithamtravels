"""
Django Signals for Enquiry Notifications
Automatically sends notifications when enquiries are created
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from .models import Enquiry

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Enquiry)
def send_enquiry_notifications(sender, instance, created, **kwargs):
    """
    Send notifications when a new enquiry is created
    
    Args:
        sender: The model class (Enquiry)
        instance: The enquiry instance
        created: Boolean indicating if this is a new enquiry
        **kwargs: Additional keyword arguments
    """
    if created:
        try:
            # Admin email addresses
            admin_emails = [
                'info@rithamtravels.in',
                'admin@rithamtravels.in'
            ]
            
            # Also include settings-based company email if different
            company_email = getattr(settings, 'COMPANY_EMAIL', None)
            if company_email and company_email not in admin_emails:
                admin_emails.append(company_email)
            
            # Create detailed email content
            email_subject = f'New Contact Enquiry: {instance.subject}'
            email_message = f"""
New Contact Enquiry Received

Customer Details:
Name: {instance.name}
Email: {instance.email}
Phone: {instance.phone}
Enquiry Type: {instance.get_enquiry_type_display()}

Subject: {instance.subject}

Message:
{instance.message}

---
Submitted on: {instance.created_at.strftime('%d %B %Y at %I:%M %p')}
Enquiry ID: {instance.id}

Please respond to the customer at: {instance.email}

Admin Panel: {getattr(settings, 'WEBSITE_URL', 'https://rithamtravels.in')}/travels-dashboard/
            """.strip()
            
            send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                admin_emails,
                fail_silently=False,
            )
            
            logger.info(f"Enquiry notification sent to: {', '.join(admin_emails)} for enquiry {instance.id}")
            
        except Exception as e:
            logger.error(f"Error sending enquiry notification for enquiry {instance.id}: {str(e)}")


# Signal configuration
def configure_enquiry_signals():
    """Configure enquiry signals - called from apps.py"""
    logger.info("Enquiry notification signals configured")