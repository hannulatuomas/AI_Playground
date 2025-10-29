
"""
Python-Specific Code Planning Agent

This agent specializes in planning Python projects with awareness of:
- Python packaging (setup.py, pyproject.toml)
- Virtual environments
- Common Python project structures
- Popular frameworks (Flask, Django, FastAPI, etc.)
"""

from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodePlannerBase


class PythonCodePlannerAgent(CodePlannerBase):
    """
    Agent specialized for Python project planning.
    
    Features:
    - Python package structure awareness
    - Virtual environment recommendations
    - Framework-specific planning
    - Testing structure (pytest)
    - Documentation (Sphinx)
    """
    
    def __init__(
        self,
        name: str = "code_planner_python",
        description: str = "Python-specific code planning agent",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            primary_language="Python",
            **kwargs
        )
    
    def _get_language_specific_context(self, context: Dict[str, Any]) -> str:
        """
        Get Python-specific context for planning.
        """
        return """
## Python-Specific Context

Follow Python best practices:
- **PEP 8**: Style guide for Python code
- **PEP 257**: Docstring conventions
- **Type hints**: Use type annotations (PEP 484)
- **Virtual environments**: Use venv or virtualenv
- **Package management**: Use pip, poetry, or pipenv
- **Testing**: pytest or unittest
- **Documentation**: Docstrings, Sphinx
- **Project structure**:
  - `src/` layout or flat layout
  - `tests/` directory
  - `docs/` for documentation
  - `requirements.txt` or `pyproject.toml`
  - `setup.py` for packages
  - `.gitignore` for Python

Popular frameworks to consider:
- **Web**: Flask, Django, FastAPI
- **Data Science**: NumPy, Pandas, scikit-learn
- **Testing**: pytest, unittest, mock
- **CLI**: Click, argparse, Typer
- **Async**: asyncio, aiohttp

Package structure:
```
project/
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── module.py
│       └── ...
├── tests/
│   ├── __init__.py
│   └── test_module.py
├── docs/
├── README.md
├── pyproject.toml
├── requirements.txt
└── .gitignore
```
"""
    
    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Python-specific plan requirements.
        """
        errors = []
        warnings = []
        
        # Check for Python-specific files
        file_paths = [f['path'] for f in plan.get('files', [])]
        
        # Should have __init__.py for packages
        has_init = any('__init__.py' in p for p in file_paths)
        if not has_init and any('.py' in p for p in file_paths):
            warnings.append("Consider adding __init__.py for Python packages")
        
        # Should have requirements or pyproject.toml
        has_deps = any(p in file_paths for p in ['requirements.txt', 'pyproject.toml', 'setup.py'])
        if not has_deps:
            warnings.append("Missing dependency management file (requirements.txt or pyproject.toml)")
        
        # Should have tests directory
        has_tests = any('test' in p.lower() for p in file_paths)
        if not has_tests:
            warnings.append("No test files or test directory in plan")
        
        # Check tech stack
        tech_stack = plan.get('tech_stack', {})
        if tech_stack.get('language', '').lower() != 'python':
            warnings.append("Tech stack language should be 'Python'")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _enhance_plan_with_language_specifics(
        self,
        plan: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance plan with Python-specific details.
        """
        file_paths = [f['path'] for f in plan.get('files', [])]
        
        # Add Python-specific files if not present
        python_files = {
            'requirements.txt': 'Python package dependencies',
            '.gitignore': 'Git ignore patterns for Python',
            'pytest.ini': 'pytest configuration',
            'setup.py': 'Package setup configuration',
            'README.md': 'Project documentation',
        }
        
        for file_path, purpose in python_files.items():
            if file_path not in file_paths:
                plan.setdefault('files', []).append({
                    'path': file_path,
                    'purpose': purpose,
                    'priority': 'high' if file_path in ['requirements.txt', 'README.md'] else 'medium'
                })
        
        # Add testing recommendations
        if 'testing' not in plan:
            plan['testing'] = {
                'framework': 'pytest',
                'structure': 'tests/ directory with test_*.py files',
                'coverage_tool': 'pytest-cov',
                'coverage_target': '80%'
            }
        
        # Add virtual environment recommendation
        if 'virtual_env' not in plan:
            plan['virtual_env'] = {
                'tool': 'venv',
                'command': 'python -m venv venv',
                'activation': 'source venv/bin/activate  # Linux/Mac\nvenv\\Scripts\\activate  # Windows'
            }
        
        # Add code quality tools
        if 'code_quality' not in plan:
            plan['code_quality'] = {
                'linter': 'pylint or flake8',
                'formatter': 'black',
                'type_checker': 'mypy',
                'import_sorter': 'isort'
            }
        
        return plan
    
    def _get_language_directory(self) -> Optional[Path]:
        """Get the Python language directory."""
        return Path(__file__).parent

