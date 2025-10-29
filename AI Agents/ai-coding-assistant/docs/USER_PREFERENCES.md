# User Preferences and Customization Guide

## Overview

The AI Coding Assistant can be customized to match your workflow, preferences, and requirements. This guide covers all available customization options.

---

## Configuration File (data/config.json)

The main configuration file controls the behavior of the LLM and application.

### Location
```
data/config.json
```

### Complete Configuration Template

```json
{
  "model_path": "data/models/your-model.gguf",
  "executable_path": "llama.cpp/llama-cli",
  "context_size": 4096,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "repeat_penalty": 1.1,
  "threads": 4,
  "gpu_layers": 0,
  "max_tokens": 2048,
  "timeout": 120
}
```

### Configuration Parameters

#### **model_path** (Required)
- **Type:** String (path)
- **Description:** Path to your GGUF model file
- **Example:** `"data/models/codellama-13b-instruct.Q4_K_M.gguf"`
- **Tips:**
  - Use absolute paths if relative paths don't work
  - Ensure file has `.gguf` extension
  - Larger models = better quality but slower

#### **executable_path** (Required)
- **Type:** String (path)
- **Description:** Path to llama-cli executable
- **Examples:**
  - Linux/macOS: `"llama.cpp/llama-cli"`
  - Windows: `"llama.cpp\\build\\bin\\Release\\llama-cli.exe"`
- **Tips:**
  - Test the path: run it directly in terminal
  - Use forward slashes (/) on all platforms

#### **context_size** (Optional, Default: 4096)
- **Type:** Integer
- **Range:** 512 - 32768
- **Description:** Maximum context window size in tokens
- **Recommendations:**
  - **2048:** Fast, good for simple tasks
  - **4096:** Balanced (recommended)
  - **8192:** Best for complex code
- **Trade-off:** Larger = slower but handles longer code

#### **temperature** (Optional, Default: 0.7)
- **Type:** Float
- **Range:** 0.0 - 2.0
- **Description:** Controls randomness/creativity
- **Recommendations:**
  - **0.1-0.3:** Deterministic, precise (debugging)
  - **0.7:** Balanced (recommended for most tasks)
  - **1.0-1.5:** Creative (code generation, brainstorming)
- **Tips:**
  - Lower for production code
  - Higher for exploring alternatives

#### **top_p** (Optional, Default: 0.9)
- **Type:** Float
- **Range:** 0.0 - 1.0
- **Description:** Nucleus sampling - alternative to temperature
- **Recommendations:**
  - **0.9:** Standard (recommended)
  - **0.95:** More diverse
  - **0.8:** More focused
- **Tips:** Works together with temperature

#### **top_k** (Optional, Default: 40)
- **Type:** Integer
- **Range:** 1 - 100
- **Description:** Limits token selection to top K choices
- **Recommendations:**
  - **40:** Standard (recommended)
  - **20:** More focused
  - **60-80:** More diverse
- **Tips:** Lower = more predictable

#### **repeat_penalty** (Optional, Default: 1.1)
- **Type:** Float
- **Range:** 1.0 - 1.5
- **Description:** Penalizes repetition
- **Recommendations:**
  - **1.0:** No penalty
  - **1.1:** Light penalty (recommended)
  - **1.3-1.5:** Strong penalty
- **Tips:** Increase if output is repetitive

#### **threads** (Optional, Default: 4)
- **Type:** Integer
- **Range:** 1 - CPU cores
- **Description:** Number of CPU threads to use
- **Recommendations:**
  - Match your CPU core count
  - Leave 1-2 cores for system
- **Example:** 8-core CPU = use 6-7 threads

#### **gpu_layers** (Optional, Default: 0)
- **Type:** Integer
- **Range:** 0 - model layers
- **Description:** Number of layers to offload to GPU
- **Recommendations:**
  - **0:** CPU only
  - **10-20:** Partial GPU (balanced)
  - **-1 or 99:** All layers to GPU
- **Requirements:**
  - NVIDIA GPU with CUDA
  - Or Apple Silicon with Metal
- **Tips:** Start low and increase if stable

#### **max_tokens** (Optional, Default: 2048)
- **Type:** Integer
- **Range:** 128 - 8192
- **Description:** Maximum tokens to generate
- **Recommendations:**
  - **512:** Short snippets
  - **2048:** Standard functions/classes
  - **4096:** Large code blocks
- **Tips:** Adjust based on expected output size

#### **timeout** (Optional, Default: 120)
- **Type:** Integer (seconds)
- **Range:** 30 - 600
- **Description:** Maximum time to wait for generation
- **Recommendations:**
  - **60:** Fast responses
  - **120:** Standard (recommended)
  - **300:** Complex generations
- **Tips:** Increase for large models or slow hardware

---

## Performance Presets

### Fast & Efficient
```json
{
  "context_size": 2048,
  "temperature": 0.5,
  "top_p": 0.9,
  "top_k": 40,
  "threads": 4,
  "gpu_layers": 0,
  "max_tokens": 1024,
  "timeout": 60
}
```
**Use for:** Quick answers, simple code generation

