
"""
Sandboxed File I/O Tool

This tool provides safe file read/write operations with:
- Path validation (prevents access to system directories)
- File size limits
- Extension validation
- Overwrite confirmations
- Cross-platform path handling
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from .base import Tool


class FileIOTool(Tool):
    """
    Sandboxed file I/O tool for safe file operations.
    
    Features:
    - Read files with encoding support
    - Write files with overwrite protection
    - Create directories safely
    - Path validation against blocked directories
    - File extension whitelisting
    - File size limits
    - Cross-platform path handling
    
    Safety:
    - Blocked system directories
    - File size limits
    - Extension validation
    - Overwrite confirmations
    - Path traversal prevention
    """
    
    def __init__(
        self,
        name: str = "file_io",
        description: str = "Sandboxed file I/O operations",
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(name=name, description=description, config=config)
        
        # Default configuration
        self.max_file_size = self.config.get('max_file_size', 104857600)  # 100 MB
        self.allowed_extensions = self.config.get('allowed_file_extensions', [])
        self.blocked_paths = self.config.get('blocked_paths', [
            '/etc', '/sys', '/proc', '/boot', '/dev', '/root',
            'C:\\Windows', 'C:\\System32', 'C:\\Program Files'
        ])
        self.require_confirmation = self.config.get('require_file_confirmation', True)
    
    def invoke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute file I/O operation.
        
        Args:
            params: Dictionary with:
                - operation: 'read', 'write', 'append', 'delete', 'list', 'mkdir'
                - path: File or directory path
                - content: Content to write (for write/append)
                - encoding: File encoding (default: utf-8)
                - force: Skip confirmation (default: False)
                
        Returns:
            Dictionary with operation result
        """
        self._log_invocation(params)
        
        try:
            # Validate required parameters
            operation = params.get('operation')
            if not operation:
                raise ValueError("Missing required parameter: operation")
            
            path = params.get('path')
            if not path:
                raise ValueError("Missing required parameter: path")
            
            # Validate path
            validated_path = self._validate_path(path)
            if not validated_path:
                return {
                    'success': False,
                    'error': f"Invalid or blocked path: {path}"
                }
            
            # Execute operation
            handlers = {
                'read': self._read_file,
                'write': self._write_file,
                'append': self._append_file,
                'delete': self._delete_file,
                'list': self._list_directory,
                'mkdir': self._make_directory,
                'exists': self._check_exists,
                'info': self._get_file_info
            }
            
            handler = handlers.get(operation)
            if not handler:
                return {
                    'success': False,
                    'error': f"Unknown operation: {operation}"
                }
            
            return handler(validated_path, params)
            
        except Exception as e:
            self.logger.exception(f"File I/O operation failed")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_path(self, path: str) -> Optional[Path]:
        """
        Validate file path for safety.
        
        Args:
            path: Path to validate
            
        Returns:
            Validated Path object or None if invalid
        """
        try:
            # Convert to Path object
            file_path = Path(path).resolve()
            
            # Check for path traversal
            if '..' in str(file_path):
                self.logger.warning(f"Path traversal attempt: {path}")
                return None
            
            # Check blocked paths
            for blocked in self.blocked_paths:
                blocked_path = Path(blocked).resolve()
                try:
                    file_path.relative_to(blocked_path)
                    self.logger.warning(f"Blocked path access: {file_path}")
                    return None
                except ValueError:
                    # Not under blocked path, continue
                    pass
            
            # Check file extension if exists or will be created
            if file_path.exists() or any(op in str(file_path) for op in ['.', '/']):
                if self.allowed_extensions:
                    if file_path.suffix and file_path.suffix not in self.allowed_extensions:
                        self.logger.warning(f"Extension not allowed: {file_path.suffix}")
                        return None
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"Path validation error: {e}")
            return None
    
    def _check_file_size(self, size: int) -> bool:
        """Check if file size is within limits."""
        if size > self.max_file_size:
            self.logger.warning(f"File size {size} exceeds limit {self.max_file_size}")
            return False
        return True
    
    def _read_file(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read file content."""
        try:
            if not path.exists():
                return {
                    'success': False,
                    'error': f"File not found: {path}"
                }
            
            if not path.is_file():
                return {
                    'success': False,
                    'error': f"Not a file: {path}"
                }
            
            # Check file size
            size = path.stat().st_size
            if not self._check_file_size(size):
                return {
                    'success': False,
                    'error': f"File too large: {size} bytes (max: {self.max_file_size})"
                }
            
            # Read file
            encoding = params.get('encoding', 'utf-8')
            
            try:
                with open(path, 'r', encoding=encoding) as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try reading as binary
                with open(path, 'rb') as f:
                    content = f.read()
                    return {
                        'success': True,
                        'content': content,
                        'binary': True,
                        'size': size,
                        'path': str(path)
                    }
            
            return {
                'success': True,
                'content': content,
                'binary': False,
                'size': size,
                'path': str(path),
                'encoding': encoding
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Read failed: {str(e)}"
            }
    
    def _write_file(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to file."""
        try:
            content = params.get('content')
            if content is None:
                return {
                    'success': False,
                    'error': "Missing required parameter: content"
                }
            
            # Check if file exists and confirmation required
            if path.exists() and self.require_confirmation and not params.get('force', False):
                return {
                    'success': False,
                    'error': f"File exists and confirmation required: {path}",
                    'requires_confirmation': True
                }
            
            # Check content size
            content_size = len(content) if isinstance(content, str) else len(content)
            if not self._check_file_size(content_size):
                return {
                    'success': False,
                    'error': f"Content too large: {content_size} bytes"
                }
            
            # Create parent directories
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            encoding = params.get('encoding', 'utf-8')
            
            if isinstance(content, bytes):
                with open(path, 'wb') as f:
                    f.write(content)
            else:
                with open(path, 'w', encoding=encoding) as f:
                    f.write(content)
            
            return {
                'success': True,
                'path': str(path),
                'size': content_size,
                'operation': 'write'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Write failed: {str(e)}"
            }
    
    def _append_file(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """Append content to file."""
        try:
            content = params.get('content')
            if content is None:
                return {
                    'success': False,
                    'error': "Missing required parameter: content"
                }
            
            # Check content size
            content_size = len(content) if isinstance(content, str) else len(content)
            if not self._check_file_size(content_size):
                return {
                    'success': False,
                    'error': f"Content too large: {content_size} bytes"
                }
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Append to file
            encoding = params.get('encoding', 'utf-8')
            
            if isinstance(content, bytes):
                with open(path, 'ab') as f:
                    f.write(content)
            else:
                with open(path, 'a', encoding=encoding) as f:
                    f.write(content)
            
            return {
                'success': True,
                'path': str(path),
                'appended_size': content_size,
                'operation': 'append'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Append failed: {str(e)}"
            }
    
    def _delete_file(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete file."""
        try:
            if not path.exists():
                return {
                    'success': False,
                    'error': f"File not found: {path}"
                }
            
            # Confirmation required for deletion
            if self.require_confirmation and not params.get('force', False):
                return {
                    'success': False,
                    'error': f"Deletion requires confirmation: {path}",
                    'requires_confirmation': True
                }
            
            # Delete file
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()  # Only removes empty directories
            
            return {
                'success': True,
                'path': str(path),
                'operation': 'delete'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Delete failed: {str(e)}"
            }
    
    def _list_directory(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """List directory contents."""
        try:
            if not path.exists():
                return {
                    'success': False,
                    'error': f"Directory not found: {path}"
                }
            
            if not path.is_dir():
                return {
                    'success': False,
                    'error': f"Not a directory: {path}"
                }
            
            # List contents
            pattern = params.get('pattern', '*')
            recursive = params.get('recursive', False)
            
            if recursive:
                items = list(path.rglob(pattern))
            else:
                items = list(path.glob(pattern))
            
            # Build results
            results = []
            for item in items:
                results.append({
                    'name': item.name,
                    'path': str(item),
                    'is_file': item.is_file(),
                    'is_dir': item.is_dir(),
                    'size': item.stat().st_size if item.is_file() else None
                })
            
            return {
                'success': True,
                'path': str(path),
                'count': len(results),
                'items': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"List failed: {str(e)}"
            }
    
    def _make_directory(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create directory."""
        try:
            # Create directory
            path.mkdir(parents=True, exist_ok=True)
            
            return {
                'success': True,
                'path': str(path),
                'operation': 'mkdir'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"mkdir failed: {str(e)}"
            }
    
    def _check_exists(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check if file/directory exists."""
        exists = path.exists()
        
        return {
            'success': True,
            'path': str(path),
            'exists': exists,
            'is_file': path.is_file() if exists else None,
            'is_dir': path.is_dir() if exists else None
        }
    
    def _get_file_info(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get file information."""
        try:
            if not path.exists():
                return {
                    'success': False,
                    'error': f"Path not found: {path}"
                }
            
            stat_info = path.stat()
            
            return {
                'success': True,
                'path': str(path),
                'name': path.name,
                'size': stat_info.st_size,
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
                'modified': stat_info.st_mtime,
                'created': stat_info.st_ctime,
                'permissions': oct(stat_info.st_mode)[-3:]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Info failed: {str(e)}"
            }

