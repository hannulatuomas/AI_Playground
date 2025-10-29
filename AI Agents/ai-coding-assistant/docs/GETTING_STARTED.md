# Getting Started with AI Coding Assistant

## 🚀 Complete Setup Guide

This guide will walk you through setting up and using the AI Coding Assistant from scratch.

---

## Step 1: Prerequisites

### Required
- **Python 3.8+** (Python 3.12 recommended)
- **Git** (for cloning llama.cpp)
- **Build tools**:
  - Linux/macOS: gcc, make
  - Windows: Visual Studio or MinGW

### Check Your Setup
```bash
python --version    # Should show 3.8 or higher
git --version      # Should show git version
```

---

## Step 2: Download the Project

If you have the project:
```bash
cd ai-coding-assistant
```

---

## Step 3: Run Setup Script

### On Linux/macOS:
```bash
chmod +x setup.sh
./setup.sh
```

### On Windows:
```bash
setup.bat
```

The setup script will:
- ✅ Check Python version
- ✅ Create virtual environment (optional)
- ✅ Install dependencies
- ✅ Create necessary directories
- ✅ Offer to clone and build llama.cpp

---

## Step 4: Build llama.cpp

### Option A: Automatic (via setup script)
The setup script can do this for you automatically.

### Option B: Manual

#### Linux/macOS:
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
cd ..
```

#### Windows:
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release
cd ..
```

---

## Step 5: Download a Model

### Recommended Models

**For Code Generation (Best):**
- **CodeLlama 13B Instruct** (7-8 GB)
- **DeepSeek Coder 6.7B** (4-5 GB)

**For General Use:**
- **Llama 3 8B Instruct** (4-5 GB)

### Where to Download

1. Go to https://huggingface.co/TheBloke
2. Search for: `CodeLlama-13B-Instruct-GGUF`
3. Download the **Q4_K_M** version (best balance)
4. Place in: `ai-coding-assistant/data/models/`

### Using huggingface-cli (Recommended):
```bash
# Install huggingface-cli
pip install huggingface-hub

# Download CodeLlama 13B
huggingface-cli download TheBloke/CodeLlama-13B-Instruct-GGUF \
    codellama-13b-instruct.Q4_K_M.gguf \
    --local-dir ./data/models
```

### Using wget/curl:
Find the download link on HuggingFace and:
```bash
cd data/models
wget [download-url]
# or
curl -O [download-url]
```

---

## Step 6: First Run & Configuration

### Start the Assistant
```bash
# Using run script
./run.sh      # Linux/macOS
run.bat       # Windows

# Or directly
python src/main.py
```

### Configuration Prompts

You'll be asked for:

1. **llama.cpp executable path**
   - Linux/macOS: `./llama.cpp/llama-cli`
   - Windows: `.\llama.cpp\build\bin\Release\llama-cli.exe`

2. **Model file path**
   - Example: `./data/models/codellama-13b-instruct.Q4_K_M.gguf`

3. **Optional settings** (press Enter for defaults):
   - Context size: `4096` (default is fine)
   - Temperature: `0.7` (default is fine)
   - Threads: `4` (or your CPU core count)
   - GPU layers: `0` (set higher if you have compatible GPU)

Configuration is saved to `data/config.json`

---

## Step 7: Test the Assistant

### Try Your First Command

```bash
> /gen python Create a function to calculate fibonacci numbers with memoization
```

You should see generated code with explanation!

---

## Basic Commands Reference

### Code Generation
```bash
/gen <language> <description>
```
Examples:
```bash
/gen python Create a web scraper using requests
/gen react Create a todo list component
/gen cpp Implement a binary search tree
```

### Debugging
```bash
/debug <language> [filename]
```
Examples:
```bash
/debug python mycode.py
/debug javascript
# Then paste code and error message
```

### Code Operations
```bash
/explain <language>    # Explain code (paste after)
/optimize <language>   # Optimize code (paste after)
/refactor <language>   # Refactor code (paste after)
```

### Information
```bash
/help          # Show all commands
/languages     # List supported languages
/stats         # Show learning statistics
/errors python # Show common Python errors
```

### Feedback (Important!)
```bash
/feedback y    # Mark last response as good
/feedback n    # Mark as not good (will ask for details)
```

---

## Example Session

```
============================================================
  Ultimate AI Coding Assistant
============================================================

Initializing components...
Testing LLM connection...
✓ Initialization successful!

> /gen python Create a function to read a CSV and return top 10 rows

Generating python code...

Generated code:

```python
import csv
from typing import List, Dict

def read_csv_top_rows(filename: str, n: int = 10) -> List[Dict[str, str]]:
    """
    Read a CSV file and return the top n rows.
    
    Args:
        filename: Path to the CSV file
        n: Number of rows to return (default: 10)
        
    Returns:
        List of dictionaries representing rows
    """
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for i, row in enumerate(reader) if i < n]
```

Explanation:
This function uses Python's csv module to read a CSV file safely...

Was this helpful? Use /feedback <y/n> to provide feedback

> /feedback y

Great! Glad it worked.

> /exit

Goodbye!
```

---

## Tips for Best Results

### 1. Be Specific
❌ Bad: "Create a function"
✅ Good: "Create a Python function to parse JSON from a file with error handling"

### 2. Mention Frameworks
❌ Bad: "Create a web form"
✅ Good: "Create a React form component with validation"

### 3. Always Give Feedback
- Use `/feedback y` when code works
- Use `/feedback n` when it doesn't (and explain why)
- This helps the system learn and improve

### 4. Check Error Patterns
```bash
/errors python
```
See what mistakes are common and learn from them

### 5. Start Simple
- Test with "hello world" first
- Then try more complex tasks
- Build confidence with the system

---

## Troubleshooting

### "llama.cpp executable not found"
- Check the path in `data/config.json`
- Verify llama.cpp is built: `./llama.cpp/llama-cli --version`
- Use absolute paths if relative paths don't work

### "Model file not found"
- Check the path in `data/config.json`
- Verify file exists: `ls data/models/`
- Check file extension is `.gguf`

### "Generation is too slow"
Edit `data/config.json`:
- Reduce `context_size` to `2048`
- Reduce max tokens
- Use a smaller model

### "Out of memory"
- Use a smaller model (7B instead of 13B)
- Use higher quantization (Q4_0 instead of Q4_K_M)
- Close other applications

### "Python module not found"
```bash
pip install -r requirements.txt
```

---

## Next Steps

1. **Explore Commands**: Try all the different commands
2. **Read API Docs**: Check `docs/API.md` for advanced usage
3. **Customize**: Edit prompts in `src/core/prompt_engine.py`
4. **Extend**: Add new languages or features
5. **Contribute**: See `CONTRIBUTING.md`

---

## GUI Mode (Optional)

Want a graphical interface?

```bash
python src/main.py --mode gui
```

---

## Getting Help

- Check `README.md` for full documentation
- Review `docs/API.md` for API reference
- See `docs/QUICKSTART.md` for quick reference
- Check error messages carefully
- Use `/help` command in CLI

---

## Summary Checklist

- [ ] Python 3.8+ installed
- [ ] Project downloaded/extracted
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] llama.cpp built
- [ ] Model downloaded and placed in `data/models/`
- [ ] First run completed and configured
- [ ] Test generation successful
- [ ] Read this guide

**You're ready to code with AI assistance! 🎉**

Happy coding!
