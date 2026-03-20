import pytest
from sms_service import SMSService
from flask import Flask
from datetime import datetime

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['TWILIO_ACCOUNT_SID'] = 'test-account-sid'
    app.config['TWILIO_AUTH_TOKEN'] = 'test-auth-token'
    app.config['TWILIO_PHONE_NUMBER'] = '+1234567890'
    return app

@pytest.fixture
def sms_service(app):
    return SMSService(app)

def test_send_verification_sms(sms_service):
    """Test sending verification SMS."""
    phone_number = '+919876543210'
    otp = '123456'
    
    result = sms_service.send_verification_sms(phone_number, otp)
    assert result == True

def test_send_password_reset_sms(sms_service):
    """Test sending password reset SMS."""
    phone_number = '+919876543210'
    otp = '123456'
    
    result = sms_service.send_password_reset_sms(phone_number, otp)
    assert result == True

def test_send_donation_reminder_sms(sms_service):
    """Test sending donation reminder SMS."""
    phone_number = '+919876543210'
    last_donation_date = datetime.now() - timedelta(days=89)
    
    result = sms_service.send_donation_reminder_sms(phone_number, last_donation_date)
    assert result == True

def test_send_blood_request_notification_sms(sms_service):
    """Test sending blood request notification SMS."""
    phone_number = '+919876543210'
    request_data = {
        'patient_name': 'Test Patient',
        'blood_group': 'A+',
        'units_required': 2,
        'hospital_name': 'Test Hospital',
        'hospital_address': 'Test Address',
        'contact_number': '9876543210',
        'urgency_level': 'high'
    }
    
    result = sms_service.send_blood_request_notification_sms(phone_number, request_data)
    assert result == True

def test_send_emergency_alert_sms(sms_service):
    """Test sending emergency alert SMS."""
    phone_number = '+919876543210'
    emergency_data = {
        'patient_name': 'Emergency Patient',
        'blood_group': 'A+',
        'units_required': 2,
        'hospital_name': 'Emergency Hospital',
        'hospital_address': 'Emergency Address',
        'contact_number': '9876543210',
        'urgency_level': 'critical'
    }
    
    result = sms_service.send_emergency_alert_sms(phone_number, emergency_data)
    assert result == True

def test_send_donation_confirmation_sms(sms_service):
    """Test sending donation confirmation SMS."""
    phone_number = '+919876543210'
    donation_data = {
        'donation_date': datetime.now(),
        'blood_group': 'A+',
        'units_donated': 1,
        'blood_bank_name': 'Test Blood Bank'
    }
    
    result = sms_service.send_donation_confirmation_sms(phone_number, donation_data)
    assert result == True

def test_send_blood_availability_notification_sms(sms_service):
    """Test sending blood availability notification SMS."""
    phone_number = '+919876543210'
    availability_data = {
        'blood_group': 'A+',
        'units_available': 10,
        'blood_bank_name': 'Test Blood Bank',
        'blood_bank_address': 'Test Address',
        'contact_number': '9876543210'
    }
    
    result = sms_service.send_blood_availability_notification_sms(phone_number, availability_data)
    assert result == True

def test_send_custom_sms(sms_service):
    """Test sending custom SMS."""
    phone_number = '+919876543210'
    message = 'This is a test SMS message.'
    
    result = sms_service.send_custom_sms(phone_number, message)
    assert result == True

def test_phone_number_validation(sms_service):
    """Test phone number validation."""
    assert sms_service.validate_phone_number('+919876543210') == True
    assert sms_service.validate_phone_number('9876543210') == True
    assert sms_service.validate_phone_number('1234567890') == False
    assert sms_service.validate_phone_number('invalid') == False
    assert sms_service.validate_phone_number('+911234567890') == False

def test_sms_sending_error_handling(sms_service):
    """Test SMS sending error handling."""
    # Test with invalid phone number
    result = sms_service.send_custom_sms('invalid', 'Test')
    assert result == False
    
    # Test with empty message
    result = sms_service.send_custom_sms('+919876543210', '')
    assert result == False
    
    # Test with message too long
    long_message = 'x' * 161  # SMS messages are limited to 160 characters
    result = sms_service.send_custom_sms('+919876543210', long_message)
    assert result == False

def test_sms_service_initialization():
    """Test SMS service initialization."""
    app = Flask(__name__)
    app.config['TWILIO_ACCOUNT_SID'] = None  # Invalid configuration
    
    with pytest.raises(Exception):
        SMSService(app)

def test_sms_template_rendering(sms_service):
    """Test SMS template rendering."""
    template_name = 'verification.txt'
    context = {
        'otp': '123456'
    }
    
    rendered_content = sms_service.render_template(template_name, context)
    assert rendered_content is not None
    assert '123456' in rendered_content

def test_sms_character_limit(sms_service):
    """Test SMS character limit handling."""
    # Test with message within limit
    message = 'x' * 160
    result = sms_service.send_custom_sms('+919876543210', message)
    assert result == True
    
    # Test with message exceeding limit
    message = 'x' * 161
    result = sms_service.send_custom_sms('+919876543210', message)
    assert result == False

def test_sms_unicode_support(sms_service):
    """Test SMS Unicode character support."""
    # Test with ASCII characters
    message = 'Test message'
    result = sms_service.send_custom_sms('+919876543210', message)
    assert result == True
    
    # Test with Unicode characters
    message = 'Test message with emoji 😊'
    result = sms_service.send_custom_sms('+919876543210', message)
    assert result == True 