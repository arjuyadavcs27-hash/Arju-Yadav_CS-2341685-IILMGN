from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, BloodBank, City, State, BloodInventory, Donation
from datetime import datetime
from functools import wraps

blood_bank_bp = Blueprint('blood_bank', __name__)

def blood_bank_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'blood_bank':
            flash('Please login as a blood bank to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@blood_bank_bp.route('/blood-bank/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            address = request.form.get('address')
            city_id = request.form.get('city_id')
            contact_number = request.form.get('contact_number')
            email = request.form.get('email')
            license_number = request.form.get('license_number')
            
            new_blood_bank = BloodBank(
                name=name,
                address=address,
                city_id=city_id,
                contact_number=contact_number,
                email=email,
                license_number=license_number
            )
            
            db.session.add(new_blood_bank)
            db.session.commit()
            
            flash('Blood bank registration successful! Please wait for verification.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('blood_bank.register'))
    
    states = State.query.all()
    return render_template('blood_bank/register.html', states=states)

@blood_bank_bp.route('/blood-bank/dashboard')
@blood_bank_required
def dashboard():
    blood_bank = BloodBank.query.filter_by(id=session['blood_bank_id']).first()
    if not blood_bank:
        flash('Blood bank profile not found', 'error')
        return redirect(url_for('login'))
    
    inventory = BloodInventory.query.filter_by(blood_bank_id=blood_bank.id).all()
    recent_donations = Donation.query.filter_by(blood_bank_id=blood_bank.id)\
        .order_by(Donation.donation_date.desc())\
        .limit(5)\
        .all()
    
    return render_template('blood_bank/dashboard.html',
                         blood_bank=blood_bank,
                         inventory=inventory,
                         recent_donations=recent_donations)

@blood_bank_bp.route('/blood-bank/inventory', methods=['GET', 'POST'])
@blood_bank_required
def manage_inventory():
    blood_bank = BloodBank.query.filter_by(id=session['blood_bank_id']).first()
    
    if request.method == 'POST':
        try:
            blood_group = request.form.get('blood_group')
            quantity = int(request.form.get('quantity'))
            expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d')
            
            inventory = BloodInventory(
                blood_bank_id=blood_bank.id,
                blood_group=blood_group,
                quantity=quantity,
                expiry_date=expiry_date,
                city_id=blood_bank.city_id
            )
            
            db.session.add(inventory)
            db.session.commit()
            
            flash('Inventory updated successfully', 'success')
            return redirect(url_for('blood_bank.manage_inventory'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating inventory', 'error')
            return redirect(url_for('blood_bank.manage_inventory'))
    
    inventory = BloodInventory.query.filter_by(blood_bank_id=blood_bank.id).all()
    return render_template('blood_bank/inventory.html', inventory=inventory)

@blood_bank_bp.route('/api/cities/<state_id>')
def get_cities(state_id):
    cities = City.query.filter_by(state_id=state_id).all()
    return jsonify([{'id': city.id, 'name': city.name} for city in cities]) 