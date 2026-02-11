import os
import re
import base64
import pytz
import csv
import bcrypt
from datetime import datetime
from dotenv import load_dotenv
from io import StringIO
from flask import Response, send_from_directory
from werkzeug.utils import secure_filename

# Load env vars before anything else
load_dotenv() 

from flask import Flask, render_template, request, jsonify, session, redirect
from db_config import init_db_pool, execute_query, test_connection

app = Flask(__name__)

# [SECURE] Load Configuration
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_dev_key")

# Photo configuration - now using database BLOB storage
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# NEW: Define IST Timezone
IST = pytz.timezone('Asia/Kolkata')

# Faculty Department Codes (automatically allowed)
ALLOWED_DEPTS = ['cse', 'it', 'ece', 'eee', 'mech', 'civil', 'aids', 'aiml', 'sh', 'auto', 'bme']
FACULTY_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._]+[.](" + "|".join(ALLOWED_DEPTS) + r")@sritcbe\.ac\.in$")

# Department Code to Full Name Mapping
DEPT_MAPPING = {
    'cse': 'CSE',
    'it': 'IT',
    'ece': 'ECE',
    'eee': 'EEE',
    'mech': 'MECH',
    'civil': 'CIVIL',
    'aids': 'AIDS',
    'aiml': 'AIML',
    'sh': 'Science and Humanities',
    'auto': 'AUTOMOBILE',
    'bme': 'BIOMEDICAL'
}

def connect_to_db():
    """Initialize database connection pool"""
    return init_db_pool()

# Initialize database on startup
connect_to_db()

def get_dept_from_email(email):
    try:
        local_part = email.split('@')[0]
        dept_code = local_part.split('.')[-1].lower()
        return DEPT_MAPPING.get(dept_code, "STAFF")
    except:
        return "STAFF"

def save_photo_to_blob(image_bytes):
    """Return photo data and MIME type for database storage"""
    try:
        # Determine MIME type based on image header
        if image_bytes.startswith(b'\xff\xd8\xff'):
            mime_type = 'image/jpeg'
        elif image_bytes.startswith(b'\x89PNG'):
            mime_type = 'image/png'
        else:
            mime_type = 'image/jpeg'  # Default
        
        return image_bytes, mime_type
    except Exception as e:
        print(f"❌ Photo processing error: {e}")
        return None, None

def format_time(time_value):
    """Convert timedelta or time to formatted string"""
    if time_value is None:
        return ''
    # MySQL TIME fields return as timedelta
    if hasattr(time_value, 'total_seconds'):
        # It's a timedelta
        total_seconds = int(time_value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        # Convert to 12-hour format
        period = 'AM' if hours < 12 else 'PM'
        display_hour = hours % 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour:02d}:{minutes:02d} {period}"
    # It's already a time object
    return time_value.strftime("%I:%M %p")

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username and password are required.'})

    # Check if member exists in database
    member = execute_query("SELECT * FROM members WHERE username = %s", (username,), fetch=True)
    
    if not member:
        return jsonify({'status': 'error', 'message': 'Invalid username or password.'})
    
    member = member[0]
    
    # Check if account is suspended
    if member.get('suspended', 0) == 1:
        return jsonify({'status': 'error', 'message': 'Account is suspended. Contact administrator.'})
    
    # Verify password - supports both bcrypt hashed and plain text passwords
    stored_password = member['pwd']
    password_valid = False
    
    if stored_password.startswith('$2b$') or stored_password.startswith('$2a$'):
        # Password is bcrypt hashed - verify with bcrypt
        try:
            password_valid = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
        except Exception:
            password_valid = False
    else:
        # Password is plain text (e.g. created directly in phpMyAdmin)
        password_valid = (password == stored_password)
        
        # Auto-upgrade: hash the plain text password for future security
        if password_valid:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            execute_query("UPDATE members SET pwd = %s WHERE id = %s", (hashed, member['id']))
    
    if not password_valid:
        return jsonify({'status': 'error', 'message': 'Invalid username or password.'})
    
    # Set session
    session['user'] = member['username']
    session['role'] = member['role']
    session['name'] = f"{member['firstname']} {member['lastname']}"
    session['dept'] = member.get('department', 'STAFF')
    session['user_id'] = member['id']
    
    return jsonify({'status': 'success', 'redirect': '/dashboard'})

