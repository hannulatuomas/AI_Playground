# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AI Agent Console
This file configures how PyInstaller builds the Windows executable.

Usage:
    pyinstaller ai-agent-console.spec

This will create a standalone executable in the dist/ directory.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all

# Get the directory containing this spec file
spec_root = os.path.abspath(SPECPATH)

# ============================================================================
# Configuration
# ============================================================================

APP_NAME = 'ai-agent-console'
MAIN_SCRIPT = 'main.py'
ICON_FILE = None  # Set to 'icon.ico' if you have an icon file

# ============================================================================
# Hidden Imports
# ============================================================================
# These are modules that PyInstaller might not detect automatically

hidden_imports = [
    # Core modules
    'core',
    'core.config',
    'core.engine',
    'core.llm_router',
    'core.memory',
    'core.prompts',
    
    # Agent system
    'agents',
    'agents.registry',
    'agents.base',
    
    # All agent modules
    'agents.code_planner',
    'agents.git_agent',
    'agents.web_data',
    'agents.web_search',
    'agents.database',
    'agents.data_analysis',
    'agents.cybersecurity',
    'agents.windows_admin',
    'agents.api_agent',
    'agents.enhanced_prompt_refiner',
    
    # Generic agents
    'agents.generic',
    'agents.generic.generic_code_editor',
    'agents.generic.generic_debug_agent',
    'agents.generic.generic_build_agent',
    'agents.generic.generic_code_tester',
    'agents.generic.task_orchestrator',
    'agents.generic.task_decomposition',
    'agents.generic.specification_extraction',
    'agents.generic.context_manager',
    
    # Language-specific agents
    'agents.languages',
    'agents.languages.python',
    'agents.languages.csharp',
    'agents.languages.cpp',
    'agents.languages.web',
    'agents.languages.shell',
    'agents.languages.powershell',
    'agents.languages.batch',
    
    # Agent utilities
    'agents.utils',
    'agents.utils.codebase_awareness',
    'agents.utils.context_optimizer',
    'agents.utils.clarification_templates',
    
    # Tool system
    'tools',
    'tools.registry',
    'tools.base',
    'tools.web_fetch',
    'tools.git',
    'tools.filesystem',
    'tools.web_scraper',
    'tools.code_analyzer',
    'tools.ollama_manager',
    'tools.mcp',
    'tools.file_operations',
    
    # Development tools
    'tools.devtools',
    'tools.devtools.linter',
    'tools.devtools.formatter',
    'tools.devtools.static_analyzer',
    'tools.devtools.devtools_manager',
    
    # Orchestration
    'orchestration',
    'orchestration.workflows',
    'orchestration.workflows.base_workflow',
    'orchestration.workflows.workflow_manager',
    'orchestration.workflows.task_loop_workflow',
    'orchestration.task_loop_processor',
    
    # Utilities
    'utils',
    
    # Third-party dependencies that might need explicit import
    'typer',
    'pydantic',
    'pydantic_settings',
    'rich',
    'rich.console',
    'rich.table',
    'rich.panel',
    'rich.progress',
    'rich.logging',
    'rich.markdown',
    'rich.syntax',
    'yaml',
    'tomli',
    'gitpython',
    'git',
    'httpx',
    'requests',
    'beautifulsoup4',
    'bs4',
    'lxml',
    'ollama',
    'openai',
    'chromadb',
    'pandas',
    'numpy',
    'matplotlib',
    'seaborn',
    'pymongo',
    'redis',
    'neo4j',
    'pymysql',
    'psycopg2',
    'duckduckgo_search',
    
    # llama-cpp-python support
    'llama_cpp',
    'llama_cpp.llama_cpp',
    'llama_cpp.llama',
    'llama_cpp.server',
    
    # Windows-specific (conditional)
    'wmi',
    'win32api',
    'win32con',
    'win32file',
    'pywintypes',
]

# Collect all submodules from key packages
hidden_imports += collect_submodules('agents')
hidden_imports += collect_submodules('tools')
hidden_imports += collect_submodules('core')
hidden_imports += collect_submodules('orchestration')

