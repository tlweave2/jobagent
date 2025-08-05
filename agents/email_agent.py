"""
Email Agent - Email Monitoring and 2FA Code Extraction

This agent monitors emails for verification codes, 2FA codes, and application confirmations.
It provides automated email verification for job applications.
"""

import asyncio
import re
import imaplib
import email
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

class EmailAgent:
    """Agent responsible for email monitoring and verification code extraction."""
    
    def __init__(self, email_config: Dict[str, str]):
        self.email_config = email_config
        self.imap_server = None
        self.last_check_time = datetime.now()
        self.verification_codes = {}
        
        print("📧 Email Agent initialized")
    
    async def initialize(self):
        """Initialize email connection and start monitoring."""
        print("📧 Connecting to email server...")
        
        try:
            # Connect to IMAP server
            self.imap_server = imaplib.IMAP4_SSL(
                self.email_config.get('imap_host', 'imap.gmail.com'),
                self.email_config.get('imap_port', 993)
            )
            
            # Login with credentials
            self.imap_server.login(
                self.email_config['email'],
                self.email_config['password']
            )
            
            # Select inbox
            self.imap_server.select('INBOX')
            
            print("✅ Email server connected successfully")
            
            # Start background monitoring
            asyncio.create_task(self.monitor_emails())
            
        except Exception as e:
            print(f"❌ Email connection failed: {e}")
            print("   ⚠️  Email verification will not be available")
    
    async def monitor_emails(self):
        """Continuously monitor for new emails with verification codes."""
        print("📧 Starting email monitoring for verification codes...")
        
        while True:
            try:
                await self.check_for_verification_emails()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ Email monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def check_for_verification_emails(self):
        """Check for new emails containing verification codes."""
        if not self.imap_server:
            return
        
        try:
            # Search for emails since last check
            since_date = self.last_check_time.strftime("%d-%b-%Y")
            
            # Search for recent emails
            search_criteria = f'(SINCE "{since_date}")'
            status, message_ids = self.imap_server.search(None, search_criteria)
            
            if status != 'OK':
                return
            
            message_ids = message_ids[0].split()
            
            # Process new emails
            for msg_id in message_ids[-10:]:  # Only check last 10 emails
                await self.process_email_for_codes(msg_id)
            
            self.last_check_time = datetime.now()
            
        except Exception as e:
            print(f"❌ Error checking emails: {e}")
    
    async def process_email_for_codes(self, msg_id: bytes):
        """Process a single email to extract verification codes."""
        try:
            # Fetch email
            status, data = self.imap_server.fetch(msg_id, '(RFC822)')
            if status != 'OK':
                return
            
            # Parse email
            email_body = data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Extract email details
            subject = email_message.get('Subject', '')
            sender = email_message.get('From', '')
            date_received = email_message.get('Date', '')
            
            # Get email content
            content = self.extract_email_content(email_message)
            
            # Check if this looks like a verification email
            if self.is_verification_email(subject, sender, content):
                # Extract verification code
                code = self.extract_verification_code(content)
                
                if code:
                    # Store the code with timestamp
                    verification_info = {
                        'code': code,
                        'subject': subject,
                        'sender': sender,
                        'received_at': datetime.now(),
                        'content': content[:200]  # First 200 chars for context
                    }
                    
                    # Store by sender domain for easy lookup
                    sender_domain = self.extract_domain(sender)
                    self.verification_codes[sender_domain] = verification_info
                    
                    print(f"📧 ✅ Verification code found: {code} from {sender_domain}")
                    
        except Exception as e:
            print(f"❌ Error processing email: {e}")
    
    def extract_email_content(self, email_message) -> str:
        """Extract readable content from email message."""
        content = ""
        
        try:
            if email_message.is_multipart():
                # Handle multipart emails
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            content += payload.decode('utf-8', errors='ignore')
                    elif part.get_content_type() == "text/html" and not content:
                        # Fallback to HTML if no plain text
                        payload = part.get_payload(decode=True)
                        if payload:
                            html_content = payload.decode('utf-8', errors='ignore')
                            # Simple HTML tag removal
                            content = re.sub(r'<[^>]+>', '', html_content)
            else:
                # Handle single part emails
                payload = email_message.get_payload(decode=True)
                if payload:
                    content = payload.decode('utf-8', errors='ignore')
            
        except Exception as e:
            print(f"❌ Error extracting email content: {e}")
        
        return content.strip()
    
    def is_verification_email(self, subject: str, sender: str, content: str) -> bool:
        """Determine if an email contains a verification code."""
        # Check subject line
        verification_subjects = [
            'verification', 'confirm', 'code', 'otp', 'authentication',
            'security', 'login', 'sign in', 'two-factor', '2fa'
        ]
        
        subject_lower = subject.lower()
        if any(keyword in subject_lower for keyword in verification_subjects):
            return True
        
        # Check sender domain
        trusted_domains = [
            'linkedin.com', 'indeed.com', 'glassdoor.com', 'monster.com',
            'ziprecruiter.com', 'careerbuilder.com', 'dice.com',
            'google.com', 'microsoft.com', 'apple.com'
        ]
        
        sender_lower = sender.lower()
        if any(domain in sender_lower for domain in trusted_domains):
            # Check content for verification patterns
            verification_patterns = [
                r'\b\d{4,8}\b',  # 4-8 digit codes
                r'verification code',
                r'confirmation code',
                r'security code',
                r'two.factor',
                r'authenticate'
            ]
            
            content_lower = content.lower()
            if any(re.search(pattern, content_lower) for pattern in verification_patterns):
                return True
        
        return False
    
    def extract_verification_code(self, content: str) -> Optional[str]:
        """Extract verification code from email content."""
        # Common verification code patterns
        patterns = [
            r'verification code[:\s]*(\d{4,8})',
            r'confirmation code[:\s]*(\d{4,8})',
            r'security code[:\s]*(\d{4,8})',
            r'your code[:\s]*(\d{4,8})',
            r'enter[:\s]*(\d{4,8})',
            r'code[:\s]*(\d{4,8})',
            r'\b(\d{6})\b',  # Common 6-digit codes
            r'\b(\d{4})\b',  # Common 4-digit codes
            r'\b(\d{8})\b'   # Common 8-digit codes
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                code = match.group(1)
                # Validate code (should be reasonable length)
                if 4 <= len(code) <= 8:
                    return code
        
        return None
    
    def extract_domain(self, email_address: str) -> str:
        """Extract domain from email address."""
        try:
            # Handle format: "Name <email@domain.com>"
            if '<' in email_address and '>' in email_address:
                email_address = email_address.split('<')[1].split('>')[0]
            
            # Extract domain
            domain = email_address.split('@')[-1].lower()
            return domain
            
        except:
            return email_address.lower()
    
    async def get_verification_code(self, domain: str = None, timeout: int = 300) -> Optional[str]:
        """Get the most recent verification code, optionally filtered by domain."""
        print(f"📧 Waiting for verification code{f' from {domain}' if domain else ''}...")
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            if domain:
                # Look for code from specific domain
                if domain in self.verification_codes:
                    code_info = self.verification_codes[domain]
                    # Check if code is recent (within last 10 minutes)
                    if (datetime.now() - code_info['received_at']).seconds < 600:
                        print(f"📧 ✅ Found verification code: {code_info['code']}")
                        return code_info['code']
            else:
                # Look for any recent code
                for domain_key, code_info in self.verification_codes.items():
                    if (datetime.now() - code_info['received_at']).seconds < 600:
                        print(f"📧 ✅ Found verification code: {code_info['code']} from {domain_key}")
                        return code_info['code']
            
            # Wait and check again
            await asyncio.sleep(10)
        
        print(f"⏰ Timeout waiting for verification code")
        return None
    
    async def wait_for_application_confirmation(self, job_title: str, company: str, timeout: int = 1800) -> bool:
        """Wait for application confirmation email."""
        print(f"📧 Waiting for application confirmation: {job_title} at {company}")
        
        start_time = datetime.now()
        initial_check_time = self.last_check_time
        
        while (datetime.now() - start_time).seconds < timeout:
            try:
                # Check for new emails since we started waiting
                since_date = initial_check_time.strftime("%d-%b-%Y")
                search_criteria = f'(SINCE "{since_date}")'
                
                status, message_ids = self.imap_server.search(None, search_criteria)
                if status == 'OK':
                    message_ids = message_ids[0].split()
                    
                    # Check recent emails for confirmation
                    for msg_id in message_ids[-20:]:  # Check last 20 emails
                        if await self.is_application_confirmation(msg_id, job_title, company):
                            print(f"📧 ✅ Application confirmation received!")
                            return True
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ Error checking for confirmation: {e}")
                await asyncio.sleep(60)
        
        print(f"⏰ Timeout waiting for application confirmation")
        return False
    
    async def is_application_confirmation(self, msg_id: bytes, job_title: str, company: str) -> bool:
        """Check if an email is an application confirmation."""
        try:
            # Fetch email
            status, data = self.imap_server.fetch(msg_id, '(RFC822)')
            if status != 'OK':
                return False
            
            # Parse email
            email_body = data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            subject = email_message.get('Subject', '').lower()
            sender = email_message.get('From', '').lower()
            content = self.extract_email_content(email_message).lower()
            
            # Check for confirmation keywords
            confirmation_keywords = [
                'application received', 'application submitted', 'thank you for applying',
                'application confirmation', 'we received your application',
                'application has been received', 'thank you for your interest'
            ]
            
            # Check if subject or content contains confirmation keywords
            full_text = f"{subject} {content}"
            has_confirmation = any(keyword in full_text for keyword in confirmation_keywords)
            
            if has_confirmation:
                # Check if it's related to our job application
                company_match = company.lower() in full_text
                title_words = job_title.lower().split()
                title_match = any(word in full_text for word in title_words if len(word) > 3)
                
                if company_match or title_match:
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error checking confirmation email: {e}")
            return False
    
    async def send_notification_email(self, subject: str, message: str, recipient: str = None):
        """Send a notification email about application status."""
        if not recipient:
            recipient = self.email_config['email']  # Send to self
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = recipient
            msg['Subject'] = f"Job Application Bot: {subject}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            with smtplib.SMTP_SSL(
                self.email_config.get('smtp_host', 'smtp.gmail.com'),
                self.email_config.get('smtp_port', 465)
            ) as server:
                server.login(self.email_config['email'], self.email_config['password'])
                server.send_message(msg)
            
            print(f"📧 ✅ Notification sent: {subject}")
            
        except Exception as e:
            print(f"❌ Failed to send notification: {e}")
    
    async def get_recent_codes(self, minutes: int = 10) -> List[Dict[str, Any]]:
        """Get all verification codes received in the last X minutes."""
        recent_codes = []
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        for domain, code_info in self.verification_codes.items():
            if code_info['received_at'] > cutoff_time:
                recent_codes.append({
                    'domain': domain,
                    'code': code_info['code'],
                    'received_at': code_info['received_at'],
                    'subject': code_info['subject']
                })
        
        # Sort by received time (newest first)
        recent_codes.sort(key=lambda x: x['received_at'], reverse=True)
        return recent_codes
    
    async def clear_old_codes(self, hours: int = 24):
        """Clear verification codes older than X hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        domains_to_remove = []
        for domain, code_info in self.verification_codes.items():
            if code_info['received_at'] < cutoff_time:
                domains_to_remove.append(domain)
        
        for domain in domains_to_remove:
            del self.verification_codes[domain]
        
        if domains_to_remove:
            print(f"📧 Cleared {len(domains_to_remove)} old verification codes")
    
    async def shutdown(self):
        """Shutdown the email agent."""
        print("📧 Shutting down email monitoring...")
        
        try:
            if self.imap_server:
                self.imap_server.close()
                self.imap_server.logout()
        except:
            pass
        
        print("📧 Email Agent shut down")
