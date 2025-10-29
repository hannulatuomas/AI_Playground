# Quick Start: Project Templates

## 🚀 Create a Project in 3 Steps

### Step 1: Import TemplateManager

```python
from src.features.project_lifecycle import TemplateManager
from pathlib import Path

manager = TemplateManager()
```

### Step 2: Configure Variables

```python
config = {
    "PROJECT_NAME": "my-project",
    "AUTHOR": "Your Name",
    "DESCRIPTION": "Project description"
}
```

### Step 3: Create Project

```python
success, message = manager.create_from_template(
    "template-name",  # web-react, api-fastapi, or cli-python
    Path("./my-project"),
    config
)

print(message)
```

---

## 📋 Available Templates

### 1. web-react
Modern React application with Vite and TypeScript

```python
config = {
    "PROJECT_NAME": "my-react-app",
    "AUTHOR": "John Doe",
    "DESCRIPTION": "My React application",
    "LICENSE": "MIT"
}

manager.create_from_template("web-react", Path("./my-react-app"), config)
```

**Then run:**
```bash
cd my-react-app
npm install
npm run dev
```

### 2. api-fastapi
FastAPI REST API with SQLAlchemy

```python
config = {
    "PROJECT_NAME": "my_api",
    "AUTHOR": "Jane Smith",
    "DESCRIPTION": "My API service",
    "VERSION": "1.0.0",
    "PYTHON_VERSION": "3.12"
}

manager.create_from_template("api-fastapi", Path("./my-api"), config)
```

**Then run:**
```bash
cd my-api
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. cli-python
Professional Python CLI tool

```python
config = {
    "PROJECT_NAME": "my_cli",
    "AUTHOR": "Bob Johnson",
    "EMAIL": "bob@example.com",
    "DESCRIPTION": "My CLI tool",
    "VERSION": "0.1.0"
}

manager.create_from_template("cli-python", Path("./my-cli"), config)
```

**Then run:**
```bash
cd my-cli
python -m venv venv
venv\Scripts\activate  # Windows
pip install -e ".[dev]"
my_cli --help
```

---

## 🔍 List Available Templates

```python
templates = manager.list_templates()

for t in templates:
    print(f"{t['name']}: {t['description']}")
```

---

## ✅ Validate a Template

```python
template = manager.get_template("web-react")

if template:
    is_valid, errors = manager.validate_template(template)
    if is_valid:
        print("✅ Template is valid!")
    else:
        print("❌ Errors:", errors)
```

---

## 📦 Add Custom Template

```python
success, message = manager.add_custom_template(
    Path("./my-custom-template.json")
)

print(message)
```

---

## 📝 Custom Template Format

```json
{
  "name": "my-template",
  "description": "Template description",
  "version": "1.0.0",
  "variables": {
    "PROJECT_NAME": {
      "type": "string",
      "required": true
    },
    "AUTHOR": {
      "type": "string",
      "default": ""
    }
  },
  "files": {
    "README.md": "# {{PROJECT_NAME}}\n\nBy {{AUTHOR}}",
    "main.py": "print('{{PROJECT_NAME}}')"
  },
  "commands": [
    "pip install -r requirements.txt"
  ]
}
```

---

## ⚡ Quick Examples

### Example 1: Create Multiple Projects

```python
projects = [
    ("web-react", "project1", "React App 1"),
    ("api-fastapi", "project2", "API Service 2"),
    ("cli-python", "project3", "CLI Tool 3")
]

for template, name, desc in projects:
    config = {
        "PROJECT_NAME": name,
        "AUTHOR": "Your Name",
        "DESCRIPTION": desc
    }
    
    success, msg = manager.create_from_template(
        template,
        Path(f"./{name}"),
        config
    )
    
    print(f"{template}: {msg}")
```

### Example 2: Interactive Creation

```python
def create_project_interactive():
    # Get template
    templates = manager.list_templates()
    print("Available templates:")
    for i, t in enumerate(templates):
        print(f"{i+1}. {t['name']}: {t['description']}")
    
    choice = int(input("Choose template: ")) - 1
    template_name = templates[choice]['name']
    
    # Get variables
    config = {}
    config['PROJECT_NAME'] = input("Project name: ")
    config['AUTHOR'] = input("Author (optional): ")
    config['DESCRIPTION'] = input("Description (optional): ")
    
    # Create
    dest = Path(f"./{config['PROJECT_NAME']}")
    success, msg = manager.create_from_template(
        template_name,
        dest,
        config
    )
    
    print(msg)

create_project_interactive()
```

### Example 3: Batch Project Creation

```python
import json

# Load projects from config
with open('projects_to_create.json') as f:
    projects = json.load(f)

# Create each project
for project in projects:
    success, msg = manager.create_from_template(
        project['template'],
        Path(project['path']),
        project['config']
    )
    
    status = "✅" if success else "❌"
    print(f"{status} {project['config']['PROJECT_NAME']}: {msg}")
```

---

## 🔧 Common Issues

### Issue 1: Template Not Found

```
Template 'my-template' not found
```

**Solution**: Check spelling, ensure template exists in:
- `src/features/project_lifecycle/templates/` (built-in)
- `data/project_templates/` (custom)

### Issue 2: Invalid Project Name

```
Invalid project name. Use only alphanumeric characters...
```

**Solution**: Use only letters, numbers, hyphens, and underscores
- ✅ Good: `my-project`, `my_project`, `MyProject123`
- ❌ Bad: `my project`, `my@project`, `my.project`

### Issue 3: Destination Already Exists

```
Destination './my-app' already exists
```

**Solution**: Choose different path or remove existing directory

---

## 📚 More Information

- **Full Guide**: `docs/TEMPLATE_GUIDE.md`
- **Developer Guide**: `docs/EXTENDING_GUIDE.md`
- **API Reference**: See docstrings in `templates.py`

---

## 💡 Tips

1. **Variable Names**: Use UPPER_SNAKE_CASE
2. **Project Names**: Use kebab-case for web, snake_case for Python
3. **Validation**: Always validate before creating
4. **Custom Templates**: Store in `data/project_templates/`
5. **Defaults**: Provide sensible defaults for optional variables

---

**Happy Scaffolding!** 🎉

Create professional projects in seconds with best practices built-in.