# ============================================================================
# Data Files
# ============================================================================
# Include non-Python files that the application needs

datas = []

# Configuration file
if os.path.exists(os.path.join(spec_root, 'config.yaml')):
    datas += [(os.path.join(spec_root, 'config.yaml'), '.')]

# VERSION file
if os.path.exists(os.path.join(spec_root, 'VERSION')):
    datas += [(os.path.join(spec_root, 'VERSION'), '.')]

# Agents directory - include all markdown files
if os.path.exists(os.path.join(spec_root, 'agents')):
    datas += [(os.path.join(spec_root, 'agents'), 'agents')]

# Tools directory - include all files
if os.path.exists(os.path.join(spec_root, 'tools')):
    datas += [(os.path.join(spec_root, 'tools'), 'tools')]

# Orchestration directory - include workflow YAML files
if os.path.exists(os.path.join(spec_root, 'orchestration')):
    datas += [(os.path.join(spec_root, 'orchestration'), 'orchestration')]

# Core directory - include all files
if os.path.exists(os.path.join(spec_root, 'core')):
    datas += [(os.path.join(spec_root, 'core'), 'core')]

# Utilities directory
if os.path.exists(os.path.join(spec_root, 'utils')):
    datas += [(os.path.join(spec_root, 'utils'), 'utils')]

# Documentation (optional but recommended)
if os.path.exists(os.path.join(spec_root, 'docs')):
    datas += [(os.path.join(spec_root, 'docs'), 'docs')]

# Examples
if os.path.exists(os.path.join(spec_root, 'examples')):
    datas += [(os.path.join(spec_root, 'examples'), 'examples')]

# Config directory
if os.path.exists(os.path.join(spec_root, 'config')):
    datas += [(os.path.join(spec_root, 'config'), 'config')]

# Collect data files from installed packages
datas += collect_data_files('chromadb')
datas += collect_data_files('rich')
datas += collect_data_files('typer')

# Collect llama-cpp-python library files (if installed)
# We need to collect files WITHOUT importing llama_cpp (which would fail if CUDA deps missing)
try:
    # Find llama_cpp without importing it
    import importlib.util
    spec_obj = importlib.util.find_spec('llama_cpp')
    
    if spec_obj and spec_obj.origin:
        llama_cpp_path = os.path.dirname(spec_obj.origin)
        print(f"*** llama-cpp-python found at: {llama_cpp_path}")
        
        # Method 1: Collect the entire llama_cpp package directory
        # This ensures the directory structure is preserved
        if os.path.exists(llama_cpp_path):
            datas.append((llama_cpp_path, 'llama_cpp'))
            print(f"*** Bundling entire llama_cpp directory: {llama_cpp_path}")
            
            # Count what we're bundling
            file_count = sum(1 for root, dirs, files in os.walk(llama_cpp_path) for f in files)
            print(f"*** Found {file_count} files in llama_cpp")
        
        # Try collect_all but suppress import errors
        try:
            # This may trigger a warning about failed submodule collection, which is fine
            llama_datas, llama_binaries, llama_hiddenimports = collect_all('llama_cpp')
            # Only add if we got meaningful results
            if llama_datas:
                datas += llama_datas
                print(f"*** collect_all found {len(llama_datas)} additional data files")
            if llama_hiddenimports:
                hidden_imports += llama_hiddenimports
                print(f"*** collect_all found {len(llama_hiddenimports)} hidden imports")
        except (ImportError, RuntimeError) as e:
            # Expected - llama_cpp can't be imported without CUDA libs in PATH
            print(f"*** collect_all import warning (expected, not critical): {type(e).__name__}")
        except Exception as e:
            print(f"*** collect_all warning (not critical): {type(e).__name__}: {e}")
    else:
        print("*** llama-cpp-python not found (spec.origin is None)")
    
except ImportError:
    print("*** llama-cpp-python not installed, skipping")
except Exception as e:
    print(f"*** Warning: Could not locate llama-cpp-python: {type(e).__name__}: {e}")
    print("*** Continuing build without llama-cpp-python")

# ============================================================================
# Binaries
# ============================================================================
# External binary dependencies (usually auto-detected)

