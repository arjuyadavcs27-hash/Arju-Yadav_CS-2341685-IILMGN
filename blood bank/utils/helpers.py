import re
import bcrypt
from datetime import datetime, timedelta
import jwt
from flask import current_app
import os
import requests
from typing import Dict, Any, Optional

def validate_indian_mobile(mobile: str) -> bool:
    """Validate Indian mobile number format."""
    pattern = r'^[6-9]\d{9}$'
    return bool(re.match(pattern, mobile))

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hashed password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_reset_token(user_id: int) -> str:
    """Generate password reset token."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_reset_token(token: str) -> Optional[int]:
    """Verify password reset token."""
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def send_sms(mobile: str, message: str) -> bool:
    """Send SMS using Twilio."""
    try:
        from twilio.rest import Client
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=f'+91{mobile}'
        )
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send SMS: {str(e)}")
        return False

def send_email(to: str, subject: str, body: str) -> bool:
    """Send email using SMTP."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = os.getenv('MAIL_USERNAME')
        msg['To'] = to
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(os.getenv('MAIL_SERVER'), int(os.getenv('MAIL_PORT')))
        server.starttls()
        server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

def validate_blood_type(blood_type: str) -> bool:
    """Validate blood type format."""
    valid_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    return blood_type in valid_types

def calculate_age(date_of_birth: datetime) -> int:
    """Calculate age from date of birth."""
    today = datetime.today()
    return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

def is_donation_eligible(age: int, weight: float, last_donation_date: Optional[datetime]) -> bool:
    """Check if donor is eligible to donate blood."""
    if age < 18 or age > 65:
        return False
    if weight < 45:
        return False
    if last_donation_date:
        days_since_last_donation = (datetime.now() - last_donation_date).days
        if days_since_last_donation < 90:
            return False
    return True

def format_phone_number(phone: str) -> str:
    """Format phone number to Indian format."""
    phone = re.sub(r'\D', '', phone)
    if len(phone) == 10:
        return f"+91 {phone[:5]} {phone[5:]}"
    return phone

def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize input data to prevent XSS."""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = re.sub(r'<[^>]+>', '', value)
        else:
            sanitized[key] = value
    return sanitized

def get_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers."""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def generate_otp() -> str:
    """Generate a 6-digit OTP."""
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def validate_pincode(pincode: str) -> bool:
    """Validate Indian pincode format."""
    pattern = r'^[1-9][0-9]{5}$'
    return bool(re.match(pattern, pincode)) 