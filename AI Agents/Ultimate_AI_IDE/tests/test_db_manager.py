"""
Tests for Database Manager Module
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.modules.db_manager import (
    SchemaGenerator, MigrationManager, QueryOptimizer,
    DatabaseDebugger, DatabaseSchema, Table, Field, FieldType
)


class MockAIBackend:
    """Mock AI backend for testing."""
    
    def query(self, prompt, max_tokens=1000):
        """Mock query method."""
        return "ISSUE: Syntax error\nSOLUTION: Fix syntax\nEXPLANATION: Error in query\nEXAMPLE: SELECT * FROM table"


@pytest.fixture
def mock_ai():
    """Provide mock AI backend."""
    return MockAIBackend()


@pytest.fixture
def temp_migrations_dir():
    """Create temporary migrations directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_schema_generator_basic(mock_ai):
    """Test basic schema generation."""
    generator = SchemaGenerator(mock_ai)
    
    models = [
        {
            'name': 'users',
            'fields': [
                {'name': 'id', 'type': 'integer', 'primary_key': True},
                {'name': 'name', 'type': 'string'},
                {'name': 'email', 'type': 'string', 'unique': True}
            ]
        }
    ]
    
    schema = generator.generate_schema(models, 'sqlite')
    
    assert schema.name == "generated_schema"
    assert len(schema.tables) == 1
    assert schema.db_type == 'sqlite'


def test_schema_generator_sql(mock_ai):
    """Test SQL generation."""
    generator = SchemaGenerator(mock_ai)
    
    schema = DatabaseSchema(
        name="test_db",
        tables=[
            Table(
                name="users",
                fields=[
                    Field(name="id", field_type=FieldType.INTEGER, primary_key=True),
                    Field(name="name", field_type=FieldType.STRING, nullable=False)
                ]
            )
        ],
        db_type="sqlite"
    )
    
    sql = generator.generate_sql(schema)
    
    assert "CREATE TABLE users" in sql
    assert "id" in sql
    assert "name" in sql


def test_schema_generator_postgresql(mock_ai):
    """Test PostgreSQL schema generation."""
    generator = SchemaGenerator(mock_ai)
    
    schema = DatabaseSchema(
        name="test_db",
        tables=[
            Table(
                name="products",
                fields=[
                    Field(name="id", field_type=FieldType.INTEGER, primary_key=True),
                    Field(name="price", field_type=FieldType.FLOAT)
                ]
            )
        ],
        db_type="postgresql"
    )
    
    sql = generator.generate_sql(schema)
    
    assert "CREATE TABLE products" in sql


def test_migration_manager_create(temp_migrations_dir):
    """Test migration creation."""
    manager = MigrationManager(temp_migrations_dir)
    
    migration = manager.create_migration(
        name="add_users_table",
        up_sql="CREATE TABLE users (id INTEGER PRIMARY KEY);",
        down_sql="DROP TABLE users;"
    )
    
    assert migration.name == "add_users_table"
    assert not migration.applied
    assert len(manager.migrations) == 1


def test_migration_manager_pending(temp_migrations_dir):
    """Test getting pending migrations."""
    manager = MigrationManager(temp_migrations_dir)
    
    manager.create_migration(
        name="migration1",
        up_sql="CREATE TABLE test1 (id INTEGER);",
        down_sql="DROP TABLE test1;"
    )
    
    manager.create_migration(
        name="migration2",
        up_sql="CREATE TABLE test2 (id INTEGER);",
        down_sql="DROP TABLE test2;"
    )
    
    pending = manager.get_pending_migrations()
    
    assert len(pending) == 2


def test_query_optimizer_basic(mock_ai):
    """Test basic query optimization."""
    optimizer = QueryOptimizer(mock_ai, 'sqlite')
    
    query = "SELECT * FROM users WHERE id = 1"
    result = optimizer.optimize_query(query)
    
    assert result.original_query == query
    assert len(result.optimized_query) > 0


def test_query_optimizer_analysis(mock_ai):
    """Test query analysis."""
    optimizer = QueryOptimizer(mock_ai, 'sqlite')
    
    query = "SELECT * FROM users"
    analysis = optimizer.analyze_query(query)
    
    assert len(analysis.issues) > 0  # Should detect SELECT *
    assert len(analysis.suggestions) > 0


def test_query_optimizer_suggest_indexes(mock_ai):
    """Test index suggestion."""
    optimizer = QueryOptimizer(mock_ai, 'sqlite')
    
    query = "SELECT * FROM users WHERE email = 'test@example.com'"
    indexes = optimizer.suggest_indexes(query, 'users')
    
    assert len(indexes) > 0
    assert any('email' in idx for idx in indexes)


def test_database_debugger_query(mock_ai):
    """Test query debugging."""
    debugger = DatabaseDebugger(mock_ai, 'sqlite')
    
    query = "SELECT * FROM users"
    error = "no such table: users"
    
    result = debugger.debug_query(query, error)
    
    assert result.issue is not None
    assert result.solution is not None


def test_database_debugger_connection(mock_ai):
    """Test connection debugging."""
    debugger = DatabaseDebugger(mock_ai, 'sqlite')
    
    conn_string = "sqlite:///test.db"
    error = "database does not exist"
    
    result = debugger.debug_connection(conn_string, error)
    
    assert "database" in result.issue.lower() or "not found" in result.issue.lower()


def test_field_type_enum():
    """Test FieldType enum."""
    assert FieldType.INTEGER.value == "INTEGER"
    assert FieldType.STRING.value == "STRING"
    assert FieldType.BOOLEAN.value == "BOOLEAN"


def test_table_creation():
    """Test Table dataclass."""
    table = Table(
        name="products",
        fields=[
            Field(name="id", field_type=FieldType.INTEGER, primary_key=True),
            Field(name="name", field_type=FieldType.STRING, nullable=False),
            Field(name="price", field_type=FieldType.FLOAT)
        ]
    )
    
    assert table.name == "products"
    assert len(table.fields) == 3
    assert table.fields[0].primary_key is True
