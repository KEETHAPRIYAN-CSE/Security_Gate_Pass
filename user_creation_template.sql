-- SQL Template for Creating Members in phpMyAdmin
-- Copy and modify this template, then run it in phpMyAdmin SQL tab

-- IMPORTANT: Use the generate_password_hash.py script to get the correct password hash
-- DO NOT put plain text passwords in the pwd field!

-- ========================================================================
-- ROLE-BASED DASHBOARD ACCESS (Dropdown in phpMyAdmin):
-- 'Admin'    -> Admin Dashboard (full system access, user management)
-- 'Faculty'  -> Faculty Dashboard (book visitors, view bookings)
-- 'Security' -> Security Dashboard (visitor entry/exit, check-in/out)
--
-- Note: Role is ENUM type - phpMyAdmin shows dropdown for easy selection!
-- ========================================================================

-- Example 1: Create a Faculty member
INSERT INTO members (username, pwd, role, firstname, lastname, department, suspended) VALUES
('john.faculty', 'PASTE_BCRYPT_HASH_HERE', 'Faculty', 'John', 'Doe', 'CSE', 0);

-- Example 2: Create an Admin member  
INSERT INTO members (username, pwd, role, firstname, lastname, department, suspended) VALUES
('jane.admin', 'PASTE_BCRYPT_HASH_HERE', 'Admin', 'Jane', 'Smith', 'ADMIN', 0);

-- Example 3: Create a Security member
INSERT INTO members (username, pwd, role, firstname, lastname, department, suspended) VALUES
('security2', 'PASTE_BCRYPT_HASH_HERE', 'Security', 'Security', 'Officer 2', 'SECURITY', 0);

-- STEPS TO USE THIS TEMPLATE:
-- 1. Run: python generate_password_hash.py
-- 2. Enter your desired password to get the bcrypt hash
-- 3. Replace 'PASTE_BCRYPT_HASH_HERE' with the generated hash
-- 4. Modify username, firstname, lastname, department as needed
-- 5. Set suspended to 0 (active) or 1 (suspended)
-- 6. Copy the modified INSERT statement to phpMyAdmin > SQL tab
-- 7. Click 'Go' to execute

-- ROLE FIELD: ENUM type with dropdown in phpMyAdmin - click to select!
--   Options: 'Admin', 'Faculty', 'Security'
-- DEPARTMENTS: Any department code (CSE, IT, ECE, etc.) or ADMIN/SECURITY for system members
-- SUSPENDED: 0 = Active, 1 = Suspended (also shows as dropdown in phpMyAdmin)

-- EXAMPLE WITH REAL HASH (password: test123):
-- INSERT INTO members (username, pwd, role, firstname, lastname, department, suspended) VALUES
-- ('test.user', '$2b$12$abcdef1234567890', 'Faculty', 'Test', 'User', 'CSE', 0);