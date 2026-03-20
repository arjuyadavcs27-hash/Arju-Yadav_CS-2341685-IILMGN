import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from api.auth import auth_bp
from utils.helpers import validate_indian_mobile, validate_email, hash_password, verify_password
import json

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_validate_indian_mobile():
    assert validate_indian_mobile('9876543210') == True
    assert validate_indian_mobile('1234567890') == False
    assert validate_indian_mobile('987654321') == False
    assert validate_indian_mobile('98765432101') == False
    assert validate_indian_mobile('abcdefghij') == False

def test_validate_email():
    assert validate_email('test@example.com') == True
    assert validate_email('test.example.com') == False
    assert validate_email('test@example') == False
    assert validate_email('@example.com') == False
    assert validate_email('test@.com') == False

def test_password_hashing():
    password = 'Test@123'
    hashed = hash_password(password)
    assert verify_password(password, hashed) == True
    assert verify_password('Wrong@123', hashed) == False

def test_login_missing_credentials(client):
    response = client.post('/api/auth/login', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Username and password are required'

def test_login_invalid_credentials(client):
    response = client.post('/api/auth/login', json={
        'username': 'test@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Invalid credentials'

def test_register_missing_fields(client):
    response = client.post('/api/auth/register', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert 'fields' in data

def test_register_invalid_email(client):
    response = client.post('/api/auth/register', json={
        'email': 'invalid-email',
        'mobile': '9876543210',
        'password': 'Test@123',
        'name': 'Test User',
        'role': 'donor'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Invalid email format'

def test_register_invalid_mobile(client):
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'mobile': '1234567890',
        'password': 'Test@123',
        'name': 'Test User',
        'role': 'donor'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Invalid mobile number format'

def test_register_weak_password(client):
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'mobile': '9876543210',
        'password': 'weak',
        'name': 'Test User',
        'role': 'donor'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Password does not meet requirements'

def test_forgot_password_missing_email(client):
    response = client.post('/api/auth/forgot-password', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Email is required'

def test_forgot_password_invalid_email(client):
    response = client.post('/api/auth/forgot-password', json={
        'email': 'nonexistent@example.com'
    })
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Email not found'

def test_reset_password_missing_token(client):
    response = client.post('/api/auth/reset-password', json={
        'password': 'New@123'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Token and new password are required'

def test_reset_password_invalid_token(client):
    response = client.post('/api/auth/reset-password', json={
        'token': 'invalid-token',
        'password': 'New@123'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Invalid or expired reset token'

def test_reset_password_weak_password(client):
    response = client.post('/api/auth/reset-password', json={
        'token': 'valid-token',
        'password': 'weak'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Password does not meet requirements'

def test_account_locking(client):
    # Test multiple failed login attempts
    for _ in range(5):
        response = client.post('/api/auth/login', json={
            'username': 'test@example.com',
            'password': 'wrongpassword'
        })
    
    # Next attempt should be locked
    response = client.post('/api/auth/login', json={
        'username': 'test@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'message' in data
    assert 'Account is locked' in data['message']

def test_rate_limiting(client):
    # Test multiple requests within a short time
    for _ in range(100):
        response = client.post('/api/auth/login', json={
            'username': 'test@example.com',
            'password': 'wrongpassword'
        })
    
    # Next request should be rate limited
    response = client.post('/api/auth/login', json={
        'username': 'test@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 429
    data = json.loads(response.data)
    assert 'message' in data
    assert 'Rate limit exceeded' in data['message'] 