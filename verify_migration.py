#!/usr/bin/env python3
"""
Verify migration results
"""

import pymysql
from config import MYSQL_CONFIG

def verify_migration():
    """Check row counts in all tables"""
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        print("\n" + "="*60)
        print("MIGRATION VERIFICATION")
        print("="*60 + "\n")
        
        tables = [
            'users', 'maintenances', 'follows', 'frames', 'frame_images',
            'frame_tags', 'frame_likes', 'frame_uses', 'tickets', 'ticket_images',
            'reports', 'photos', 'photo_images', 'photo_videos', 'photoposts',
            'photopost_images', 'photopost_likes', 'photopost_comments',
            'photocollabs', 'photo_collab_images', 'photo_collab_stickers',
            'aiphotobooth_usages', 'broadcasts', 'broadcast_target_roles',
            'notifications'
        ]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            icon = "✓" if count > 0 else "○"
            print(f"{icon} {table:30s}: {count:6d} rows")
        
        print("\n" + "="*60)
        
        # Show some sample data
        print("\nSample Users:")
        cursor.execute("SELECT username, email, role FROM users LIMIT 5")
        for row in cursor.fetchall():
            print(f"  - {row[0]:20s} ({row[1]:30s}) [{row[2]}]")
        
        print("\nSample Frames:")
        cursor.execute("SELECT title, visibility, official_status FROM frames LIMIT 5")
        for row in cursor.fetchall():
            print(f"  - {row[0]:40s} [{row[1]}] Official: {row[2]}")
        
        print("\n" + "="*60)
        print("✓ Verification completed!")
        print("="*60 + "\n")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    verify_migration()
