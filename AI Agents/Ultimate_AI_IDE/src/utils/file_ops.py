"""
File Operations Utilities

Provides file and directory manipulation utilities.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


def ensure_dir(path: str) -> Path:
    """
    Ensure directory exists, create if needed.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def read_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
    """
    Read file contents safely.
    
    Args:
        file_path: Path to file
        encoding: File encoding
        
    Returns:
        File contents or None if error
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None


def write_file(
    file_path: str,
    content: str,
    encoding: str = 'utf-8',
    create_dirs: bool = True
) -> bool:
    """
    Write content to file safely.
    
    Args:
        file_path: Path to file
        content: Content to write
        encoding: File encoding
        create_dirs: Create parent directories if needed
        
    Returns:
        True if successful
    """
    try:
        path = Path(file_path)
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        return False


def copy_file(src: str, dst: str, overwrite: bool = False) -> bool:
    """
    Copy file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        overwrite: Overwrite if exists
        
    Returns:
        True if successful
    """
    try:
        if not overwrite and Path(dst).exists():
            logger.warning(f"Destination {dst} already exists")
            return False
        
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        logger.error(f"Error copying file {src} to {dst}: {e}")
        return False


def delete_file(file_path: str) -> bool:
    """
    Delete file safely.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if successful
    """
    try:
        Path(file_path).unlink(missing_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False


def list_files(
    directory: str,
    pattern: str = "*",
    recursive: bool = False
) -> List[Path]:
    """
    List files in directory matching pattern.
    
    Args:
        directory: Directory path
        pattern: Glob pattern
        recursive: Search recursively
        
    Returns:
        List of file paths
    """
    try:
        dir_path = Path(directory)
        if recursive:
            return list(dir_path.rglob(pattern))
        else:
            return list(dir_path.glob(pattern))
    except Exception as e:
        logger.error(f"Error listing files in {directory}: {e}")
        return []


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes, -1 if error
    """
    try:
        return Path(file_path).stat().st_size
    except Exception as e:
        logger.error(f"Error getting file size {file_path}: {e}")
        return -1


def file_exists(file_path: str) -> bool:
    """
    Check if file exists.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file exists
    """
    return Path(file_path).is_file()


def dir_exists(dir_path: str) -> bool:
    """
    Check if directory exists.
    
    Args:
        dir_path: Path to directory
        
    Returns:
        True if directory exists
    """
    return Path(dir_path).is_dir()
