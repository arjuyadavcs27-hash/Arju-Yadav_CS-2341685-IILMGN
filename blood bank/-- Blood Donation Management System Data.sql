-- Blood Donation Management System Database Schema

-- Users Table
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(255),
    role ENUM('admin', 'donor', 'staff', 'hospital'),
    email VARCHAR(100),
    phone VARCHAR(15),
    created_at TIMESTAMP
);

-- Donors Table
CREATE TABLE donors (
    id INT PRIMARY KEY,
    user_id INT,
    blood_type VARCHAR(5),
    last_donation_date DATE,
    health_status VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Blood Banks Table
CREATE TABLE blood_banks (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    license_number VARCHAR(50),
    contact_number VARCHAR(15),
    email VARCHAR(100)
);

-- Inventory Table
CREATE TABLE inventory (
    id INT PRIMARY KEY,
    blood_bank_id INT,
    blood_type VARCHAR(5),
    quantity INT,
    expiry_date DATE,
    status VARCHAR(20),
    last_updated TIMESTAMP,
    FOREIGN KEY (blood_bank_id) REFERENCES blood_banks(id)
);

-- Donations Table
CREATE TABLE donations (
    id INT PRIMARY KEY,
    donor_id INT,
    blood_bank_id INT,
    blood_type VARCHAR(5),
    quantity INT,
    donation_date TIMESTAMP,
    status VARCHAR(20),
    FOREIGN KEY (donor_id) REFERENCES donors(id),
    FOREIGN KEY (blood_bank_id) REFERENCES blood_banks(id)
);

-- Requests Table
CREATE TABLE requests (
    id INT PRIMARY KEY,
    hospital_id INT,
    blood_type VARCHAR(5),
    quantity INT,
    status VARCHAR(20),
    request_date TIMESTAMP,
    urgency_level VARCHAR(20),
    FOREIGN KEY (hospital_id) REFERENCES users(id)
);

-- Staff Table
CREATE TABLE staff (
    id INT PRIMARY KEY,
    user_id INT,
    blood_bank_id INT,
    role VARCHAR(50),
    department VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (blood_bank_id) REFERENCES blood_banks(id)
);