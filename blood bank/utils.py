import re
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask_sqlalchemy import SQLAlchemy

# Constants
ADMIN_CODE_LENGTH = 16
PASSWORD_MIN_LENGTH = 8
TOKEN_EXPIRY_DAYS = 30

db = SQLAlchemy()

class AdminActivity(db.Model):
    """
    Model for tracking admin activities
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

def validate_email(email: str) -> bool:
    """
    Validate email format using regex
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> bool:
    """
    Validate password strength
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        return False
    
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    return all([has_upper, has_lower, has_digit, has_special])

def hash_password(password: str) -> str:
    """
    Hash password using SHA-256 with salt
    """
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify password against hashed password
    """
    salt, stored_hash = hashed_password.split(':')
    computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return computed_hash == stored_hash

def generate_admin_code() -> str:
    """
    Generate a secure admin registration code
    """
    return secrets.token_hex(ADMIN_CODE_LENGTH)

def generate_auth_token() -> str:
    """
    Generate a secure authentication token
    """
    return secrets.token_hex(32)

def validate_admin_code(code: str, stored_code: str) -> bool:
    """
    Validate admin registration code
    """
    return code == stored_code

def create_admin_session(user_id: int) -> Dict[str, Any]:
    """
    Create a new admin session
    """
    token = generate_auth_token()
    expiry = datetime.utcnow() + timedelta(days=TOKEN_EXPIRY_DAYS)
    
    return {
        'token': token,
        'user_id': user_id,
        'expires_at': expiry.isoformat(),
        'created_at': datetime.utcnow().isoformat()
    }

def validate_admin_session(token: str, user_id: int) -> bool:
    """
    Validate admin session token
    """
    # TODO: Implement session validation logic
    # This would typically check against a database
    return True

def sanitize_admin_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize admin registration data
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = value.strip()
        else:
            sanitized[key] = value
    return sanitized

def format_admin_response(admin_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format admin data for response
    """
    return {
        'id': admin_data.get('id'),
        'name': admin_data.get('name'),
        'email': admin_data.get('email'),
        'created_at': admin_data.get('created_at'),
        'last_login': admin_data.get('last_login')
    }

def handle_admin_registration_error(error: Exception) -> Dict[str, Any]:
    """
    Handle admin registration errors
    """
    error_messages = {
        'email_exists': 'Email already registered',
        'invalid_email': 'Invalid email format',
        'invalid_password': 'Password does not meet requirements',
        'invalid_admin_code': 'Invalid admin registration code',
        'database_error': 'Database error occurred',
        'unknown_error': 'An unknown error occurred'
    }
    
    error_type = str(error)
    return {
        'success': False,
        'message': error_messages.get(error_type, error_messages['unknown_error'])
    }

def validate_admin_permissions(user_id: int) -> bool:
    """
    Validate if a user has admin permissions
    """
    try:
        user = User.query.get(user_id)
        admin_role = Role.query.filter_by(name='admin').first()
        return user and admin_role and admin_role.id == user.role_id
    except Exception:
        return False

def get_admin_stats() -> Dict[str, Any]:
    """
    Get admin dashboard statistics
    """
    try:
        return {
            'total_donors': Donor.query.count(),
            'total_donations': Donation.query.count(),
            'total_requests': BloodRequest.query.count(),
            'total_staff': Staff.query.count(),
            'blood_inventory': {
                bg.blood_group: bg.quantity
                for bg in BloodInventory.query.all()
            }
        }
    except Exception:
        return {}

def log_admin_activity(user_id: int, action: str, details: str) -> bool:
    """
    Log admin activities for audit purposes
    """
    try:
        activity = AdminActivity(
            user_id=user_id,
            action=action,
            details=details,
            timestamp=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False 