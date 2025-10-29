"""
PyInstaller runtime hook for llama-cpp-python

This hook helps llama_cpp find its library files when running as a bundled executable.
Place this file in the same directory as your .spec file.
"""

import os
import sys

# When running as a PyInstaller bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Get the PyInstaller extraction directory
    bundle_dir = sys._MEIPASS
    
    # Set up the llama_cpp library path
    llama_cpp_lib = os.path.join(bundle_dir, 'llama_cpp', 'lib')
    llama_cpp_dir = os.path.join(bundle_dir, 'llama_cpp')
    
    # Add all potential DLL locations to PATH
    paths_to_add = []
    
    if os.path.exists(llama_cpp_lib):
        paths_to_add.append(llama_cpp_lib)
    
    if os.path.exists(llama_cpp_dir):
        paths_to_add.append(llama_cpp_dir)
    
    # Also check for CUDA DLLs in common locations within the bundle
    cuda_paths = [
        os.path.join(bundle_dir, 'nvidia', 'cublas', 'bin'),
        os.path.join(bundle_dir, 'nvidia', 'cudart', 'bin'),
        os.path.join(bundle_dir, 'nvidia', 'cuda_runtime', 'bin'),
        os.path.join(bundle_dir, '_internal'),
        bundle_dir
    ]
    
    for cuda_path in cuda_paths:
        if os.path.exists(cuda_path):
            paths_to_add.append(cuda_path)
    
    # Update PATH environment variable
    if paths_to_add and sys.platform == 'win32':
        current_path = os.environ.get('PATH', '')
        new_path = os.pathsep.join(paths_to_add) + os.pathsep + current_path
        os.environ['PATH'] = new_path
        print(f"[Hook] Added {len(paths_to_add)} paths to PATH for llama_cpp")
        
        # Try to preload the DLL with full path
        if os.path.exists(llama_cpp_lib):
            llama_dll = os.path.join(llama_cpp_lib, 'llama.dll')
            if os.path.exists(llama_dll):
                # Add this directory to DLL search path (Windows 8+)
                try:
                    if hasattr(os, 'add_dll_directory'):
                        os.add_dll_directory(llama_cpp_lib)
                        print(f"[Hook] Added DLL directory: {llama_cpp_lib}")
                except Exception as e:
                    print(f"[Hook] Warning: Could not add DLL directory: {e}")
    
    # For Linux
    elif paths_to_add and sys.platform.startswith('linux'):
        current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
        new_ld_path = os.pathsep.join(paths_to_add) + os.pathsep + current_ld_path
        os.environ['LD_LIBRARY_PATH'] = new_ld_path
        print(f"[Hook] Added {len(paths_to_add)} paths to LD_LIBRARY_PATH")

