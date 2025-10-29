
"""
Pytest configuration and shared fixtures.

This module provides common fixtures and configurations used across
all test modules in the AI Agent Console test suite.
"""

import pytest
import logging
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import Mock, MagicMock

# Set up logging for tests
logging.basicConfig(level=logging.INFO)


# ============================================================================
# Fixtures for Configuration
# ============================================================================

@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide a mock configuration dictionary for testing."""
    return {
        'llm': {
            'default_provider': 'ollama',
            'default_model': 'llama3.2:3b',
            'temperature': 0.7,
            'max_tokens': 2000
        },
        'agents': {
            'code_editor': {
                'model': 'llama3.2:3b'
            },
            'code_planner': {
                'model': 'llama3.2:3b'
            }
        },
        'tools': {
            'git': {
                'enabled': True
            },
            'web_fetch': {
                'enabled': True,
                'timeout': 30
            }
        },
        'memory': {
            'enabled': True,
            'max_history': 100
        },
        'vector_db': {
            'enabled': False,
            'collection_name': 'test_collection'
        }
    }


@pytest.fixture
def mock_llm_config() -> Dict[str, Any]:
    """Provide LLM-specific configuration."""
    return {
        'provider': 'ollama',
        'model': 'llama3.2:3b',
        'temperature': 0.7,
        'max_tokens': 2000,
        'timeout': 60
    }


@pytest.fixture
def app_config() -> Any:
    """
    Provide a proper AppConfig object for testing.
    
    This creates a full AppConfig instance with all necessary settings
    for testing components that require proper configuration objects.
    """
    from core.config import AppConfig, OllamaSettings, OpenAISettings, ModelSettings, FallbackPreferences, RetryPolicy
    
    # Create a minimal but complete AppConfig
    config = AppConfig(
        ollama=OllamaSettings(
            host="http://localhost",
            port=11434,
            timeout=60,
            default_model="llama3.2:3b"
        ),
        openai=OpenAISettings(
            api_key="test-key",
            default_model="gpt-3.5-turbo",
            timeout=60
        ),
        models=ModelSettings(
            default_provider="ollama",
            default_model="llama3.2:3b",
            ollama_default="llama3.2:3b",
            openai_default="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=2000
        ),
        fallback=FallbackPreferences(
            enabled=True,
            primary_provider="ollama",
            fallback_provider="openai"
        ),
        retry=RetryPolicy(
            max_retries=3,
            initial_delay=1.0,
            max_delay=10.0,
            exponential_base=2.0
        )
    )
    
    return config


# ============================================================================
# Fixtures for LLM Router
# ============================================================================

@pytest.fixture
def mock_llm_router() -> Mock:
    """Provide a mock LLM router for testing."""
    router = Mock()
    router.query = Mock(return_value={
        'success': True,
        'response': 'Mock LLM response',
        'model': 'llama3.2:3b',
        'tokens': 50
    })
    router.query_async = Mock(return_value={
        'success': True,
        'response': 'Mock async LLM response',
        'model': 'llama3.2:3b',
        'tokens': 50
    })
    router.is_available = Mock(return_value=True)
    router.get_model = Mock(return_value='llama3.2:3b')
    return router


@pytest.fixture
def llm_router(app_config) -> Any:
    """
    Provide a real LLM router instance for testing.
    
    This fixture creates an actual LLMRouter with proper configuration,
    useful for integration tests that need real routing logic.
    """
    from core.llm_router import LLMRouter
    
    # Create router with app_config
    router = LLMRouter(config=app_config)
    return router


# ============================================================================
# Fixtures for Tool Registry
# ============================================================================

@pytest.fixture
def mock_tool_registry() -> Mock:
    """Provide a mock tool registry for testing."""
    registry = Mock()
    
    # Mock tools
    mock_git_tool = Mock()
    mock_git_tool.name = 'git'
    mock_git_tool.invoke = Mock(return_value={'success': True, 'message': 'Git operation successful'})
    
    mock_web_tool = Mock()
    mock_web_tool.name = 'web_fetch'
    mock_web_tool.invoke = Mock(return_value={'success': True, 'content': 'Web content'})
    
    # Set up registry methods
    registry.get = Mock(side_effect=lambda name: {
        'git': mock_git_tool,
        'web_fetch': mock_web_tool
    }.get(name))
    
    registry.list_tools = Mock(return_value=['git', 'web_fetch', 'shell'])
    
    return registry


# ============================================================================
# Fixtures for Memory Manager
# ============================================================================

@pytest.fixture
def mock_memory_manager() -> Mock:
    """Provide a mock memory manager for testing."""
    manager = Mock()
    manager.add_message = Mock()
    manager.get_history = Mock(return_value=[])
    manager.clear = Mock()
    manager.save_session = Mock()
    manager.load_session = Mock()
    manager.get_summary = Mock(return_value='Session summary')
    return manager


# ============================================================================
# Fixtures for Agent Registry
# ============================================================================

@pytest.fixture
def mock_agent_registry(mock_llm_router, mock_tool_registry) -> Mock:
    """Provide a mock agent registry for testing."""
    registry = Mock()
    
    # Mock agents
    mock_code_editor = Mock()
    mock_code_editor.name = 'code_editor'
    mock_code_editor.execute = Mock(return_value={
        'success': True,
        'message': 'Code edited successfully'
    })
    
    # Set up registry methods
    registry.get = Mock(return_value=mock_code_editor)
    registry.get_or_create_agent = Mock(return_value=mock_code_editor)
    registry.list_agents = Mock(return_value=['code_editor', 'code_planner', 'git_agent'])
    
    return registry


# ============================================================================
# Fixtures for File System
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_project_dir(temp_dir) -> Path:
    """Provide a temporary project directory with sample structure."""
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    
    # Create sample structure
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "docs").mkdir()
    
    # Create sample files
    (project_dir / "README.md").write_text("# Test Project")
    (project_dir / "requirements.txt").write_text("pytest>=7.0.0\n")
    (project_dir / "src" / "main.py").write_text("def main():\n    print('Hello')\n")
    
    return project_dir


# ============================================================================
# Fixtures for Test Data
# ============================================================================

@pytest.fixture
def sample_python_code() -> str:
    """Provide sample Python code for testing."""
    return '''
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b


def main():
    result = calculate_sum(5, 3)
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
'''


@pytest.fixture
def sample_task_context() -> Dict[str, Any]:
    """Provide sample task context for testing."""
    return {
        'project_path': '/tmp/test_project',
        'language': 'python',
        'user_preferences': {
            'style': 'pep8',
            'max_line_length': 88
        },
        'previous_results': {},
        'session_id': 'test-session-123'
    }


# ============================================================================
# Fixtures for Mocking External Services
# ============================================================================

@pytest.fixture
def mock_ollama_client() -> Mock:
    """Provide a mock Ollama client for testing."""
    client = Mock()
    client.generate = Mock(return_value={
        'response': 'Mock Ollama response',
        'done': True
    })
    client.list = Mock(return_value={
        'models': [
            {'name': 'llama3.2:3b'},
            {'name': 'codellama:7b'}
        ]
    })
    return client


@pytest.fixture
def mock_chromadb_client() -> Mock:
    """Provide a mock ChromaDB client for testing."""
    client = Mock()
    collection = Mock()
    collection.add = Mock()
    collection.query = Mock(return_value={
        'ids': [['id1', 'id2']],
        'documents': [['doc1', 'doc2']],
        'metadatas': [[{'source': 'test'}, {'source': 'test'}]],
        'distances': [[0.1, 0.2]]
    })
    collection.count = Mock(return_value=10)
    collection.name = 'test_collection'
    client.get_or_create_collection = Mock(return_value=collection)
    client.get_collection = Mock(return_value=collection)
    client.create_collection = Mock(return_value=collection)
    client.list_collections = Mock(return_value=[collection])
    return client


# ============================================================================
# Fixtures for Git Operations
# ============================================================================

@pytest.fixture
def mock_git_repo(temp_project_dir) -> Mock:
    """Provide a mock Git repository for testing."""
    repo = Mock()
    repo.working_dir = str(temp_project_dir)
    repo.is_dirty = Mock(return_value=False)
    repo.active_branch = Mock()
    repo.active_branch.name = 'main'
    repo.remotes = Mock()
    
    # Mock index.diff() to return empty list (no changes)
    mock_diff_item = Mock()
    mock_diff_item.a_path = 'test_file.txt'
    repo.index.diff = Mock(return_value=[])
    repo.untracked_files = []
    
    return repo


# ============================================================================
# Markers and Test Categories
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interactions"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests for complete workflows"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take a long time to run"
    )
    config.addinivalue_line(
        "markers", "requires_ollama: Tests that require Ollama to be running"
    )
    config.addinivalue_line(
        "markers", "requires_db: Tests that require database connections"
    )
    config.addinivalue_line(
        "markers", "requires_web: Tests that require internet connectivity"
    )
