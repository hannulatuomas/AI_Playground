"""
Database Manager Module

Database schema generation, migrations, and optimization.
Phase 3 implementation.
"""

from .schema_generator import SchemaGenerator, DatabaseSchema, Table, Field, FieldType
from .migration_manager import MigrationManager, Migration
from .query_optimizer import QueryOptimizer, OptimizedQuery
from .debugger import DatabaseDebugger, DebugResult

__all__ = [
    'SchemaGenerator',
    'DatabaseSchema',
    'Table',
    'Field',
    'FieldType',
    'MigrationManager',
    'Migration',
    'QueryOptimizer',
    'OptimizedQuery',
    'DatabaseDebugger',
    'DebugResult'
]
