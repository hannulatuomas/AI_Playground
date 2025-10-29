"""
Codebase Indexer Module

Indexes project structure, files, classes, functions, and dependencies.
Provides fast search and analysis capabilities for large codebases.
"""

import os
import ast
import json
import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class FileIndex:
    """Index entry for a file."""
    path: str
    language: str
    lines_of_code: int
    classes: List[str]
    functions: List[str]
    imports: List[str]
    exports: List[str]
    last_modified: float
    size_bytes: int


@dataclass
class ClassIndex:
    """Index entry for a class."""
    name: str
    file_path: str
    line_number: int
    methods: List[str]
    base_classes: List[str]
    docstring: Optional[str]


@dataclass
class FunctionIndex:
    """Index entry for a function."""
    name: str
    file_path: str
    line_number: int
    parameters: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    is_async: bool = False


@dataclass
class DependencyEdge:
    """Represents a dependency between files."""
    from_file: str
    to_file: str
    import_type: str  # 'import', 'from_import', 'require', etc.


class CodebaseIndexer:
    """Indexes and analyzes codebase structure."""
    
    SUPPORTED_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cs': 'csharp',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.go': 'go',
        '.rs': 'rust',
    }
    
    def __init__(self, project_path: str):
        """
        Initialize codebase indexer.
        
        Args:
            project_path: Path to project root
        """
        self.project_path = Path(project_path)
        self.file_index: Dict[str, FileIndex] = {}
        self.class_index: Dict[str, List[ClassIndex]] = {}
        self.function_index: Dict[str, List[FunctionIndex]] = {}
        self.dependency_graph: List[DependencyEdge] = []
        self.last_index_time: Optional[float] = None
    
    def index_project(self, incremental: bool = False) -> Dict:
        """
        Index entire project.
        
        Args:
            incremental: Only index changed files
            
        Returns:
            Index statistics
        """
        start_time = datetime.now()
        files_indexed = 0
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in {
                '.git', '.venv', 'venv', '__pycache__', 'node_modules',
                'dist', 'build', '.pytest_cache', '.mypy_cache'
            }]
            
            for file in files:
                ext = Path(file).suffix
                if ext in self.SUPPORTED_EXTENSIONS:
                    file_path = Path(root) / file
                    
                    # Skip if incremental and file hasn't changed
                    if incremental and self._is_file_unchanged(file_path):
                        continue
                    
                    self._index_file(file_path)
                    files_indexed += 1
        
        self.last_index_time = datetime.now().timestamp()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        stats = {
            'files_indexed': files_indexed,
            'total_files': len(self.file_index),
            'total_classes': sum(len(classes) for classes in self.class_index.values()),
            'total_functions': sum(len(funcs) for funcs in self.function_index.values()),
            'total_dependencies': len(self.dependency_graph),
            'duration_seconds': round(duration, 2),
            'incremental': incremental
        }
        
        logger.info(f"Indexed {files_indexed} files in {duration:.2f}s")
        
        return stats
    
    def _is_file_unchanged(self, file_path: Path) -> bool:
        """Check if file has changed since last index."""
        rel_path = str(file_path.relative_to(self.project_path))
        
        if rel_path not in self.file_index:
            return False
        
        current_mtime = file_path.stat().st_mtime
        indexed_mtime = self.file_index[rel_path].last_modified
        
        return current_mtime <= indexed_mtime
    
    def _index_file(self, file_path: Path):
        """Index a single file."""
        rel_path = str(file_path.relative_to(self.project_path))
        ext = file_path.suffix
        language = self.SUPPORTED_EXTENSIONS.get(ext, 'unknown')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count lines of code
            lines = content.split('\n')
            loc = len([l for l in lines if l.strip() and not l.strip().startswith(('#', '//'))])
            
            # Language-specific indexing
            if language == 'python':
                index = self._index_python_file(file_path, content)
            elif language in {'javascript', 'typescript'}:
                index = self._index_js_file(file_path, content)
            else:
                index = FileIndex(
                    path=rel_path,
                    language=language,
                    lines_of_code=loc,
                    classes=[],
                    functions=[],
                    imports=[],
                    exports=[],
                    last_modified=file_path.stat().st_mtime,
                    size_bytes=file_path.stat().st_size
                )
            
            self.file_index[rel_path] = index
            
        except Exception as e:
            logger.error(f"Error indexing {file_path}: {e}")
    
    def _index_python_file(self, file_path: Path, content: str) -> FileIndex:
        """Index Python file."""
        rel_path = str(file_path.relative_to(self.project_path))
        
        try:
            tree = ast.parse(content)
            
            classes = []
            functions = []
            imports = []
            
            # First pass: collect all class names
            class_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_names.add(node.name)
            
            # Second pass: index everything
            for node in tree.body:  # Only top-level nodes
                # Index classes
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    
                    # Index class details
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    base_classes = [self._get_name(base) for base in node.bases]
                    
                    class_idx = ClassIndex(
                        name=node.name,
                        file_path=rel_path,
                        line_number=node.lineno,
                        methods=methods,
                        base_classes=base_classes,
                        docstring=ast.get_docstring(node)
                    )
                    
                    if node.name not in self.class_index:
                        self.class_index[node.name] = []
                    self.class_index[node.name].append(class_idx)
                
                # Index standalone functions (not methods)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node.name)
                    
                    params = [arg.arg for arg in node.args.args]
                    return_type = self._get_annotation(node.returns) if node.returns else None
                    
                    func_idx = FunctionIndex(
                        name=node.name,
                        file_path=rel_path,
                        line_number=node.lineno,
                        parameters=params,
                        return_type=return_type,
                        docstring=ast.get_docstring(node),
                        is_async=isinstance(node, ast.AsyncFunctionDef)
                    )
                    
                    if node.name not in self.function_index:
                        self.function_index[node.name] = []
                    self.function_index[node.name].append(func_idx)
                
                # Index imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                        self._add_dependency(rel_path, alias.name, 'import')
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        self._add_dependency(rel_path, node.module, 'from_import')
            
            lines = content.split('\n')
            loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            
            return FileIndex(
                path=rel_path,
                language='python',
                lines_of_code=loc,
                classes=classes,
                functions=functions,
                imports=imports,
                exports=[],  # Python doesn't have explicit exports
                last_modified=file_path.stat().st_mtime,
                size_bytes=file_path.stat().st_size
            )
        
        except Exception as e:
            logger.error(f"Error parsing Python file {file_path}: {e}")
            return FileIndex(
                path=rel_path,
                language='python',
                lines_of_code=0,
                classes=[],
                functions=[],
                imports=[],
                exports=[],
                last_modified=file_path.stat().st_mtime,
                size_bytes=file_path.stat().st_size
            )
    
    def _index_js_file(self, file_path: Path, content: str) -> FileIndex:
        """Index JavaScript/TypeScript file."""
        rel_path = str(file_path.relative_to(self.project_path))
        
        # Simple regex-based parsing for JS/TS
        classes = re.findall(r'class\s+(\w+)', content)
        functions = re.findall(r'function\s+(\w+)', content)
        functions.extend(re.findall(r'const\s+(\w+)\s*=\s*(?:async\s+)?\(', content))
        
        imports = []
        import_pattern = r"import\s+.*\s+from\s+['\"]([^'\"]+)['\"]"
        imports.extend(re.findall(import_pattern, content))
        
        require_pattern = r"require\(['\"]([^'\"]+)['\"]\)"
        imports.extend(re.findall(require_pattern, content))
        
        exports = []
        export_pattern = r"export\s+(?:default\s+)?(?:class|function|const)\s+(\w+)"
        exports.extend(re.findall(export_pattern, content))
        
        # Add dependencies
        for imp in imports:
            self._add_dependency(rel_path, imp, 'import')
        
        lines = content.split('\n')
        loc = len([l for l in lines if l.strip() and not l.strip().startswith('//')])
        
        return FileIndex(
            path=rel_path,
            language='javascript' if file_path.suffix in {'.js', '.jsx'} else 'typescript',
            lines_of_code=loc,
            classes=classes,
            functions=functions,
            imports=imports,
            exports=exports,
            last_modified=file_path.stat().st_mtime,
            size_bytes=file_path.stat().st_size
        )
    
    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)
    
    def _get_annotation(self, node: Optional[ast.AST]) -> Optional[str]:
        """Get type annotation as string."""
        if node is None:
            return None
        return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
    
    def _add_dependency(self, from_file: str, to_module: str, import_type: str):
        """Add dependency edge."""
        # Try to resolve module to file path
        to_file = self._resolve_module_path(to_module)
        
        edge = DependencyEdge(
            from_file=from_file,
            to_file=to_file,
            import_type=import_type
        )
        
        self.dependency_graph.append(edge)
    
    def _resolve_module_path(self, module: str) -> str:
        """Resolve module name to file path."""
        # Simple resolution - can be enhanced
        if module.startswith('.'):
            return module  # Relative import
        
        # Check if it's a local module
        potential_paths = [
            f"{module.replace('.', '/')}.py",
            f"{module.replace('.', '/')}/__init__.py",
        ]
        
        for path in potential_paths:
            if path in self.file_index:
                return path
        
        return module  # External module
    
    def search_symbol(self, symbol_name: str) -> Dict[str, List]:
        """
        Search for a symbol (class, function, etc.).
        
        Args:
            symbol_name: Symbol to search for
            
        Returns:
            Dictionary with matches
        """
        results = {
            'classes': self.class_index.get(symbol_name, []),
            'functions': self.function_index.get(symbol_name, []),
            'files': []
        }
        
        # Search in file names
        for path in self.file_index.keys():
            if symbol_name.lower() in path.lower():
                results['files'].append(path)
        
        return results
    
    def find_definition(self, symbol_name: str) -> Optional[Dict]:
        """
        Find definition of a symbol.
        
        Args:
            symbol_name: Symbol to find
            
        Returns:
            Definition info or None
        """
        # Check classes
        if symbol_name in self.class_index:
            class_def = self.class_index[symbol_name][0]
            return {
                'type': 'class',
                'file': class_def.file_path,
                'line': class_def.line_number,
                'definition': asdict(class_def)
            }
        
        # Check functions
        if symbol_name in self.function_index:
            func_def = self.function_index[symbol_name][0]
            return {
                'type': 'function',
                'file': func_def.file_path,
                'line': func_def.line_number,
                'definition': asdict(func_def)
            }
        
        return None
    
    def find_usages(self, symbol_name: str) -> List[str]:
        """
        Find files that use a symbol.
        
        Args:
            symbol_name: Symbol to search for
            
        Returns:
            List of file paths
        """
        usages = []
        
        # Search through imports
        for edge in self.dependency_graph:
            if symbol_name in edge.to_file:
                usages.append(edge.from_file)
        
        return list(set(usages))
    
    def get_file_dependencies(self, file_path: str) -> List[str]:
        """
        Get dependencies for a file.
        
        Args:
            file_path: File path
            
        Returns:
            List of dependency file paths
        """
        dependencies = []
        
        for edge in self.dependency_graph:
            if edge.from_file == file_path:
                dependencies.append(edge.to_file)
        
        return dependencies
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular dependencies.
        
        Returns:
            List of circular dependency chains
        """
        circles = []
        visited = set()
        
        def dfs(file: str, path: List[str]):
            if file in path:
                # Found a circle
                circle_start = path.index(file)
                circle = path[circle_start:] + [file]
                if circle not in circles:
                    circles.append(circle)
                return
            
            if file in visited:
                return
            
            visited.add(file)
            path.append(file)
            
            # Follow dependencies
            for edge in self.dependency_graph:
                if edge.from_file == file:
                    dfs(edge.to_file, path.copy())
        
        # Start DFS from each file
        for file_path in self.file_index.keys():
            dfs(file_path, [])
        
        return circles
    
    def get_project_structure(self) -> Dict:
        """
        Get project structure summary.
        
        Returns:
            Structure dictionary
        """
        structure = {
            'total_files': len(self.file_index),
            'by_language': {},
            'total_lines': 0,
            'total_classes': 0,
            'total_functions': 0,
            'largest_files': [],
            'most_complex_files': []
        }
        
        # Count by language
        for file_idx in self.file_index.values():
            lang = file_idx.language
            structure['by_language'][lang] = structure['by_language'].get(lang, 0) + 1
            structure['total_lines'] += file_idx.lines_of_code
        
        structure['total_classes'] = sum(len(classes) for classes in self.class_index.values())
        structure['total_functions'] = sum(len(funcs) for funcs in self.function_index.values())
        
        # Find largest files
        sorted_by_size = sorted(
            self.file_index.values(),
            key=lambda x: x.lines_of_code,
            reverse=True
        )
        structure['largest_files'] = [
            {'path': f.path, 'lines': f.lines_of_code}
            for f in sorted_by_size[:10]
        ]
        
        return structure
    
    def save_index(self, file_path: str):
        """Save index to file."""
        index_data = {
            'file_index': {k: asdict(v) for k, v in self.file_index.items()},
            'class_index': {k: [asdict(c) for c in v] for k, v in self.class_index.items()},
            'function_index': {k: [asdict(f) for f in v] for k, v in self.function_index.items()},
            'dependency_graph': [asdict(e) for e in self.dependency_graph],
            'last_index_time': self.last_index_time
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2)
        
        logger.info(f"Saved index to {file_path}")
    
    def load_index(self, file_path: str):
        """Load index from file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        self.file_index = {k: FileIndex(**v) for k, v in index_data['file_index'].items()}
        self.class_index = {k: [ClassIndex(**c) for c in v] for k, v in index_data['class_index'].items()}
        self.function_index = {k: [FunctionIndex(**f) for f in v] for k, v in index_data['function_index'].items()}
        self.dependency_graph = [DependencyEdge(**e) for e in index_data['dependency_graph']]
        self.last_index_time = index_data.get('last_index_time')
        
        logger.info(f"Loaded index from {file_path}")
