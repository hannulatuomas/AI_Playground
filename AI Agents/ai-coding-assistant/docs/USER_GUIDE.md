# User Guide - AI Coding Assistant

## Complete Guide to Using the AI Coding Assistant

**Version:** 1.0.0  
**Last Updated:** October 16, 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [First-Time Setup](#first-time-setup)
4. [Using the CLI](#using-the-cli)
5. [Using the GUI](#using-the-gui)
6. [Core Features](#core-features)
7. [Advanced Usage](#advanced-usage)
8. [Tips and Best Practices](#tips-and-best-practices)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## Introduction

The AI Coding Assistant is a lightweight, self-improving tool that helps you:
- Generate code from natural language descriptions
- Debug and fix code errors
- Explain complex code
- Optimize code for performance
- Refactor code for better structure

**Key Features:**
- 🚀 **Lightweight**: Minimal dependencies, runs locally
- 🧠 **Self-Improving**: Learns from your feedback
- 💻 **Multi-Language**: Supports 12+ programming languages
- 🔒 **Private**: All processing happens locally
- ⚡ **Fast**: Direct integration with llama.cpp

---

## Installation

### Prerequisites

- **Python 3.8+** (Python 3.12 recommended)
- **Git** (for cloning llama.cpp)
- **Build tools**:
  - Linux/macOS: gcc, make
  - Windows: Visual Studio 2019+ or MinGW
- **8 GB RAM** minimum (16 GB recommended)
- **10-20 GB disk space** for models

### Quick Install

#### On Linux/macOS:
```bash
cd ai-coding-assistant
chmod +x setup.sh
./setup.sh
```

#### On Windows:
```batch
cd ai-coding-assistant
setup.bat
```

The setup script will:
- Check Python version
- Create virtual environment (optional)
- Install dependencies
- Create necessary directories
- Guide you through llama.cpp setup

### Manual Installation

If the setup script doesn't work:

1. **Build llama.cpp:**
```bash
# Linux/macOS
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
cd ..

# Windows
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release
cd ..
```

2. **Download a Model:**
```bash
# Using huggingface-cli (recommended)
pip install huggingface-hub
huggingface-cli download TheBloke/CodeLlama-13B-Instruct-GGUF \
    codellama-13b-instruct.Q4_K_M.gguf \
    --local-dir ./data/models
```

Or download manually from [HuggingFace](https://huggingface.co/TheBloke) and place in `data/models/`

---

## First-Time Setup

### Running Setup

```bash
python src/main.py
```

On first run, you'll be prompted to configure:

### 1. llama.cpp Executable Path

**Linux/macOS:**
```
./llama.cpp/llama-cli
```

**Windows:**
```
llama.cpp\build\bin\Release\llama-cli.exe
```

**Tip:** Use absolute paths if relative paths don't work.

### 2. Model File Path

Example:
```
data/models/codellama-13b-instruct.Q4_K_M.gguf
```

**Tip:** Tab completion may work in terminal.

### 3. Optional Settings

You can accept defaults (press Enter) or customize:

- **Context Size** (default: 4096):
  - 2048 for fast responses
  - 4096 for balanced (recommended)
  - 8192 for complex code

- **Temperature** (default: 0.7):
  - 0.3 for precise, deterministic code
  - 0.7 for balanced
  - 1.0+ for creative solutions

- **Threads** (default: 4):
  - Set to your CPU core count minus 2
  - Check with: `nproc` (Linux) or Task Manager (Windows)

- **GPU Layers** (default: 0):
  - 0 for CPU only
  - 10-20 for partial GPU
  - -1 for full GPU (requires CUDA or Metal)

Configuration is saved to `data/config.json`

---

## Using the CLI

### Starting the CLI

```bash
python src/main.py
# or
./run.sh  # Linux/macOS
run.bat   # Windows
```

### Basic Commands

#### Generate Code

```bash
/gen <language> <description>
```

**Examples:**
```bash
/gen python Create a function to calculate fibonacci numbers with memoization
/gen javascript Create a React component for a todo list with state
/gen cpp Implement a binary search tree with insert and search methods
```

#### Debug Code

```bash
/debug <language> [filename]
```

**Examples:**
```bash
# From file
/debug python my_script.py

# Interactive (paste code)
/debug javascript
# Paste code...
# Ctrl+D (Linux/macOS) or Ctrl+Z (Windows) when done
```

#### Explain Code

```bash
/explain <language>
# Paste code to explain
# Ctrl+D or Ctrl+Z when done
```

#### Optimize Code

```bash
/optimize <language>
# Paste code to optimize
```

#### Refactor Code

```bash
/refactor <language>
# Paste code to refactor
```

#### Provide Feedback

```bash
/feedback <y/n>
```

**Important:** Always provide feedback! It helps the system learn.

```bash
/feedback y    # Code worked perfectly
/feedback n    # Code didn't work or needs improvement
```

#### View Statistics

```bash
/stats
```

Shows:
- Total interactions
- Success rate
- Languages used
- Recent learnings

#### Analyze Errors

```bash
/errors <language>
```

**Examples:**
```bash
/errors python    # Show common Python errors
/errors all       # Show all error patterns
```

#### List Languages

```bash
/languages
```

Shows all supported languages and frameworks.

#### Clear History

```bash
/clear
```

Clears conversation history (not learning database).

#### Help

```bash
/help
```

Shows all available commands.

#### Exit

```bash
/exit
```

or press `Ctrl+C`

### Multi-Line Input

For pasting code:

1. Enter command (e.g., `/debug python`)
2. Paste your code
3. Press:
   - **Linux/macOS:** `Ctrl+D`
   - **Windows:** `Ctrl+Z` then Enter

### File Operations

#### Load Code from File

When prompted for code:
```bash
# Instead of pasting, you can specify file
/debug python myfile.py
```

#### Save Generated Code

After generation:
1. Copy the code block
2. Save to file manually

Or use output redirection:
```bash
python src/main.py > output.txt
```

---

## Using the GUI

### Starting the GUI

```bash
python src/main.py --mode gui
```

### GUI Layout

```
┌─────────────────────────────────────────────┐
│ AI Coding Assistant              [_][□][X] │
├─────────────────────────────────────────────┤
│ Task: [Generate Code ▼]  Language: [Python▼]│
├─────────────────────────────────────────────┤
│ Input:                                      │
│ ┌─────────────────────────────────────────┐ │
│ │ Enter your task or code here...        │ │
│ │                                         │ │
│ │                                         │ │
│ └─────────────────────────────────────────┘ │
│ [Process] [Load File] [Clear Input]        │
├─────────────────────────────────────────────┤
│ Output:                                     │
│ ┌─────────────────────────────────────────┐ │
│ │ Results will appear here...            │ │
│ │                                         │ │
│ │                                         │ │
│ └─────────────────────────────────────────┘ │
│ [Save Output] [Copy] [Clear Output]        │
├─────────────────────────────────────────────┤
│ Status: Ready          [View Stats]        │
└─────────────────────────────────────────────┘
```

### GUI Operations

#### 1. Generate Code
- Select "Generate Code" from Task dropdown
- Choose language
- Enter description in Input area
- Click "Process"
- Wait for results in Output area

#### 2. Debug Code
- Select "Debug Code"
- Choose language
- Paste code in Input area
- Include error message if available
- Click "Process"

#### 3. Load File
- Click "Load File"
- Select file
- Code appears in Input area

#### 4. Save Output
- Click "Save Output"
- Choose location and filename
- Output is saved

#### 5. View Statistics
- Click "View Stats"
- See performance metrics

### GUI Tips

- **Background Processing**: GUI remains responsive during generation
- **Copy/Paste**: Use `Ctrl+C` / `Ctrl+V` as normal
- **Font Size**: May be customizable in future versions
- **Window Size**: Resize window as needed

---

## Core Features

### Code Generation

**What it does:** Creates code from natural language descriptions.

**How to use:**
```bash
/gen python Create a function to parse JSON from a file with error handling
```

**Tips:**
- Be specific about requirements
- Mention frameworks if needed
- Include expected input/output
- Specify error handling needs

**Example Session:**
```bash
> /gen python Create a web scraper for article titles using requests and BeautifulSoup

Generating python code...

[Generated code appears]

def scrape_article_titles(url):
    """
    Scrape article titles from a webpage.
    
    Args:
        url: URL of the page to scrape
        
    Returns:
        List of article titles
    """
    import requests
    from bs4 import BeautifulSoup
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        titles = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])]
        
        return titles
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []

Explanation: This function uses requests to fetch the webpage and
BeautifulSoup to parse HTML...

> /feedback y
```

### Code Debugging

**What it does:** Identifies and fixes errors in code.

**How to use:**
```bash
/debug python
# Paste code with error
# Provide error message
```

**Error Types Detected:**
- Syntax errors
- Type errors
- Logic errors
- Runtime errors
- Import errors
- Attribute errors
- Index errors
- Key errors
- Value errors
- Name errors
- File errors
- Permission errors

**Example:**
```bash
> /debug python

Paste your code (Ctrl+D when done):
def calculate_average(numbers):
    return sum(numbers) / len(numbers)

result = calculate_average([])
print(result)

Error message (if any):
ZeroDivisionError: division by zero

Analyzing code...

[Fixed code appears]

def calculate_average(numbers):
    """Calculate average of numbers with error handling."""
    if not numbers:
        return 0  # or raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)

# Safe usage
result = calculate_average([])
print(result)  # Output: 0

Explanation: The error occurred because len([]) is 0, causing division
by zero. Added check for empty list...

> /feedback y
```

### Code Explanation

**What it does:** Explains how code works in plain English.

**How to use:**
```bash
/explain python
# Paste code to explain
```

**Great for:**
- Understanding unfamiliar code
- Learning new patterns
- Code reviews
- Documentation

### Code Optimization

**What it does:** Improves code performance.

**How to use:**
```bash
/optimize python
# Paste code to optimize
```

**Optimizations include:**
- Algorithmic improvements
- Memory usage reduction
- Loop optimization
- Caching strategies
- Database query optimization
- Async/parallel processing

### Code Refactoring

**What it does:** Improves code structure and readability.

**How to use:**
```bash
/refactor python
# Paste code to refactor
```

**Improvements include:**
- Better naming
- Function extraction
- Removing duplication
- Simplifying logic
- Following best practices
- Adding type hints/documentation

---

## Advanced Usage

### Working with Frameworks

**React Example:**
```bash
/gen react Create a todo list component with hooks for state management and localStorage persistence
```

**Django Example:**
```bash
/gen python Create a Django model for a blog post with title, content, author, and timestamps
```

**Express Example:**
```bash
/gen javascript Create an Express.js REST API endpoint for user authentication with JWT
```

### Chaining Operations

1. Generate code
2. Copy output
3. Debug if needed
4. Optimize
5. Get explanation for complex parts

### Using Learning System

The assistant learns from feedback:

**First Time:**
```bash
> /gen python Create a function with default argument
# Might generate: def func(items=[]):
> /feedback n
# Explain: Don't use mutable default arguments
```

**Next Time:**
```bash
> /gen python Create another function with default argument
# Now generates: def func(items=None):
#                    if items is None:
#                        items = []
```

### Viewing Learning Progress

```bash
> /stats

Statistics:
- Total Interactions: 150
- Success Rate: 87%
- Most Used Languages: python (60), javascript (40), cpp (30)
- Recent Improvements: 15 error patterns learned

> /errors python

Common Python Errors:
1. Using mutable default arguments
   Solution: Use None and initialize in function
   Occurrences: 5

2. Not handling exceptions
   Solution: Add try/except blocks
   Occurrences: 8
```

---

## Tips and Best Practices

### Writing Good Prompts

**❌ Too Vague:**
```bash
/gen python make a function
```

**✅ Specific:**
```bash
/gen python Create a function to validate email addresses using regex, returning True for valid emails and False otherwise
```

**✅ Even Better:**
```bash
/gen python Create a function to validate email addresses using regex. Should handle common formats like user@domain.com and user+tag@domain.co.uk. Include type hints and docstring. Return True for valid, False for invalid.
```

### Mentioning Frameworks

Always mention the framework:
- "Create a React component" not "Create a JavaScript component"
- "Write a Flask route" not "Write a Python web endpoint"
- "Make a Bash script" not "Write a shell script"

### Providing Context

Include:
- Expected input format
- Desired output format
- Error handling requirements
- Performance constraints
- Coding style preferences

### Using Feedback Effectively

**When to use `/feedback y`:**
- Code works perfectly
- Explanation is clear
- Fix resolved the issue

**When to use `/feedback n`:**
- Code has bugs
- Missing important features
- Explanation is unclear
- Better solution exists

**After `/feedback n`, explain:**
```bash
> /feedback n
# System asks: What went wrong?
> The function doesn't handle edge cases like negative numbers
```

### Performance Tips

**For Faster Responses:**
1. Use smaller model (7B instead of 13B)
2. Reduce context_size in config (2048)
3. Use more CPU threads
4. Enable GPU if available

**For Better Quality:**
1. Use larger model (13B)
2. Increase context_size (8192)
3. Provide more detailed prompts
4. Give feedback consistently

---

## Troubleshooting

### Common Issues

#### "llama.cpp executable not found"

**Solution:**
1. Check the path in `data/config.json`
2. Verify llama.cpp is built: `./llama.cpp/llama-cli --version`
3. Use absolute path if relative doesn't work
4. On Windows, ensure `.exe` extension

#### "Model file not found"

**Solution:**
1. Check path in `data/config.json`
2. Verify file exists: `ls data/models/`
3. Ensure file has `.gguf` extension
4. Download model if missing

#### "Generation is very slow"

**Solution:**
1. Reduce `context_size` to 2048 in `data/config.json`
2. Use smaller model (7B)
3. Increase `threads` to match CPU cores
4. Close other applications
5. Enable GPU if available

#### "Out of memory error"

**Solution:**
1. Use smaller model
2. Use higher quantization (Q4_0 instead of Q4_K_M)
3. Reduce `context_size`
4. Close other applications
5. Restart computer

#### "Generation times out"

**Solution:**
1. Increase `timeout` in config (to 300)
2. Reduce `max_tokens`
3. Check CPU usage (Task Manager/htop)
4. Verify model is compatible with llama.cpp version

#### "Gibberish output"

**Solution:**
1. Verify model is for coding (CodeLlama, DeepSeek Coder)
2. Check temperature (should be 0.1-1.0)
3. Ensure model file isn't corrupted
4. Try different model

#### "Database locked" error

**Solution:**
1. Close other instances of the app
2. Check file permissions on `data/db/`
3. Restart application
4. If persistent, delete `data/db/learning.db` (loses history)

### Getting Help

1. **Check error message carefully**
2. **Run diagnostics:**
   ```bash
   python src/main.py --check
   ```
3. **Test llama.cpp independently:**
   ```bash
   ./llama.cpp/llama-cli -m data/models/model.gguf -p "Hello"
   ```
4. **Check logs** (if logging enabled)
5. **Review README troubleshooting section**
6. **Open GitHub issue** with:
   - Error message
   - Operating system
   - Python version
   - Model being used
   - Config file (remove sensitive info)

---

## FAQ

### General Questions

**Q: Is my code sent to the internet?**  
A: No! All processing happens locally on your machine. Nothing is sent externally.

**Q: Which model should I use?**  
A: For coding: CodeLlama 13B Instruct or DeepSeek Coder 6.7B. For general: Llama 3 8B.

**Q: Can I use multiple models?**  
A: Not simultaneously, but you can change the model in `data/config.json`.

**Q: How much disk space do I need?**  
A: About 10-20 GB: 50 MB for app + 4-8 GB per model + space for llama.cpp.

**Q: Does it work offline?**  
A: Yes! Once setup, it works completely offline.

**Q: Can I use it for commercial projects?**  
A: Yes! MIT license. Check individual model licenses too.

### Usage Questions

**Q: How do I save generated code?**  
A: Copy from terminal/GUI and paste into your editor. Or use output redirection.

**Q: Can it generate entire applications?**  
A: It works best for functions/classes. For whole apps, generate piece by piece.

**Q: Does it remember previous conversations?**  
A: It learns from past interactions but doesn't maintain conversation context between sessions.

**Q: How do I reset if it learns something wrong?**  
A: Use `/clear` for conversation, or delete `data/db/learning.db` to reset all learning.

**Q: Can multiple people share the learning database?**  
A: Technically yes, but not recommended. Each user should have their own.

### Technical Questions

**Q: Why llama.cpp instead of transformers library?**  
A: llama.cpp is much more efficient and doesn't require PyTorch/TensorFlow.

**Q: Can I fine-tune the model?**  
A: Not directly with this tool. You'd need to fine-tune externally and use the new model.

**Q: Does it support GPU acceleration?**  
A: Yes! Set `gpu_layers` in config. Requires CUDA (NVIDIA) or Metal (Apple Silicon).

**Q: What's the context limit?**  
A: Depends on model. Usually 2048-8192 tokens. Set in `context_size` config.

**Q: Can I add more languages?**  
A: Yes! See `docs/EXTENDING_GUIDE.md` for instructions.

---

## Keyboard Shortcuts

### CLI
- **Ctrl+C**: Exit application
- **Ctrl+D**: End multi-line input (Linux/macOS)
- **Ctrl+Z + Enter**: End multi-line input (Windows)
- **Up/Down Arrow**: Command history (if supported by terminal)

### GUI
- **Ctrl+C**: Copy
- **Ctrl+V**: Paste
- **Ctrl+A**: Select all
- **Ctrl+Z**: Undo (in text areas)

---

## Configuration Reference

Located at: `data/config.json`

### All Options

```json
{
  "model_path": "data/models/model.gguf",
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

See `USER_PREFERENCES.md` for detailed explanations.

---

## Support

- **Documentation**: Check `docs/` folder
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@aicodingassistant.com (if available)

---

## What's Next?

1. **Explore Features**: Try all commands
2. **Provide Feedback**: Help the system learn
3. **Check Statistics**: Monitor your progress
4. **Read Advanced Docs**: `docs/API.md`, `docs/EXTENDING_GUIDE.md`
5. **Customize**: Edit prompts, add languages
6. **Contribute**: See `CONTRIBUTING.md`

---

**Enjoy coding with your AI assistant!** 🚀

**Last Updated:** October 16, 2025  
**Version:** 1.0.0

For quick reference, see `docs/QUICKSTART.md`
