# User Preferences & Configuration

Complete guide to customizing UAIDE to your preferences.

---

## Configuration File

Main configuration: `config.json`

Example configuration is in `config.example.json`.

---

## AI Settings

### Model Configuration

```json
{
  "ai": {
    "model_path": "models/llama-3-8b-q4.gguf",
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "context_length": 8192,
    "gpu_layers": 0
  }
}
```

**Options**:
- `model_path`: Path to your AI model
- `max_tokens`: Max response length (512-4096)
- `temperature`: Creativity (0.0-1.0)
  - 0.3: Precise code generation
  - 0.7: Balanced (recommended)
  - 0.9: Creative documentation
- `gpu_layers`: Number of layers on GPU (0 = CPU only)

---

## Code Generation Preferences

```json
{
  "code_generation": {
    "max_file_length": 500,
    "auto_format": true,
    "auto_import": true,
    "style_guide": "pep8",
    "add_type_hints": true,
    "add_docstrings": true,
    "check_duplicates": true
  }
}
```

**Options**:
- `max_file_length`: Lines per file (300-1000)
- `auto_format`: Auto-format code (black, prettier)
- `auto_import`: Add missing imports
- `style_guide`: Coding standard
- `add_type_hints`: Include type annotations
- `add_docstrings`: Generate documentation strings
- `check_duplicates`: Detect existing code

---

## Testing Preferences

```json
{
  "testing": {
    "auto_test": true,
    "coverage_threshold": 80,
    "test_framework": "pytest",
    "generate_fixtures": true,
    "mock_external_deps": true
  }
}
```

**Options**:
- `auto_test`: Run tests after generation
- `coverage_threshold`: Minimum coverage (%)
- `test_framework`: Testing library
- `generate_fixtures`: Create test data
- `mock_external_deps`: Mock external services

---

## Documentation Preferences

```json
{
  "documentation": {
    "auto_sync": true,
    "generate_readme": true,
    "generate_api_docs": true,
    "docstring_style": "google",
    "include_examples": true
  }
}
```

**Options**:
- `auto_sync`: Update docs on code change
- `generate_readme`: Auto-generate README
- `generate_api_docs`: Create API docs
- `docstring_style`: google, numpy, sphinx
- `include_examples`: Add usage examples

---

## Refactoring Preferences

```json
{
  "refactoring": {
    "auto_refactor": false,
    "max_complexity": 10,
    "max_function_length": 50,
    "enforce_naming": true,
    "remove_dead_code": true
  }
}
```

**Options**:
- `auto_refactor`: Auto-apply improvements
- `max_complexity`: McCabe complexity limit
- `max_function_length`: Max lines per function
- `enforce_naming`: Check naming conventions
- `remove_dead_code`: Delete unused code

---

## UI Preferences

```json
{
  "ui": {
    "theme": "dark",
    "color_output": true,
    "show_progress": true,
    "interactive_mode": true,
    "auto_save": true
  }
}
```

**Options**:
- `theme`: dark, light
- `color_output`: Colored terminal output
- `show_progress`: Progress bars
- `interactive_mode`: Confirmations
- `auto_save`: Save changes automatically

---

## Project Defaults

```json
{
  "project": {
    "default_language": "python",
    "default_framework": null,
    "git_auto_init": true,
    "create_venv": true,
    "install_deps": true
  }
}
```

**Options**:
- `default_language`: Default programming language
- `default_framework`: Default framework
- `git_auto_init`: Initialize git repo
- `create_venv`: Create virtual environment
- `install_deps`: Auto-install dependencies

---

## Rules Configuration

```json
{
  "rules": {
    "enforce_global": true,
    "enforce_project": true,
    "strict_mode": false
  }
}
```

**Options**:
- `enforce_global`: Apply global rules
- `enforce_project`: Apply project rules
- `strict_mode`: Fail on rule violations

---

## Performance Settings

```json
{
  "performance": {
    "async_operations": true,
    "parallel_processing": true,
    "max_workers": 4,
    "cache_responses": true
  }
}
```

**Options**:
- `async_operations`: Use async operations
- `parallel_processing`: Process in parallel
- `max_workers`: Number of worker threads
- `cache_responses`: Cache AI responses

---

## Custom Rules

### Global Rules

Apply to all projects:

```bash
python src/main.py rules add --global "Use descriptive variable names"
python src/main.py rules add --global "Maximum line length: 100"
python src/main.py rules add --global "No bare except clauses"
```

### Project Rules

Apply to current project:

```bash
python src/main.py rules add "Use async/await for I/O"
python src/main.py rules add "All endpoints require authentication"
```

### Rule Categories

- `style`: Code style and formatting
- `structure`: File and project organization
- `quality`: Code quality standards
- `testing`: Test requirements
- `documentation`: Doc requirements
- `security`: Security practices

---

## Language-Specific Preferences

### Python

```json
{
  "languages": {
    "python": {
      "version": "3.12",
      "formatter": "black",
      "linter": "pylint",
      "type_checker": "mypy",
      "import_order": ["standard", "third-party", "local"]
    }
  }
}
```

### JavaScript/TypeScript

```json
{
  "languages": {
    "javascript": {
      "use_semicolons": false,
      "quote_style": "single",
      "formatter": "prettier"
    },
    "typescript": {
      "strict": true,
      "target": "ES2020"
    }
  }
}
```

---

## Workflow Customization

### Pre-Generation Hooks

Run before code generation:

```json
{
  "hooks": {
    "pre_generate": [
      "lint",
      "format"
    ]
  }
}
```

### Post-Generation Hooks

Run after code generation:

```json
{
  "hooks": {
    "post_generate": [
      "test",
      "format",
      "docs"
    ]
  }
}
```

---

## Environment Variables

Override config with environment variables:

```bash
export UAIDE_MODEL_PATH=/path/to/model.gguf
export UAIDE_TEMPERATURE=0.5
export UAIDE_MAX_TOKENS=4096
```

---

## Profiles

Create multiple configuration profiles:

```bash
# Development profile
config.dev.json

# Production profile  
config.prod.json

# Use profile
python src/main.py --config config.dev.json
```

---

## Import/Export Settings

### Export Configuration

```bash
python src/main.py config export > my-settings.json
```

### Import Configuration

```bash
python src/main.py config import my-settings.json
```

---

## Best Practices

### 1. Start with Defaults

Use defaults initially, customize as needed.

### 2. Document Custom Rules

Keep a record of your project rules.

### 3. Version Control

Commit `config.json` (without secrets).

### 4. Environment-Specific

Use different configs for dev/prod.

### 5. Regular Review

Periodically review and update settings.

---

## Troubleshooting

### Configuration Not Loading

1. Check JSON syntax
2. Verify file path
3. Check file permissions

### Rules Not Applied

1. Check rule enforcement settings
2. Verify rule syntax
3. Check rule scope (global vs project)

### Performance Issues

1. Reduce `max_tokens`
2. Increase `cache_size`
3. Enable `parallel_processing`
4. Use GPU layers

---

## FAQ

**Q: Can I have project-specific configs?**
A: Yes, place `config.json` in project root.

**Q: How do I reset to defaults?**
A: Copy from `config.example.json`.

**Q: Can I share configs between projects?**
A: Yes, use global config or profiles.

---

**Last Updated**: January 19, 2025  
**Version**: 0.1.0
