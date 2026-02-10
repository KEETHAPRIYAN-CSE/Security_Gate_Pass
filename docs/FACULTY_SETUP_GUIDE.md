# Adding Faculty Users to the System

## Quick Setup

### Step 1: Create Faculty Firebase Accounts
These users must be created in your Firebase Authentication console:

**Required Accounts:**
1. **Admin**: admin@sritcbe.ac.in
2. **Security**: security@sritcbe.ac.in
3. **Faculty Examples**:
   - john.cse@sritcbe.ac.in
   - mary.it@sritcbe.ac.in
   - raj.ece@sritcbe.ac.in
   - priya.mech@sritcbe.ac.in
   - kumar.civil@sritcbe.ac.in
   - sara.eee@sritcbe.ac.in

### Step 2: Add Users to MySQL Database

**Option A: Run Complete Schema (Fresh Install)**
1. Open phpMyAdmin (http://localhost/phpmyadmin)
2. Click on SQL tab
3. Copy and paste entire contents of `db_schema.sql`
4. Click "Go" button
5. Done! All 8 users (Admin, Security, 6 Faculty) are created

**Option B: Add Faculty Only (Existing Database)**
1. Open phpMyAdmin
2. Select `visitor_management` database
3. Click SQL tab
4. Copy and paste contents of `add_faculty_users.sql`
5. Click "Go" button

## Email Format Requirements

**Faculty emails MUST follow this pattern:**
```
firstname.department@sritcbe.ac.in
```

**Valid Department Codes:**
- CSE - Computer Science and Engineering
- IT - Information Technology
- ECE - Electronics and Communication Engineering
- EEE - Electrical and Electronics Engineering
- MECH - Mechanical Engineering
- CIVIL - Civil Engineering
- AIDS - Artificial Intelligence and Data Science
- AIML - Artificial Intelligence and Machine Learning

## Adding New Faculty Member

### Example: Add "Dr. David Wilson" from CSE Department

**Step 1: Create Firebase Account**
1. Go to Firebase Console → Authentication → Users
2. Click "Add User"
3. Email: `david.cse@sritcbe.ac.in`
4. Password: (set temporary password)
5. Click "Add User"

**Step 2: Add to MySQL Database**
1. Open phpMyAdmin → visitor_management → SQL tab
2. Run this query:
```sql
INSERT IGNORE INTO users (email, role, name, department) VALUES
('david.cse@sritcbe.ac.in', 'Faculty', 'Dr. David Wilson', 'CSE');
```

**Step 3: Verify**
```sql
SELECT * FROM users WHERE email = 'david.cse@sritcbe.ac.in';
```

## Bulk Add Multiple Faculty

Use this template in phpMyAdmin SQL tab:

```sql
USE visitor_management;

INSERT IGNORE INTO users (email, role, name, department) VALUES
('david.cse@sritcbe.ac.in', 'Faculty', 'Dr. David Wilson', 'CSE'),
('anita.it@sritcbe.ac.in', 'Faculty', 'Dr. Anita Sharma', 'IT'),
('robert.ece@sritcbe.ac.in', 'Faculty', 'Dr. Robert Thomas', 'ECE'),
('lakshmi.eee@sritcbe.ac.in', 'Faculty', 'Dr. Lakshmi Devi', 'EEE');
```

## View All Faculty

```sql
SELECT email, name, department 
FROM users 
WHERE role = 'Faculty' 
ORDER BY department, name;
```

## Important Notes

⚠️ **Both Steps Required:**
- Faculty MUST be created in **Firebase** (for login)
- Faculty MUST be added to **MySQL** (for role/department)
- If user is missing from either, login will fail

⚠️ **Email Format:**
- Use lowercase letters only
- Format: `firstname.dept@sritcbe.ac.in`
- No spaces, no special characters except dot (.)

⚠️ **Department Codes:**
- Use standard abbreviations (CSE, IT, ECE, etc.)
- Must match faculty's actual department
- Used for booking assignments and reporting

## Troubleshooting

**"Access Denied" Error:**
- Check if user exists in Firebase Authentication
- Check if user exists in MySQL users table
- Verify email spelling is identical in both places

**"Invalid Credentials":**
- Check Firebase password
- Try password reset in Firebase Console

**User Can Login but No Dashboard:**
- Check user's role in MySQL database
- Faculty role should show Faculty Dashboard
- Admin role should show Admin Console
- Security role should show Security Dashboard
