const jwt = require('jsonwebtoken');
const Donor = require('../models/Donor');
const BloodBank = require('../models/BloodBank');

const auth = async (req, res, next) => {
    try {
        const token = req.header('Authorization')?.replace('Bearer ', '');
        
        if (!token) {
            throw new Error();
        }
        
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        
        // Try to find user in either Donor or BloodBank collection
        let user = await Donor.findOne({ _id: decoded.id });
        if (!user) {
            user = await BloodBank.findOne({ _id: decoded.id });
        }
        
        if (!user) {
            throw new Error();
        }
        
        req.token = token;
        req.user = user;
        next();
    } catch (err) {
        res.status(401).json({ message: 'Please authenticate' });
    }
};

module.exports = auth; 