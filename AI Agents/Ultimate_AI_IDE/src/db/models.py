"""
Database Models

Defines data models for database tables.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import json


@dataclass
class Project:
    """Project model."""
    name: str
    path: str
    language: Optional[str] = None
    framework: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'language': self.language,
            'framework': self.framework,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class Rule:
    """Rule model."""
    rule_text: str
    scope: str = 'project'  # 'global' or 'project'
    project_id: Optional[int] = None
    category: Optional[str] = None
    priority: int = 0
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'scope': self.scope,
            'category': self.category,
            'rule_text': self.rule_text,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class Memory:
    """Memory model."""
    key: str
    value: str
    context: Optional[str] = None
    embedding: Optional[bytes] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    accessed_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'context': self.context,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'accessed_at': self.accessed_at.isoformat() if self.accessed_at else None
        }


@dataclass
class Log:
    """Log model."""
    module: str
    action: str
    level: str = 'INFO'
    success: bool = True
    error_message: Optional[str] = None
    feedback: Optional[str] = None
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'level': self.level,
            'module': self.module,
            'action': self.action,
            'success': self.success,
            'error_message': self.error_message,
            'feedback': self.feedback
        }


@dataclass
class Prompt:
    """Prompt template model."""
    name: str
    template: str
    category: Optional[str] = None
    variables: Optional[List[str]] = field(default_factory=list)
    version: int = 1
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'template': self.template,
            'variables': json.dumps(self.variables) if self.variables else None,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class CodeSummary:
    """Code summary model for context management."""
    project_id: int
    file_path: str
    summary: Optional[str] = None
    classes: Optional[str] = None
    functions: Optional[str] = None
    imports: Optional[str] = None
    embedding: Optional[bytes] = None
    last_modified: Optional[datetime] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'file_path': self.file_path,
            'summary': self.summary,
            'classes': self.classes,
            'functions': self.functions,
            'imports': self.imports,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
