import pytest
from datetime import datetime, timedelta
from models import (
    User,
    Donor,
    BloodBank,
    BloodRequest,
    Donation,
    BloodInventory,
    BloodGroup,
    Location,
    Notification,
    Feedback,
    EmergencyRequest
)

@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test@123',
        'phone': '9876543210',
        'role': 'donor'
    }

@pytest.fixture
def donor_data():
    return {
        'user_id': 1,
        'blood_group': 'A+',
        'date_of_birth': datetime.now() - timedelta(days=365*25),
        'gender': 'M',
        'weight': 60,
        'last_donation_date': None,
        'is_available': True,
        'address': 'Test Address',
        'pincode': '110001',
        'latitude': 28.6139,
        'longitude': 77.2090
    }

@pytest.fixture
def blood_bank_data():
    return {
        'name': 'Test Blood Bank',
        'license_number': 'BB123456',
        'address': 'Test Address',
        'pincode': '110001',
        'latitude': 28.6139,
        'longitude': 77.2090,
        'contact_number': '9876543210',
        'email': 'bloodbank@example.com',
        'is_verified': True
    }

@pytest.fixture
def blood_request_data():
    return {
        'patient_name': 'Test Patient',
        'blood_group': 'A+',
        'units_required': 2,
        'hospital_name': 'Test Hospital',
        'hospital_address': 'Test Address',
        'contact_number': '9876543210',
        'urgency_level': 'high',
        'status': 'pending'
    }

def test_user_creation(user_data):
    """Test user model creation and validation."""
    user = User(**user_data)
    
    assert user.username == user_data['username']
    assert user.email == user_data['email']
    assert user.phone == user_data['phone']
    assert user.role == user_data['role']
    assert user.is_active == True
    assert user.is_verified == False
    assert user.created_at is not None
    assert user.updated_at is not None
    
    # Test password hashing
    assert user.password != user_data['password']
    assert user.check_password(user_data['password']) == True
    assert user.check_password('Wrong@123') == False

def test_donor_creation(donor_data):
    """Test donor model creation and validation."""
    donor = Donor(**donor_data)
    
    assert donor.user_id == donor_data['user_id']
    assert donor.blood_group == donor_data['blood_group']
    assert donor.date_of_birth == donor_data['date_of_birth']
    assert donor.gender == donor_data['gender']
    assert donor.weight == donor_data['weight']
    assert donor.is_available == donor_data['is_available']
    assert donor.address == donor_data['address']
    assert donor.pincode == donor_data['pincode']
    assert donor.latitude == donor_data['latitude']
    assert donor.longitude == donor_data['longitude']
    
    # Test age calculation
    assert donor.age == 25
    
    # Test eligibility
    assert donor.is_eligible() == True
    
    # Test with last donation date
    donor.last_donation_date = datetime.now() - timedelta(days=89)
    assert donor.is_eligible() == False
    donor.last_donation_date = datetime.now() - timedelta(days=91)
    assert donor.is_eligible() == True

def test_blood_bank_creation(blood_bank_data):
    """Test blood bank model creation and validation."""
    blood_bank = BloodBank(**blood_bank_data)
    
    assert blood_bank.name == blood_bank_data['name']
    assert blood_bank.license_number == blood_bank_data['license_number']
    assert blood_bank.address == blood_bank_data['address']
    assert blood_bank.pincode == blood_bank_data['pincode']
    assert blood_bank.latitude == blood_bank_data['latitude']
    assert blood_bank.longitude == blood_bank_data['longitude']
    assert blood_bank.contact_number == blood_bank_data['contact_number']
    assert blood_bank.email == blood_bank_data['email']
    assert blood_bank.is_verified == blood_bank_data['is_verified']

