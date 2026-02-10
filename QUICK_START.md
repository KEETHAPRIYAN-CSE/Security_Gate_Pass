# 🎯 Quick Start Guide - Database Authentication

## ⚡ What You Need to Do (Step-by-Step)

### 1️⃣ Install XAMPP (5 minutes)
- Download: https://www.apachefriends.org/download.html
- Install to default location: `C:\xampp`
- Start **Apache** and **MySQL** from XAMPP Control Panel

### 2️⃣ Create Database (2 minutes)
1. Open browser → `http://localhost/phpmyadmin`
2. Click "New" to create database
3. Click "SQL" tab
4. Copy **all content** from `db_schema.sql` file
5. Paste and click "Go"
6. ✅ You should see `visitor_management` database with 3 tables

### 3️⃣ Photo Storage (Built-in)
✅ Photos are stored directly in the database as BLOB data.
- No additional setup required
- Photos are automatically backed up with the database
- Access via: `/api/photo/<visitor_id>`

### 4️⃣ Configure Environment (1 minute)
1. In your project folder, copy `.env.example` to `.env`:
   ```
   copy .env.example .env
   ```
2. Open `.env` in notepad
3. Update this value:
   - `FLASK_SECRET_KEY`: Put any random text (e.g., "my_secret_key_12345")
   - Database settings should work as-is (defaults for XAMPP)
   - No Firebase setup needed anymore!

### 5️⃣ Install Dependencies (2 minutes)
```bash
cd D:\V8\V7
pip install -r requirements.txt
```

### 6️⃣ Replace Application File (1 minute)
**Option A - Backup old file:**
```bash
move app.py app_old.py
move app_mysql.py app.py
```

### 6️⃣ Application Ready
Your `app.py` file is already updated with database authentication. No file changes needed!

### 7️⃣ Test Everything (2 minutes)
```bash
python setup_mysql.py
```

If all checks pass ✅, start the app:
```bash
python app.py
```

### 8️⃣ Access Application
Open browser: `http://localhost:5000`

## 🔑 Login Credentials

Use username and password authentication:
- **Admin**: username=`admin`, password=`password123`
- **Security**: username=`security`, password=`password123`
- **Faculty**: Created by admin with default password `password123`

**Note**: All users must change password on first login for security.

## 🎨 What Changed?

| Before | After |
|--------|-------|
| Google Sheets | MySQL Database |
| Google Drive | Database BLOB storage |
| Slow API calls | Fast local database |
| Quota limits | No limits |
| Internet required | Works offline |

## 📊 Your Data

Photos are stored in:
- **Location**: MySQL database (BLOB data)
- **Access**: Via API `/api/photo/<visitor_id>`
- **Benefits**: Centralized storage, automatic backup
- **Format**: JPEG binary data in database

Database is in:
- **Name**: `visitor_management`
- **Tables**: users, visitors, bookings
- **Access**: http://localhost/phpmyadmin

## 🆘 Common Issues

### Issue: "Database connection failed"
**Solution**: 
1. Check XAMPP MySQL is running (green in Control Panel)
2. Make sure you ran `db_schema.sql` in phpMyAdmin
3. Check `.env` file has correct database name

### Issue: "Photo upload failed"
**Solution**: This should not occur with database BLOB storage.
- Check database connection is working
- Verify MySQL is running in XAMPP
- Check if `visitors` table has `photo_data` column

### Issue: "Port 5000 already in use"
**Solution**: Change port in `app.py` (last line):
```python
app.run(debug=True, port=5001)
```

### Issue: "Cannot import db_config"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

## ✅ Checklist

Before running the app, make sure:
- [ ] XAMPP installed and MySQL running
- [ ] Database `visitor_management` created via phpMyAdmin
- [ ] `db_schema.sql` executed successfully  
- [ ] `.env` file created and configured
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `app_mysql.py` renamed to `app.py` (old one backed up)

## 📚 Need More Help?

Read these files:
1. **MIGRATION_GUIDE.md** - Detailed migration steps
2. **FILE_STRUCTURE.md** - Project structure explanation
3. **db_schema.sql** - Database structure

## 🎉 You're Done!

Once `python app.py` starts successfully, you'll have:
- ✅ MySQL database instead of Google Sheets
- ✅ Local photo storage instead of Google Drive
- ✅ Faster performance
- ✅ No Google API dependencies
- ✅ No quota limits
- ✅ Works completely offline

**Total setup time: ~15 minutes**
