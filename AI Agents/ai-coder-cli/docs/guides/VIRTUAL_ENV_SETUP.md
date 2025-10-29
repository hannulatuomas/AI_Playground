
# Virtual Environment Setup Guide

**Version:** 2.5.0  
**Last Updated:** October 13, 2025  
**Status:** ✅ Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Why Use a Virtual Environment?](#why-use-a-virtual-environment)
3. [Quick Start](#quick-start)
4. [Platform-Specific Instructions](#platform-specific-instructions)
5. [Manual Setup](#manual-setup)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## Overview

This guide provides comprehensive instructions for setting up and using Python virtual environments with the AI Agent Console project. Virtual environments are essential for managing Python dependencies and ensuring consistent development environments across different systems.

---

## Why Use a Virtual Environment?

Virtual environments provide several key benefits:

1. **Dependency Isolation**: Keep project dependencies separate from system Python packages
2. **Version Control**: Install specific package versions without affecting other projects
3. **Reproducibility**: Ensure consistent environments across development, testing, and production
4. **Clean Environment**: Avoid conflicts between different projects' dependencies
5. **Easy Cleanup**: Simply delete the virtual environment directory to remove all packages

---

## Quick Start

### Linux/macOS

```bash
# Make the setup script executable
chmod +x setup_venv.sh

# Run the setup script
./setup_venv.sh

# For development (includes testing, linting tools)
./setup_venv.sh --dev

# Activate the virtual environment
source venv/bin/activate
# or
source ./activate_venv.sh

# Deactivate when done
deactivate
```

### Windows (Command Prompt)

```cmd
REM Run the setup script
setup_venv.bat

REM For development
setup_venv.bat --dev

REM Activate the virtual environment
venv\Scripts\activate.bat
REM or
activate_venv.bat

REM Deactivate when done
deactivate
```

### Windows (PowerShell)

```powershell
# You may need to enable script execution first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the setup script
.\setup_venv.ps1

# For development
.\setup_venv.ps1 -Dev

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
# or
.\activate_venv.ps1

# Deactivate when done
deactivate
```

---

## Platform-Specific Instructions

### Linux/macOS Setup

#### Prerequisites

- Python 3.9 or higher
- pip (usually comes with Python)
- bash shell

#### Installation Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd /path/to/ai-agent-console
   ```

2. **Run the setup script**:
   ```bash
   chmod +x setup_venv.sh
   ./setup_venv.sh
   ```

3. **The script will**:
   - Check Python version (requires 3.9+)
   - Create a virtual environment in the `venv` directory
   - Upgrade pip, setuptools, and wheel
   - Install all required dependencies from `requirements.txt`
   - Verify the installation
   - Create a helper activation script

4. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

5. **Verify activation**:
   ```bash
   which python
   # Should show: /path/to/ai-agent-console/venv/bin/python
   
   python --version
   # Should show Python 3.9 or higher
   ```

### Windows Setup (Command Prompt)

#### Prerequisites

- Python 3.9 or higher
- pip (usually comes with Python)
- Command Prompt or PowerShell

#### Installation Steps

1. **Navigate to the project directory**:
   ```cmd
   cd C:\path\to\ai-agent-console
   ```

2. **Run the setup script**:
   ```cmd
   setup_venv.bat
   ```

3. **Activate the virtual environment**:
   ```cmd
   venv\Scripts\activate.bat
   ```

4. **Verify activation**:
   ```cmd
   where python
   REM Should show: C:\path\to\ai-agent-console\venv\Scripts\python.exe
   ```

### Windows Setup (PowerShell)

#### Prerequisites

- Python 3.9 or higher
- pip (usually comes with Python)
- PowerShell 5.1 or PowerShell Core 7+

#### Enable Script Execution (First Time Only)

PowerShell has security policies that may prevent scripts from running. Enable script execution:

```powershell
# Check current policy
Get-ExecutionPolicy

# If it's "Restricted", change it:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Installation Steps

1. **Navigate to the project directory**:
   ```powershell
   cd C:\path\to\ai-agent-console
   ```

2. **Run the setup script**:
   ```powershell
   .\setup_venv.ps1
   ```

3. **Activate the virtual environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Verify activation**:
   ```powershell
   Get-Command python | Select-Object Source
   # Should show: C:\path\to\ai-agent-console\venv\Scripts\python.exe
   ```

---

## Manual Setup

If you prefer to set up the virtual environment manually or the automated scripts don't work:

### 1. Create Virtual Environment

```bash
# Linux/macOS
python3 -m venv venv

# Windows
python -m venv venv
```

### 2. Activate Virtual Environment

```bash
# Linux/macOS
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Upgrade Core Tools

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 4. Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (optional)
pip install -r requirements-dev.txt
```

### 5. Verify Installation

```bash
# Check Python version
python --version

# Check pip version
pip --version

# Verify core dependencies
python -c "import typer; import pydantic; import yaml; import ollama; print('All core dependencies imported successfully!')"
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Python Not Found

**Problem**: `python` or `python3` command not found

**Solution**:
- Ensure Python is installed
- Add Python to your PATH environment variable
- On Windows, run the Python installer again and check "Add Python to PATH"

#### 2. Permission Denied (Linux/macOS)

**Problem**: Cannot execute setup script

**Solution**:
```bash
chmod +x setup_venv.sh
```

#### 3. Script Execution Disabled (Windows PowerShell)

**Problem**: PowerShell won't run the script

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 4. Virtual Environment Already Exists

**Problem**: The setup script warns that `venv` already exists

**Solution**:
- The script will ask if you want to recreate it
- Choose 'y' to recreate or 'n' to keep the existing one
- Or manually delete the `venv` directory and run setup again:
  ```bash
  rm -rf venv  # Linux/macOS
  rmdir /s /q venv  # Windows
  ```

#### 5. Package Installation Fails

**Problem**: pip fails to install some packages

**Solutions**:
- Ensure you have an active internet connection
- Try upgrading pip: `python -m pip install --upgrade pip`
- For specific packages:
  - **GitPython**: May need git installed on your system
  - **lxml**: May need libxml2 and libxslt development libraries
  - **psycopg2**: May need PostgreSQL development libraries
- On Windows, some packages may require Visual C++ Build Tools

#### 6. Import Errors After Installation

**Problem**: Packages installed but cannot import

**Solution**:
- Ensure the virtual environment is activated
- Verify you're using the correct Python:
  ```bash
  which python  # Linux/macOS
  where python  # Windows
  ```
- Try reinstalling the specific package:
  ```bash
  pip install --force-reinstall <package-name>
  ```

#### 7. Slow Package Installation

**Problem**: pip is taking too long to install packages

**Solutions**:
- Use a faster mirror (if available in your region)
- Install packages in smaller batches
- Consider using `pip install --no-cache-dir` to skip cache

---

## Best Practices

### 1. Always Use Virtual Environments

Never install project dependencies globally. Always create and use a virtual environment for each project.

### 2. Keep Virtual Environments Out of Version Control

The `.gitignore` file already excludes `venv/`, `env/`, and similar directories. Never commit virtual environments to version control.

### 3. Update Requirements Files

When adding new dependencies:

```bash
# Add to requirements.txt manually with specific versions
echo "new-package==1.0.0" >> requirements.txt

# Or regenerate from current environment (not recommended for production)
pip freeze > requirements-current.txt
```

### 4. Regular Updates

Periodically update dependencies to get bug fixes and security patches:

```bash
# Update pip first
python -m pip install --upgrade pip

# Update all packages (use with caution)
pip list --outdated
pip install --upgrade <package-name>

# Test thoroughly after updates
pytest
```

### 5. Separate Development and Production Dependencies

- `requirements.txt`: Production dependencies (minimal, essential packages)
- `requirements-dev.txt`: Development dependencies (testing, linting, documentation)

Install production deps: `pip install -r requirements.txt`  
Install dev deps: `pip install -r requirements-dev.txt` (includes production)

### 6. Document Environment Variables

If your project needs environment variables:

1. Create a `.env.example` file with variable names (no values)
2. Copy it to `.env` and fill in actual values
3. Never commit `.env` to version control
4. Document required variables in README.md

### 7. Use Activation Helper Scripts

The setup scripts create `activate_venv.sh` or `activate_venv.bat` for quick activation:

```bash
# Linux/macOS
source ./activate_venv.sh

# Windows
activate_venv.bat
```

### 8. Deactivate When Switching Projects

Always deactivate the virtual environment when switching to another project:

```bash
deactivate
```

### 9. Recreate Virtual Environments When Needed

If you encounter persistent issues:

```bash
# Delete and recreate
rm -rf venv  # or rmdir /s /q venv on Windows
./setup_venv.sh
```

### 10. IDE Integration

Configure your IDE to use the virtual environment:

**VS Code**:
1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Select "Python: Select Interpreter"
3. Choose the interpreter in `./venv/bin/python` or `.\venv\Scripts\python.exe`

**PyCharm**:
1. File → Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Existing environment"
4. Browse to `venv/bin/python` or `venv\Scripts\python.exe`

---

## Additional Resources

- [Python venv Documentation](https://docs.python.org/3/library/venv.html)
- [pip User Guide](https://pip.pypa.io/en/stable/user_guide/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Virtual Environments Tutorial](https://realpython.com/python-virtual-environments-a-primer/)

---

## Summary

Virtual environments are essential for Python development. The AI Agent Console provides automated setup scripts for all major platforms, making it easy to get started. Follow the quick start guide for your platform, and refer to the troubleshooting section if you encounter any issues.

For questions or issues not covered in this guide, please open an issue on the project repository.
