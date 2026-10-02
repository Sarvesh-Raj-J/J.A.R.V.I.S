"""
Email Module
Handles email composition and sending via Gmail
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class EmailManager:
    """Manages email operations with Gmail"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.email_config = config.get('email', {})
        self.sender_email = os.getenv(
            "JARVIS_EMAIL", self.email_config.get('sender_email', '')
        )
        self.sender_password = os.getenv(
            "JARVIS_EMAIL_PASSWORD", self.email_config.get('sender_password', '')
        )
        self.smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = self.email_config.get('smtp_port', 587)
    
    def validate_credentials(self) -> bool:
        """Check if email credentials are configured"""
        if not self.sender_email or self.sender_email == 'your_email@gmail.com':
            logger.warning("Email credentials not configured")
            return False
        if not self.sender_password or self.sender_password == 'your_app_password':
            logger.warning("Email password not configured")
            return False
        return True
    
    def send_email(self, to_email: str, subject: str, content: str) -> bool:
        """
        Send an email via Gmail
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            content: Email body content
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            if not self.validate_credentials():
                logger.error("Email credentials not properly configured")
                return False
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = to_email
            
            # Create plain text and HTML versions
            text_part = MIMEText(content, "plain")
            message.attach(text_part)
            
            # Create secure SSL context
            context = ssl.create_default_context()
            
            # Connect and send email
            logger.info(f"Sending email to {to_email}")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            logger.info("Email sent successfully")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication error: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def compose_email_interactive(self, voice_engine) -> Optional[Dict]:
        """
        Interactive email composition using voice commands
        
        Args:
            voice_engine: VoiceEngine instance for interaction
            
        Returns:
            dict: Email details or None if cancelled
        """
        try:
            # Get recipient
            voice_engine.speak("Who should I send the email to? Please say the email address clearly.")
            to_email = voice_engine.listen()
            
            if not to_email:
                voice_engine.speak("I didn't catch that. Email composition cancelled.")
                return None
            
            # Validate email format (basic check)
            if '@' not in to_email or '.' not in to_email:
                voice_engine.speak("That doesn't seem like a valid email address. Let me try again.")
                voice_engine.speak("Please spell out the email address word by word.")
                to_email = voice_engine.listen()
                
                if not to_email or '@' not in to_email:
                    voice_engine.speak("Email composition cancelled.")
                    return None
            
            # Get subject
            voice_engine.speak("What should be the subject of the email?")
            subject = voice_engine.listen()
            
            if not subject:
                subject = "Message from Jarvis"
            
            # Get content
            voice_engine.speak("What should the email say? You can speak multiple sentences.")
            content = voice_engine.listen()
            
            if not content:
                voice_engine.speak("No content provided. Email composition cancelled.")
                return None
            
            # Confirmation
            voice_engine.speak(f"I will send an email to {to_email}")
            voice_engine.speak(f"Subject: {subject}")
            voice_engine.speak(f"Content: {content}")
            voice_engine.speak("Should I send it? Say yes to confirm or no to cancel.")
            
            confirmation = voice_engine.listen()
            
            if confirmation and 'yes' in confirmation:
                return {
                    'to': to_email,
                    'subject': subject,
                    'content': content
                }
            else:
                voice_engine.speak("Email cancelled.")
                return None
                
        except Exception as e:
            logger.error(f"Error in interactive email composition: {e}")
            return None
    
    def update_credentials(self, email: str, password: str):
        """Update email credentials"""
        self.sender_email = email
        self.sender_password = password
        logger.info("Email credentials updated")
