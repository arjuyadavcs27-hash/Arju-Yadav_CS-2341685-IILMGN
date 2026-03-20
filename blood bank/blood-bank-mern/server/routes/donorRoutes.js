const express = require('express');
const router = express.Router();
const Donor = require('../models/Donor');
const auth = require('../middleware/auth');

// Get all donors
router.get('/', async (req, res) => {
    try {
        const { city, bloodGroup } = req.query;
        let query = {};
        
        if (city) query.city = city;
        if (bloodGroup) query.bloodGroup = bloodGroup;
        
        const donors = await Donor.find(query).select('-password');
        res.json(donors);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

// Get single donor
router.get('/:id', async (req, res) => {
    try {
        const donor = await Donor.findById(req.params.id).select('-password');
        if (!donor) {
            return res.status(404).json({ message: 'Donor not found' });
        }
        res.json(donor);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

// Register new donor
router.post('/register', async (req, res) => {
    try {
        const donor = new Donor(req.body);
        await donor.save();
        const token = await donor.generateAuthToken();
        res.status(201).json({ donor, token });
    } catch (err) {
        res.status(400).json({ message: err.message });
    }
});

// Update donor
router.patch('/:id', auth, async (req, res) => {
    try {
        const donor = await Donor.findById(req.params.id);
        if (!donor) {
            return res.status(404).json({ message: 'Donor not found' });
        }
        
        Object.keys(req.body).forEach(key => {
            donor[key] = req.body[key];
        });
        
        await donor.save();
        res.json(donor);
    } catch (err) {
        res.status(400).json({ message: err.message });
    }
});

// Delete donor
router.delete('/:id', auth, async (req, res) => {
    try {
        const donor = await Donor.findByIdAndDelete(req.params.id);
        if (!donor) {
            return res.status(404).json({ message: 'Donor not found' });
        }
        res.json({ message: 'Donor deleted' });
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

module.exports = router; 