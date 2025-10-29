"""
AI Coding Assistant - Main Entry Point

Ultimate AI coding assistant powered by llama.cpp.
Supports multiple languages, self-improving through learning from user feedback.
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ui.cli import main as cli_main

# GUI import is optional (requires tkinter)
try:
    from ui.gui import main as gui_main
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    gui_main = None


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Ultimate AI Coding Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Start CLI interface (default)
  python main.py --mode cli   # Start CLI interface
  python main.py --mode gui   # Start GUI interface

For first-time setup, run with CLI mode and follow the prompts.
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['cli', 'gui'],
        default='cli',
        help='Interface mode (default: cli)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='AI Coding Assistant v1.0.0'
    )

    args = parser.parse_args()

    # Launch appropriate interface
    if args.mode == 'gui':
        if not GUI_AVAILABLE:
            print("ERROR: GUI mode not available (tkinter not installed)")
            print("Please install tkinter or use CLI mode (default)")
            print("  Linux: sudo apt-get install python3-tk")
            print("  Windows: Reinstall Python with tkinter option")
            print("  macOS: tkinter should be included with Python")
            sys.exit(1)
        print("Starting GUI mode...")
        gui_main()
    else:
        cli_main()


if __name__ == "__main__":
    main()
