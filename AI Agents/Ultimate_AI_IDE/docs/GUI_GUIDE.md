# UAIDE GUI Guide

## Overview

The UAIDE GUI provides a comprehensive graphical interface for all UAIDE features, built with Python's tkinter library for maximum compatibility.

## Launching the GUI

### Windows
```bash
.\scripts\run_gui.bat
```

### Linux/Mac
```bash
python -m src.ui.gui.main_window
```

## Features

### 📁 Projects Tab

**New Project**
- Create new projects with language and framework selection
- Automatic project structure generation
- Git initialization option

**Detect Project**
- Analyze existing projects
- Detect language, framework, and dependencies
- View project structure

**My Projects**
- List all registered projects
- Quick access to project details

### 💻 Code Generation Tab

**Generate Feature**
- Describe features in natural language
- AI-powered code generation
- Task decomposition and execution

**Generate Class**
- Create classes with AI assistance
- Support for multiple languages
- Automatic documentation

**Generate Function**
- Generate functions from descriptions
- Type hints and documentation included

### 🧪 Testing Tab

**Generate Tests**
- Automatic test generation from source files
- Support for pytest, jest, unittest, etc.
- Comprehensive test coverage

**Run Tests**
- Execute test suites
- View results and coverage
- Detailed error reporting

**Fix Bugs**
- AI-powered bug diagnosis
- Suggested fixes with confidence scores
- Root cause analysis

### 📚 Documentation Tab

- Generate README.md files
- Create API documentation
- Sync documentation with code
- Changelog generation

### 🔧 Refactoring Tab

**Analyze Code**
- Code quality metrics
- Complexity analysis
- Issue detection
- Improvement suggestions

**Refactor**
- Improve naming conventions
- Reduce complexity
- Add/improve docstrings
- Optimize imports

### 💬 AI Chat Tab

- Interactive AI assistant
- Code-related questions
- Context-aware responses
- Chat history

### ⚙️ Settings Tab

**AI Settings**
- Model configuration
- Token limits
- Temperature settings
- GPU acceleration

**Database**
- Database path configuration
- Backup management

**General**
- Logging configuration
- Code generation preferences

## Keyboard Shortcuts

- **Ctrl+Enter** (in chat): Send message
- **Ctrl+Q**: Quit application (when implemented)

## Tips

1. **Browse Buttons**: Use browse buttons to select files/directories instead of typing paths
2. **Async Operations**: Long-running operations run in background threads
3. **Error Messages**: Check output panels for detailed error information
4. **Settings**: Configure AI model path in Settings before first use

## Architecture

The GUI is modularly designed with separate files for each component:

```
src/ui/gui/
├── __init__.py          # Module exports
├── base.py              # Base classes and utilities
├── main_window.py       # Main application window
├── tab_project.py       # Project management
├── tab_code.py          # Code generation
├── tab_test.py          # Testing features
├── tab_docs.py          # Documentation
├── tab_refactor.py      # Refactoring
├── tab_chat.py          # AI chat
└── tab_settings.py      # Settings
```

## Troubleshooting

### GUI Won't Start

1. Ensure virtual environment is activated
2. Check Python version (3.8+)
3. Verify tkinter is installed: `python -m tkinter`

### Import Errors

Run from project root:
```bash
python -m src.ui.gui.main_window
```

### AI Not Responding

1. Check AI model path in Settings
2. Verify model file exists
3. Check llama.cpp binary location

## Development

To extend the GUI:

1. Create new tab in `src/ui/gui/tab_*.py`
2. Inherit from `BaseTab`
3. Implement `setup_ui()` method
4. Add to `main_window.py` notebook
5. Use `run_async()` for long operations

Example:
```python
from .base import BaseTab, run_async

class MyTab(BaseTab):
    def setup_ui(self):
        # Create UI components
        pass
    
    def my_action(self):
        def task():
            return self.uaide.some_method()
        
        def callback(result, error=None):
            if error:
                self.show_error("Error", error)
            else:
                self.show_success("Success", "Done!")
        
        run_async(task, callback)
```

## Future Enhancements

- [ ] Syntax highlighting in code panels
- [ ] Drag-and-drop file support
- [ ] Project templates
- [ ] Custom themes
- [ ] Keyboard shortcuts configuration
- [ ] Plugin system
