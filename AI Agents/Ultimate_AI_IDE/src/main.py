"""
Ultimate AI-Powered IDE - Main Entry Point

This is the main application entry point for UAIDE.
"""

import sys
from pathlib import Path

from .ui.cli import main as cli_main


def main():
    """Main application entry point."""
    try:
        cli_main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
