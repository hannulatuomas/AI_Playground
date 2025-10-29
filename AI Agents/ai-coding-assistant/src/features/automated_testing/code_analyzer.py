"""
Code Analyzer Module

Analyzes code structure to extract information for test generation.
Supports multiple languages using AST parsing where available.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class Language(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    CSHARP = "csharp"
    CPP = "cpp"
    JAVA = "java"
    UNKNOWN = "unknown"


@dataclass
class ParameterInfo:
    """Information about a function parameter."""
    name: str
    type_hint: Optional[str] = None
    default_value: Optional[str] = None
    is_optional: bool = False


@dataclass
class FunctionInfo:
    """Information about a function or method."""
    name: str
    parameters: List[ParameterInfo] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    is_method: bool = False
    is_static: bool = False
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)
    line_number: int = 0
    complexity: int = 1


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    methods: List[FunctionInfo] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    line_number: int = 0


@dataclass
class CodeAnalysisResult:
    """Result of code analysis."""
    language: Language
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    globals: List[str] = field(default_factory=list)
    file_path: Optional[Path] = None


class CodeAnalyzer:
    """
    Analyzes code to extract structure and metadata for test generation.
    
    Supports:
    - Python: Full AST analysis
    - JavaScript/TypeScript: Regex-based analysis
    - C#/C++: Basic regex-based analysis
    """
    
    def __init__(self):
        """Initialize the code analyzer."""
        self.language_detectors = {
            '.py': Language.PYTHON,
            '.js': Language.JAVASCRIPT,
            '.ts': Language.TYPESCRIPT,
            '.tsx': Language.TYPESCRIPT,
            '.cs': Language.CSHARP,
            '.cpp': Language.CPP,
            '.cc': Language.CPP,
            '.cxx': Language.CPP,
            '.h': Language.CPP,
            '.hpp': Language.CPP,
            '.java': Language.JAVA,
        }
    
    def analyze_file(self, file_path: Path) -> CodeAnalysisResult:
        """
        Analyze a source code file.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            CodeAnalysisResult with extracted information
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Detect language
        language = self._detect_language(file_path)
        
        if language == Language.UNKNOWN:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        # Analyze based on language
        if language == Language.PYTHON:
            return self._analyze_python(code, file_path)
        elif language in (Language.JAVASCRIPT, Language.TYPESCRIPT):
            return self._analyze_javascript(code, file_path, language)
        elif language == Language.CSHARP:
            return self._analyze_csharp(code, file_path)
        elif language == Language.CPP:
            return self._analyze_cpp(code, file_path)
        else:
            return CodeAnalysisResult(language=language, file_path=file_path)
    
    def analyze_code(self, code: str, language: Language) -> CodeAnalysisResult:
        """
        Analyze code from a string.
        
        Args:
            code: Source code as string
            language: Programming language
            
        Returns:
            CodeAnalysisResult with extracted information
        """
        if language == Language.PYTHON:
            return self._analyze_python(code)
        elif language in (Language.JAVASCRIPT, Language.TYPESCRIPT):
            return self._analyze_javascript(code, language=language)
        elif language == Language.CSHARP:
            return self._analyze_csharp(code)
        elif language == Language.CPP:
            return self._analyze_cpp(code)
        else:
            return CodeAnalysisResult(language=language)
    
    def _detect_language(self, file_path: Path) -> Language:
        """Detect programming language from file extension."""
        suffix = file_path.suffix.lower()
        return self.language_detectors.get(suffix, Language.UNKNOWN)
    
    def _analyze_python(
        self,
        code: str,
        file_path: Optional[Path] = None
    ) -> CodeAnalysisResult:
        """
        Analyze Python code using AST.
        
        Args:
            code: Python source code
            file_path: Optional file path
            
        Returns:
            CodeAnalysisResult with full analysis
        """
        result = CodeAnalysisResult(language=Language.PYTHON, file_path=file_path)
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            print(f"Syntax error in Python code: {e}")
            return result
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    result.imports.append(f"{module}.{alias.name}")
        
        # Extract top-level elements
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                func_info = self._extract_python_function(node)
                result.functions.append(func_info)
            elif isinstance(node, ast.ClassDef):
                class_info = self._extract_python_class(node)
                result.classes.append(class_info)
            elif isinstance(node, ast.Assign):
                # Global variables
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        result.globals.append(target.id)
        
        return result
    
    def _extract_python_function(
        self,
        node: ast.FunctionDef,
        is_method: bool = False
    ) -> FunctionInfo:
        """
        Extract information from a Python function AST node.
        
        Args:
            node: AST FunctionDef or AsyncFunctionDef node
            is_method: Whether this is a class method
            
        Returns:
            FunctionInfo object
        """
        func_info = FunctionInfo(
            name=node.name,
            is_method=is_method,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            line_number=node.lineno
        )
        
        # Extract docstring
        if (node.body and isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Constant)):
            func_info.docstring = node.body[0].value.value
        
        # Extract decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                func_info.decorators.append(decorator.id)
                if decorator.id == 'staticmethod':
                    func_info.is_static = True
        
        # Extract parameters
        args = node.args
        defaults = [None] * (len(args.args) - len(args.defaults)) + args.defaults
        
        for arg, default in zip(args.args, defaults):
            param = ParameterInfo(
                name=arg.arg,
                type_hint=ast.unparse(arg.annotation) if arg.annotation else None,
                default_value=ast.unparse(default) if default else None,
                is_optional=default is not None
            )
            func_info.parameters.append(param)
        
        # Extract return type
        if node.returns:
            func_info.return_type = ast.unparse(node.returns)
        
        # Calculate complexity (simple metric: count branches)
        func_info.complexity = self._calculate_complexity(node)
        
        return func_info
    
    def _extract_python_class(self, node: ast.ClassDef) -> ClassInfo:
        """
        Extract information from a Python class AST node.
        
        Args:
            node: AST ClassDef node
            
        Returns:
            ClassInfo object
        """
        class_info = ClassInfo(
            name=node.name,
            line_number=node.lineno
        )
        
        # Extract docstring
        if (node.body and isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Constant)):
            class_info.docstring = node.body[0].value.value
        
        # Extract base classes
        for base in node.bases:
            if isinstance(base, ast.Name):
                class_info.base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                class_info.base_classes.append(ast.unparse(base))
        
        # Extract methods and attributes
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._extract_python_function(item, is_method=True)
                class_info.methods.append(method_info)
            elif isinstance(item, ast.AnnAssign):
                # Class attribute with type annotation
                if isinstance(item.target, ast.Name):
                    class_info.attributes.append(item.target.id)
            elif isinstance(item, ast.Assign):
                # Class attribute without type annotation
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_info.attributes.append(target.id)
        
        return class_info
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity of a function.
        
        Args:
            node: AST node
            
        Returns:
            Complexity score (1 = simple, higher = more complex)
        """
        complexity = 1
        
        for child in ast.walk(node):
            # Each branch adds to complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _analyze_javascript(
        self,
        code: str,
        file_path: Optional[Path] = None,
        language: Language = Language.JAVASCRIPT
    ) -> CodeAnalysisResult:
        """
        Analyze JavaScript/TypeScript code using regex patterns.
        
        Args:
            code: JavaScript/TypeScript source code
            file_path: Optional file path
            language: Language (JAVASCRIPT or TYPESCRIPT)
            
        Returns:
            CodeAnalysisResult with extracted information
        """
        result = CodeAnalysisResult(language=language, file_path=file_path)
        
        # Extract imports
        import_patterns = [
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)',
        ]
        for pattern in import_patterns:
            for match in re.finditer(pattern, code):
                result.imports.append(match.group(1))
        
        # Extract functions
        func_pattern = r'(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(func_pattern, code):
            func_name = match.group(1)
            params_str = match.group(2)
            is_async = 'async' in match.group(0)
            
            # Parse parameters
            parameters = []
            if params_str.strip():
                for param in params_str.split(','):
                    param = param.strip()
                    param_name = param.split(':')[0].strip() if ':' in param else param
                    type_hint = param.split(':')[1].strip() if ':' in param else None
                    parameters.append(ParameterInfo(
                        name=param_name,
                        type_hint=type_hint
                    ))
            
            result.functions.append(FunctionInfo(
                name=func_name,
                parameters=parameters,
                is_async=is_async
            ))
        
        # Extract arrow functions (simple cases)
        arrow_pattern = r'const\s+(\w+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>'
        for match in re.finditer(arrow_pattern, code):
            func_name = match.group(1)
            params_str = match.group(2)
            is_async = 'async' in match.group(0)
            
            parameters = []
            if params_str.strip():
                for param in params_str.split(','):
                    param = param.strip()
                    param_name = param.split(':')[0].strip() if ':' in param else param
                    type_hint = param.split(':')[1].strip() if ':' in param else None
                    parameters.append(ParameterInfo(
                        name=param_name,
                        type_hint=type_hint
                    ))
            
            result.functions.append(FunctionInfo(
                name=func_name,
                parameters=parameters,
                is_async=is_async
            ))
        
        # Extract classes
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            base_class = match.group(2)
            
            class_info = ClassInfo(
                name=class_name,
                base_classes=[base_class] if base_class else []
            )
            result.classes.append(class_info)
        
        return result
    
    def _analyze_csharp(
        self,
        code: str,
        file_path: Optional[Path] = None
    ) -> CodeAnalysisResult:
        """
        Analyze C# code using regex patterns.
        
        Args:
            code: C# source code
            file_path: Optional file path
            
        Returns:
            CodeAnalysisResult with extracted information
        """
        result = CodeAnalysisResult(language=Language.CSHARP, file_path=file_path)
        
        # Extract imports
        using_pattern = r'using\s+([^;]+);'
        for match in re.finditer(using_pattern, code):
            result.imports.append(match.group(1).strip())
        
        # Extract methods
        method_pattern = r'(?:public|private|protected|internal)?\s+(?:static\s+)?(?:async\s+)?(\w+)\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(method_pattern, code):
            return_type = match.group(1)
            method_name = match.group(2)
            params_str = match.group(3)
            is_async = 'async' in match.group(0)
            is_static = 'static' in match.group(0)
            
            # Parse parameters
            parameters = []
            if params_str.strip():
                for param in params_str.split(','):
                    parts = param.strip().split()
                    if len(parts) >= 2:
                        type_hint = parts[0]
                        param_name = parts[1]
                        parameters.append(ParameterInfo(
                            name=param_name,
                            type_hint=type_hint
                        ))
            
            result.functions.append(FunctionInfo(
                name=method_name,
                parameters=parameters,
                return_type=return_type,
                is_async=is_async,
                is_static=is_static
            ))
        
        # Extract classes
        class_pattern = r'(?:public|private|protected|internal)?\s+class\s+(\w+)(?:\s*:\s*([^{]+))?'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            base_classes_str = match.group(2)
            
            base_classes = []
            if base_classes_str:
                base_classes = [bc.strip() for bc in base_classes_str.split(',')]
            
            result.classes.append(ClassInfo(
                name=class_name,
                base_classes=base_classes
            ))
        
        return result
    
    def _analyze_cpp(
        self,
        code: str,
        file_path: Optional[Path] = None
    ) -> CodeAnalysisResult:
        """
        Analyze C++ code using regex patterns.
        
        Args:
            code: C++ source code
            file_path: Optional file path
            
        Returns:
            CodeAnalysisResult with extracted information
        """
        result = CodeAnalysisResult(language=Language.CPP, file_path=file_path)
        
        # Extract includes
        include_pattern = r'#include\s+[<"]([^>"]+)[>"]'
        for match in re.finditer(include_pattern, code):
            result.imports.append(match.group(1))
        
        # Extract functions (simple cases)
        func_pattern = r'(\w+)\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(func_pattern, code):
            return_type = match.group(1)
            func_name = match.group(2)
            params_str = match.group(3)
            
            # Skip common keywords
            if return_type in ('if', 'while', 'for', 'switch', 'class', 'struct'):
                continue
            
            # Parse parameters
            parameters = []
            if params_str.strip():
                for param in params_str.split(','):
                    parts = param.strip().split()
                    if len(parts) >= 2:
                        type_hint = ' '.join(parts[:-1])
                        param_name = parts[-1].strip('*&')
                        parameters.append(ParameterInfo(
                            name=param_name,
                            type_hint=type_hint
                        ))
            
            result.functions.append(FunctionInfo(
                name=func_name,
                parameters=parameters,
                return_type=return_type
            ))
        
        # Extract classes
        class_pattern = r'class\s+(\w+)(?:\s*:\s*(?:public|protected|private)?\s*(\w+))?'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            base_class = match.group(2)
            
            result.classes.append(ClassInfo(
                name=class_name,
                base_classes=[base_class] if base_class else []
            ))
        
        return result
    
    def detect_edge_cases(self, parameters: List[ParameterInfo]) -> List[Dict[str, Any]]:
        """
        Detect edge cases to test based on parameter types.
        
        Args:
            parameters: List of function parameters
            
        Returns:
            List of edge case test scenarios
        """
        edge_cases = []
        
        for param in parameters:
            type_hint = param.type_hint or ""
            
            # Numeric types
            if any(t in type_hint.lower() for t in ['int', 'float', 'double', 'number']):
                edge_cases.append({
                    'name': f'{param.name}_zero',
                    'description': f'Test with {param.name} = 0',
                    'value': 0,
                    'parameter': param.name
                })
                edge_cases.append({
                    'name': f'{param.name}_negative',
                    'description': f'Test with {param.name} < 0',
                    'value': -1,
                    'parameter': param.name
                })
                edge_cases.append({
                    'name': f'{param.name}_large',
                    'description': f'Test with large {param.name}',
                    'value': 1000000,
                    'parameter': param.name
                })
            
            # String types
            elif any(t in type_hint.lower() for t in ['str', 'string']):
                edge_cases.append({
                    'name': f'{param.name}_empty',
                    'description': f'Test with empty {param.name}',
                    'value': '',
                    'parameter': param.name
                })
                edge_cases.append({
                    'name': f'{param.name}_whitespace',
                    'description': f'Test with whitespace {param.name}',
                    'value': '   ',
                    'parameter': param.name
                })
            
            # Collection types
            elif any(t in type_hint.lower() for t in ['list', 'array', 'dict', 'map']):
                edge_cases.append({
                    'name': f'{param.name}_empty',
                    'description': f'Test with empty {param.name}',
                    'value': [] if 'list' in type_hint.lower() or 'array' in type_hint.lower() else {},
                    'parameter': param.name
                })
            
            # Nullable types
            if not param.is_optional and 'Optional' not in type_hint:
                edge_cases.append({
                    'name': f'{param.name}_none',
                    'description': f'Test with None {param.name}',
                    'value': None,
                    'parameter': param.name
                })
        
        return edge_cases


def analyze_code(code: str, language: str) -> CodeAnalysisResult:
    """
    Convenience function to analyze code.
    
    Args:
        code: Source code
        language: Language name as string
        
    Returns:
        CodeAnalysisResult
    """
    lang_map = {
        'python': Language.PYTHON,
        'javascript': Language.JAVASCRIPT,
        'typescript': Language.TYPESCRIPT,
        'csharp': Language.CSHARP,
        'cpp': Language.CPP,
        'c++': Language.CPP,
    }
    
    lang_enum = lang_map.get(language.lower(), Language.UNKNOWN)
    analyzer = CodeAnalyzer()
    return analyzer.analyze_code(code, lang_enum)


if __name__ == "__main__":
    # Test the code analyzer
    test_python_code = """
def calculate_sum(a: int, b: int) -> int:
    '''Calculate the sum of two numbers.'''
    return a + b

class User:
    '''User class.'''
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
    
    def validate(self) -> bool:
        return bool(self.name and '@' in self.email)
"""
    
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_code(test_python_code, Language.PYTHON)
    
    print("Functions found:")
    for func in result.functions:
        print(f"  - {func.name}: {len(func.parameters)} parameters")
    
    print("\nClasses found:")
    for cls in result.classes:
        print(f"  - {cls.name}: {len(cls.methods)} methods")
