const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const validator = require('validator');

const donorSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, 'Name is required'],
        trim: true
    },
    email: {
        type: String,
        required: [true, 'Email is required'],
        unique: true,
        lowercase: true,
        validate: [validator.isEmail, 'Please provide a valid email']
    },
    password: {
        type: String,
        required: [true, 'Password is required'],
        minlength: 8,
        select: false
    },
    phone: {
        type: String,
        required: [true, 'Phone number is required']
    },
    bloodGroup: {
        type: String,
        required: [true, 'Blood group is required'],
        enum: ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    },
    city: {
        type: String,
        required: [true, 'City is required']
    },
    state: {
        type: String,
        required: [true, 'State is required']
    },
    isAvailable: {
        type: Boolean,
        default: true
    },
    lastDonationDate: {
        type: Date
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
});

// Hash password before saving
donorSchema.pre('save', async function(next) {
    if (!this.isModified('password')) return next();
    this.password = await bcrypt.hash(this.password, 12);
    next();
});

// Compare password method
donorSchema.methods.comparePassword = async function(candidatePassword) {
    return await bcrypt.compare(candidatePassword, this.password);
};

const Donor = mongoose.model('Donor', donorSchema);

module.exports = Donor; 