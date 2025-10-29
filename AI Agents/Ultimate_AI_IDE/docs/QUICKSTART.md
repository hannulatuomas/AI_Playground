# Quick Start Guide - Ultimate AI-Powered IDE

Get up and running with UAIDE in 5 minutes!

---

## Installation

### Prerequisites
- Python 3.12.10 or higher
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space (for AI model)

### Step 1: Clone or Download

```bash
git clone https://github.com/yourusername/ultimate-ai-ide.git
cd ultimate-ai-ide
```

### Step 2: Run Setup

```bash
python scripts/setup.py
```

This will:
- Install dependencies
- Download the AI model
- Initialize the database
- Create configuration file

### Step 3: Verify Installation

```bash
python src/main.py --version
```

---

## Your First Project

### Create a New Project

```bash
# Python FastAPI project
python src/main.py new-project myapi --lang python --framework fastapi

# React + TypeScript project
python src/main.py new-project myapp --lang typescript --framework react
```

### Generate a Feature

```bash
cd myapi
python ../src/main.py generate "Add user authentication with JWT"
```

The AI will:
1. Analyze your request
2. Break it into sub-tasks
3. Generate code for each task
4. Create tests
5. Update documentation

### Run Tests

```bash
python ../src/main.py test
```

### View Documentation

```bash
python ../src/main.py docs generate
```

---

## Basic Commands

| Command | Description |
|---------|-------------|
| `new-project <name>` | Create a new project |
| `generate <description>` | Generate code feature |
| `test [files]` | Run tests |
| `fix [error]` | Fix bugs automatically |
| `refactor [files]` | Refactor code |
| `docs [action]` | Manage documentation |
| `chat` | Interactive AI chat mode |
| `status` | Show project status |

---

## Interactive Chat Mode

For a more conversational experience:

```bash
python src/main.py chat
```

Then you can:
```
> create a new fastapi project called blog_api
> add a blog post model with title, content, and author
> generate crud endpoints for blog posts
> add authentication
> run tests
```

---

## Configuration

Edit `config.json` to customize:

```json
{
  "ai": {
    "temperature": 0.7,
    "max_tokens": 2048
  },
  "code_generation": {
    "max_file_length": 500,
    "auto_format": true
  }
}
```

---

## Tips

1. **Be Specific**: More detailed descriptions = better results
2. **Use Context**: Reference existing files/functions
3. **Iterative**: Start small, then add complexity
4. **Review**: Always review generated code
5. **Test Often**: Run tests after each generation

---

## Next Steps

- Read the [User Guide](USER_GUIDE.md) for detailed features
- Check [API Documentation](API.md) for programmatic usage
- Learn about [Extending](EXTENDING_GUIDE.md) the IDE
- Join our [Community](#) for support

---

## Troubleshooting

**Model loading fails**
```bash
python scripts/download_model.py
```

**Database errors**
```bash
rm data/uaide.db
python scripts/setup.py --reset-db
```

**Import errors**
```bash
pip install -r requirements.txt --upgrade
```

For more help, see the [User Guide](USER_GUIDE.md) or file an [issue](https://github.com/yourusername/ultimate-ai-ide/issues).
