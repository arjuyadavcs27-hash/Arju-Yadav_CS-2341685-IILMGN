const express = require('express');
const router = express.Router();
const BloodBank = require('../models/BloodBank');
const auth = require('../middleware/auth');

// Get all blood banks
router.get('/', async (req, res) => {
    try {
        const { city, bloodGroup } = req.query;
        let query = {};
        
        if (city) query.city = city;
        if (bloodGroup) query.availableBloodGroups = bloodGroup;
        
        const bloodBanks = await BloodBank.find(query).select('-password');
        res.json(bloodBanks);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

// Get single blood bank
router.get('/:id', async (req, res) => {
    try {
        const bloodBank = await BloodBank.findById(req.params.id).select('-password');
        if (!bloodBank) {
            return res.status(404).json({ message: 'Blood bank not found' });
        }
        res.json(bloodBank);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

// Register new blood bank
router.post('/register', async (req, res) => {
    try {
        const bloodBank = new BloodBank(req.body);
        await bloodBank.save();
        const token = await bloodBank.generateAuthToken();
        res.status(201).json({ bloodBank, token });
    } catch (err) {
        res.status(400).json({ message: err.message });
    }
});

// Update blood bank
router.patch('/:id', auth, async (req, res) => {
    try {
        const bloodBank = await BloodBank.findById(req.params.id);
        if (!bloodBank) {
            return res.status(404).json({ message: 'Blood bank not found' });
        }
        
        Object.keys(req.body).forEach(key => {
            bloodBank[key] = req.body[key];
        });
        
        await bloodBank.save();
        res.json(bloodBank);
    } catch (err) {
        res.status(400).json({ message: err.message });
    }
});

// Update inventory
router.patch('/:id/inventory', auth, async (req, res) => {
    try {
        const { bloodGroup, quantity } = req.body;
        const bloodBank = await BloodBank.findById(req.params.id);
        
        if (!bloodBank) {
            return res.status(404).json({ message: 'Blood bank not found' });
        }
        
        const inventoryItem = bloodBank.inventory.find(item => item.bloodGroup === bloodGroup);
        if (inventoryItem) {
            inventoryItem.quantity = quantity;
        } else {
            bloodBank.inventory.push({ bloodGroup, quantity });
        }
        
        await bloodBank.save();
        res.json(bloodBank);
    } catch (err) {
        res.status(400).json({ message: err.message });
    }
});

// Delete blood bank
router.delete('/:id', auth, async (req, res) => {
    try {
        const bloodBank = await BloodBank.findByIdAndDelete(req.params.id);
        if (!bloodBank) {
            return res.status(404).json({ message: 'Blood bank not found' });
        }
        res.json({ message: 'Blood bank deleted' });
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

module.exports = router; 