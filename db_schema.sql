-- SRIT Visitor Management System Database Schema
-- Execute this in phpMyAdmin or MySQL command line

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE DATABASE IF NOT EXISTS visitor_management;
USE visitor_management;

-- Members Table (Faculty, Admin, Security) with Authentication
-- Role provides dropdown selection in phpMyAdmin for easy selection
-- Role determines dashboard access:
--   'Admin'    -> Admin Dashboard (full system access, user management, all visitors)
--   'Faculty'  -> Faculty Dashboard (book visitors, view own bookings)
--   'Security' -> Security Dashboard (visitor entry/exit, check-in/out)
CREATE TABLE IF NOT EXISTS members (
    id INT(4) NOT NULL AUTO_INCREMENT,
    username VARCHAR(65) NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    role ENUM('Admin', 'Faculty', 'Security') NOT NULL COMMENT 'Dropdown: Admin, Faculty, or Security',
    suspended INT(11) NOT NULL DEFAULT 0 COMMENT '0=Active, 1=Suspended',
    pwd VARCHAR(200) NOT NULL COMMENT 'md5 hashed password',
    department VARCHAR(100),
    PRIMARY KEY (id),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Visitors Table (Entry/Exit Log)
CREATE TABLE IF NOT EXISTS visitors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    in_time TIMESTAMP NOT NULL,
    mobile VARCHAR(15) NOT NULL,
    name VARCHAR(255) NOT NULL,
    designation VARCHAR(100),
    company VARCHAR(255),
    laptop VARCHAR(50) DEFAULT '-',
    to_meet VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    photo_data LONGBLOB,
    photo_mime_type VARCHAR(50) DEFAULT 'image/jpeg',
    out_time TIMESTAMP NULL,
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
    booking_time TIMESTAMP NOT NULL,
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

-- Insert Admin and Security members (REQUIRED - Must be in database)
-- Default password for all members is 'password123' (hashed with md5)
-- Faculty members should be manually created with default password
-- Using INSERT IGNORE to prevent duplicate entry errors if run multiple times
-- Note: Generate password hash using md5
-- Insert default members (password: password123)
INSERT IGNORE INTO members (username, pwd, role, firstname, lastname, department, suspended) VALUES
('admin', '482c811da5d5b4bc6d497ffa98491e38', 'Admin', 'System', 'Admin', 'ADMIN', 0),
('security', '482c811da5d5b4bc6d497ffa98491e38', 'Security', 'Security', 'Desk', 'SECURITY', 0);

-- Create view for active visitors (those who haven't exited)
CREATE OR REPLACE VIEW active_visitors AS
SELECT * FROM visitors WHERE out_time IS NULL ORDER BY created_at DESC;

-- Create view for pending bookings
CREATE OR REPLACE VIEW pending_bookings AS
SELECT * FROM bookings WHERE status = 'Pending' ORDER BY booking_time DESC;
