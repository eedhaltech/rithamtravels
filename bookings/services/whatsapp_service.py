"""
WhatsApp Cloud API Service for Ritham Tours & Travels
Handles WhatsApp message sending and webhook processing
"""

import requests
import json
import logging
from django.conf import settings
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppService:
    """WhatsApp Cloud API service for sending messages and handling webhooks"""
    
    def __init__(self):
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.business_account_id = settings.WHATSAPP_BUSINESS_ACCOUNT_ID
        self.verify_token = settings.WHATSAPP_VERIFY_TOKEN
        self.api_url = f"https://graph.facebook.com/v19.0/{self.phone_number_id}/messages"
        
        # Validate configuration
        if not all([self.access_token, self.phone_number_id, self.business_account_id]):
            logger.error("WhatsApp configuration incomplete. Check environment variables.")
    
    def send_message(self, to_phone: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """
        Send WhatsApp message to a phone number
        
        Args:
            to_phone (str): Recipient phone number (with country code, no +)
            message (str): Message content
            message_type (str): Type of message (text, template, etc.)
            
        Returns:
            Dict containing success status and response data
        """
        try:
            # Clean phone number (remove + and spaces)
            clean_phone = to_phone.replace('+', '').replace(' ', '').replace('-', '')
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": message_type,
                "text": {
                    "body": message
                }
            }
            
            logger.info(f"Sending WhatsApp message to {clean_phone}")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                logger.info(f"WhatsApp message sent successfully to {clean_phone}")
                return {
                    'success': True,
                    'message_id': response_data.get('messages', [{}])[0].get('id'),
                    'response': response_data
                }
            else:
                logger.error(f"WhatsApp API error: {response_data}")
                return {
                    'success': False,
                    'error': response_data.get('error', {}).get('message', 'Unknown error'),
                    'response': response_data
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp request failed: {str(e)}")
            return {
                'success': False,
                'error': f'Request failed: {str(e)}'
            }
        except Exception as e:
            logger.error(f"WhatsApp service error: {str(e)}")
            return {
                'success': False,
                'error': f'Service error: {str(e)}'
            }
    
    def send_booking_notification(self, booking, phone_number: str) -> Dict[str, Any]:
        """
        Send booking notification via WhatsApp
        
        Args:
            booking: Booking model instance
            phone_number (str): Customer phone number
            
        Returns:
            Dict containing success status and response data
        """
        try:
            # Format booking message
            message = self._format_booking_message(booking)
            
            # Send WhatsApp message
            result = self.send_message(phone_number, message)
            
            # Log the result
            if result['success']:
                logger.info(f"Booking notification sent via WhatsApp for booking {booking.booking_number}")
            else:
                logger.error(f"Failed to send WhatsApp notification for booking {booking.booking_number}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending booking WhatsApp notification for booking {getattr(booking, 'booking_number', 'unknown')}: {str(e)}")
            return {
                'success': False,
                'error': f'Notification error: {str(e)}'
            }
    
    def _format_booking_message(self, booking) -> str:
        """Format booking information into WhatsApp message"""
        
        # Get status emoji
        status_emoji = {
            'pending': '⏳',
            'confirmed': '✅',
            'cancelled': '❌',
            'completed': '🎉'
        }.get(booking.status.lower(), '📋')
        
        # Format travel date and time with safe formatting
        travel_date = self._safe_format_date(booking.pickup_date)
        travel_time = self._safe_format_time(booking.pickup_time)
        
        # Get pickup and drop locations
        pickup_location = getattr(booking.pickup_city, 'name', 'Not specified') if hasattr(booking, 'pickup_city') else 'Not specified'
        drop_location = getattr(booking.drop_city, 'name', pickup_location) if hasattr(booking, 'drop_city') else pickup_location
        
        # Create booking details URL
        booking_url = f"https://rithamtravels.in/booking/{booking.id}/"
        
        message = f"""🚗 *Ritham Tours & Travels*

{status_emoji} *Booking Update*

👤 *Customer:* {booking.customer_name}
🆔 *Booking ID:* {booking.booking_number}
📊 *Status:* {booking.get_status_display()}

📍 *Pickup:* {pickup_location}
📍 *Drop:* {drop_location}
📅 *Travel Date:* {travel_date}
🕐 *Pickup Time:* {travel_time}

🔗 *View Details:* {booking_url}

Thank you for choosing Ritham Tours & Travels!
📞 Support: +91 97871 10763"""

        return message
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Verify webhook subscription request from Meta
        
        Args:
            mode (str): Verification mode
            token (str): Verification token
            challenge (str): Challenge string
            
        Returns:
            Challenge string if verification successful, None otherwise
        """
        if mode == "subscribe" and token == self.verify_token:
            logger.info("WhatsApp webhook verified successfully")
            return challenge
        else:
            logger.warning(f"WhatsApp webhook verification failed. Mode: {mode}, Token: {token}")
            return None
    
    def process_webhook_event(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming webhook events from WhatsApp
        
        Args:
            webhook_data (dict): Webhook payload from Meta
            
        Returns:
            Dict containing processing result
        """
        try:
            logger.info(f"Processing WhatsApp webhook event: {json.dumps(webhook_data, indent=2)}")
            
            # Extract entry data
            entry = webhook_data.get('entry', [])
            if not entry:
                return {'success': True, 'message': 'No entry data'}
            
            for entry_item in entry:
                changes = entry_item.get('changes', [])
                
                for change in changes:
                    field = change.get('field')
                    value = change.get('value', {})
                    
                    if field == 'messages':
                        # Process incoming messages
                        messages = value.get('messages', [])
                        for message in messages:
                            self._process_incoming_message(message, value)
                    
                    elif field == 'message_status':
                        # Process message status updates
                        statuses = value.get('statuses', [])
                        for status in statuses:
                            self._process_message_status(status)
            
            return {'success': True, 'message': 'Webhook processed successfully'}
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp webhook: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _process_incoming_message(self, message: Dict[str, Any], value: Dict[str, Any]) -> None:
        """Process incoming WhatsApp message"""
        try:
            message_id = message.get('id')
            from_number = message.get('from')
            message_type = message.get('type')
            timestamp = message.get('timestamp')
            
            # Get contact info
            contacts = value.get('contacts', [])
            contact_name = contacts[0].get('profile', {}).get('name', 'Unknown') if contacts else 'Unknown'
            
            logger.info(f"Received WhatsApp message from {contact_name} ({from_number}): Type {message_type}")
            
            # Handle different message types
            if message_type == 'text':
                text_content = message.get('text', {}).get('body', '')
                logger.info(f"Text message content: {text_content}")
                
                # You can add auto-reply logic here if needed
                # For now, just log the message
                
        except Exception as e:
            logger.error(f"Error processing incoming message: {str(e)}")
    
    def _process_message_status(self, status: Dict[str, Any]) -> None:
        """Process message delivery status"""
        try:
            message_id = status.get('id')
            recipient_id = status.get('recipient_id')
            status_type = status.get('status')  # sent, delivered, read, failed
            timestamp = status.get('timestamp')
            
            logger.info(f"Message {message_id} status: {status_type} for recipient {recipient_id}")
            
            # You can update message delivery status in database here if needed
            
        except Exception as e:
            logger.error(f"Error processing message status: {str(e)}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get WhatsApp service configuration status"""
        return {
            'configured': bool(self.access_token and self.phone_number_id),
            'phone_number_id': self.phone_number_id,
            'business_account_id': self.business_account_id,
            'api_url': self.api_url,
            'has_access_token': bool(self.access_token),
            'verify_token_set': bool(self.verify_token)
        }
    
    def _safe_format_date(self, date_obj, format_str='%d %B %Y', default='TBD'):
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
    
    def _safe_format_time(self, time_obj, format_str='%I:%M %p', default='TBD'):
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


# Global service instance
whatsapp_service = WhatsAppService()