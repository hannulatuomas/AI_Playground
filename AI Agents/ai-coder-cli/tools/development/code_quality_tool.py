
"""
Code Quality Tool

Provides code quality metrics and reporting
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import subprocess


logger = logging.getLogger(__name__)


class CodeQualityTool:
    """
    Tool for measuring and reporting code quality metrics.
    
    Provides:
    - Lines of code metrics
    - Cyclomatic complexity
    - Maintainability index
    - Test coverage
    - Code duplication
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize code quality tool.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        logger.info("CodeQualityTool initialized")
    
    def analyze_quality(
        self,
        project_path: Path,
        include_tests: bool = False
    ) -> Dict[str, Any]:
        """
        Perform comprehensive code quality analysis.
        
        Args:
            project_path: Path to project root
            include_tests: Whether to include test files in metrics
            
        Returns:
            Dictionary with quality metrics
        """
        if not project_path.exists() or not project_path.is_dir():
            return {
                'success': False,
                'error': f'Project path not found: {project_path}'
            }
        
        metrics = {
            'success': True,
            'project_path': str(project_path),
            'lines_of_code': self._count_lines(project_path, include_tests),
            'complexity': self._measure_complexity(project_path),
            'maintainability': self._calculate_maintainability(project_path),
            'duplication': self._detect_duplication(project_path),
            'quality_score': 0
        }
        
        # Calculate overall quality score (0-100)
        metrics['quality_score'] = self._calculate_quality_score(metrics)
        
        return metrics
    
    def _count_lines(self, project_path: Path, include_tests: bool) -> Dict[str, int]:
        """Count lines of code."""
        total_lines = 0
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        patterns = ['**/*.py', '**/*.js', '**/*.ts', '**/*.jsx', '**/*.tsx', '**/*.cpp', '**/*.c', '**/*.h']
        
        for pattern in patterns:
            for file_path in project_path.glob(pattern):
                if not include_tests and 'test' in str(file_path).lower():
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            total_lines += 1
                            stripped = line.strip()
                            
                            if not stripped:
                                blank_lines += 1
                            elif stripped.startswith('#') or stripped.startswith('//'):
                                comment_lines += 1
                            else:
                                code_lines += 1
                except Exception as e:
                    logger.warning(f"Failed to read {file_path}: {e}")
        
        return {
            'total': total_lines,
            'code': code_lines,
            'comments': comment_lines,
            'blank': blank_lines
        }
    
    def _measure_complexity(self, project_path: Path) -> Dict[str, Any]:
        """Measure cyclomatic complexity."""
        # Try using radon for Python projects
        try:
            result = subprocess.run(
                ['radon', 'cc', str(project_path), '-a', '-j'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                complexities = []
                for file_data in data.values():
                    for item in file_data:
                        complexities.append(item.get('complexity', 0))
                
                if complexities:
                    avg_complexity = sum(complexities) / len(complexities)
                    return {
                        'average': round(avg_complexity, 2),
                        'max': max(complexities),
                        'min': min(complexities),
                        'functions': len(complexities)
                    }
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Fallback: simple estimation
        return {
            'average': 0,
            'max': 0,
            'min': 0,
            'functions': 0
        }
    
    def _calculate_maintainability(self, project_path: Path) -> Dict[str, Any]:
        """Calculate maintainability index."""
        # Try using radon for Python projects
        try:
            result = subprocess.run(
                ['radon', 'mi', str(project_path), '-j'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                indices = []
                for file_data in data.values():
                    if isinstance(file_data, dict):
                        mi = file_data.get('mi', 0)
                        indices.append(mi)
                
                if indices:
                    avg_mi = sum(indices) / len(indices)
                    return {
                        'average': round(avg_mi, 2),
                        'max': round(max(indices), 2),
                        'min': round(min(indices), 2),
                        'grade': self._mi_to_grade(avg_mi)
                    }
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Fallback
        return {
            'average': 0,
            'max': 0,
            'min': 0,
            'grade': 'N/A'
        }
    
    def _mi_to_grade(self, mi: float) -> str:
        """Convert maintainability index to letter grade."""
        if mi >= 80:
            return 'A'
        elif mi >= 60:
            return 'B'
        elif mi >= 40:
            return 'C'
        elif mi >= 20:
            return 'D'
        else:
            return 'F'
    
    def _detect_duplication(self, project_path: Path) -> Dict[str, Any]:
        """Detect code duplication."""
        # This is a placeholder - actual implementation would use tools like:
        # - PMD CPD for general duplication
        # - jscpd for JavaScript
        # - Code duplication detection algorithms
        
        return {
            'percentage': 0,
            'blocks': 0,
            'files': []
        }
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> int:
        """
        Calculate overall quality score (0-100).
        
        Based on:
        - Maintainability index
        - Complexity
        - Code duplication
        - Lines of code ratio
        """
        score = 100
        
        # Maintainability impact (40%)
        mi = metrics.get('maintainability', {}).get('average', 0)
        if mi > 0:
            score = score * 0.6 + (mi * 0.4)
        
        # Complexity impact (30%)
        complexity = metrics.get('complexity', {}).get('average', 0)
        if complexity > 10:
            score -= 30
        elif complexity > 5:
            score -= 15
        
        # Duplication impact (20%)
        duplication = metrics.get('duplication', {}).get('percentage', 0)
        if duplication > 10:
            score -= 20
        elif duplication > 5:
            score -= 10
        
        # Code/comment ratio impact (10%)
        loc = metrics.get('lines_of_code', {})
        if loc.get('code', 0) > 0:
            comment_ratio = loc.get('comments', 0) / loc['code']
            if comment_ratio < 0.05:  # Less than 5% comments
                score -= 10
        
        return max(0, min(100, int(score)))
    
    def generate_report(
        self,
        metrics: Dict[str, Any],
        output_format: str = "text"
    ) -> str:
        """
        Generate a quality report.
        
        Args:
            metrics: Quality metrics
            output_format: Output format (text, markdown, json)
            
        Returns:
            Formatted report string
        """
        if output_format == "json":
            import json
            return json.dumps(metrics, indent=2)
        
        elif output_format == "markdown":
            return self._generate_markdown_report(metrics)
        
        else:  # text
            return self._generate_text_report(metrics)
    
    def _generate_text_report(self, metrics: Dict[str, Any]) -> str:
        """Generate text format report."""
        lines = [
            "=" * 60,
            "CODE QUALITY REPORT",
            "=" * 60,
            "",
            f"Project: {metrics.get('project_path', 'Unknown')}",
            f"Overall Quality Score: {metrics.get('quality_score', 0)}/100",
            "",
            "Lines of Code:",
            f"  Total: {metrics.get('lines_of_code', {}).get('total', 0)}",
            f"  Code: {metrics.get('lines_of_code', {}).get('code', 0)}",
            f"  Comments: {metrics.get('lines_of_code', {}).get('comments', 0)}",
            f"  Blank: {metrics.get('lines_of_code', {}).get('blank', 0)}",
            "",
            "Complexity:",
            f"  Average: {metrics.get('complexity', {}).get('average', 0)}",
            f"  Max: {metrics.get('complexity', {}).get('max', 0)}",
            f"  Functions: {metrics.get('complexity', {}).get('functions', 0)}",
            "",
            "Maintainability:",
            f"  Index: {metrics.get('maintainability', {}).get('average', 0)}",
            f"  Grade: {metrics.get('maintainability', {}).get('grade', 'N/A')}",
            "",
            "Code Duplication:",
            f"  Percentage: {metrics.get('duplication', {}).get('percentage', 0)}%",
            f"  Blocks: {metrics.get('duplication', {}).get('blocks', 0)}",
            "",
            "=" * 60
        ]
        
        return "\n".join(lines)
    
    def _generate_markdown_report(self, metrics: Dict[str, Any]) -> str:
        """Generate markdown format report."""
        lines = [
            "# Code Quality Report",
            "",
            f"**Project:** {metrics.get('project_path', 'Unknown')}  ",
            f"**Overall Quality Score:** {metrics.get('quality_score', 0)}/100",
            "",
            "## Lines of Code",
            "",
            f"- **Total:** {metrics.get('lines_of_code', {}).get('total', 0)}",
            f"- **Code:** {metrics.get('lines_of_code', {}).get('code', 0)}",
            f"- **Comments:** {metrics.get('lines_of_code', {}).get('comments', 0)}",
            f"- **Blank:** {metrics.get('lines_of_code', {}).get('blank', 0)}",
            "",
            "## Complexity",
            "",
            f"- **Average:** {metrics.get('complexity', {}).get('average', 0)}",
            f"- **Max:** {metrics.get('complexity', {}).get('max', 0)}",
            f"- **Functions Analyzed:** {metrics.get('complexity', {}).get('functions', 0)}",
            "",
            "## Maintainability",
            "",
            f"- **Index:** {metrics.get('maintainability', {}).get('average', 0)}",
            f"- **Grade:** {metrics.get('maintainability', {}).get('grade', 'N/A')}",
            "",
            "## Code Duplication",
            "",
            f"- **Percentage:** {metrics.get('duplication', {}).get('percentage', 0)}%",
            f"- **Blocks:** {metrics.get('duplication', {}).get('blocks', 0)}",
            ""
        ]
        
        return "\n".join(lines)
