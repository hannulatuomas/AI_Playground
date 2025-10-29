"""
Database Manager

Manages SQLite database connections and operations.
"""

import sqlite3
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
import logging

from .models import Project, Rule, Memory, Log, Prompt, CodeSummary

logger = logging.getLogger(__name__)


class Database:
    """
    Database manager for UAIDE.
    
    Handles SQLite database operations including projects, rules,
    memory, logs, and code summaries.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or "data/uaide.db"
        self.connection: Optional[sqlite3.Connection] = None
        
    def connect(self) -> bool:
        """
        Connect to database.
        
        Returns:
            True if successful
        """
        try:
            db_file = Path(self.db_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return False
    
    def initialize(self) -> bool:
        """
        Initialize database schema.
        
        Returns:
            True if successful
        """
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            # Projects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    language TEXT,
                    framework TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Rules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    scope TEXT CHECK(scope IN ('global', 'project')),
                    category TEXT,
                    rule_text TEXT NOT NULL,
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            ''')
            
            # Memory table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT,
                    embedding BLOB,
                    context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level TEXT CHECK(level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
                    module TEXT,
                    action TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    feedback TEXT
                )
            ''')
            
            # Prompts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    category TEXT,
                    template TEXT NOT NULL,
                    variables TEXT,
                    version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Code summaries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS code_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    file_path TEXT NOT NULL,
                    summary TEXT,
                    classes TEXT,
                    functions TEXT,
                    imports TEXT,
                    embedding BLOB,
                    last_modified TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rules_project ON rules(project_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rules_scope ON rules(scope)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_key ON memory(key)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_module ON logs(module)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_prompts_name ON prompts(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_code_summaries_project ON code_summaries(project_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_code_summaries_path ON code_summaries(file_path)')
            
            self.connection.commit()
            logger.info("Database schema initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return False
    
    def execute(self, query: str, params: Optional[Tuple] = None) -> Optional[sqlite3.Cursor]:
        """
        Execute SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Cursor object or None
        """
        if not self.connection:
            logger.error("No database connection")
            return None
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return None
    
    def fetchone(self, query: str, params: Optional[Tuple] = None) -> Optional[sqlite3.Row]:
        """
        Execute query and fetch one result.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Single row or None
        """
        cursor = self.execute(query, params)
        return cursor.fetchone() if cursor else None
    
    def fetchall(self, query: str, params: Optional[Tuple] = None) -> List[sqlite3.Row]:
        """
        Execute query and fetch all results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of rows
        """
        cursor = self.execute(query, params)
        return cursor.fetchall() if cursor else []
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    # Project operations
    def add_project(self, project: Project) -> Optional[int]:
        """Add new project."""
        query = '''
            INSERT INTO projects (name, path, language, framework)
            VALUES (?, ?, ?, ?)
        '''
        cursor = self.execute(query, (project.name, project.path, project.language, project.framework))
        return cursor.lastrowid if cursor else None
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        row = self.fetchone('SELECT * FROM projects WHERE id = ?', (project_id,))
        if row:
            return Project(
                id=row['id'],
                name=row['name'],
                path=row['path'],
                language=row['language'],
                framework=row['framework'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
            )
        return None
    
    def get_project_by_path(self, path: str) -> Optional[Project]:
        """Get project by path."""
        row = self.fetchone('SELECT * FROM projects WHERE path = ?', (path,))
        if row:
            return Project(
                id=row['id'],
                name=row['name'],
                path=row['path'],
                language=row['language'],
                framework=row['framework']
            )
        return None
    
    def list_projects(self) -> List[Project]:
        """List all projects."""
        rows = self.fetchall('SELECT * FROM projects ORDER BY created_at DESC')
        return [Project(
            id=row['id'],
            name=row['name'],
            path=row['path'],
            language=row['language'],
            framework=row['framework']
        ) for row in rows]
    
    # Rule operations
    def add_rule(self, rule: Rule) -> Optional[int]:
        """Add new rule."""
        query = '''
            INSERT INTO rules (project_id, scope, category, rule_text, priority)
            VALUES (?, ?, ?, ?, ?)
        '''
        cursor = self.execute(query, (rule.project_id, rule.scope, rule.category, rule.rule_text, rule.priority))
        return cursor.lastrowid if cursor else None
    
    def get_rules(self, project_id: Optional[int] = None, scope: Optional[str] = None) -> List[Rule]:
        """Get rules by project and/or scope."""
        query = 'SELECT * FROM rules WHERE 1=1'
        params = []
        
        if project_id is not None:
            query += ' AND project_id = ?'
            params.append(project_id)
        
        if scope:
            query += ' AND scope = ?'
            params.append(scope)
        
        query += ' ORDER BY priority DESC, created_at'
        
        rows = self.fetchall(query, tuple(params) if params else None)
        return [Rule(
            id=row['id'],
            project_id=row['project_id'],
            scope=row['scope'],
            category=row['category'],
            rule_text=row['rule_text'],
            priority=row['priority']
        ) for row in rows]
    
    # Memory operations
    def add_memory(self, memory: Memory) -> Optional[int]:
        """Add new memory."""
        query = '''
            INSERT INTO memory (key, value, context, embedding)
            VALUES (?, ?, ?, ?)
        '''
        cursor = self.execute(query, (memory.key, memory.value, memory.context, memory.embedding))
        return cursor.lastrowid if cursor else None
    
    def get_memory(self, key: str) -> Optional[Memory]:
        """Get memory by key."""
        row = self.fetchone('SELECT * FROM memory WHERE key = ?', (key,))
        if row:
            # Update accessed_at
            self.execute('UPDATE memory SET accessed_at = CURRENT_TIMESTAMP WHERE key = ?', (key,))
            return Memory(
                id=row['id'],
                key=row['key'],
                value=row['value'],
                context=row['context'],
                embedding=row['embedding']
            )
        return None
    
    # Log operations
    def add_log(self, log: Log) -> Optional[int]:
        """Add new log entry."""
        query = '''
            INSERT INTO logs (level, module, action, success, error_message, feedback)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        cursor = self.execute(query, (log.level, log.module, log.action, log.success, log.error_message, log.feedback))
        return cursor.lastrowid if cursor else None
    
    def get_logs(self, module: Optional[str] = None, limit: int = 100) -> List[Log]:
        """Get recent logs."""
        query = 'SELECT * FROM logs'
        params = None
        
        if module:
            query += ' WHERE module = ?'
            params = (module,)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params = (params[0], limit) if params else (limit,)
        
        rows = self.fetchall(query, params)
        return [Log(
            id=row['id'],
            timestamp=datetime.fromisoformat(row['timestamp']) if row['timestamp'] else None,
            level=row['level'],
            module=row['module'],
            action=row['action'],
            success=row['success'],
            error_message=row['error_message'],
            feedback=row['feedback']
        ) for row in rows]
