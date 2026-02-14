"""
Configuration file for MongoDB to MySQL migration
Copy this file to config.py and update with your settings
"""

import os

# MySQL Configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_mysql_password_here',  # CHANGE THIS!
    'database': 'snaplove_db',
    'charset': 'utf8mb4',
    'use_unicode': True,
    'autocommit': False
}

# Path Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'backup_data')
SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

# Migration Settings
BATCH_SIZE = 1000  # Number of records to insert at once
VERBOSE = True  # Print detailed logs

# File mapping - MongoDB collection name to JSON file
DATA_FILES = {
    'users': 'test.users.json',
    'maintenances': 'test.maintenances.json',
    'follows': 'test.follows.json',
    'frames': 'test.frames.json',
    'tickets': 'test.tickets.json',
    'reports': 'test.reports.json',
    'photos': 'test.photos.json',
    'photocollabs': 'test.photocollabs.json',
    'aiphotobooth_usages': 'test.aiphotoboothusages.json',
    'broadcasts': 'test.broadcasts.json',
    'notifications': 'test.notifications.json',
}

# Migration order (important for foreign key constraints)
MIGRATION_ORDER = [
    'users',
    'maintenances',
    'follows',
    'frames',
    'tickets',
    'reports',
    'photos',
    'photocollabs',
    'aiphotobooth_usages',
    'broadcasts',
    'notifications',
]
