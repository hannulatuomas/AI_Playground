"""
User Interface Module

Provides CLI and GUI interfaces.
"""

# Don't import cli here to avoid circular import warnings when running as module
# Import only when needed
def get_cli():
    """Lazy import of CLI to avoid module execution warnings"""
    from .cli import cli, main
    return cli, main

# GUI is optional - only import if tkinter is available
def get_gui():
    """Lazy import of GUI"""
    try:
        from .gui import UAIDEApp
        return UAIDEApp
    except ImportError:
        # tkinter not available, GUI won't work but CLI will
        return None

__all__ = ["get_cli", "get_gui"]
