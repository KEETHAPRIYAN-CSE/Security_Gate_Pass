"""
Password Hash Generator for Manual User Creation
Use this script to generate bcrypt password hashes for inserting users directly into phpMyAdmin
"""

import bcrypt
import sys

def generate_password_hash(password):
    """Generate bcrypt hash for a password"""
    try:
        # Generate hash with bcrypt
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Error generating hash: {e}")
        return None

def main():
    print("=" * 60)
    print("🔐 PASSWORD HASH GENERATOR FOR PHPMYADMIN")
    print("=" * 60)
    print()
    print("This tool generates bcrypt password hashes for manual user creation in phpMyAdmin.")
    print("Copy the generated hash and paste it in the 'password' field in phpMyAdmin.")
    print()
    
    while True:
        # Get password input
        password = input("Enter password to hash (or 'quit' to exit): ").strip()
        
        if password.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        if not password:
            print("❌ Password cannot be empty!")
            continue
            
        if len(password) < 6:
            print("⚠️  Warning: Password should be at least 6 characters for security.")
        
        # Generate hash
        print("\nGenerating hash...")
        hash_result = generate_password_hash(password)
        
        if hash_result:
            print("✅ Hash generated successfully!")
            print()
            print("=" * 60)
            print("COPY THIS HASH TO PHPMYADMIN:")
            print("=" * 60)
            print(hash_result)
            print("=" * 60)
            print()
            print("📝 Instructions for phpMyAdmin:")
            print("1. Go to phpMyAdmin > visitor_management > users table")
            print("2. Click 'Insert' to add new row")
            print("3. Fill in the fields:")
            print("   - username: (your choice)")
            print("   - password: PASTE THE HASH ABOVE")
            print("   - email: (optional)")
            print("   - role: Faculty/Admin/Security")
            print("   - name: (full name)")
            print("   - department: (department code)")
            print("   - first_login: TRUE (they can change password on first login)")
            print("4. Click 'Go' to insert")
            print()
        else:
            print("❌ Failed to generate hash!")
        
        print("-" * 40)

if __name__ == "__main__":
    main()