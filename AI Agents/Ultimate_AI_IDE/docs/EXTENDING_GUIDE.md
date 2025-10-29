# Extending Guide - Ultimate AI-Powered IDE

Guide for developers who want to extend or contribute to UAIDE.

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Architecture Overview](#architecture-overview)
3. [Adding New Features](#adding-new-features)
4. [Adding Language Support](#adding-language-support)
5. [Creating Plugins](#creating-plugins)
6. [Contributing Guidelines](#contributing-guidelines)
7. [Code Standards](#code-standards)

---

## Development Setup

### Prerequisites

- Python 3.12.10+
- Git
- Virtual environment tool
- IDE with Python support

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd ultimate-ai-ide

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # (to be created)

# Run setup
python scripts/setup.py

# Run tests
pytest tests/
```

---

## Architecture Overview

### Module Structure

```
src/
├── ai/           # AI backend (Phase 1)
├── db/           # Database (Phase 1)
├── ui/           # User interface (Phase 1)
├── config/       # Configuration (Phase 1)
├── core/         # Core orchestration (Phase 5)
├── modules/      # Feature modules (Phases 2-4)
└── utils/        # Utilities (Phase 1)
```

### Design Principles

1. **Modularity**: Each module is independent
2. **Single Responsibility**: One purpose per module
3. **Open/Closed**: Open for extension, closed for modification
4. **Dependency Injection**: Pass dependencies explicitly
5. **Interface Segregation**: Small, focused interfaces

---

## Adding New Features

### Step 1: Plan

1. Define feature requirements
2. Identify affected modules
3. Design API
4. Plan tests

### Step 2: Create Module

```python
# src/modules/my_feature/__init__.py
"""
My Feature Module

Description of what this module does.
"""

from .manager import MyFeatureManager

__all__ = ["MyFeatureManager"]
```

```python
# src/modules/my_feature/manager.py
"""
My Feature Manager

Detailed description.
"""

from typing import Optional, Any


class MyFeatureManager:
    """Manages my feature functionality."""
    
    def __init__(self, ai_backend, database):
        """
        Initialize manager.
        
        Args:
            ai_backend: AI backend instance
            database: Database instance
        """
        self.ai = ai_backend
        self.db = database
        
    def do_something(self, param: str) -> Any:
        """
        Do something useful.
        
        Args:
            param: Input parameter
            
        Returns:
            Result of operation
        """
        # Implementation
        pass
```

### Step 3: Write Tests

```python
# tests/unit/test_my_feature.py
"""Tests for MyFeature module."""

import pytest
from src.modules.my_feature import MyFeatureManager


class TestMyFeatureManager:
    """Test MyFeatureManager class."""
    
    def test_initialization(self, mock_ai, mock_db):
        """Test manager initializes correctly."""
        manager = MyFeatureManager(mock_ai, mock_db)
        assert manager.ai is mock_ai
        assert manager.db is mock_db
        
    def test_do_something(self, mock_ai, mock_db):
        """Test do_something method."""
        manager = MyFeatureManager(mock_ai, mock_db)
        result = manager.do_something("test")
        assert result is not None
```

### Step 4: Integrate

```python
# src/core/orchestrator.py
from src.modules.my_feature import MyFeatureManager

class UAIDE:
    def __init__(self, config):
        # ... existing initialization
        self.my_feature = MyFeatureManager(self.ai, self.db)
```

### Step 5: Document

- Update API.md
- Add usage examples
- Update USER_GUIDE.md
- Add to CHANGELOG.md

---

## Adding Language Support

### Step 1: Create Language Handler

```python
# src/modules/project_manager/languages/rust.py
"""Rust language support."""

from typing import Dict, Any


class RustHandler:
    """Handles Rust projects."""
    
    @staticmethod
    def get_template(framework: str = None) -> Dict[str, Any]:
        """
        Get Rust project template.
        
        Args:
            framework: Optional framework (e.g., 'actix')
            
        Returns:
            Template structure
        """
        return {
            "files": {
                "Cargo.toml": rust_cargo_template(),
                "src/main.rs": rust_main_template(),
                "src/lib.rs": rust_lib_template(),
            },
            "directories": ["src", "tests", "benches"]
        }
    
    @staticmethod
    def detect_project(path: str) -> bool:
        """Detect if path is Rust project."""
        return (Path(path) / "Cargo.toml").exists()
```

### Step 2: Register Handler

```python
# src/modules/project_manager/languages/__init__.py
from .python import PythonHandler
from .rust import RustHandler

LANGUAGE_HANDLERS = {
    "python": PythonHandler,
    "rust": RustHandler,
}
```

### Step 3: Add Templates

```python
# src/modules/project_manager/templates/rust/basic/
Cargo.toml
src/
  main.rs
  lib.rs
tests/
README.md
```

### Step 4: Update Configuration

```python
# src/utils/constants.py
SUPPORTED_LANGUAGES = [
    # ... existing languages
    "rust",
]

FRAMEWORKS = {
    # ... existing frameworks
    "rust": ["actix", "rocket", "warp"],
}
```

### Step 5: Add Tests

```python
# tests/unit/test_rust_support.py
def test_rust_project_creation():
    """Test Rust project creation."""
    pm = ProjectManager(ai, db)
    project = pm.create_project(
        name="rust_app",
        language="rust",
        framework="actix"
    )
    assert project.language == "rust"
    assert (Path(project.path) / "Cargo.toml").exists()
```

---

## Creating Plugins

### Plugin Structure

```python
# plugins/my_plugin/__init__.py
from src.core.plugin_system import Plugin


class MyPlugin(Plugin):
    """My custom plugin."""
    
    name = "my_plugin"
    version = "1.0.0"
    description = "Does something useful"
    
    def initialize(self, uaide):
        """Initialize plugin with UAIDE instance."""
        self.uaide = uaide
        self.register_hooks()
        
    def register_hooks(self):
        """Register event hooks."""
        self.uaide.events.subscribe(
            "code.generated",
            self.on_code_generated
        )
        
    def on_code_generated(self, event):
        """Handle code generation event."""
        # Custom logic here
        pass
        
    def execute(self, context):
        """Execute plugin logic."""
        # Main plugin functionality
        pass
```

### Plugin Installation

```python
# plugins/my_plugin/setup.py
from setuptools import setup

setup(
    name="uaide-my-plugin",
    version="1.0.0",
    packages=["my_plugin"],
    install_requires=["uaide>=0.1.0"],
    entry_points={
        "uaide.plugins": [
            "my_plugin = my_plugin:MyPlugin"
        ]
    }
)
```

### Plugin Usage

```bash
# Install plugin
pip install uaide-my-plugin

# Enable plugin
python src/main.py plugins enable my_plugin

# List plugins
python src/main.py plugins list
```

---

## Contributing Guidelines

### Before Contributing

1. Read the codebase structure
2. Check existing issues/PRs
3. Discuss major changes first
4. Follow code standards

### Pull Request Process

1. **Fork and Branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make Changes**
   - Follow code standards
   - Add tests
   - Update documentation

3. **Test**
   ```bash
   pytest tests/
   black src/ tests/
   pylint src/
   mypy src/
   ```

4. **Commit**
   ```bash
   git commit -m "feat: Add my feature

   - Detailed description
   - Breaking changes
   - Related issues"
   ```

5. **Push and PR**
   ```bash
   git push origin feature/my-feature
   ```

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

---

## Code Standards

### Python Style

- **PEP 8**: Follow Python style guide
- **Black**: Auto-formatter
- **Line Length**: 100 characters max
- **File Length**: 500 lines max (split if larger)

### Type Hints

Required for all functions:

```python
def process_data(
    input: str,
    options: Optional[Dict[str, Any]] = None
) -> List[Result]:
    """Process data with options."""
    pass
```

### Docstrings

Google style, required for all public APIs:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Short description.
    
    Longer description with more details about what
    the function does and how to use it.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
        
    Example:
        >>> my_function("test", 42)
        True
    """
    pass
```

### Error Handling

```python
def risky_operation() -> Result:
    """Operation that might fail."""
    try:
        # Attempt operation
        result = do_something()
    except SpecificError as e:
        # Handle specific error
        logger.error(f"Operation failed: {e}")
        raise
    except Exception as e:
        # Handle unexpected errors
        logger.exception("Unexpected error")
        raise OperationError("Failed") from e
    else:
        # Success path
        return result
    finally:
        # Cleanup
        cleanup()
```

### Testing

- **Coverage**: >80% required
- **Unit Tests**: Test each function
- **Integration Tests**: Test module interactions
- **Fixtures**: Use pytest fixtures
- **Mocking**: Mock external dependencies

```python
@pytest.fixture
def mock_ai():
    """Mock AI backend."""
    return Mock(spec=AIBackend)

def test_feature(mock_ai):
    """Test with mocked AI."""
    feature = MyFeature(mock_ai)
    result = feature.do_something()
    assert result is not None
    mock_ai.query.assert_called_once()
```

---

## Development Workflow

### 1. Choose Task

Check TODO.md or issues for tasks.

### 2. Create Branch

```bash
git checkout -b type/description
```

### 3. Implement

- Write code
- Add tests
- Update docs

### 4. Test Locally

```bash
pytest tests/
black --check src/ tests/
pylint src/
mypy src/
```

### 5. Commit

Follow commit message format.

### 6. Submit PR

Include:
- Description of changes
- Related issues
- Testing performed
- Breaking changes (if any)

---

## Resources

- [Project Structure](CODEBASE_STRUCTURE.md)
- [API Reference](API.md)
- [Phase Plans](PHASE_*_PLAN.md)
- [TODO](../TODO.md)

---

## Getting Help

- Check documentation
- Review existing code
- Ask in discussions
- File an issue

---

**Last Updated**: January 19, 2025  
**Version**: 0.1.0
