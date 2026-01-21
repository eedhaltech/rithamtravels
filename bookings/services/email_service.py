"""
Email Service for Ritham Tours & Travels
Handles email notifications for bookings and other communications
"""

import logging
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending notifications and communications"""
    
    def __init__(self):
        self.from_email = settings.EMAIL_HOST_USER
        self.company_name = settings.COMPANY_NAME
        self.company_phone = settings.COMPANY_PHONE
        self.company_email = settings.COMPANY_EMAIL
        
        # Validate email configuration
        if not self.from_email:
            logger.error("Email configuration incomplete. Check EMAIL_HOST_USER setting.")
    
    @staticmethod
    def safe_format_date(date_obj, format_str='%d %B %Y', default='TBD'):
        """Safely format date object, handling strings and None values"""
        if not date_obj:
            return default
        
        # If it's already a string, return it
        if isinstance(date_obj, str):
            return date_obj
        
        # If it has strftime method (datetime, date objects)
        if hasattr(date_obj, 'strftime'):
            try:
                return date_obj.strftime(format_str)
            except (ValueError, AttributeError):
                return str(date_obj)
        
        # Fallback to string conversion
        return str(date_obj)
    
    @staticmethod
    def safe_format_time(time_obj, format_str='%I:%M %p', default='TBD'):
        """Safely format time object, handling strings and None values"""
        if not time_obj:
            return default
        
        # If it's already a string, return it
        if isinstance(time_obj, str):
            return time_obj
        
        # If it has strftime method (time, datetime objects)
        if hasattr(time_obj, 'strftime'):
            try:
                return time_obj.strftime(format_str)
            except (ValueError, AttributeError):
                return str(time_obj)
        
        # Fallback to string conversion
        return str(time_obj)
    
    def send_booking_notification(self, booking, recipient_email: str) -> Dict[str, Any]:
        """
        Send booking notification via email
        
        Args:
            booking: Booking model instance
            recipient_email (str): Customer email address
            
        Returns:
            Dict containing success status and response data
        """
        try:
            # Format email content
            subject = f"Booking Update - {getattr(booking, 'booking_number', 'Unknown')} | Ritham Tours & Travels"
            
            # Create HTML and text versions
            html_content = self._format_booking_email_html(booking)
            text_content = self._format_booking_email_text(booking)
            
            # Send email
            result = self.send_html_email(
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                recipient_emails=[recipient_email]
            )
            
            # Log the result
            if result['success']:
                logger.info(f"Booking notification sent via email for booking {getattr(booking, 'booking_number', 'unknown')}")
            else:
                logger.error(f"Failed to send email notification for booking {getattr(booking, 'booking_number', 'unknown')}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending booking email notification for booking {getattr(booking, 'booking_number', 'unknown')}: {str(e)}")
            return {
                'success': False,
                'error': f'Email notification error: {str(e)}'
            }
    
    def send_html_email(self, subject: str, html_content: str, text_content: str, 
                       recipient_emails: List[str], cc_emails: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Send HTML email with text fallback
        
        Args:
            subject (str): Email subject
            html_content (str): HTML email content
            text_content (str): Plain text email content
            recipient_emails (List[str]): List of recipient email addresses
            cc_emails (Optional[List[str]]): List of CC email addresses
            
        Returns:
            Dict containing success status and response data
        """
        try:
            from django.core.mail import EmailMultiAlternatives
            
            # Create email message with text content as base
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=f"{self.company_name} <{self.from_email}>",
                to=recipient_emails,
                cc=cc_emails or []
            )
            
            # Add HTML alternative
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            result = email.send()
            
            if result:
                logger.info(f"HTML email sent successfully to {', '.join(recipient_emails)}")
                return {
                    'success': True,
                    'recipients': recipient_emails,
                    'subject': subject
                }
            else:
                logger.error(f"Failed to send HTML email to {', '.join(recipient_emails)}")
                return {
                    'success': False,
                    'error': 'Email sending failed'
                }
                
        except Exception as e:
            logger.error(f"HTML email sending error: {str(e)}")
            return {
                'success': False,
                'error': f'Email error: {str(e)}'
            }
    
    def send_simple_email(self, subject: str, message: str, recipient_emails: List[str]) -> Dict[str, Any]:
        """
        Send simple text email
        
        Args:
            subject (str): Email subject
            message (str): Email message
            recipient_emails (List[str]): List of recipient email addresses
            
        Returns:
            Dict containing success status and response data
        """
        try:
            result = send_mail(
                subject=subject,
                message=message,
                from_email=f"{self.company_name} <{self.from_email}>",
                recipient_list=recipient_emails,
                fail_silently=False
            )
            
            if result:
                logger.info(f"Simple email sent successfully to {', '.join(recipient_emails)}")
                return {
                    'success': True,
                    'recipients': recipient_emails,
                    'subject': subject
                }
            else:
                logger.error(f"Failed to send simple email to {', '.join(recipient_emails)}")
                return {
                    'success': False,
                    'error': 'Email sending failed'
                }
                
        except Exception as e:
            logger.error(f"Simple email sending error: {str(e)}")
            return {
                'success': False,
                'error': f'Email error: {str(e)}'
            }
    
    def _format_booking_email_html(self, booking) -> str:
        """Format booking information into HTML email"""
        
        # Get status styling
        status_styles = {
            'pending': {'color': '#f59e0b', 'bg': '#fef3c7', 'icon': '⏳'},
            'confirmed': {'color': '#10b981', 'bg': '#d1fae5', 'icon': '✅'},
            'cancelled': {'color': '#ef4444', 'bg': '#fee2e2', 'icon': '❌'},
            'completed': {'color': '#8b5cf6', 'bg': '#ede9fe', 'icon': '🎉'}
        }
        
        status_info = status_styles.get(booking.status.lower(), {
            'color': '#6b7280', 'bg': '#f3f4f6', 'icon': '📋'
        })
        
        # Format travel date and time with safe formatting
        travel_date = self.safe_format_date(booking.pickup_date)
        travel_time = self.safe_format_time(booking.pickup_time)
        
        # Get pickup and drop locations
        pickup_location = getattr(booking.pickup_city, 'name', 'Not specified') if hasattr(booking, 'pickup_city') else 'Not specified'
        drop_location = getattr(booking.drop_city, 'name', pickup_location) if hasattr(booking, 'drop_city') else pickup_location
        
        # Create booking details URL
        booking_url = f"https://rithamtravels.in/booking/{booking.id}/"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Booking Update - {booking.booking_number}</title>
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px 15px 0 0; text-align: center;">
                <h1 style="margin: 0; font-size: 28px; font-weight: 700;">🚗 Ritham Tours & Travels</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Your Trusted Travel Partner</p>
            </div>
            
            <!-- Status Banner -->
            <div style="background: {status_info['bg']}; color: {status_info['color']}; padding: 20px; text-align: center; border-left: 5px solid {status_info['color']};">
                <h2 style="margin: 0; font-size: 24px; font-weight: 600;">
                    {status_info['icon']} Booking {booking.get_status_display()}
                </h2>
            </div>
            
            <!-- Booking Details -->
            <div style="background: white; padding: 30px; border: 1px solid #e5e7eb;">
                <h3 style="color: #2563eb; margin-top: 0; font-size: 20px;">Booking Details</h3>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; font-weight: 600; color: #374151; width: 40%;">
                            👤 Customer Name:
                        </td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; color: #1f2937;">
                            {booking.customer_name}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; font-weight: 600; color: #374151;">
                            🆔 Booking ID:
                        </td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; color: #1f2937; font-family: monospace; font-weight: 600;">
                            {booking.booking_number}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; font-weight: 600; color: #374151;">
                            📊 Status:
                        </td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6;">
                            <span style="background: {status_info['bg']}; color: {status_info['color']}; padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 14px;">
                                {status_info['icon']} {booking.get_status_display()}
                            </span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; font-weight: 600; color: #374151;">
                            📍 Pickup Location:
                        </td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; color: #1f2937;">
                            {pickup_location}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; font-weight: 600; color: #374151;">
                            📍 Drop Location:
                        </td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; color: #1f2937;">
                            {drop_location}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; font-weight: 600; color: #374151;">
                            📅 Travel Date:
                        </td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f3f4f6; color: #1f2937; font-weight: 600;">
                            {travel_date}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; font-weight: 600; color: #374151;">
                            🕐 Pickup Time:
                        </td>
                        <td style="padding: 12px 0; color: #1f2937; font-weight: 600;">
                            {travel_time}
                        </td>
                    </tr>
                </table>
                
                <!-- Action Button -->
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{booking_url}" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: 600; font-size: 16px; display: inline-block; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                        🔗 View Booking Details
                    </a>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f8f9fa; padding: 25px; border-radius: 0 0 15px 15px; text-align: center; border-top: 3px solid #667eea;">
                <p style="margin: 0 0 15px 0; color: #6b7280; font-size: 14px;">
                    Thank you for choosing Ritham Tours & Travels!
                </p>
                
                <div style="margin: 15px 0;">
                    <p style="margin: 5px 0; color: #374151; font-weight: 600;">
                        📞 24/7 Support: <a href="tel:+919787110763" style="color: #2563eb; text-decoration: none;">+91 97871 10763</a>
                    </p>
                    <p style="margin: 5px 0; color: #374151; font-weight: 600;">
                        📧 Email: <a href="mailto:{self.company_email}" style="color: #2563eb; text-decoration: none;">{self.company_email}</a>
                    </p>
                    <p style="margin: 5px 0; color: #374151; font-weight: 600;">
                        🌐 Website: <a href="https://rithamtravels.in/" style="color: #2563eb; text-decoration: none;">rithamtravels.in</a>
                    </p>
                </div>
                
                <p style="margin: 15px 0 0 0; color: #9ca3af; font-size: 12px;">
                    This is an automated message. Please do not reply to this email.
                </p>
            </div>
            
        </body>
        </html>
        """
        
        return html_content
    
    def _format_booking_email_text(self, booking) -> str:
        """Format booking information into plain text email"""
        
        # Get status emoji
        status_emoji = {
            'pending': '⏳',
            'confirmed': '✅',
            'cancelled': '❌',
            'completed': '🎉'
        }.get(booking.status.lower(), '📋')
        
        # Format travel date and time with safe formatting
        travel_date = self.safe_format_date(booking.pickup_date)
        travel_time = self.safe_format_time(booking.pickup_time)
        
        # Get pickup and drop locations
        pickup_location = getattr(booking.pickup_city, 'name', 'Not specified') if hasattr(booking, 'pickup_city') else 'Not specified'
        drop_location = getattr(booking.drop_city, 'name', pickup_location) if hasattr(booking, 'drop_city') else pickup_location
        
        # Create booking details URL
        booking_url = f"https://rithamtravels.in/booking/{booking.id}/"
        
        text_content = f"""
🚗 RITHAM TOURS & TRAVELS
Your Trusted Travel Partner

{status_emoji} BOOKING UPDATE

Customer Name: {booking.customer_name}
Booking ID: {booking.booking_number}
Status: {booking.get_status_display()}

Pickup Location: {pickup_location}
Drop Location: {drop_location}
Travel Date: {travel_date}
Pickup Time: {travel_time}

View Booking Details: {booking_url}

---
Thank you for choosing Ritham Tours & Travels!

24/7 Support: +91 97871 10763
Email: {self.company_email}
Website: https://rithamtravels.in/

This is an automated message. Please do not reply to this email.
        """
        
        return text_content.strip()
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get email service configuration status"""
        return {
            'configured': bool(self.from_email),
            'from_email': self.from_email,
            'company_name': self.company_name,
            'company_email': self.company_email,
            'smtp_configured': bool(settings.EMAIL_HOST and settings.EMAIL_PORT)
        }


# Global service instance
email_service = EmailService()