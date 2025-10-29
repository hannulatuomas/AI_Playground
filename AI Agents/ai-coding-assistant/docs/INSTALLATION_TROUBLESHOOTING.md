# Installation Troubleshooting Guide

## Issue: numpy installation fails on Python 3.12

### Problem
```
ERROR: Exception:
numpy==1.24.3 requires compilation
```

### Solution

We've updated the requirements to use Python 3.12 compatible versions.

#### Option 1: Install All Dependencies (Recommended)
```bash
# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# Install all dependencies including RAG
pip install -r requirements.txt
```

#### Option 2: Install Core Only (No RAG)
If RAG installation fails, you can use the assistant without RAG features:
```bash
# Install only core dependencies
pip install -r requirements-core.txt
```

The assistant will work perfectly fine without RAG - it will just use keyword-based search instead of semantic search.

#### Option 3: Install RAG Separately
```bash
# First install core
pip install -r requirements-core.txt

# Then try RAG dependencies separately
pip install -r requirements-rag.txt
```

#### Option 4: Manual Installation
```bash
# Install one by one
pip install colorama
pip install regex
pip install numpy>=1.26.0
pip install sentence-transformers>=2.2.2
pip install chromadb>=0.4.18
```

---

## Python Version Requirements

- **Minimum**: Python 3.8
- **Recommended**: Python 3.12.10
- **Best for RAG**: Python 3.10-3.12

---

## Common Issues

### 1. Build Tools Missing (Windows)

**Error**: "Microsoft Visual C++ 14.0 or greater is required"

**Solution**: Install Visual Studio Build Tools
- Download: https://visualstudio.microsoft.com/downloads/
- Install "Desktop development with C++"
- OR use pre-built wheels: `pip install --upgrade pip`

### 2. Long Path Issues (Windows)

**Error**: "Could not install packages due to path too long"

**Solution**: Enable long paths
```powershell
# Run PowerShell as Administrator
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### 3. Permission Errors

**Error**: "Permission denied"

**Solution**:
```bash
# Use --user flag
pip install --user -r requirements.txt

# OR create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 4. SSL Certificate Errors

**Error**: "SSL: CERTIFICATE_VERIFY_FAILED"

**Solution**:
```bash
# Update certificates
pip install --upgrade certifi

# Or use trusted host (less secure)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### 5. Network/Proxy Issues

**Error**: "Connection timeout"

**Solution**:
```bash
# Set timeout
pip install --timeout 300 -r requirements.txt

# Use proxy
pip install --proxy http://proxy.server:port -r requirements.txt
```

---

## Verification

After installation, verify everything works:

```python
# Test imports
python -c "import colorama; print('✓ colorama')"
python -c "import regex; print('✓ regex')"

# Test RAG (if installed)
python -c "import numpy; print('✓ numpy')"
python -c "import sentence_transformers; print('✓ sentence-transformers')"
python -c "import chromadb; print('✓ chromadb')"
```

Or run the assistant:
```bash
python src/main.py
```

Look for:
- `✓ All components initialized!` (core working)
- `✓ RAG system ready` (RAG working)
- `⚠ RAG not available` (core working, RAG not installed - this is OK!)

---

## Quick Start Without RAG

If you want to start immediately without RAG:

```bash
# Install minimal dependencies
pip install colorama regex

# Run the assistant
python src/main.py
```

The assistant will work perfectly fine, just without semantic search.

---

## Getting Help

If issues persist:

1. Check Python version: `python --version`
2. Check pip version: `pip --version`
3. Upgrade pip: `python -m pip install --upgrade pip`
4. Try virtual environment (see above)
5. Check error message carefully
6. Search error online
7. Open GitHub issue with:
   - Python version
   - OS and version
   - Full error message
   - Output of `pip list`

---

## Success!

Once installed, you should see:

```
============================================================
  AI Coding Assistant
  Powered by llama.cpp
============================================================

Initializing components...
✓ Configuration loaded
✓ Database initialized
✓ Prompt engine ready
✓ LLM interface ready
✓ Code generator ready
✓ Debugger ready
✓ Language support loaded
✓ RAG system ready (semantic search available)

✓ All components initialized!

Type 'help' for available commands
Type 'exit' or 'quit' to exit

ai-assistant>
```

Happy coding! 🚀
