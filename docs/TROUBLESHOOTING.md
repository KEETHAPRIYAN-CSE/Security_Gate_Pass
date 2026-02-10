# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 🔴 Database Connection Issues

#### Error: "Can't connect to MySQL server on 'localhost'"
**Cause**: MySQL service not running

**Solution**:
1. Open XAMPP Control Panel
2. Click "Start" next to MySQL
3. Wait for it to turn green
4. Retry your application

#### Error: "Access denied for user 'root'@'localhost'"
**Cause**: Incorrect database credentials

**Solution**:
1. Check `.env` file:
   ```env
   DB_USER=root
   DB_PASSWORD=        # Leave blank for default XAMPP
   ```
2. If you set a password in phpMyAdmin, update it here

#### Error: "Unknown database 'visitor_management'"
**Cause**: Database not created

**Solution**:
1. Go to http://localhost/phpmyadmin
2. Click "SQL" tab
3. Run the entire `db_schema.sql` file
4. Verify database appears in left panel

---

### 🔴 Photo Upload Issues

#### Error: "Photo Upload Failed" 
**Cause**: Database connection issue or corrupted image data

**Solution**:
1. Check MySQL connection is working
2. Verify `visitors` table has `photo_data` LONGBLOB column  
3. Test with smaller image (< 2MB)
4. Restart MySQL service in XAMPP

#### Photos save but don't display
**Cause**: Photo API endpoint not working or database issue

**Solution**:
1. Test photo API: `http://localhost:5000/api/photo/1`
2. Check if visitor ID exists in database
3. Verify `photo_data` column is not NULL/empty
4. Check browser console for errors

#### Error: "Photo data too large"
**Cause**: Image file exceeds MySQL max_allowed_packet

**Solution**:  
1. Compress image before upload
2. Increase MySQL max_allowed_packet:
   - Edit `my.cnf` or `my.ini`
   - Add: `max_allowed_packet=64M`
   - Restart MySQL service
3. Ensure "Users" has "Modify" permission
4. Apply changes

---

### 🔴 Application Startup Issues

#### Error: "Port 5000 is already in use"
**Cause**: Another application using port 5000

**Solution**:
```python
# Option 1: Change port in app.py (last line)
app.run(debug=True, port=5001)  # Use 5001 instead

# Option 2: Kill process on port 5000 (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process
```

#### Error: "ModuleNotFoundError: No module named 'mysql'"
**Cause**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt

# If still fails, install manually:
pip install mysql-connector-python
pip install Flask
pip install python-dotenv
pip install pytz
```

#### Error: "No module named 'db_config'"
**Cause**: Running from wrong directory

**Solution**:
```bash
# Make sure you're in the project directory
cd D:\V8\V7

# Then run
python app.py
```

---

### 🔴 XAMPP Issues

#### XAMPP MySQL won't start
**Cause**: Port 3306 already in use (another MySQL instance)

**Solution**:
```bash
# Option 1: Stop other MySQL service
# Open Services (services.msc)
# Find "MySQL" or "MySQL80"
# Right-click → Stop

# Option 2: Change XAMPP MySQL port
# Edit: C:\xampp\mysql\bin\my.ini
# Find: port=3306
# Change to: port=3307
# Restart XAMPP MySQL
# Update .env: DB_PORT=3307
```

#### phpMyAdmin shows "Access Denied"
**Cause**: MySQL user issue

**Solution**:
1. Check XAMPP MySQL is running (green)
2. Default XAMPP credentials:
   - Username: `root`
   - Password: (blank)
3. If changed, update in XAMPP config

#### XAMPP Control Panel won't open
**Cause**: Already running or permission issue

**Solution**:
1. Check system tray for XAMPP icon
2. Right-click XAMPP → Run as Administrator
3. Or restart computer

---

### 🔴 Login & Authentication Issues

#### Error: "Access Denied: User not found"
**Cause**: User not in database

**Solution**:
```sql
-- Run in phpMyAdmin SQL tab
INSERT INTO users (email, role, name, department) 
VALUES ('youremail@sritcbe.ac.in', 'Admin', 'Your Name', 'ADMIN');
```

#### Faculty login not working
**Cause**: Email pattern mismatch

**Solution**:
Faculty emails must match: `name.DEPT@sritcbe.ac.in`
- Valid: `john.cse@sritcbe.ac.in`
- Valid: `mary.it@sritcbe.ac.in`
- Invalid: `john@sritcbe.ac.in` (no department)

Allowed departments: cse, it, me, sh, ece, eee

#### Session expires immediately
**Cause**: Secret key issue

**Solution**:
1. Check `.env` file has `FLASK_SECRET_KEY`
2. Make sure it's a consistent value (don't change it)
3. Restart the application

---

### 🔴 Data & Query Issues

#### Visitors not showing in dashboard
**Cause**: Query error or no data

**Solution**:
```sql
-- Check if data exists (run in phpMyAdmin)
SELECT COUNT(*) FROM visitors;

