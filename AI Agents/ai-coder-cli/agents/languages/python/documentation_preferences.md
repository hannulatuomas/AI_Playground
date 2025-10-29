
# Python Documentation Preferences

This document defines the documentation standards and preferences for Python projects.
These preferences guide AI agents in maintaining consistent, high-quality documentation.

---

## General Documentation Philosophy

**Core Principles:**
1. **Clarity Over Cleverness**: Documentation should be clear and understandable
2. **Completeness**: All public APIs should be documented
3. **Consistency**: Follow established patterns throughout the project
4. **Currency**: Keep documentation synchronized with code
5. **Accessibility**: Write for developers of varying experience levels

---

## Code Documentation Standards

### Docstring Format

**Preferred Style:** Google Style (NumPy style acceptable as alternative)

**Module Docstrings:**
```python
"""
Module name and one-line summary.

More detailed description of the module, its purpose, and key components.
Can span multiple paragraphs.

Examples:
    Basic usage example:
    >>> import module_name
    >>> result = module_name.function()

Attributes:
    MODULE_CONSTANT (str): Description of module-level constant.

Notes:
    Any important notes about the module.
"""
```

**Class Docstrings:**
```python
class ClassName:
    """
    One-line summary of the class.
    
    More detailed description of the class purpose, behavior, and usage.
    
    Attributes:
        attribute_name (type): Description of attribute.
        another_attr (type): Description of another attribute.
    
    Examples:
        >>> obj = ClassName()
        >>> obj.method()
        'result'
    
    Notes:
        Important notes about the class.
    """
```

**Function/Method Docstrings:**
```python
def function_name(param1: str, param2: int = 0) -> bool:
    """
    One-line summary of function purpose.
    
    More detailed description if needed. Explain what the function
    does, not how it does it (implementation details).
    
    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 0.
    
    Returns:
        Description of return value.
    
    Raises:
        ValueError: When param1 is empty.
        TypeError: When param2 is not an integer.
    
    Examples:
        >>> function_name("test", 5)
        True
        >>> function_name("example")
        True
    
    Notes:
        Any important implementation notes or gotchas.
    """
```

### Type Hints

**Always include type hints** for:
- Function parameters
- Return values
- Class attributes (using class-level annotations)
- Module-level constants

```python
from typing import List, Dict, Optional, Union, Any

def process_data(
    items: List[str],
    config: Optional[Dict[str, Any]] = None
) -> Union[str, None]:
    """Process items according to configuration."""
    pass
```

### Inline Comments

**When to use:**
- Complex algorithms that need explanation
- Non-obvious code patterns or workarounds
- Business logic that isn't self-evident
- Performance optimizations

**Style:**
```python
# This is a single-line comment explaining the next line
result = complex_operation()

# For multi-line explanations:
# First line of explanation
# Second line of explanation
# Third line of explanation
another_result = another_operation()
```

**Avoid:**
- Obvious comments that just restate the code
- Commented-out code (use version control instead)
- Outdated comments

---

## Project Documentation Structure

### Required Files

