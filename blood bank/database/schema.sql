-- Create database
CREATE DATABASE IF NOT EXISTS blood_bank;
USE blood_bank;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    mobile VARCHAR(15) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'donor', 'staff') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_locked BOOLEAN DEFAULT FALSE,
    lock_until DATETIME,
    reset_token VARCHAR(255),
    reset_token_expiry DATETIME,
    last_login DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME
);

-- Donors table
CREATE TABLE IF NOT EXISTS donors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    blood_type ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    date_of_birth DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    height DECIMAL(5,2) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    emergency_contact_name VARCHAR(100) NOT NULL,
    emergency_contact_phone VARCHAR(15) NOT NULL,
    medical_conditions TEXT,
    allergies TEXT,
    last_donation_date DATE,
    is_eligible BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Donations table
CREATE TABLE IF NOT EXISTS donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    donation_date DATETIME NOT NULL,
    blood_type ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    quantity_ml INT NOT NULL,
    hemoglobin_level DECIMAL(4,2) NOT NULL,
    blood_pressure VARCHAR(20) NOT NULL,
    pulse_rate INT NOT NULL,
    temperature DECIMAL(4,2) NOT NULL,
    status ENUM('pending', 'approved', 'rejected', 'completed') DEFAULT 'pending',
    notes TEXT,
    created_by INT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME,
    FOREIGN KEY (donor_id) REFERENCES donors(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Blood inventory table
CREATE TABLE IF NOT EXISTS blood_inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    blood_type ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    quantity_ml INT NOT NULL,
    expiry_date DATE NOT NULL,
    donation_id INT,
    status ENUM('available', 'reserved', 'expired', 'used') DEFAULT 'available',
    created_at DATETIME NOT NULL,
    updated_at DATETIME,
    FOREIGN KEY (donation_id) REFERENCES donations(id)
);

-- Appointments table
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    status ENUM('scheduled', 'completed', 'cancelled', 'no_show') DEFAULT 'scheduled',
    notes TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME,
    FOREIGN KEY (donor_id) REFERENCES donors(id)
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info', 'warning', 'success', 'error') NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INT,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_mobile ON users(mobile);
CREATE INDEX idx_donors_blood_type ON donors(blood_type);
CREATE INDEX idx_donations_donation_date ON donations(donation_date);
CREATE INDEX idx_blood_inventory_expiry ON blood_inventory(expiry_date);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);

-- Create triggers for updated_at
DELIMITER //

CREATE TRIGGER users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    SET NEW.updated_at = NOW();
END//

CREATE TRIGGER donors_updated_at
BEFORE UPDATE ON donors
FOR EACH ROW
BEGIN
    SET NEW.updated_at = NOW();
END//

CREATE TRIGGER donations_updated_at
BEFORE UPDATE ON donations
FOR EACH ROW
BEGIN
    SET NEW.updated_at = NOW();
END//

CREATE TRIGGER blood_inventory_updated_at
BEFORE UPDATE ON blood_inventory
FOR EACH ROW
BEGIN
    SET NEW.updated_at = NOW();
END//

CREATE TRIGGER appointments_updated_at
BEFORE UPDATE ON appointments
FOR EACH ROW
BEGIN
    SET NEW.updated_at = NOW();
END//

DELIMITER ; 