### Balanced (Recommended)
```json
{
  "context_size": 4096,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "threads": 6,
  "gpu_layers": 20,
  "max_tokens": 2048,
  "timeout": 120
}
```
**Use for:** Most coding tasks

### Quality & Precision
```json
{
  "context_size": 8192,
  "temperature": 0.3,
  "top_p": 0.95,
  "top_k": 20,
  "threads": 8,
  "gpu_layers": -1,
  "max_tokens": 4096,
  "timeout": 300
}
```
**Use for:** Production code, critical applications

### Creative & Exploratory
```json
{
  "context_size": 4096,
  "temperature": 1.2,
  "top_p": 0.95,
  "top_k": 60,
  "threads": 6,
  "gpu_layers": 20,
  "max_tokens": 2048,
  "timeout": 120
}
```
**Use for:** Brainstorming, exploring alternatives

---

## Customizing Prompts

### Location
Prompt templates are in: `src/core/prompt_engine.py`

### System Prompts (Per Language)

To customize system prompts for a language:

1. Open `src/core/prompt_engine.py`
2. Find the `system_prompts` dictionary
3. Edit the prompt for your language

**Example:** Custom Python prompt
```python
'python': """You are a senior Python developer with expertise in:
- Clean, Pythonic code following PEP 8
- Type hints and modern Python 3.12 features
- FastAPI and async programming
- Testing with pytest
- Performance optimization

Always provide:
1. Complete, working code
2. Type hints
3. Docstrings
4. Error handling
5. Brief explanation
"""
```

### Task Templates

To customize task templates:

1. Open `src/core/prompt_engine.py`
2. Find the `task_templates` dictionary
3. Edit the template for your task

**Example:** Custom generation template
```python
'generate': PromptTemplate(
    system="You are an expert software engineer.",
    user_prefix="Language: {language}\n\nTask: ",
    user_suffix="\n\nProvide complete, production-ready code with comments."
)
```

---

## Language Support Customization

### Adding a New Language

1. Open `src/features/lang_support.py`
2. Add to `language_info` dictionary:

```python
'rust': {
    'extensions': ['.rs'],
    'comment': '//',
    'common_keywords': ['fn', 'let', 'mut', 'impl', 'trait'],
    'frameworks': ['tokio', 'actix', 'rocket']
}
```

3. Open `src/core/prompt_engine.py`
4. Add system prompt:

```python
'rust': """You are a Rust expert. Follow best practices:
- Use ownership and borrowing correctly
- Prefer `match` over `if let` for clarity
- Use appropriate error handling
- Write idiomatic Rust code
"""
```

### Customizing Framework Detection

Edit `src/features/lang_support.py`:

```python
# In detect_language() method, add detection pattern:
if 'use rocket::' in code or 'rocket' in frameworks:
    framework = 'rocket'
```

---

## CLI Customization

### Color Scheme

Edit `src/ui/cli.py` to change colors:

```python
# Find color definitions
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
RED = Fore.RED
CYAN = Fore.CYAN

# Change to your preference
GREEN = Fore.LIGHTGREEN_EX
YELLOW = Fore.LIGHTYELLOW_EX
```

### Custom Commands

Add new commands in `src/ui/cli.py`:

```python
def handle_command(self, command: str):
    # Add your custom command
    if command.startswith('/mycommand'):
        parts = command.split(maxsplit=1)
        if len(parts) > 1:
            arg = parts[1]
            # Your implementation
            print("Running custom command...")
```

### Shortcuts/Aliases

Add command aliases:

```python
# In handle_command()
if command.startswith('/g '):  # Alias for /gen
    command = '/gen' + command[2:]
if command.startswith('/d '):  # Alias for /debug
    command = '/debug' + command[2:]
```

---

## GUI Customization

### Window Size and Position

Edit `src/ui/gui.py`:

```python
def __init__(self):
    self.root = tk.Tk()
    self.root.title("AI Coding Assistant")
    self.root.geometry("1200x800+100+100")  # Width x Height + X + Y
```

### Font and Colors

```python
# Custom fonts
self.font_family = "Consolas"  # or "Monaco", "Courier New"
self.font_size = 11

# Custom colors
self.bg_color = "#2b2b2b"  # Dark background
self.fg_color = "#ffffff"  # White text
self.button_color = "#0d7377"  # Teal buttons
```

### Dark Mode

```python
# Apply dark theme
self.root.configure(bg=self.bg_color)
self.input_text.configure(
    bg="#1e1e1e", 
    fg="#ffffff",
    insertbackground="#ffffff"
)
```

---

## Learning Database Customization

### Adjusting Learning Behavior

Edit `src/core/learning_db.py`:

```python
# Change how many learnings to retrieve
def get_relevant_learnings(self, language, task_type, limit=5):  # Changed from 3 to 5

# Change confidence score threshold
if confidence_score > 0.7:  # Changed from 0.5 to 0.7

# Change cleanup age
DELETE FROM interactions WHERE timestamp < date('now', '-60 days')  # Changed from 30
```

### Custom Learning Filters

Add custom filters in `get_relevant_learnings()`:

