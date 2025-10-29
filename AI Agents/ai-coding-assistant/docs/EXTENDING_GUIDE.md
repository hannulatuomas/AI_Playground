# Extending Guide - AI Coding Assistant

## Overview

This guide is for developers who want to extend, customize, or contribute to the AI Coding Assistant. Learn how to add new features, languages, and integrations.

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Architecture Overview](#architecture-overview)
3. [Adding a New Language](#adding-a-new-language)
4. [Adding a New Feature](#adding-a-new-feature)
5. [Adding a Project Template](#adding-a-project-template)
6. [Adding a New UI Mode](#adding-a-new-ui-mode)
7. [Customizing Prompts](#customizing-prompts)
8. [Database Modifications](#database-modifications)
9. [Testing Your Extensions](#testing-your-extensions)
10. [Contributing Guidelines](#contributing-guidelines)

---

## Development Setup

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/ai-coding-assistant.git
cd ai-coding-assistant
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Install Development Dependencies

```bash
pip install pylint flake8 mypy black pytest pytest-cov
```

### 3. Setup Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF

# Install hooks
pre-commit install
```

### 4. Verify Setup

```bash
python tests/tests.py
python src/main.py --help
```

---

## Architecture Overview

### Module Hierarchy

```
UI Layer (src/ui/)
    ↓
Features Layer (src/features/)
    ↓
Core Layer (src/core/)
```

**Rules:**
- UI depends on Features and Core
- Features depends only on Core
- Core has no internal dependencies
- No circular dependencies

### Key Design Patterns

1. **Dependency Injection**: Pass dependencies to constructors
2. **Strategy Pattern**: Different strategies for different languages
3. **Repository Pattern**: Database abstraction
4. **Factory Pattern**: Object creation
5. **Observer Pattern**: Event handling

---

## Adding a New Language

[Previous content remains exactly the same through "Step 6: Test Thoroughly"]

---

## Adding a New Feature

[Previous content remains exactly the same through "Step 5: Update Documentation"]

---

## Adding a Project Template

### Overview

Project templates allow users to quickly scaffold new projects with best practices built-in. The template system supports variable substitution, multiple languages and frameworks, and cross-platform compatibility.

### Template Structure

Templates are JSON files with this structure:

```json
{
  "name": "my-template",
  "description": "Template description",
  "version": "1.0.0",
  "variables": {
    "PROJECT_NAME": {
      "type": "string",
      "required": true,
      "description": "Project name"
    },
    "AUTHOR": {
      "type": "string",
      "default": "",
      "description": "Author name"
    }
  },
  "files": {
    "relative/path/file.txt": "Content with {{VARIABLE}}",
    "src/main.py": "print('{{PROJECT_NAME}}')"
  },
  "commands": [
    "pip install -r requirements.txt",
    "python setup.py"
  ]
}
```

### Step 1: Create Template JSON

Create a new template file (e.g., `my-flask-app.json`):

```json
{
  "name": "flask-api",
  "description": "Flask REST API with SQLAlchemy",
  "version": "1.0.0",
  "variables": {
    "PROJECT_NAME": {
      "type": "string",
      "required": true
    },
    "AUTHOR": {
      "type": "string",
      "default": ""
    },
    "DESCRIPTION": {
      "type": "string",
      "default": "A Flask API"
    },
    "PORT": {
      "type": "integer",
      "default": "5000"
    }
  },
  "files": {
    "app.py": "from flask import Flask\n\napp = Flask('{{PROJECT_NAME}}')\n\n@app.route('/')\ndef index():\n    return 'Welcome to {{PROJECT_NAME}}'\n\nif __name__ == '__main__':\n    app.run(port={{PORT}})",
    "requirements.txt": "flask==3.0.0\nsqlalchemy==2.0.23\n",
    "README.md": "# {{PROJECT_NAME}}\n\n{{DESCRIPTION}}\n\n## Author\n\n{{AUTHOR}}",
    ".gitignore": "__pycache__/\n*.pyc\nvenv/\n.env"
  },
  "commands": [
    "python -m venv venv",
    "pip install -r requirements.txt"
  ]
}
```

### Step 2: Add to Built-in or Custom Templates

**For built-in templates**, place in:
```
src/features/project_lifecycle/templates/
```

**For custom user templates**, place in:
```
data/project_templates/
```

Or add programmatically:

```python
from src.features.project_lifecycle import TemplateManager
from pathlib import Path

manager = TemplateManager()
success, message = manager.add_custom_template(
    Path("./my-flask-app.json")
)
print(message)
```

### Step 3: Test Template

```python
from src.features.project_lifecycle import TemplateManager
from pathlib import Path

manager = TemplateManager()

# Validate template
template = manager.get_template("flask-api")
if template:
    is_valid, errors = manager.validate_template(template)
    if is_valid:
        print("✓ Template is valid!")
    else:
        print(f"✗ Errors: {errors}")

# Create project
config = {
    "PROJECT_NAME": "my-flask-app",
    "AUTHOR": "John Doe",
    "DESCRIPTION": "My awesome API",
    "PORT": "8000"
}

success, message = manager.create_from_template(
    "flask-api",
    Path("./test-project"),
    config
)

print(message)
```

### Step 4: Add Tests

Create tests in `tests/test_templates.py`:

```python
import unittest
from pathlib import Path
import tempfile
import shutil
from src.features.project_lifecycle import TemplateManager

class TestMyTemplate(unittest.TestCase):
    def test_template_valid(self):
        manager = TemplateManager()
        template = manager.get_template("flask-api")
        self.assertIsNotNone(template)
        
        is_valid, errors = manager.validate_template(template)
        self.assertTrue(is_valid)
    
    def test_create_project(self):
        manager = TemplateManager()
        dest = Path(tempfile.mkdtemp()) / "test-flask"
        
        try:
            config = {
                "PROJECT_NAME": "test-flask",
                "AUTHOR": "Test"
            }
            
            success, msg = manager.create_from_template(
                "flask-api",
                dest,
                config
            )
            
            self.assertTrue(success)
            self.assertTrue((dest / "app.py").exists())
            
            # Check variable substitution
            content = (dest / "app.py").read_text()
            self.assertIn("test-flask", content)
            
        finally:
            if dest.exists():
                shutil.rmtree(dest.parent)
```

### Step 5: Document Template

Add documentation:

```markdown
## Available Templates

### flask-api
Flask REST API with SQLAlchemy

**Usage:**
```python
manager.create_from_template(
    "flask-api",
    Path("./my-api"),
    {"PROJECT_NAME": "my-api", "AUTHOR": "Your Name"}
)
```

**Variables:**
- PROJECT_NAME: Name of your project (required)
- AUTHOR: Your name (optional)
- DESCRIPTION: Project description (optional)
- PORT: Server port (default: 5000)
```

### Template Best Practices

1. **Variable Names**: Use UPPER_SNAKE_CASE (e.g., PROJECT_NAME)
2. **Paths**: Always use forward slashes (/)
3. **Required vs Optional**: Mark truly required variables
4. **Defaults**: Provide sensible defaults for optional variables
5. **Commands**: List post-creation steps (not executed automatically)
6. **Documentation**: Include comprehensive README in template
7. **Validation**: Test on multiple platforms
8. **Gitignore**: Always include .gitignore
9. **License**: Include appropriate license
10. **Dependencies**: Pin versions in requirements files

### Variable Substitution Rules

- Variables use `{{VARIABLE_NAME}}` syntax
- Variables work in both file content and file paths
- Non-required variables default to empty string if not provided
- Variable validation happens before project creation
- Case-sensitive variable names

### Common Template Patterns

**Python Package:**
```json
{
  "files": {
    "setup.py": "...",
    "src/{{PROJECT_NAME}}/__init__.py": "__version__ = '{{VERSION}}'",
    "tests/test_{{PROJECT_NAME}}.py": "..."
  }
}
```

**Web Application:**
```json
{
  "files": {
    "package.json": "{\"name\": \"{{PROJECT_NAME}}\", ...}",
    "src/index.js": "...",
    "public/index.html": "<title>{{PROJECT_NAME}}</title>"
  }
}
```

**CLI Tool:**
```json
{
  "files": {
    "{{PROJECT_NAME}}.py": "#!/usr/bin/env python\n...",
    "README.md": "# {{PROJECT_NAME}}\n\n{{DESCRIPTION}}"
  }
}
```

For more details, see `docs/TEMPLATE_GUIDE.md` and `docs/TEMPLATE_QUICKSTART.md`.

---

## Adding a New UI Mode

[Rest of the content continues exactly as before...]

---

**Happy Extending!**

For more details, see the well-commented source code in `src/`.

**Last Updated:** October 18, 2025  
**Version:** 2.0.0
