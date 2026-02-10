-- SRIT Visitor Management System Database Schema
-- Execute this in phpMyAdmin or MySQL command line

CREATE DATABASE IF NOT EXISTS visitor_management;
USE visitor_management;

-- Users Table (Faculty, Admin, Security) with Authentication
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    role ENUM('Admin', 'Faculty', 'Security') NOT NULL,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    first_login BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Visitors Table (Entry/Exit Log)
CREATE TABLE IF NOT EXISTS visitors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    in_time TIME NOT NULL,
    mobile VARCHAR(15) NOT NULL,
    name VARCHAR(255) NOT NULL,
    designation VARCHAR(100),
    company VARCHAR(255),
    laptop VARCHAR(50) DEFAULT '-',
    to_meet VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    photo_data LONGBLOB,
    photo_mime_type VARCHAR(50) DEFAULT 'image/jpeg',
    out_time TIME NULL,
    entered_by VARCHAR(255),
    vehicle_number VARCHAR(50) DEFAULT '-',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_mobile (mobile),
    INDEX idx_date (date),
    INDEX idx_out_time (out_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Bookings Table (Pre-booking)
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_time DATETIME NOT NULL,
    booked_by_email VARCHAR(255) NOT NULL,
    host_name VARCHAR(255) NOT NULL,
    host_department VARCHAR(100) NOT NULL,
    visitor_mobile VARCHAR(15) NOT NULL,
    visitor_name VARCHAR(255) NOT NULL,
    purpose TEXT NOT NULL,
    status ENUM('Pending', 'Arrived', 'Cancelled') DEFAULT 'Pending',
    company VARCHAR(255) DEFAULT '-',
    vehicle_number VARCHAR(50) DEFAULT '-',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_mobile (visitor_mobile),
    INDEX idx_status (status),
    INDEX idx_booking_time (booking_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert Admin and Security users (REQUIRED - Must be in database)
-- Default password for all users is 'password123' (hashed with bcrypt)
-- Faculty users should be manually created with default password, they can change it on first login
-- Using INSERT IGNORE to prevent duplicate entry errors if run multiple times
-- Note: Generate password hash using: python -c "import bcrypt; print(bcrypt.hashpw('password123'.encode(), bcrypt.gensalt()).decode())"
-- Insert default users (password: password123)
INSERT IGNORE INTO users (username, password, email, role, name, department, first_login) VALUES
('admin', '$2b$12$9/SUE9oND0k88cl8b/nCBuoP0l8tddCLM9vPJHV80p/oQ6oyolFq6', 'admin@sritcbe.ac.in', 'Admin', 'System Admin', 'ADMIN', FALSE),
('security', '$2b$12$9/SUE9oND0k88cl8b/nCBuoP0l8tddCLM9vPJHV80p/oQ6oyolFq6', 'security@sritcbe.ac.in', 'Security', 'Security Desk', 'SECURITY', FALSE);

-- Create view for active visitors (those who haven't exited)
CREATE OR REPLACE VIEW active_visitors AS
SELECT * FROM visitors WHERE out_time IS NULL ORDER BY created_at DESC;

-- Create view for pending bookings
CREATE OR REPLACE VIEW pending_bookings AS
SELECT * FROM bookings WHERE status = 'Pending' ORDER BY booking_time DESC;
