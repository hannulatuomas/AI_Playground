"""
Path Utilities

Provides path manipulation and validation utilities.
"""

import os
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


def normalize_path(path: str) -> str:
    """
    Normalize path to absolute path.
    
    Args:
        path: Path to normalize
        
    Returns:
        Normalized absolute path
    """
    return str(Path(path).resolve())


def get_relative_path(path: str, base: str) -> str:
    """
    Get relative path from base.
    
    Args:
        path: Target path
        base: Base path
        
    Returns:
        Relative path
    """
    try:
        return str(Path(path).relative_to(base))
    except ValueError:
        return path


def join_paths(*paths: str) -> str:
    """
    Join multiple path components.
    
    Args:
        *paths: Path components
        
    Returns:
        Joined path
    """
    return str(Path(*paths))


def get_parent_dir(path: str, levels: int = 1) -> str:
    """
    Get parent directory.
    
    Args:
        path: File or directory path
        levels: Number of levels up
        
    Returns:
        Parent directory path
    """
    p = Path(path)
    for _ in range(levels):
        p = p.parent
    return str(p)


def get_filename(path: str, with_extension: bool = True) -> str:
    """
    Get filename from path.
    
    Args:
        path: File path
        with_extension: Include file extension
        
    Returns:
        Filename
    """
    p = Path(path)
    if with_extension:
        return p.name
    else:
        return p.stem


def get_extension(path: str) -> str:
    """
    Get file extension.
    
    Args:
        path: File path
        
    Returns:
        File extension (including dot)
    """
    return Path(path).suffix


def change_extension(path: str, new_ext: str) -> str:
    """
    Change file extension.
    
    Args:
        path: File path
        new_ext: New extension (with or without dot)
        
    Returns:
        Path with new extension
    """
    p = Path(path)
    if not new_ext.startswith('.'):
        new_ext = '.' + new_ext
    return str(p.with_suffix(new_ext))


def is_subpath(path: str, parent: str) -> bool:
    """
    Check if path is subpath of parent.
    
    Args:
        path: Path to check
        parent: Parent path
        
    Returns:
        True if path is under parent
    """
    try:
        Path(path).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False


def find_project_root(start_path: str, markers: Optional[List[str]] = None) -> Optional[str]:
    """
    Find project root by looking for marker files.
    
    Args:
        start_path: Starting directory
        markers: List of marker files/dirs (e.g., .git, setup.py)
        
    Returns:
        Project root path or None
    """
    if markers is None:
        markers = ['.git', 'setup.py', 'pyproject.toml', 'package.json']
    
    current = Path(start_path).resolve()
    
    while current != current.parent:
        for marker in markers:
            if (current / marker).exists():
                return str(current)
        current = current.parent
    
    return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def expand_user(path: str) -> str:
    """
    Expand ~ to user home directory.
    
    Args:
        path: Path with ~ notation
        
    Returns:
        Expanded path
    """
    return str(Path(path).expanduser())


def get_size_str(size_bytes: int) -> str:
    """
    Convert bytes to human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
