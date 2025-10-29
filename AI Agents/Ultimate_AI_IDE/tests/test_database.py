"""
Tests for Database Manager
"""

import pytest
import tempfile
import os
from datetime import datetime

from src.db.database import Database
from src.db.models import Project, Rule, Memory, Log


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)
        db.connect()
        db.initialize()
        yield db
        db.close()


def test_database_connection(temp_db):
    """Test database connection."""
    assert temp_db.connection is not None


def test_database_initialization(temp_db):
    """Test database schema initialization."""
    # Check if tables exist by querying them
    cursor = temp_db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = ['projects', 'rules', 'memory', 'logs', 'prompts', 'code_summaries']
    for table in expected_tables:
        assert table in tables


def test_add_project(temp_db):
    """Test adding a project."""
    project = Project(
        name="test_project",
        path="/path/to/project",
        language="python",
        framework="flask"
    )
    
    project_id = temp_db.add_project(project)
    assert project_id is not None
    assert project_id > 0


def test_get_project(temp_db):
    """Test retrieving a project."""
    # Add project
    project = Project(
        name="test_project",
        path="/path/to/project",
        language="python"
    )
    project_id = temp_db.add_project(project)
    
    # Retrieve project
    retrieved = temp_db.get_project(project_id)
    assert retrieved is not None
    assert retrieved.name == "test_project"
    assert retrieved.language == "python"


def test_get_project_by_path(temp_db):
    """Test retrieving project by path."""
    project = Project(
        name="test_project",
        path="/unique/path",
        language="python"
    )
    temp_db.add_project(project)
    
    retrieved = temp_db.get_project_by_path("/unique/path")
    assert retrieved is not None
    assert retrieved.name == "test_project"


def test_list_projects(temp_db):
    """Test listing all projects."""
    # Add multiple projects
    for i in range(3):
        project = Project(
            name=f"project_{i}",
            path=f"/path/to/project_{i}",
            language="python"
        )
        temp_db.add_project(project)
    
    projects = temp_db.list_projects()
    assert len(projects) == 3


def test_add_rule(temp_db):
    """Test adding a rule."""
    rule = Rule(
        rule_text="Always use type hints",
        scope="global",
        category="coding",
        priority=5
    )
    
    rule_id = temp_db.add_rule(rule)
    assert rule_id is not None
    assert rule_id > 0


def test_get_rules(temp_db):
    """Test retrieving rules."""
    # Add global rule
    global_rule = Rule(
        rule_text="Global rule",
        scope="global"
    )
    temp_db.add_rule(global_rule)
    
    # Add project rule
    project_rule = Rule(
        rule_text="Project rule",
        scope="project",
        project_id=1
    )
    temp_db.add_rule(project_rule)
    
    # Get all rules
    all_rules = temp_db.get_rules()
    assert len(all_rules) == 2
    
    # Get global rules only
    global_rules = temp_db.get_rules(scope="global")
    assert len(global_rules) == 1
    assert global_rules[0].scope == "global"


def test_add_memory(temp_db):
    """Test adding memory."""
    memory = Memory(
        key="test_key",
        value="test_value",
        context="test context"
    )
    
    memory_id = temp_db.add_memory(memory)
    assert memory_id is not None
    assert memory_id > 0


def test_get_memory(temp_db):
    """Test retrieving memory."""
    memory = Memory(
        key="test_key",
        value="test_value"
    )
    temp_db.add_memory(memory)
    
    retrieved = temp_db.get_memory("test_key")
    assert retrieved is not None
    assert retrieved.key == "test_key"
    assert retrieved.value == "test_value"


def test_add_log(temp_db):
    """Test adding log entry."""
    log = Log(
        module="test_module",
        action="test_action",
        level="INFO",
        success=True
    )
    
    log_id = temp_db.add_log(log)
    assert log_id is not None
    assert log_id > 0


def test_get_logs(temp_db):
    """Test retrieving logs."""
    # Add multiple logs
    for i in range(5):
        log = Log(
            module=f"module_{i}",
            action=f"action_{i}",
            level="INFO",
            success=True
        )
        temp_db.add_log(log)
    
    # Get all logs
    logs = temp_db.get_logs(limit=10)
    assert len(logs) == 5
    
    # Get logs for specific module
    logs = temp_db.get_logs(module="module_0")
    assert len(logs) == 1
    assert logs[0].module == "module_0"
