"""
WhatsApp Service - DISABLED
This service has been disabled to prevent API errors on the server.
All methods return success responses but don't actually send messages.
"""

import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Disabled WhatsApp service - returns success responses without sending messages"""
    
    def __init__(self):
        self.access_token = None
        self.phone_number_id = None
        self.business_account_id = None
        self.verify_token = None
        self.api_url = None
        
        logger.info("WhatsApp service initialized in DISABLED mode - no messages will be sent")
    
    def send_message(self, to_phone: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """
        Disabled - returns success without sending message
        """
        logger.info(f"WhatsApp DISABLED: Would have sent message to {to_phone}")
        return {
            'success': True,
            'message_id': 'disabled_service',
            'response': {'status': 'disabled'}
        }
    
    def send_booking_notification(self, booking, phone_number: str) -> Dict[str, Any]:
        """
        Disabled - returns success without sending notification
        """
        logger.info(f"WhatsApp DISABLED: Would have sent booking notification for {getattr(booking, 'booking_number', 'unknown')}")
        return {
            'success': True,
            'message_id': 'disabled_service',
            'response': {'status': 'disabled'}
        }
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Disabled - returns None (webhook verification disabled)
        """
        logger.info("WhatsApp DISABLED: Webhook verification disabled")
        return None
    
    def process_webhook_event(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Disabled - returns success without processing
        """
        logger.info("WhatsApp DISABLED: Webhook event processing disabled")
        return {'success': True, 'message': 'WhatsApp service disabled'}
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get WhatsApp service status - shows as disabled"""
        return {
            'configured': False,
            'phone_number_id': None,
            'business_account_id': None,
            'api_url': None,
            'has_access_token': False,
            'verify_token_set': False,
            'status': 'DISABLED',
            'message': 'WhatsApp service has been disabled'
        }


# Global service instance
whatsapp_service = WhatsAppService()