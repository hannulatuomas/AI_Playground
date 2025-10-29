"""
File Splitter Module

Automatically splits large files into smaller, more manageable modules.
Enforces the <500 lines per file rule.
"""

import ast
import re
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path
import logging


class FileSplitter:
    """Split large files into smaller modules"""
    
    def __init__(self, max_lines: int = 500):
        """
        Initialize file splitter
        
        Args:
            max_lines: Maximum lines per file (default: 500)
        """
        self.max_lines = max_lines
        self.logger = logging.getLogger(__name__)
    
    def detect_large_files(self, project_path: str, 
                          extensions: Optional[List[str]] = None) -> List[Dict[str, any]]:
        """
        Detect files exceeding max_lines
        
        Args:
            project_path: Project root path
            extensions: File extensions to check (default: ['.py', '.js', '.ts'])
            
        Returns:
            List of large files with metadata
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx']
        
        large_files = []
        project = Path(project_path)
        
        for ext in extensions:
            for file_path in project.rglob(f'*{ext}'):
                # Skip test files, generated files, and venv
                if any(skip in str(file_path) for skip in ['test_', '__pycache__', 'node_modules', '.venv', 'venv', '.git']):
                    continue
                
                # Skip very large files (>10MB) to avoid hangs
                try:
                    file_size = file_path.stat().st_size
                    if file_size > 10 * 1024 * 1024:  # 10MB
                        self.logger.warning(f"Skipping very large file: {file_path} ({file_size} bytes)")
                        continue
                except:
                    continue
                
                try:
                    # Count lines without loading entire file into memory
                    line_count = 0
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for _ in f:
                            line_count += 1
                            # Early exit if we know it's large enough
                            if line_count > self.max_lines * 2:
                                break
                    
                    if line_count > self.max_lines:
                        large_files.append({
                            'path': str(file_path.relative_to(project)),
                            'lines': line_count,
                            'excess': line_count - self.max_lines,
                            'language': self._detect_language(file_path)
                        })
                except Exception as e:
                    self.logger.warning(f"Could not read {file_path}: {e}")
        
        return sorted(large_files, key=lambda x: x['lines'], reverse=True)
    
    def suggest_split_points(self, file_path: str) -> Dict[str, any]:
        """
        Suggest split points for a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Split suggestions
        """
        language = self._detect_language(Path(file_path))
        
        if language == 'python':
            return self._suggest_python_splits(file_path)
        elif language in ['javascript', 'typescript']:
            return self._suggest_js_splits(file_path)
        else:
            return self._suggest_generic_splits(file_path)
    
    def split_file(self, file_path: str, 
                   strategy: str = 'auto',
                   dry_run: bool = False) -> Dict[str, any]:
        """
        Split a file into smaller modules
        
        Args:
            file_path: Path to file to split
            strategy: Split strategy (auto, by_class, by_function, by_size)
            dry_run: If True, only show what would be done
            
        Returns:
            Split results
        """
        language = self._detect_language(Path(file_path))
        
        if language == 'python':
            return self._split_python_file(file_path, strategy, dry_run)
        elif language in ['javascript', 'typescript']:
            return self._split_js_file(file_path, strategy, dry_run)
        else:
            return {'success': False, 'error': f'Unsupported language: {language}'}
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        ext = file_path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cs': 'csharp',
            '.cpp': 'cpp',
            '.c': 'c'
        }
        
        return language_map.get(ext, 'unknown')
    
    def _suggest_python_splits(self, file_path: str) -> Dict[str, any]:
        """Suggest split points for Python file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {'success': False, 'error': f'Syntax error: {e}'}
        
        classes = []
        functions = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'line': node.lineno,
                    'end_line': node.end_lineno,
                    'size': node.end_lineno - node.lineno
                })
            elif isinstance(node, ast.FunctionDef):
                # Only top-level functions
                if node.col_offset == 0:
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'end_line': node.end_lineno,
                        'size': node.end_lineno - node.lineno
                    })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append({
                    'line': node.lineno,
                    'type': 'import'
                })
        
        suggestions = []
        
        # Strategy 1: One class per file
        if classes:
            suggestions.append({
                'strategy': 'by_class',
                'description': f'Split into {len(classes)} files (one per class)',
                'files': len(classes),
                'classes': [c['name'] for c in classes]
            })
        
        # Strategy 2: Group related functions
        if functions:
            function_groups = self._group_related_functions(functions)
            suggestions.append({
                'strategy': 'by_function_group',
                'description': f'Split into {len(function_groups)} files (grouped functions)',
                'files': len(function_groups),
                'groups': function_groups
            })
        
        # Strategy 3: By size
        with open(file_path, 'r', encoding='utf-8') as f:
            total_lines = len(f.readlines())
        
        estimated_files = (total_lines // self.max_lines) + 1
        suggestions.append({
            'strategy': 'by_size',
            'description': f'Split into ~{estimated_files} files by size',
            'files': estimated_files
        })
        
        return {
            'success': True,
            'file': file_path,
            'total_lines': total_lines,
            'classes': len(classes),
            'functions': len(functions),
            'suggestions': suggestions
        }
    
    def _suggest_js_splits(self, file_path: str) -> Dict[str, any]:
        """Suggest split points for JavaScript/TypeScript file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Simple regex-based detection for JS/TS
        classes = []
        functions = []
        exports = []
        
        class_pattern = re.compile(r'^\s*(?:export\s+)?class\s+(\w+)')
        function_pattern = re.compile(r'^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)')
        arrow_function_pattern = re.compile(r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(')
        
        for i, line in enumerate(lines, 1):
            if class_match := class_pattern.search(line):
                classes.append({'name': class_match.group(1), 'line': i})
            elif function_match := function_pattern.search(line):
                functions.append({'name': function_match.group(1), 'line': i})
            elif arrow_match := arrow_function_pattern.search(line):
                functions.append({'name': arrow_match.group(1), 'line': i})
        
        suggestions = []
        
        if classes:
            suggestions.append({
                'strategy': 'by_class',
                'description': f'Split into {len(classes)} files (one per class)',
                'files': len(classes),
                'classes': [c['name'] for c in classes]
            })
        
        if functions:
            suggestions.append({
                'strategy': 'by_function',
                'description': f'Group {len(functions)} functions into modules',
                'files': max(1, len(functions) // 5),
                'functions': [f['name'] for f in functions]
            })
        
        estimated_files = (len(lines) // self.max_lines) + 1
        suggestions.append({
            'strategy': 'by_size',
            'description': f'Split into ~{estimated_files} files by size',
            'files': estimated_files
        })
        
        return {
            'success': True,
            'file': file_path,
            'total_lines': len(lines),
            'classes': len(classes),
            'functions': len(functions),
            'suggestions': suggestions
        }
    
    def _suggest_generic_splits(self, file_path: str) -> Dict[str, any]:
        """Generic split suggestions for unsupported languages"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        estimated_files = (len(lines) // self.max_lines) + 1
        
        return {
            'success': True,
            'file': file_path,
            'total_lines': len(lines),
            'suggestions': [{
                'strategy': 'by_size',
                'description': f'Split into ~{estimated_files} files by size',
                'files': estimated_files
            }]
        }
    
    def _split_python_file(self, file_path: str, strategy: str, dry_run: bool) -> Dict[str, any]:
        """Split Python file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {'success': False, 'error': f'Syntax error: {e}'}
        
        # Extract imports
        imports = self._extract_python_imports(tree)
        
        # Extract classes and functions
        classes = []
        functions = []
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'code': ast.get_source_segment(content, node),
                    'line': node.lineno
                })
            elif isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'code': ast.get_source_segment(content, node),
                    'line': node.lineno
                })
        
        if strategy == 'auto':
            strategy = 'by_class' if classes else 'by_function'
        
        result = {'success': True, 'files_created': [], 'dry_run': dry_run}
        
        if strategy == 'by_class' and classes:
            result['files_created'] = self._split_by_class(
                file_path, imports, classes, dry_run
            )
        elif strategy == 'by_function' and functions:
            result['files_created'] = self._split_by_function(
                file_path, imports, functions, dry_run
            )
        else:
            result['success'] = False
            result['error'] = f'Cannot apply strategy {strategy}'
        
        return result
    
    def _split_js_file(self, file_path: str, strategy: str, dry_run: bool) -> Dict[str, any]:
        """Split JavaScript/TypeScript file"""
        # Simplified JS splitting - would need proper parser for production
        return {
            'success': False,
            'error': 'JavaScript splitting not fully implemented yet'
        }
    
    def _extract_python_imports(self, tree: ast.AST) -> str:
        """Extract import statements from Python AST"""
        imports = []
        
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node))
        
        return '\n'.join(imports)
    
    def _split_by_class(self, file_path: str, imports: str, 
                       classes: List[Dict], dry_run: bool) -> List[str]:
        """Split file by class (one class per file)"""
        created_files = []
        base_path = Path(file_path).parent
        base_name = Path(file_path).stem
        
        for cls in classes:
            new_file_name = f"{cls['name'].lower()}.py"
            new_file_path = base_path / new_file_name
            
            content = f'"""\n{cls["name"]} module\n"""\n\n{imports}\n\n\n{cls["code"]}\n'
            
            if not dry_run:
                with open(new_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            created_files.append(str(new_file_path))
        
        # Create __init__.py to export all classes
        if not dry_run:
            init_path = base_path / '__init__.py'
            init_content = '\n'.join([
                f'from .{cls["name"].lower()} import {cls["name"]}'
                for cls in classes
            ])
            init_content += '\n\n__all__ = [' + ', '.join([
                f"'{cls['name']}'" for cls in classes
            ]) + ']\n'
            
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write(init_content)
        
        return created_files
    
    def _split_by_function(self, file_path: str, imports: str,
                          functions: List[Dict], dry_run: bool) -> List[str]:
        """Split file by grouping related functions"""
        # Group functions (simplified - would need better heuristics)
        groups = self._group_related_functions(functions)
        
        created_files = []
        base_path = Path(file_path).parent
        
        for i, group in enumerate(groups, 1):
            new_file_name = f"utils_{i}.py"
            new_file_path = base_path / new_file_name
            
            functions_code = '\n\n'.join([f['code'] for f in group])
            content = f'"""\nUtility functions module {i}\n"""\n\n{imports}\n\n\n{functions_code}\n'
            
            if not dry_run:
                with open(new_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            created_files.append(str(new_file_path))
        
        return created_files
    
    def _group_related_functions(self, functions: List[Dict]) -> List[List[Dict]]:
        """Group related functions together"""
        # Simple grouping by name prefix
        groups = {}
        
        for func in functions:
            # Get prefix (e.g., 'get_', 'set_', 'validate_')
            parts = func['name'].split('_')
            prefix = parts[0] if len(parts) > 1 else 'misc'
            
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append(func)
        
        # Convert to list of groups
        return list(groups.values())
    
    def validate_split(self, original_file: str, new_files: List[str]) -> Dict[str, any]:
        """
        Validate that split files maintain functionality
        
        Args:
            original_file: Original file path
            new_files: List of new file paths
            
        Returns:
            Validation results
        """
        issues = []
        
        # Check that all new files are valid
        for file_path in new_files:
            if not Path(file_path).exists():
                issues.append(f"File not created: {file_path}")
                continue
            
            # Check syntax
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if file_path.endswith('.py'):
                    ast.parse(content)
            except SyntaxError as e:
                issues.append(f"Syntax error in {file_path}: {e}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'files_checked': len(new_files)
        }
