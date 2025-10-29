
"""
File Operations Tool

This tool provides comprehensive file operations for agents:
- Read files with encoding support
- Write/create files
- Edit existing files (line-based or content replacement)
- Move/rename files
- Delete/remove files
- Proper error handling and validation

This tool can be used as a dependency by other agents for all their
file operation needs.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List

from .base import Tool


class FileOperationsTool(Tool):
    """
    Comprehensive file operations tool for agents.
    
    Features:
    - Read files with encoding support and error handling
    - Write files (create new or overwrite existing)
    - Edit files (line-based editing or content replacement)
    - Move/rename files and directories
    - Delete/remove files and directories
    - Safe operations with validation
    - Detailed error reporting
    
    Operations:
    - read: Read file contents
    - write: Write/create file
    - edit: Modify existing file content
    - move: Move or rename file/directory
    - rename: Alias for move
    - delete: Delete file/directory
    - remove: Alias for delete
    - copy: Copy file/directory
    - exists: Check if path exists
    - mkdir: Create directory
    """
    
    def __init__(
        self,
        name: str = "file_operations",
        description: str = "Comprehensive file operations (read, write, edit, move, delete)",
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(name=name, description=description, config=config)
        
        # Configuration
        self.max_file_size = self.config.get('max_file_size', 104857600)  # 100 MB
        self.require_confirmation = self.config.get('require_file_confirmation', False)
        self.blocked_paths = self.config.get('blocked_paths', [
            '/etc', '/sys', '/proc', '/boot', '/dev', '/root',
            'C:\\Windows', 'C:\\System32', 'C:\\Program Files'
        ])
    
    def invoke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute file operation.
        
        Args:
            params: Dictionary with:
                - operation: Operation type (read, write, edit, move, delete, etc.)
                - path: Target file/directory path
                - content: Content for write/edit operations
                - destination: Destination for move/copy operations
                - encoding: File encoding (default: utf-8)
                - backup: Create backup before editing (default: False)
                - force: Skip confirmations (default: False)
                - line_start: Start line for line-based editing
                - line_end: End line for line-based editing
                - old_content: Content to replace in edit operations
                - new_content: New content for replacements
                
        Returns:
            Dictionary with operation result
        """
        self._log_invocation(params)
        
        try:
            operation = params.get('operation', '').lower()
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
                'edit': self._edit_file,
                'move': self._move_path,
                'rename': self._move_path,
                'delete': self._delete_path,
                'remove': self._delete_path,
                'copy': self._copy_path,
                'exists': self._check_exists,
                'mkdir': self._make_directory,
            }
            
            handler = handlers.get(operation)
            if not handler:
                return {
                    'success': False,
                    'error': f"Unknown operation: {operation}. Available: {', '.join(handlers.keys())}"
                }
            
            return handler(validated_path, params)
            
        except Exception as e:
            self.logger.exception("File operation failed")
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
            file_path = Path(path).resolve()
            
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
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"Path validation error: {e}")
            return None
    
    def _read_file(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read file content.
        
        Args:
            path: File path
            params: Additional parameters (encoding, etc.)
            
        Returns:
            Result dictionary with file content
        """
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
            if size > self.max_file_size:
                return {
                    'success': False,
                    'error': f"File too large: {size} bytes (max: {self.max_file_size})"
                }
            
            # Read file
            encoding = params.get('encoding', 'utf-8')
            
            try:
                with open(path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # Also read lines if requested
                lines = None
                if params.get('read_lines', False):
                    with open(path, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                
                return {
                    'success': True,
                    'content': content,
                    'lines': lines,
                    'size': size,
                    'path': str(path),
                    'encoding': encoding,
                    'line_count': len(content.split('\n')) if content else 0
                }
                
            except UnicodeDecodeError as e:
                return {
                    'success': False,
                    'error': f"Failed to decode file with {encoding} encoding: {str(e)}"
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Read operation failed: {str(e)}"
            }
    
    def _write_file(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write content to file (create or overwrite).
        
        Args:
            path: File path
            params: Parameters including 'content'
            
        Returns:
            Result dictionary
        """
        try:
            content = params.get('content')
            if content is None:
                return {
                    'success': False,
                    'error': "Missing required parameter: content"
                }
            
            # Check if overwriting existing file
            if path.exists() and self.require_confirmation and not params.get('force', False):
                return {
                    'success': False,
                    'error': f"File exists and confirmation required: {path}",
                    'requires_confirmation': True
                }
            
            # Create backup if requested
            if path.exists() and params.get('backup', False):
                backup_path = Path(str(path) + '.backup')
                shutil.copy2(path, backup_path)
                self.logger.info(f"Created backup: {backup_path}")
            
            # Create parent directories
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            encoding = params.get('encoding', 'utf-8')
            
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return {
                'success': True,
                'path': str(path),
                'size': len(content),
                'operation': 'write',
                'created': not path.exists()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Write operation failed: {str(e)}"
            }
    
    def _edit_file(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit existing file content.
        
        Supports two modes:
        1. Line-based editing: Replace specific line range
        2. Content replacement: Replace old content with new
        
        Args:
            path: File path
            params: Edit parameters
            
        Returns:
            Result dictionary
        """
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
            
            # Create backup if requested
            if params.get('backup', True):
                backup_path = Path(str(path) + '.backup')
                shutil.copy2(path, backup_path)
                self.logger.info(f"Created backup: {backup_path}")
            
            encoding = params.get('encoding', 'utf-8')
            
            # Read current content
            with open(path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            # Determine edit mode
            if 'line_start' in params or 'line_end' in params:
                # Line-based editing
                result = self._edit_lines(path, lines, params, encoding)
            elif 'old_content' in params and 'new_content' in params:
                # Content replacement
                result = self._edit_replace(path, lines, params, encoding)
            else:
                return {
                    'success': False,
                    'error': "Edit requires either (line_start/line_end) or (old_content/new_content)"
                }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Edit operation failed: {str(e)}"
            }
    
    def _edit_lines(
        self,
        path: Path,
        lines: List[str],
        params: Dict[str, Any],
        encoding: str
    ) -> Dict[str, Any]:
        """
        Edit specific lines in file.
        
        Args:
            path: File path
            lines: Current file lines
            params: Edit parameters
            encoding: File encoding
            
        Returns:
            Result dictionary
        """
        try:
            line_start = params.get('line_start', 1)  # 1-based
            line_end = params.get('line_end', line_start)
            new_content = params.get('new_content', params.get('content', ''))
            
            # Convert to 0-based index
            start_idx = max(0, line_start - 1)
            end_idx = min(len(lines), line_end)
            
            # Ensure new_content ends with newline if replacing lines
            if new_content and not new_content.endswith('\n'):
                new_content += '\n'
            
            # Replace lines
            new_lines = lines[:start_idx] + [new_content] + lines[end_idx:]
            
            # Write back
            with open(path, 'w', encoding=encoding) as f:
                f.writelines(new_lines)
            
            return {
                'success': True,
                'path': str(path),
                'operation': 'edit_lines',
                'lines_modified': end_idx - start_idx,
                'line_range': f"{line_start}-{line_end}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Line-based edit failed: {str(e)}"
            }
    
    def _edit_replace(
        self,
        path: Path,
        lines: List[str],
        params: Dict[str, Any],
        encoding: str
    ) -> Dict[str, Any]:
        """
        Replace content in file.
        
        Args:
            path: File path
            lines: Current file lines
            params: Edit parameters
            encoding: File encoding
            
        Returns:
            Result dictionary
        """
        try:
            old_content = params['old_content']
            new_content = params['new_content']
            
            # Join lines to full content
            content = ''.join(lines)
            
            # Check if old content exists
            if old_content not in content:
                return {
                    'success': False,
                    'error': "Old content not found in file"
                }
            
            # Count occurrences
            count = content.count(old_content)
            
            # Replace content
            new_file_content = content.replace(old_content, new_content)
            
            # Write back
            with open(path, 'w', encoding=encoding) as f:
                f.write(new_file_content)
            
            return {
                'success': True,
                'path': str(path),
                'operation': 'edit_replace',
                'replacements': count
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Content replacement failed: {str(e)}"
            }
    
    def _move_path(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Move or rename file/directory.
        
        Args:
            path: Source path
            params: Parameters including 'destination'
            
        Returns:
            Result dictionary
        """
        try:
            if not path.exists():
                return {
                    'success': False,
                    'error': f"Source path not found: {path}"
                }
            
            destination = params.get('destination')
            if not destination:
                return {
                    'success': False,
                    'error': "Missing required parameter: destination"
                }
            
            dest_path = self._validate_path(destination)
            if not dest_path:
                return {
                    'success': False,
                    'error': f"Invalid destination path: {destination}"
                }
            
            # Check if destination exists
            if dest_path.exists() and not params.get('force', False):
                return {
                    'success': False,
                    'error': f"Destination already exists: {dest_path}",
                    'requires_confirmation': True
                }
            
            # Create parent directory
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move
            shutil.move(str(path), str(dest_path))
            
            return {
                'success': True,
                'source': str(path),
                'destination': str(dest_path),
                'operation': 'move'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Move operation failed: {str(e)}"
            }
    
    def _delete_path(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete file or directory.
        
        Args:
            path: Path to delete
            params: Additional parameters
            
        Returns:
            Result dictionary
        """
        try:
            if not path.exists():
                return {
                    'success': False,
                    'error': f"Path not found: {path}"
                }
            
            # Confirmation for deletion
            if self.require_confirmation and not params.get('force', False):
                return {
                    'success': False,
                    'error': f"Deletion requires confirmation: {path}",
                    'requires_confirmation': True
                }
            
            # Delete
            if path.is_file():
                path.unlink()
                item_type = 'file'
            elif path.is_dir():
                if params.get('recursive', False):
                    shutil.rmtree(path)
                else:
                    path.rmdir()  # Only removes empty directories
                item_type = 'directory'
            else:
                return {
                    'success': False,
                    'error': f"Unknown path type: {path}"
                }
            
            return {
                'success': True,
                'path': str(path),
                'operation': 'delete',
                'type': item_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Delete operation failed: {str(e)}"
            }
    
    def _copy_path(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Copy file or directory.
        
        Args:
            path: Source path
            params: Parameters including 'destination'
            
        Returns:
            Result dictionary
        """
        try:
            if not path.exists():
                return {
                    'success': False,
                    'error': f"Source path not found: {path}"
                }
            
            destination = params.get('destination')
            if not destination:
                return {
                    'success': False,
                    'error': "Missing required parameter: destination"
                }
            
            dest_path = self._validate_path(destination)
            if not dest_path:
                return {
                    'success': False,
                    'error': f"Invalid destination path: {destination}"
                }
            
            # Check if destination exists
            if dest_path.exists() and not params.get('force', False):
                return {
                    'success': False,
                    'error': f"Destination already exists: {dest_path}",
                    'requires_confirmation': True
                }
            
            # Create parent directory
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy
            if path.is_file():
                shutil.copy2(path, dest_path)
                item_type = 'file'
            elif path.is_dir():
                shutil.copytree(path, dest_path, dirs_exist_ok=params.get('force', False))
                item_type = 'directory'
            else:
                return {
                    'success': False,
                    'error': f"Unknown path type: {path}"
                }
            
            return {
                'success': True,
                'source': str(path),
                'destination': str(dest_path),
                'operation': 'copy',
                'type': item_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Copy operation failed: {str(e)}"
            }
    
    def _check_exists(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if path exists.
        
        Args:
            path: Path to check
            params: Additional parameters
            
        Returns:
            Result dictionary
        """
        exists = path.exists()
        
        result = {
            'success': True,
            'path': str(path),
            'exists': exists
        }
        
        if exists:
            result.update({
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
                'size': path.stat().st_size if path.is_file() else None
            })
        
        return result
    
    def _make_directory(self, path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create directory.
        
        Args:
            path: Directory path
            params: Additional parameters
            
        Returns:
            Result dictionary
        """
        try:
            parents = params.get('parents', True)
            exist_ok = params.get('exist_ok', True)
            
            path.mkdir(parents=parents, exist_ok=exist_ok)
            
            return {
                'success': True,
                'path': str(path),
                'operation': 'mkdir'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"mkdir operation failed: {str(e)}"
            }


