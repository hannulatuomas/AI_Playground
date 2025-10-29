"""
Quality Monitor Module

Monitors code quality and triggers automatic refactoring when needed.
Enforces file size limits, function complexity, and modular architecture.
"""

import os
import ast
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class QualityIssue:
    """Represents a code quality issue."""
    type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    file_path: str
    line_number: Optional[int] = None
    message: str = ""
    suggestion: str = ""
    auto_fixable: bool = False


@dataclass
class QualityMetrics:
    """Code quality metrics for a file."""
    file_path: str
    lines_of_code: int
    num_functions: int
    num_classes: int
    max_function_length: int
    avg_function_length: float
    complexity_score: int
    issues: List[QualityIssue]


class QualityMonitor:
    """Monitors and enforces code quality standards."""
    
    # Quality thresholds
    MAX_FILE_LINES = 500
    MAX_FUNCTION_LINES = 50
    MAX_COMPLEXITY = 10
    MAX_NESTING_DEPTH = 4
    
    def __init__(self, project_path: str):
        """
        Initialize quality monitor.
        
        Args:
            project_path: Path to project root
        """
        self.project_path = Path(project_path)
        self.metrics_cache: Dict[str, QualityMetrics] = {}
    
    def monitor_project(self) -> Dict[str, List[QualityIssue]]:
        """
        Monitor entire project for quality issues.
        
        Returns:
            Dictionary mapping file paths to quality issues
        """
        all_issues = {}
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv', '__pycache__', 'node_modules', 'dist', 'build'}]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    rel_path = str(file_path.relative_to(self.project_path))
                    
                    issues = self.check_file(file_path)
                    if issues:
                        all_issues[rel_path] = issues
        
        logger.info(f"Monitored project: found issues in {len(all_issues)} files")
        return all_issues
    
    def check_file(self, file_path: Path) -> List[QualityIssue]:
        """
        Check a single file for quality issues.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of quality issues
        """
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check file size
            lines = content.split('\n')
            loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            
            if loc > self.MAX_FILE_LINES:
                issues.append(QualityIssue(
                    type='file_too_long',
                    severity='high',
                    file_path=str(file_path),
                    message=f'File has {loc} lines (max: {self.MAX_FILE_LINES})',
                    suggestion='Split file into smaller modules',
                    auto_fixable=False
                ))
            
            # Parse AST for deeper analysis
            try:
                tree = ast.parse(content)
                issues.extend(self._check_ast(tree, file_path))
            except SyntaxError as e:
                issues.append(QualityIssue(
                    type='syntax_error',
                    severity='critical',
                    file_path=str(file_path),
                    line_number=e.lineno,
                    message=f'Syntax error: {e.msg}',
                    suggestion='Fix syntax error',
                    auto_fixable=False
                ))
        
        except Exception as e:
            logger.error(f"Error checking file {file_path}: {e}")
        
        return issues
    
    def _check_ast(self, tree: ast.AST, file_path: Path) -> List[QualityIssue]:
        """Check AST for quality issues."""
        issues = []
        
        for node in ast.walk(tree):
            # Check function length
            if isinstance(node, ast.FunctionDef):
                func_issues = self._check_function(node, file_path)
                issues.extend(func_issues)
            
            # Check class size
            elif isinstance(node, ast.ClassDef):
                class_issues = self._check_class(node, file_path)
                issues.extend(class_issues)
        
        return issues
    
    def _check_function(self, node: ast.FunctionDef, file_path: Path) -> List[QualityIssue]:
        """Check function for quality issues."""
        issues = []
        
        # Calculate function length
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            func_length = node.end_lineno - node.lineno + 1
            
            if func_length > self.MAX_FUNCTION_LINES:
                issues.append(QualityIssue(
                    type='function_too_long',
                    severity='medium',
                    file_path=str(file_path),
                    line_number=node.lineno,
                    message=f'Function "{node.name}" has {func_length} lines (max: {self.MAX_FUNCTION_LINES})',
                    suggestion='Split function into smaller functions',
                    auto_fixable=False
                ))
        
        # Check complexity
        complexity = self._calculate_complexity(node)
        if complexity > self.MAX_COMPLEXITY:
            issues.append(QualityIssue(
                type='high_complexity',
                severity='medium',
                file_path=str(file_path),
                line_number=node.lineno,
                message=f'Function "{node.name}" has complexity {complexity} (max: {self.MAX_COMPLEXITY})',
                suggestion='Simplify function logic',
                auto_fixable=False
            ))
        
        # Check nesting depth
        max_depth = self._calculate_nesting_depth(node)
        if max_depth > self.MAX_NESTING_DEPTH:
            issues.append(QualityIssue(
                type='deep_nesting',
                severity='low',
                file_path=str(file_path),
                line_number=node.lineno,
                message=f'Function "{node.name}" has nesting depth {max_depth} (max: {self.MAX_NESTING_DEPTH})',
                suggestion='Reduce nesting by extracting functions or using early returns',
                auto_fixable=False
            ))
        
        # Check for missing docstring
        if not ast.get_docstring(node):
            issues.append(QualityIssue(
                type='missing_docstring',
                severity='low',
                file_path=str(file_path),
                line_number=node.lineno,
                message=f'Function "{node.name}" is missing a docstring',
                suggestion='Add docstring describing function purpose and parameters',
                auto_fixable=True
            ))
        
        return issues
    
    def _check_class(self, node: ast.ClassDef, file_path: Path) -> List[QualityIssue]:
        """Check class for quality issues."""
        issues = []
        
        # Count methods
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        
        if len(methods) > 20:
            issues.append(QualityIssue(
                type='god_class',
                severity='high',
                file_path=str(file_path),
                line_number=node.lineno,
                message=f'Class "{node.name}" has {len(methods)} methods (consider splitting)',
                suggestion='Split class into smaller, focused classes',
                auto_fixable=False
            ))
        
        # Check for missing docstring
        if not ast.get_docstring(node):
            issues.append(QualityIssue(
                type='missing_docstring',
                severity='low',
                file_path=str(file_path),
                line_number=node.lineno,
                message=f'Class "{node.name}" is missing a docstring',
                suggestion='Add docstring describing class purpose',
                auto_fixable=True
            ))
        
        return issues
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate cyclomatic complexity of a function.
        
        Args:
            node: Function AST node
            
        Returns:
            Complexity score
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Decision points increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _calculate_nesting_depth(self, node: ast.FunctionDef) -> int:
        """
        Calculate maximum nesting depth in a function.
        
        Args:
            node: Function AST node
            
        Returns:
            Maximum nesting depth
        """
        def get_depth(node, current_depth=0):
            max_depth = current_depth
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                    child_depth = get_depth(child, current_depth + 1)
                    max_depth = max(max_depth, child_depth)
                else:
                    child_depth = get_depth(child, current_depth)
                    max_depth = max(max_depth, child_depth)
            
            return max_depth
        
        return get_depth(node)
    
    def calculate_metrics(self, file_path: Path) -> QualityMetrics:
        """
        Calculate quality metrics for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Quality metrics
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            
            tree = ast.parse(content)
            
            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            
            function_lengths = []
            max_func_length = 0
            
            for func in functions:
                if hasattr(func, 'end_lineno') and hasattr(func, 'lineno'):
                    length = func.end_lineno - func.lineno + 1
                    function_lengths.append(length)
                    max_func_length = max(max_func_length, length)
            
            avg_func_length = sum(function_lengths) / len(function_lengths) if function_lengths else 0
            
            # Calculate overall complexity
            complexity = sum(self._calculate_complexity(f) for f in functions)
            
            issues = self.check_file(file_path)
            
            metrics = QualityMetrics(
                file_path=str(file_path),
                lines_of_code=loc,
                num_functions=len(functions),
                num_classes=len(classes),
                max_function_length=max_func_length,
                avg_function_length=avg_func_length,
                complexity_score=complexity,
                issues=issues
            )
            
            self.metrics_cache[str(file_path)] = metrics
            return metrics
        
        except Exception as e:
            logger.error(f"Error calculating metrics for {file_path}: {e}")
            return QualityMetrics(
                file_path=str(file_path),
                lines_of_code=0,
                num_functions=0,
                num_classes=0,
                max_function_length=0,
                avg_function_length=0,
                complexity_score=0,
                issues=[]
            )
    
    def should_trigger_refactoring(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Determine if file should trigger automatic refactoring.
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (should_refactor, reasons)
        """
        metrics = self.calculate_metrics(file_path)
        reasons = []
        
        if metrics.lines_of_code > self.MAX_FILE_LINES:
            reasons.append(f'File exceeds {self.MAX_FILE_LINES} lines ({metrics.lines_of_code} lines)')
        
        if metrics.max_function_length > self.MAX_FUNCTION_LINES:
            reasons.append(f'Contains function exceeding {self.MAX_FUNCTION_LINES} lines ({metrics.max_function_length} lines)')
        
        if metrics.complexity_score > self.MAX_COMPLEXITY * metrics.num_functions:
            reasons.append(f'High overall complexity ({metrics.complexity_score})')
        
        critical_issues = [i for i in metrics.issues if i.severity in {'high', 'critical'}]
        if critical_issues:
            reasons.append(f'{len(critical_issues)} critical quality issues')
        
        return (len(reasons) > 0, reasons)
    
    def generate_refactoring_suggestions(self, file_path: Path) -> List[Dict]:
        """
        Generate specific refactoring suggestions for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        metrics = self.calculate_metrics(file_path)
        
        # File too long - suggest splitting
        if metrics.lines_of_code > self.MAX_FILE_LINES:
            suggestions.append({
                'type': 'split_file',
                'priority': 'high',
                'description': f'Split file into smaller modules (current: {metrics.lines_of_code} lines)',
                'suggestion': self._suggest_file_split(file_path)
            })
        
        # Long functions - suggest extraction
        for issue in metrics.issues:
            if issue.type == 'function_too_long':
                suggestions.append({
                    'type': 'extract_function',
                    'priority': 'medium',
                    'description': issue.message,
                    'suggestion': issue.suggestion,
                    'line': issue.line_number
                })
        
        # High complexity - suggest simplification
        for issue in metrics.issues:
            if issue.type == 'high_complexity':
                suggestions.append({
                    'type': 'simplify_logic',
                    'priority': 'medium',
                    'description': issue.message,
                    'suggestion': issue.suggestion,
                    'line': issue.line_number
                })
        
        return suggestions
    
    def _suggest_file_split(self, file_path: Path) -> str:
        """Suggest how to split a large file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            
            if len(classes) > 1:
                return f"Split into {len(classes)} files, one per class: " + ", ".join([f"{c.name.lower()}.py" for c in classes[:3]])
            else:
                return "Group related functions into separate modules based on functionality"
        
        except:
            return "Split file into logical modules"
    
    def get_project_quality_report(self) -> Dict:
        """
        Generate overall project quality report.
        
        Returns:
            Quality report dictionary
        """
        all_issues = self.monitor_project()
        
        total_issues = sum(len(issues) for issues in all_issues.values())
        severity_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        
        for issues in all_issues.values():
            for issue in issues:
                severity_counts[issue.severity] += 1
        
        files_needing_refactoring = []
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    should_refactor, reasons = self.should_trigger_refactoring(file_path)
                    if should_refactor:
                        files_needing_refactoring.append({
                            'file': str(file_path.relative_to(self.project_path)),
                            'reasons': reasons
                        })
        
        return {
            'total_files_with_issues': len(all_issues),
            'total_issues': total_issues,
            'severity_breakdown': severity_counts,
            'files_needing_refactoring': files_needing_refactoring,
            'quality_score': self._calculate_quality_score(severity_counts, total_issues)
        }
    
    def _calculate_quality_score(self, severity_counts: Dict, total_issues: int) -> float:
        """Calculate overall quality score (0-100)."""
        if total_issues == 0:
            return 100.0
        
        # Weight issues by severity
        weighted_issues = (
            severity_counts['low'] * 1 +
            severity_counts['medium'] * 2 +
            severity_counts['high'] * 4 +
            severity_counts['critical'] * 8
        )
        
        # Calculate score (arbitrary formula)
        max_weighted = total_issues * 8  # If all were critical
        score = max(0, 100 - (weighted_issues / max_weighted * 100))
        
        return round(score, 2)
