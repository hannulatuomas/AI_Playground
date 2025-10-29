"""
Code Editor Module

Handles code insertion and file modifications.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple
from .generator import CodeArtifact


class CodeEditor:
    """Edits and inserts code into files."""
    
    def insert_code(self, artifact: CodeArtifact, 
                   backup: bool = True) -> bool:
        """
        Insert or update code in a file.
        
        Args:
            artifact: Code artifact to insert
            backup: Create backup before modifying
            
        Returns:
            True if successful, False otherwise
        """
        file_path = Path(artifact.file_path)
        
        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Backup existing file if requested
            if backup and file_path.exists():
                self._backup_file(file_path)
            
            # Write the code
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(artifact.content)
            
            return True
            
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
            return False
    
    def insert_at_location(self, file_path: str, code: str, 
                          line_number: Optional[int] = None,
                          after_pattern: Optional[str] = None) -> bool:
        """
        Insert code at specific location in file.
        
        Args:
            file_path: Path to file
            code: Code to insert
            line_number: Line number to insert at (optional)
            after_pattern: Insert after this pattern (optional)
            
        Returns:
            True if successful
        """
        path = Path(file_path)
        
        if not path.exists():
            return False
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Determine insertion point
            if line_number is not None:
                insert_idx = min(line_number, len(lines))
            elif after_pattern:
                insert_idx = self._find_pattern(lines, after_pattern)
                if insert_idx == -1:
                    return False
            else:
                # Append at end
                insert_idx = len(lines)
            
            # Insert the code
            code_lines = code.split('\n')
            for i, line in enumerate(code_lines):
                lines.insert(insert_idx + i, line + '\n')
            
            # Write back
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            print(f"Error inserting code: {e}")
            return False
    
    def replace_function(self, file_path: str, function_name: str,
                        new_code: str) -> bool:
        """
        Replace a function in a file.
        
        Args:
            file_path: Path to file
            function_name: Name of function to replace
            new_code: New function code
            
        Returns:
            True if successful
        """
        path = Path(file_path)
        
        if not path.exists():
            return False
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find function boundaries
            start, end = self._find_function_boundaries(content, function_name)
            
            if start == -1:
                return False
            
            # Replace the function
            new_content = content[:start] + new_code + content[end:]
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            print(f"Error replacing function: {e}")
            return False
    
    def add_import(self, file_path: str, import_statement: str,
                  language: str) -> bool:
        """
        Add an import statement to a file.
        
        Args:
            file_path: Path to file
            import_statement: Import to add
            language: Programming language
            
        Returns:
            True if successful
        """
        path = Path(file_path)
        
        if not path.exists():
            return False
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Check if import already exists
            if any(import_statement in line for line in lines):
                return True  # Already exists
            
            # Find where to insert import
            insert_idx = self._find_import_location(lines, language)
            
            # Insert the import
            lines.insert(insert_idx, import_statement + '\n')
            
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            print(f"Error adding import: {e}")
            return False
    
    def update_indentation(self, code: str, base_indent: int = 0) -> str:
        """
        Update code indentation.
        
        Args:
            code: Code to update
            base_indent: Base indentation level (spaces)
            
        Returns:
            Code with updated indentation
        """
        lines = code.split('\n')
        
        # Find minimum indentation
        min_indent = float('inf')
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)
        
        if min_indent == float('inf'):
            min_indent = 0
        
        # Adjust indentation
        adjusted_lines = []
        for line in lines:
            if line.strip():
                current_indent = len(line) - len(line.lstrip())
                new_indent = base_indent + (current_indent - min_indent)
                adjusted_lines.append(' ' * new_indent + line.lstrip())
            else:
                adjusted_lines.append('')
        
        return '\n'.join(adjusted_lines)
    
    def _backup_file(self, file_path: Path):
        """Create a backup of the file."""
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
        except Exception:
            pass  # Backup failed, continue anyway
    
    def _find_pattern(self, lines: list, pattern: str) -> int:
        """Find line index matching pattern."""
        for i, line in enumerate(lines):
            if pattern in line or re.search(pattern, line):
                return i + 1  # Insert after the match
        return -1
    
    def _find_function_boundaries(self, content: str, 
                                  function_name: str) -> Tuple[int, int]:
        """
        Find start and end positions of a function.
        
        Returns:
            Tuple of (start_pos, end_pos) or (-1, -1) if not found
        """
        # Simple implementation - can be improved
        lines = content.split('\n')
        
        start_line = -1
        indent_level = 0
        
        # Find function start
        for i, line in enumerate(lines):
            if f'def {function_name}' in line or f'function {function_name}' in line:
                start_line = i
                indent_level = len(line) - len(line.lstrip())
                break
        
        if start_line == -1:
            return (-1, -1)
        
        # Find function end (next function or class at same indent level)
        end_line = len(lines)
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip():
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level:
                    if line.strip().startswith(('def ', 'class ', 'function ')):
                        end_line = i
                        break
        
        # Convert line numbers to character positions
        start_pos = sum(len(line) + 1 for line in lines[:start_line])
        end_pos = sum(len(line) + 1 for line in lines[:end_line])
        
        return (start_pos, end_pos)
    
    def _find_import_location(self, lines: list, language: str) -> int:
        """Find where to insert import statement."""
        if language == 'python':
            # Insert after existing imports or at top
            last_import = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')):
                    last_import = i + 1
                elif line.strip() and not line.strip().startswith('#'):
                    # First non-import, non-comment line
                    break
            return last_import
        
        elif language in ['javascript', 'typescript']:
            # Insert after existing imports
            last_import = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('import '):
                    last_import = i + 1
                elif line.strip() and not line.strip().startswith('//'):
                    break
            return last_import
        
        elif language == 'csharp':
            # Insert after existing using statements
            last_using = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('using '):
                    last_using = i + 1
                elif line.strip() and not line.strip().startswith('//'):
                    break
            return last_using
        
        return 0
