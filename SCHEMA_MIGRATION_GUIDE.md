# 🔄 Schema Migration Guide: users → members

## Overview
The database schema has been updated to use a new `members` table structure as per your requirements. This guide explains all changes and how to migrate your existing data.

## 📋 Schema Changes

### Table Renamed
- **Old**: `users`
- **New**: `members`

### Column Changes

| Old Column | New Column | Type Change | Notes |
|------------|------------|-------------|-------|
| `password` | `pwd` | VARCHAR(255) → VARCHAR(200) | Password hash field renamed |
| `name` | `firstname` + `lastname` | VARCHAR(255) → VARCHAR(100) each | Single name field split into two |
| `email` | *removed* | - | Email field no longer used |
| `first_login` | *removed* | - | No longer forcing password change on first login |
| `created_at` | *removed* | - | Timestamp no longer tracked |
| - | `suspended` | INT(11) | **NEW**: 0=Active, 1=Suspended |
| `role` | `role` | ENUM → ENUM('Admin','Faculty','Security') | **IMPROVED**: Now dropdown in phpMyAdmin! |
| `id` | `id` | AUTO_INCREMENT → INT(4) | Size constraint added |
| `username` | `username` | VARCHAR(100) → VARCHAR(65) | Size reduced |

### Fields Retained
- `username` - Login identifier
- `role` - User role (Admin, Faculty, Security)
- `department` - User's department (now optional)

## 🔧 Files Updated

### 1. Database Schema
- **File**: `db_schema.sql`
- **Changes**:
  - Replaced `users` table with `members` table
  - Updated default admin and security records
  - Changed column names and types

### 2. User Creation Script
- **File**: `create_user_directly.py`
- **Changes**:
  - Updated to work with `members` table
  - Now prompts for firstname and lastname separately
  - Uses `pwd` column instead of `password`
  - Removed email input
  - Sets `suspended=0` by default

### 3. Main Application
- **File**: `app.py`
- **Changes**:
  - All database queries updated to use `members` table
  - Login now checks `suspended` status
  - Password field changed from `password` to `pwd`
  - Removed `first_login` logic (no forced password change)
  - Session stores full name as `firstname + lastname`
  - User management APIs updated

### 4. SQL Template
- **File**: `user_creation_template.sql`
- **Changes**:
  - Updated INSERT statements for `members` table
  - Changed column references
  - Added `suspended` field

### 5. Password Hash Generator
- **File**: `generate_password_hash.py`
- **Changes**:
  - Documentation updated to reference `members` table
  - Instructions now mention `pwd` field instead of `password`
  - Added `suspended` field in instructions

### 6. Documentation
- **File**: `docs/ARCHITECTURE.md`
- **Changes**:
  - Database diagram updated with new schema

## 🚀 Migration Steps

### For Fresh Installation:
1. Drop existing database (if any):
   ```sql
   DROP DATABASE IF EXISTS visitor_management;
   ```

2. Run the new schema:
   ```sql
   -- Copy contents of db_schema.sql and run in phpMyAdmin
   ```

3. Default members will be created:
   - Username: `admin`, Password: `password123`
   - Username: `security`, Password: `password123`

### For Existing Database (With Data):

**⚠️ IMPORTANT: Backup your database first!**

```sql
-- Step 1: Backup existing users table
CREATE TABLE users_backup AS SELECT * FROM users;

-- Step 2: Create new members table
CREATE TABLE IF NOT EXISTS members (
    id INT(4) NOT NULL AUTO_INCREMENT,
    username VARCHAR(65) NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    role ENUM('Admin', 'Faculty', 'Security') NOT NULL,
    suspended INT(11) NOT NULL DEFAULT 0,
    pwd VARCHAR(200) NOT NULL,
    department VARCHAR(100),
    PRIMARY KEY (id),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Step 3: Migrate data from users to members
-- Note: This splits names at the first space
INSERT INTO members (id, username, firstname, lastname, role, pwd, department, suspended)
SELECT 
    id,
    username,
    SUBSTRING_INDEX(name, ' ', 1) as firstname,
    SUBSTRING_INDEX(name, ' ', -1) as lastname,
    role,
    password as pwd,
    department,
    0 as suspended
FROM users;

-- Step 4: Verify data migration
SELECT * FROM members;

-- Step 5: Once verified, drop old table (CAREFUL!)
-- DROP TABLE users;
-- DROP TABLE users_backup;  -- Only after confirming everything works
```

## 🔑 Key Behavior Changes

### 1. No More First Login Password Change
- Old: Users were forced to change password on first login
- New: Users can keep their assigned password indefinitely
- Admins can still reset passwords via admin panel

### 2. Account Suspension
- New feature to suspend accounts without deleting them
- `suspended=0` means active
- `suspended=1` means suspended (cannot login)

### 3. Email Removed
- Email field is no longer part of the members table
- If you need email functionality, you'll need to add it back or use a separate communication method

### 4. Name Handling
- Old: Single `name` field
- New: Separate `firstname` and `lastname` fields
- Display name in session: `firstname + ' ' + lastname`

## 🧪 Testing

After migration, test these functions:

1. **Login**
   - Try logging in with admin/password123
   - Verify suspended accounts cannot login

2. **Create New Member**
   - Use `python create_user_directly.py`
   - Enter firstname and lastname separately

3. **Change Password**
   - Login and go to change password page
   - Verify password updates successfully

4. **Admin Functions**
   - Create new member via admin panel
   - Reset member password
   - Delete member (except admins)

## 📞 Support

If you encounter issues after migration:
1. Check error messages in terminal/console
2. Verify database connection in phpMyAdmin
3. Ensure all column names match the new schema
4. Review `TROUBLESHOOTING.md` for common issues

## ✅ Verification Checklist

- [ ] Database schema updated successfully
- [ ] Can login with admin/password123
- [ ] Can create new members
- [ ] Can change password
- [ ] Visitor entry still works
- [ ] All dashboards load correctly
- [ ] No errors in browser console
- [ ] No errors in Python terminal

---

**Last Updated**: February 11, 2026  
**Schema Version**: members v1.0
