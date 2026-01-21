"""
Template Engine for Booking Notifications
Generates consistent booking-summary-card layouts for all notification types
"""

import logging
from typing import Dict, Any, Optional
from django.template.loader import render_to_string
from django.template import Context, Template
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime, date, time
from decimal import Decimal

logger = logging.getLogger(__name__)

class BookingTemplateEngine:
    """Template engine for generating consistent booking notification templates"""
    
    def __init__(self):
        self.company_name = getattr(settings, 'COMPANY_NAME', 'Ritham Tours & Travels')
        self.company_phone = getattr(settings, 'COMPANY_PHONE', '+91 97871 10763')
        self.company_email = getattr(settings, 'COMPANY_EMAIL', 'info@rithamtravels.in')
        self.website_url = getattr(settings, 'WEBSITE_URL', 'https://rithamtravels.in')
    
    def generate_confirmation_template(self, booking, format_type='html') -> Dict[str, str]:
        """
        Generate booking confirmation template for travelers
        
        Args:
            booking: Booking model instance
            format_type: 'html' or 'text'
            
        Returns:
            Dict with 'subject' and 'content' keys
        """
        try:
            context = self._prepare_booking_context(booking)
            context.update({
                'template_type': 'confirmation',
                'message': 'Your booking is pending confirmation. We will contact you shortly.',
                'show_admin_actions': False,
                'is_customer_notification': True,
            })
            
            if format_type == 'html':
                subject = f"Booking Confirmation - {booking.booking_number} | {self.company_name}"
                content = render_to_string('notifications/email_confirmation.html', context)
            else:
                subject = f"Booking Confirmation - {booking.booking_number}"
                content = self._generate_text_confirmation(context)
            
            return {
                'subject': subject,
                'content': content,
                'context': context
            }
            
        except Exception as e:
            logger.error(f"Error generating confirmation template for booking {booking.booking_number}: {str(e)}")
            return self._generate_fallback_template(booking, 'confirmation', format_type)
    
    def generate_admin_template(self, booking, format_type='html') -> Dict[str, str]:
        """
        Generate admin notification template with management links
        
        Args:
            booking: Booking model instance
            format_type: 'html' or 'text'
            
        Returns:
            Dict with 'subject' and 'content' keys
        """
        try:
            context = self._prepare_booking_context(booking)
            context.update({
                'template_type': 'admin',
                'message': 'New booking received. Please review and take action.',
                'show_admin_actions': True,
                'is_customer_notification': False,
                'admin_url': f"{self.website_url}/travels-dashboard/bookings/{booking.id}/",
                'management_text': 'Click here to view full booking details and Accept or Cancel the booking.'
            })
            
            if format_type == 'html':
                subject = f"New Booking Alert - {booking.booking_number} | Admin Panel"
                content = render_to_string('notifications/email_admin.html', context)
            else:
                subject = f"New Booking Alert - {booking.booking_number}"
                content = self._generate_text_admin(context)
            
            return {
                'subject': subject,
                'content': content,
                'context': context
            }
            
        except Exception as e:
            logger.error(f"Error generating admin template for booking {booking.booking_number}: {str(e)}")
            return self._generate_fallback_template(booking, 'admin', format_type)
    
    def generate_final_bill_template(self, booking, extra_payments=None, format_type='html') -> Dict[str, str]:
        """
        Generate final bill template for completed trips
        
        Args:
            booking: Booking model instance
            extra_payments: List of ExtraPayment instances
            format_type: 'html' or 'text'
            
        Returns:
            Dict with 'subject' and 'content' keys
        """
        try:
            context = self._prepare_booking_context(booking)
            
            # Calculate final bill
            final_bill = booking.calculate_final_bill()
            
            context.update({
                'template_type': 'final_bill',
                'message': 'Your trip has been completed. Please find your final bill below.',
                'show_admin_actions': False,
                'is_customer_notification': True,
                'final_bill': final_bill,
                'extra_payments': extra_payments or [],
                'is_completed': True,
            })
            
            if format_type == 'html':
                subject = f"Final Bill - {booking.booking_number} | Trip Completed"
                content = render_to_string('notifications/email_final_bill.html', context)
            else:
                subject = f"Final Bill - {booking.booking_number}"
                content = self._generate_text_final_bill(context)
            
            return {
                'subject': subject,
                'content': content,
                'context': context
            }
            
        except Exception as e:
            logger.error(f"Error generating final bill template for booking {booking.booking_number}: {str(e)}")
            return self._generate_fallback_template(booking, 'final_bill', format_type)
    
    def generate_status_update_template(self, booking, message, format_type='html') -> Dict[str, str]:
        """
        Generate status update template for booking changes
        
        Args:
            booking: Booking model instance
            message: Status update message
            format_type: 'html' or 'text'
            
        Returns:
            Dict with 'subject' and 'content' keys
        """
        try:
            context = self._prepare_booking_context(booking)
            context.update({
                'template_type': 'status_update',
                'message': message,
                'show_admin_actions': False,
                'is_customer_notification': True,
            })
            
            if format_type == 'html':
                subject = f"Booking Status Update - {booking.booking_number} | {self.company_name}"
                content = render_to_string('notifications/email_status_update.html', context)
            else:
                subject = f"Booking Status Update - {booking.booking_number}"
                content = self._generate_text_status_update(context)
            
            return {
                'subject': subject,
                'content': content,
                'context': context
            }
            
        except Exception as e:
            logger.error(f"Error generating status update template for booking {booking.booking_number}: {str(e)}")
            return self._generate_fallback_template(booking, 'status_update', format_type)
    
    def render_booking_summary_card(self, booking, context_override=None) -> str:
        """
        Render the booking summary card component
        
        Args:
            booking: Booking model instance
            context_override: Additional context to override defaults
            
        Returns:
            Rendered HTML string
        """
        try:
            context = self._prepare_booking_context(booking)
            if context_override:
                context.update(context_override)
            
            return render_to_string('notifications/booking_summary_card.html', context)
            
        except Exception as e:
            logger.error(f"Error rendering booking summary card for booking {booking.booking_number}: {str(e)}")
            return self._generate_fallback_card(booking)
    
    def generate_whatsapp_message(self, booking, template_type='confirmation') -> str:
        """
        Generate WhatsApp message with booking summary
        
        Args:
            booking: Booking model instance
            template_type: Type of message (confirmation, admin, final_bill)
            
        Returns:
            Formatted WhatsApp message string
        """
        try:
            context = self._prepare_booking_context(booking)
            
            # Status emoji mapping
            status_emoji = {
                'pending': '⏳',
                'confirmed': '✅',
                'cancelled': '❌',
                'completed': '🎉'
            }
            
            emoji = status_emoji.get(booking.status, '📋')
            
            if template_type == 'confirmation':
                message = f"""🚗 *RITHAM TOURS & TRAVELS*
Your Trusted Travel Partner

{emoji} *BOOKING CONFIRMATION*

👤 *Customer:* {booking.name}
🆔 *Booking ID:* {booking.booking_number}
📊 *Status:* {booking.get_status_display()}

📍 *Pickup:* {booking.pickup_city}
📍 *Drop:* {booking.pickup_city}  
📅 *Date:* {self._format_date(booking.pickup_date)}
🕐 *Time:* {self._format_time(booking.pickup_time)}

💰 *Total Amount:* ₹{booking.total_amount}
💳 *Payment:* {booking.get_payment_type_display()}

✨ *Your booking is pending confirmation. We will contact you shortly.*

📞 *24/7 Support:* {self.company_phone}
🌐 *Website:* {self.website_url}

View Details: {self.website_url}/booking/{booking.id}/"""

            elif template_type == 'admin':
                message = f"""🚗 *ADMIN ALERT - NEW BOOKING*

{emoji} *BOOKING DETAILS*

👤 *Customer:* {booking.name}
📧 *Email:* {booking.email}
📱 *Phone:* {booking.phone}
🆔 *Booking ID:* {booking.booking_number}

📍 *Route:* {booking.pickup_city} → {booking.pickup_city}
📅 *Date:* {self._format_date(booking.pickup_date)}
💰 *Amount:* ₹{booking.total_amount}

🔗 *Manage Booking:*
{self.website_url}/travels-dashboard/bookings/{booking.id}/

⚡ *Action Required:* Review and confirm booking"""

            elif template_type == 'final_bill':
                final_bill = booking.calculate_final_bill()
                message = f"""🚗 *TRIP COMPLETED - FINAL BILL*

🎉 *Thank you for traveling with us!*

👤 *Customer:* {booking.name}
🆔 *Booking ID:* {booking.booking_number}

💰 *PAYMENT SUMMARY*
• Original Amount: ₹{booking.total_amount}
• Advance Paid: ₹{booking.advance_amount}
• Extra Charges: ₹{final_bill['extra_amount']}
• *Total Amount: ₹{final_bill['final_total']}*
• *Outstanding: ₹{final_bill['outstanding_balance']}*

📞 *Support:* {self.company_phone}
🌐 *Website:* {self.website_url}"""

            else:
                message = self._generate_fallback_whatsapp(booking)
            
            return message
            
        except Exception as e:
            logger.error(f"Error generating WhatsApp message for booking {booking.booking_number}: {str(e)}")
            return self._generate_fallback_whatsapp(booking)
    
    def _prepare_booking_context(self, booking) -> Dict[str, Any]:
        """Prepare common context for all templates"""
        context = booking.get_notification_context()
        
        # Add company information
        context.update({
            'company_name': self.company_name,
            'company_phone': self.company_phone,
            'company_email': self.company_email,
            'website_url': self.website_url,
        })
        
        # Add formatted dates and times
        context.update({
            'formatted_pickup_date': self._format_date(booking.pickup_date),
            'formatted_pickup_time': self._format_time(booking.pickup_time),
            'formatted_drop_date': self._format_date(booking.drop_date),
            'formatted_drop_time': self._format_time(booking.drop_time),
        })
        
        # Add status styling
        status_styles = {
            'pending': {'color': '#f59e0b', 'bg': '#fef3c7', 'icon': '⏳'},
            'confirmed': {'color': '#10b981', 'bg': '#d1fae5', 'icon': '✅'},
            'cancelled': {'color': '#ef4444', 'bg': '#fee2e2', 'icon': '❌'},
            'completed': {'color': '#8b5cf6', 'bg': '#ede9fe', 'icon': '🎉'}
        }
        
        context['status_style'] = status_styles.get(booking.status, {
            'color': '#6b7280', 'bg': '#f3f4f6', 'icon': '📋'
        })
        
        return context
    
    def _format_date(self, date_obj, default='TBD'):
        """Safely format date object"""
        if not date_obj:
            return default
        
        if isinstance(date_obj, str):
            return date_obj
        
        if hasattr(date_obj, 'strftime'):
            try:
                return date_obj.strftime('%d %B %Y')
            except (ValueError, AttributeError):
                return str(date_obj)
        
        return str(date_obj)
    
    def _format_time(self, time_obj, default='TBD'):
        """Safely format time object"""
        if not time_obj:
            return default
        
        if isinstance(time_obj, str):
            return time_obj
        
        if hasattr(time_obj, 'strftime'):
            try:
                return time_obj.strftime('%I:%M %p')
            except (ValueError, AttributeError):
                return str(time_obj)
        
        return str(time_obj)
    
    def _generate_text_confirmation(self, context) -> str:
        """Generate plain text confirmation message"""
        booking = context['booking']
        return f"""
🚗 RITHAM TOURS & TRAVELS
Your Trusted Travel Partner

{context['status_style']['icon']} BOOKING CONFIRMATION

Customer Name: {booking.name}
Booking ID: {booking.booking_number}
Status: {booking.get_status_display()}

Pickup Location: {booking.pickup_city}
Drop Location: {booking.pickup_city}
Travel Date: {context['formatted_pickup_date']}
Pickup Time: {context['formatted_pickup_time']}

Total Amount: ₹{booking.total_amount}
Payment Method: {booking.get_payment_type_display()}

{context['message']}

View Booking Details: {self.website_url}/booking/{booking.id}/

---
Thank you for choosing Ritham Tours & Travels!

24/7 Support: {self.company_phone}
Email: {self.company_email}
Website: {self.website_url}

This is an automated message.
        """.strip()
    
    def _generate_text_admin(self, context) -> str:
        """Generate plain text admin notification"""
        booking = context['booking']
        return f"""
🚗 ADMIN ALERT - NEW BOOKING RECEIVED

Customer Details:
Name: {booking.name}
Email: {booking.email}
Phone: {booking.phone}

Booking Details:
Booking ID: {booking.booking_number}
Route: {booking.pickup_city} → {booking.pickup_city}
Date: {context['formatted_pickup_date']}
Time: {context['formatted_pickup_time']}
Amount: ₹{booking.total_amount}
Payment: {booking.get_payment_type_display()}

{context['management_text']}
{context['admin_url']}

Action Required: Please review and confirm this booking.
        """.strip()
    
    def _generate_text_final_bill(self, context) -> str:
        """Generate plain text final bill"""
        booking = context['booking']
        final_bill = context['final_bill']
        
        # Check if GST is enabled in system settings
        from accounts.models import SystemSettings
        system_settings = SystemSettings.get_settings()
        
        gst_line = ""
        if system_settings.gst_enabled and final_bill.get('gst_amount', 0) > 0:
            gst_line = f"GST ({final_bill['gst_rate']}%): ₹{final_bill['gst_amount']:.2f}\n"
        
        return f"""
🚗 TRIP COMPLETED - FINAL BILL

Thank you for traveling with Ritham Tours & Travels!

Customer: {booking.name}
Booking ID: {booking.booking_number}
Trip Date: {context['formatted_pickup_date']}

PAYMENT SUMMARY:
Original Amount: ₹{booking.total_amount}
Advance Paid: ₹{booking.advance_amount}
Extra Charges: ₹{final_bill['extra_amount']}
{gst_line}---
Total Amount: ₹{final_bill['final_total']}
Outstanding Balance: ₹{final_bill['outstanding_balance']}

{context['message']}

Support: {self.company_phone}
Email: {self.company_email}
Website: {self.website_url}
        """.strip()
    
    def _generate_text_status_update(self, context) -> str:
        """Generate plain text status update message"""
        booking = context['booking']
        return f"""
🚗 RITHAM TOURS & TRAVELS
Your Trusted Travel Partner

{context['status_style']['icon']} BOOKING STATUS UPDATE

Customer Name: {booking.name}
Booking ID: {booking.booking_number}
Status: {booking.get_status_display()}

Pickup Location: {booking.pickup_city}
Drop Location: {booking.pickup_city}
Travel Date: {context['formatted_pickup_date']}
Pickup Time: {context['formatted_pickup_time']}

Total Amount: ₹{booking.total_amount}
Payment Method: {booking.get_payment_type_display()}

{context['message']}

View Booking Details: {self.website_url}/booking/{booking.id}/

---
Thank you for choosing Ritham Tours & Travels!

24/7 Support: {self.company_phone}
Email: {self.company_email}
Website: {self.website_url}

This is an automated message.
        """.strip()
    
    def _generate_fallback_template(self, booking, template_type, format_type):
        """Generate fallback template when main template fails"""
        subject = f"Booking Update - {booking.booking_number}"
        
        if format_type == 'html':
            content = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Booking Update</h2>
                <p><strong>Booking ID:</strong> {booking.booking_number}</p>
                <p><strong>Customer:</strong> {booking.name}</p>
                <p><strong>Status:</strong> {booking.get_status_display()}</p>
                <p>Thank you for choosing Ritham Tours & Travels!</p>
                <p>Contact: {self.company_phone}</p>
            </div>
            """
        else:
            content = f"""
Booking Update - {booking.booking_number}

Customer: {booking.name}
Status: {booking.get_status_display()}

Thank you for choosing Ritham Tours & Travels!
Contact: {self.company_phone}
            """.strip()
        
        return {
            'subject': subject,
            'content': content,
            'context': {'booking': booking}
        }
    
    def _generate_fallback_card(self, booking):
        """Generate fallback booking card when main template fails"""
        return f"""
        <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0;">
            <h3>Booking Summary</h3>
            <p><strong>ID:</strong> {booking.booking_number}</p>
            <p><strong>Customer:</strong> {booking.name}</p>
            <p><strong>Status:</strong> {booking.get_status_display()}</p>
            <p><strong>Amount:</strong> ₹{booking.total_amount}</p>
        </div>
        """
    
    def _generate_fallback_whatsapp(self, booking):
        """Generate fallback WhatsApp message"""
        return f"""
🚗 RITHAM TOURS & TRAVELS

Booking Update: {booking.booking_number}
Customer: {booking.name}
Status: {booking.get_status_display()}

Contact: {self.company_phone}
Website: {self.website_url}
        """.strip()


# Global template engine instance
template_engine = BookingTemplateEngine()