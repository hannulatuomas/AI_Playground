"""
Database Migration Script

Migrates existing learning.db to new schema with project_id and file_path columns.
Run this script before using v1.7.0 if you have existing data.

Usage:
    python scripts/migrate_db.py           # Migrate (preserve data)
    python scripts/migrate_db.py --reset   # Reset (fresh start)
"""

import sqlite3
from pathlib import Path
import shutil
from datetime import datetime
import os
import sys


# Change to project root directory
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)


def migrate_database(db_path: str = "data/db/learning.db"):
    """
    Migrate database to new schema.
    
    Args:
        db_path: Path to database file (relative to project root)
    """
    db_file = Path(db_path)
    
    if not db_file.exists():
        print(f"✓ No existing database found at {db_path}")
        print("  New database will be created automatically.")
        return
    
    print(f"Found existing database: {db_path}")
    
    # Create backup
    backup_path = db_file.parent / f"learning_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(db_file, backup_path)
    print(f"✓ Backup created: {backup_path}")
    
    # Connect to database
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(interactions)")
        columns = {row[1] for row in cursor.fetchall()}
        
        needs_migration = False
        
        # Check for project_id column
        if 'project_id' not in columns:
            print("Adding project_id column...")
            cursor.execute("ALTER TABLE interactions ADD COLUMN project_id TEXT")
            needs_migration = True
        else:
            print("✓ project_id column already exists")
        
        # Check for file_path column
        if 'file_path' not in columns:
            print("Adding file_path column...")
            cursor.execute("ALTER TABLE interactions ADD COLUMN file_path TEXT")
            needs_migration = True
        else:
            print("✓ file_path column already exists")
        
        if needs_migration:
            # Create index on project_id if it doesn't exist
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_project_id 
                    ON interactions(project_id)
                """)
                print("✓ Created index on project_id")
            except sqlite3.OperationalError:
                print("✓ Index on project_id already exists")
            
            conn.commit()
            print("✓ Migration completed successfully!")
        else:
            print("✓ Database already up to date!")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        print(f"  Restoring from backup...")
        conn.close()
        shutil.copy2(backup_path, db_file)
        print(f"✓ Database restored from backup")
        raise
    
    finally:
        conn.close()
    
    print("\n✓ Database is ready for v1.7.0!")


def reset_database(db_path: str = "data/db/learning.db"):
    """
    Delete existing database (it will be recreated with new schema).
    
    Args:
        db_path: Path to database file (relative to project root)
    """
    db_file = Path(db_path)
    
    if not db_file.exists():
        print(f"✓ No database to reset at {db_path}")
        return
    
    # Create backup before deleting
    backup_path = db_file.parent / f"learning_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(db_file, backup_path)
    print(f"✓ Backup created: {backup_path}")
    
    # Delete database
    db_file.unlink()
    print(f"✓ Deleted old database: {db_path}")
    print("  New database will be created automatically on next run.")


if __name__ == "__main__":
    print("=" * 60)
    print("  Database Migration Tool")
    print("  AI Coding Assistant v1.7.0")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        print("Mode: RESET (delete and recreate)")
        print()
        response = input("This will delete your learning history. Continue? (yes/no): ")
        if response.lower() == 'yes':
            reset_database()
        else:
            print("Cancelled.")
    else:
        print("Mode: MIGRATE (preserve existing data)")
        print()
        migrate_database()
    
    print()
    print("=" * 60)
