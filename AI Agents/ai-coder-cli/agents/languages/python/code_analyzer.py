
"""
Python-Specific Code Analyzer Agent

This agent specializes in analyzing Python code with awareness of:
- PEP 8 style guidelines
- Python complexity metrics
- Security vulnerabilities (bandit)
- Performance patterns
- Type hint usage
"""

import ast
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

from ...base import CodeAnalyzerBase


class PythonCodeAnalyzerAgent(CodeAnalyzerBase):
    """
    Agent specialized for Python code analysis.
    
    Features:
    - AST-based analysis
    - PEP 8 compliance checking
    - Cyclomatic complexity calculation
    - Security vulnerability detection
    - Performance anti-pattern detection
    - Type hint analysis
    """
    
    def __init__(
        self,
        name: str = "code_analyzer_python",
        description: str = "Python-specific code analysis agent",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            primary_language="Python",
            **kwargs
        )
    
    def _analyze_code_quality(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Python code quality.
        """
        issues = []
        score = 100
        
        try:
            # Parse AST
            tree = ast.parse(code)
            
            # Check for docstrings
            has_module_docstring = ast.get_docstring(tree) is not None
            if not has_module_docstring:
                issues.append({
                    'type': 'documentation',
                    'severity': 'warning',
                    'message': 'Module missing docstring',
                    'line': 1
                })
                score -= 10
            
            # Analyze functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for docstring
                    if not ast.get_docstring(node):
                        issues.append({
                            'type': 'documentation',
                            'severity': 'warning',
                            'message': f'Function {node.name} missing docstring',
                            'line': node.lineno
                        })
                        score -= 5
                    
                    # Check for too many arguments
                    if len(node.args.args) > 5:
                        issues.append({
                            'type': 'complexity',
                            'severity': 'warning',
                            'message': f'Function {node.name} has too many parameters ({len(node.args.args)})',
                            'line': node.lineno
                        })
                        score -= 5
                
                elif isinstance(node, ast.ClassDef):
                    # Check for docstring
                    if not ast.get_docstring(node):
                        issues.append({
                            'type': 'documentation',
                            'severity': 'warning',
                            'message': f'Class {node.name} missing docstring',
                            'line': node.lineno
                        })
                        score -= 5
            
        except SyntaxError as e:
            issues.append({
                'type': 'syntax',
                'severity': 'critical',
                'message': f'Syntax error: {str(e)}',
                'line': e.lineno if hasattr(e, 'lineno') else 0
            })
            score -= 50
        
        # Check PEP 8 line length
        lines = code.split('\n')
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 79]
        if long_lines:
            issues.append({
                'type': 'style',
                'severity': 'info',
                'message': f'Lines exceed 79 characters (PEP 8): {len(long_lines)} lines',
                'lines': long_lines[:5]
            })
            score -= min(10, len(long_lines))
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': [
                'Add docstrings to all modules, classes, and functions',
                'Follow PEP 8 style guide (79 characters per line)',
                'Keep functions small with fewer than 5 parameters',
                'Use type hints for function parameters and return values',
            ]
        }
    
    def _calculate_complexity(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Python code complexity metrics.
        """
        try:
            tree = ast.parse(code)
            
            # Count lines of code
            lines = [l for l in code.split('\n') if l.strip() and not l.strip().startswith('#')]
            loc = len(lines)
            
            # Count functions and classes
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'complexity': complexity
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': len([n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)])
                    })
            
            # Calculate average complexity
            avg_complexity = sum(f['complexity'] for f in functions) / len(functions) if functions else 0
            max_complexity = max((f['complexity'] for f in functions), default=0)
            
            # Determine score
            score = 100
            if avg_complexity > 10:
                score -= 30
            elif avg_complexity > 5:
                score -= 15
            
            if loc > 1000:
                score -= 20
            elif loc > 500:
                score -= 10
            
            issues = []
            if max_complexity > 15:
                complex_funcs = [f for f in functions if f['complexity'] > 15]
                issues.append({
                    'type': 'complexity',
                    'severity': 'warning',
                    'message': f'High complexity functions: {", ".join(f["name"] for f in complex_funcs[:3])}'
                })
            
            return {
                'score': max(0, score),
                'metrics': {
                    'lines_of_code': loc,
                    'functions': len(functions),
                    'classes': len(classes),
                    'average_complexity': round(avg_complexity, 2),
                    'max_complexity': max_complexity,
                    'maintainability_index': self._calculate_python_maintainability(loc, avg_complexity)
                },
                'issues': issues,
                'recommendations': [
                    'Break down complex functions (complexity > 10)',
                    'Keep files under 500 lines of code',
                    'Extract reusable code into separate functions',
                ]
            }
            
        except SyntaxError:
            return {
                'score': 0,
                'metrics': {},
                'issues': [{'type': 'syntax', 'severity': 'critical', 'message': 'Cannot parse code'}],
                'recommendations': ['Fix syntax errors before analyzing complexity']
            }
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1
        
        for child in ast.walk(node):
            # Count decision points
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _calculate_python_maintainability(self, loc: int, avg_complexity: float) -> int:
        """Calculate maintainability index for Python code."""
        if loc == 0:
            return 100
        
        # Simplified maintainability index
        volume = loc * 2.4
        mi = 171 - 5.2 * (volume ** 0.23) - 0.23 * avg_complexity - 16.2 * (loc ** 0.34)
        mi = max(0, min(100, mi))
        return int(mi)
    
    def _check_security(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for Python security issues.
        """
        issues = []
        score = 100
        
        # Security anti-patterns
        security_patterns = [
            (r'eval\s*\(', 'Use of eval() - code injection risk', 'critical'),
            (r'exec\s*\(', 'Use of exec() - code injection risk', 'critical'),
            (r'pickle\.loads?\(', 'Use of pickle - arbitrary code execution risk', 'warning'),
            (r'os\.system\(', 'Use of os.system() - command injection risk', 'warning'),
            (r'subprocess\..*shell=True', 'Use of shell=True - command injection risk', 'warning'),
            (r'password\s*=\s*["\']', 'Hardcoded password detected', 'critical'),
            (r'api[_-]?key\s*=\s*["\'][^"\']{10,}', 'Hardcoded API key detected', 'critical'),
            (r'SECRET_KEY\s*=\s*["\']', 'Hardcoded secret key', 'critical'),
            (r'\.format\(.*sql', 'Possible SQL injection - use parameterized queries', 'warning'),
        ]
        
        for pattern, message, severity in security_patterns:
            matches = list(re.finditer(pattern, code, re.IGNORECASE))
            if matches:
                lines = [code[:m.start()].count('\n') + 1 for m in matches]
                issues.append({
                    'type': 'security',
                    'severity': severity,
                    'message': message,
                    'lines': lines
                })
                
                if severity == 'critical':
                    score -= 20
                else:
                    score -= 10
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': [
                'Never use eval() or exec() on untrusted input',
                'Use parameterized queries to prevent SQL injection',
                'Avoid pickle for untrusted data',
                'Never hardcode credentials or secrets',
                'Use environment variables for sensitive data',
                'Validate and sanitize all user inputs',
            ]
        }
    
    def _analyze_performance(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Python performance issues.
        """
        issues = []
        score = 100
        
        # Performance anti-patterns
        patterns = [
            (r'for\s+.*:\s*\n\s+for\s+.*:', 'Nested loops - consider list comprehension or numpy', 'warning'),
            (r'\.append\(.*\)\s*#.*loop', 'List append in loop - consider list comprehension', 'info'),
            (r'\+\s*=\s*["\'].*for', 'String concatenation in loop - use join()', 'warning'),
            (r'global\s+\w+', 'Use of global variables - impacts performance', 'info'),
        ]
        
        for pattern, message, severity in patterns:
            matches = list(re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE))
            if matches:
                lines = [code[:m.start()].count('\n') + 1 for m in matches]
                issues.append({
                    'type': 'performance',
                    'severity': severity,
                    'message': message,
                    'lines': lines
                })
                
                if severity == 'warning':
                    score -= 10
                else:
                    score -= 5
        
        # Check for inefficient data structures
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # Check for list when set might be better
                if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name):
                    if any(isinstance(op, ast.In) for op in node.ops):
                        issues.append({
                            'type': 'performance',
                            'severity': 'info',
                            'message': 'Consider using set instead of list for membership tests',
                            'line': node.lineno
                        })
                        score -= 5
        except:
            pass
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': [
                'Use list comprehensions instead of loops where possible',
                'Use join() for string concatenation in loops',
                'Consider numpy for numerical operations',
                'Use generators for large datasets',
                'Profile code to identify actual bottlenecks',
            ]
        }
    
    def _check_best_practices(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check Python best practices adherence.
        """
        issues = []
        score = 100
        
        try:
            tree = ast.parse(code)
            
            # Check for type hints
            functions_without_hints = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    has_hints = node.returns is not None or any(arg.annotation for arg in node.args.args)
                    if not has_hints:
                        functions_without_hints.append(node.name)
            
            if functions_without_hints:
                issues.append({
                    'type': 'typing',
                    'severity': 'info',
                    'message': f'Functions without type hints: {", ".join(functions_without_hints[:5])}'
                })
                score -= 10
            
            # Check for bare except
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues.append({
                            'type': 'error_handling',
                            'severity': 'warning',
                            'message': 'Bare except clause - catch specific exceptions',
                            'line': node.lineno
                        })
                        score -= 10
            
        except SyntaxError:
            pass
        
        # Check for print statements (should use logging)
        print_matches = list(re.finditer(r'\bprint\s*\(', code))
        if len(print_matches) > 3:
            issues.append({
                'type': 'best_practice',
                'severity': 'info',
                'message': f'Multiple print statements ({len(print_matches)}) - consider using logging module'
            })
            score -= 5
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': [
                'Add type hints to functions for better code clarity',
                'Catch specific exceptions instead of bare except',
                'Use logging module instead of print statements',
                'Follow PEP 8 style guide',
                'Write docstrings for all public APIs',
            ]
        }
    
    def _get_language_directory(self) -> Optional[Path]:
        """Get the Python language directory."""
        return Path(__file__).parent

