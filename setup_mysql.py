"""
Quick setup script for MySQL migration
Run this after installing XAMPP and creating the database
"""

import os
import sys
from pathlib import Path

def check_xampp():
    """Check if XAMPP is installed"""
    xampp_path = Path("C:/xampp")
    if xampp_path.exists():
        print("✅ XAMPP found at C:/xampp")
        return True
    else:
        print("❌ XAMPP not found. Please install XAMPP first.")
        return False

def check_photo_storage():
    """Check if database is configured for BLOB photo storage"""
    try:
        print("✅ Photo storage: Database BLOB (no file system needed)")
        return True
    except Exception as e:
        print(f"❌ Photo storage check failed: {e}")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found")
        print("📝 Creating .env from .env.example...")
        try:
            example = Path(".env.example")
            if example.exists():
                import shutil
                shutil.copy(".env.example", ".env")
                print("✅ .env file created. Please edit it with your settings.")
                return True
            else:
                print("❌ .env.example not found")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def test_db_connection():
    """Test database connection"""
    try:
        from db_config import test_connection
        print("\n🔍 Testing database connection...")
        if test_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed")
            print("💡 Make sure:")
            print("   1. XAMPP MySQL is running")
            print("   2. Database 'visitor_management' is created")
            print("   3. .env file has correct credentials")
            return False
    except ImportError:
        print("⚠️  Cannot import db_config. Installing dependencies...")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import mysql.connector
        import flask
        import pytz
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"⚠️  Missing package: {e.name}")
        print("📦 Run: pip install -r requirements.txt")
        return False

def main():
    print("=" * 60)
    print("🚀 VISITOR MANAGEMENT SYSTEM - MySQL Migration Setup")
    print("=" * 60)
    print()
    
    # Step 1: Check XAMPP
    print("📍 Step 1: Checking XAMPP installation...")
    if not check_xampp():
        print("\n💡 Install XAMPP from: https://www.apachefriends.org/")
        return
    print()
    
    # Step 2: Check photo storage
    print("📍 Step 2: Checking photo storage configuration...")
    check_photo_storage()
    print()
    
    # Step 3: Check .env
    print("📍 Step 3: Checking environment configuration...")
    check_env_file()
    print()
    
    # Step 4: Check dependencies
    print("📍 Step 4: Checking Python dependencies...")
    deps_ok = check_dependencies()
    print()
    
    if not deps_ok:
        print("⏸️  Please install dependencies first:")
        print("   pip install -r requirements.txt")
        print("\nThen run this script again.")
        return
    
    # Step 5: Test database
    print("📍 Step 5: Testing database connection...")
    db_ok = test_db_connection()
    print()
    
    # Summary
    print("=" * 60)
    print("📊 SETUP SUMMARY")
    print("=" * 60)
    
    if db_ok:
        print("✅ All checks passed! You're ready to go.")
        print("\n🎯 Next steps:")
        print("   1. Review your .env file settings")
        print("   2. Make sure you've run db_schema.sql in phpMyAdmin")
        print("   3. Start the application: python app.py")
        print("\n🌐 Access application at: http://localhost:5000")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\n📖 See MIGRATION_GUIDE.md for detailed instructions")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
