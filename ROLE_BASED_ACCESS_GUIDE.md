# 🔐 Role-Based Dashboard Access Guide

## Overview
The system uses the `role` field in the `members` table to automatically route users to their appropriate dashboard after login.

## Roles and Dashboards

| Role | Dashboard | Access Level | Features |
|------|-----------|--------------|----------|
| **Admin** | Admin Dashboard | Full System Access | • View all visitors<br>• Manage bookings<br>• Create/delete members<br>• Reset passwords<br>• View analytics |
| **Faculty** | Faculty Dashboard | Booking & Viewing | • Book visitors<br>• View own bookings<br>• Cancel bookings<br>• View visitor status |
| **Security** | Security Dashboard | Entry/Exit Control | • Add visitor entries<br>• Record visitor exits<br>• Capture photos<br>• Quick check-in/out |

## How It Works

### 1. Login Process
```
User enters credentials → System checks members table → Validates password
→ If valid: Sets session with role → Redirects to /dashboard
→ Dashboard route checks role → Routes to correct dashboard
```

### 2. Code Flow
```python
# In app.py - Login sets the session
session['role'] = member['role']  # From database

# In app.py - Dashboard routing
if role == 'Admin':
    return render_template('admin_dashboard.html')
elif role == 'Faculty':
    return render_template('faculty_dashboard.html')
elif role == 'Security':
    return render_template('security_dashboard.html')
```

## Testing Role-Based Access

### Test Accounts (Default)

1. **Admin Account**
   - Username: `admin`
   - Password: `password123`
   - Expected: Admin Dashboard

2. **Security Account**
   - Username: `security`
   - Password: `password123`
   - Expected: Security Dashboard

### Create Test Faculty Account

**Option 1: Using Python Script**
```bash
python create_user_directly.py
```
Enter:
- Username: `test.faculty`
- Password: `test123`
- First Name: `Test`
- Last Name: `Faculty`
- Role: `1` (Faculty)
- Department: `CSE`

**Option 2: Using phpMyAdmin**
```sql
-- Generate hash first: python generate_password_hash.py
-- Enter password: test123

INSERT INTO members (username, pwd, role, firstname, lastname, department, suspended) 
VALUES ('test.faculty', '$2b$12$YOUR_HASH_HERE', 'Faculty', 'Test', 'Faculty', 'CSE', 0);
```

**💡 TIP**: In phpMyAdmin's Insert interface, the `role` field shows as a **dropdown menu** - just click and select Admin, Faculty, or Security!

## Verification Steps

1. **Clear Browser Cache/Session**
   - Close all browser windows
   - Or use incognito mode

2. **Test Each Role**

   **Admin Test:**
   ```
   Login: admin / password123
   Expected: See "Admin Dashboard" with all visitors, user management
   ```

   **Security Test:**
   ```
   Login: security / password123
   Expected: See "Security Dashboard" with visitor entry form
   ```

   **Faculty Test:**
   ```
   Login: test.faculty / test123
   Expected: See "Faculty Dashboard" with booking form
   ```

3. **Verify Session Data**
   - Open browser console (F12)
   - Check that correct dashboard loads
   - Verify no errors in console

## Common Issues & Solutions

### ❌ Wrong Dashboard Appears

**Cause**: Role mismatch in database

**Solution**:
```sql
-- Check current role
SELECT username, role FROM members;

-- Fix role if needed (EXACT case-sensitive match required)
UPDATE members SET role = 'Admin' WHERE username = 'admin';
UPDATE members SET role = 'Faculty' WHERE username = 'test.faculty';
UPDATE members SET role = 'Security' WHERE username = 'security';
```

### ❌ "Unknown Role" Message

**Cause**: Role value doesn't match 'Admin', 'Faculty', or 'Security'

**Solution**:
```sql
-- Check for typos or wrong case
SELECT username, role, LENGTH(role), 
       CASE 
         WHEN role = 'Admin' THEN 'MATCH'
         WHEN role = 'Faculty' THEN 'MATCH'
         WHEN role = 'Security' THEN 'MATCH'
         ELSE 'NO MATCH - FIX NEEDED'
       END as role_status
FROM members;
```

### ❌ Redirects to Login After Successful Login

**Cause**: Session not being set

**Solution**:
- Check Flask secret key in `.env` file
- Ensure cookies are enabled in browser
- Check console for JavaScript errors

## Valid Role Values (Case-Sensitive!)

✅ **Correct:**
- `'Admin'`
- `'Faculty'`
- `'Security'`

❌ **Incorrect:**
- `'admin'` (lowercase)
- `'ADMIN'` (uppercase)
- `'Administrator'` (wrong value)
- `'faculty'` (lowercase)
- `'security'` (lowercase)

## Database Schema Reference

```sql
CREATE TABLE IF NOT EXISTS members (
    id INT(4) NOT NULL AUTO_INCREMENT,
    username VARCHAR(65) NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    role ENUM('Admin', 'Faculty', 'Security') NOT NULL,  -- Dropdown in phpMyAdmin!
    suspended INT(11) NOT NULL DEFAULT 0,  -- 0=Active, 1=Suspended
    pwd VARCHAR(200) NOT NULL,
    department VARCHAR(100),
    PRIMARY KEY (id)
);
```

**✨ NEW: Role is ENUM type** - When you add/edit members in phpMyAdmin, the `role` field shows a dropdown menu with three options: Admin, Faculty, Security. Just click to select!

## Quick Commands

### Check All Members and Their Roles
```sql
SELECT username, role, CONCAT(firstname, ' ', lastname) as name, 
       CASE WHEN suspended = 0 THEN 'Active' ELSE 'Suspended' END as status
FROM members
ORDER BY role, username;
```

### Create New Member (All Roles Example)
```sql
-- Faculty Member
INSERT INTO members (username, pwd, role, firstname, lastname, department, suspended) 
VALUES ('john.cse', '$2b$12$HASH', 'Faculty', 'John', 'Doe', 'CSE', 0);

-- Admin Member
INSERT INTO members (username, pwd, role, firstname, lastname, department, suspended) 
VALUES ('admin2', '$2b$12$HASH', 'Admin', 'Admin', 'Two', 'ADMIN', 0);

-- Security Member
INSERT INTO members (username, pwd, role, firstname, lastname, department, suspended) 
VALUES ('gate2', '$2b$12$HASH', 'Security', 'Gate', 'Officer', 'SECURITY', 0);
```

## Summary

✅ **Role determines dashboard access automatically**  
✅ **Three valid roles: Admin, Faculty, Security**  
✅ **Case-sensitive matching required**  
✅ **Default accounts ready to test**  
✅ **Session-based authentication with role routing**

---

**Need Help?**
- Check terminal for error messages
- Verify database connection
- Ensure role values match exactly (case-sensitive)
- See `TROUBLESHOOTING.md` for more help
