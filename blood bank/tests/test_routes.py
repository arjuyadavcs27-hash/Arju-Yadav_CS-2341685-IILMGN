import pytest
from flask import Flask, jsonify
from flask_jwt_extended import create_access_token
from routes import (
    auth_bp,
    donor_bp,
    blood_bank_bp,
    blood_request_bp,
    donation_bp,
    inventory_bp,
    location_bp,
    notification_bp,
    feedback_bp,
    emergency_bp
)
from models import User, Donor, BloodBank, BloodRequest, Donation, BloodInventory, Location, Notification, Feedback, EmergencyRequest
from datetime import datetime, timedelta

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(blood_bank_bp)
    app.register_blueprint(blood_request_bp)
    app.register_blueprint(donation_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(emergency_bp)
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers():
    user = User(
        username='testuser',
        email='test@example.com',
        password='Test@123',
        role='donor'
    )
    access_token = create_access_token(identity=user.id)
    return {'Authorization': f'Bearer {access_token}'}

def test_register_user(client):
    """Test user registration endpoint."""
    response = client.post('/auth/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'Test@123',
        'phone': '9876543210',
        'role': 'donor'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert 'User registered successfully' in data['message']
    assert 'user' in data

def test_login_user(client):
    """Test user login endpoint."""
    # First register a user
    client.post('/auth/register', json={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'Test@123',
        'phone': '9876543210',
        'role': 'donor'
    })
    
    # Then try to login
    response = client.post('/auth/login', json={
        'email': 'login@example.com',
        'password': 'Test@123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_get_donor_profile(client, auth_headers):
    """Test getting donor profile endpoint."""
    response = client.get('/donor/profile', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'donor' in data

def test_update_donor_profile(client, auth_headers):
    """Test updating donor profile endpoint."""
    response = client.put('/donor/profile', json={
        'blood_group': 'A+',
        'weight': 65,
        'address': 'New Address',
        'pincode': '110001'
    }, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert 'Profile updated successfully' in data['message']

def test_create_blood_request(client, auth_headers):
    """Test creating blood request endpoint."""
    response = client.post('/blood-request', json={
        'patient_name': 'Test Patient',
        'blood_group': 'A+',
        'units_required': 2,
        'hospital_name': 'Test Hospital',
        'hospital_address': 'Test Address',
        'contact_number': '9876543210',
        'urgency_level': 'high'
    }, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert 'Blood request created successfully' in data['message']
    assert 'request' in data

def test_get_blood_requests(client, auth_headers):
    """Test getting blood requests endpoint."""
    response = client.get('/blood-request', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'requests' in data
    assert isinstance(data['requests'], list)

def test_create_donation(client, auth_headers):
    """Test creating donation endpoint."""
    response = client.post('/donation', json={
        'blood_bank_id': 1,
        'blood_group': 'A+',
        'units_donated': 1
    }, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert 'Donation recorded successfully' in data['message']
    assert 'donation' in data

def test_get_donations(client, auth_headers):
    """Test getting donations endpoint."""
    response = client.get('/donation', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'donations' in data
    assert isinstance(data['donations'], list)

def test_get_blood_inventory(client, auth_headers):
    """Test getting blood inventory endpoint."""
    response = client.get('/inventory', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'inventory' in data
    assert isinstance(data['inventory'], list)

def test_search_blood_banks(client, auth_headers):
    """Test searching blood banks endpoint."""
    response = client.get('/blood-bank/search?pincode=110001', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'blood_banks' in data
    assert isinstance(data['blood_banks'], list)

def test_get_notifications(client, auth_headers):
    """Test getting notifications endpoint."""
    response = client.get('/notification', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'notifications' in data
    assert isinstance(data['notifications'], list)

def test_create_feedback(client, auth_headers):
    """Test creating feedback endpoint."""
    response = client.post('/feedback', json={
        'rating': 5,
        'comment': 'Great service!',
        'feedback_type': 'donation'
    }, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert 'Feedback submitted successfully' in data['message']
    assert 'feedback' in data

def test_create_emergency_request(client, auth_headers):
    """Test creating emergency request endpoint."""
    response = client.post('/emergency', json={
        'patient_name': 'Emergency Patient',
        'blood_group': 'A+',
        'units_required': 2,
        'hospital_name': 'Emergency Hospital',
        'hospital_address': 'Emergency Address',
        'contact_number': '9876543210',
        'urgency_level': 'critical'
    }, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert 'Emergency request created successfully' in data['message']
    assert 'request' in data

def test_get_locations(client, auth_headers):
    """Test getting locations endpoint."""
    response = client.get('/location', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'locations' in data
    assert isinstance(data['locations'], list)

def test_error_handling(client):
    """Test error handling for invalid routes."""
    response = client.get('/invalid-route')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert 'Not Found' in data['error']

def test_unauthorized_access(client):
    """Test unauthorized access to protected routes."""
    response = client.get('/donor/profile')
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data
    assert 'Unauthorized' in data['error'] 