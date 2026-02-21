#!/usr/bin/env python3
"""
MongoDB to MySQL Migration Script
Converts JSON exported data from MongoDB to MySQL database
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import pymysql
from pymysql.cursors import DictCursor
import bson
from config import MYSQL_CONFIG, DATA_DIR, SCHEMA_FILE, BATCH_SIZE, VERBOSE, DATA_FILES, MIGRATION_ORDER


class MongoToMySQLConverter:
    """Handles conversion of MongoDB JSON data to MySQL"""
    
    def __init__(self):
        self.connection = None
        self.stats = {
            'total_records': 0,
            'successful': 0,
            'failed': 0,
            'by_collection': {}
        }
        # Track successfully inserted IDs for foreign key validation
        self.inserted_user_ids = set()
        self.inserted_frame_ids = set()
        self.inserted_photo_ids = set()
    
    def connect(self):
        """Establish MySQL connection"""
        try:
            self.connection = pymysql.connect(**MYSQL_CONFIG)
            print(f"✓ Connected to MySQL database: {MYSQL_CONFIG['database']}")
            return True
        except pymysql.err.OperationalError as e:
            # Handle "Unknown database" error (1049)
            if e.args[0] == 1049:
                print(f"⚠ Database '{MYSQL_CONFIG['database']}' does not exist. Creating it...")
                try:
                    # Connect without specifying database
                    temp_config = MYSQL_CONFIG.copy()
                    db_name = temp_config.pop('database')
                    temp_connection = pymysql.connect(**temp_config)
                    cursor = temp_connection.cursor()
                    
                    # Create database
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    print(f"✓ Database '{db_name}' created successfully")
                    
                    cursor.close()
                    temp_connection.close()
                    
                    # Now connect to the newly created database
                    self.connection = pymysql.connect(**MYSQL_CONFIG)
                    print(f"✓ Connected to MySQL database: {MYSQL_CONFIG['database']}")
                    return True
                except Exception as create_error:
                    print(f"✗ Failed to create database: {create_error}")
                    return False
            else:
                print(f"✗ Failed to connect to MySQL: {e}")
                return False
        except Exception as e:
            print(f"✗ Failed to connect to MySQL: {e}")
            return False
    
    def close(self):
        """Close MySQL connection"""
        if self.connection:
            self.connection.close()
            print("✓ MySQL connection closed")
    
    def execute_schema(self):
        """Execute SQL schema file to create tables"""
        if not os.path.exists(SCHEMA_FILE):
            print(f"✗ Schema file not found: {SCHEMA_FILE}")
            return False
        
        try:
            with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            cursor = self.connection.cursor()
            
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            
            for statement in statements:
                if statement:
                    cursor.execute(statement)
            
            self.connection.commit()
            print(f"✓ Database schema created successfully ({len(statements)} statements)")
            return True
        except Exception as e:
            print(f"✗ Failed to execute schema: {e}")
            self.connection.rollback()
            return False
    
    def load_data_file(self, filename: str) -> List[Dict]:
        """Load data from JSON or BSON file"""
        filepath = os.path.join(DATA_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"⚠ File not found: {filepath}")
            return []
        
        try:
            # Check file extension to determine format
            if filename.endswith('.bson'):
                # Load BSON file (mongodump format - concatenated BSON documents)
                data = []
                with open(filepath, 'rb') as f:
                    raw_data = f.read()
                    
                    # Try to decode all documents at once using decode_all
                    try:
                        # Method 1: Use decode_all (pymongo 4.x)
                        from bson import decode_all
                        data = decode_all(raw_data)
                        print(f"✓ Loaded {len(data)} records from {filename}")
                        return data
                    except (ImportError, AttributeError):
                        # Method 2: Parse concatenated BSON documents manually
                        offset = 0
                        while offset < len(raw_data):
                            # Each BSON document starts with 4-byte size (little-endian)
                            if offset + 4 > len(raw_data):
                                break
                            doc_size = int.from_bytes(raw_data[offset:offset+4], 'little')
                            if offset + doc_size > len(raw_data):
                                break
                            # Decode single BSON document
                            doc_bytes = raw_data[offset:offset+doc_size]
                            try:
                                # Try different decode methods
                                if hasattr(bson, 'BSON'):
                                    doc = bson.BSON(doc_bytes).decode()
                                elif hasattr(bson, 'decode'):
                                    doc = bson.decode(doc_bytes)
                                else:
                                    # Use codec directly
                                    from bson.codec_options import CodecOptions
                                    import bson as bson_module
                                    codec_opts = CodecOptions()
                                    doc = bson_module._bson_to_dict(doc_bytes, codec_opts)[0]
                                data.append(doc)
                            except Exception as e:
                                if VERBOSE:
                                    print(f"  ⚠ Failed to decode BSON document at offset {offset}: {e}")
                            offset += doc_size
                        print(f"✓ Loaded {len(data)} records from {filename}")
                        return data
            else:
                # Load JSON file
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✓ Loaded {len(data)} records from {filename}")
                    return data
        except Exception as e:
            print(f"✗ Failed to load {filename}: {e}")
            return []
    
    @staticmethod
    def convert_mongo_id(mongo_id: Any) -> Optional[str]:
        """Convert MongoDB ObjectId to string"""
        if mongo_id is None:
            return None
        if isinstance(mongo_id, dict) and '$oid' in mongo_id:
            return mongo_id['$oid']
        return str(mongo_id)
    
    @staticmethod
    def convert_boolean(value: Any) -> bool:
        """Convert various boolean representations to Python bool"""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        return bool(value)
    
    @staticmethod
    def convert_date(date_value: Any) -> Optional[str]:
        """Convert MongoDB date to MySQL datetime format"""
        if date_value is None:
            return None
        
        if isinstance(date_value, dict) and '$date' in date_value:
            date_str = date_value['$date']
            if isinstance(date_str, str):
                # Parse ISO format
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    return None
            elif isinstance(date_str, int):
                # Unix timestamp in milliseconds
                dt = datetime.fromtimestamp(date_str / 1000.0)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
        
        if isinstance(date_value, str):
            try:
                dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                return date_value
        
        return date_value
    
    def migrate_users(self, data: List[Dict]) -> bool:
        """Migrate users collection"""
        if not data:
            return True
        
        cursor = self.connection.cursor()
        successful = 0
        failed = 0
        
        try:
            for record in data:
                try:
                    user_data = {
                        'id': self.convert_mongo_id(record.get('_id')),
                        'image_profile': record.get('image_profile'),
                        'custom_profile_image': record.get('custom_profile_image'),
                        'use_google_profile': self.convert_boolean(record.get('use_google_profile', True)),
                        'name': record.get('name'),
                        'username': record.get('username'),
                        'email': record.get('email'),
                        'password': record.get('password'),
                        'role': record.get('role', 'basic'),
                        'bio': record.get('bio', ''),
                        'birthdate': self.convert_date(record.get('birthdate')),
                        'birthdate_changed': self.convert_boolean(record.get('birthdate_changed', False)),
                        'birthdate_changed_at': self.convert_date(record.get('birthdate_changed_at')),
                        'last_birthday_notification': self.convert_date(record.get('last_birthday_notification')),
                        'ban_status': self.convert_boolean(record.get('ban_status', False)),
                        'ban_release_datetime': self.convert_date(record.get('ban_release_datetime')),
                        'google_id': record.get('google_id'),
                        'email_verified': self.convert_boolean(record.get('email_verified', False)),
                        'email_verification_token': record.get('email_verification_token'),
                        'email_verification_expires': self.convert_date(record.get('email_verification_expires')),
                        'email_verified_at': self.convert_date(record.get('email_verified_at')),
                        'created_at': self.convert_date(record.get('created_at')),
                        'updated_at': self.convert_date(record.get('updated_at')),
                    }
                    
                    placeholders = ', '.join(['%s'] * len(user_data))
                    columns = ', '.join(f'`{k}`' for k in user_data.keys())
                    sql = f"INSERT INTO users ({columns}) VALUES ({placeholders})"
                    
                    cursor.execute(sql, list(user_data.values()))
                    self.inserted_user_ids.add(user_data['id'])  # Track inserted user ID
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    if VERBOSE:
                        print(f"  ✗ Failed to insert user {record.get('username')}: {e}")
            
            self.connection.commit()
            print(f"✓ Users: {successful} successful, {failed} failed")
            return True
            
        except Exception as e:
            print(f"✗ Users migration failed: {e}")
            self.connection.rollback()
            return False
    
    def migrate_maintenances(self, data: List[Dict]) -> bool:
        """Migrate maintenances collection"""
        if not data:
            return True
        
        cursor = self.connection.cursor()
        successful = 0
        failed = 0
        
        try:
            for record in data:
                try:
                    maintenance_data = {
                        'id': self.convert_mongo_id(record.get('_id')),
                        'is_active': self.convert_boolean(record.get('isActive', False)),
                        'estimated_end_time': self.convert_date(record.get('estimatedEndTime')),
                        'message': record.get('message'),
                        'updated_by': self.convert_mongo_id(record.get('updatedBy')),
                        'created_at': self.convert_date(record.get('createdAt')),
                        'updated_at': self.convert_date(record.get('updatedAt')),
                    }
                    
                    placeholders = ', '.join(['%s'] * len(maintenance_data))
                    columns = ', '.join(f'`{k}`' for k in maintenance_data.keys())
                    sql = f"INSERT INTO maintenances ({columns}) VALUES ({placeholders})"
                    
                    cursor.execute(sql, list(maintenance_data.values()))
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    if VERBOSE:
                        print(f"  ✗ Failed to insert maintenance: {e}")
            
            self.connection.commit()
            print(f"✓ Maintenances: {successful} successful, {failed} failed")
            return True
            
        except Exception as e:
            print(f"✗ Maintenances migration failed: {e}")
            self.connection.rollback()
            return False
    
    def migrate_follows(self, data: List[Dict]) -> bool:
        """Migrate follows collection"""
        if not data:
            return True
        
        cursor = self.connection.cursor()
        successful = 0
        failed = 0
        
        try:
            for record in data:
                try:
                    follower_id = self.convert_mongo_id(record.get('follower_id'))
                    following_id = self.convert_mongo_id(record.get('following_id'))
                    
                    # Validate foreign keys
                    if follower_id not in self.inserted_user_ids:
                        failed += 1
                        if VERBOSE:
                            print(f"  ✗ Skipped follow: follower_id {follower_id} not found")
                        continue
                    
                    if following_id not in self.inserted_user_ids:
                        failed += 1
                        if VERBOSE:
                            print(f"  ✗ Skipped follow: following_id {following_id} not found")
                        continue
                    
                    follow_data = {
                        'id': self.convert_mongo_id(record.get('_id')),
                        'follower_id': follower_id,
                        'following_id': following_id,
                        'status': record.get('status', 'active'),
                        'created_at': self.convert_date(record.get('created_at')),
                        'updated_at': self.convert_date(record.get('updated_at')),
                    }
                    
                    placeholders = ', '.join(['%s'] * len(follow_data))
                    columns = ', '.join(f'`{k}`' for k in follow_data.keys())
                    sql = f"INSERT INTO follows ({columns}) VALUES ({placeholders})"
                    
                    cursor.execute(sql, list(follow_data.values()))
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    if VERBOSE:
                        print(f"  ✗ Failed to insert follow: {e}")
            
            self.connection.commit()
            print(f"✓ Follows: {successful} successful, {failed} failed")
            return True
            
        except Exception as e:
            print(f"✗ Follows migration failed: {e}")
            self.connection.rollback()
            return False
    
    def migrate_frames(self, data: List[Dict]) -> bool:
        """Migrate frames collection"""
        if not data:
            return True
        
        cursor = self.connection.cursor()
        successful = 0
        failed = 0
        
        try:
            for record in data:
                try:
                    frame_id = self.convert_mongo_id(record.get('_id'))
                    user_id = self.convert_mongo_id(record.get('user_id'))
                    
                    # Validate user_id foreign key
                    if user_id not in self.inserted_user_ids:
                        failed += 1
                        if VERBOSE:
                            print(f"  ✗ Skipped frame {record.get('title')}: user_id {user_id} not found")
                        continue
                    
                    # Validate approved_by foreign key (optional)
                    approved_by = self.convert_mongo_id(record.get('approved_by'))
                    if approved_by and approved_by not in self.inserted_user_ids:
                        approved_by = None  # Set to NULL if user doesn't exist
                    
                    # Insert main frame record
                    frame_data = {
                        'id': frame_id,
                        'title': record.get('title'),
                        'desc': record.get('desc', ''),
                        'thumbnail': record.get('thumbnail'),
                        'layout_type': record.get('layout_type'),
                        'official_status': self.convert_boolean(record.get('official_status', False)),
                        'visibility': record.get('visibility', 'private'),
                        'approval_status': record.get('approval_status', 'pending'),
                        'approved_by': approved_by,
                        'approved_at': self.convert_date(record.get('approved_at')),
                        'rejection_reason': record.get('rejection_reason'),
                        'user_id': user_id,
                        'created_at': self.convert_date(record.get('created_at')),
                        'updated_at': self.convert_date(record.get('updated_at')),
                    }
                    
                    placeholders = ', '.join(['%s'] * len(frame_data))
                    columns = ', '.join(f'`{k}`' for k in frame_data.keys())
                    sql = f"INSERT INTO frames ({columns}) VALUES ({placeholders})"
                    cursor.execute(sql, list(frame_data.values()))
                    self.inserted_frame_ids.add(frame_id)  # Track inserted frame ID
                    
                    # Insert frame images
                    images = record.get('images', [])
                    for idx, image_url in enumerate(images):
                        cursor.execute(
                            "INSERT INTO frame_images (frame_id, image_url, order_index) VALUES (%s, %s, %s)",
                            (frame_id, image_url, idx)
                        )
                    
                    # Insert frame tags
                    tags = record.get('tag_label', [])
                    for tag in tags:
                        cursor.execute(
                            "INSERT INTO frame_tags (frame_id, tag) VALUES (%s, %s)",
                            (frame_id, tag)
                        )
                    
                    # Insert frame likes (only if user exists)
                    likes = record.get('like_count', [])
                    for like in likes:
                        like_user_id = self.convert_mongo_id(like.get('user_id'))
                        if like_user_id in self.inserted_user_ids:
                            cursor.execute(
                                "INSERT INTO frame_likes (frame_id, user_id, created_at) VALUES (%s, %s, %s)",
                                (frame_id, like_user_id, 
                             self.convert_date(like.get('created_at')))
                        )
                    
                    # Insert frame uses (only if user exists)
                    uses = record.get('use_count', [])
                    for use in uses:
                        use_user_id = self.convert_mongo_id(use.get('user_id'))
                        if use_user_id in self.inserted_user_ids:
                            cursor.execute(
                                "INSERT INTO frame_uses (frame_id, user_id, created_at) VALUES (%s, %s, %s)",
                                (frame_id, use_user_id, 
                                 self.convert_date(use.get('created_at')))
                            )
                    
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    if VERBOSE:
                        print(f"  ✗ Failed to insert frame {record.get('title')}: {e}")
            
            self.connection.commit()
            print(f"✓ Frames: {successful} successful, {failed} failed")
            return True
            
        except Exception as e:
            print(f"✗ Frames migration failed: {e}")
            self.connection.rollback()
            return False
    
    def migrate_tickets(self, data: List[Dict]) -> bool:
        """Migrate tickets collection"""
        if not data:
            return True
        
        cursor = self.connection.cursor()
        successful = 0
        failed = 0
        
        try:
            for record in data:
                try:
                    ticket_id = self.convert_mongo_id(record.get('_id'))
                    user_id = self.convert_mongo_id(record.get('user_id'))
                    admin_id = self.convert_mongo_id(record.get('admin_id'))
                    
                    # Validate admin_id foreign key (optional)
                    if admin_id and admin_id not in self.inserted_user_ids:
                        admin_id = None  # Set to NULL if admin doesn't exist
                    
                    ticket_data = {
                        'id': ticket_id,
                        'title': record.get('title'),
                        'description': record.get('description'),
                        'user_id': user_id,
                        'type': record.get('type'),
                        'status': record.get('status', 'pending'),
                        'admin_response': record.get('admin_response'),
                        'admin_id': admin_id,
                        'priority': record.get('priority', 'medium'),
                        'created_at': self.convert_date(record.get('created_at')),
                        'updated_at': self.convert_date(record.get('updated_at')),
                    }
                    
                    placeholders = ', '.join(['%s'] * len(ticket_data))
                    columns = ', '.join(f'`{k}`' for k in ticket_data.keys())
                    sql = f"INSERT INTO tickets ({columns}) VALUES ({placeholders})"
                    cursor.execute(sql, list(ticket_data.values()))
                    
                    # Insert ticket images
                    images = record.get('images', [])
                    for idx, image_url in enumerate(images):
                        cursor.execute(
                            "INSERT INTO ticket_images (ticket_id, image_url, order_index) VALUES (%s, %s, %s)",
                            (ticket_id, image_url, idx)
                        )
                    
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    if VERBOSE:
                        print(f"  ✗ Failed to insert ticket: {e}")
            
            self.connection.commit()
            print(f"✓ Tickets: {successful} successful, {failed} failed")
            return True
            
        except Exception as e:
            print(f"✗ Tickets migration failed: {e}")
            self.connection.rollback()
            return False
    
    def migrate_reports(self, data: List[Dict]) -> bool:
        """Migrate reports collection"""
        if not data:
            return True
        
        cursor = self.connection.cursor()
        successful = 0
        failed = 0
        
        try:
            for record in data:
                try:
                    frame_id = self.convert_mongo_id(record.get('frame_id'))
                    user_id = self.convert_mongo_id(record.get('user_id'))
                    
                    # Validate foreign keys
                    if frame_id not in self.inserted_frame_ids:
                        failed += 1
                        if VERBOSE:
                            print(f"  ✗ Skipped report: frame_id {frame_id} not found")
                        continue
                    
                    if user_id not in self.inserted_user_ids:
                        failed += 1
                        if VERBOSE:
                            print(f"  ✗ Skipped report: user_id {user_id} not found")
                        continue
                    
                    # Validate admin_id foreign key (optional)
                    admin_id = self.convert_mongo_id(record.get('admin_id'))
                    if admin_id and admin_id not in self.inserted_user_ids:
                        admin_id = None
                    
                    report_data = {
                        'id': self.convert_mongo_id(record.get('_id')),
                        'title': record.get('title'),
                        'description': record.get('description'),
                        'frame_id': frame_id,
                        'user_id': user_id,
                        'report_status': record.get('report_status', 'pending'),
                        'admin_response': record.get('admin_response'),
                        'admin_id': admin_id,
                        'created_at': self.convert_date(record.get('created_at')),
                        'updated_at': self.convert_date(record.get('updated_at')),
                    }
                    
                    placeholders = ', '.join(['%s'] * len(report_data))
                    columns = ', '.join(f'`{k}`' for k in report_data.keys())
                    sql = f"INSERT INTO reports ({columns}) VALUES ({placeholders})"
                    
                    cursor.execute(sql, list(report_data.values()))
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    if VERBOSE:
                        print(f"  ✗ Failed to insert report: {e}")
            
            self.connection.commit()
            print(f"✓ Reports: {successful} successful, {failed} failed")
            return True
            
        except Exception as e:
            print(f"✗ Reports migration failed: {e}")
            self.connection.rollback()
            return False
    
    def migrate_photos(self, data: List[Dict]) -> bool:
        """Migrate photos collection"""
        if not data:
            return True
        
        cursor = self.connection.cursor()
        successful = 0
        failed = 0
        
        try:
            for record in data:
                try:
                    photo_id = self.convert_mongo_id(record.get('_id'))
                    frame_id = self.convert_mongo_id(record.get('frame_id'))
                    user_id = self.convert_mongo_id(record.get('user_id'))
                    
                    # Validate foreign keys
                    if frame_id not in self.inserted_frame_ids:
                        failed += 1
                        if VERBOSE:
                            print(f"  ✗ Skipped photo: frame_id {frame_id} not found")
                        continue
                    
                    if user_id not in self.inserted_user_ids:
                        failed += 1
                        if VERBOSE:
                            print(f"  ✗ Skipped photo: user_id {user_id} not found")
                        continue
                    
                    photo_data = {
                        'id': photo_id,
                        'title': record.get('title'),
                        'desc': record.get('desc', ''),
                        'frame_id': frame_id,
                        'user_id': user_id,
                        'expires_at': self.convert_date(record.get('expires_at')),
                        'live_photo': self.convert_boolean(record.get('livePhoto', False)),
                        'ai_photo': self.convert_boolean(record.get('aiPhoto', False)),
                        'created_at': self.convert_date(record.get('created_at')),
                        'updated_at': self.convert_date(record.get('updated_at')),
                    }
                    
                    placeholders = ', '.join(['%s'] * len(photo_data))
                    columns = ', '.join(f'`{k}`' for k in photo_data.keys())
                    sql = f"INSERT INTO photos ({columns}) VALUES ({placeholders})"
                    cursor.execute(sql, list(photo_data.values()))
                    self.inserted_photo_ids.add(photo_id)  # Track inserted photo ID
                    
                    # Insert photo images
                    images = record.get('images', [])
                    for idx, image_url in enumerate(images):
                        cursor.execute(
                            "INSERT INTO photo_images (photo_id, image_url, order_index) VALUES (%s, %s, %s)",
                            (photo_id, image_url, idx)
                        )
                    
                    # Insert video files
                    videos = record.get('video_files', [])
                    for idx, video_url in enumerate(videos):
                        cursor.execute(
                            "INSERT INTO photo_videos (photo_id, video_url, order_index) VALUES (%s, %s, %s)",
                            (photo_id, video_url, idx)
                        )
                    
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    if VERBOSE:
                        print(f"  ✗ Failed to insert photo: {e}")
            
            self.connection.commit()
            print(f"✓ Photos: {successful} successful, {failed} failed")
            return True
            
        except Exception as e:
            print(f"✗ Photos migration failed: {e}")
            self.connection.rollback()
            return False
    
    def migrate_photoposts(self, data: List[Dict]) -> bool:
        """Migrate photo posts collection"""
        if not data:
            return True
        
        cursor = self.connection.cursor()
        successful = 0
        failed = 0
        
        try:
            for record in data:
                try:
                    photopost_id = self.convert_mongo_id(record.get('_id'))
                    photo_id = self.convert_mongo_id(record.get('photo_id'))
                    user_id = self.convert_mongo_id(record.get('user_id'))
                    
                    # Validate user_id foreign key
                    if user_id not in self.inserted_user_ids:
                        failed += 1
                        if VERBOSE:
                            print(f"  ✗ Skipped photopost: user_id {user_id} not found")
                        continue
                    
                    # photo_id is optional and can be NULL
                    if photo_id and photo_id not in self.inserted_photo_ids:
                        photo_id = None  # Set to NULL if referenced photo doesn't exist
                    
                    photopost_data = {
                        'id': photopost_id,
                        'title': record.get('title'),
                        'desc': record.get('desc', ''),
                        'photo_id': photo_id,
                        'user_id': user_id,
                        'visibility': record.get('visibility', 'public'),
                        'post_type': record.get('post_type', 'normal'),
                        'view_count': record.get('view_count', 0),
                        'created_at': self.convert_date(record.get('created_at')),
                        'updated_at': self.convert_date(record.get('updated_at')),
                    }
                    
                    placeholders = ', '.join(['%s'] * len(photopost_data))
                    columns = ', '.join(f'`{k}`' for k in photopost_data.keys())
                    sql = f"INSERT INTO photoposts ({columns}) VALUES ({placeholders})"
                    cursor.execute(sql, list(photopost_data.values()))
                    
                    # Insert photo post images
                    images = record.get('images', [])
                    for idx, image_url in enumerate(images):
                        cursor.execute(
                            "INSERT INTO photopost_images (photopost_id, image_url, order_index) VALUES (%s, %s, %s)",
                            (photopost_id, image_url, idx)
                        )
                    
                    # Insert photo post likes (only if user exists)
                    likes = record.get('likes', [])
                    for like in likes:
                        like_user_id = self.convert_mongo_id(like.get('user_id') if isinstance(like, dict) else like)
                        if like_user_id and like_user_id in self.inserted_user_ids:
                            like_created = self.convert_date(like.get('created_at')) if isinstance(like, dict) else None
                            cursor.execute(
                                "INSERT INTO photopost_likes (photopost_id, user_id, created_at) VALUES (%s, %s, %s)",
                                (photopost_id, like_user_id, like_created)
                            )
                    
                    # Insert photo post comments (only if user exists)
                    comments = record.get('comments', [])
                    for comment in comments:
                        comment_user_id = self.convert_mongo_id(comment.get('user_id'))
                        if comment_user_id and comment_user_id in self.inserted_user_ids:
                            comment_id = self.convert_mongo_id(comment.get('_id'))
                            cursor.execute(
                                """INSERT INTO photopost_comments 
                                (id, photopost_id, user_id, comment, created_at, updated_at) 
                                VALUES (%s, %s, %s, %s, %s, %s)""",
                                (
                                    comment_id,
                                    photopost_id,
                                    comment_user_id,
                                    comment.get('comment', ''),
                                    self.convert_date(comment.get('created_at')),
                                    self.convert_date(comment.get('updated_at'))
                                )
                            )
                    
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    if VERBOSE:
                        print(f"  ✗ Failed to insert photopost: {e}")
            
            self.connection.commit()
            print(f"✓ Photo Posts: {successful} successful, {failed} failed")
            return True
            
        except Exception as e:
            print(f"✗ Photo Posts migration failed: {e}")
            self.connection.rollback()
            return False
    
    def migrate_photocollabs(self, data: List[Dict]) -> bool:
        """Migrate photo collabs collection"""
        if not data:
            return True
        
        cursor = self.connection.cursor()
        successful = 0
        failed = 0
        
        try:
            for record in data:
                try:
                    collab_id = self.convert_mongo_id(record.get('_id'))
                    
                    inviter = record.get('inviter', {})
                    receiver = record.get('receiver', {})
                    invitation = record.get('invitation', {})
                    
                    collab_data = {
                        'id': collab_id,
                        'title': record.get('title'),
                        'desc': record.get('desc', ''),
                        'frame_id': self.convert_mongo_id(record.get('frame_id')),
                        'layout_type': record.get('layout_type'),
                        'inviter_user_id': self.convert_mongo_id(inviter.get('user_id')),
                        'inviter_photo_id': self.convert_mongo_id(inviter.get('photo_id')),
                        'receiver_user_id': self.convert_mongo_id(receiver.get('user_id')),
                        'receiver_photo_id': self.convert_mongo_id(receiver.get('photo_id')),
                        'status': record.get('status', 'pending'),
                        'invitation_message': invitation.get('message', ''),
                        'invitation_sent_at': self.convert_date(invitation.get('sent_at')),
                        'invitation_responded_at': self.convert_date(invitation.get('responded_at')),
                        'expires_at': self.convert_date(record.get('expires_at')),
                        'completed_at': self.convert_date(record.get('completed_at')),
                        'created_at': self.convert_date(record.get('created_at')),
                        'updated_at': self.convert_date(record.get('updated_at')),
                    }
                    
                    placeholders = ', '.join(['%s'] * len(collab_data))
                    columns = ', '.join(f'`{k}`' for k in collab_data.keys())
                    sql = f"INSERT INTO photo_collabs ({columns}) VALUES ({placeholders})"
                    cursor.execute(sql, list(collab_data.values()))
                    
                    # Insert merged images
                    merged_images = record.get('merged_images', [])
                    for idx, image_url in enumerate(merged_images):
                        cursor.execute(
                            "INSERT INTO photo_collab_images (photo_collab_id, image_url, order_index) VALUES (%s, %s, %s)",
                            (collab_id, image_url, idx)
                        )
                    
                    # Insert stickers
                    stickers = record.get('stickers', [])
                    for sticker in stickers:
                        position = sticker.get('position', {})
                        size = sticker.get('size', {})
                        
                        cursor.execute(
                            """INSERT INTO photo_collab_stickers 
                            (id, photo_collab_id, type, content, position_x, position_y, 
                             size_width, size_height, rotation, added_by, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (
                                sticker.get('id'),
                                collab_id,
                                sticker.get('type'),
                                sticker.get('content'),
                                position.get('x', 0),
                                position.get('y', 0),
                                size.get('width', 0),
                                size.get('height', 0),
                                sticker.get('rotation', 0),
                                self.convert_mongo_id(sticker.get('added_by')),
                                self.convert_date(sticker.get('created_at'))
                            )
                        )
                    
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    if VERBOSE:
                        print(f"  ✗ Failed to insert photo collab: {e}")
            
            self.connection.commit()
            print(f"✓ Photo Collabs: {successful} successful, {failed} failed")
            return True
            
        except Exception as e:
            print(f"✗ Photo Collabs migration failed: {e}")
            self.connection.rollback()
            return False
    
    def migrate_aiphotobooth_usages(self, data: List[Dict]) -> bool:
        """Migrate AI photobooth usages collection"""
        if not data:
            return True
        
        cursor = self.connection.cursor()
        successful = 0
        failed = 0
        
        try:
            for record in data:
                try:
                    user_id = self.convert_mongo_id(record.get('user_id'))
                    
                    # Validate foreign key
                    if user_id not in self.inserted_user_ids:
                        failed += 1
                        if VERBOSE:
                            print(f"  ✗ Skipped AI usage: user_id {user_id} not found")
                        continue
                    
                    usage_data = {
                        'id': self.convert_mongo_id(record.get('_id')),
                        'user_id': user_id,
                        'username': record.get('username'),
                        'count': record.get('count', 0),
                        'month': record.get('month'),
                        'year': record.get('year'),
                        'last_used_at': self.convert_date(record.get('last_used_at')),
                        'created_at': self.convert_date(record.get('created_at')),
                        'updated_at': self.convert_date(record.get('updated_at')),
                    }
                    
                    placeholders = ', '.join(['%s'] * len(usage_data))
                    columns = ', '.join(f'`{k}`' for k in usage_data.keys())
                    sql = f"INSERT INTO aiphotobooth_usages ({columns}) VALUES ({placeholders})"
                    
                    cursor.execute(sql, list(usage_data.values()))
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    if VERBOSE:
                        print(f"  ✗ Failed to insert AI usage: {e}")
            
            self.connection.commit()
            print(f"✓ AI Photobooth Usages: {successful} successful, {failed} failed")
            return True
            
        except Exception as e:
            print(f"✗ AI Photobooth Usages migration failed: {e}")
            self.connection.rollback()
            return False
    
    def migrate_broadcasts(self, data: List[Dict]) -> bool:
        """Migrate broadcasts collection"""
        if not data:
            return True
        
        cursor = self.connection.cursor()
        successful = 0
        failed = 0
        
        try:
            for record in data:
                try:
                    broadcast_id = self.convert_mongo_id(record.get('_id'))
                    settings = record.get('settings', {})
                    metadata = record.get('metadata', {})
                    maintenance_window = metadata.get('maintenance_window', {})
                    delivery_stats = record.get('delivery_stats', {})
                    
                    broadcast_data = {
                        'id': broadcast_id,
                        'title': record.get('title'),
                        'message': record.get('message'),
                        'type': record.get('type', 'general'),
                        'priority': record.get('priority', 'medium'),
                        'target_audience': record.get('target_audience', 'all'),
                        'status': record.get('status', 'draft'),
                        'scheduled_at': self.convert_date(record.get('scheduled_at')),
                        'sent_at': self.convert_date(record.get('sent_at')),
                        'expires_at': self.convert_date(record.get('expires_at')),
                        'created_by': self.convert_mongo_id(record.get('created_by')),
                        'sent_by': self.convert_mongo_id(record.get('sent_by')),
                        'total_recipients': record.get('total_recipients', 0),
                        'notifications_created': record.get('notifications_created', 0),
                        'delivery_online': delivery_stats.get('online_delivery', 0),
                        'delivery_offline': delivery_stats.get('offline_delivery', 0),
                        'delivery_failed': delivery_stats.get('failed_delivery', 0),
                        'send_to_new_users': self.convert_boolean(settings.get('send_to_new_users', False)),
                        'persistent': self.convert_boolean(settings.get('persistent', True)),
                        'dismissible': self.convert_boolean(settings.get('dismissible', True)),
                        'action_url': settings.get('action_url'),
                        'icon': settings.get('icon'),
                        'color': settings.get('color'),
                        'metadata_version': metadata.get('version'),
                        'metadata_feature': metadata.get('feature_announcement'),
                        'metadata_maintenance_start': self.convert_date(maintenance_window.get('start')),
                        'metadata_maintenance_end': self.convert_date(maintenance_window.get('end')),
                        'created_at': self.convert_date(record.get('created_at')),
                        'updated_at': self.convert_date(record.get('updated_at')),
                    }
                    
                    placeholders = ', '.join(['%s'] * len(broadcast_data))
                    columns = ', '.join(f'`{k}`' for k in broadcast_data.keys())
                    sql = f"INSERT INTO broadcasts ({columns}) VALUES ({placeholders})"
                    cursor.execute(sql, list(broadcast_data.values()))
                    
                    # Insert target roles
                    target_roles = record.get('target_roles', [])
                    for role in target_roles:
                        cursor.execute(
                            "INSERT INTO broadcast_target_roles (broadcast_id, role) VALUES (%s, %s)",
                            (broadcast_id, role)
                        )
                    
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    if VERBOSE:
                        print(f"  ✗ Failed to insert broadcast: {e}")
            
            self.connection.commit()
            print(f"✓ Broadcasts: {successful} successful, {failed} failed")
            return True
            
        except Exception as e:
            print(f"✗ Broadcasts migration failed: {e}")
            self.connection.rollback()
            return False
    
    def migrate_notifications(self, data: List[Dict]) -> bool:
        """Migrate notifications collection"""
        if not data:
            return True
        
        cursor = self.connection.cursor()
        successful = 0
        failed = 0
        
        try:
            for record in data:
                try:
                    recipient_id = self.convert_mongo_id(record.get('recipient_id'))
                    sender_id = self.convert_mongo_id(record.get('sender_id'))
                    
                    # Validate foreign keys
                    if recipient_id not in self.inserted_user_ids:
                        failed += 1
                        if VERBOSE:
                            print(f"  ✗ Skipped notification: recipient_id {recipient_id} not found")
                        continue
                    
                    if sender_id not in self.inserted_user_ids:
                        failed += 1
                        if VERBOSE:
                            print(f"  ✗ Skipped notification: sender_id {sender_id} not found")
                        continue
                    
                    notification_data_obj = record.get('data', {})
                    
                    notification_data = {
                        'id': self.convert_mongo_id(record.get('_id')),
                        'recipient_id': recipient_id,
                        'sender_id': sender_id,
                        'type': record.get('type'),
                        'title': record.get('title'),
                        'message': record.get('message'),
                        'is_read': self.convert_boolean(record.get('is_read', False)),
                        'read_at': self.convert_date(record.get('read_at')),
                        'is_dismissible': self.convert_boolean(record.get('is_dismissible', True)),
                        'expires_at': self.convert_date(record.get('expires_at')),
                        'data_frame_id': self.convert_mongo_id(notification_data_obj.get('frame_id')),
                        'data_frame_title': notification_data_obj.get('frame_title'),
                        'data_frame_thumbnail': notification_data_obj.get('frame_thumbnail'),
                        'data_follower_id': self.convert_mongo_id(notification_data_obj.get('follower_id')),
                        'data_follower_name': notification_data_obj.get('follower_name'),
                        'data_follower_username': notification_data_obj.get('follower_username'),
                        'data_follower_image': notification_data_obj.get('follower_image'),
                        'data_owner_id': self.convert_mongo_id(notification_data_obj.get('owner_id')),
                        'data_owner_name': notification_data_obj.get('owner_name'),
                        'data_owner_username': notification_data_obj.get('owner_username'),
                        'data_owner_image': notification_data_obj.get('owner_image'),
                        'data_birthday_user_id': self.convert_mongo_id(notification_data_obj.get('birthday_user_id')),
                        'data_birthday_user_name': notification_data_obj.get('birthday_user_name'),
                        'data_birthday_user_username': notification_data_obj.get('birthday_user_username'),
                        'data_birthday_user_age': notification_data_obj.get('birthday_user_age'),
                        'data_broadcast_id': self.convert_mongo_id(notification_data_obj.get('broadcast_id')),
                        'data_broadcast_type': notification_data_obj.get('broadcast_type'),
                        'data_broadcast_priority': notification_data_obj.get('broadcast_priority'),
                        'data_action_url': notification_data_obj.get('action_url'),
                        'data_custom_icon': notification_data_obj.get('custom_icon'),
                        'data_custom_color': notification_data_obj.get('custom_color'),
                        'data_additional_info': json.dumps(notification_data_obj.get('additional_info')) if notification_data_obj.get('additional_info') else None,
                        'created_at': self.convert_date(record.get('created_at')),
                        'updated_at': self.convert_date(record.get('updated_at')),
                    }
                    
                    placeholders = ', '.join(['%s'] * len(notification_data))
                    columns = ', '.join(f'`{k}`' for k in notification_data.keys())
                    sql = f"INSERT INTO notifications ({columns}) VALUES ({placeholders})"
                    
                    cursor.execute(sql, list(notification_data.values()))
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    if VERBOSE:
                        print(f"  ✗ Failed to insert notification: {e}")
            
            self.connection.commit()
            print(f"✓ Notifications: {successful} successful, {failed} failed")
            return True
            
        except Exception as e:
            print(f"✗ Notifications migration failed: {e}")
            self.connection.rollback()
            return False
    
    def run_migration(self):
        """Run the complete migration process"""
        print("\n" + "="*60)
        print("MongoDB to MySQL Migration Tool")
        print("="*60 + "\n")
        
        # Connect to MySQL
        if not self.connect():
            return False
        
        try:
            # Execute schema
            print("\n[Step 1] Creating database schema...")
            if not self.execute_schema():
                return False
            
            # Migrate each collection in order
            print("\n[Step 2] Migrating data...")
            
            migration_methods = {
                'users': self.migrate_users,
                'maintenances': self.migrate_maintenances,
                'follows': self.migrate_follows,
                'frames': self.migrate_frames,
                'tickets': self.migrate_tickets,
                'reports': self.migrate_reports,
                'photos': self.migrate_photos,
                'photoposts': self.migrate_photoposts,
                'photocollabs': self.migrate_photocollabs,
                'aiphotobooth_usages': self.migrate_aiphotobooth_usages,
                'broadcasts': self.migrate_broadcasts,
                'notifications': self.migrate_notifications,
            }
            
            for collection in MIGRATION_ORDER:
                print(f"\n--- Migrating {collection} ---")
                filename = DATA_FILES.get(collection)
                
                if not filename:
                    print(f"⚠ No file mapping found for {collection}, skipping...")
                    continue
                
                data = self.load_data_file(filename)
                
                if collection in migration_methods:
                    migration_methods[collection](data)
                else:
                    print(f"⚠ No migration method for {collection}, skipping...")
            
            print("\n" + "="*60)
            print("✓ Migration completed successfully!")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            return False
        finally:
            self.close()


def main():
    """Main entry point"""
    converter = MongoToMySQLConverter()
    success = converter.run_migration()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
