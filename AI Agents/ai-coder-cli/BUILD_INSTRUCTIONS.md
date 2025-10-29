# Windows Binary Build Instructions

This document explains how to build Windows executables for AI Agent Console.

## Overview

The AI Agent Console can be packaged as a standalone Windows executable using PyInstaller. This allows users to run the application without installing Python or any dependencies.

## Prerequisites

To build the Windows binary, you need:

1. **Python 3.9+** (3.11 recommended)
2. **Windows 10 or later** (64-bit)
3. **Git** (optional, for cloning the repository)
4. **500 MB free disk space** (for build artifacts)

## Quick Start

### Option 1: PowerShell (Recommended)

Open PowerShell in the project directory and run:

```powershell
.\build_windows.ps1
```

### Option 2: Command Prompt

Open Command Prompt in the project directory and run:

```cmd
build_windows.bat
```

## Build Process

The build scripts perform the following steps:

1. **Clean up** previous build artifacts
2. **Create** a temporary virtual environment
3. **Install** all project dependencies
4. **Install** PyInstaller
5. **Run** PyInstaller with the spec file
6. **Verify** the build output
7. **Create** a distribution ZIP package

## Build Output

After a successful build, you'll find:

### Executable Directory

```
dist/
└── ai-agent-console/
    ├── ai-agent-console.exe    # Main executable
    ├── config.yaml              # Configuration file
    ├── VERSION                  # Version file
    ├── agents/                  # Agent modules and data
    ├── tools/                   # Tool modules
    ├── orchestration/           # Orchestration workflows
    ├── core/                    # Core modules
    ├── docs/                    # Documentation
    ├── examples/                # Example files
    └── _internal/               # PyInstaller runtime files
```

### Distribution Package

A ZIP file is also created:

```
ai-agent-console-windows-YYYYMMDD_HHMMSS.zip
```

This can be distributed to users for easy installation.

## Configuration Files

### ai-agent-console.spec

The PyInstaller spec file that defines:
- Entry point (`main.py`)
- Hidden imports (packages not auto-detected)
- Data files to include
- Executable settings

**Location:** `ai-agent-console.spec`

**Documentation:** See comments in the spec file for detailed information.

### Build Scripts

Two build scripts are provided:

1. **build_windows.ps1** - PowerShell version
   - Better error handling
   - Colored output
   - Progress indicators

2. **build_windows.bat** - Batch version
   - Compatible with older Windows
   - Works without PowerShell

Both scripts perform the same operations and produce identical output.

## Customizing the Build

### Changing the App Name

Edit `ai-agent-console.spec`:

```python
APP_NAME = 'your-custom-name'
```

### Adding an Icon

1. Create or obtain a `.ico` file
2. Place it in the project root
3. Edit `ai-agent-console.spec`:

```python
ICON_FILE = 'your-icon.ico'
```

### Excluding Packages

To reduce file size, exclude unnecessary packages in the spec file:

```python
excludes=[
    'tkinter',
    'matplotlib.tests',
    'numpy.tests',
    # Add more packages to exclude
]
```

### Single-File Executable

By default, the build creates a directory with multiple files. To create a single executable:

Edit `ai-agent-console.spec`, in the `EXE()` section:

```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # Add this
    a.zipfiles,  # Add this
    a.datas,     # Add this
    [],
    exclude_binaries=False,  # Change to False
    # ... rest of settings
)
```

Then remove or comment out the `COLLECT()` section.

**Note:** Single-file executables are slower to start and may have compatibility issues.

## Troubleshooting

### Build Fails: "Python not found"

**Solution:** Ensure Python is in your PATH:

```cmd
python --version
```

If not found, reinstall Python with "Add to PATH" option checked.

### Build Fails: "pip not found"

**Solution:** Upgrade pip:

```cmd
python -m pip install --upgrade pip
```

### Build Fails: "Module not found"

**Solution:** Install missing dependencies:

```cmd
pip install -r requirements.txt
```

### Build Succeeds but Executable Fails to Run

**Check 1:** Missing hidden imports

Add to `hiddenimports` list in `ai-agent-console.spec`:

```python
hidden_imports = [
    'your_missing_module',
]
```

**Check 2:** Missing data files

Add to `datas` list in `ai-agent-console.spec`:

```python
datas += [('path/to/file', 'destination')]
```

**Check 3:** Check build logs

Look for errors in the PyInstaller output during build.

### Build Takes Too Long

**Normal:** First build takes 5-15 minutes depending on system.

**To Speed Up:**
- Use an SSD
- Close unnecessary applications
- Exclude testing/development packages

### Antivirus Blocks Executable

**Solution:** Add build directory to antivirus exclusions:
- `dist/`
- `build/`
- `build_venv/`

