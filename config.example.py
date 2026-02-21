"""
Configuration file for MongoDB to MySQL migration
Copy this file to config.py and update with your settings

Usage:
    1. Copy this file: cp config.example.py config.py (or copy on Windows)
    2. Edit config.py with your actual database credentials
    3. Run migration: python converter.py
"""

import os

# ============================================================
# MySQL Database Configuration
# ============================================================
# Update these settings with your MySQL database credentials

MYSQL_CONFIG = {
    'host': 'localhost',        # MySQL server hostname or IP address
    'port': 3306,               # MySQL server port (default: 3306)
    'user': 'root',             # MySQL username
    'password': 'your_password_here',  # MySQL password - CHANGE THIS!
    'database': 'snaplove_db',  # Target database name (will be created if not exists)
    'charset': 'utf8mb4',       # Character set (use utf8mb4 for emoji support)
    'use_unicode': True,        # Enable unicode support
    'autocommit': False         # Use transactions for data integrity
}

# ============================================================
# Path Configuration
# ============================================================
# Paths to data directory and schema file
# Usually no need to change these unless you have custom directory structure

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'backup_data')  # Directory containing BSON files
SCHEMA_FILE = os.path.join(BASE_DIR, 'schema.sql')  # SQL schema file

# ============================================================
# Migration Settings
# ============================================================

BATCH_SIZE = 1000  # Number of records to insert at once (adjust for performance)
VERBOSE = True     # Print detailed logs during migration (set to False for less output)

# ============================================================
# File Mapping
# ============================================================
# Maps MongoDB collection names to BSON files in the backup_data directory
# Update filenames if your BSON exports have different names

DATA_FILES = {
    'users': 'users.bson',
    'maintenances': 'maintenances.bson',
    'follows': 'follows.bson',
    'frames': 'frames.bson',
    'tickets': 'tickets.bson',
    'reports': 'reports.bson',
    'photos': 'photos.bson',
    'photocollabs': 'photocollabs.bson',
    'photoposts': 'photoposts.bson',
    'aiphotobooth_usages': 'aiphotoboothusages.bson',
    'broadcasts': 'broadcasts.bson',
    'notifications': 'notifications.bson',
}

# ============================================================
# Migration Order
# ============================================================
# Order matters! Tables with foreign key dependencies must be migrated
# after their parent tables. Do not change this order unless you know
# what you're doing.

MIGRATION_ORDER = [
    'users',                    # Must be first (parent table for many relationships)
    'maintenances',             # Independent table
    'follows',                  # Depends on users
    'frames',                   # Depends on users
    'tickets',                  # Depends on users
    'reports',                  # Depends on users and frames
    'photos',                   # Depends on users and frames
    'photoposts',               # Depends on users and photos
    'photocollabs',             # Depends on users and photos
    'aiphotobooth_usages',      # Depends on users
    'broadcasts',               # Depends on users
    'notifications',            # Depends on users (must be last)
]

# ============================================================
# Notes:
# ============================================================
# - Make sure MySQL server is running before starting migration
# - Ensure the database user has CREATE, INSERT, and ALTER privileges
# - Backup your data before running migration
# - The migration will drop existing tables and recreate them
# - Large datasets may take several minutes to migrate
