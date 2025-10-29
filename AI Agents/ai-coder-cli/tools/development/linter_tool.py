
"""
Linter Tool

Integration with language-specific linters (pylint, eslint, etc.)
"""

import logging
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class LinterTool:
    """
    Wrapper for language-specific linters.
    
    Supports:
    - Python: pylint, flake8, ruff
    - JavaScript/TypeScript: eslint
    - C/C++: cpplint, cppcheck
    - Shell: shellcheck
    - Go: golint
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize linter tool.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.linters = {
            'python': {
                'pylint': ['pylint', '--output-format=json'],
                'flake8': ['flake8', '--format=json'],
                'ruff': ['ruff', 'check', '--output-format=json']
            },
            'javascript': {
                'eslint': ['eslint', '--format=json']
            },
            'typescript': {
                'eslint': ['eslint', '--format=json']
            },
            'cpp': {
                'cpplint': ['cpplint'],
                'cppcheck': ['cppcheck', '--enable=all', '--xml']
            },
            'shell': {
                'shellcheck': ['shellcheck', '--format=json']
            },
            'go': {
                'golint': ['golint']
            }
        }
        
        logger.info("LinterTool initialized")
    
    def lint_file(
        self,
        file_path: Path,
        language: Optional[str] = None,
        linter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lint a single file.
        
        Args:
            file_path: Path to file to lint
            language: Programming language (auto-detected if not provided)
            linter: Specific linter to use (uses default if not provided)
            
        Returns:
            Dictionary with lint results
        """
        if not file_path.exists():
            return {
                'success': False,
                'error': f'File not found: {file_path}'
            }
        
        # Auto-detect language if not provided
        if not language:
            language = self._detect_language(file_path)
        
        # Get linter command
        linter_cmd = self._get_linter_command(language, linter)
        
        if not linter_cmd:
            return {
                'success': False,
                'error': f'No linter available for {language}'
            }
        
        try:
            # Run linter
            result = subprocess.run(
                linter_cmd + [str(file_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                'success': result.returncode == 0,
                'issues': self._parse_linter_output(
                    result.stdout,
                    result.stderr,
                    language,
                    linter_cmd[0]
                ),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Linter timed out'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': f'Linter not found: {linter_cmd[0]}'
            }
        except Exception as e:
            logger.error(f"Linting failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def lint_directory(
        self,
        directory: Path,
        language: Optional[str] = None,
        linter: Optional[str] = None,
        recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Lint all files in a directory.
        
        Args:
            directory: Directory to lint
            language: Programming language filter
            linter: Specific linter to use
            recursive: Whether to lint recursively
            
        Returns:
            Dictionary with aggregated lint results
        """
        if not directory.exists() or not directory.is_dir():
            return {
                'success': False,
                'error': f'Directory not found: {directory}'
            }
        
        # Get linter command
        linter_cmd = self._get_linter_command(language, linter)
        
        if not linter_cmd:
            return {
                'success': False,
                'error': f'No linter available for {language}'
            }
        
        try:
            # Run linter on directory
            result = subprocess.run(
                linter_cmd + [str(directory)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                'success': result.returncode == 0,
                'issues': self._parse_linter_output(
                    result.stdout,
                    result.stderr,
                    language,
                    linter_cmd[0]
                ),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Linter timed out'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': f'Linter not found: {linter_cmd[0]}'
            }
        except Exception as e:
            logger.error(f"Linting failed: {e}", exc_info=True)
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
            '.hpp': 'cpp',
            '.sh': 'shell',
            '.bash': 'shell',
            '.go': 'go'
        }
        
        return extension_map.get(file_path.suffix.lower(), 'unknown')
    
    def _get_linter_command(
        self,
        language: str,
        linter: Optional[str] = None
    ) -> Optional[List[str]]:
        """Get linter command for language."""
        if language not in self.linters:
            return None
        
        lang_linters = self.linters[language]
        
        if linter and linter in lang_linters:
            return lang_linters[linter].copy()
        
        # Return first available linter
        for cmd in lang_linters.values():
            return cmd.copy()
        
        return None
    
    def _parse_linter_output(
        self,
        stdout: str,
        stderr: str,
        language: str,
        linter: str
    ) -> List[Dict[str, Any]]:
        """
        Parse linter output into structured format.
        
        Returns list of issues with file, line, column, severity, message.
        """
        issues = []
        
        # Try JSON parsing first
        if stdout.strip():
            try:
                import json
                data = json.loads(stdout)
                
                # Handle different linter output formats
                if isinstance(data, list):
                    for item in data:
                        issues.append(self._normalize_issue(item, linter))
                elif isinstance(data, dict):
                    # Handle nested structures
                    for file_issues in data.values():
                        if isinstance(file_issues, list):
                            for item in file_issues:
                                issues.append(self._normalize_issue(item, linter))
                
                return issues
            except json.JSONDecodeError:
                pass
        
        # Fall back to text parsing
        for line in (stdout + '\n' + stderr).split('\n'):
            if line.strip():
                issue = self._parse_text_line(line, linter)
                if issue:
                    issues.append(issue)
        
        return issues
    
    def _normalize_issue(self, issue: Dict[str, Any], linter: str) -> Dict[str, Any]:
        """Normalize issue format across different linters."""
        normalized = {
            'file': issue.get('path') or issue.get('file') or 'unknown',
            'line': issue.get('line') or issue.get('line_number') or 0,
            'column': issue.get('column') or issue.get('col') or 0,
            'severity': issue.get('severity') or issue.get('type') or 'warning',
            'message': issue.get('message') or issue.get('msg') or '',
            'rule': issue.get('rule') or issue.get('code') or '',
            'linter': linter
        }
        
        return normalized
    
    def _parse_text_line(self, line: str, linter: str) -> Optional[Dict[str, Any]]:
        """Parse a text line from linter output."""
        # Generic pattern: file:line:column: severity: message
        parts = line.split(':', 4)
        
        if len(parts) >= 4:
            try:
                return {
                    'file': parts[0].strip(),
                    'line': int(parts[1].strip()) if parts[1].strip().isdigit() else 0,
                    'column': int(parts[2].strip()) if parts[2].strip().isdigit() else 0,
                    'severity': 'warning',
                    'message': parts[3].strip() if len(parts) > 3 else '',
                    'rule': '',
                    'linter': linter
                }
            except (ValueError, IndexError):
                pass
        
        return None
