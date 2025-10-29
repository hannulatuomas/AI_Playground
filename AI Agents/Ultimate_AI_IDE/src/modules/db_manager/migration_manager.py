"""
Database Migration Manager

Manages database schema migrations.
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class Migration:
    """Database migration."""
    version: str
    name: str
    up_sql: str
    down_sql: str
    timestamp: str
    applied: bool = False


class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self, migrations_dir: str = "migrations"):
        """
        Initialize migration manager.
        
        Args:
            migrations_dir: Directory to store migrations
        """
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(exist_ok=True)
        self.migrations: List[Migration] = []
        self._load_migrations()
    
    def create_migration(self, name: str, up_sql: str, 
                        down_sql: str) -> Migration:
        """
        Create a new migration.
        
        Args:
            name: Migration name
            up_sql: SQL to apply migration
            down_sql: SQL to rollback migration
            
        Returns:
            Created Migration object
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        version = f"{timestamp}_{name}"
        
        migration = Migration(
            version=version,
            name=name,
            up_sql=up_sql,
            down_sql=down_sql,
            timestamp=timestamp
        )
        
        self._save_migration(migration)
        self.migrations.append(migration)
        
        return migration
    
    def apply_migration(self, migration: Migration, 
                       db_connection=None) -> bool:
        """
        Apply a migration.
        
        Args:
            migration: Migration to apply
            db_connection: Database connection
            
        Returns:
            True if successful
        """
        if migration.applied:
            print(f"Migration {migration.version} already applied")
            return True
        
        try:
            if db_connection:
                cursor = db_connection.cursor()
                cursor.execute(migration.up_sql)
                db_connection.commit()
            
            migration.applied = True
            self._update_migration_status(migration)
            
            print(f"Applied migration: {migration.version}")
            return True
            
        except Exception as e:
            print(f"Error applying migration {migration.version}: {e}")
            if db_connection:
                db_connection.rollback()
            return False
    
    def rollback_migration(self, migration: Migration, 
                          db_connection=None) -> bool:
        """
        Rollback a migration.
        
        Args:
            migration: Migration to rollback
            db_connection: Database connection
            
        Returns:
            True if successful
        """
        if not migration.applied:
            print(f"Migration {migration.version} not applied")
            return True
        
        try:
            if db_connection:
                cursor = db_connection.cursor()
                cursor.execute(migration.down_sql)
                db_connection.commit()
            
            migration.applied = False
            self._update_migration_status(migration)
            
            print(f"Rolled back migration: {migration.version}")
            return True
            
        except Exception as e:
            print(f"Error rolling back migration {migration.version}: {e}")
            if db_connection:
                db_connection.rollback()
            return False
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations."""
        return [m for m in self.migrations if not m.applied]
    
    def get_applied_migrations(self) -> List[Migration]:
        """Get list of applied migrations."""
        return [m for m in self.migrations if m.applied]
    
    def _save_migration(self, migration: Migration):
        """Save migration to file."""
        file_path = self.migrations_dir / f"{migration.version}.json"
        
        data = {
            'version': migration.version,
            'name': migration.name,
            'up_sql': migration.up_sql,
            'down_sql': migration.down_sql,
            'timestamp': migration.timestamp,
            'applied': migration.applied
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _load_migrations(self):
        """Load migrations from directory."""
        if not self.migrations_dir.exists():
            return
        
        for file_path in sorted(self.migrations_dir.glob("*.json")):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                migration = Migration(
                    version=data['version'],
                    name=data['name'],
                    up_sql=data['up_sql'],
                    down_sql=data['down_sql'],
                    timestamp=data['timestamp'],
                    applied=data.get('applied', False)
                )
                
                self.migrations.append(migration)
                
            except Exception as e:
                print(f"Error loading migration {file_path}: {e}")
    
    def _update_migration_status(self, migration: Migration):
        """Update migration status in file."""
        self._save_migration(migration)
    
    def generate_migration_from_schema_diff(self, old_schema: str, 
                                           new_schema: str) -> Optional[Migration]:
        """
        Generate migration from schema differences.
        
        Args:
            old_schema: Old schema SQL
            new_schema: New schema SQL
            
        Returns:
            Migration object or None
        """
        # Simple implementation: just use new schema as up, old as down
        # A more sophisticated version would parse and diff the schemas
        
        name = "schema_update"
        
        up_sql = f"-- Apply new schema\n{new_schema}"
        down_sql = f"-- Revert to old schema\n{old_schema}"
        
        return self.create_migration(name, up_sql, down_sql)
