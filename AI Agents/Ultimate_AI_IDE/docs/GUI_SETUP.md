# UAIDE GUI Setup

## Prerequisites

The UAIDE GUI uses Python's tkinter library, which is included with most Python installations.

### Checking if tkinter is installed

```bash
python -m tkinter
```

This should open a small test window. If it does, tkinter is installed correctly.

### Installing tkinter

#### Windows

Tkinter is usually included with Python on Windows. If missing:

1. **Reinstall Python** from python.org and ensure "tcl/tk and IDLE" is checked during installation

OR

2. **Install via Chocolatey**:
```bash
choco install python --params "/InstallDir:C:\Python"
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get install python3-tk
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install python3-tkinter
```

#### macOS

Tkinter is included with Python on macOS. If missing:

```bash
brew install python-tk
```

## Launching the GUI

Once tkinter is installed:

### Windows
```bash
.\scripts\run_gui.bat
```

### Linux/Mac
```bash
python -m src.ui.gui.main_window
```

## Alternative: Using the CLI

If you cannot install tkinter, use the CLI interface instead:

```bash
.\scripts\run_uaide.bat --help
```

The CLI provides all the same features through command-line commands.

## Troubleshooting

### "No module named 'tkinter'"

1. Verify Python installation includes tkinter
2. Check Python version (3.8+)
3. Reinstall Python with tkinter support
4. Use the CLI interface as an alternative

### GUI appears but is blank

1. Update graphics drivers
2. Try running with different display settings
3. Check for conflicting GUI libraries

### GUI is slow or unresponsive

1. Close other applications
2. Check AI model size (large models need more RAM)
3. Reduce max_tokens in Settings

## Development Mode

To run the GUI in development mode with debugging:

```bash
python -m src.ui.gui.main_window --debug
```

## Next Steps

Once the GUI is running, see [GUI_GUIDE.md](GUI_GUIDE.md) for usage instructions.
