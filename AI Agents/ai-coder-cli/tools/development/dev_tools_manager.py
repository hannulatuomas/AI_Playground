"""
Development Tools Manager

Coordinates all development tools (linters, formatters, analyzers, quality metrics).
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from .linter_tool import LinterTool
from .formatter_tool import FormatterTool
from .static_analyzer_tool import StaticAnalyzerTool
from .code_quality_tool import CodeQualityTool


logger = logging.getLogger(__name__)


class DevToolsManager:
    """
    Central manager for all development tools.
    
    Provides unified interface for:
    - Code linting
    - Code formatting
    - Static analysis
    - Quality metrics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize development tools manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Initialize tools
        self.linter = LinterTool(config.get('linter', {}))
        self.formatter = FormatterTool(config.get('formatter', {}))
        self.analyzer = StaticAnalyzerTool(config.get('analyzer', {}))
        self.quality = CodeQualityTool(config.get('quality', {}))
        
        logger.info("DevToolsManager initialized")
    
    def run_full_check(
        self,
        target_path: Path,
        language: Optional[str] = None,
        fix_issues: bool = False
    ) -> Dict[str, Any]:
        """
        Run full suite of development tools on a target.
        
        Args:
            target_path: Path to file or directory
            language: Programming language
            fix_issues: Whether to auto-fix issues (formatting, etc.)
            
        Returns:
            Dictionary with all results
        """
        results = {
            'target_path': str(target_path),
            'language': language,
            'checks': {}
        }
        
        # Determine if target is file or directory
        is_file = target_path.is_file()
        
        # 1. Linting
        logger.info("Running linter...")
        if is_file:
            results['checks']['lint'] = self.linter.lint_file(
                target_path,
                language=language
            )
        else:
            results['checks']['lint'] = self.linter.lint_directory(
                target_path,
                language=language
            )
        
        # 2. Formatting
        logger.info("Running formatter...")
        if is_file:
            results['checks']['format'] = self.formatter.format_file(
                target_path,
                language=language,
                dry_run=not fix_issues
            )
        else:
            results['checks']['format'] = self.formatter.format_directory(
                target_path,
                language=language,
                dry_run=not fix_issues
            )
        
        # 3. Static Analysis
        logger.info("Running static analysis...")
        if is_file:
            results['checks']['static_analysis'] = self.analyzer.analyze_file(
                target_path,
                language=language
            )
        else:
            results['checks']['static_analysis'] = self.analyzer.analyze_directory(
                target_path,
                language=language
            )
        
        # 4. Quality Metrics (directory only)
        if not is_file:
            logger.info("Calculating quality metrics...")
            results['checks']['quality'] = self.quality.analyze_quality(
                target_path
            )
        
        # Generate summary
        results['summary'] = self._generate_summary(results['checks'])
        
        return results
    
    def lint(
        self,
        target_path: Path,
        language: Optional[str] = None,
        linter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run linter on target.
        
        Args:
            target_path: Path to file or directory
            language: Programming language
            linter: Specific linter to use
            
        Returns:
            Lint results
        """
        if target_path.is_file():
            return self.linter.lint_file(target_path, language, linter)
        else:
            return self.linter.lint_directory(target_path, language, linter)
    
    def format(
        self,
        target_path: Path,
        language: Optional[str] = None,
        formatter: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Format code.
        
        Args:
            target_path: Path to file or directory
            language: Programming language
            formatter: Specific formatter to use
            dry_run: Check only, don't modify
            
        Returns:
            Format results
        """
        if target_path.is_file():
            return self.formatter.format_file(target_path, language, formatter, dry_run)
        else:
            return self.formatter.format_directory(target_path, language, formatter, dry_run)
    
    def analyze(
        self,
        target_path: Path,
        language: Optional[str] = None,
        analyzer: Optional[str] = None,
        analysis_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Run static analysis.
        
        Args:
            target_path: Path to file or directory
            language: Programming language
            analyzer: Specific analyzer to use
            analysis_type: Type of analysis
            
        Returns:
            Analysis results
        """
        if target_path.is_file():
            return self.analyzer.analyze_file(target_path, language, analyzer, analysis_type)
        else:
            return self.analyzer.analyze_directory(target_path, language, analyzer, analysis_type)
    
    def measure_quality(
        self,
        project_path: Path,
        include_tests: bool = False
    ) -> Dict[str, Any]:
        """
        Measure code quality metrics.
        
        Args:
            project_path: Path to project root
            include_tests: Whether to include test files
            
        Returns:
            Quality metrics
        """
        return self.quality.analyze_quality(project_path, include_tests)
    
    def generate_quality_report(
        self,
        project_path: Path,
        output_format: str = "markdown",
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate comprehensive quality report.
        
        Args:
            project_path: Path to project root
            output_format: Output format (text, markdown, json)
            output_path: Optional path to save report
            
        Returns:
            Report content
        """
        # Get quality metrics
        metrics = self.quality.analyze_quality(project_path)
        
        # Generate report
        report = self.quality.generate_report(metrics, output_format)
        
        # Save if output path provided
        if output_path:
            output_path.write_text(report)
            logger.info(f"Quality report saved to {output_path}")
        
        return report
    
    def _generate_summary(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary of all check results.
        
        Args:
            checks: Dictionary of check results
            
        Returns:
            Summary dictionary
        """
        summary = {
            'total_issues': 0,
            'critical_issues': 0,
            'warnings': 0,
            'info': 0,
            'formatting_needed': False,
            'quality_score': 0,
            'all_passed': True
        }
        
        # Count lint issues
        lint_result = checks.get('lint', {})
        if lint_result.get('issues'):
            for issue in lint_result['issues']:
                summary['total_issues'] += 1
                severity = issue.get('severity', 'warning').lower()
                
                if severity in ['critical', 'error']:
                    summary['critical_issues'] += 1
                elif severity == 'warning':
                    summary['warnings'] += 1
                else:
                    summary['info'] += 1
        
        if not lint_result.get('success', True):
            summary['all_passed'] = False
        
        # Check formatting
        format_result = checks.get('format', {})
        if format_result.get('changes_needed'):
            summary['formatting_needed'] = True
            summary['all_passed'] = False
        
        # Count static analysis issues
        analysis_result = checks.get('static_analysis', {})
        if analysis_result.get('issues'):
            for issue in analysis_result['issues']:
                summary['total_issues'] += 1
                severity = issue.get('severity', 'warning').lower()
                
                if severity in ['critical', 'error']:
                    summary['critical_issues'] += 1
                elif severity == 'warning':
                    summary['warnings'] += 1
                else:
                    summary['info'] += 1
        
        if not analysis_result.get('success', True):
            summary['all_passed'] = False
        
        # Get quality score
        quality_result = checks.get('quality', {})
        if quality_result:
            summary['quality_score'] = quality_result.get('quality_score', 0)
        
        return summary
    
    def get_tool_status(self) -> Dict[str, Any]:
        """
        Get status of all development tools.
        
        Returns:
            Dictionary with tool availability
        """
        import subprocess
        
        tools = {
            'linters': {},
            'formatters': {},
            'analyzers': {}
        }
        
        # Check linters
        linter_commands = ['pylint', 'flake8', 'ruff', 'eslint', 'shellcheck']
        for cmd in linter_commands:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    timeout=5
                )
                tools['linters'][cmd] = {
                    'available': result.returncode == 0,
                    'version': result.stdout.decode('utf-8').strip()[:50]
                }
            except (subprocess.TimeoutExpired, FileNotFoundError):
                tools['linters'][cmd] = {
                    'available': False,
                    'version': None
                }
        
        # Check formatters
        formatter_commands = ['black', 'prettier', 'autopep8', 'clang-format']
        for cmd in formatter_commands:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    timeout=5
                )
                tools['formatters'][cmd] = {
                    'available': result.returncode == 0,
                    'version': result.stdout.decode('utf-8').strip()[:50]
                }
            except (subprocess.TimeoutExpired, FileNotFoundError):
                tools['formatters'][cmd] = {
                    'available': False,
                    'version': None
                }
        
        # Check analyzers
        analyzer_commands = ['mypy', 'bandit', 'cppcheck', 'radon']
        for cmd in analyzer_commands:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    timeout=5
                )
                tools['analyzers'][cmd] = {
                    'available': result.returncode == 0,
                    'version': result.stdout.decode('utf-8').strip()[:50]
                }
            except (subprocess.TimeoutExpired, FileNotFoundError):
                tools['analyzers'][cmd] = {
                    'available': False,
                    'version': None
                }
        
        return tools
