"""
Direct Member Creation Script
Use this script to create members directly in the database without using phpMyAdmin
"""

from db_config import execute_query
import hashlib

def create_user_in_db(username, password, role, firstname, lastname, department):
    """Create a member directly in the database with proper password hashing"""
    
    # Check if username already exists
    existing = execute_query("SELECT username FROM members WHERE username = %s", (username,), fetch=True)
    if existing:
        return False, "Username already exists"
    
    # Hash the password
    try:
        hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()
    except Exception as e:
        return False, f"Password hashing failed: {e}"
    
    # Insert member
    try:
        result = execute_query(
            "INSERT INTO members (username, pwd, role, firstname, lastname, department, suspended) VALUES (%s, %s, %s, %s, %s, %s, 0)",
            (username, hashed_password, role, firstname, lastname, department)
        )
        
        if result:
            return True, "Member created successfully"
        else:
            return False, "Database insertion failed"
            
    except Exception as e:
        return False, f"Database error: {e}"

def main():
    print("=" * 60)
    print("👤 DIRECT MEMBER CREATION TOOL")
    print("=" * 60)
    print()
    print("Create members directly in the database with proper password hashing.")
    print("This is easier than using phpMyAdmin manually.")
    print()
    
    while True:
        print("Enter member details (or 'quit' to exit):")
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
            
        firstname = input("First Name: ").strip()
        if not firstname:
            print("❌ First name is required!")
            continue
        
        lastname = input("Last Name: ").strip()
        if not lastname:
            print("❌ Last name is required!")
            continue
        
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
            
        department = input("Department (optional): ").strip()
        
        print(f"\nCreating member:")
        print(f"  Username: {username}")
        print(f"  Name: {firstname} {lastname}")
        print(f"  Role: {role}")
        print(f"  Department: {department or 'None'}")
        print()
        
        confirm = input("Create this member? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Member creation cancelled.")
            continue
        
        # Create the member
        success, message = create_user_in_db(username, password, role, firstname, lastname, department)
        
        if success:
            print("✅ " + message)
            print(f"🔑 Member can login with: {username} / {password}")
        else:
            print("❌ " + message)
        
        print("-" * 40)
        print()

if __name__ == "__main__":
    main()