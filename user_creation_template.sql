-- SQL Template for Creating Users in phpMyAdmin
-- Copy and modify this template, then run it in phpMyAdmin SQL tab

-- IMPORTANT: Use the generate_password_hash.py script to get the correct password hash
-- DO NOT put plain text passwords in the password field!

-- Example 1: Create a Faculty user
INSERT INTO users (username, password, email, role, name, department, first_login) VALUES
('john.faculty', 'PASTE_BCRYPT_HASH_HERE', 'john.cse@sritcbe.ac.in', 'Faculty', 'John Doe', 'CSE', TRUE);

-- Example 2: Create an Admin user  
INSERT INTO users (username, password, email, role, name, department, first_login) VALUES
('jane.admin', 'PASTE_BCRYPT_HASH_HERE', 'jane.admin@sritcbe.ac.in', 'Admin', 'Jane Smith', 'ADMIN', TRUE);

-- Example 3: Create a Security user
INSERT INTO users (username, password, email, role, name, department, first_login) VALUES
('security2', 'PASTE_BCRYPT_HASH_HERE', 'security2@sritcbe.ac.in', 'Security', 'Security Officer 2', 'SECURITY', TRUE);

-- STEPS TO USE THIS TEMPLATE:
-- 1. Run: python generate_password_hash.py
-- 2. Enter your desired password to get the bcrypt hash
-- 3. Replace 'PASTE_BCRYPT_HASH_HERE' with the generated hash
-- 4. Modify username, email, name, department as needed
-- 5. Copy the modified INSERT statement to phpMyAdmin > SQL tab
-- 6. Click 'Go' to execute

-- VALID ROLES: 'Admin', 'Faculty', 'Security'
-- VALID DEPARTMENTS: Any department code (CSE, IT, ECE, etc.) or ADMIN/SECURITY for system users

-- EXAMPLE WITH REAL HASH (password: test123):
-- INSERT INTO users (username, password, email, role, name, department, first_login) VALUES
-- ('test.user', '$2b$12$abcdef1234567890', 'test@sritcbe.ac.in', 'Faculty', 'Test User', 'CSE', TRUE);