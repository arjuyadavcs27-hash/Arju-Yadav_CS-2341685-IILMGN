from flask import request, jsonify, current_app
from functools import wraps
import jwt
from datetime import datetime
import os
from typing import Callable, Any
import re
from utils.helpers import sanitize_input

def rate_limit(max_requests: int, time_window: int) -> Callable:
    """Rate limiting decorator."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # In production, use Redis or similar for rate limiting
            # This is a simple in-memory implementation
            ip = request.remote_addr
            key = f"rate_limit:{ip}"
            
            # Get current count
            count = getattr(current_app, '_rate_limit', {}).get(key, 0)
            
            # Check if limit exceeded
            if count >= max_requests:
                return jsonify({
                    'message': 'Rate limit exceeded',
                    'retry_after': time_window
                }), 429
            
            # Increment count
            if not hasattr(current_app, '_rate_limit'):
                current_app._rate_limit = {}
            current_app._rate_limit[key] = count + 1
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

def validate_request_data(required_fields: list) -> Callable:
    """Validate request data decorator."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            data = request.get_json()
            if not data:
                return jsonify({'message': 'No data provided'}), 400
            
            # Check for required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'message': 'Missing required fields',
                    'fields': missing_fields
                }), 400
            
            # Sanitize input
            data = sanitize_input(data)
            request.json = data
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

def validate_content_type(content_types: list) -> Callable:
    """Validate content type decorator."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            content_type = request.headers.get('Content-Type', '')
            if not any(ct in content_type for ct in content_types):
                return jsonify({
                    'message': f'Invalid content type. Allowed types: {", ".join(content_types)}'
                }), 415
            return f(*args, **kwargs)
        return wrapper
    return decorator

def validate_file_upload(allowed_extensions: list, max_size: int) -> Callable:
    """Validate file upload decorator."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if 'file' not in request.files:
                return jsonify({'message': 'No file provided'}), 400
            
            file = request.files['file']
            
            # Check file extension
            if not file.filename or not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
                return jsonify({
                    'message': f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}'
                }), 400
            
            # Check file size
            file.seek(0, 2)  # Seek to end
            size = file.tell()
            file.seek(0)  # Seek back to start
            if size > max_size:
                return jsonify({
                    'message': f'File too large. Maximum size: {max_size} bytes'
                }), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

def validate_origin(allowed_origins: list) -> Callable:
    """Validate request origin decorator."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            origin = request.headers.get('Origin', '')
            if origin and origin not in allowed_origins:
                return jsonify({'message': 'Invalid origin'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

def validate_user_agent() -> Callable:
    """Validate user agent decorator."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            user_agent = request.headers.get('User-Agent', '')
            if not user_agent:
                return jsonify({'message': 'User-Agent header required'}), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator

def log_request() -> Callable:
    """Log request details decorator."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_app.logger.info(f"Request: {request.method} {request.path}")
            current_app.logger.info(f"IP: {request.remote_addr}")
            current_app.logger.info(f"User-Agent: {request.headers.get('User-Agent')}")
            return f(*args, **kwargs)
        return wrapper
    return decorator

def validate_api_key() -> Callable:
    """Validate API key decorator."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            api_key = request.headers.get('X-API-Key')
            if not api_key or api_key != os.getenv('API_KEY'):
                return jsonify({'message': 'Invalid API key'}), 401
            return f(*args, **kwargs)
        return wrapper
    return decorator

def prevent_brute_force(max_attempts: int, lock_time: int) -> Callable:
    """Prevent brute force attacks decorator."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            ip = request.remote_addr
            key = f"login_attempts:{ip}"
            
            # Get current attempts
            attempts = getattr(current_app, '_login_attempts', {}).get(key, 0)
            
            # Check if account is locked
            if attempts >= max_attempts:
                lock_key = f"account_locked:{ip}"
                locked_until = getattr(current_app, '_account_locks', {}).get(lock_key)
                
                if locked_until and datetime.now() < locked_until:
                    return jsonify({
                        'message': 'Account locked. Please try again later.',
                        'retry_after': (locked_until - datetime.now()).seconds
                    }), 403
                else:
                    # Reset attempts if lock time has passed
                    if hasattr(current_app, '_login_attempts'):
                        current_app._login_attempts[key] = 0
            
            # Increment attempts
            if not hasattr(current_app, '_login_attempts'):
                current_app._login_attempts = {}
            current_app._login_attempts[key] = attempts + 1
            
            # Lock account if max attempts reached
            if attempts + 1 >= max_attempts:
                if not hasattr(current_app, '_account_locks'):
                    current_app._account_locks = {}
                current_app._account_locks[lock_key] = datetime.now() + timedelta(seconds=lock_time)
            
            return f(*args, **kwargs)
        return wrapper
    return decorator 