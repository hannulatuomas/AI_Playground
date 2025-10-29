# Quick Reference - Setup and Run Scripts

**AI Coding Assistant v1.0.1**

---

## 🚀 Quick Start

### First Time Setup

**Windows:**
```batch
setup.bat
```

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

### Run Application

**Windows:**
```batch
run.bat
```

**Linux/macOS:**
```bash
./run.sh
```

### Run Tests

**Windows:**
```batch
run_tests.bat
```

**Linux/macOS:**
```bash
./run_tests.sh
```

---

## 📋 Script Details

### setup.bat / setup.sh

**Purpose:** Automated environment setup

**What it does:**
- ✅ Checks Python version (3.12.10 recommended)
- ✅ Creates virtual environment
- ✅ Upgrades pip
- ✅ Installs dependencies
- ✅ Creates necessary directories
- ✅ Checks for llama.cpp
- ✅ Checks for models
- ✅ Creates config file

**When to use:**
- First time installation
- After cloning repository
- When dependencies change
- To recreate environment

**Time:** 2-3 minutes

---

### run.bat / run.sh

**Purpose:** Launch the AI Coding Assistant

**What it does:**
- ✅ Checks virtual environment exists
- ✅ Activates virtual environment
- ✅ Verifies main script exists
- ✅ Runs the application
- ✅ Reports errors clearly

**When to use:**
- Every time you want to use the app
- Instead of manual venv activation + python command

**With arguments:**
```batch
# Windows
run.bat --help
run.bat --mode gui

# Linux/macOS
./run.sh --help
./run.sh --mode gui
```

**Time:** Instant

---

### run_tests.bat / run_tests.sh

**Purpose:** Run all tests

**What it does:**
- ✅ Checks virtual environment exists
- ✅ Activates virtual environment
- ✅ Discovers all test files
- ✅ Runs tests with verbose output
- ✅ Reports results

**When to use:**
- After making changes
- Before committing code
- To verify installation
- Regular quality checks

**Output:** Detailed test results with pass/fail

**Time:** 10-30 seconds

---

## 🔧 Common Scenarios

### Scenario 1: Brand New Installation

```batch
# 1. Clone or extract project
cd ai-coding-assistant

# 2. Run setup
setup.bat          # Windows
./setup.sh         # Linux/macOS

# 3. Download model (if needed)
# Place .gguf file in data/models/

# 4. Get llama.cpp (if needed)
# Extract to llama.cpp/ folder

# 5. Run the app
run.bat            # Windows
./run.sh           # Linux/macOS
```

---

### Scenario 2: Daily Usage

```batch
# Just run it!
run.bat            # Windows
./run.sh           # Linux/macOS
```

---

### Scenario 3: After Pulling Updates

```batch
# 1. Pull changes
git pull

# 2. Update dependencies (if requirements.txt changed)
setup.bat          # Windows
./setup.sh         # Linux/macOS

# 3. Run tests to verify
run_tests.bat      # Windows
./run_tests.sh     # Linux/macOS

# 4. Use the app
run.bat            # Windows
./run.sh           # Linux/macOS
```

---

### Scenario 4: Development Workflow

```batch
# 1. Make changes to code
# ... edit files ...

# 2. Run tests
run_tests.bat      # Windows
./run_tests.sh     # Linux/macOS

# 3. Test the app
run.bat            # Windows
./run.sh           # Linux/macOS

# 4. Commit if tests pass
git add .
git commit -m "Your changes"
```

---

## ❗ Troubleshooting

### "Virtual environment not found"

**Solution:**
```batch
# Run setup first
setup.bat          # Windows
./setup.sh         # Linux/macOS
```

---

### "Python is not installed"

**Solution:**
1. Install Python 3.12.10 from python.org
2. Add Python to PATH
3. Restart terminal
4. Run setup again

---

### "llama.cpp executable not found"

**Solution:**
1. Download llama.cpp from GitHub releases
2. Extract to `llama.cpp/` folder
3. Or build from source (see README)
4. Run app again

---

### "No model files found"

**Solution:**
1. Download a GGUF model
2. Place in `data/models/` folder
3. Edit `data/config.json` if needed
4. Run app again

---

### "Permission denied" (Linux/macOS)

**Solution:**
```bash
# Make scripts executable
chmod +x setup.sh run.sh run_tests.sh

# Then run normally
./setup.sh
```

---

### "Tests failed"

**Solution:**
1. Check error messages carefully
2. Ensure dependencies installed correctly
3. Try re-running setup
4. Check if models/llama.cpp are configured

---

## 💡 Tips & Tricks

### Tip 1: Check Everything is Working

```batch
# Windows
setup.bat
run_tests.bat

# Linux/macOS
./setup.sh
./run_tests.sh
```

If both complete without errors, you're good to go!

---

### Tip 2: Quick Validation

```batch
# Run setup to validate environment
setup.bat          # Windows
./setup.sh         # Linux/macOS
```

Setup script checks everything and tells you what's missing.

---

### Tip 3: Clean Reinstall

```batch
# 1. Delete virtual environment
rmdir /s venv      # Windows
rm -rf venv        # Linux/macOS

# 2. Run setup again
setup.bat          # Windows
./setup.sh         # Linux/macOS
```

---

### Tip 4: Pass Arguments to App

```batch
# Examples
run.bat --help
run.bat --mode gui
run.bat --verbose

# Linux/macOS
./run.sh --help
./run.sh --mode gui
./run.sh --verbose
```

---

### Tip 5: Specific Test Files

For more control, activate venv and run tests directly:

```batch
# Windows
venv\Scripts\activate
python -m unittest tests.test_core -v

# Linux/macOS
source venv/bin/activate
python -m unittest tests.test_core -v
```

---

## 📊 Script Comparison

| Feature | setup | run | run_tests |
|---------|-------|-----|-----------|
| Creates venv | ✅ | ❌ | ❌ |
| Activates venv | ✅ | ✅ | ✅ |
| Installs deps | ✅ | ❌ | ❌ |
| Runs app | ❌ | ✅ | ❌ |
| Runs tests | ❌ | ❌ | ✅ |
| Validates environment | ✅ | ✅ | ✅ |
| Error handling | ✅ | ✅ | ✅ |
| Time | 2-3 min | Instant | 10-30 sec |

---

## 🎯 Best Practices

### ✅ DO:

1. Run `setup` first before anything else
2. Use `run_tests` after making changes
3. Keep scripts in project root
4. Read error messages carefully
5. Run setup after pulling updates

### ❌ DON'T:

1. Manually activate venv (use run scripts instead)
2. Delete scripts (they're essential)
3. Ignore error messages
4. Skip running tests
5. Modify scripts without backing up

---

## 📖 Manual Alternative

If you prefer manual control:

```batch
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src\main.py

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

But scripts are easier! 😊

---

## 🔗 Quick Links

- **Full Documentation:** README.md
- **Quick Start Guide:** docs/QUICKSTART.md
- **User Guide:** docs/USER_GUIDE.md
- **API Docs:** docs/API.md
- **Contributing:** CONTRIBUTING.md

---

## 📝 Summary

**Three commands, that's it:**

1. **setup.bat / setup.sh** - Run once to set up
2. **run.bat / run.sh** - Run every time to use app
3. **run_tests.bat / run_tests.sh** - Run to verify everything works

Simple, easy, reliable! 🚀

---

**Version:** 1.0.1  
**Last Updated:** January 16, 2025  
**Status:** Production Ready ✅
