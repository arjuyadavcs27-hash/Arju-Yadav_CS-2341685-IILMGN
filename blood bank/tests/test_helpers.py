import pytest
from datetime import datetime, timedelta
from utils.helpers import (
    validate_indian_mobile,
    validate_email,
    hash_password,
    verify_password,
    validate_blood_type,
    calculate_age,
    is_donation_eligible,
    format_phone_number,
    sanitize_input,
    get_distance,
    generate_otp,
    validate_pincode
)

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

def test_validate_blood_type():
    assert validate_blood_type('A+') == True
    assert validate_blood_type('B-') == True
    assert validate_blood_type('AB+') == True
    assert validate_blood_type('O-') == True
    assert validate_blood_type('X+') == False
    assert validate_blood_type('A') == False
    assert validate_blood_type('+') == False

def test_calculate_age():
    today = datetime.today()
    birth_date = today.replace(year=today.year - 25)
    assert calculate_age(birth_date) == 25
    
    # Test edge case: birthday today
    birth_date = today.replace(year=today.year - 30)
    assert calculate_age(birth_date) == 30
    
    # Test edge case: birthday tomorrow
    birth_date = today.replace(year=today.year - 20, day=today.day + 1)
    assert calculate_age(birth_date) == 19

def test_is_donation_eligible():
    # Test age limits
    assert is_donation_eligible(17, 50, None) == False  # Too young
    assert is_donation_eligible(66, 50, None) == False  # Too old
    assert is_donation_eligible(25, 50, None) == True   # Valid age
    
    # Test weight limits
    assert is_donation_eligible(25, 44, None) == False  # Underweight
    assert is_donation_eligible(25, 45, None) == True   # Minimum weight
    assert is_donation_eligible(25, 50, None) == True   # Valid weight
    
    # Test donation interval
    last_donation = datetime.now() - timedelta(days=89)
    assert is_donation_eligible(25, 50, last_donation) == False  # Too soon
    last_donation = datetime.now() - timedelta(days=90)
    assert is_donation_eligible(25, 50, last_donation) == True   # Valid interval
    last_donation = datetime.now() - timedelta(days=100)
    assert is_donation_eligible(25, 50, last_donation) == True   # Valid interval

def test_format_phone_number():
    assert format_phone_number('9876543210') == '+91 98765 43210'
    assert format_phone_number('98765 43210') == '+91 98765 43210'
    assert format_phone_number('98765-43210') == '+91 98765 43210'
    assert format_phone_number('+919876543210') == '+91 98765 43210'
    assert format_phone_number('invalid') == 'invalid'

def test_sanitize_input():
    data = {
        'name': '<script>alert("xss")</script>John',
        'email': 'test@example.com',
        'age': 25,
        'html': '<p>Hello</p>'
    }
    sanitized = sanitize_input(data)
    assert sanitized['name'] == 'John'
    assert sanitized['email'] == 'test@example.com'
    assert sanitized['age'] == 25
    assert sanitized['html'] == 'Hello'

def test_get_distance():
    # Test with known coordinates (Delhi to Mumbai)
    delhi_lat, delhi_lon = 28.6139, 77.2090
    mumbai_lat, mumbai_lon = 19.0760, 72.8777
    
    distance = get_distance(delhi_lat, delhi_lon, mumbai_lat, mumbai_lon)
    assert isinstance(distance, float)
    assert distance > 0
    assert abs(distance - 1150) < 50  # Approximate distance in km
    
    # Test with same coordinates
    assert get_distance(delhi_lat, delhi_lon, delhi_lat, delhi_lon) == 0

def test_generate_otp():
    otp = generate_otp()
    assert len(otp) == 6
    assert otp.isdigit()
    
    # Test multiple generations
    otps = set(generate_otp() for _ in range(100))
    assert len(otps) > 1  # Should have some variation

def test_validate_pincode():
    assert validate_pincode('110001') == True
    assert validate_pincode('400001') == True
    assert validate_pincode('560001') == True
    assert validate_pincode('12345') == False
    assert validate_pincode('1234567') == False
    assert validate_pincode('abcdef') == False
    assert validate_pincode('000000') == False
    assert validate_pincode('123456') == True 