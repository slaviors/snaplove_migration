#!/usr/bin/env python3
"""
Test MySQL connection and verify setup
"""

import sys
import os

# Check if config.py exists
if not os.path.exists('config.py'):
    print("="*60)
    print("ERROR: config.py not found!")
    print("="*60)
    print("\nPlease create config.py from template:")
    print("  1. Copy config.example.py to config.py")
    print("  2. Edit config.py and update MySQL credentials")
    print("\nExample:")
    if sys.platform == 'win32':
        print("  copy config.example.py config.py")
        print("  notepad config.py")
    else:
        print("  cp config.example.py config.py")
        print("  nano config.py")
    print()
    sys.exit(1)

from config import MYSQL_CONFIG, DATA_DIR, DATA_FILES

def test_mysql_connection():
    """Test MySQL connection"""
    try:
        import pymysql
        print("✓ PyMySQL module found")
    except ImportError:
        print("✗ PyMySQL not installed. Run: pip install -r requirements.txt")
        return False
    
    try:
        connection = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password']
        )
        print(f"✓ MySQL connection successful")
        print(f"  Host: {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}")
        print(f"  User: {MYSQL_CONFIG['user']}")
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"  MySQL Version: {version[0]}")
        
        connection.close()
        return True
    except Exception as e:
        print(f"✗ MySQL connection failed: {e}")
        return False

def test_data_files():
    """Check if data files exist"""
    print("\nChecking data files...")
    
    if not os.path.exists(DATA_DIR):
        print(f"✗ Data directory not found: {DATA_DIR}")
        return False
    
    print(f"✓ Data directory found: {DATA_DIR}")
    
    found_files = 0
    missing_files = 0
    
    for collection, filename in DATA_FILES.items():
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  ✓ {filename} ({size:,} bytes)")
            found_files += 1
        else:
            print(f"  ✗ {filename} - NOT FOUND")
            missing_files += 1
    
    print(f"\nSummary: {found_files} files found, {missing_files} missing")
    
    return missing_files == 0

def main():
    print("="*60)
    print("Migration Setup Test")
    print("="*60)
    
    print("\n1. Testing Python dependencies...")
    
    print("\n2. Testing MySQL connection...")
    mysql_ok = test_mysql_connection()
    
    print("\n3. Checking data files...")
    files_ok = test_data_files()
    
    print("\n" + "="*60)
    if mysql_ok and files_ok:
        print("✓ All checks passed! Ready to run migration.")
        print("\nTo start migration, run:")
        print("  python converter.py")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        if not mysql_ok:
            print("\n  - Check MySQL connection settings in config.py")
        if not files_ok:
            print("\n  - Export MongoDB data to backup_data/ folder")
    print("="*60)

if __name__ == '__main__':
    main()
