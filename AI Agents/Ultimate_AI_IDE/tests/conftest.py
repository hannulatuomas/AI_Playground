"""
Pytest Configuration

Shared fixtures and configuration for tests.
"""

import pytest
from pathlib import Path


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for testing."""
    return tmp_path / "test_project"


@pytest.fixture
def sample_config():
    """Provide sample configuration for testing."""
    return {
        "ai": {
            "model_path": "models/test-model.gguf",
            "max_tokens": 512,
            "temperature": 0.7
        },
        "database": {
            "path": ":memory:"  # In-memory database for tests
        }
    }