-- If 0, add test data:
INSERT INTO visitors (date, in_time, mobile, name, designation, company, 
                      to_meet, department, photo_data, photo_mime_type, entered_by)
VALUES (CURDATE(), CURTIME(), '9876543210', 'Test Visitor', 'Manager', 
        'Test Company', 'Test Faculty', 'CSE', NULL, NULL,
        'security@sritcbe.ac.in');
```

#### Bookings not updating to "Arrived"
**Cause**: Mobile number mismatch

**Solution**:
- Ensure mobile number is exactly the same in booking and entry
- No spaces, dashes, or country codes
- Format: `9876543210` (10 digits)

#### Export CSV is empty
**Cause**: Date range issue

**Solution**:
- Check date format is `YYYY-MM-DD`
- Ensure database has data in that range
- Try wider date range

---

### 🔴 Performance Issues

#### Application is slow
**Possible causes**:

1. **No database indexes**:
   ```sql
   -- Run in phpMyAdmin to add indexes
   ALTER TABLE visitors ADD INDEX idx_mobile (mobile);
   ALTER TABLE visitors ADD INDEX idx_date (date);
   ```

2. **Too many connections**:
   ```python
   # In db_config.py, reduce pool size
   pool_size=5  # Default
   pool_size=3  # If issues
   ```

3. **Large database**:
   ```sql
   -- Archive old data (older than 1 year)
   CREATE TABLE visitors_archive AS 
   SELECT * FROM visitors WHERE date < DATE_SUB(CURDATE(), INTERVAL 1 YEAR);
   
   DELETE FROM visitors WHERE date < DATE_SUB(CURDATE(), INTERVAL 1 YEAR);
   ```

---

### 🔴 Migration Issues

#### Lost data during migration
**Solution**:
Google Sheets data is still there! Export manually:
1. Open Google Sheet
2. File → Download → CSV
3. Import to MySQL via phpMyAdmin:
   - Select table
   - Import tab
   - Choose CSV file
   - Map columns
   - Import

#### Old app.py and new one conflict
**Solution**:
```bash
# Backup old file
move app.py app_google_sheets_backup.py

# Use new file
move app_mysql.py app.py

# Or delete old
del app.py
ren app_mysql.py app.py
```

---

## 🔍 Diagnostic Commands

### Check MySQL Status
```bash
# In PowerShell or CMD
mysql -u root -e "SELECT VERSION();"
```

### Check Database Tables
```sql
-- Run in phpMyAdmin SQL tab
SHOW TABLES FROM visitor_management;
DESCRIBE users;
DESCRIBE visitors;
DESCRIBE bookings;
```

### Check Photo Storage
```sql
-- Check if photos are being stored in database
SELECT COUNT(*) FROM visitors WHERE photo_data IS NOT NULL;
SELECT id, mobile, LENGTH(photo_data) as photo_size_bytes 
FROM visitors WHERE photo_data IS NOT NULL LIMIT 5;
```

### Test Database Connection
```bash
# In project directory
python -c "from db_config import test_connection; test_connection()"
```

### Check Flask Server
```bash
# Test if port is open
Test-NetConnection -ComputerName localhost -Port 5000
```

---

## 📝 Logs & Debugging

### Enable Debug Mode
Already enabled in `app.py`:
```python
app.run(debug=True, port=5000)
```

This shows detailed error messages in browser.

### Check MySQL Logs
Location: `C:\xampp\mysql\data\mysql_error.log`

### Check Application Logs
The console where you run `python app.py` shows all errors.

### Browser Console
Press F12 in browser → Console tab
Shows JavaScript errors and API response issues

---

## 🆘 Still Having Issues?

### Checklist
- [ ] XAMPP MySQL is running (green)
- [ ] Database `visitor_management` exists
- [ ] All 3 tables created (users, visitors, bookings)
- [ ] Photo storage: Database BLOB (no folder needed)
- [ ] `.env` file exists and configured
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Using correct `app.py` (MySQL version)
- [ ] No port conflicts (5000, 3306)

### Reset Everything
```bash
# 1. Stop application (Ctrl+C)

# 2. Drop and recreate database
# In phpMyAdmin SQL tab:
DROP DATABASE visitor_management;
# Then run db_schema.sql again

# 3. Clear database data  
TRUNCATE TABLE visitors;
TRUNCATE TABLE bookings;

# 4. Restart MySQL in XAMPP

# 5. Start app
python app.py
```

### Contact Support
If all else fails, check these files for reference:
- `MIGRATION_GUIDE.md` - Full migration steps
- `QUICK_START.md` - Quick setup guide
- `ARCHITECTURE.md` - System design
- `db_schema.sql` - Database structure
