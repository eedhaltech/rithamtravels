"""
Django Signals for Booking Notifications
Automatically sends notifications when bookings are created or updated
"""

import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import Booking

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Booking)
def send_booking_notifications(sender, instance, created, **kwargs):
    """
    Send notifications when a booking is created or status changes
    
    Args:
        sender: The model class (Booking)
        instance: The booking instance
        created: Boolean indicating if this is a new booking
        **kwargs: Additional keyword arguments
    """
    try:
        # Import here to avoid circular imports
        from .services.notification_service import notification_orchestrator
        
        # Only send notifications if enabled in settings
        if not getattr(settings, 'BOOKING_NOTIFICATIONS_ENABLED', True):
            logger.info(f"Booking notifications disabled - skipping for {instance.booking_number}")
            return
        
        if created:
            # New booking created - send confirmation and admin notifications
            logger.info(f"New booking created: {instance.booking_number} - sending notifications")
            
            # Send customer confirmation notification
            try:
                confirmation_result = notification_orchestrator.send_booking_confirmation(instance)
                if confirmation_result['overall_success']:
                    logger.info(f"Customer notifications sent successfully for {instance.booking_number}")
                else:
                    logger.warning(f"Some customer notifications failed for {instance.booking_number}")
            except Exception as e:
                logger.error(f"Error sending customer notifications for {instance.booking_number}: {str(e)}")
            
            # Send admin notification
            try:
                admin_result = notification_orchestrator.send_admin_notification(instance)
                if admin_result['overall_success']:
                    logger.info(f"Admin notifications sent successfully for {instance.booking_number}")
                else:
                    logger.warning(f"Admin notifications failed for {instance.booking_number}")
            except Exception as e:
                logger.error(f"Error sending admin notifications for {instance.booking_number}: {str(e)}")
        
        else:
            # Existing booking updated - check if status changed
            try:
                # Get the previous instance to compare status
                if hasattr(instance, '_previous_status'):
                    previous_status = instance._previous_status
                    current_status = instance.status
                    
                    if previous_status != current_status:
                        logger.info(f"Booking {instance.booking_number} status changed from {previous_status} to {current_status}")
                        
                        # Send status update notifications
                        _send_status_update_notifications(instance, previous_status, current_status)
                        
                        # If booking is completed, send final bill
                        if current_status == 'completed':
                            _send_completion_notifications(instance)
                
            except Exception as e:
                logger.error(f"Error handling status change for {instance.booking_number}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in booking notification signal for {instance.booking_number}: {str(e)}")


@receiver(pre_save, sender=Booking)
def track_booking_status_changes(sender, instance, **kwargs):
    """
    Track status changes before saving to detect updates
    
    Args:
        sender: The model class (Booking)
        instance: The booking instance
        **kwargs: Additional keyword arguments
    """
    try:
        if instance.pk:  # Only for existing bookings
            try:
                previous_instance = Booking.objects.get(pk=instance.pk)
                instance._previous_status = previous_instance.status
            except Booking.DoesNotExist:
                instance._previous_status = None
        else:
            instance._previous_status = None
    
    except Exception as e:
        logger.error(f"Error tracking status changes for booking: {str(e)}")
        instance._previous_status = None


def _send_status_update_notifications(booking, previous_status, current_status):
    """
    Send notifications when booking status changes
    
    Args:
        booking: Booking instance
        previous_status: Previous status
        current_status: New status
    """
    try:
        from .services.template_engine import template_engine
        from .services.email_service import email_service
        from .services.whatsapp_service import whatsapp_service
        
        # Create status update message
        status_messages = {
            'confirmed': 'Great news! Your booking has been confirmed. We will contact you with driver details soon.',
            'cancelled': 'Your booking has been cancelled. If you have any questions, please contact us.',
            'completed': 'Thank you for traveling with us! Your trip has been completed.'
        }
        
        message = status_messages.get(current_status, f'Your booking status has been updated to {booking.get_status_display()}.')
        
        # Send email notification using template engine
        if booking.email:
            try:
                # Use the template engine to generate proper status update email
                template_data = template_engine.generate_status_update_template(booking, message, 'html')
                text_template_data = template_engine.generate_status_update_template(booking, message, 'text')
                
                email_service.send_html_email(
                    subject=template_data['subject'],
                    html_content=template_data['content'],
                    text_content=text_template_data['content'],
                    recipient_emails=[booking.email]
                )
                
                logger.info(f"Status update email sent for {booking.booking_number}")
                
            except Exception as e:
                logger.error(f"Error sending status update email for {booking.booking_number}: {str(e)}")
        
        # Also send status update to admin emails
        try:
            admin_emails = [
                'info@rithamtravels.in',
                'admin@rithamtravels.in'
            ]
            
            # Include settings-based admin email if different
            settings_admin_email = getattr(settings, 'ADMIN_EMAIL', getattr(settings, 'COMPANY_EMAIL', None))
            if settings_admin_email and settings_admin_email not in admin_emails:
                admin_emails.append(settings_admin_email)
            
            # Generate admin version of status update
            admin_message = f"Booking {booking.booking_number} status changed from {previous_status} to {current_status}.\n\nCustomer: {booking.name}\nEmail: {booking.email}\nPhone: {booking.phone}"
            
            admin_template_data = template_engine.generate_status_update_template(booking, admin_message, 'html')
            admin_text_template_data = template_engine.generate_status_update_template(booking, admin_message, 'text')
            
            email_service.send_html_email(
                subject=f"[ADMIN] {admin_template_data['subject']}",
                html_content=admin_template_data['content'],
                text_content=admin_text_template_data['content'],
                recipient_emails=admin_emails
            )
            
            logger.info(f"Admin status update emails sent for {booking.booking_number} to {', '.join(admin_emails)}")
            
        except Exception as e:
            logger.error(f"Error sending admin status update emails for {booking.booking_number}: {str(e)}")
        
        # Send WhatsApp notification
        if booking.phone:
            try:
                whatsapp_message = f"""🚗 *BOOKING STATUS UPDATE*

📋 *Booking:* {booking.booking_number}
📊 *Status:* {booking.get_status_display()}

{message}

📞 *Support:* {getattr(settings, 'COMPANY_PHONE', '+91 97871 10763')}
🌐 *Website:* {getattr(settings, 'WEBSITE_URL', 'https://rithamtravels.in')}"""

                whatsapp_service.send_message(str(booking.phone), whatsapp_message)
                logger.info(f"Status update WhatsApp sent for {booking.booking_number}")
                
            except Exception as e:
                logger.error(f"Error sending status update WhatsApp for {booking.booking_number}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error sending status update notifications for {booking.booking_number}: {str(e)}")


def _send_completion_notifications(booking):
    """
    Send notifications when booking is completed
    
    Args:
        booking: Booking instance
    """
    try:
        # Import here to avoid circular imports
        from .services.notification_service import notification_orchestrator
        
        # Check if there are any extra payments
        extra_payments = booking.extra_payments.all()
        
        # Send final bill notification
        final_bill_result = notification_orchestrator.send_final_bill(booking, extra_payments)
        
        if final_bill_result['overall_success']:
            logger.info(f"Final bill notifications sent successfully for {booking.booking_number}")
        else:
            logger.warning(f"Some final bill notifications failed for {booking.booking_number}")
    
    except Exception as e:
        logger.error(f"Error sending completion notifications for {booking.booking_number}: {str(e)}")


# Signal configuration
def configure_booking_signals():
    """Configure booking signals - called from apps.py"""
    logger.info("Booking notification signals configured")