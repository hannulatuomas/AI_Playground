# AI Agent Console - Examples

This directory contains example files and demonstrations for the AI Agent Console features.

## Contents

### 1. `sample_prompts.json`

**Purpose:** Sample prompt library demonstrating the Saved Prompts and Snippets feature

**Contains:**
- Code review templates
- Debugging assistant prompts
- Documentation generation templates
- Testing templates
- Security review prompts
- Performance analysis templates
- API documentation templates
- Git commit message templates
- Daily standup templates
- Bug report templates

**Usage:**
```bash
# Import sample prompts
python main.py prompt-import examples/sample_prompts.json

# List imported prompts
python main.py prompt-list

# Use a sample prompt
python main.py prompt-use "code-review-template" \
  --vars "language=Python,concerns=performance"
```

**Features Demonstrated:**
- Global and project-scoped prompts
- Variable substitution with `{{variable}}` syntax
- Tag-based organization
- Multiple prompt types (prompts and snippets)
- Metadata and usage tracking

**See Also:** [Saved Prompts Guide](../docs/guides/SAVED_PROMPTS.md)

---

### 2. `llamacpp_demo.py`

**Purpose:** Demonstration of direct GGUF model loading with llama-cpp

**Features:**
- Loading GGUF models without a server
- GPU acceleration configuration
- Context window management
- Temperature and sampling parameters
- Streaming responses

**Usage:**
```bash
# Ensure you have a GGUF model downloaded
python examples/llamacpp_demo.py
```

**Prerequisites:**
- llama-cpp-python installed
- GGUF model file (e.g., llama-2-7b-chat.Q4_K_M.gguf)

**Configuration:** Edit the script to point to your GGUF model file

**See Also:** [Llama-cpp Integration Guide](../docs/LLAMA_CPP_INTEGRATION.md)

---

### 3. `task_loop_demo.py`

**Purpose:** Demonstration of automated task lifecycle management

**Features:**
- Automated task list processing
- Plan → Implement → Test → Fix → Document workflow
- Priority-based task execution
- Dependency management
- State persistence
- Progress tracking

**Usage:**
```bash
python examples/task_loop_demo.py
```

**Demonstrates:**
- Task loop initialization
- Adding tasks with priorities
- Automatic workflow execution
- Error handling and retry logic
- State persistence across runs

**See Also:** [Task Loop Processing Guide](../docs/TASK_LOOP_PROCESSING.md)

---

### 4. `versioning_demo.py`

**Purpose:** Demonstration of automated semantic versioning system

**Features:**
- Automatic version bump detection
- Multi-file version updates
- Git integration
- Changelog generation
- Version history tracking

**Usage:**
```bash
chmod +x examples/versioning_demo.py
./examples/versioning_demo.py
```

**Demonstrates:**
- Version bump (major, minor, patch)
- Updating version in multiple files
- Creating git tags
- Generating changelogs
- Rollback capabilities

**See Also:** [Versioning System Guide](../docs/guides/VERSIONING_SYSTEM.md)

---

## Running Examples

### Prerequisites

Ensure you have the AI Agent Console installed and configured:

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp config.yaml my_config.yaml
# Edit my_config.yaml with your settings
```

### General Usage

Most examples can be run directly with Python:

```bash
python examples/<example_name>.py
```

Some examples may require additional setup (e.g., downloading models, configuring API keys). Check the individual example comments for specific requirements.

---

## Creating Your Own Examples

Want to add your own examples? Follow these guidelines:

1. **File Naming:** Use descriptive names with `_demo.py` suffix
2. **Documentation:** Include a docstring at the top explaining the example
3. **Comments:** Add inline comments for complex logic
4. **Prerequisites:** Document any required setup or dependencies
5. **Error Handling:** Include proper error handling and user feedback

Example template:

```python
"""
Example: [Feature Name] Demonstration

Purpose: Brief description of what this example demonstrates

Prerequisites:
- Requirement 1
- Requirement 2

Usage:
    python examples/my_example.py

Author: Your Name
Date: YYYY-MM-DD
"""

import logging
from core.engine import Engine

# Example code here...

if __name__ == "__main__":
    # Run example
    pass
```

---

## Contributing Examples

To contribute new examples:

1. Create your example following the guidelines above
2. Test thoroughly
3. Add documentation to this README
4. Submit a pull request

---

## Additional Resources

- **[User Guide](../docs/guides/user_guide.md)** - Complete usage guide
- **[Example Usage](../docs/guides/EXAMPLE_USAGE.md)** - More usage examples
- **[API Documentation](../docs/)** - Full API reference
- **[GitHub Repository](#)** - Source code and issues

---

## Need Help?

- Check the [User Guide](../docs/guides/user_guide.md)
- Read the [Documentation](../docs/README.md)
- Open an issue on GitHub
- Join our community chat

---

**Last Updated:** October 14, 2025  
**Version:** 2.5.0
