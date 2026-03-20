class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(2), nullable=False)  # State code (e.g., MH for Maharashtra)
    cities = db.relationship('City', backref='state', lazy=True)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)
    pincode = db.Column(db.String(6))
    blood_banks = db.relationship('BloodBank', backref='city', lazy=True)

class BloodBank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120))
    license_number = db.Column(db.String(50), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    inventory = db.relationship('BloodInventory', backref='blood_bank', lazy=True)
    staff = db.relationship('Staff', backref='blood_bank', lazy=True)

# Update existing Donor model
class Donor(User):
    __tablename__ = 'donor'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    blood_group = db.Column(db.String(5))
    last_donation_date = db.Column(db.DateTime)
    health_status = db.Column(db.String(50))
    is_available = db.Column(db.Boolean, default=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    donations = db.relationship('Donation', backref='donor', lazy=True)
    preferred_blood_bank_id = db.Column(db.Integer, db.ForeignKey('blood_bank.id'))

# Update existing Donation model
class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    blood_bank_id = db.Column(db.Integer, db.ForeignKey('blood_bank.id'), nullable=False)
    donation_date = db.Column(db.DateTime, default=datetime.utcnow)
    blood_group = db.Column(db.String(5))
    quantity = db.Column(db.Integer)
    status = db.Column(db.String(20), default='Pending')
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)

# Update existing BloodInventory model
class BloodInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blood_bank_id = db.Column(db.Integer, db.ForeignKey('blood_bank.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Available')
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False) 