
"""
Formatter Tool

Integration with code formatters (black, prettier, etc.)
"""

import logging
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class FormatterTool:
    """
    Wrapper for language-specific code formatters.
    
    Supports:
    - Python: black, autopep8, yapf
    - JavaScript/TypeScript: prettier
    - C/C++: clang-format
    - Go: gofmt
    - Rust: rustfmt
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize formatter tool.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.formatters = {
            'python': {
                'black': ['black'],
                'autopep8': ['autopep8', '--in-place'],
                'yapf': ['yapf', '--in-place']
            },
            'javascript': {
                'prettier': ['prettier', '--write']
            },
            'typescript': {
                'prettier': ['prettier', '--write']
            },
            'cpp': {
                'clang-format': ['clang-format', '-i']
            },
            'go': {
                'gofmt': ['gofmt', '-w']
            },
            'rust': {
                'rustfmt': ['rustfmt']
            }
        }
        
        logger.info("FormatterTool initialized")
    
    def format_file(
        self,
        file_path: Path,
        language: Optional[str] = None,
        formatter: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Format a single file.
        
        Args:
            file_path: Path to file to format
            language: Programming language (auto-detected if not provided)
            formatter: Specific formatter to use
            dry_run: Check only, don't modify file
            
        Returns:
            Dictionary with format results
        """
        if not file_path.exists():
            return {
                'success': False,
                'error': f'File not found: {file_path}'
            }
        
        # Auto-detect language if not provided
        if not language:
            language = self._detect_language(file_path)
        
        # Get formatter command
        formatter_cmd = self._get_formatter_command(language, formatter)
        
        if not formatter_cmd:
            return {
                'success': False,
                'error': f'No formatter available for {language}'
            }
        
        try:
            # Add dry-run flag if supported
            if dry_run:
                formatter_cmd = self._add_dry_run_flag(formatter_cmd, language, formatter)
            
            # Run formatter
            result = subprocess.run(
                formatter_cmd + [str(file_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                'success': result.returncode == 0,
                'formatted': not dry_run and result.returncode == 0,
                'changes_needed': dry_run and result.returncode != 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Formatter timed out'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': f'Formatter not found: {formatter_cmd[0]}'
            }
        except Exception as e:
            logger.error(f"Formatting failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def format_directory(
        self,
        directory: Path,
        language: Optional[str] = None,
        formatter: Optional[str] = None,
        dry_run: bool = False,
        recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Format all files in a directory.
        
        Args:
            directory: Directory to format
            language: Programming language filter
            formatter: Specific formatter to use
            dry_run: Check only, don't modify files
            recursive: Whether to format recursively
            
        Returns:
            Dictionary with aggregated format results
        """
        if not directory.exists() or not directory.is_dir():
            return {
                'success': False,
                'error': f'Directory not found: {directory}'
            }
        
        # Get formatter command
        formatter_cmd = self._get_formatter_command(language, formatter)
        
        if not formatter_cmd:
            return {
                'success': False,
                'error': f'No formatter available for {language}'
            }
        
        try:
            # Add dry-run flag if supported
            if dry_run:
                formatter_cmd = self._add_dry_run_flag(formatter_cmd, language, formatter)
            
            # Run formatter on directory
            result = subprocess.run(
                formatter_cmd + [str(directory)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                'success': result.returncode == 0,
                'formatted': not dry_run and result.returncode == 0,
                'changes_needed': dry_run and result.returncode != 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Formatter timed out'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': f'Formatter not found: {formatter_cmd[0]}'
            }
        except Exception as e:
            logger.error(f"Formatting failed: {e}", exc_info=True)
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
            '.go': 'go',
            '.rs': 'rust'
        }
        
        return extension_map.get(file_path.suffix.lower(), 'unknown')
    
    def _get_formatter_command(
        self,
        language: str,
        formatter: Optional[str] = None
    ) -> Optional[List[str]]:
        """Get formatter command for language."""
        if language not in self.formatters:
            return None
        
        lang_formatters = self.formatters[language]
        
        if formatter and formatter in lang_formatters:
            return lang_formatters[formatter].copy()
        
        # Return first available formatter
        for cmd in lang_formatters.values():
            return cmd.copy()
        
        return None
    
    def _add_dry_run_flag(
        self,
        cmd: List[str],
        language: str,
        formatter: Optional[str]
    ) -> List[str]:
        """Add dry-run/check flag to formatter command."""
        formatter_name = formatter or cmd[0]
        
        dry_run_flags = {
            'black': ['--check', '--diff'],
            'prettier': ['--check'],
            'autopep8': ['--diff'],
            'yapf': ['--diff'],
            'clang-format': ['--dry-run'],
            'gofmt': ['-d'],  # Different: just prints diff
            'rustfmt': ['--check']
        }
        
        flags = dry_run_flags.get(formatter_name, [])
        
        # Insert flags after command name
        return [cmd[0]] + flags + cmd[1:]
