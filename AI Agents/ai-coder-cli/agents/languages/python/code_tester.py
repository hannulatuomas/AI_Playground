
"""
Python-Specific Code Testing Agent

This agent specializes in running and analyzing Python tests with awareness of:
- pytest framework
- unittest framework
- pytest fixtures and markers
- Coverage analysis
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

from ...base import CodeTesterBase


class PythonCodeTesterAgent(CodeTesterBase):
    """
    Agent specialized for Python code testing.
    
    Features:
    - pytest and unittest framework support
    - Coverage analysis integration
    - Fixture and marker awareness
    - Virtual environment detection
    - Test discovery and execution
    """
    
    def __init__(
        self,
        name: str = "code_tester_python",
        description: str = "Python-specific code testing agent",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            supported_frameworks=['pytest', 'unittest', 'nose', 'coverage'],
            **kwargs
        )
    
    def _detect_test_framework(self, test_info: Dict[str, Any]) -> Optional[str]:
        """
        Detect Python test framework.
        
        Priority: pytest > unittest > nose
        """
        working_dir = Path(test_info['working_dir'])
        
        # Check for pytest
        if (working_dir / 'pytest.ini').exists() or \
           (working_dir / 'pyproject.toml').exists():
            return 'pytest'
        
        # Check for setup.cfg with pytest
        setup_cfg = working_dir / 'setup.cfg'
        if setup_cfg.exists():
            try:
                content = setup_cfg.read_text()
                if '[pytest]' in content or '[tool:pytest]' in content:
                    return 'pytest'
            except Exception:
                pass
        
        # Check test file content
        test_path = test_info.get('test_path')
        if test_path:
            test_file = Path(test_path)
            if not test_file.is_absolute():
                test_file = working_dir / test_file
            
            if test_file.exists() and test_file.is_file():
                try:
                    content = test_file.read_text()
                    if 'import pytest' in content or '@pytest' in content:
                        return 'pytest'
                    elif 'import unittest' in content or 'from unittest' in content:
                        return 'unittest'
                    elif 'import nose' in content:
                        return 'nose'
                except Exception:
                    pass
        
        # Default to pytest
        return 'pytest'
    
    def _build_test_command(
        self,
        framework: str,
        test_path: str,
        options: Dict[str, Any]
    ) -> Optional[List[str]]:
        """
        Build Python test execution command.
        """
        if framework == 'pytest':
            cmd = ['python', '-m', 'pytest', '-v']
            
            # Add coverage if requested
            if options.get('coverage', False):
                cmd.extend(['--cov=.', '--cov-report=term-missing'])
            
            # Add markers if specified
            if options.get('markers'):
                cmd.extend(['-m', options['markers']])
            
            # Add test path
            if test_path:
                cmd.append(test_path)
            else:
                cmd.append('.')
            
            return cmd
        
        elif framework == 'unittest':
            if test_path:
                return ['python', '-m', 'unittest', test_path, '-v']
            else:
                return ['python', '-m', 'unittest', 'discover', '-v']
        
        elif framework == 'nose':
            cmd = ['nosetests', '-v']
            if test_path:
                cmd.append(test_path)
            return cmd
        
        return None
    
    def _parse_test_output(
        self,
        framework: str,
        stdout: str,
        stderr: str,
        return_code: int
    ) -> Dict[str, Any]:
        """
        Parse Python test output.
        """
        output = stdout + '\n' + stderr
        
        results = {
            'summary': 'Unknown',
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'total': 0,
            'failures': [],
            'duration': None,
            'coverage': None
        }
        
        if framework == 'pytest':
            results.update(self._parse_pytest_output(output))
        elif framework == 'unittest':
            results.update(self._parse_unittest_output(output))
        elif framework == 'nose':
            results.update(self._parse_nose_output(output))
        
        # Calculate total
        results['total'] = results['passed'] + results['failed'] + results['skipped']
        
        # Generate summary
        results['summary'] = f"{results['passed']} passed, {results['failed']} failed, {results['skipped']} skipped"
        
        return results
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """Parse pytest output."""
        results = {}
        
        # Look for pytest summary line
        match = re.search(r'(\d+) passed(?:, (\d+) failed)?(?:, (\d+) skipped)?(?:, (\d+) error)?', output)
        if match:
            results['passed'] = int(match.group(1) or 0)
            results['failed'] = int(match.group(2) or 0)
            results['skipped'] = int(match.group(3) or 0)
            if match.group(4):
                results['failed'] += int(match.group(4))
        
        # Alternative pattern
        if not results.get('passed'):
            match = re.search(r'=+ (\d+) passed', output)
            if match:
                results['passed'] = int(match.group(1))
        
        # Look for FAILED markers
        failures = re.findall(r'FAILED (.*?) -', output)
        results['failures'] = failures[:10]
        
        # Extract duration
        match = re.search(r'in ([\d.]+)s', output)
        if match:
            results['duration'] = float(match.group(1))
        
        # Extract coverage if present
        match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
        if match:
            results['coverage'] = int(match.group(1))
        
        return results
    
    def _parse_unittest_output(self, output: str) -> Dict[str, Any]:
        """Parse unittest output."""
        results = {}
        
        # Look for OK or FAILED
        if re.search(r'^OK', output, re.MULTILINE):
            match = re.search(r'Ran (\d+) test', output)
            if match:
                results['passed'] = int(match.group(1))
                results['failed'] = 0
        else:
            match = re.search(r'Ran (\d+) test', output)
            if match:
                total = int(match.group(1))
                
                # Look for failures and errors
                failures = 0
                match_fail = re.search(r'failures=(\d+)', output)
                if match_fail:
                    failures += int(match_fail.group(1))
                
                match_err = re.search(r'errors=(\d+)', output)
                if match_err:
                    failures += int(match_err.group(1))
                
                results['failed'] = failures
                results['passed'] = total - failures
        
        # Look for skipped
        match = re.search(r'skipped=(\d+)', output)
        if match:
            results['skipped'] = int(match.group(1))
        
        return results
    
    def _parse_nose_output(self, output: str) -> Dict[str, Any]:
        """Parse nose test output."""
        results = {}
        
        # Similar to unittest
        match = re.search(r'Ran (\d+) test', output)
        if match:
            total = int(match.group(1))
            
            if 'OK' in output:
                results['passed'] = total
                results['failed'] = 0
            else:
                match_fail = re.search(r'FAILED \(.*?failures=(\d+)', output)
                if match_fail:
                    results['failed'] = int(match_fail.group(1))
                    results['passed'] = total - results['failed']
        
        return results
    
    def _get_supported_frameworks(self) -> List[str]:
        """Get list of supported test frameworks."""
        return self.supported_frameworks
    
    def _get_language_directory(self) -> Optional[Path]:
        """Get the Python language directory."""
        # Get the directory where this file is located
        return Path(__file__).parent

