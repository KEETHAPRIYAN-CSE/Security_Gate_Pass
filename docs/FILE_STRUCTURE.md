# 📁 Project Structure - MySQL Version

## New Files (Added)
```
├── db_schema.sql           # MySQL database schema
├── db_config.py            # Database connection & utilities
├── app_mysql.py            # New MySQL-based application
├── setup_mysql.py          # Quick setup script
├── .env.example            # Environment variables template
├── MIGRATION_GUIDE.md      # Complete migration instructions
└── FILE_STRUCTURE.md       # This file
```

## Modified Files
```
└── requirements.txt        # Updated dependencies (removed Google APIs, added MySQL)
```

## Unchanged Files (Keep as-is)
```
├── templates/
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── faculty_dashboard.html
│   └── security_dashboard.html
├── static/
│   ├── script.js
│   └── style.css
└── vercel.json             # May need updates for production deployment
```

## Files to Remove (After Migration)
```
├── drive_manager.py        # No longer needed (Google Drive)
├── setup_drive.py          # No longer needed (Google Drive)
├── app.py                  # Replace with app_mysql.py
├── credentials.json        # Google OAuth credentials (delete)
└── token.json              # Google OAuth token (delete)
```

## Configuration Files

### .env (Create from .env.example)
Environment variables for:
- Flask configuration
- MySQL database credentials
- Photo upload folder path
- Firebase authentication

### db_schema.sql
Database structure:
- `users` table: Faculty, Admin, Security
- `visitors` table: Entry/exit logs
- `bookings` table: Pre-booking system

## Directory Structure After Migration

```
D:\V8\V7\                          # Your project root
├── app.py                         # Main application (renamed from app_mysql.py)
├── db_config.py                   # Database utilities
├── db_schema.sql                  # SQL schema
├── setup_mysql.py                 # Setup script
├── requirements.txt               # Python dependencies
├── .env                           # Environment config (create this)
├── .env.example                   # Environment template
├── MIGRATION_GUIDE.md             # Migration instructions
├── FILE_STRUCTURE.md              # This file
├── static/
│   ├── script.js
│   └── style.css
└── templates/
    ├── login.html
    ├── admin_dashboard.html
    ├── faculty_dashboard.html
    └── security_dashboard.html

C:\xampp\htdocs\visitor_photos\    # Photo storage location
```

## Key Changes

### Database Layer
- **Before**: Google Sheets API (gspread)
- **After**: MySQL with connection pooling

### Photo Storage
- **Before**: Google Drive API
- **After**: XAMPP htdocs folder (C:/xampp/htdocs/visitor_photos/)

### Dependencies
- **Removed**: gspread, google-api-python-client, google-auth-*
- **Added**: mysql-connector-python, Pillow

## Quick Start

1. Install XAMPP
2. Run `db_schema.sql` in phpMyAdmin
3. Copy `.env.example` to `.env` and configure
4. Run `python setup_mysql.py` to verify setup
5. Install dependencies: `pip install -r requirements.txt`
6. Rename `app_mysql.py` to `app.py` (or delete old app.py first)
7. Run: `python app.py`

## File Purposes

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application with routes |
| `db_config.py` | Database connection pooling and query execution |
| `db_schema.sql` | Creates database tables and default users |
| `setup_mysql.py` | Automated setup verification script |
| `.env` | Configuration (database, paths, secrets) |
| `requirements.txt` | Python package dependencies |
| `templates/*.html` | Frontend HTML templates |
| `static/*.{js,css}` | Frontend scripts and styles |

## Important Paths

| Purpose | Path |
|---------|------|
| Application | `D:\V8\V7\` |
| Photos | `C:\xampp\htdocs\visitor_photos\` |
| Database | phpMyAdmin: `http://localhost/phpmyadmin` |
| Web Access | `http://localhost:5000` |
| Photo URL | `http://localhost:5000/visitor_photos/{filename}` |
| Photo Direct | `http://localhost/visitor_photos/{filename}` |

## Notes

- Photos are stored as files, not in database (only path is stored)
- Database uses connection pooling for better performance
- All times are in IST timezone
- Firebase is still used for authentication
- Default MySQL password is blank (change in production)
