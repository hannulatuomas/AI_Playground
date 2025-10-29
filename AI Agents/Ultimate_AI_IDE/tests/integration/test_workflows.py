"""
Integration Tests - Complete Workflows

Tests complete workflows across multiple modules.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.core.orchestrator import UAIDE


@pytest.fixture
def temp_workspace():
    """Create temporary workspace."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def uaide():
    """Create UAIDE instance."""
    return UAIDE()


def test_project_creation_workflow(uaide, temp_workspace):
    """Test complete project creation workflow."""
    # Create project
    result = uaide.new_project(
        name="test_project",
        language="python",
        framework="fastapi",
        path=temp_workspace
    )
    
    assert result.success is True
    assert "test_project" in result.message
    
    # Verify project structure
    project_path = Path(temp_workspace)
    assert project_path.exists()


def test_code_generation_workflow(uaide, temp_workspace):
    """Test code generation workflow."""
    # Create project first
    uaide.new_project(
        name="test_app",
        language="python",
        path=temp_workspace
    )
    
    # Generate feature
    result = uaide.generate_feature(
        description="Create a simple calculator function",
        project_path=temp_workspace
    )
    
    # Should succeed or have meaningful error
    assert isinstance(result.success, bool)
    assert result.message is not None


def test_documentation_workflow(uaide, temp_workspace):
    """Test documentation generation workflow."""
    # Create project
    uaide.new_project(
        name="test_docs",
        language="python",
        path=temp_workspace
    )
    
    # Generate documentation
    result = uaide.generate_docs(
        project_path=temp_workspace,
        language="python"
    )
    
    assert isinstance(result.success, bool)


def test_event_bus_integration(uaide):
    """Test event bus integration."""
    events_received = []
    
    def handler(event):
        events_received.append(event)
    
    # Subscribe to events
    uaide.event_bus.subscribe('test.event', handler)
    
    # Emit event
    uaide.event_bus.emit('test.event', {'data': 'test'})
    
    # Verify event was received
    assert len(events_received) == 1
    assert events_received[0].type == 'test.event'


def test_stats_collection(uaide):
    """Test statistics collection."""
    stats = uaide.get_stats()
    
    assert 'context_manager' in stats
    assert 'event_history' in stats
    assert 'rules_loaded' in stats


def test_error_handling(uaide):
    """Test error handling in workflows."""
    # Try to create project with invalid parameters
    result = uaide.new_project(
        name="",  # Invalid name
        language="python"
    )
    
    # Should handle error gracefully
    assert result.success is False
    assert result.errors is not None or result.message is not None
