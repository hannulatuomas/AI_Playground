#!/usr/bin/env python3
"""
Type Checking Script for AI Agent Console

This script runs mypy type checking on the codebase with various options.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str]) -> int:
    """
    Run a command and return the exit code.
    
    Args:
        cmd: Command and arguments as list
        
    Returns:
        Exit code from the command
    """
    print(f"Running: {' '.join(cmd)}")
    print("-" * 80)
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    print("-" * 80)
    print()
    
    return result.returncode


def check_all() -> int:
    """Check the entire project."""
    print("Type checking entire project...")
    return run_command(["mypy", "."])


def check_core() -> int:
    """Check core modules only."""
    print("Type checking core modules...")
    return run_command(["mypy", "core/"])


def check_agents() -> int:
    """Check agents modules."""
    print("Type checking agents...")
    return run_command(["mypy", "agents/"])


def check_tools() -> int:
    """Check tools modules."""
    print("Type checking tools...")
    return run_command(["mypy", "tools/"])


def check_strict() -> int:
    """Run strict type checking."""
    print("Type checking with strict mode...")
    return run_command(["mypy", "--strict", "tools/", "core/"])


def check_specific(path: str) -> int:
    """Check a specific file or directory."""
    print(f"Type checking {path}...")
    return run_command(["mypy", path])


def show_help():
    """Show help message."""
    print("""
Type Checking Script for AI Agent Console

Usage:
    python check_types.py [option]

Options:
    all         Check entire project (default)
    core        Check core modules only
    agents      Check agents modules
    tools       Check tools modules
    strict      Run strict type checking on core and tools
    <path>      Check specific file or directory
    help        Show this help message

Examples:
    python check_types.py
    python check_types.py core
    python check_types.py agents/base/
    python check_types.py tools/vector_db.py

Configuration:
    Type checking settings are in mypy.ini

Tips:
    - Start with 'core' and 'tools' (stricter checking)
    - Gradually add type hints to agents
    - Use '# type: ignore' sparingly for unavoidable issues
    - Run before committing code
    """)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
        
        if option in ["help", "-h", "--help"]:
            show_help()
            return 0
        elif option == "all":
            return check_all()
        elif option == "core":
            return check_core()
        elif option == "agents":
            return check_agents()
        elif option == "tools":
            return check_tools()
        elif option == "strict":
            return check_strict()
        else:
            # Treat as path
            return check_specific(option)
    else:
        # Default: check all
        return check_all()


if __name__ == "__main__":
    exit_code = main()
    
    if exit_code == 0:
        print("✅ Type checking passed!")
    else:
        print("❌ Type checking failed!")
        print("\nTo fix type errors:")
        print("  1. Add type annotations to functions")
        print("  2. Use Optional[T] for values that can be None")
        print("  3. Add '# type: ignore' comments for unavoidable issues")
        print("  4. Check mypy.ini configuration")
    
    sys.exit(exit_code)
