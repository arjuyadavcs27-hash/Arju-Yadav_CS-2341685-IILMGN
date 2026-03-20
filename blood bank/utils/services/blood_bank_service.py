from datetime import datetime, timedelta
from app import db
from utils.models.models import Donor, Hospital, BloodRequest, Donation, BloodInventory
from utils.validators.validators import validate_blood_group, validate_quantity

class BloodBankService:
    @staticmethod
    def process_blood_request(hospital_id, blood_group, quantity, urgency, patient_info):
        if not validate_blood_group(blood_group) or not validate_quantity(quantity):
            return False, "Invalid blood group or quantity"
        
        inventory = BloodInventory.query.filter_by(blood_group=blood_group).first()
        if not inventory or inventory.quantity < quantity:
            return False, "Insufficient blood stock"
        
        request = BloodRequest(
            hospital_id=hospital_id,
            blood_group=blood_group,
            quantity=quantity,
            urgency=urgency,
            patient_name=patient_info.get('name'),
            patient_age=patient_info.get('age'),
            reason=patient_info.get('reason')
        )
        
        db.session.add(request)
        db.session.commit()
        return True, "Blood request processed successfully"

    @staticmethod
    def schedule_donation(donor_id, blood_group, quantity, appointment_date):
        if not validate_blood_group(blood_group) or not validate_quantity(quantity):
            return False, "Invalid blood group or quantity"
        
        donor = Donor.query.get(donor_id)
        if not donor or not donor.is_available:
            return False, "Donor not available"
        
        donation = Donation(
            donor_id=donor_id,
            blood_group=blood_group,
            quantity=quantity,
            donation_date=appointment_date
        )
        
        db.session.add(donation)
        db.session.commit()
        return True, "Donation scheduled successfully"

    @staticmethod
    def update_inventory(blood_group, quantity, operation='add'):
        inventory = BloodInventory.query.filter_by(blood_group=blood_group).first()
        if not inventory:
            inventory = BloodInventory(blood_group=blood_group, quantity=0)
            db.session.add(inventory)
        
        if operation == 'add':
            inventory.quantity += quantity
        else:
            if inventory.quantity < quantity:
                return False, "Insufficient stock"
            inventory.quantity -= quantity
        
        inventory.last_updated = datetime.utcnow()
        inventory.status = self._get_inventory_status(inventory.quantity)
        db.session.commit()
        return True, "Inventory updated successfully"

    @staticmethod
    def get_available_donors(blood_group):
        return Donor.query.filter_by(
            blood_group=blood_group,
            is_available=True
        ).all()

    @staticmethod
    def get_pending_requests():
        return BloodRequest.query.filter_by(status='pending').all()

    @staticmethod
    def get_donation_history(donor_id):
        return Donation.query.filter_by(donor_id=donor_id).order_by(Donation.donation_date.desc()).all()

    @staticmethod
    def _get_inventory_status(quantity):
        if quantity <= 5:
            return 'Critical'
        elif quantity <= 15:
            return 'Low'
        return 'Available' 