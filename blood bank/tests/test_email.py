import pytest
from email_service import EmailService
from flask import Flask
from datetime import datetime

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'test@example.com'
    app.config['MAIL_PASSWORD'] = 'test-password'
    return app

@pytest.fixture
def email_service(app):
    return EmailService(app)

def test_send_verification_email(email_service):
    """Test sending verification email."""
    recipient = 'test@example.com'
    token = 'test-verification-token'
    
    result = email_service.send_verification_email(recipient, token)
    assert result == True

def test_send_password_reset_email(email_service):
    """Test sending password reset email."""
    recipient = 'test@example.com'
    token = 'test-reset-token'
    
    result = email_service.send_password_reset_email(recipient, token)
    assert result == True

def test_send_donation_reminder(email_service):
    """Test sending donation reminder email."""
    recipient = 'test@example.com'
    last_donation_date = datetime.now() - timedelta(days=89)
    
    result = email_service.send_donation_reminder(recipient, last_donation_date)
    assert result == True

def test_send_blood_request_notification(email_service):
    """Test sending blood request notification email."""
    recipient = 'test@example.com'
    request_data = {
        'patient_name': 'Test Patient',
        'blood_group': 'A+',
        'units_required': 2,
        'hospital_name': 'Test Hospital',
        'hospital_address': 'Test Address',
        'contact_number': '9876543210',
        'urgency_level': 'high'
    }
    
    result = email_service.send_blood_request_notification(recipient, request_data)
    assert result == True

def test_send_emergency_alert(email_service):
    """Test sending emergency alert email."""
    recipient = 'test@example.com'
    emergency_data = {
        'patient_name': 'Emergency Patient',
        'blood_group': 'A+',
        'units_required': 2,
        'hospital_name': 'Emergency Hospital',
        'hospital_address': 'Emergency Address',
        'contact_number': '9876543210',
        'urgency_level': 'critical'
    }
    
    result = email_service.send_emergency_alert(recipient, emergency_data)
    assert result == True

def test_send_donation_confirmation(email_service):
    """Test sending donation confirmation email."""
    recipient = 'test@example.com'
    donation_data = {
        'donation_date': datetime.now(),
        'blood_group': 'A+',
        'units_donated': 1,
        'blood_bank_name': 'Test Blood Bank'
    }
    
    result = email_service.send_donation_confirmation(recipient, donation_data)
    assert result == True

def test_send_blood_availability_notification(email_service):
    """Test sending blood availability notification email."""
    recipient = 'test@example.com'
    availability_data = {
        'blood_group': 'A+',
        'units_available': 10,
        'blood_bank_name': 'Test Blood Bank',
        'blood_bank_address': 'Test Address',
        'contact_number': '9876543210'
    }
    
    result = email_service.send_blood_availability_notification(recipient, availability_data)
    assert result == True

def test_send_feedback_acknowledgement(email_service):
    """Test sending feedback acknowledgement email."""
    recipient = 'test@example.com'
    feedback_data = {
        'rating': 5,
        'comment': 'Great service!',
        'feedback_type': 'donation'
    }
    
    result = email_service.send_feedback_acknowledgement(recipient, feedback_data)
    assert result == True

def test_send_newsletter(email_service):
    """Test sending newsletter email."""
    recipient = 'test@example.com'
    newsletter_data = {
        'subject': 'Monthly Newsletter',
        'content': 'This is a test newsletter content.'
    }
    
    result = email_service.send_newsletter(recipient, newsletter_data)
    assert result == True

def test_send_custom_email(email_service):
    """Test sending custom email."""
    recipient = 'test@example.com'
    subject = 'Test Subject'
    body = 'This is a test email body.'
    
    result = email_service.send_custom_email(recipient, subject, body)
    assert result == True

def test_email_template_rendering(email_service):
    """Test email template rendering."""
    template_name = 'verification.html'
    context = {
        'username': 'Test User',
        'verification_link': 'http://example.com/verify/test-token'
    }
    
    rendered_content = email_service.render_template(template_name, context)
    assert rendered_content is not None
    assert 'Test User' in rendered_content
    assert 'http://example.com/verify/test-token' in rendered_content

def test_email_validation(email_service):
    """Test email validation."""
    assert email_service.validate_email('test@example.com') == True
    assert email_service.validate_email('invalid-email') == False
    assert email_service.validate_email('test@example') == False
    assert email_service.validate_email('@example.com') == False
    assert email_service.validate_email('test@.com') == False

def test_email_sending_error_handling(email_service):
    """Test email sending error handling."""
    # Test with invalid recipient
    result = email_service.send_custom_email('invalid-email', 'Test', 'Test')
    assert result == False
    
    # Test with empty subject
    result = email_service.send_custom_email('test@example.com', '', 'Test')
    assert result == False
    
    # Test with empty body
    result = email_service.send_custom_email('test@example.com', 'Test', '')
    assert result == False

def test_email_service_initialization():
    """Test email service initialization."""
    app = Flask(__name__)
    app.config['MAIL_SERVER'] = None  # Invalid configuration
    
    with pytest.raises(Exception):
        EmailService(app) 