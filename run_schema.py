"""
Execute SQL schema file against the database
This script reads the db_schema.sql file and executes it against the MySQL database
"""

import os
from db_config import get_db_connection
import mysql.connector

def execute_sql_file(sql_file_path):
    """Execute SQL file against the database"""
    
    # Read the SQL file
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        print(f"✅ Successfully read {sql_file_path}")
    except FileNotFoundError:
        print(f"❌ File not found: {sql_file_path}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Split SQL commands (simple split by semicolon)
    # Remove empty statements and comments-only statements
    statements = []
    for statement in sql_content.split(';'):
        statement = statement.strip()
        if statement and not statement.startswith('--') and statement != '\n':
            statements.append(statement)
    
    print(f"Found {len(statements)} SQL statements to execute")
    
    # Get database connection
    try:
        connection = get_db_connection()
        if not connection:
            print("❌ Failed to get database connection")
            return False
        
        cursor = connection.cursor()
        print("✅ Connected to database")
        
        # Execute each statement
        success_count = 0
        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                connection.commit()
                print(f"✅ Statement {i}: Success")
                success_count += 1
            except mysql.connector.Error as err:
                # Some errors are expected (like "database exists", "table exists")
                if "already exists" in str(err) or "Duplicate entry" in str(err):
                    print(f"⚠️  Statement {i}: {err} (This is normal)")
                    success_count += 1
                else:
                    print(f"❌ Statement {i}: {err}")
                    # Don't break, continue with other statements
        
        cursor.close()
        connection.close()
        
        print(f"\n📊 Execution Summary:")
        print(f"   Total statements: {len(statements)}")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {len(statements) - success_count}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    print("=" * 60)
    print("🗃️  DATABASE SCHEMA SETUP")
    print("=" * 60)
    
    schema_file = "db_schema.sql"
    
    if not os.path.exists(schema_file):
        print(f"❌ Schema file not found: {schema_file}")
        return
    
    print(f"📁 Executing SQL schema: {schema_file}")
    print()
    
    success = execute_sql_file(schema_file)
    
    if success:
        print("\n🎉 Schema setup completed!")
        print("💡 You can now run your application with: python app.py")
    else:
        print("\n❌ Schema setup failed!")
        print("💡 Check the error messages above")

if __name__ == "__main__":
    main()