### "Access Denied" Errors

**Solution:** Run as Administrator:
- Right-click script
- Select "Run as administrator"

## Testing the Build

After building, test the executable:

### Basic Test

```cmd
cd dist\ai-agent-console
ai-agent-console.exe --help
```

### Status Check

```cmd
ai-agent-console.exe status
```

### Simple Query

```cmd
ai-agent-console.exe run "Test query"
```

**Note:** You need to configure Ollama or OpenAI before running queries.

## Distribution

### For End Users

Distribute the entire `dist/ai-agent-console/` directory or the ZIP file.

**Instructions for users:**

1. Extract ZIP to desired location
2. Edit `config.yaml` with settings
3. Run `ai-agent-console.exe`

### For Professional Distribution

For production distribution, consider:

1. **Code Signing Certificate**
   - Prevents "Unknown Publisher" warnings
   - Required for some enterprise environments
   - Obtain from CA (DigiCert, Sectigo, etc.)

2. **Installer Creation**
   - Use NSIS (Nullsoft Scriptable Install System)
   - Or Inno Setup
   - Provides professional installation experience

3. **Version Information**
   - Update VERSION file before building
   - Include in installer/package name

## Build Size Optimization

The default build is ~200-500 MB. To reduce size:

### 1. Exclude Unused Packages

In `ai-agent-console.spec`:

```python
excludes=[
    'tkinter',
    '_tkinter',
    'matplotlib.tests',
    'numpy.tests',
    'pandas.tests',
    'pytest',
    'IPython',
    'jupyter',
]
```

### 2. Use UPX Compression

PyInstaller automatically uses UPX if available:

1. Download UPX: https://upx.github.io/
2. Extract to a directory in PATH
3. Rebuild - PyInstaller will auto-detect and use it

### 3. Remove Unnecessary Data Files

Only include essential documentation in `datas`:

```python
# Instead of including all docs:
datas += [(os.path.join(spec_root, 'docs'), 'docs')]

# Include only essential:
datas += [
    (os.path.join(spec_root, 'docs/guides/WINDOWS_INSTALLATION.md'), 'docs/guides'),
]
```

### 4. Strip Debug Symbols

In `EXE()` section:

```python
strip=True,  # Strip debug symbols
```

## Automation

### GitHub Actions

For automated builds on GitHub:

```yaml
name: Build Windows Binary

on:
  release:
    types: [created]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Build
        run: .\build_windows.ps1
      - name: Upload
        uses: actions/upload-artifact@v2
        with:
          name: windows-binary
          path: dist/ai-agent-console/
```

### Scheduled Builds

For nightly or scheduled builds:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
```

## Version Management

Before building a release:

1. **Update VERSION file:**
   ```
   2.5.0
   ```

2. **Update version in spec file** (if applicable)

3. **Tag the release:**
   ```cmd
   git tag -a v2.5.0 -m "Version 2.5.0"
   git push origin v2.5.0
   ```

4. **Build:**
   ```cmd
   build_windows.ps1
   ```

5. **Test the build**

6. **Create GitHub release** with ZIP file

## Advanced Topics

### Multi-Architecture Builds

To build for both 32-bit and 64-bit:

1. Use 32-bit Python for 32-bit build
2. Use 64-bit Python for 64-bit build
3. Name outputs accordingly: `ai-agent-console-win64.zip`, `ai-agent-console-win32.zip`

**Note:** 32-bit builds are not recommended for this application due to memory requirements.

### Portable Version

To create a truly portable version:

1. Use relative paths in configuration
2. Store data in application directory
3. Don't write to system directories
4. Include all required files

### Silent Installation

Create a silent installer script:

```bat
@echo off
echo Installing AI Agent Console...
xcopy /E /I /Y "source\*.*" "%ProgramFiles%\AI-Agent-Console\"
echo Installation complete!
pause
```

## Support

For build issues:

1. Check logs in `build/` directory
2. Review PyInstaller warnings in console output
3. Test on a clean Windows installation
4. Check GitHub Issues for similar problems
5. Consult [Windows Installation Guide](docs/guides/WINDOWS_INSTALLATION.md)

## Resources

- **PyInstaller Documentation:** https://pyinstaller.org/
- **UPX:** https://upx.github.io/
- **NSIS:** https://nsis.sourceforge.io/
- **Inno Setup:** https://jrsoftware.org/isinfo.php
- **Code Signing:** https://docs.microsoft.com/en-us/windows/win32/seccrypto/signtool

## Changelog

- **v2.5.0 (2025-10-14)**: Initial build system implementation

---

**Last Updated:** 2025-10-14  
**Version:** 2.5.0
