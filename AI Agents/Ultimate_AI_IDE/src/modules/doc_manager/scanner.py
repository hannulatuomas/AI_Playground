"""
Documentation Scanner

Scans project code to extract structure and identify documentation needs.
"""

from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
import ast
import re


@dataclass
class FunctionInfo:
    """Information about a function or method."""
    name: str
    file_path: str
    line_number: int
    docstring: Optional[str]
    parameters: List[str]
    return_type: Optional[str]
    is_public: bool
    is_method: bool = False
    class_name: Optional[str] = None


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    file_path: str
    line_number: int
    docstring: Optional[str]
    methods: List[FunctionInfo] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    is_public: bool = True


@dataclass
class ModuleInfo:
    """Information about a module."""
    name: str
    file_path: str
    docstring: Optional[str]
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)


@dataclass
class CodeStructure:
    """Complete code structure of a project."""
    modules: List[ModuleInfo] = field(default_factory=list)
    undocumented_items: List[str] = field(default_factory=list)
    public_api: List[str] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)


class CodeScanner:
    """Scans project code to extract structure."""
    
    def __init__(self):
        """Initialize code scanner."""
        self.supported_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx'}
    
    def scan_project(self, project_path: str, language: str = 'python') -> CodeStructure:
        """
        Scan project and extract code structure.
        
        Args:
            project_path: Root path of project
            language: Programming language
            
        Returns:
            CodeStructure with project information
        """
        structure = CodeStructure()
        project_root = Path(project_path)
        
        if not project_root.exists():
            return structure
        
        # Find all code files
        code_files = self._find_code_files(project_root, language)
        
        # Scan each file
        for file_path in code_files:
            if language == 'python':
                module_info = self._scan_python_file(file_path)
            elif language in ['javascript', 'typescript']:
                module_info = self._scan_js_file(file_path)
            else:
                continue
            
            if module_info:
                structure.modules.append(module_info)
                
                # Identify public API
                self._identify_public_api(module_info, structure)
                
                # Find undocumented items
                self._find_undocumented(module_info, structure)
        
        # Find entry points
        structure.entry_points = self._find_entry_points(project_root, language)
        
        return structure
    
    def _find_code_files(self, root: Path, language: str) -> List[Path]:
        """Find all code files in project."""
        extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx']
        }
        
        ext_list = extensions.get(language, ['.py'])
        files = []
        
        for ext in ext_list:
            files.extend(root.rglob(f'*{ext}'))
        
        # Filter out common directories to skip
        skip_dirs = {'__pycache__', 'node_modules', '.git', 'venv', 'env', 
                     'build', 'dist', '.pytest_cache'}
        
        return [f for f in files if not any(skip in f.parts for skip in skip_dirs)]
    
    def _scan_python_file(self, file_path: Path) -> Optional[ModuleInfo]:
        """Scan a Python file and extract information."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            module_info = ModuleInfo(
                name=file_path.stem,
                file_path=str(file_path),
                docstring=ast.get_docstring(tree)
            )
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_info.imports.append(node.module)
            
            # Extract classes and functions
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node, str(file_path))
                    module_info.classes.append(class_info)
                elif isinstance(node, ast.FunctionDef):
                    func_info = self._extract_function_info(node, str(file_path))
                    module_info.functions.append(func_info)
            
            return module_info
            
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            return None
    
    def _extract_class_info(self, node: ast.ClassDef, file_path: str) -> ClassInfo:
        """Extract information from a class definition."""
        class_info = ClassInfo(
            name=node.name,
            file_path=file_path,
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            is_public=not node.name.startswith('_')
        )
        
        # Extract base classes
        for base in node.bases:
            if isinstance(base, ast.Name):
                class_info.base_classes.append(base.id)
        
        # Extract methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_function_info(item, file_path, 
                                                         is_method=True, 
                                                         class_name=node.name)
                class_info.methods.append(method_info)
        
        return class_info
    
    def _extract_function_info(self, node: ast.FunctionDef, file_path: str,
                               is_method: bool = False, 
                               class_name: Optional[str] = None) -> FunctionInfo:
        """Extract information from a function definition."""
        # Extract parameters
        params = []
        for arg in node.args.args:
            if arg.arg != 'self' and arg.arg != 'cls':
                params.append(arg.arg)
        
        # Extract return type
        return_type = None
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return_type = node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return_type = str(node.returns.value)
        
        return FunctionInfo(
            name=node.name,
            file_path=file_path,
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            parameters=params,
            return_type=return_type,
            is_public=not node.name.startswith('_'),
            is_method=is_method,
            class_name=class_name
        )
    
    def _scan_js_file(self, file_path: Path) -> Optional[ModuleInfo]:
        """Scan a JavaScript/TypeScript file (basic implementation)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            module_info = ModuleInfo(
                name=file_path.stem,
                file_path=str(file_path),
                docstring=self._extract_js_module_doc(content)
            )
            
            # Basic regex-based extraction for JS/TS
            # Extract function declarations
            func_pattern = r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\('
            for match in re.finditer(func_pattern, content):
                func_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                func_info = FunctionInfo(
                    name=func_name,
                    file_path=str(file_path),
                    line_number=line_num,
                    docstring=None,
                    parameters=[],
                    return_type=None,
                    is_public=True
                )
                module_info.functions.append(func_info)
            
            # Extract class declarations
            class_pattern = r'(?:export\s+)?class\s+(\w+)'
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                class_info = ClassInfo(
                    name=class_name,
                    file_path=str(file_path),
                    line_number=line_num,
                    docstring=None,
                    is_public=True
                )
                module_info.classes.append(class_info)
            
            return module_info
            
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            return None
    
    def _extract_js_module_doc(self, content: str) -> Optional[str]:
        """Extract module-level documentation from JS/TS file."""
        # Look for JSDoc comment at start of file
        jsdoc_pattern = r'^\s*/\*\*\s*(.*?)\s*\*/'
        match = re.search(jsdoc_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    def _identify_public_api(self, module: ModuleInfo, structure: CodeStructure):
        """Identify public API elements."""
        # Public functions
        for func in module.functions:
            if func.is_public:
                structure.public_api.append(f"{module.name}.{func.name}")
        
        # Public classes and their public methods
        for cls in module.classes:
            if cls.is_public:
                structure.public_api.append(f"{module.name}.{cls.name}")
                for method in cls.methods:
                    if method.is_public:
                        structure.public_api.append(
                            f"{module.name}.{cls.name}.{method.name}"
                        )
    
    def _find_undocumented(self, module: ModuleInfo, structure: CodeStructure):
        """Find undocumented code elements."""
        # Check module docstring
        if not module.docstring:
            structure.undocumented_items.append(f"Module: {module.name}")
        
        # Check functions
        for func in module.functions:
            if func.is_public and not func.docstring:
                structure.undocumented_items.append(
                    f"Function: {module.name}.{func.name}"
                )
        
        # Check classes
        for cls in module.classes:
            if cls.is_public and not cls.docstring:
                structure.undocumented_items.append(
                    f"Class: {module.name}.{cls.name}"
                )
            
            # Check methods
            for method in cls.methods:
                if method.is_public and not method.docstring:
                    structure.undocumented_items.append(
                        f"Method: {module.name}.{cls.name}.{method.name}"
                    )
    
    def _find_entry_points(self, root: Path, language: str) -> List[str]:
        """Find entry points in the project."""
        entry_points = []
        
        if language == 'python':
            # Look for __main__.py, main.py, app.py, cli.py
            for name in ['__main__.py', 'main.py', 'app.py', 'cli.py']:
                if (root / name).exists():
                    entry_points.append(str(root / name))
        
        elif language in ['javascript', 'typescript']:
            # Look for index.js, index.ts, main.js, app.js
            for name in ['index.js', 'index.ts', 'main.js', 'app.js', 'server.js']:
                if (root / name).exists():
                    entry_points.append(str(root / name))
        
        return entry_points
