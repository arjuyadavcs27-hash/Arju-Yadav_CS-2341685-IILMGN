import pytest
from blood_bank_service import BloodBankService
from flask import Flask
from datetime import datetime
from models import BloodBank, BloodInventory, Donation, BloodRequest

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def blood_bank_service(app):
    return BloodBankService(app)

@pytest.fixture
def test_blood_bank():
    return BloodBank(
        id=1,
        name='Test Blood Bank',
        license_number='BB123456',
        address='Test Address',
        pincode='110001',
        latitude=28.6139,
        longitude=77.2090,
        contact_number='9876543210',
        email='bloodbank@example.com',
        is_verified=True
    )

@pytest.fixture
def test_blood_inventory(test_blood_bank):
    return BloodInventory(
        blood_bank_id=test_blood_bank.id,
        blood_group='A+',
        units_available=10,
        last_updated=datetime.now()
    )

@pytest.fixture
def test_donation(test_blood_bank):
    return Donation(
        id=1,
        blood_bank_id=test_blood_bank.id,
        blood_group='A+',
        units_donated=1,
        donation_date=datetime.now(),
        status='completed'
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
        urgency_level='high',
        status='pending'
    )

def test_register_blood_bank(blood_bank_service):
    """Test registering a new blood bank."""
    blood_bank_data = {
        'name': 'New Blood Bank',
        'license_number': 'BB789012',
        'address': 'New Address',
        'pincode': '110001',
        'latitude': 28.6139,
        'longitude': 77.2090,
        'contact_number': '9876543210',
        'email': 'new@example.com'
    }
    
    result = blood_bank_service.register_blood_bank(blood_bank_data)
    assert result is not None
    assert result.name == blood_bank_data['name']
    assert result.license_number == blood_bank_data['license_number']
    assert result.is_verified == False

def test_verify_blood_bank(blood_bank_service, test_blood_bank):
    """Test verifying a blood bank."""
    result = blood_bank_service.verify_blood_bank(test_blood_bank.id)
    assert result == True
    
    # Verify the blood bank is now marked as verified
    blood_bank = blood_bank_service.get_blood_bank(test_blood_bank.id)
    assert blood_bank.is_verified == True

def test_update_blood_bank(blood_bank_service, test_blood_bank):
    """Test updating blood bank information."""
    update_data = {
        'name': 'Updated Blood Bank',
        'address': 'Updated Address',
        'contact_number': '9876543211'
    }
    
    result = blood_bank_service.update_blood_bank(test_blood_bank.id, update_data)
    assert result == True
    
    # Verify the updates
    blood_bank = blood_bank_service.get_blood_bank(test_blood_bank.id)
    assert blood_bank.name == update_data['name']
    assert blood_bank.address == update_data['address']
    assert blood_bank.contact_number == update_data['contact_number']

def test_update_inventory(blood_bank_service, test_blood_bank):
    """Test updating blood inventory."""
    inventory_data = {
        'blood_group': 'A+',
        'units_available': 15
    }
    
    result = blood_bank_service.update_inventory(test_blood_bank.id, inventory_data)
    assert result == True
    
    # Verify the inventory update
    inventory = blood_bank_service.get_inventory(test_blood_bank.id, 'A+')
    assert inventory.units_available == inventory_data['units_available']

def test_process_donation(blood_bank_service, test_blood_bank, test_donation):
    """Test processing a blood donation."""
    result = blood_bank_service.process_donation(test_donation)
    assert result == True
    
    # Verify the inventory was updated
    inventory = blood_bank_service.get_inventory(test_blood_bank.id, test_donation.blood_group)
    assert inventory.units_available > 0

def test_process_blood_request(blood_bank_service, test_blood_bank, test_blood_request):
    """Test processing a blood request."""
    result = blood_bank_service.process_blood_request(test_blood_bank.id, test_blood_request)
    assert result == True
    
    # Verify the inventory was updated
    inventory = blood_bank_service.get_inventory(test_blood_bank.id, test_blood_request.blood_group)
    assert inventory.units_available >= 0

def test_get_blood_bank(blood_bank_service, test_blood_bank):
    """Test getting blood bank details."""
    blood_bank = blood_bank_service.get_blood_bank(test_blood_bank.id)
    assert blood_bank is not None
    assert blood_bank.id == test_blood_bank.id
    assert blood_bank.name == test_blood_bank.name

def test_get_inventory(blood_bank_service, test_blood_bank, test_blood_inventory):
    """Test getting blood inventory."""
    inventory = blood_bank_service.get_inventory(test_blood_bank.id, 'A+')
    assert inventory is not None
    assert inventory.blood_bank_id == test_blood_bank.id
    assert inventory.blood_group == 'A+'

def test_get_donations(blood_bank_service, test_blood_bank, test_donation):
    """Test getting blood bank donations."""
    donations = blood_bank_service.get_donations(test_blood_bank.id)
    assert isinstance(donations, list)
    assert len(donations) > 0
    assert all(donation.blood_bank_id == test_blood_bank.id for donation in donations)

def test_get_blood_requests(blood_bank_service, test_blood_bank, test_blood_request):
    """Test getting blood bank requests."""
    requests = blood_bank_service.get_blood_requests(test_blood_bank.id)
    assert isinstance(requests, list)
    assert len(requests) > 0

def test_search_blood_banks(blood_bank_service, test_blood_bank):
    """Test searching blood banks."""
    # Search by location
    blood_banks = blood_bank_service.search_blood_banks(
        latitude=28.6139,
        longitude=77.2090,
        radius=10
    )
    assert isinstance(blood_banks, list)
    assert len(blood_banks) > 0
    
    # Search by blood group
    blood_banks = blood_bank_service.search_blood_banks(blood_group='A+')
    assert isinstance(blood_banks, list)
    assert len(blood_banks) > 0

def test_get_blood_availability(blood_bank_service, test_blood_bank):
    """Test getting blood availability."""
    availability = blood_bank_service.get_blood_availability(test_blood_bank.id)
    assert isinstance(availability, dict)
    assert all(isinstance(count, int) for count in availability.values())

def test_blood_bank_service_initialization():
    """Test blood bank service initialization."""
    app = Flask(__name__)
    blood_bank_service = BloodBankService(app)
    assert blood_bank_service is not None

def test_error_handling(blood_bank_service):
    """Test error handling for invalid inputs."""
    # Test with invalid blood bank ID
    blood_bank = blood_bank_service.get_blood_bank(999)
    assert blood_bank is None
    
    # Test with invalid blood group
    inventory = blood_bank_service.get_inventory(1, 'Invalid')
    assert inventory is None
    
    # Test with invalid donation
    result = blood_bank_service.process_donation(None)
    assert result == False
    
    # Test with invalid blood request
    result = blood_bank_service.process_blood_request(1, None)
    assert result == False 