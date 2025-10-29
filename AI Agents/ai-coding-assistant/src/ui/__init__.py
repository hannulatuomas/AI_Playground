"""
UI modules for AI Coding Assistant.

This package contains user interface implementations:
- cli: Command-line interface (primary)
- gui: Graphical user interface (optional, tkinter-based)
"""

from .cli import CLI

# GUI is optional (requires tkinter)
try:
    from .gui import GUI
    __all__ = ['CLI', 'GUI']
except ImportError:
    # tkinter not available, GUI won't be available
    __all__ = ['CLI']

__version__ = '1.0.0'
