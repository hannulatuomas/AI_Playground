# UAIDE Scripts - One-Click Workflow

This directory contains scripts for easy setup, testing, and running of UAIDE.

## 🚀 Quick Start (One-Click)

### First Time Setup
Just run:
```bash
scripts\setup_venv.bat
```

This **single command** will:
1. ✅ Create virtual environment
2. ✅ Install all Python dependencies
3. ✅ Create necessary directories (data/, logs/, llama-cpp/, llama-cpp/models/)
4. ✅ Create config.json from config.example.json
5. ✅ Initialize the database with all tables

**Then:**
1. Download llama.cpp binary (see [llama.cpp Setup Guide](../docs/LLAMA_CPP_SETUP.md))
2. Place binary in `llama-cpp/` directory
3. Download AI model (.gguf) and place in `llama-cpp/models/`
4. Update `config.json` with model path

**That's it!** Everything is ready to use.

---

## 📜 Available Scripts

### `setup_venv.bat` - Complete Setup
**One-click installation of everything.**

```bash
scripts\setup_venv.bat
```

Runs the complete setup process. Safe to run multiple times (skips existing venv).

---

### `run_uaide.bat` - Run UAIDE
**Auto-setup if needed, then run UAIDE.**

```bash
# Show help
scripts\run_uaide.bat --help

# Initialize UAIDE
scripts\run_uaide.bat init

# Check status
scripts\run_uaide.bat status

# Create new project
scripts\run_uaide.bat new-project myapp --language python

# Interactive chat
scripts\run_uaide.bat chat
```

**Smart Features:**
- ✅ Auto-runs setup if venv doesn't exist
- ✅ Activates/deactivates venv automatically
- ✅ Passes all arguments to UAIDE
- ✅ Returns proper exit codes

---

### `run_tests.bat` - Run Tests
**Auto-setup if needed, then run all tests.**

```bash
scripts\run_tests.bat
```

**Features:**
- ✅ Auto-runs setup if venv doesn't exist
- ✅ Runs pytest with verbose output
- ✅ Shows test results
- ✅ Returns proper exit codes

---

### `run_tests_coverage.bat` - Run Tests with Coverage
**Auto-setup if needed, then run tests with coverage analysis.**

```bash
scripts\run_tests_coverage.bat
```

**Features:**
- ✅ Auto-runs setup if venv doesn't exist
- ✅ Generates HTML coverage report
- ✅ Shows coverage statistics
- ✅ Opens coverage report in browser

---

### `quick_test_phase2.bat` - Quick Phase 2 Tests
**Run only Phase 2 module tests (faster).**

```bash
scripts\quick_test_phase2.bat
```

**Features:**
- ✅ Tests Project Manager module
- ✅ Tests Code Generator module
- ✅ Tests Tester module
- ✅ Faster than full test suite

---

### `demo_phase2.bat` - Phase 2 Demo
**Interactive demo of Phase 2 features.**

```bash
scripts\demo_phase2.bat
```

**Features:**
- ✅ Demonstrates Project Manager
- ✅ Demonstrates Code Generator
- ✅ Demonstrates Tester module
- ✅ Shows real-time feature detection

---

## 🎯 Typical Workflow

### Brand New Project
```bash
# 1. Clone repository
git clone <repo-url>
cd Ultimate_AI_IDE

# 2. One-click setup (only needed once)
scripts\setup_venv.bat

# 3. Download AI model and place in models/

# 4. Start using UAIDE
scripts\run_uaide.bat init
scripts\run_uaide.bat status
```

### Daily Development
```bash
# Run tests
scripts\run_tests.bat

# Run UAIDE
scripts\run_uaide.bat [command]

# No need to worry about venv activation!
```

---

## 🔧 What Each Script Does

### `setup_venv.bat`
1. Checks Python version
2. Creates venv (if doesn't exist)
3. Activates venv
4. Upgrades pip
5. Installs requirements.txt
6. Runs setup.py (creates dirs, config, initializes DB)
7. Deactivates venv

### `run_uaide.bat`
1. Checks if venv exists (auto-setup if not)
2. Activates venv
3. Runs `python src\main.py` with your arguments
4. Deactivates venv
5. Returns exit code

### `run_tests.bat`
1. Checks if venv exists (auto-setup if not)
2. Activates venv
3. Runs `pytest tests/ -v --tb=short`
4. Deactivates venv
5. Returns exit code

### `run_tests_coverage.bat`
1. Checks if venv exists (auto-setup if not)
2. Activates venv
3. Runs pytest with coverage
4. Generates HTML report in `htmlcov/`
5. Deactivates venv
6. Returns exit code

---

## 💡 Key Features

### ✅ True One-Click
- No manual venv activation needed
- No manual dependency installation needed
- No manual database setup needed
- Just run the script!

### ✅ Auto-Setup
- `run_uaide.bat` and `run_tests.bat` automatically run setup if venv is missing
- Safe to use on fresh clone
- Safe to use after deleting venv

### ✅ Smart
- Skips venv creation if already exists
- Skips config creation if already exists
- Proper error handling
- Clear status messages

### ✅ Clean
- Auto-activates and deactivates venv
- No lingering activated environments
- Proper exit codes for CI/CD

---

## 🛠️ Manual Operations (Optional)

If you prefer manual control:

```bash
# Activate venv manually
venv\Scripts\activate.bat

# Run UAIDE directly
python src\main.py --help

# Run tests directly
pytest tests/ -v

# Deactivate venv
deactivate
```

But the scripts handle all this for you! 🎉

---

## 📋 Requirements

- Python 3.12.10 or higher
- pip package manager
- Windows OS (for .bat files)

---

## 🐛 Troubleshooting

**Problem:** "Virtual environment not found"
**Solution:** Just run the script again - it will auto-setup!

**Problem:** "Python is not installed or not in PATH"
**Solution:** Install Python 3.12+ and add to PATH

**Problem:** "Failed to install dependencies"
**Solution:** Check internet connection, ensure pip is working

**Problem:** Tests fail
**Solution:** Run `scripts\run_tests.bat` to see detailed error messages

---

## 📝 Notes

- All scripts handle venv activation/deactivation automatically
- All scripts return proper exit codes for automation
- All scripts are safe to run multiple times
- The `setup.py` is integrated into `setup_venv.bat` - no need to run it separately

---

**Everything is designed for one-click simplicity!** 🚀
