"""
File Splitter

Splits large files into smaller, more manageable modules.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import ast
import re


@dataclass
class FileSplit:
    """Information about a file split."""
    original_file: str
    new_files: List[Tuple[str, str]]  # (filename, content)
    imports_to_update: Dict[str, List[str]]  # file -> imports to add


class FileSplitter:
    """Splits large files into smaller modules."""
    
    def __init__(self, max_lines: int = 500):
        """
        Initialize file splitter.
        
        Args:
            max_lines: Maximum lines per file
        """
        self.max_lines = max_lines
    
    def split_large_file(self, file_path: str, language: str = 'python',
                        split_points: Optional[List[int]] = None) -> Optional[FileSplit]:
        """
        Split a large file into smaller modules.
        
        Args:
            file_path: Path to file to split
            language: Programming language
            split_points: Optional specific line numbers to split at
            
        Returns:
            FileSplit with new file information, or None if no split needed
        """
        path = Path(file_path)
        
        if not path.exists():
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Check if split is needed
        if len(lines) <= self.max_lines and not split_points:
            return None
        
        if language == 'python':
            return self._split_python_file(path, content, split_points)
        elif language in ['javascript', 'typescript']:
            return self._split_js_file(path, content, split_points)
        else:
            return None
    
    def _split_python_file(self, file_path: Path, content: str,
                          split_points: Optional[List[int]]) -> Optional[FileSplit]:
        """Split Python file into smaller modules."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            print(f"Cannot split {file_path}: syntax errors")
            return None
        
        # Extract imports
        imports = self._extract_python_imports(tree)
        
        # Group top-level definitions
        groups = self._group_python_definitions(tree, content)
        
        if len(groups) <= 1:
            return None
        
        # Create new files
        new_files = []
        base_name = file_path.stem
        parent_dir = file_path.parent
        
        for i, (group_name, group_content) in enumerate(groups):
            # Generate filename
            if group_name:
                new_filename = f"{base_name}_{group_name.lower()}.py"
            else:
                new_filename = f"{base_name}_part{i+1}.py"
            
            # Add imports to new file
            file_content = imports + "\n\n" + group_content
            
            new_files.append((new_filename, file_content))
        
        # Create __init__.py to re-export everything
        init_content = self._create_python_init(new_files, base_name)
        new_files.append(("__init__.py", init_content))
        
        return FileSplit(
            original_file=str(file_path),
            new_files=new_files,
            imports_to_update={}
        )
    
    def _extract_python_imports(self, tree: ast.AST) -> str:
        """Extract import statements from AST."""
        imports = []
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node))
        
        return '\n'.join(imports) if imports else ""
    
    def _group_python_definitions(self, tree: ast.AST, 
                                 content: str) -> List[Tuple[str, str]]:
        """Group Python definitions logically."""
        groups = []
        lines = content.split('\n')
        
        # Group by classes
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                
                class_content = '\n'.join(lines[start_line:end_line])
                groups.append((node.name, class_content))
        
        # Group standalone functions
        functions = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                
                func_content = '\n'.join(lines[start_line:end_line])
                functions.append(func_content)
        
        if functions:
            groups.append(("functions", '\n\n'.join(functions)))
        
        return groups
    
    def _create_python_init(self, new_files: List[Tuple[str, str]], 
                           base_name: str) -> str:
        """Create __init__.py to re-export split modules."""
        init_lines = [
            f'"""',
            f'{base_name} module - split for maintainability.',
            f'"""',
            ''
        ]
        
        # Import from each new file
        for filename, _ in new_files:
            if filename != "__init__.py":
                module_name = filename.replace('.py', '')
                init_lines.append(f'from .{module_name} import *')
        
        return '\n'.join(init_lines)
    
    def _split_js_file(self, file_path: Path, content: str,
                      split_points: Optional[List[int]]) -> Optional[FileSplit]:
        """Split JavaScript/TypeScript file."""
        # Basic implementation: split by export statements
        lines = content.split('\n')
        
        # Find export statements
        exports = []
        current_export = []
        in_export = False
        
        for i, line in enumerate(lines):
            if re.match(r'^\s*export\s+(class|function|const|let|var)', line):
                if current_export:
                    exports.append('\n'.join(current_export))
                current_export = [line]
                in_export = True
            elif in_export:
                current_export.append(line)
                # Simple heuristic: export ends at next export or empty line
                if not line.strip() or line.strip().startswith('export'):
                    if line.strip().startswith('export'):
                        exports.append('\n'.join(current_export[:-1]))
                        current_export = [line]
                    else:
                        exports.append('\n'.join(current_export))
                        current_export = []
                        in_export = False
        
        if current_export:
            exports.append('\n'.join(current_export))
        
        if len(exports) <= 1:
            return None
        
        # Create new files
        new_files = []
        base_name = file_path.stem
        ext = file_path.suffix
        
        for i, export_content in enumerate(exports):
            new_filename = f"{base_name}_part{i+1}{ext}"
            new_files.append((new_filename, export_content))
        
        # Create index file
        index_content = self._create_js_index(new_files, ext)
        new_files.append((f"index{ext}", index_content))
        
        return FileSplit(
            original_file=str(file_path),
            new_files=new_files,
            imports_to_update={}
        )
    
    def _create_js_index(self, new_files: List[Tuple[str, str]], ext: str) -> str:
        """Create index file to re-export split modules."""
        lines = []
        
        for filename, _ in new_files:
            if filename != f"index{ext}":
                module_name = filename.replace(ext, '')
                lines.append(f"export * from './{module_name}';")
        
        return '\n'.join(lines)
    
    def write_split_files(self, split: FileSplit, target_dir: Optional[str] = None) -> bool:
        """
        Write split files to disk.
        
        Args:
            split: FileSplit information
            target_dir: Target directory (uses original file's dir if None)
            
        Returns:
            True if successful
        """
        if not split:
            return False
        
        original_path = Path(split.original_file)
        
        if target_dir:
            output_dir = Path(target_dir)
        else:
            # Create subdirectory with original filename
            output_dir = original_path.parent / original_path.stem
        
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Write new files
            for filename, content in split.new_files:
                file_path = output_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Created: {file_path}")
            
            print(f"\nOriginal file can be replaced with: {output_dir}")
            return True
            
        except Exception as e:
            print(f"Error writing split files: {e}")
            return False
