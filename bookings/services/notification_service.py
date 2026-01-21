"""
Notification Service for Ritham Tours & Travels
Coordinates WhatsApp and Email notifications for bookings
"""

import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.utils import timezone
from datetime import datetime, date, time
from .whatsapp_service import whatsapp_service
from .email_service import email_service
from .template_engine import template_engine

logger = logging.getLogger(__name__)

class NotificationOrchestrator:
    """Central orchestrator for all booking-related notifications"""
    
    def __init__(self):
        self.whatsapp_service = whatsapp_service
        self.email_service = email_service
        self.template_engine = template_engine
    
    def send_booking_confirmation(self, booking) -> Dict[str, Any]:
        """
        Send booking confirmation notifications to traveler and admin
        
        Args:
            booking: Booking model instance
            
        Returns:
            Dict containing results of notification attempts
        """
        results = {
            'booking_id': booking.id,
            'booking_number': booking.booking_number,
            'notification_type': 'booking_confirmation',
            'whatsapp': {'attempted': False, 'success': False},
            'email': {'attempted': False, 'success': False},
            'admin_email': {'attempted': False, 'success': False},
            'overall_success': False,
            'notifications_sent': []
        }
        
        try:
            logger.info(f"Sending booking confirmation for {booking.booking_number}")
            
            # Send WhatsApp notification to customer
            if booking.phone:
                results['whatsapp']['attempted'] = True
                whatsapp_result = self._send_whatsapp_confirmation(booking)
                results['whatsapp'].update(whatsapp_result)
                
                if whatsapp_result['success']:
                    results['notifications_sent'].append('whatsapp')
                    logger.info(f"WhatsApp confirmation sent for booking {booking.booking_number}")
                else:
                    logger.error(f"WhatsApp confirmation failed for booking {booking.booking_number}: {whatsapp_result.get('error')}")
            
            # Send Email notification to customer
            if booking.email:
                results['email']['attempted'] = True
                email_result = self._send_email_confirmation(booking)
                results['email'].update(email_result)
                
                if email_result['success']:
                    results['notifications_sent'].append('email')
                    logger.info(f"Email confirmation sent for booking {booking.booking_number}")
                else:
                    logger.error(f"Email confirmation failed for booking {booking.booking_number}: {email_result.get('error')}")
            
            # Send copy to admin emails
            try:
                admin_emails = [
                    'info@rithamtravels.in',
                    'admin@rithamtravels.in'
                ]
                
                # Include settings-based admin email if different
                settings_admin_email = getattr(settings, 'ADMIN_EMAIL', getattr(settings, 'COMPANY_EMAIL', None))
                if settings_admin_email and settings_admin_email not in admin_emails:
                    admin_emails.append(settings_admin_email)
                
                results['admin_email']['attempted'] = True
                admin_email_result = self._send_admin_confirmation_copy(booking, admin_emails)
                results['admin_email'].update(admin_email_result)
                
                if admin_email_result['success']:
                    results['notifications_sent'].append('admin_email')
                    logger.info(f"Admin confirmation copies sent for booking {booking.booking_number}")
                else:
                    logger.error(f"Admin confirmation copies failed for booking {booking.booking_number}: {admin_email_result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error sending admin confirmation copies for booking {booking.booking_number}: {str(e)}")
            
            # Update booking notification tracking
            self._update_booking_notification_tracking(booking, 'booking_confirmation')
            
            # Determine overall success
            results['overall_success'] = len(results['notifications_sent']) > 0
            
            return results
            
        except Exception as e:
            logger.error(f"Error in booking confirmation for {booking.booking_number}: {str(e)}")
            results['error'] = str(e)
            return results
    
    def send_admin_notification(self, booking) -> Dict[str, Any]:
        """
        Send booking notification to admin with management links
        
        Args:
            booking: Booking model instance
            
        Returns:
            Dict containing results of notification attempts
        """
        results = {
            'booking_id': booking.id,
            'booking_number': booking.booking_number,
            'notification_type': 'admin_notification',
            'email': {'attempted': False, 'success': False},
            'whatsapp': {'attempted': False, 'success': False},
            'overall_success': False,
            'notifications_sent': []
        }
        
        try:
            logger.info(f"Sending admin notification for booking {booking.booking_number}")
            
            # Get admin emails - send to multiple admin addresses
            admin_emails = [
                'info@rithamtravels.in',
                'admin@rithamtravels.in'
            ]
            
            # Also include settings-based admin email if different
            settings_admin_email = getattr(settings, 'ADMIN_EMAIL', getattr(settings, 'COMPANY_EMAIL', None))
            if settings_admin_email and settings_admin_email not in admin_emails:
                admin_emails.append(settings_admin_email)
            
            admin_phone = getattr(settings, 'ADMIN_PHONE', getattr(settings, 'COMPANY_PHONE', None))
            
            # Send Email notification to all admin addresses
            if admin_emails:
                results['email']['attempted'] = True
                email_result = self._send_admin_email(booking, admin_emails)
                results['email'].update(email_result)
                
                if email_result['success']:
                    results['notifications_sent'].append('email')
                    logger.info(f"Admin emails sent for booking {booking.booking_number} to {', '.join(admin_emails)}")
                else:
                    logger.error(f"Admin emails failed for booking {booking.booking_number}: {email_result.get('error')}")
            
            # Send WhatsApp notification to admin
            if admin_phone:
                results['whatsapp']['attempted'] = True
                whatsapp_result = self._send_admin_whatsapp(booking, admin_phone)
                results['whatsapp'].update(whatsapp_result)
                
                if whatsapp_result['success']:
                    results['notifications_sent'].append('whatsapp')
                    logger.info(f"Admin WhatsApp sent for booking {booking.booking_number}")
                else:
                    logger.error(f"Admin WhatsApp failed for booking {booking.booking_number}: {whatsapp_result.get('error')}")
            
            # Track notification for each admin email
            for admin_email in admin_emails:
                self._track_notification(booking, 'admin_notification', 'email', admin_email, 
                                       'sent' if results['email']['success'] else 'failed')
            
            results['overall_success'] = len(results['notifications_sent']) > 0
            
            return results
            
        except Exception as e:
            logger.error(f"Error in admin notification for {booking.booking_number}: {str(e)}")
            results['error'] = str(e)
            return results
    
    def send_final_bill(self, booking, extra_payments=None) -> Dict[str, Any]:
        """
        Send final bill notification for completed trips
        
        Args:
            booking: Booking model instance
            extra_payments: List of ExtraPayment instances
            
        Returns:
            Dict containing results of notification attempts
        """
        results = {
            'booking_id': booking.id,
            'booking_number': booking.booking_number,
            'notification_type': 'final_bill',
            'whatsapp': {'attempted': False, 'success': False},
            'email': {'attempted': False, 'success': False},
            'overall_success': False,
            'notifications_sent': []
        }
        
        try:
            logger.info(f"Sending final bill for booking {booking.booking_number}")
            
            # Send WhatsApp notification
            if booking.phone:
                results['whatsapp']['attempted'] = True
                whatsapp_result = self._send_whatsapp_final_bill(booking, extra_payments)
                results['whatsapp'].update(whatsapp_result)
                
                if whatsapp_result['success']:
                    results['notifications_sent'].append('whatsapp')
                    logger.info(f"WhatsApp final bill sent for booking {booking.booking_number}")
            
            # Send Email notification
            if booking.email:
                results['email']['attempted'] = True
                email_result = self._send_email_final_bill(booking, extra_payments)
                results['email'].update(email_result)
                
                if email_result['success']:
                    results['notifications_sent'].append('email')
                    logger.info(f"Email final bill sent for booking {booking.booking_number}")
            
            # Update booking notification tracking
            self._update_booking_notification_tracking(booking, 'final_bill')
            
            results['overall_success'] = len(results['notifications_sent']) > 0
            
            return results
            
        except Exception as e:
            logger.error(f"Error in final bill notification for {booking.booking_number}: {str(e)}")
            results['error'] = str(e)
            return results
    
    def resend_notification(self, notification_id: str) -> Dict[str, Any]:
        """
        Resend a failed notification
        
        Args:
            notification_id: ID of the notification record to resend
            
        Returns:
            Dict containing resend results
        """
        try:
            from ..models import NotificationRecord
            
            notification = NotificationRecord.objects.get(id=notification_id)
            booking = notification.booking
            
            if notification.channel == 'email':
                if notification.notification_type == 'booking_confirmation':
                    result = self._send_email_confirmation(booking)
                elif notification.notification_type == 'admin_notification':
                    result = self._send_admin_email(booking, notification.recipient)
                elif notification.notification_type == 'final_bill':
                    result = self._send_email_final_bill(booking)
                else:
                    result = {'success': False, 'error': 'Unknown notification type'}
            
            elif notification.channel == 'whatsapp':
                if notification.notification_type == 'booking_confirmation':
                    result = self._send_whatsapp_confirmation(booking)
                elif notification.notification_type == 'admin_notification':
                    result = self._send_admin_whatsapp(booking, notification.recipient)
                elif notification.notification_type == 'final_bill':
                    result = self._send_whatsapp_final_bill(booking)
                else:
                    result = {'success': False, 'error': 'Unknown notification type'}
            
            else:
                result = {'success': False, 'error': 'Unknown channel'}
            
            # Update notification record
            if result['success']:
                notification.status = 'sent'
                notification.error_message = None
            else:
                notification.mark_failed(result.get('error', 'Resend failed'))
            
            notification.save()
            
            return result
            
        except Exception as e:
            logger.error(f"Error resending notification {notification_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_email_confirmation(self, booking) -> Dict[str, Any]:
        """Send email confirmation using template engine"""
        try:
            template_data = self.template_engine.generate_confirmation_template(booking, 'html')
            
            result = self.email_service.send_html_email(
                subject=template_data['subject'],
                html_content=template_data['content'],
                text_content=self.template_engine.generate_confirmation_template(booking, 'text')['content'],
                recipient_emails=[booking.email]
            )
            
            # Track notification
            self._track_notification(booking, 'booking_confirmation', 'email', booking.email, 
                                   'sent' if result['success'] else 'failed', 
                                   result.get('error'))
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending email confirmation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_admin_email(self, booking, admin_emails) -> Dict[str, Any]:
        """Send admin email using template engine to multiple admin addresses"""
        try:
            template_data = self.template_engine.generate_admin_template(booking, 'html')
            
            # Ensure admin_emails is a list
            if isinstance(admin_emails, str):
                admin_emails = [admin_emails]
            
            result = self.email_service.send_html_email(
                subject=template_data['subject'],
                html_content=template_data['content'],
                text_content=self.template_engine.generate_admin_template(booking, 'text')['content'],
                recipient_emails=admin_emails
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending admin email: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_email_final_bill(self, booking, extra_payments=None) -> Dict[str, Any]:
        """Send final bill email using template engine"""
        try:
            template_data = self.template_engine.generate_final_bill_template(booking, extra_payments, 'html')
            
            result = self.email_service.send_html_email(
                subject=template_data['subject'],
                html_content=template_data['content'],
                text_content=self.template_engine.generate_final_bill_template(booking, extra_payments, 'text')['content'],
                recipient_emails=[booking.email]
            )
            
            # Track notification
            self._track_notification(booking, 'final_bill', 'email', booking.email, 
                                   'sent' if result['success'] else 'failed', 
                                   result.get('error'))
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending final bill email: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_whatsapp_confirmation(self, booking) -> Dict[str, Any]:
        """Send WhatsApp confirmation using template engine"""
        try:
            message = self.template_engine.generate_whatsapp_message(booking, 'confirmation')
            
            result = self.whatsapp_service.send_booking_notification(booking, str(booking.phone))
            
            # Track notification
            self._track_notification(booking, 'booking_confirmation', 'whatsapp', str(booking.phone), 
                                   'sent' if result['success'] else 'failed', 
                                   result.get('error'))
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp confirmation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_admin_whatsapp(self, booking, admin_phone) -> Dict[str, Any]:
        """Send admin WhatsApp using template engine"""
        try:
            message = self.template_engine.generate_whatsapp_message(booking, 'admin')
            
            # Use WhatsApp service to send admin message
            result = self.whatsapp_service.send_message(admin_phone, message)
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending admin WhatsApp: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_whatsapp_final_bill(self, booking, extra_payments=None) -> Dict[str, Any]:
        """Send WhatsApp final bill using template engine"""
        try:
            message = self.template_engine.generate_whatsapp_message(booking, 'final_bill')
            
            result = self.whatsapp_service.send_message(str(booking.phone), message)
            
            # Track notification
            self._track_notification(booking, 'final_bill', 'whatsapp', str(booking.phone), 
                                   'sent' if result['success'] else 'failed', 
                                   result.get('error'))
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp final bill: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_admin_confirmation_copy(self, booking, admin_emails) -> Dict[str, Any]:
        """Send booking confirmation copy to admin emails"""
        try:
            # Generate admin version with additional context
            template_data = self.template_engine.generate_admin_template(booking, 'html')
            
            # Modify subject to indicate it's a copy
            admin_subject = f"[COPY] {template_data['subject']}"
            
            result = self.email_service.send_html_email(
                subject=admin_subject,
                html_content=template_data['content'],
                text_content=self.template_engine.generate_admin_template(booking, 'text')['content'],
                recipient_emails=admin_emails
            )
            
            # Track notification for each admin email
            for admin_email in admin_emails:
                self._track_notification(booking, 'booking_confirmation', 'email', admin_email, 
                                       'sent' if result['success'] else 'failed', 
                                       result.get('error'))
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending admin confirmation copy: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _track_notification(self, booking, notification_type, channel, recipient, status, error_message=None):
        """Track notification in database"""
        try:
            from ..models import NotificationRecord
            
            NotificationRecord.objects.create(
                booking=booking,
                notification_type=notification_type,
                channel=channel,
                recipient=recipient,
                status=status,
                error_message=error_message,
                template_used=f"{notification_type}_{channel}"
            )
            
        except Exception as e:
            logger.error(f"Error tracking notification: {str(e)}")
    
    def _update_booking_notification_tracking(self, booking, notification_type):
        """Update booking-level notification tracking"""
        try:
            booking.last_notification_sent = timezone.now()
            booking.notification_count += 1
            booking.save(update_fields=['last_notification_sent', 'notification_count'])
            
        except Exception as e:
            logger.error(f"Error updating booking notification tracking: {str(e)}")


class NotificationService:
    """Legacy service class for backward compatibility"""
    
    def __init__(self):
        self.orchestrator = NotificationOrchestrator()
        self.whatsapp_service = whatsapp_service
        self.email_service = email_service
    
    def send_booking_notifications(self, booking, phone_number: Optional[str] = None, 
                                 email_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Send booking notifications via both WhatsApp and Email
        Maintained for backward compatibility
        """
        return self.orchestrator.send_booking_confirmation(booking)
    
    def send_whatsapp_only(self, booking, phone_number: str) -> Dict[str, Any]:
        """Send only WhatsApp notification"""
        if not phone_number:
            return {'success': False, 'error': 'No phone number provided'}
        
        return self.whatsapp_service.send_booking_notification(booking, phone_number)
    
    def send_email_only(self, booking, email_address: str) -> Dict[str, Any]:
        """Send only Email notification"""
        if not email_address:
            return {'success': False, 'error': 'No email address provided'}
        
        return self.email_service.send_booking_notification(booking, email_address)
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all notification services"""
        return {
            'whatsapp': self.whatsapp_service.get_service_status(),
            'email': self.email_service.get_service_status(),
            'notification_service': {
                'active': True,
                'services_available': {
                    'whatsapp': bool(self.whatsapp_service.access_token),
                    'email': bool(self.email_service.from_email)
                }
            }
        }


# Global service instances
notification_orchestrator = NotificationOrchestrator()
notification_service = NotificationService()  # For backward compatibility