from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import CSRFProtect
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_admin import Admin, AdminIndexView, expose
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps
import json
import pytz
from dotenv import load_dotenv
import hashlib
from flask_cors import CORS
from api.auth import auth_bp
from utils.models.models import User, Donor, BloodBank, State, City, Donation, BloodInventory
from utils.auth.auth_utils import hash_password
from utils.services.blood_bank_service import BloodBankService

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///bloodbank.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
socketio = SocketIO(app)
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    pincode = db.Column(db.String(10))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    roles = db.relationship('Role', secondary='user_roles')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Donor(User):
    __tablename__ = 'donor'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    blood_group = db.Column(db.String(5))
    last_donation_date = db.Column(db.DateTime)
    health_status = db.Column(db.String(50))
    is_available = db.Column(db.Boolean, default=True)
    donations = db.relationship('Donation', backref='donor', lazy=True)

class Staff(User):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    designation = db.Column(db.String(50))
    department = db.Column(db.String(50))
    joining_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

class BloodInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blood_group = db.Column(db.String(5), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Available')

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    donation_date = db.Column(db.DateTime, default=datetime.utcnow)
    blood_group = db.Column(db.String(5))
    quantity = db.Column(db.Integer)
    status = db.Column(db.String(20), default='Pending')
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    quantity = db.Column(db.Integer)
    hospital_name = db.Column(db.String(100))
    patient_name = db.Column(db.String(100))
    urgency_level = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

# User-Role Association Table
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

# Initialize Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

def verify_admin_credentials(username, password):
    # Check if admin credentials file exists
    if not os.path.exists("data/admin_credentials.txt"):
        return False
    
    # Read admin credentials
    with open("data/admin_credentials.txt", "r") as f:
        lines = f.readlines()
        stored_username = lines[0].split(": ")[1].strip()
        stored_password_hash = lines[1].split(": ")[1].strip()
    
    # Hash the provided password
    provided_password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Verify credentials
    return username == stored_username and provided_password_hash == stored_password_hash

@app.route('/')
def index():
    return render_template('webpage.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle registration logic
        pass
    return render_template('donor_registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic
        pass
    return render_template('admin_login.html')

@app.route('/admin')
def admin_login_page():
    return render_template('admin.html')

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'GET':
        return render_template('10_admin_register.html')
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Validate input data
        if not all([data.get('name'), data.get('email'), data.get('password'), data.get('adminCode')]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        try:
            # Validate email format
            if not validate_email(data['email']):
                return jsonify({'success': False, 'message': 'Invalid email format'}), 400
            
            # Validate password strength
            if not validate_password(data['password']):
                return jsonify({'success': False, 'message': 'Password does not meet requirements'}), 400
            
            # Validate admin code
            stored_admin_code = os.getenv('ADMIN_REGISTRATION_CODE')
            if not validate_admin_code(data['adminCode'], stored_admin_code):
                return jsonify({'success': False, 'message': 'Invalid admin registration code'}), 400
            
            # Check if email already exists
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'success': False, 'message': 'Email already registered'}), 400
            
            # Create new admin user
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                admin_role = Role(name='admin', description='Administrator')
                db.session.add(admin_role)
            
            new_admin = User(
                email=data['email'],
                first_name=data['name'].split()[0],
                last_name=' '.join(data['name'].split()[1:]) if len(data['name'].split()) > 1 else '',
                role_id=admin_role.id,
                created_at=datetime.utcnow()
            )
            new_admin.set_password(data['password'])
            
            db.session.add(new_admin)
            db.session.commit()
            
            # Create admin session
            session_data = create_admin_session(new_admin.id)
            
            return jsonify({
                'success': True,
                'message': 'Admin registration successful',
                'data': format_admin_response({
                    'id': new_admin.id,
                    'name': data['name'],
                    'email': new_admin.email,
                    'created_at': new_admin.created_at.isoformat(),
                    'last_login': None
                })
            }), 201
            
        except Exception as e:
            db.session.rollback()
            error_response = handle_admin_registration_error(e)
            return jsonify(error_response), 500

@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('email')
    password = request.form.get('password')
    
    if verify_admin_credentials(username, password):
        session['admin_logged_in'] = True
        session['admin_username'] = username
        flash('Login successful!', 'success')
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid credentials. Please try again.', 'error')
        return redirect(url_for('admin_login_page'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login_page'))

@app.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    # Get recent donor registrations
    recent_donors = Donor.query.order_by(Donor.id.desc()).limit(5).all()
    
    # Get blood inventory status
    inventory = BloodInventory.query.all()
    
    # Get pending blood requests
    pending_requests = BloodRequest.query.filter_by(status='pending').all()
    
    return render_template('admin-dashboard.html',
                         recent_donors=recent_donors,
                         inventory=inventory,
                         pending_requests=pending_requests)

@app.route('/donor-registration', methods=['GET', 'POST'])
def donor_registration():
    if request.method == 'GET':
        return render_template('02_donor-registration.html')
    
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            name = request.form.get('name')
            blood_group = request.form.get('blood_group')
            phone = request.form.get('phone')
            address = request.form.get('address')
            
            # Validate required fields
            if not all([username, email, password, name, blood_group, phone, address]):
                flash('All fields are required', 'danger')
                return redirect(url_for('donor_registration'))
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('donor_registration'))
            
            # Check if username already exists
            if User.query.filter_by(username=username).first():
                flash('Username already taken', 'danger')
                return redirect(url_for('donor_registration'))
            
            # Create new user
            new_user = User(
                username=username,
                email=email,
                name=name,
                phone=phone,
                address=address
            )
            new_user.set_password(password)
            
            # Create donor profile
            new_donor = Donor(
                user=new_user,
                blood_group=blood_group,
                is_available=True
            )
            
            # Add to database
            db.session.add(new_user)
            db.session.add(new_donor)
            db.session.commit()
            
            # Log in the user
            login_user(new_user)
            
            flash('Registration successful!', 'success')
            return redirect(url_for('donor_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration', 'danger')
            return redirect(url_for('donor_registration'))

@app.route('/donor-dashboard')
@login_required
def donor_dashboard():
    donor = Donor.query.filter_by(id=current_user.id).first()
    donations = Donation.query.filter_by(donor_id=donor.id).order_by(Donation.donation_date.desc()).all()
    return render_template('06_donor-dashboard.html', donor=donor, donations=donations)

@app.route('/staff/dashboard')
@login_required
def staff_dashboard():
    if not current_user.has_role('staff'):
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    return render_template('staff_reports.html')

# API Routes
@app.route('/api/blood-inventory', methods=['GET'])
@jwt_required()
def get_blood_inventory():
    inventory = BloodInventory.query.all()
    return jsonify([{
        'blood_group': item.blood_group,
        'quantity': item.quantity,
        'status': item.status
    } for item in inventory])

@app.route('/api/blood-request', methods=['POST'])
@jwt_required()
def create_blood_request():
    data = request.get_json()
    # Handle blood request creation
    return jsonify({'message': 'Request created successfully'})

@app.route('/api/cities/<state_id>')
def get_cities(state_id):
    cities = City.query.filter_by(state_id=state_id).all()
    return jsonify([{'id': city.id, 'name': city.name} for city in cities])

@app.route('/api/inventory/<inventory_id>/status', methods=['POST'])
@login_required(role='blood_bank')
def update_inventory_status(inventory_id):
    try:
        inventory = BloodInventory.query.get_or_404(inventory_id)
        if inventory.blood_bank_id != session['blood_bank_id']:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        inventory.status = 'Unavailable' if inventory.status == 'Available' else 'Available'
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    emit('connected', {'data': 'Connected'})

@socketio.on('blood_request')
def handle_blood_request(data):
    # Handle real-time blood request notifications
    emit('new_request', data, broadcast=True)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'message': 'Bad request'}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'message': 'Unauthorized'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'message': 'Forbidden'}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'message': 'Internal server error'}), 500

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/donor-login', methods=['GET', 'POST'])
def donor_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and verify_password(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            update_last_login(user.id)
            flash('Login successful!', 'success')
            return redirect(url_for('donor_dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('donor_login'))
    
    return render_template('donor_login.html')

@app.route('/search')
def search():
    states = State.query.all()
    return render_template('search.html', states=states)

@app.route('/api/blood-banks')
def get_blood_banks():
    city_id = request.args.get('city_id')
    blood_group = request.args.get('blood_group')
    
    query = BloodBank.query.filter_by(is_verified=True)
    
    if city_id:
        query = query.filter_by(city_id=city_id)
    
    blood_banks = query.all()
    
    results = []
    for bank in blood_banks:
        inventory = BloodInventory.query.filter_by(blood_bank_id=bank.id)
        if blood_group:
            inventory = inventory.filter_by(blood_group=blood_group, status='Available')
        
        available_blood_groups = set()
        for item in inventory:
            if item.status == 'Available':
                available_blood_groups.add(item.blood_group)
        
        if not blood_group or available_blood_groups:
            results.append({
                'id': bank.id,
                'name': bank.name,
                'address': bank.address,
                'city': bank.city.name,
                'contact_number': bank.contact_number,
                'email': bank.email,
                'available_blood_groups': list(available_blood_groups)
            })
    
    return jsonify(results)

@app.route('/api/donors')
def get_donors():
    city_id = request.args.get('city_id')
    blood_group = request.args.get('blood_group')
    
    query = Donor.query.filter_by(is_available=True)
    
    if city_id:
        query = query.filter_by(city_id=city_id)
    if blood_group:
        query = query.filter_by(blood_group=blood_group)
    
    donors = query.all()
    
    results = []
    for donor in donors:
        last_donation = Donation.query.filter_by(donor_id=donor.id)\
            .order_by(Donation.donation_date.desc())\
            .first()
        
        results.append({
            'id': donor.id,
            'name': donor.name,
            'blood_group': donor.blood_group,
            'city': donor.city.name,
            'phone': donor.phone,
            'last_donation_date': last_donation.donation_date.strftime('%Y-%m-%d') if last_donation else None,
            'is_available': donor.is_available
        })
    
    return jsonify(results)

@app.route('/donor/register', methods=['POST'])
def donor_register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'first_name', 'last_name', 'email', 'phone', 'password',
            'street_address', 'city', 'state', 'zip_code', 'blood_type',
            'date_of_birth', 'gender'
        ]
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400

        # Validate email format
        if not validate_email(data['email']):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400

        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 400

        # Create new user
        new_user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            address=data['street_address'],
            city=data['city'],
            state=data['state'],
            pincode=data['zip_code']
        )
        new_user.set_password(data['password'])

        # Create donor record
        new_donor = Donor(
            id=new_user.id,
            blood_group=data['blood_type'],
            health_status='Pending',
            is_available=True
        )

        db.session.add(new_user)
        db.session.add(new_donor)
        db.session.commit()

        # Create session
        login_user(new_user)
        session['user_id'] = new_user.id
        session['role'] = 'donor'

        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'redirect': '06_donor-dashboard.html'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'An error occurred during registration'
        }), 500

