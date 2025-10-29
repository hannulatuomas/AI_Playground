
"""
Python Project Initialization Agent

This agent handles Python project initialization with support for various
project types including CLI tools, web APIs, packages, and more.
"""

from typing import Dict, Any, List, Optional
from ...base import ProjectInitBase


class PythonProjectInitAgent(ProjectInitBase):
    """
    Python-specific project initialization agent.
    
    Capabilities:
    - Initialize Python projects (console, web, package, CLI, etc.)
    - Create proper Python package structure
    - Generate requirements.txt, setup.py, pyproject.toml
    - Support for various frameworks (FastAPI, Django, Flask, etc.)
    - Virtual environment setup guidance
    - Type hints and mypy configuration
    """
    
    def __init__(
        self,
        name: str = "project_init_python",
        description: str = "Python project initialization",
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None
    ):
        super().__init__(
            name=name,
            description=description,
            language="Python",
            llm_router=llm_router,
            tool_registry=tool_registry,
            config=config,
            memory_manager=memory_manager
        )
    
    def _get_project_types(self) -> List[str]:
        """Get supported Python project types."""
        return [
            'console',       # Console application
            'package',       # Python package/library
            'cli',           # CLI tool (with Click/Typer)
            'fastapi',       # FastAPI web application
            'flask',         # Flask web application
            'django',        # Django web application
            'data_science',  # Data science project
            'ml',            # Machine learning project
            'automation',    # Automation/scripting project
        ]
    
    def _get_project_structure(self, project_type: str) -> Dict[str, Any]:
        """Get directory structure for project type."""
        structures = {
            'console': {
                'directories': [
                    'src/{package_name}',
                    'tests',
                    'docs',
                ],
            },
            'package': {
                'directories': [
                    'src/{package_name}',
                    'tests',
                    'docs',
                    'examples',
                ],
            },
            'cli': {
                'directories': [
                    'src/{package_name}',
                    'src/{package_name}/commands',
                    'tests',
                    'docs',
                ],
            },
            'fastapi': {
                'directories': [
                    'app',
                    'app/api',
                    'app/api/endpoints',
                    'app/core',
                    'app/models',
                    'app/schemas',
                    'app/services',
                    'tests',
                    'docs',
                ],
            },
            'flask': {
                'directories': [
                    'app',
                    'app/routes',
                    'app/models',
                    'app/templates',
                    'app/static',
                    'tests',
                    'docs',
                ],
            },
            'django': {
                'directories': [
                    'config',
                    'apps',
                    'static',
                    'media',
                    'templates',
                    'tests',
                    'docs',
                ],
            },
            'data_science': {
                'directories': [
                    'data',
                    'data/raw',
                    'data/processed',
                    'notebooks',
                    'src',
                    'models',
                    'reports',
                    'docs',
                ],
            },
            'ml': {
                'directories': [
                    'data',
                    'data/raw',
                    'data/processed',
                    'notebooks',
                    'src',
                    'src/data',
                    'src/features',
                    'src/models',
                    'models',
                    'tests',
                    'docs',
                ],
            },
            'automation': {
                'directories': [
                    'scripts',
                    'config',
                    'logs',
                    'tests',
                    'docs',
                ],
            },
        }
        
        return structures.get(project_type, structures['console'])
    
    def _get_default_files(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate default Python configuration files."""
        files = {}
        package_name = config['project_name'].replace('-', '_').replace(' ', '_').lower()
        project_type = config['project_type']
        
        # README.md
        files['README.md'] = f"""# {config['project_name']}

{config.get('description', 'A Python project')}

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\\Scripts\\activate
# On Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```python
# Add usage examples here
```

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run type checking
mypy src/

# Format code
black src/ tests/
```

## Project Structure

See `.project_ai/rules.md` for detailed project guidelines.

## Author

{config.get('author', 'N/A')}

## License

{config.get('license', 'MIT')}
"""
        
        # requirements.txt
        requirements = self._get_requirements(project_type)
        files['requirements.txt'] = '\n'.join(requirements) + '\n'
        
        # requirements-dev.txt
        dev_requirements = [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'mypy>=1.0.0',
            'pylint>=2.17.0',
            'isort>=5.12.0',
        ]
        files['requirements-dev.txt'] = '\n'.join(dev_requirements) + '\n'
        
        # pyproject.toml
        files['pyproject.toml'] = f"""[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{config['project_name']}"
version = "0.1.0"
description = "{config.get('description', 'A Python project')}"
authors = [
    {{name = "{config.get('author', 'Author')}", email = "{config.get('email', 'author@example.com')}"}}
]
readme = "README.md"
requires-python = ">=3.9"
license = {{text = "{config.get('license', 'MIT')}"}}

dependencies = [
{self._format_dependencies_for_toml(requirements)}
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]

[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=html --cov-report=term"
"""
        
        # setup.py (for backward compatibility)
        files['setup.py'] = f"""from setuptools import setup, find_packages

setup(
    name="{config['project_name']}",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    install_requires=[
{self._format_dependencies_for_setup(requirements)}
    ],
)
"""
        
        # .gitignore
        files['.gitignore'] = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Type checking
.mypy_cache/
.dmypy.json
dmypy.json

# Environment
.env
.env.local

# Jupyter
.ipynb_checkpoints/
*.ipynb

# OS
.DS_Store
Thumbs.db
"""
        
        # Main entry point (project type specific)
        if project_type in ['console', 'package', 'cli']:
            files[f'src/{package_name}/__init__.py'] = f'''"""
{config['project_name']} - {config.get('description', 'A Python project')}
"""

__version__ = "0.1.0"
__author__ = "{config.get('author', 'Author')}"
'''
            
            files[f'src/{package_name}/main.py'] = '''"""Main entry point for the application."""

def main() -> None:
    """Main function."""
    print("Hello from {config['project_name']}!")


if __name__ == "__main__":
    main()
'''
        
        # FastAPI specific
        if project_type == 'fastapi':
            files['app/__init__.py'] = ''
            files['app/main.py'] = '''"""FastAPI application entry point."""

from fastapi import FastAPI
from app.api.endpoints import router

app = FastAPI(
    title="{config['project_name']}",
    description="{config.get('description', 'A FastAPI application')}",
    version="0.1.0"
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to {config['project_name']}"}
'''
            
            files['app/api/__init__.py'] = ''
            files['app/api/endpoints.py'] = '''"""API endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
'''
        
        # Test file
        files['tests/__init__.py'] = ''
        files['tests/test_basic.py'] = f'''"""Basic tests."""

import pytest


def test_example():
    """Example test."""
    assert True
'''
        
        return files
    
    def _get_requirements(self, project_type: str) -> List[str]:
        """Get requirements for project type."""
        common = []
        
        specific = {
            'fastapi': ['fastapi>=0.104.0', 'uvicorn[standard]>=0.24.0', 'pydantic>=2.0.0'],
            'flask': ['flask>=3.0.0', 'flask-cors>=4.0.0'],
            'django': ['django>=4.2.0', 'djangorestframework>=3.14.0'],
            'cli': ['click>=8.1.0', 'rich>=13.0.0'],
            'data_science': ['pandas>=2.0.0', 'numpy>=1.24.0', 'matplotlib>=3.7.0', 'jupyter>=1.0.0'],
            'ml': ['pandas>=2.0.0', 'numpy>=1.24.0', 'scikit-learn>=1.3.0', 'torch>=2.0.0'],
        }
        
        return common + specific.get(project_type, [])
    
    def _format_dependencies_for_toml(self, deps: List[str]) -> str:
        """Format dependencies for pyproject.toml."""
        if not deps:
            return ''
        return ',\n'.join(f'    "{dep}"' for dep in deps)
    
    def _format_dependencies_for_setup(self, deps: List[str]) -> str:
        """Format dependencies for setup.py."""
        if not deps:
            return ''
        return ',\n'.join(f'        "{dep}"' for dep in deps)
    
    def _generate_language_rules(self, config: Dict[str, Any]) -> str:
        """Generate Python-specific rules."""
        return f"""## Python-Specific Rules

### Python Version

- **Target Version**: Python 3.9+
- **Compatibility**: Maintain compatibility with Python 3.9-3.12

### Code Style

1. **PEP 8 Compliance**: Follow PEP 8 style guide
2. **Type Hints**: Use type hints for all function signatures
3. **Docstrings**: Use Google-style or NumPy-style docstrings
4. **Line Length**: Maximum 100 characters (configurable via Black)
5. **Imports**: 
   - Standard library first
   - Third-party packages second
   - Local imports last
   - Sort with isort

### Project Type: {config['project_type']}

{self._get_project_type_guidelines(config['project_type'])}

### Testing

1. **Framework**: Use pytest for testing
2. **Coverage**: Aim for >80% code coverage
3. **Test Structure**: Mirror source structure in tests/
4. **Fixtures**: Use pytest fixtures for test setup
5. **Mocking**: Use pytest-mock or unittest.mock

### Type Checking

1. **Tool**: Use mypy for static type checking
2. **Strictness**: Enable strict mode in mypy.ini
3. **Coverage**: All public APIs must be typed
4. **Generics**: Use proper generic types from typing

### Dependencies

1. **Management**: Use requirements.txt or pyproject.toml
2. **Versioning**: Pin major versions, allow minor/patch updates
3. **Virtual Environment**: Always use virtual environments
4. **Security**: Regular audits with pip-audit or safety

### Code Quality Tools

1. **Formatter**: Black (automated formatting)
2. **Linter**: Pylint or Flake8
3. **Import Sorter**: isort
4. **Type Checker**: mypy
5. **Security**: bandit for security checks

### Documentation

1. **Docstrings**: All public functions/classes must have docstrings
2. **README**: Keep README.md comprehensive
3. **API Docs**: Use Sphinx for API documentation
4. **Type Hints**: Type hints serve as inline documentation

### Package Structure

1. **Source Layout**: Use src/ layout for packages
2. **Init Files**: Use __init__.py to define public API
3. **Entry Points**: Define in pyproject.toml
4. **Version**: Single source of truth for version

### Error Handling

1. **Exceptions**: Use built-in exceptions when appropriate
2. **Custom Exceptions**: Create custom exceptions for domain errors
3. **Logging**: Use logging module, not print()
4. **Error Messages**: Provide clear, actionable error messages

### Performance

1. **Profiling**: Use cProfile for performance profiling
2. **Optimization**: Optimize after profiling, not before
3. **Generators**: Use generators for large data processing
4. **Caching**: Use functools.lru_cache for expensive operations

### Security

1. **Secrets**: Use environment variables or secret managers
2. **Input Validation**: Validate all external inputs
3. **SQL Injection**: Use parameterized queries
4. **Dependencies**: Keep dependencies updated
"""
    
    def _get_project_type_guidelines(self, project_type: str) -> str:
        """Get guidelines specific to project type."""
        guidelines = {
            'fastapi': """
**FastAPI Project Guidelines:**
- Use Pydantic models for request/response validation
- Implement dependency injection for database connections
- Use async/await for I/O operations
- Follow REST API best practices
- Document endpoints with OpenAPI descriptions
""",
            'django': """
**Django Project Guidelines:**
- Follow Django project structure conventions
- Use Django ORM for database operations
- Implement proper middleware for cross-cutting concerns
- Use Django REST Framework for APIs
- Follow Django security best practices
""",
            'flask': """
**Flask Project Guidelines:**
- Use Flask blueprints for modularity
- Implement application factory pattern
- Use Flask-SQLAlchemy for database operations
- Follow RESTful routing conventions
- Implement proper error handling
""",
            'cli': """
**CLI Tool Guidelines:**
- Use Click or Typer for command-line interfaces
- Implement proper help text and documentation
- Use Rich for beautiful terminal output
- Handle keyboard interrupts gracefully
- Provide clear error messages
""",
            'package': """
**Package/Library Guidelines:**
- Design a clear public API
- Use semantic versioning
- Provide comprehensive documentation
- Include usage examples
- Maintain backward compatibility
""",
        }
        
        return guidelines.get(project_type, "")
    
    def _get_language_specific_questions(self) -> List[Dict[str, Any]]:
        """Get Python-specific questions."""
        return [
            {
                'key': 'python_version',
                'question': 'Minimum Python version?',
                'type': 'choice',
                'options': ['3.9', '3.10', '3.11', '3.12'],
                'default': '3.9',
                'required': False
            },
            {
                'key': 'use_type_hints',
                'question': 'Use type hints?',
                'type': 'bool',
                'default': True,
                'required': False
            },
            {
                'key': 'use_black',
                'question': 'Use Black for formatting?',
                'type': 'bool',
                'default': True,
                'required': False
            },
            {
                'key': 'use_mypy',
                'question': 'Use mypy for type checking?',
                'type': 'bool',
                'default': True,
                'required': False
            },
        ]


