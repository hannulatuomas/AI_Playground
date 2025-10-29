"""
Code Validation Module

Validates generated code for syntax and style.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of code validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    
    def __init__(self):
        self.valid = True
        self.errors = []
        self.warnings = []
        self.suggestions = []


class CodeValidator:
    """Validates code quality and correctness."""
    
    def __init__(self):
        """Initialize validator."""
        self.max_line_length = 100
        self.max_file_lines = 500
    
    def validate_code(self, code: str, language: str) -> ValidationResult:
        """
        Validate code for syntax and style.
        
        Args:
            code: Code to validate
            language: Programming language
            
        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult()
        
        # Syntax validation
        if language == 'python':
            self._validate_python_syntax(code, result)
        elif language in ['javascript', 'typescript']:
            self._validate_js_syntax(code, result)
        
        # Style validation (common for all languages)
        self._validate_style(code, result)
        
        # Best practices
        self._check_best_practices(code, language, result)
        
        return result
    
    def validate_file(self, file_path: str, language: str) -> ValidationResult:
        """
        Validate a file.
        
        Args:
            file_path: Path to file
            language: Programming language
            
        Returns:
            ValidationResult
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.validate_code(code, language)
        except Exception as e:
            result = ValidationResult()
            result.valid = False
            result.errors.append(f"Cannot read file: {e}")
            return result
    
    def _validate_python_syntax(self, code: str, result: ValidationResult):
        """Validate Python syntax."""
        try:
            ast.parse(code)
        except SyntaxError as e:
            result.valid = False
            result.errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            result.valid = False
            result.errors.append(f"Parse error: {str(e)}")
    
    def _validate_js_syntax(self, code: str, result: ValidationResult):
        """Validate JavaScript/TypeScript syntax (basic)."""
        # Basic checks (would need proper parser for full validation)
        
        # Check for unmatched braces
        brace_count = code.count('{') - code.count('}')
        if brace_count != 0:
            result.warnings.append(f"Unmatched braces: {abs(brace_count)} {'opening' if brace_count > 0 else 'closing'}")
        
        # Check for unmatched parentheses
        paren_count = code.count('(') - code.count(')')
        if paren_count != 0:
            result.warnings.append(f"Unmatched parentheses: {abs(paren_count)} {'opening' if paren_count > 0 else 'closing'}")
    
    def _validate_style(self, code: str, result: ValidationResult):
        """Validate code style."""
        lines = code.split('\n')
        
        # Check file length
        if len(lines) > self.max_file_lines:
            result.warnings.append(
                f"File has {len(lines)} lines (recommended: <{self.max_file_lines}). "
                "Consider splitting into multiple files."
            )
        
        # Check line length
        long_lines = []
        for i, line in enumerate(lines, 1):
            if len(line) > self.max_line_length:
                long_lines.append(i)
        
        if long_lines:
            result.warnings.append(
                f"Lines exceed {self.max_line_length} characters: "
                f"{', '.join(map(str, long_lines[:5]))}"
                f"{' and more' if len(long_lines) > 5 else ''}"
            )
        
        # Check for trailing whitespace
        trailing_ws = [i for i, line in enumerate(lines, 1) 
                      if line and line[-1].isspace()]
        if trailing_ws:
            result.suggestions.append(
                f"Remove trailing whitespace on lines: "
                f"{', '.join(map(str, trailing_ws[:5]))}"
            )
    
    def _check_best_practices(self, code: str, language: str, 
                             result: ValidationResult):
        """Check for best practices."""
        if language == 'python':
            self._check_python_best_practices(code, result)
        elif language in ['javascript', 'typescript']:
            self._check_js_best_practices(code, result)
    
    def _check_python_best_practices(self, code: str, 
                                    result: ValidationResult):
        """Check Python best practices."""
        # Check for docstrings
        if 'def ' in code or 'class ' in code:
            if '"""' not in code and "'''" not in code:
                result.suggestions.append(
                    "Add docstrings to classes and functions"
                )
        
        # Check for type hints
        if 'def ' in code:
            functions = re.findall(r'def\s+\w+\([^)]*\)', code)
            functions_with_hints = [f for f in functions if '->' in f or ':' in f]
            
            if len(functions_with_hints) < len(functions) * 0.5:
                result.suggestions.append(
                    "Consider adding type hints to function signatures"
                )
        
        # Check for bare except
        if re.search(r'except\s*:', code):
            result.warnings.append(
                "Avoid bare 'except:' clauses. Specify exception types."
            )
    
    def _check_js_best_practices(self, code: str, 
                                result: ValidationResult):
        """Check JavaScript/TypeScript best practices."""
        # Check for var usage
        if re.search(r'\bvar\s+', code):
            result.suggestions.append(
                "Use 'const' or 'let' instead of 'var'"
            )
        
        # Check for console.log in production code
        console_logs = len(re.findall(r'console\.log', code))
        if console_logs > 3:
            result.suggestions.append(
                f"Remove or reduce console.log statements ({console_logs} found)"
            )
        
        # Check for proper error handling
        if 'async ' in code and 'try' not in code:
            result.suggestions.append(
                "Add error handling (try/catch) for async functions"
            )
    
    def check_imports(self, code: str, language: str) -> List[str]:
        """
        Extract and validate imports.
        
        Args:
            code: Code to check
            language: Programming language
            
        Returns:
            List of import issues
        """
        issues = []
        
        if language == 'python':
            # Check for unused imports (basic check)
            imports = re.findall(r'import\s+([\w.]+)', code)
            for imp in imports:
                if code.count(imp) == 1:  # Only appears in import
                    issues.append(f"Potentially unused import: {imp}")
        
        return issues
    
    def check_complexity(self, code: str) -> Dict[str, int]:
        """
        Check code complexity metrics.
        
        Args:
            code: Code to analyze
            
        Returns:
            Dictionary with complexity metrics
        """
        metrics = {
            'lines': len(code.split('\n')),
            'functions': len(re.findall(r'\bdef\s+\w+|\bfunction\s+\w+', code)),
            'classes': len(re.findall(r'\bclass\s+\w+', code)),
            'max_nesting': self._calculate_max_nesting(code),
        }
        
        return metrics
    
    def _calculate_max_nesting(self, code: str) -> int:
        """Calculate maximum nesting level."""
        max_nesting = 0
        current_nesting = 0
        
        for line in code.split('\n'):
            stripped = line.strip()
            
            # Increase nesting
            if stripped.endswith(':') or stripped.endswith('{'):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            
            # Decrease nesting
            if stripped.startswith('}') or (stripped and 
                len(line) - len(line.lstrip()) < current_nesting * 4):
                current_nesting = max(0, current_nesting - 1)
        
        return max_nesting
