import pytest
from location_service import LocationService
from flask import Flask
from models import Location, BloodBank, Donor

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['GOOGLE_MAPS_API_KEY'] = 'test-api-key'
    return app

@pytest.fixture
def location_service(app):
    return LocationService(app)

@pytest.fixture
def test_location():
    return Location(
        pincode='110001',
        city='New Delhi',
        state='Delhi',
        country='India',
        latitude=28.6139,
        longitude=77.2090
    )

@pytest.fixture
def test_blood_bank():
    return BloodBank(
        id=1,
        name='Test Blood Bank',
        address='Test Address',
        pincode='110001',
        latitude=28.6139,
        longitude=77.2090
    )

@pytest.fixture
def test_donor():
    return Donor(
        user_id=1,
        address='Test Address',
        pincode='110001',
        latitude=28.6139,
        longitude=77.2090
    )

def test_get_location_by_pincode(location_service, test_location):
    """Test getting location by pincode."""
    location = location_service.get_location_by_pincode('110001')
    assert location is not None
    assert location.pincode == test_location.pincode
    assert location.city == test_location.city
    assert location.state == test_location.state
    assert location.country == test_location.country

def test_get_nearby_blood_banks(location_service, test_blood_bank):
    """Test getting nearby blood banks."""
    blood_banks = location_service.get_nearby_blood_banks(
        latitude=28.6139,
        longitude=77.2090,
        radius=10  # 10 kilometers
    )
    assert isinstance(blood_banks, list)

def test_get_nearby_donors(location_service, test_donor):
    """Test getting nearby donors."""
    donors = location_service.get_nearby_donors(
        latitude=28.6139,
        longitude=77.2090,
        radius=10,  # 10 kilometers
        blood_group='A+'
    )
    assert isinstance(donors, list)

def test_calculate_distance(location_service):
    """Test calculating distance between two points."""
    # Test with known coordinates (Delhi to Mumbai)
    delhi_lat, delhi_lon = 28.6139, 77.2090
    mumbai_lat, mumbai_lon = 19.0760, 72.8777
    
    distance = location_service.calculate_distance(
        delhi_lat, delhi_lon,
        mumbai_lat, mumbai_lon
    )
    assert isinstance(distance, float)
    assert distance > 0
    assert abs(distance - 1150) < 50  # Approximate distance in km
    
    # Test with same coordinates
    distance = location_service.calculate_distance(
        delhi_lat, delhi_lon,
        delhi_lat, delhi_lon
    )
    assert distance == 0

def test_geocode_address(location_service):
    """Test geocoding an address."""
    address = 'Connaught Place, New Delhi'
    result = location_service.geocode_address(address)
    
    assert result is not None
    assert 'latitude' in result
    assert 'longitude' in result
    assert isinstance(result['latitude'], float)
    assert isinstance(result['longitude'], float)

def test_reverse_geocode(location_service):
    """Test reverse geocoding coordinates."""
    latitude = 28.6139
    longitude = 77.2090
    result = location_service.reverse_geocode(latitude, longitude)
    
    assert result is not None
    assert 'address' in result
    assert 'pincode' in result
    assert 'city' in result
    assert 'state' in result
    assert 'country' in result

def test_validate_coordinates(location_service):
    """Test coordinate validation."""
    # Test valid coordinates
    assert location_service.validate_coordinates(28.6139, 77.2090) == True
    
    # Test invalid coordinates
    assert location_service.validate_coordinates(91, 181) == False  # Latitude > 90
    assert location_service.validate_coordinates(-91, -181) == False  # Latitude < -90
    assert location_service.validate_coordinates(0, 181) == False  # Longitude > 180
    assert location_service.validate_coordinates(0, -181) == False  # Longitude < -180

def test_validate_pincode(location_service):
    """Test pincode validation."""
    # Test valid pincodes
    assert location_service.validate_pincode('110001') == True
    assert location_service.validate_pincode('400001') == True
    assert location_service.validate_pincode('560001') == True
    
    # Test invalid pincodes
    assert location_service.validate_pincode('12345') == False
    assert location_service.validate_pincode('1234567') == False
    assert location_service.validate_pincode('abcdef') == False
    assert location_service.validate_pincode('000000') == False

def test_get_location_suggestions(location_service):
    """Test getting location suggestions."""
    query = 'Delhi'
    suggestions = location_service.get_location_suggestions(query)
    
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
    assert all(isinstance(suggestion, dict) for suggestion in suggestions)
    assert all('pincode' in suggestion for suggestion in suggestions)
    assert all('city' in suggestion for suggestion in suggestions)
    assert all('state' in suggestion for suggestion in suggestions)

def test_get_route_directions(location_service):
    """Test getting route directions."""
    origin = {'latitude': 28.6139, 'longitude': 77.2090}  # Delhi
    destination = {'latitude': 19.0760, 'longitude': 72.8777}  # Mumbai
    
    directions = location_service.get_route_directions(origin, destination)
    
    assert directions is not None
    assert 'distance' in directions
    assert 'duration' in directions
    assert 'steps' in directions
    assert isinstance(directions['distance'], float)
    assert isinstance(directions['duration'], float)
    assert isinstance(directions['steps'], list)

def test_location_service_initialization():
    """Test location service initialization."""
    app = Flask(__name__)
    app.config['GOOGLE_MAPS_API_KEY'] = None  # Invalid configuration
    
    with pytest.raises(Exception):
        LocationService(app)

def test_error_handling(location_service):
    """Test error handling for invalid inputs."""
    # Test with invalid pincode
    location = location_service.get_location_by_pincode('invalid')
    assert location is None
    
    # Test with invalid coordinates for distance calculation
    distance = location_service.calculate_distance(91, 181, 0, 0)
    assert distance is None
    
    # Test with invalid address for geocoding
    result = location_service.geocode_address('')
    assert result is None
    
    # Test with invalid coordinates for reverse geocoding
    result = location_service.reverse_geocode(91, 181)
    assert result is None 