binaries = []

# Collect llama-cpp-python binaries (DLLs, shared libraries)
# Do this WITHOUT importing llama_cpp to avoid dependency errors
try:
    # Find llama_cpp path without importing
    import importlib.util
    spec_obj = importlib.util.find_spec('llama_cpp')
    
    if spec_obj and spec_obj.origin:
        llama_cpp_path = os.path.dirname(spec_obj.origin)
        
        # Collect ALL files from llama_cpp directory recursively
        print(f"*** Scanning {llama_cpp_path} for binaries...")
        binary_count = 0
        for root, dirs, files in os.walk(llama_cpp_path):
            for file in files:
                if file.endswith(('.dll', '.pyd', '.so', '.dylib', '.bin', '.cu')):
                    src = os.path.join(root, file)
                    # Calculate relative path from llama_cpp root
                    rel_path = os.path.relpath(root, llama_cpp_path)
                    if rel_path == '.':
                        dest = 'llama_cpp'
                    else:
                        dest = os.path.join('llama_cpp', rel_path).replace('\\', '/')
                    binaries.append((src, dest))
                    # Only print first few to avoid spam
                    if binary_count < 5:
                        print(f"***   Binary: {file} -> {dest}")
                    binary_count += 1
        
        print(f"*** Found {binary_count} binary files in llama_cpp")
        
        # Skip collect_all for binaries - it tries to import which fails
        print("*** Skipping collect_all for binaries (would cause import errors)")
    else:
        print("*** llama-cpp-python spec not found")
    
except ImportError:
    print("*** llama-cpp-python not installed, skipping binary collection")
except Exception as e:
    print(f"*** Warning collecting llama-cpp binaries (not critical): {type(e).__name__}: {e}")

# ============================================================================
# Analysis
# ============================================================================
# PyInstaller analysis phase

a = Analysis(
    [MAIN_SCRIPT],
    pathex=[spec_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hook-llama_cpp.py'] if os.path.exists('hook-llama_cpp.py') else [],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'tkinter',
        'tk',
        '_tkinter',
        'matplotlib.tests',
        'numpy.tests',
        'pandas.tests',
        'pytest',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# ============================================================================
# PYZ Archive
# ============================================================================
# Create a PYZ archive containing all Python modules

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None
)

# ============================================================================
# Executable
# ============================================================================
# Create the main executable

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX if available
    console=True,  # Show console window (CLI application)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_FILE if ICON_FILE and os.path.exists(ICON_FILE) else None,
)

# ============================================================================
# COLLECT
# ============================================================================
# Collect all files into the distribution directory

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

# ============================================================================
# Notes
# ============================================================================
"""
Build Notes:

1. This spec file creates a directory-based distribution (not a single file).
   The output will be in: dist/ai-agent-console/

2. To create a single-file executable instead, modify the EXE() section:
   - Change exclude_binaries=True to exclude_binaries=False
   - Add all binaries and datas to the EXE() parameters
   - Remove the COLLECT() section

3. The executable will be: dist/ai-agent-console/ai-agent-console.exe

4. Users will need to:
   - Copy the entire dist/ai-agent-console/ directory to their system
   - Edit config.yaml with their settings
   - Run ai-agent-console.exe from the command line

5. Optional optimizations:
   - Add UPX (Ultimate Packer for eXecutables) for compression
   - Create an installer using NSIS or Inno Setup
   - Sign the executable with a code signing certificate

6. Known limitations:
   - Ollama or OpenAI must be configured separately
   - Some dynamic imports may need manual testing
   - Large dependencies (pandas, numpy) increase file size

7. Testing checklist:
   - Test all CLI commands
   - Test agent execution
   - Test configuration loading
   - Test file operations
   - Test with both Ollama and OpenAI
   - Test on clean Windows system

8. llama-cpp-python support:
   - Automatically detects and bundles llama-cpp-python if installed
   - Includes all CUDA/CPU libraries from lib/ directory
   - Collects all DLL and binary files
   - Build continues even if llama-cpp-python is not installed
   - Watch for "*** Found llama-cpp-python" messages during build
"""
