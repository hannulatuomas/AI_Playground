#!/usr/bin/env python3
"""
Quick verification script to check if the environment is set up correctly.
Run this after installing dependencies to verify the installation.
"""

import sys
import importlib
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.10+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python version too old: {version.major}.{version.minor}.{version.micro} (need 3.10+)")
        return False


def check_dependencies():
    """Check if all required dependencies are installed"""
    required = [
        'typer',
        'pydantic',
        'ollama',
        'openai',
    ]
    
    all_ok = True
    for package in required:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - not installed")
            all_ok = False
    
    return all_ok


def check_project_structure():
    """Check if all project files exist"""
    required_files = [
        'core/__init__.py',
        'core/config.py',
        'core/engine.py',
        'core/llm_router.py',
        'main.py',
        'config.yaml',
        'requirements.txt',
        'README.md',
    ]
    
    all_ok = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - missing")
            all_ok = False
    
    return all_ok


def main():
    print("=" * 60)
    print("AI Agent Console - Setup Verification")
    print("=" * 60)
    
    print("\n1. Checking Python version...")
    py_ok = check_python_version()
    
    print("\n2. Checking project structure...")
    struct_ok = check_project_structure()
    
    print("\n3. Checking dependencies...")
    deps_ok = check_dependencies()
    
    print("\n" + "=" * 60)
    if py_ok and struct_ok and deps_ok:
        print("✓ All checks passed! The environment is ready.")
        print("\nTry running:")
        print("  python main.py --help")
        print("  python main.py status")
        return 0
    else:
        print("✗ Some checks failed. Please review the output above.")
        if not deps_ok:
            print("\nTo install dependencies, run:")
            print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