```python
# Only include learnings with high success rate
WHERE success = 1 AND feedback NOT LIKE '%wrong%'

# Prioritize recent learnings
ORDER BY timestamp DESC, occurrence_count DESC
```

---

## Environment Variables

Set environment variables for additional customization:

### Linux/macOS
```bash
# In ~/.bashrc or ~/.zshrc
export AI_CODING_ASSISTANT_MODEL="/path/to/model.gguf"
export AI_CODING_ASSISTANT_THREADS=8
export AI_CODING_ASSISTANT_DEBUG=1  # Enable debug output
```

### Windows
```batch
# In System Environment Variables
set AI_CODING_ASSISTANT_MODEL=C:\path\to\model.gguf
set AI_CODING_ASSISTANT_THREADS=8
set AI_CODING_ASSISTANT_DEBUG=1
```

### Usage in Code

```python
import os

model_path = os.environ.get('AI_CODING_ASSISTANT_MODEL', 'data/models/default.gguf')
threads = int(os.environ.get('AI_CODING_ASSISTANT_THREADS', '4'))
debug = bool(os.environ.get('AI_CODING_ASSISTANT_DEBUG', False))
```

---

## Advanced Customization

### Custom Response Parser

Edit `src/features/code_gen.py`:

```python
def _parse_response(self, response: str) -> Dict[str, str]:
    """Parse LLM response into code and explanation."""
    # Add your custom parsing logic
    # Example: support for different code block formats
    if '```' in response:
        # Existing logic
        pass
    elif '<code>' in response:
        # Custom XML-style code blocks
        parts = response.split('<code>')
        if len(parts) > 1:
            code_part = parts[1].split('</code>')[0]
            # ...
```

### Custom Error Classification

Edit `src/features/debugger.py`:

```python
def _classify_error(self, error_msg: str) -> str:
    """Classify error type from error message."""
    # Add your custom error patterns
    if 'NullPointerException' in error_msg:
        return 'null_pointer'
    if 'OutOfMemoryError' in error_msg:
        return 'memory_error'
    # ...
```

### Custom Statistics

Add custom statistics in `src/core/learning_db.py`:

```python
def get_custom_statistics(self) -> Dict:
    """Get custom statistics."""
    cursor = self.conn.cursor()
    
    # Average generation time by language
    cursor.execute("""
        SELECT language, AVG(generation_time) 
        FROM interactions 
        GROUP BY language
    """)
    
    # Most improved error types
    cursor.execute("""
        SELECT error_type, COUNT(*) as fixes
        FROM error_patterns
        WHERE occurrence_count > 5
        ORDER BY occurrence_count DESC
    """)
    
    # Your custom queries...
```

---

## Model-Specific Optimizations

### For CodeLlama Models
```json
{
  "context_size": 16384,
  "temperature": 0.2,
  "top_p": 0.95,
  "repeat_penalty": 1.1
}
```

### For Llama 3 Models
```json
{
  "context_size": 8192,
  "temperature": 0.7,
  "top_p": 0.9,
  "repeat_penalty": 1.2
}
```

### For DeepSeek Coder
```json
{
  "context_size": 4096,
  "temperature": 0.3,
  "top_p": 0.95,
  "repeat_penalty": 1.05
}
```

---

## Keyboard Shortcuts (Planned)

Future versions will support custom keyboard shortcuts:

```json
{
  "shortcuts": {
    "generate": "Ctrl+G",
    "debug": "Ctrl+D",
    "explain": "Ctrl+E",
    "save": "Ctrl+S",
    "load": "Ctrl+O"
  }
}
```

---

## Tips for Best Results

### 1. Start with Defaults
- Use default settings first
- Adjust gradually based on results
- Document what works for you

### 2. Match Model to Task
- Use coding models for code generation
- Use general models for explanations
- Consider model size vs. speed trade-off

### 3. Optimize for Your Hardware
- Set threads = CPU cores - 2
- Use GPU if available
- Reduce context_size if slow

### 4. Language-Specific Settings
- Lower temperature for production code
- Higher for exploratory coding
- Adjust based on language verbosity

### 5. Monitor Performance
- Use `/stats` to check success rates
- Use `/errors` to identify patterns
- Adjust prompts based on common issues

---

## Backup and Restore

### Backup Configuration
```bash
cp data/config.json data/config.json.backup
```

### Backup Learning Database
```bash
cp data/db/learning.db data/db/learning.db.backup
```

### Restore
```bash
cp data/config.json.backup data/config.json
cp data/db/learning.db.backup data/db/learning.db
```

---

## Reset to Defaults

### Reset Configuration
```bash
rm data/config.json
python src/main.py  # Will recreate with defaults
```

### Reset Learning Database
```bash
rm data/db/learning.db
# Database will be recreated on next run
```

---

## Getting Help

- Check `docs/API.md` for API reference
- See `README.md` for general usage
- Review `docs/EXTENDING_GUIDE.md` for development
- Open an issue on GitHub for bugs

---

**Last Updated:** October 16, 2025  
**Version:** 1.0.0

For more advanced customization, see the source code with extensive inline comments.
