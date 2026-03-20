from flask import session, redirect, url_for, flash
from functools import wraps
from datetime import datetime
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page.', 'error')
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def generate_token(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, 'your-secret-key', algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def hash_password(password):
    return generate_password_hash(password)

def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)

def update_last_login(user_id):
    from app import db
    from models import User
    user = User.query.get(user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.session.commit() 