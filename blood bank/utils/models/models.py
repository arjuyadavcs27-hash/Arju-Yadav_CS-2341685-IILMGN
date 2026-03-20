from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, donor, hospital
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    last_donation = db.Column(db.DateTime)
    is_available = db.Column(db.Boolean, default=True)
    health_status = db.Column(db.String(50))
    donations = db.relationship('Donation', backref='donor', lazy=True)

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    license_number = db.Column(db.String(50), nullable=False)
    blood_requests = db.relationship('BloodRequest', backref='hospital', lazy=True)

class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    urgency = db.Column(db.String(20), nullable=False)
    patient_name = db.Column(db.String(100))
    patient_age = db.Column(db.Integer)
    reason = db.Column(db.Text)

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    donation_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    test_results = db.Column(db.Text)
    notes = db.Column(db.Text)

class BloodInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blood_group = db.Column(db.String(5), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Available')  # Available, Low, Critical
    location = db.Column(db.String(50))
    batch_number = db.Column(db.String(50)) 