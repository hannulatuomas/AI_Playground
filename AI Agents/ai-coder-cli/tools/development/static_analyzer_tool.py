
"""
Static Analyzer Tool

Integration with static analysis tools for deeper code inspection
"""

import logging
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class StaticAnalyzerTool:
    """
    Wrapper for static analysis tools.
    
    Supports:
    - Python: mypy, bandit (security), radon (complexity)
    - JavaScript/TypeScript: tsc (type checking)
    - C/C++: cppcheck, clang-analyzer
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize static analyzer tool.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.analyzers = {
            'python': {
                'mypy': ['mypy', '--show-error-codes'],
                'bandit': ['bandit', '-f', 'json'],
                'radon': ['radon', 'cc', '-j']
            },
            'javascript': {
                'tsc': ['tsc', '--noEmit']
            },
            'typescript': {
                'tsc': ['tsc', '--noEmit']
            },
            'cpp': {
                'cppcheck': ['cppcheck', '--enable=all', '--xml'],
                'clang-tidy': ['clang-tidy']
            }
        }
        
        logger.info("StaticAnalyzerTool initialized")
    
    def analyze_file(
        self,
        file_path: Path,
        language: Optional[str] = None,
        analyzer: Optional[str] = None,
        analysis_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Analyze a single file.
        
        Args:
            file_path: Path to file to analyze
            language: Programming language
            analyzer: Specific analyzer to use
            analysis_type: Type of analysis (all, types, security, complexity)
            
        Returns:
            Dictionary with analysis results
        """
        if not file_path.exists():
            return {
                'success': False,
                'error': f'File not found: {file_path}'
            }
        
        # Auto-detect language if not provided
        if not language:
            language = self._detect_language(file_path)
        
        # Get analyzer based on type
        if not analyzer:
            analyzer = self._select_analyzer_for_type(language, analysis_type)
        
        # Get analyzer command
        analyzer_cmd = self._get_analyzer_command(language, analyzer)
        
        if not analyzer_cmd:
            return {
                'success': False,
                'error': f'No analyzer available for {language}'
            }
        
        try:
            # Run analyzer
            result = subprocess.run(
                analyzer_cmd + [str(file_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return {
                'success': result.returncode == 0,
                'issues': self._parse_analyzer_output(
                    result.stdout,
                    result.stderr,
                    analyzer
                ),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'analyzer': analyzer
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Analyzer timed out'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': f'Analyzer not found: {analyzer_cmd[0]}'
            }
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_directory(
        self,
        directory: Path,
        language: Optional[str] = None,
        analyzer: Optional[str] = None,
        analysis_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Analyze all files in a directory.
        
        Args:
            directory: Directory to analyze
            language: Programming language filter
            analyzer: Specific analyzer to use
            analysis_type: Type of analysis
            
        Returns:
            Dictionary with aggregated analysis results
        """
        if not directory.exists() or not directory.is_dir():
            return {
                'success': False,
                'error': f'Directory not found: {directory}'
            }
        
        # Get analyzer based on type
        if not analyzer:
            analyzer = self._select_analyzer_for_type(language, analysis_type)
        
        # Get analyzer command
        analyzer_cmd = self._get_analyzer_command(language, analyzer)
        
        if not analyzer_cmd:
            return {
                'success': False,
                'error': f'No analyzer available for {language}'
            }
        
        try:
            # Run analyzer on directory
            result = subprocess.run(
                analyzer_cmd + [str(directory)],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            return {
                'success': result.returncode == 0,
                'issues': self._parse_analyzer_output(
                    result.stdout,
                    result.stderr,
                    analyzer
                ),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'analyzer': analyzer
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Analyzer timed out'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': f'Analyzer not found: {analyzer_cmd[0]}'
            }
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'cpp',
            '.h': 'cpp',
            '.hpp': 'cpp'
        }
        
        return extension_map.get(file_path.suffix.lower(), 'unknown')
    
    def _select_analyzer_for_type(self, language: str, analysis_type: str) -> Optional[str]:
        """Select appropriate analyzer based on analysis type."""
        analyzer_map = {
            'python': {
                'types': 'mypy',
                'security': 'bandit',
                'complexity': 'radon',
                'all': 'mypy'
            },
            'javascript': {
                'types': 'tsc',
                'all': 'tsc'
            },
            'typescript': {
                'types': 'tsc',
                'all': 'tsc'
            },
            'cpp': {
                'all': 'cppcheck'
            }
        }
        
        return analyzer_map.get(language, {}).get(analysis_type, None)
    
    def _get_analyzer_command(
        self,
        language: str,
        analyzer: Optional[str] = None
    ) -> Optional[List[str]]:
        """Get analyzer command for language."""
        if language not in self.analyzers:
            return None
        
        lang_analyzers = self.analyzers[language]
        
        if analyzer and analyzer in lang_analyzers:
            return lang_analyzers[analyzer].copy()
        
        # Return first available analyzer
        for cmd in lang_analyzers.values():
            return cmd.copy()
        
        return None
    
    def _parse_analyzer_output(
        self,
        stdout: str,
        stderr: str,
        analyzer: str
    ) -> List[Dict[str, Any]]:
        """Parse analyzer output into structured format."""
        issues = []
        
        # Try JSON parsing first
        if stdout.strip():
            try:
                import json
                data = json.loads(stdout)
                
                if isinstance(data, list):
                    for item in data:
                        issues.append(self._normalize_issue(item, analyzer))
                elif isinstance(data, dict):
                    # Handle different structures
                    if 'results' in data:
                        for item in data['results']:
                            issues.append(self._normalize_issue(item, analyzer))
                
                return issues
            except json.JSONDecodeError:
                pass
        
        # Fall back to text parsing
        for line in (stdout + '\n' + stderr).split('\n'):
            if line.strip():
                issue = self._parse_text_line(line, analyzer)
                if issue:
                    issues.append(issue)
        
        return issues
    
    def _normalize_issue(self, issue: Dict[str, Any], analyzer: str) -> Dict[str, Any]:
        """Normalize issue format across different analyzers."""
        return {
            'file': issue.get('filename') or issue.get('file') or 'unknown',
            'line': issue.get('line_number') or issue.get('line') or 0,
            'column': issue.get('column') or issue.get('col') or 0,
            'severity': issue.get('issue_severity') or issue.get('severity') or 'warning',
            'message': issue.get('issue_text') or issue.get('message') or '',
            'code': issue.get('test_id') or issue.get('code') or '',
            'analyzer': analyzer
        }
    
    def _parse_text_line(self, line: str, analyzer: str) -> Optional[Dict[str, Any]]:
        """Parse a text line from analyzer output."""
        # Generic pattern: file:line:column: message
        parts = line.split(':', 3)
        
        if len(parts) >= 3:
            try:
                return {
                    'file': parts[0].strip(),
                    'line': int(parts[1].strip()) if parts[1].strip().isdigit() else 0,
                    'column': 0,
                    'severity': 'warning',
                    'message': parts[2].strip() if len(parts) > 2 else '',
                    'code': '',
                    'analyzer': analyzer
                }
            except (ValueError, IndexError):
                pass
        
        return None
