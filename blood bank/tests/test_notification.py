import pytest
from notification_service import NotificationService
from flask import Flask
from datetime import datetime, timedelta
from models import User, Donor, BloodBank, BloodRequest, Donation

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def notification_service(app):
    return NotificationService(app)

@pytest.fixture
def test_user():
    return User(
        id=1,
        username='testuser',
        email='test@example.com',
        phone='9876543210',
        role='donor'
    )

@pytest.fixture
def test_donor(test_user):
    return Donor(
        user_id=test_user.id,
        blood_group='A+',
        date_of_birth=datetime.now() - timedelta(days=365*25),
        gender='M',
        weight=60,
        is_available=True
    )

@pytest.fixture
def test_blood_bank():
    return BloodBank(
        id=1,
        name='Test Blood Bank',
        license_number='BB123456',
        address='Test Address',
        contact_number='9876543210',
        email='bloodbank@example.com'
    )

@pytest.fixture
def test_blood_request():
    return BloodRequest(
        id=1,
        patient_name='Test Patient',
        blood_group='A+',
        units_required=2,
        hospital_name='Test Hospital',
        hospital_address='Test Address',
        contact_number='9876543210',
        urgency_level='high'
    )

@pytest.fixture
def test_donation(test_donor, test_blood_bank):
    return Donation(
        id=1,
        donor_id=test_donor.user_id,
        blood_bank_id=test_blood_bank.id,
        blood_group='A+',
        units_donated=1,
        donation_date=datetime.now()
    )

def test_send_verification_notification(notification_service, test_user):
    """Test sending verification notification."""
    result = notification_service.send_verification_notification(test_user)
    assert result == True

def test_send_password_reset_notification(notification_service, test_user):
    """Test sending password reset notification."""
    result = notification_service.send_password_reset_notification(test_user)
    assert result == True

def test_send_donation_reminder_notification(notification_service, test_user, test_donor):
    """Test sending donation reminder notification."""
    result = notification_service.send_donation_reminder_notification(test_user, test_donor)
    assert result == True

def test_send_blood_request_notification(notification_service, test_user, test_blood_request):
    """Test sending blood request notification."""
    result = notification_service.send_blood_request_notification(test_user, test_blood_request)
    assert result == True

def test_send_emergency_alert_notification(notification_service, test_user, test_blood_request):
    """Test sending emergency alert notification."""
    result = notification_service.send_emergency_alert_notification(test_user, test_blood_request)
    assert result == True

def test_send_donation_confirmation_notification(notification_service, test_user, test_donation):
    """Test sending donation confirmation notification."""
    result = notification_service.send_donation_confirmation_notification(test_user, test_donation)
    assert result == True

def test_send_blood_availability_notification(notification_service, test_user, test_blood_bank):
    """Test sending blood availability notification."""
    availability_data = {
        'blood_group': 'A+',
        'units_available': 10
    }
    result = notification_service.send_blood_availability_notification(test_user, test_blood_bank, availability_data)
    assert result == True

def test_send_feedback_acknowledgement_notification(notification_service, test_user):
    """Test sending feedback acknowledgement notification."""
    feedback_data = {
        'rating': 5,
        'comment': 'Great service!',
        'feedback_type': 'donation'
    }
    result = notification_service.send_feedback_acknowledgement_notification(test_user, feedback_data)
    assert result == True

def test_send_custom_notification(notification_service, test_user):
    """Test sending custom notification."""
    notification_data = {
        'title': 'Test Notification',
        'message': 'This is a test notification',
        'type': 'info'
    }
    result = notification_service.send_custom_notification(test_user, notification_data)
    assert result == True

def test_get_user_notifications(notification_service, test_user):
    """Test getting user notifications."""
    notifications = notification_service.get_user_notifications(test_user.id)
    assert isinstance(notifications, list)

def test_mark_notification_as_read(notification_service, test_user):
    """Test marking notification as read."""
    # First create a notification
    notification_data = {
        'title': 'Test Notification',
        'message': 'This is a test notification',
        'type': 'info'
    }
    notification_service.send_custom_notification(test_user, notification_data)
    
    # Then mark it as read
    notifications = notification_service.get_user_notifications(test_user.id)
    if notifications:
        result = notification_service.mark_notification_as_read(notifications[0].id)
        assert result == True

def test_delete_notification(notification_service, test_user):
    """Test deleting notification."""
    # First create a notification
    notification_data = {
        'title': 'Test Notification',
        'message': 'This is a test notification',
        'type': 'info'
    }
    notification_service.send_custom_notification(test_user, notification_data)
    
    # Then delete it
    notifications = notification_service.get_user_notifications(test_user.id)
    if notifications:
        result = notification_service.delete_notification(notifications[0].id)
        assert result == True

def test_notification_priority(notification_service, test_user):
    """Test notification priority handling."""
    # Test high priority notification
    high_priority_data = {
        'title': 'High Priority',
        'message': 'This is a high priority notification',
        'type': 'emergency',
        'priority': 'high'
    }
    result = notification_service.send_custom_notification(test_user, high_priority_data)
    assert result == True
    
    # Test normal priority notification
    normal_priority_data = {
        'title': 'Normal Priority',
        'message': 'This is a normal priority notification',
        'type': 'info',
        'priority': 'normal'
    }
    result = notification_service.send_custom_notification(test_user, normal_priority_data)
    assert result == True

def test_notification_expiry(notification_service, test_user):
    """Test notification expiry handling."""
    # Test notification with expiry
    expiry_data = {
        'title': 'Expiring Notification',
        'message': 'This notification will expire',
        'type': 'info',
        'expires_at': datetime.now() + timedelta(hours=1)
    }
    result = notification_service.send_custom_notification(test_user, expiry_data)
    assert result == True

def test_notification_error_handling(notification_service):
    """Test notification error handling."""
    # Test with invalid user
    result = notification_service.send_custom_notification(None, {'title': 'Test'})
    assert result == False
    
    # Test with empty notification data
    result = notification_service.send_custom_notification(test_user, {})
    assert result == False
    
    # Test with missing required fields
    result = notification_service.send_custom_notification(test_user, {'title': 'Test'})
    assert result == False

def test_notification_service_initialization():
    """Test notification service initialization."""
    app = Flask(__name__)
    notification_service = NotificationService(app)
    assert notification_service is not None 