def test_blood_request_creation(blood_request_data):
    """Test blood request model creation and validation."""
    blood_request = BloodRequest(**blood_request_data)
    
    assert blood_request.patient_name == blood_request_data['patient_name']
    assert blood_request.blood_group == blood_request_data['blood_group']
    assert blood_request.units_required == blood_request_data['units_required']
    assert blood_request.hospital_name == blood_request_data['hospital_name']
    assert blood_request.hospital_address == blood_request_data['hospital_address']
    assert blood_request.contact_number == blood_request_data['contact_number']
    assert blood_request.urgency_level == blood_request_data['urgency_level']
    assert blood_request.status == blood_request_data['status']
    assert blood_request.created_at is not None
    assert blood_request.updated_at is not None

def test_donation_creation():
    """Test donation model creation and validation."""
    donation_data = {
        'donor_id': 1,
        'blood_bank_id': 1,
        'blood_group': 'A+',
        'units_donated': 1,
        'donation_date': datetime.now(),
        'status': 'completed'
    }
    
    donation = Donation(**donation_data)
    
    assert donation.donor_id == donation_data['donor_id']
    assert donation.blood_bank_id == donation_data['blood_bank_id']
    assert donation.blood_group == donation_data['blood_group']
    assert donation.units_donated == donation_data['units_donated']
    assert donation.donation_date == donation_data['donation_date']
    assert donation.status == donation_data['status']
    assert donation.created_at is not None
    assert donation.updated_at is not None

def test_blood_inventory_creation():
    """Test blood inventory model creation and validation."""
    inventory_data = {
        'blood_bank_id': 1,
        'blood_group': 'A+',
        'units_available': 10,
        'last_updated': datetime.now()
    }
    
    inventory = BloodInventory(**inventory_data)
    
    assert inventory.blood_bank_id == inventory_data['blood_bank_id']
    assert inventory.blood_group == inventory_data['blood_group']
    assert inventory.units_available == inventory_data['units_available']
    assert inventory.last_updated == inventory_data['last_updated']

def test_blood_group_creation():
    """Test blood group model creation and validation."""
    blood_group = BloodGroup(
        group='A+',
        description='A positive blood group'
    )
    
    assert blood_group.group == 'A+'
    assert blood_group.description == 'A positive blood group'

def test_location_creation():
    """Test location model creation and validation."""
    location = Location(
        pincode='110001',
        city='New Delhi',
        state='Delhi',
        country='India'
    )
    
    assert location.pincode == '110001'
    assert location.city == 'New Delhi'
    assert location.state == 'Delhi'
    assert location.country == 'India'

def test_notification_creation():
    """Test notification model creation and validation."""
    notification = Notification(
        user_id=1,
        title='Test Notification',
        message='This is a test notification',
        type='info',
        is_read=False
    )
    
    assert notification.user_id == 1
    assert notification.title == 'Test Notification'
    assert notification.message == 'This is a test notification'
    assert notification.type == 'info'
    assert notification.is_read == False
    assert notification.created_at is not None

def test_feedback_creation():
    """Test feedback model creation and validation."""
    feedback = Feedback(
        user_id=1,
        rating=5,
        comment='Great service!',
        feedback_type='donation'
    )
    
    assert feedback.user_id == 1
    assert feedback.rating == 5
    assert feedback.comment == 'Great service!'
    assert feedback.feedback_type == 'donation'
    assert feedback.created_at is not None

def test_emergency_request_creation():
    """Test emergency request model creation and validation."""
    emergency_request = EmergencyRequest(
        patient_name='Test Patient',
        blood_group='A+',
        units_required=2,
        hospital_name='Test Hospital',
        hospital_address='Test Address',
        contact_number='9876543210',
        urgency_level='critical',
        status='pending'
    )
    
    assert emergency_request.patient_name == 'Test Patient'
    assert emergency_request.blood_group == 'A+'
    assert emergency_request.units_required == 2
    assert emergency_request.hospital_name == 'Test Hospital'
    assert emergency_request.hospital_address == 'Test Address'
    assert emergency_request.contact_number == '9876543210'
    assert emergency_request.urgency_level == 'critical'
    assert emergency_request.status == 'pending'
    assert emergency_request.created_at is not None
    assert emergency_request.updated_at is not None 