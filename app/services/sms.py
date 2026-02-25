"""
SMS Service using Twilio
"""

from twilio.rest import Client
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class SMSService:
    """SMS service for alerts"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER", "")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
    
    async def send_alert(self, to_number: str, message: str) -> bool:
        """
        Send SMS alert
        
        Args:
            to_number: Recipient phone number
            message: Message content
            
        Returns:
            Success status
        """
        if not self.client:
            print(f"SMS not configured. Would send to {to_number}: {message}")
            return False
        
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            return True
        except Exception as e:
            print(f"SMS error: {e}")
            return False
    
    def format_disease_alert(self, disease_name: str, confidence: float,
                            crop_type: str) -> str:
        """Format disease alert message"""
        return (
            f"🚨 Crop Disease Alert!\n\n"
            f"Crop: {crop_type}\n"
            f"Disease: {disease_name}\n"
            f"Confidence: {confidence:.1f}%\n\n"
            f"Please take immediate action."
        )

# Global instance
sms_service = SMSService()