@app.route('/change-password')
def change_password_page():
    if 'user' not in session:
        return redirect('/')
    return render_template('change_password.html')

@app.route('/api/change-password', methods=['POST'])
def change_password():
    if 'user' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in.'})
    
    data = request.json
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    
    if not new_password or not confirm_password:
        return jsonify({'status': 'error', 'message': 'Both password fields are required.'})
    
    if new_password != confirm_password:
        return jsonify({'status': 'error', 'message': 'Passwords do not match.'})
    
    if len(new_password) < 6:
        return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters.'})
    
    # Hash new password
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Update password
    result = execute_query(
        "UPDATE members SET pwd = %s WHERE username = %s",
        (hashed, session['user'])
    )
    
    if result:
        return jsonify({'status': 'success', 'redirect': '/dashboard'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to update password.'})

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    
    role = session['role']

    if role == 'Security':
        return render_template('security_dashboard.html')
    
    elif role == 'Faculty':
        return render_template('faculty_dashboard.html')
    
    elif role == 'Admin':
        # Get recent visitors (last 20)
        visitors_raw = execute_query(
            "SELECT * FROM visitors ORDER BY created_at DESC LIMIT 20",
            fetch=True
        )
        
        # Format data for display
        visitors_data = []
        for row in visitors_raw or []:
            visitors_data.append({
                'id': row['id'],
                'date': row['date'].strftime('%d-%m-%Y') if row['date'] else '',
                'in_time': format_time(row['in_time']),
                'mobile': row['mobile'],
                'name': row['name'],
                'designation': row['designation'] or '',
                'company': row['company'] or '',
                'laptop': row['laptop'] or '-',
                'to_meet': row['to_meet'],
                'department': row['department'],
                'photo_url': f'/api/photo/{row["id"]}' if row.get('photo_data') else '',
                'out_time': format_time(row['out_time']),
                'entered_by': row['entered_by'] or '',
                'vehicle_number': row['vehicle_number'] or '-'
            })
        
        # Get active visitors (not exited)
        active_raw = execute_query(
            "SELECT * FROM visitors WHERE out_time IS NULL ORDER BY created_at DESC",
            fetch=True
        )
        
        active_visitors = []
        for row in active_raw or []:
            active_visitors.append({
                'id': row['id'],
                'date': row['date'].strftime('%d-%m-%Y') if row['date'] else '',
                'in_time': format_time(row['in_time']),
                'mobile': row['mobile'],
                'name': row['name'],
                'company': row['company'] or '',
                'to_meet': row['to_meet'],
                'department': row['department'],
                'photo_url': f'/api/photo/{row["id"]}' if row.get('photo_data') else ''
            })
        
        # Get pending bookings
        upcoming_bookings = execute_query(
            "SELECT * FROM bookings WHERE status = 'Pending' ORDER BY booking_time DESC",
            fetch=True
        )
        
        # Get completed bookings
        past_bookings = execute_query(
            "SELECT * FROM bookings WHERE status != 'Pending' ORDER BY booking_time DESC LIMIT 50",
            fetch=True
        )
        
        return render_template(
            'admin_dashboard.html',
            visitors=visitors_data,
            active_visitors=active_visitors,
            bookings=upcoming_bookings or [],
            past_bookings=past_bookings or []
        )
    
    return "Unknown Role"

@app.route('/api/book_visitor', methods=['POST'])
def book_visitor():
    if session.get('role') not in ['Faculty', 'Admin']:
        return jsonify({'error': 'Unauthorized'})
    
    data = request.json
    mobile = str(data.get('mobile')).strip()
    
    # Check for duplicate pending bookings
    duplicate = execute_query(
        "SELECT * FROM bookings WHERE visitor_mobile = %s AND status = 'Pending'",
        (mobile,),
        fetch=True
    )
    
    if duplicate:
        return jsonify({'status': 'error', 'message': 'Duplicate: Visitor has pending booking.'})
    
    # Determine host information
    if session['role'] == 'Admin':
        host_name = data.get('to_meet', session['name'])
        host_dept = data.get('department', 'ADMIN')
        booked_by_email = session['user']
    else:
        host_name = session['name']
        host_dept = get_dept_from_email(session['user'])
        booked_by_email = session['user']
    
    # Insert booking
    query = """
        INSERT INTO bookings (booking_time, booked_by_email, host_name, host_department,
                             visitor_mobile, visitor_name, purpose, status, company, vehicle_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending', %s, %s)
    """
    params = (
        datetime.now(IST),
        booked_by_email,
        host_name,
        host_dept,
        mobile,
        data['name'],
        data['purpose'],
        data.get('company', '-'),
        data.get('vehicle', '-')
    )
    
    result = execute_query(query, params)
    if result:
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Database error'})

@app.route('/api/get_today_bookings', methods=['GET'])
def get_today_bookings():
    if session.get('role') != 'Security':
        return jsonify([])
    
    bookings = execute_query(
        "SELECT * FROM bookings WHERE status = 'Pending' ORDER BY booking_time DESC",
        fetch=True
    )
    
    if not bookings:
        return jsonify([])
    
    result = []
    for row in bookings:
        result.append({
            'time': row['booking_time'].strftime("%Y-%m-%d %H:%M:%S") if row['booking_time'] else '',
            'booked_by': row['host_name'],
            'dept': row['host_department'],
            'mobile': row['visitor_mobile'],
            'visitor': row['visitor_name'],
            'purpose': row['purpose'],
            'company': row['company'] or '-',
            'vehicle_number': row['vehicle_number'] or '-'
        })
    
    return jsonify(result)

@app.route('/api/admin/filter_data', methods=['POST'])
def filter_data():
    if session.get('role') != 'Admin':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    data = request.json
    start_date = data.get('from')
    end_date = data.get('to')
    
    query = """
        SELECT * FROM visitors 
        WHERE date >= %s AND date <= %s 
        ORDER BY date DESC, in_time DESC
    """
    
    filtered_rows = execute_query(query, (start_date, end_date), fetch=True)
    
    if filtered_rows is None:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    # Convert to list format for compatibility
    data_list = []
    for row in filtered_rows:
        data_list.append([
            row['date'].strftime("%d-%m-%Y"),
            format_time(row['in_time']),
            row['mobile'],
            row['name'],
            row['designation'] or '',
            row['company'] or '',
            row['laptop'] or '-',
            row['to_meet'],
            row['department'],
            'Photo in Database',
            format_time(row['out_time']),
            row['entered_by'] or '',
            row['vehicle_number'] or '-',
            row['id']  # Add ID at index 13
        ])
    
    headers = ['Date', 'In Time', 'Mobile', 'Name', 'Designation', 'Company', 
               'Laptop', 'To Meet', 'Department', 'Photo', 'Out Time', 'Entered By', 'Vehicle', 'ID']
    
    return jsonify({
        'status': 'success',
        'headers': headers,
        'data': data_list
    })

@app.route('/api/admin/download_report', methods=['GET'])
def download_report():
    if session.get('role') != 'Admin':
        return "Unauthorized", 403
    
    start_date = request.args.get('from')
    end_date = request.args.get('to')
    
    query = """
        SELECT * FROM visitors 
        WHERE date >= %s AND date <= %s 
        ORDER BY date DESC, in_time DESC
    """
    
    rows = execute_query(query, (start_date, end_date), fetch=True)
    
    si = StringIO()
    cw = csv.writer(si)
    
    # Header row
    cw.writerow(['Date', 'In Time', 'Mobile', 'Name', 'Designation', 'Company', 
                 'Laptop', 'To Meet', 'Department', 'Photo URL', 'Out Time', 'Entered By', 'Vehicle'])
    
    # Data rows
    for row in rows:
        cw.writerow([
            row['date'].strftime("%d-%m-%Y"),
            format_time(row['in_time']),
            row['mobile'],
            row['name'],
            row['designation'] or '',
            row['company'] or '',
            row['laptop'] or '-',
            row['to_meet'],
            row['department'],
            'Photo in Database',
            format_time(row['out_time']),
            row['entered_by'] or '',
            row['vehicle_number'] or '-'
        ])
    
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=Visitor_Report_{start_date}_to_{end_date}.csv"}
    )

@app.route('/api/check_visitor', methods=['GET'])
def check_visitor():
    mobile = request.args.get('mobile')
    
    # Check bookings first
    booking = execute_query(
        "SELECT * FROM bookings WHERE visitor_mobile = %s AND status = 'Pending' ORDER BY booking_time DESC LIMIT 1",
        (mobile,),
        fetch=True
    )
    
    if booking:
        row = booking[0]
        return jsonify({
            'found': True,
            'is_booking': True,
            'name': row['visitor_name'],
            'purpose': row['purpose'],
            'booked_by': row['host_name'],
            'department': row['host_department'],
            'company': row['company'] or '-',
            'vehicle': row['vehicle_number'] or '',
            'to_meet': row['host_name']
        })
    
    # Check previous visits
    visitor = execute_query(
        "SELECT * FROM visitors WHERE mobile = %s ORDER BY created_at DESC LIMIT 1",
        (mobile,),
        fetch=True
    )
    
    if visitor:
        row = visitor[0]
        return jsonify({
            'found': True,
            'is_booking': False,
            'name': row['name'],
            'designation': row['designation'] or '',
            'company': row['company'] or '',
            'laptop': row['laptop'] or '-',
            'to_meet': row['to_meet'],
            'department': row['department'],
            'vehicle': row['vehicle_number'] or ''
        })
    
    return jsonify({'found': False})

@app.route('/api/get_next_id', methods=['GET'])
def get_next_id():
    try:
        result = execute_query("SELECT COUNT(*) as count FROM visitors", fetch=True)
        next_id = result[0]['count'] + 1 if result else 1
        return jsonify({'next_id': next_id})
    except:
        return jsonify({'next_id': '---'})

@app.route('/api/entry', methods=['POST'])
def entry():
    if session.get('role') != 'Security':
        return jsonify({'error': 'Unauthorized'})
    
    try:
        data = request.json
        image_data = data['image']
        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        
        now = datetime.now(IST)
        filename = f"{now.strftime('%d-%m-%Y')}_{data['mobile']}_{now.strftime('%H%M%S')}.jpg"
        
        # Process photo for database storage
        photo_data, mime_type = save_photo_to_blob(image_bytes)
        
        if not photo_data:
            return jsonify({'status': 'error', 'message': 'Photo processing failed.'})
        
        # Insert visitor entry
        query = """
            INSERT INTO visitors (date, in_time, mobile, name, designation, company, laptop,
                                 to_meet, department, photo_data, photo_mime_type, entered_by, vehicle_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            now.date(),
            now.time(),
            data['mobile'],
            data['name'],
            data['designation'],
            data['company'],
            data.get('laptop', '-'),
            data['to_meet'],
            data['department'],
            photo_data,
            mime_type,
            session['user'],
            data.get('vehicle', '-')
        )
        
        visitor_id = execute_query(query, params)
        
        if visitor_id:
            # Update booking status if exists
            execute_query(
                "UPDATE bookings SET status = 'Arrived' WHERE visitor_mobile = %s AND status = 'Pending'",
                (data['mobile'],)
            )
            
            # Create photo URL for the visitor
            photo_url = f'/api/photo/{visitor_id}'
            
            return jsonify({
                'status': 'success',
                'pass_id': visitor_id,
                'date': now.strftime("%d-%m-%Y"),
                'in_time': now.strftime("%I:%M %p"),
                'photo': photo_url
            })
        else:
            return jsonify({'status': 'error', 'message': 'Database error'})
            
    except Exception as e:
        print(f"Entry error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/exit', methods=['POST'])
def exit_visitor():
    data = request.json
    mobile = str(data.get('mobile')).strip()
    
    try:
        # Find latest entry without exit time
        visitor = execute_query(
            "SELECT * FROM visitors WHERE mobile = %s AND out_time IS NULL ORDER BY created_at DESC LIMIT 1",
            (mobile,),
            fetch=True
        )
        
        if not visitor:
            # Check if already exited
            last_visit = execute_query(
                "SELECT * FROM visitors WHERE mobile = %s ORDER BY created_at DESC LIMIT 1",
                (mobile,),
                fetch=True
            )
            if last_visit and last_visit[0]['out_time']:
                return jsonify({
                    'status': 'error',
                    'message': f"Already OUT (Time: {last_visit[0]['out_time'].strftime('%I:%M %p')})"
                })
            return jsonify({'status': 'error', 'message': 'Visitor not found in database'})
        
        # Update exit time
        out_time = datetime.now(IST).time()
        execute_query(
            "UPDATE visitors SET out_time = %s WHERE id = %s",
            (out_time, visitor[0]['id'])
        )
        
        return jsonify({
            'status': 'success',
            'out_time': out_time.strftime("%I:%M %p")
        })
        
    except Exception as e:
        print(f"Exit Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/get_active_visitors', methods=['GET'])
def get_active_visitors():
    """Get all visitors currently inside (no exit time)"""
    if session.get('role') != 'Security':
        return jsonify([])
    
    try:
        query = """
            SELECT id, name, company, to_meet, department, in_time, mobile
            FROM visitors
            WHERE out_time IS NULL
            ORDER BY in_time DESC
        """
        
        active_visitors = execute_query(query, fetch=True)
        
        if not active_visitors:
            return jsonify([])
        
        result = []
        for visitor in active_visitors:
            result.append({
                'id': visitor['id'],
                'name': visitor['name'],
                'company': visitor['company'] or '-',
                'to_meet': visitor['to_meet'],
                'department': visitor['department'],
                'entry_time': format_time(visitor['in_time']),
                'mobile': visitor['mobile']
            })
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Get Active Visitors Error: {e}")
        return jsonify([])

@app.route('/api/checkout_visitor', methods=['POST'])
def checkout_visitor():
    """Check out a visitor by ID with optional custom time"""
    if session.get('role') != 'Security':
        return jsonify({'status': 'error', 'message': 'Unauthorized'})
    
    try:
        data = request.json
        visitor_id = data.get('visitor_id')
        custom_time = data.get('custom_time')  # Optional: HH:MM format
        
        if not visitor_id:
            return jsonify({'status': 'error', 'message': 'Visitor ID required'})
        
        # Determine exit time
        if custom_time:
            # Parse custom time (format: HH:MM from time input)
            try:
                time_parts = custom_time.split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                
                # Validate time
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    return jsonify({'status': 'error', 'message': 'Invalid time format'})
                
                # Create time object in IST
                from datetime import time
                out_time = time(hour, minute, 0)
            except Exception as e:
                return jsonify({'status': 'error', 'message': 'Invalid time format. Use HH:MM'})
        else:
            # Use current time
            out_time = datetime.now(IST).time()
        
        # Update exit time
        execute_query(
            "UPDATE visitors SET out_time = %s WHERE id = %s",
            (out_time, visitor_id)
        )
        
        return jsonify({
            'status': 'success',
            'out_time': out_time.strftime("%I:%M %p")
        })
        
    except Exception as e:
        print(f"Checkout Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

# Photo serving route
@app.route('/api/photo/<int:visitor_id>')
def get_visitor_photo(visitor_id):
    """Serve visitor photo from database"""
    try:
        photo_data = execute_query(
            "SELECT photo_data, photo_mime_type FROM visitors WHERE id = %s AND photo_data IS NOT NULL",
            (visitor_id,),
            fetch=True
        )
        
        if not photo_data:
            return "Photo not found", 404
        
        photo_row = photo_data[0]
        return Response(
            photo_row['photo_data'], 
            mimetype=photo_row['photo_mime_type'] or 'image/jpeg'
        )
    except Exception as e:
        return "Error loading photo", 500

# Member Management Routes
@app.route('/api/admin/users', methods=['GET'])
def get_users():
    """Get all members for admin panel"""
    if session.get('role') != 'Admin':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    try:
        members = execute_query(
            "SELECT username, CONCAT(firstname, ' ', lastname) as name, role, department, suspended FROM members ORDER BY role, firstname", 
            fetch=True
        )
        return jsonify({'status': 'success', 'users': members or []})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/admin/users', methods=['POST'])
def create_user():
    """Create a new member with default password"""
    if session.get('role') != 'Admin':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    data = request.json
    username = data.get('username', '').strip()
    name = data.get('name', '').strip()
    department = data.get('department', '')
    role = data.get('role', 'Faculty')
    
    if not username or not name:
        return jsonify({'status': 'error', 'message': 'Username and name are required'})
    
    # Split name into firstname and lastname
    name_parts = name.split(' ', 1)
    firstname = name_parts[0]
    lastname = name_parts[1] if len(name_parts) > 1 else ''
    
    try:
        # Check if username already exists
        existing = execute_query("SELECT username FROM members WHERE username = %s", (username,), fetch=True)
        if existing:
            return jsonify({'status': 'error', 'message': 'Username already exists'})
        
        # Hash default password
        default_password = 'password123'
        hashed = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert new member
        execute_query(
            "INSERT INTO members (username, pwd, role, firstname, lastname, department, suspended) VALUES (%s, %s, %s, %s, %s, %s, 0)",
            (username, hashed, role, firstname, lastname, department)
        )
        
        return jsonify({'status': 'success', 'message': 'Member created successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/admin/users/<username>', methods=['DELETE'])
def delete_user(username):
    """Delete a member (except admins)"""
    if session.get('role') != 'Admin':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    try:
        # Check if member exists and is not admin
        member = execute_query("SELECT role FROM members WHERE username = %s", (username,), fetch=True)
        if not member:
            return jsonify({'status': 'error', 'message': 'Member not found'})
        
        if member[0]['role'] == 'Admin':
            return jsonify({'status': 'error', 'message': 'Cannot delete admin members'})
        
        execute_query("DELETE FROM members WHERE username = %s", (username,))
        return jsonify({'status': 'success', 'message': 'Member deleted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/admin/reset-password', methods=['POST'])
def reset_user_password():
    """Reset member password to default"""
    if session.get('role') != 'Admin':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({'status': 'error', 'message': 'Username required'})
    
    try:
        # Hash default password
        default_password = 'password123'
        hashed = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        execute_query(
            "UPDATE members SET pwd = %s WHERE username = %s",
            (hashed, username)
        )
        
        return jsonify({'status': 'success', 'message': 'Password reset successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    # Test database connection on startup
    if test_connection():
        print("🚀 Starting Flask application...")
        app.run(debug=True, port=5000)
    else:
        print("❌ Cannot start: Database connection failed!")
