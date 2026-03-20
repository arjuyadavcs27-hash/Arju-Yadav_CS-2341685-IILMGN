from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime, timedelta
import re
import bcrypt
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'blood_bank')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def validate_password(password):
    # Password requirements:
    # - At least 8 characters
    # - At least one uppercase letter
    # - At least one lowercase letter
    # - At least one number
    # - At least one special character
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def role_required(roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            if current_user['role'] not in roles:
                return jsonify({'message': 'Unauthorized access'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        # Check if username is email or mobile
        if '@' in username:
            query = "SELECT * FROM users WHERE email = %s"
        else:
            query = "SELECT * FROM users WHERE mobile = %s"
        
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'message': 'Invalid credentials'}), 401

        # Check if account is locked
        if user.get('is_locked') and user.get('lock_until') > datetime.now():
            return jsonify({'message': 'Account is locked. Please try again later.'}), 403

        # Create access token
        access_token = create_access_token(identity={
            'id': user['id'],
            'role': user['role']
        })

        # Update last login
        cursor.execute("UPDATE users SET last_login = %s WHERE id = %s", 
                      (datetime.now(), user['id']))
        connection.commit()

        return jsonify({
            'token': access_token,
            'role': user['role'],
            'message': 'Login successful'
        }), 200

    except Error as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'mobile', 'password', 'name', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} is required'}), 400

    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        return jsonify({'message': 'Invalid email format'}), 400

    # Validate mobile number (Indian format)
    if not re.match(r"^[6-9]\d{9}$", data['mobile']):
        return jsonify({'message': 'Invalid mobile number format'}), 400

    # Validate password strength
    if not validate_password(data['password']):
        return jsonify({'message': 'Password does not meet requirements'}), 400

    # Hash password
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    connection = get_db_connection()
    if not connection:
        return jsonify({'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor()
        
        # Check if email or mobile already exists
        cursor.execute("SELECT id FROM users WHERE email = %s OR mobile = %s", 
                      (data['email'], data['mobile']))
        if cursor.fetchone():
            return jsonify({'message': 'Email or mobile number already registered'}), 400

        # Insert new user
        query = """
        INSERT INTO users (name, email, mobile, password, role, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['name'],
            data['email'],
            data['mobile'],
            hashed_password.decode('utf-8'),
            data['role'],
            datetime.now()
        ))
        connection.commit()

        return jsonify({'message': 'Registration successful'}), 201

    except Error as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'message': 'Email not found'}), 404

        # Generate reset token (in production, use a more secure method)
        reset_token = os.urandom(32).hex()
        expiry = datetime.now() + timedelta(hours=1)

        cursor.execute("""
            UPDATE users 
            SET reset_token = %s, reset_token_expiry = %s 
            WHERE id = %s
        """, (reset_token, expiry, user['id']))
        connection.commit()

        # In production, send email with reset link
        # send_reset_email(email, reset_token)

        return jsonify({'message': 'Password reset instructions sent to email'}), 200

    except Error as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({'message': 'Token and new password are required'}), 400

    if not validate_password(new_password):
        return jsonify({'message': 'Password does not meet requirements'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'message': 'Database connection error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id FROM users 
            WHERE reset_token = %s AND reset_token_expiry > %s
        """, (token, datetime.now()))
        user = cursor.fetchone()

        if not user:
            return jsonify({'message': 'Invalid or expired reset token'}), 400

        # Hash new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("""
            UPDATE users 
            SET password = %s, reset_token = NULL, reset_token_expiry = NULL 
            WHERE id = %s
        """, (hashed_password.decode('utf-8'), user['id']))
        connection.commit()

        return jsonify({'message': 'Password reset successful'}), 200

    except Error as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close() 