@app.route('/check-session')
def check_session():
    if 'user_id' in session and 'role' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'logged_in': True,
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'role': session['role']
                }
            })
    return jsonify({'logged_in': False})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/donor/profile')
@login_required
def get_donor_profile():
    try:
        donor = Donor.query.get(current_user.id)
        if not donor:
            return jsonify({'success': False, 'message': 'Donor not found'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': donor.id,
                'first_name': donor.first_name,
                'last_name': donor.last_name,
                'email': donor.email,
                'phone': donor.phone,
                'address': donor.address,
                'city': donor.city,
                'state': donor.state,
                'pincode': donor.pincode,
                'blood_group': donor.blood_group,
                'health_status': donor.health_status,
                'last_donation_date': donor.last_donation_date.isoformat() if donor.last_donation_date else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/donor/history')
@login_required
def get_donation_history():
    try:
        donations = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.donation_date.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': donation.id,
                'date': donation.donation_date.isoformat(),
                'blood_group': donation.blood_group,
                'quantity': donation.quantity,
                'status': donation.status
            } for donation in donations]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/donor/appointments')
@login_required
def get_upcoming_appointments():
    try:
        # Get appointments from the last 30 days and next 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        thirty_days_ahead = datetime.utcnow() + timedelta(days=30)
        
        appointments = Donation.query.filter(
            Donation.donor_id == current_user.id,
            Donation.donation_date.between(thirty_days_ago, thirty_days_ahead)
        ).order_by(Donation.donation_date.asc()).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': appointment.id,
                'date': appointment.donation_date.isoformat(),
                'blood_group': appointment.blood_group,
                'status': appointment.status
            } for appointment in appointments]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Helper functions
def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    # Password must be at least 8 characters long and contain at least one number and one special character
    import re
    if len(password) < 8:
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=os.getenv('DEBUG', False)) 