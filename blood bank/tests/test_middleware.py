import pytest
from flask import Flask, request, jsonify
from middleware.security import (
    rate_limit,
    validate_request_data,
    validate_content_type,
    validate_file_upload,
    validate_origin,
    validate_user_agent,
    log_request,
    validate_api_key,
    prevent_brute_force
)
import os
from datetime import datetime, timedelta

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['API_KEY'] = 'test-api-key'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_rate_limit(app):
    @app.route('/test-rate-limit')
    @rate_limit(max_requests=2, time_window=60)
    def test_route():
        return jsonify({'message': 'success'})
    
    # First two requests should succeed
    response = client.get('/test-rate-limit')
    assert response.status_code == 200
    response = client.get('/test-rate-limit')
    assert response.status_code == 200
    
    # Third request should be rate limited
    response = client.get('/test-rate-limit')
    assert response.status_code == 429
    data = response.get_json()
    assert 'message' in data
    assert 'Rate limit exceeded' in data['message']

def test_validate_request_data(app):
    @app.route('/test-validate-data', methods=['POST'])
    @validate_request_data(['name', 'email'])
    def test_route():
        return jsonify({'message': 'success'})
    
    # Test missing required fields
    response = client.post('/test-validate-data', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    assert 'fields' in data
    assert 'name' in data['fields']
    assert 'email' in data['fields']
    
    # Test with all required fields
    response = client.post('/test-validate-data', json={
        'name': 'Test User',
        'email': 'test@example.com'
    })
    assert response.status_code == 200

def test_validate_content_type(app):
    @app.route('/test-content-type', methods=['POST'])
    @validate_content_type(['application/json'])
    def test_route():
        return jsonify({'message': 'success'})
    
    # Test invalid content type
    response = client.post('/test-content-type', 
                         data='test data',
                         headers={'Content-Type': 'text/plain'})
    assert response.status_code == 415
    
    # Test valid content type
    response = client.post('/test-content-type',
                         json={'test': 'data'},
                         headers={'Content-Type': 'application/json'})
    assert response.status_code == 200

def test_validate_file_upload(app):
    @app.route('/test-file-upload', methods=['POST'])
    @validate_file_upload(['jpg', 'png'], 1024 * 1024)  # 1MB max size
    def test_route():
        return jsonify({'message': 'success'})
    
    # Test missing file
    response = client.post('/test-file-upload')
    assert response.status_code == 400
    
    # Test invalid file type
    with open('test.txt', 'w') as f:
        f.write('test')
    with open('test.txt', 'rb') as f:
        response = client.post('/test-file-upload', data={'file': f})
    assert response.status_code == 400
    os.remove('test.txt')
    
    # Test file too large
    with open('large.txt', 'w') as f:
        f.write('x' * (1024 * 1024 + 1))
    with open('large.txt', 'rb') as f:
        response = client.post('/test-file-upload', data={'file': f})
    assert response.status_code == 400
    os.remove('large.txt')

def test_validate_origin(app):
    @app.route('/test-origin')
    @validate_origin(['http://localhost:3000'])
    def test_route():
        return jsonify({'message': 'success'})
    
    # Test invalid origin
    response = client.get('/test-origin', 
                         headers={'Origin': 'http://malicious.com'})
    assert response.status_code == 403
    
    # Test valid origin
    response = client.get('/test-origin',
                         headers={'Origin': 'http://localhost:3000'})
    assert response.status_code == 200

def test_validate_user_agent(app):
    @app.route('/test-user-agent')
    @validate_user_agent()
    def test_route():
        return jsonify({'message': 'success'})
    
    # Test missing user agent
    response = client.get('/test-user-agent')
    assert response.status_code == 400
    
    # Test with user agent
    response = client.get('/test-user-agent',
                         headers={'User-Agent': 'Test Browser'})
    assert response.status_code == 200

def test_validate_api_key(app):
    @app.route('/test-api-key')
    @validate_api_key()
    def test_route():
        return jsonify({'message': 'success'})
    
    # Test missing API key
    response = client.get('/test-api-key')
    assert response.status_code == 401
    
    # Test invalid API key
    response = client.get('/test-api-key',
                         headers={'X-API-Key': 'invalid-key'})
    assert response.status_code == 401
    
    # Test valid API key
    response = client.get('/test-api-key',
                         headers={'X-API-Key': 'test-api-key'})
    assert response.status_code == 200

def test_prevent_brute_force(app):
    @app.route('/test-brute-force')
    @prevent_brute_force(max_attempts=3, lock_time=60)
    def test_route():
        return jsonify({'message': 'success'})
    
    # Test multiple failed attempts
    for _ in range(3):
        response = client.get('/test-brute-force')
        assert response.status_code == 200
    
    # Test locked account
    response = client.get('/test-brute-force')
    assert response.status_code == 403
    data = response.get_json()
    assert 'message' in data
    assert 'Account locked' in data['message']

def test_log_request(app, monkeypatch):
    logged_messages = []
    
    def mock_log_info(message):
        logged_messages.append(message)
    
    monkeypatch.setattr('logging.Logger.info', mock_log_info)
    
    @app.route('/test-log')
    @log_request()
    def test_route():
        return jsonify({'message': 'success'})
    
    response = client.get('/test-log',
                         headers={
                             'User-Agent': 'Test Browser',
                             'Referer': 'http://test.com'
                         })
    assert response.status_code == 200
    assert len(logged_messages) > 0
    assert any('Request: GET /test-log' in msg for msg in logged_messages)
    assert any('User-Agent: Test Browser' in msg for msg in logged_messages)
    assert any('Referrer: http://test.com' in msg for msg in logged_messages) 