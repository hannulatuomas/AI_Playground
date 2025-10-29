"""
Code Analyzer

Analyzes code quality, complexity, and identifies refactoring opportunities.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
import ast
import re


@dataclass
class ComplexityMetrics:
    """Code complexity metrics."""
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    comment_ratio: float
    function_count: int
    class_count: int


@dataclass
class CodeSmell:
    """Identified code smell."""
    smell_type: str  # 'long_function', 'long_file', 'duplicate', 'complex', etc.
    file_path: str
    line_number: int
    severity: str  # 'low', 'medium', 'high'
    description: str
    suggestion: str


@dataclass
class AnalysisReport:
    """Complete code analysis report."""
    file_path: str
    metrics: ComplexityMetrics
    code_smells: List[CodeSmell] = field(default_factory=list)
    duplicates: List[str] = field(default_factory=list)
    optimization_opportunities: List[str] = field(default_factory=list)
    needs_splitting: bool = False
    suggested_split_points: List[int] = field(default_factory=list)


class CodeAnalyzer:
    """Analyzes code for quality and refactoring opportunities."""
    
    def __init__(self, max_lines: int = 500, max_complexity: int = 10):
        """
        Initialize code analyzer.
        
        Args:
            max_lines: Maximum lines per file before suggesting split
            max_complexity: Maximum cyclomatic complexity threshold
        """
        self.max_lines = max_lines
        self.max_complexity = max_complexity
    
    def analyze_code(self, file_path: str, language: str = 'python') -> AnalysisReport:
        """
        Analyze code file for quality and refactoring needs.
        
        Args:
            file_path: Path to code file
            language: Programming language
            
        Returns:
            AnalysisReport with findings
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if language == 'python':
            return self._analyze_python_file(path)
        elif language in ['javascript', 'typescript']:
            return self._analyze_js_file(path)
        else:
            return self._analyze_generic_file(path)
    
    def _analyze_python_file(self, file_path: Path) -> AnalysisReport:
        """Analyze Python file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Calculate metrics
        metrics = self._calculate_python_metrics(content)
        
        # Create report
        report = AnalysisReport(
            file_path=str(file_path),
            metrics=metrics
        )
        
        # Check if file is too long
        if metrics.lines_of_code > self.max_lines:
            report.needs_splitting = True
            report.code_smells.append(CodeSmell(
                smell_type='long_file',
                file_path=str(file_path),
                line_number=1,
                severity='high',
                description=f'File has {metrics.lines_of_code} lines (max: {self.max_lines})',
                suggestion='Split file into smaller modules'
            ))
            
            # Suggest split points
            report.suggested_split_points = self._find_split_points_python(content)
        
        # Analyze functions for complexity
        try:
            tree = ast.parse(content)
            self._analyze_python_functions(tree, report, str(file_path))
        except SyntaxError:
            report.code_smells.append(CodeSmell(
                smell_type='syntax_error',
                file_path=str(file_path),
                line_number=1,
                severity='high',
                description='File has syntax errors',
                suggestion='Fix syntax errors before refactoring'
            ))
        
        # Find duplicates
        report.duplicates = self._find_duplicates(content)
        
        # Find optimization opportunities
        report.optimization_opportunities = self._find_optimizations_python(content)
        
        return report
    
    def _calculate_python_metrics(self, content: str) -> ComplexityMetrics:
        """Calculate metrics for Python code."""
        lines = content.split('\n')
        
        # Count lines of code (excluding blank and comment lines)
        loc = 0
        comment_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped:
                if stripped.startswith('#'):
                    comment_lines += 1
                else:
                    loc += 1
        
        comment_ratio = comment_lines / max(loc, 1)
        
        # Count functions and classes
        function_count = content.count('def ')
        class_count = content.count('class ')
        
        # Estimate cyclomatic complexity (simplified)
        complexity = self._estimate_cyclomatic_complexity(content)
        
        return ComplexityMetrics(
            cyclomatic_complexity=complexity,
            cognitive_complexity=complexity,  # Simplified
            lines_of_code=loc,
            comment_ratio=comment_ratio,
            function_count=function_count,
            class_count=class_count
        )
    
    def _estimate_cyclomatic_complexity(self, content: str) -> int:
        """Estimate cyclomatic complexity."""
        # Count decision points
        complexity = 1  # Base complexity
        
        keywords = ['if ', 'elif ', 'for ', 'while ', 'and ', 'or ', 
                   'except ', 'with ']
        
        for keyword in keywords:
            complexity += content.count(keyword)
        
        return complexity
    
    def _analyze_python_functions(self, tree: ast.AST, report: AnalysisReport,
                                  file_path: str):
        """Analyze Python functions for complexity."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count lines in function
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                
                # Check if function is too long
                if func_lines > 50:
                    report.code_smells.append(CodeSmell(
                        smell_type='long_function',
                        file_path=file_path,
                        line_number=node.lineno,
                        severity='medium',
                        description=f'Function {node.name} has {func_lines} lines',
                        suggestion='Consider breaking into smaller functions'
                    ))
                
                # Check complexity
                func_complexity = self._calculate_function_complexity(node)
                if func_complexity > self.max_complexity:
                    report.code_smells.append(CodeSmell(
                        smell_type='complex_function',
                        file_path=file_path,
                        line_number=node.lineno,
                        severity='high',
                        description=f'Function {node.name} has complexity {func_complexity}',
                        suggestion='Simplify function logic'
                    ))
                
                # Check for missing docstring
                if not ast.get_docstring(node) and not node.name.startswith('_'):
                    report.code_smells.append(CodeSmell(
                        smell_type='missing_docstring',
                        file_path=file_path,
                        line_number=node.lineno,
                        severity='low',
                        description=f'Function {node.name} lacks docstring',
                        suggestion='Add docstring'
                    ))
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _find_split_points_python(self, content: str) -> List[int]:
        """Find logical points to split Python file."""
        split_points = []
        lines = content.split('\n')
        
        try:
            tree = ast.parse(content)
            
            # Split at class boundaries
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    split_points.append(node.lineno)
                elif isinstance(node, ast.FunctionDef):
                    # Split at top-level functions
                    split_points.append(node.lineno)
        
        except SyntaxError:
            # Fallback: split at empty lines
            for i, line in enumerate(lines):
                if not line.strip() and i > 0:
                    split_points.append(i + 1)
        
        return sorted(split_points)
    
    def _find_duplicates(self, content: str) -> List[str]:
        """Find duplicate code blocks."""
        duplicates = []
        lines = content.split('\n')
        
        # Simple duplicate detection: look for repeated blocks
        block_size = 5
        seen_blocks = {}
        
        for i in range(len(lines) - block_size):
            block = '\n'.join(lines[i:i+block_size])
            block_stripped = block.strip()
            
            if len(block_stripped) > 50:  # Only consider substantial blocks
                if block_stripped in seen_blocks:
                    duplicates.append(f"Lines {i+1}-{i+block_size} duplicate lines {seen_blocks[block_stripped]}")
                else:
                    seen_blocks[block_stripped] = f"{i+1}-{i+block_size}"
        
        return duplicates[:10]  # Limit to 10 duplicates
    
    def _find_optimizations_python(self, content: str) -> List[str]:
        """Find optimization opportunities in Python code."""
        opportunities = []
        
        # Check for inefficient patterns
        if 'for ' in content and ' in range(len(' in content:
            opportunities.append('Use enumerate() instead of range(len())')
        
        if '.append(' in content and 'for ' in content:
            opportunities.append('Consider list comprehension instead of append in loop')
        
        if 'try:' in content and 'except:' in content:
            opportunities.append('Use specific exception types instead of bare except')
        
        if content.count('import ') > 20:
            opportunities.append('Consider organizing imports into groups')
        
        return opportunities
    
    def _analyze_js_file(self, file_path: Path) -> AnalysisReport:
        """Analyze JavaScript/TypeScript file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        loc = len([l for l in lines if l.strip() and not l.strip().startswith('//')])
        
        # Basic metrics
        metrics = ComplexityMetrics(
            cyclomatic_complexity=self._estimate_cyclomatic_complexity(content),
            cognitive_complexity=0,
            lines_of_code=loc,
            comment_ratio=0.0,
            function_count=content.count('function ') + content.count('=>'),
            class_count=content.count('class ')
        )
        
        report = AnalysisReport(
            file_path=str(file_path),
            metrics=metrics
        )
        
        # Check file length
        if loc > self.max_lines:
            report.needs_splitting = True
            report.code_smells.append(CodeSmell(
                smell_type='long_file',
                file_path=str(file_path),
                line_number=1,
                severity='high',
                description=f'File has {loc} lines',
                suggestion='Split into smaller modules'
            ))
        
        return report
    
    def _analyze_generic_file(self, file_path: Path) -> AnalysisReport:
        """Analyze generic code file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        loc = len([l for l in lines if l.strip()])
        
        metrics = ComplexityMetrics(
            cyclomatic_complexity=0,
            cognitive_complexity=0,
            lines_of_code=loc,
            comment_ratio=0.0,
            function_count=0,
            class_count=0
        )
        
        return AnalysisReport(
            file_path=str(file_path),
            metrics=metrics
        )
