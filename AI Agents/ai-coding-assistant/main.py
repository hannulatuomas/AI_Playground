"""
AI Coding Assistant Launcher

This is a convenience launcher that calls the main application.
The actual application code is in src/main.py
"""

import sys
import subprocess
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main application
from src.main import main

if __name__ == "__main__":
    main()
