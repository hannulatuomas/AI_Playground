# Quickstart Guide

## Installation

### 1. Run Setup Script

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```bash
setup.bat
```

The setup script will:
- Create virtual environment
- Install dependencies
- Check for llama.cpp and models
- Create necessary directories

### 2. Download a Model

Download a GGUF model file. Recommended options:

**For general coding (7-13B parameters):**
- Llama 3 8B Instruct
- CodeLlama 13B Instruct
- DeepSeek Coder 6.7B

**Where to download:**
- https://huggingface.co/TheBloke (search for GGUF models)
- Look for Q4_K_M quantization (good balance of speed/quality)

```bash
# Example: Download using huggingface-cli
huggingface-cli download TheBloke/CodeLlama-13B-Instruct-GGUF codellama-13b-instruct.Q4_K_M.gguf --local-dir ./models
```

Place the downloaded .gguf file in `ai-coding-assistant/data/models/`

### 3. Get llama.cpp

**Option A: Download Pre-built (Recommended)**
- Visit https://github.com/ggerganov/llama.cpp/releases
- Download for your OS
- Extract to `llama.cpp/` folder

**Option B: Build from Source**
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make  # Linux/macOS
# Or use cmake for Windows
```

### 4. Run the Application

**Linux/macOS:**
```bash
./run.sh
```

**Windows:**
```bash
run.bat
```

Configuration is stored in `data/config.json`

## Basic Usage

### Generate Code

```bash
> /gen python Create a function to read a CSV file and return a pandas DataFrame
```

### Debug Code

```bash
> /debug python
# Paste your code
# Provide error message when prompted
```

### Explain Code

```bash
> /explain javascript
# Paste code to explain
```

### Other Commands

```bash
> /help          # Show all commands
> /languages     # List supported languages
> /stats         # Show learning statistics
> /feedback y    # Mark last response as helpful
```

## Example Session

```
> /gen python Create a function to calculate factorial with recursion

Generating python code...

Generated code:

```python
def factorial(n: int) -> int:
    """
    Calculate factorial of n using recursion.
    
    Args:
        n: Non-negative integer
        
    Returns:
        Factorial of n
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
```

Explanation:
This function calculates factorial recursively with proper error handling
and type hints. It includes a base case for 0 and 1, and handles negative
inputs appropriately.

Was this helpful? Use /feedback <y/n> to provide feedback

> /feedback y

Great! Glad it worked.
```

## Tips

1. **Be Specific**: More detailed prompts get better results
   - Good: "Create a Python function to parse JSON and handle errors"
   - Better: "Create a Python function to parse JSON from a file, handle FileNotFoundError and JSONDecodeError, and return None on errors"

2. **Provide Context**: Mention frameworks/libraries
   - "Create a React component..." (not just "JavaScript component")
   - "Write a bash script for Linux..." (not just "shell script")

3. **Use Feedback**: The system learns from your feedback
   - Always use `/feedback y` when code works
   - Use `/feedback n` and explain what went wrong

4. **Check Error Patterns**: Learn from mistakes
   ```bash
   > /errors python
   ```

5. **Start Small**: Test with simple tasks first
   - Generate a hello world
   - Debug simple syntax errors
   - Then move to complex tasks

## Troubleshooting Quick Fixes

**"llama.cpp executable not found"**
```bash
# Update config with correct path
# On Linux/macOS: ./llama.cpp/llama-cli
# On Windows: ./llama.cpp/build/bin/Release/llama-cli.exe
```

**"Generation is very slow"**
```bash
# Edit data/config.json:
# Reduce "context_size" to 2048
# Use a smaller model (7B instead of 13B)
# Increase "threads" to match your CPU cores
```

**"Out of memory error"**
```bash
# Use a smaller model
# Use higher quantization (Q4_0 instead of Q4_K_M)
# Reduce context_size
```

## Running Tests

**Linux/macOS:**
```bash
./run_tests.sh
```

**Windows:**
```bash
run_tests.bat
```

## Next Steps

- Read the full [User Guide](USER_GUIDE.md)
- Review [API Documentation](API.md)
- Review [README.md](../README.md) for detailed features
- Try the GUI: `python src/main.py --mode gui` (coming soon)

## Getting Help

- Check error messages carefully
- Review configuration in `data/config.json`
- Test llama.cpp independently
- Check that model file is valid GGUF format
- Review logs and statistics with `/stats`

Happy coding!