1. **README.md** - Project overview and quick start
2. **TODO.md** - Task tracking and project roadmap
3. **CHANGELOG.md** - Version history and changes
4. **CONTRIBUTING.md** - Contribution guidelines
5. **API.md** or **docs/api/** - API documentation
6. **codebase_structure.md** - Project structure overview

### README.md Structure

```markdown
# Project Title

Brief description (1-2 sentences).

[![Build Status](badge-url)](link)
[![Coverage](badge-url)](link)
[![License](badge-url)](link)

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

### Requirements

- Python 3.8+
- Additional dependencies

### Quick Install

```bash
pip install package-name
```

### Development Install

```bash
git clone https://github.com/user/repo.git
cd repo
pip install -e ".[dev]"
```

## Quick Start

```python
import package_name

# Example usage
result = package_name.main_function()
```

## Configuration

Explain configuration options, environment variables, config files.

## Usage

Detailed usage examples and common scenarios.

## API Documentation

Link to comprehensive API docs or include overview.

## Development

### Setup Development Environment

```bash
# Setup instructions
```

### Running Tests

```bash
pytest
```

### Code Style

We follow PEP 8 and use:
- `black` for formatting
- `flake8` for linting
- `mypy` for type checking

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

Licensed under [License Name]. See [LICENSE](LICENSE) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

## Contact

- Author: Name
- Email: email@example.com
- GitHub: @username
```

### TODO.md Structure

```markdown
# TODO List

**Last Updated:** YYYY-MM-DD

## Legend

- 🔴 High Priority
- 🟡 Medium Priority
- 🟢 Low Priority
- ⚡ In Progress
- ✅ Completed

## Current Sprint

### 🔴 High Priority

- [ ] Critical task 1
- [ ] Critical task 2

### ⚡ In Progress

- [ ] Task being worked on
  - Started: YYYY-MM-DD
  - Assignee: Name

### 🟡 Medium Priority

- [ ] Important task 1
- [ ] Important task 2

### 🟢 Low Priority

- [ ] Nice to have 1

## Backlog

### Features

- [ ] Future feature 1
- [ ] Future feature 2

### Technical Debt

- [ ] Refactoring task 1
- [ ] Performance improvement 1

### Documentation

- [ ] Update API docs
- [ ] Add more examples

## Completed (Recent)

- [x] Task completed recently (YYYY-MM-DD)
- [x] Another completed task (YYYY-MM-DD)
```

### CHANGELOG.md Format

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- New features here

### Changed
- Changes to existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security fixes

## [1.0.0] - YYYY-MM-DD

### Added
- Initial release
- Feature 1
- Feature 2
```

---

## API Documentation

### Docstring to Documentation

Use tools for automatic API documentation generation:
- **Sphinx** with autodoc extension (recommended)
- **pdoc3** for simpler projects
- **mkdocs** with mkdocstrings

### API Documentation Structure

```markdown
# API Reference

## Module: module_name

Description of the module.

### Functions

#### function_name

```python
def function_name(param1: str, param2: int) -> bool
```

Description of function.

**Parameters:**
- `param1` (str): Description
- `param2` (int): Description

**Returns:**
- `bool`: Description

**Raises:**
- `ValueError`: When...

**Example:**
```python
>>> function_name("test", 5)
True
```

### Classes

#### ClassName

Description of class.

**Methods:**
- `method1()`: Description
- `method2()`: Description
```

---

## Documentation Tools

### Recommended Tools

1. **Sphinx** - Full-featured documentation generator
   ```bash
   pip install sphinx sphinx-rtd-theme
   sphinx-quickstart
   ```

2. **Black** - Code formatter (standardizes formatting)
   ```bash
   pip install black
   black .
   ```

3. **mypy** - Type checker
   ```bash
   pip install mypy
   mypy --install-types
   ```

4. **pydocstyle** - Docstring style checker
   ```bash
   pip install pydocstyle
   pydocstyle src/
   ```

5. **interrogate** - Check documentation coverage
   ```bash
   pip install interrogate
   interrogate -v src/
   ```

### Documentation Build Process

```bash
# Generate API docs with Sphinx
cd docs
make html

# Check documentation coverage
interrogate -v src/

# Validate docstring style
pydocstyle src/
```

---

## Special Documentation Cases

### Async Functions

```python
async def async_function(param: str) -> Dict[str, Any]:
    """
    Async function description.
    
    Note:
        This is an async function. Must be awaited.
    
    Args:
        param: Parameter description.
    
    Returns:
        Dictionary with results.
    
    Example:
        >>> result = await async_function("test")
    """
```

### Generators

```python
def generator_function(n: int) -> Generator[int, None, None]:
    """
    Generator function description.
    
    Args:
        n: Number of items to generate.
    
    Yields:
        int: Generated values.
    
    Example:
        >>> for value in generator_function(5):
        ...     print(value)
    """
```

### Context Managers

```python
class ContextManager:
    """
    Context manager description.
    
    Examples:
        >>> with ContextManager() as cm:
        ...     cm.do_something()
    """
    
    def __enter__(self) -> 'ContextManager':
        """Enter context."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context and cleanup."""
        pass
```

### Decorators

```python
def decorator_function(func: Callable) -> Callable:
    """
    Decorator description.
    
    Args:
        func: Function to decorate.
    
    Returns:
        Decorated function.
    
    Example:
        >>> @decorator_function
        ... def my_function():
        ...     pass
    """
```

---

## Documentation Maintenance

### When to Update Documentation

1. **Immediately** when:
   - Adding new public functions/classes
   - Changing function signatures
   - Modifying behavior
   - Fixing bugs that affect usage

2. **Regularly** (weekly/sprint):
   - Update TODO.md
   - Update STATUS.md
   - Review and update README.md

3. **At Releases**:
   - Update CHANGELOG.md
   - Update version numbers
   - Regenerate API documentation
   - Review all documentation for accuracy

### Documentation Review Checklist

- [ ] All public APIs have docstrings
- [ ] Type hints are present and correct
- [ ] Examples are provided and tested
- [ ] README.md is current
- [ ] CHANGELOG.md is updated
- [ ] API documentation generated successfully
- [ ] No broken links in documentation
- [ ] Configuration examples are correct

---

## AI Agent Guidelines

**For AI Agents Maintaining Documentation:**

1. **Always preserve user-written content** - Don't remove or significantly alter manually written sections
2. **Be consistent** - Match existing style and tone
3. **Be comprehensive** - Don't skip sections
4. **Include examples** - Real, working code examples
5. **Keep it current** - Update when code changes
6. **Use proper markdown** - Follow markdown best practices
7. **Validate** - Check for broken links, code blocks, formatting
8. **Prioritize clarity** - Simple, clear language over jargon

**Priority Order for Documentation Updates:**
1. Code docstrings (highest priority)
2. README.md (user-facing)
3. codebase_structure.md (structural changes)
4. API.md (API changes)
5. TODO.md (task updates)
6. CHANGELOG.md (at releases)

---

**Last Updated:** 2025-10-12
**Version:** 1.0
