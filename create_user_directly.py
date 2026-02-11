"""
Direct User Creation Script
Use this script to create users directly in the database without using phpMyAdmin
"""

from db_config import execute_query
import bcrypt

def create_user_in_db(username, password, email, role, name, department):
    """Create a user directly in the database with proper password hashing"""
    
    # Check if username already exists
    existing = execute_query("SELECT username FROM users WHERE username = %s", (username,), fetch=True)
    if existing:
        return False, "Username already exists"
    
    # Hash the password
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except Exception as e:
        return False, f"Password hashing failed: {e}"
    
    # Insert user
    try:
        result = execute_query(
            "INSERT INTO users (username, password, email, role, name, department, first_login) VALUES (%s, %s, %s, %s, %s, %s, TRUE)",
            (username, hashed_password, email, role, name, department)
        )
        
        if result:
            return True, "User created successfully"
        else:
            return False, "Database insertion failed"
            
    except Exception as e:
        return False, f"Database error: {e}"

def main():
    print("=" * 60)
    print("👤 DIRECT USER CREATION TOOL")
    print("=" * 60)
    print()
    print("Create users directly in the database with proper password hashing.")
    print("This is easier than using phpMyAdmin manually.")
    print()
    
    while True:
        print("Enter user details (or 'quit' to exit):")
        print()
        
        username = input("Username: ").strip()
        if username.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        if not username:
            print("❌ Username is required!")
            continue
        
        password = input("Password: ").strip()
        if not password:
            print("❌ Password is required!")
            continue
            
        name = input("Full Name: ").strip()
        if not name:
            print("❌ Full name is required!")
            continue
        
        email = input("Email (optional): ").strip()
        
        print("\nSelect Role:")
        print("1. Faculty")
        print("2. Admin") 
        print("3. Security")
        role_choice = input("Enter choice (1-3): ").strip()
        
        role_map = {'1': 'Faculty', '2': 'Admin', '3': 'Security'}
        role = role_map.get(role_choice)
        
        if not role:
            print("❌ Invalid role selection!")
            continue
            
        department = input("Department: ").strip()
        if not department:
            print("❌ Department is required!")
            continue
        
        print(f"\nCreating user:")
        print(f"  Username: {username}")
        print(f"  Name: {name}")
        print(f"  Role: {role}")
        print(f"  Department: {department}")
        print(f"  Email: {email or 'None'}")
        print()
        
        confirm = input("Create this user? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ User creation cancelled.")
            continue
        
        # Create the user
        success, message = create_user_in_db(username, password, email, role, name, department)
        
        if success:
            print("✅ " + message)
            print(f"🔑 User can login with: {username} / {password}")
        else:
            print("❌ " + message)
        
        print("-" * 40)
        print()

if __name__ == "__main__":
    main()