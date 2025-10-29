"""
PowerShell-Specific Code Analyzer Agent

This agent specializes in analyzing PowerShell code.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodeAnalyzerBase


class PowerShellCodeAnalyzerAgent(CodeAnalyzerBase):
    """
    Agent specialized for PowerShell code analysis.
    
    Features:
    - Code quality analysis
    - Complexity metrics
    - Security checks
    - Performance analysis
    - Best practices adherence
    """
    
    def __init__(
        self,
        name: str = "code_analyzer_powershell",
        description: str = "PowerShell-specific code analysis agent",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            primary_language="PowerShell",
            **kwargs
        )
    
    def _analyze_code_quality(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PowerShell code quality."""
        issues = []
        score = 100
        
        # Add language-specific quality checks here
        lines = code.split('\n')
        
        # Check line length
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 120]
        if long_lines:
            issues.append({
                'type': 'style',
                'severity': 'warning',
                'message': f'Lines exceed 120 characters: {len(long_lines)} lines',
            })
            score -= min(10, len(long_lines))
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': [
                'Follow PowerShell coding standards',
                'Keep lines under 120 characters',
                'Add appropriate comments and documentation',
            ]
        }
    
    def _calculate_complexity(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate PowerShell code complexity."""
        lines = [l for l in code.split('\n') if l.strip()]
        loc = len(lines)
        
        score = 100
        if loc > 1000:
            score -= 20
        elif loc > 500:
            score -= 10
        
        return {
            'score': max(0, score),
            'metrics': {
                'lines_of_code': loc,
            },
            'issues': [],
            'recommendations': [
                'Keep files under 500 lines of code',
                'Break down large functions',
            ]
        }
    
    def _check_security(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check for PowerShell security issues."""
        issues = []
        score = 100
        
        # Add language-specific security checks here
        
        return {
            'score': score,
            'issues': issues,
            'recommendations': [
                'Validate all user inputs',
                'Use parameterized queries',
                'Never hardcode credentials',
            ]
        }
    
    def _analyze_performance(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PowerShell performance issues."""
        issues = []
        score = 100
        
        # Add language-specific performance checks here
        
        return {
            'score': score,
            'issues': issues,
            'recommendations': [
                'Optimize nested loops',
                'Use appropriate data structures',
                'Profile code to identify bottlenecks',
            ]
        }
    
    def _check_best_practices(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check PowerShell best practices adherence."""
        issues = []
        score = 100
        
        # Add language-specific best practice checks here
        
        return {
            'score': score,
            'issues': issues,
            'recommendations': [
                'Follow PowerShell style guide',
                'Add comprehensive documentation',
                'Write unit tests',
            ]
        }
    
    def _get_language_directory(self) -> Optional[Path]:
        """Get the PowerShell language directory."""
        return Path(__file__).parent
