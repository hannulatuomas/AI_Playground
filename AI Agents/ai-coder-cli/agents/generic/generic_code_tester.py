
"""
Generic Code Testing Agent

Fallback code tester for languages without specific implementations using LLM-based approaches.
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..base import CodeTesterBase


class GenericCodeTester(CodeTesterBase):
    """
    Generic code testing agent for any language.
    
    This agent provides fallback functionality for languages that don't
    have specific testing implementations. It uses LLM to guide testing
    and interprets generic test output patterns.
    """
    
    def __init__(
        self,
        name: str = "code_tester_generic",
        description: str = "Generic code tester for any language",
        **kwargs
    ):
        # Support common test frameworks
        common_frameworks = [
            'generic', 'custom', 'unittest', 'test',
            'jest', 'mocha', 'pytest', 'rspec', 'junit'
        ]
        super().__init__(
            name=name,
            description=description,
            supported_frameworks=common_frameworks,
            **kwargs
        )
    
    def _detect_test_framework(self, test_info: Dict[str, Any]) -> Optional[str]:
        """
        Detect test framework using file patterns and content analysis.
        
        Since this is generic, we try to detect common patterns or fall back
        to 'generic' framework.
        """
        test_path = test_info.get('test_path')
        working_dir = Path(test_info['working_dir'])
        
        if not test_path:
            return 'generic'
        
        # Check file extension
        test_file = Path(test_path)
        if not test_file.is_absolute():
            test_file = working_dir / test_file
        
        # Try to detect from content
        if test_file.exists() and test_file.is_file():
            try:
                content = test_file.read_text()
                
                # Python frameworks
                if '.py' in test_file.suffix:
                    if 'import pytest' in content or '@pytest' in content:
                        return 'pytest'
                    elif 'import unittest' in content:
                        return 'unittest'
                
                # JavaScript frameworks
                elif test_file.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                    if 'jest' in content or "from 'jest'" in content:
                        return 'jest'
                    elif 'mocha' in content or 'describe(' in content:
                        return 'mocha'
                
                # Ruby
                elif test_file.suffix == '.rb':
                    if 'RSpec' in content:
                        return 'rspec'
                
                # Java
                elif test_file.suffix == '.java':
                    if 'import org.junit' in content:
                        return 'junit'
                
            except Exception as e:
                self.logger.warning(f"Failed to read test file for framework detection: {e}")
        
        # Default to generic
        return 'generic'
    
    def _build_test_command(
        self,
        framework: str,
        test_path: str,
        options: Dict[str, Any]
    ) -> Optional[List[str]]:
        """
        Build test execution command for detected framework.
        """
        # Framework-specific commands
        commands = {
            'pytest': ['python', '-m', 'pytest', '-v', test_path if test_path else '.'],
            'unittest': ['python', '-m', 'unittest', 'discover', '-v'],
            'jest': ['npm', 'test', '--', '--verbose'],
            'mocha': ['npx', 'mocha', test_path if test_path else 'test/**/*.js'],
            'rspec': ['rspec', test_path if test_path else 'spec'],
            'junit': ['mvn', 'test'] if Path('pom.xml').exists() else ['gradle', 'test'],
        }
        
        if framework in commands:
            return commands[framework]
        
        # Generic fallback - try common test commands
        if test_path and Path(test_path).exists():
            # Try to execute the file directly if it looks executable
            return ['bash', '-c', f'cd {Path(test_path).parent} && ./{Path(test_path).name}']
        
        # Last resort - return None to signal we can't run tests
        self.logger.warning(f"No test command available for framework: {framework}")
        return None
    
    def _parse_test_output(
        self,
        framework: str,
        stdout: str,
        stderr: str,
        return_code: int
    ) -> Dict[str, Any]:
        """
        Parse test output using generic patterns.
        """
        output = stdout + '\n' + stderr
        
        results = {
            'summary': 'Unknown',
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'total': 0,
            'failures': [],
            'duration': None
        }
        
        # Framework-specific parsing
        if framework == 'pytest':
            results.update(self._parse_pytest_output(output))
        elif framework == 'unittest':
            results.update(self._parse_unittest_output(output))
        elif framework in ['jest', 'mocha']:
            results.update(self._parse_js_test_output(output))
        elif framework == 'rspec':
            results.update(self._parse_rspec_output(output))
        elif framework == 'junit':
            results.update(self._parse_junit_output(output))
        else:
            # Generic parsing
            results.update(self._parse_generic_output(output, return_code))
        
        # Calculate total
        results['total'] = results['passed'] + results['failed'] + results['skipped']
        
        # Generate summary
        results['summary'] = f"{results['passed']} passed, {results['failed']} failed, {results['skipped']} skipped"
        
        return results
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """Parse pytest output."""
        results = {}
        
        # Look for pytest summary
        match = re.search(r'(\d+) passed(?:, (\d+) failed)?(?:, (\d+) skipped)?', output)
        if match:
            results['passed'] = int(match.group(1) or 0)
            results['failed'] = int(match.group(2) or 0)
            results['skipped'] = int(match.group(3) or 0)
        
        # Look for FAILED markers
        failures = re.findall(r'FAILED (.*?) -', output)
        results['failures'] = failures[:10]
        
        return results
    
    def _parse_unittest_output(self, output: str) -> Dict[str, Any]:
        """Parse unittest output."""
        results = {}
        
        # Look for OK or FAILED
        if 'OK' in output:
            match = re.search(r'Ran (\d+) test', output)
            if match:
                results['passed'] = int(match.group(1))
        else:
            match = re.search(r'FAILED \(.*?failures=(\d+)', output)
            if match:
                results['failed'] = int(match.group(1))
        
        return results
    
    def _parse_js_test_output(self, output: str) -> Dict[str, Any]:
        """Parse Jest/Mocha output."""
        results = {}
        
        # Jest pattern
        match = re.search(r'Tests:\s+(\d+) failed(?:, (\d+) passed)?', output)
        if match:
            results['failed'] = int(match.group(1) or 0)
            results['passed'] = int(match.group(2) or 0)
        else:
            # Mocha pattern
            match = re.search(r'(\d+) passing', output)
            if match:
                results['passed'] = int(match.group(1))
            match = re.search(r'(\d+) failing', output)
            if match:
                results['failed'] = int(match.group(1))
        
        return results
    
    def _parse_rspec_output(self, output: str) -> Dict[str, Any]:
        """Parse RSpec output."""
        results = {}
        
        match = re.search(r'(\d+) examples?, (\d+) failures?', output)
        if match:
            total = int(match.group(1))
            failed = int(match.group(2))
            results['total'] = total
            results['failed'] = failed
            results['passed'] = total - failed
        
        return results
    
    def _parse_junit_output(self, output: str) -> Dict[str, Any]:
        """Parse JUnit output."""
        results = {}
        
        # Look for Maven/Gradle output
        match = re.search(r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)', output)
        if match:
            total = int(match.group(1))
            failed = int(match.group(2))
            errors = int(match.group(3))
            skipped = int(match.group(4))
            results['total'] = total
            results['failed'] = failed + errors
            results['skipped'] = skipped
            results['passed'] = total - failed - errors - skipped
        
        return results
    
    def _parse_generic_output(self, output: str, return_code: int) -> Dict[str, Any]:
        """Parse generic test output using common patterns."""
        results = {}
        
        # Look for common patterns
        patterns = [
            (r'(\d+)\s+passed', 'passed'),
            (r'(\d+)\s+failed', 'failed'),
            (r'(\d+)\s+skipped', 'skipped'),
            (r'(\d+)\s+errors?', 'failed'),
            (r'OK.*?(\d+)', 'passed'),
            (r'FAIL.*?(\d+)', 'failed'),
        ]
        
        for pattern, field in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                results[field] = int(match.group(1))
        
        # If no patterns matched, use return code
        if not results:
            if return_code == 0:
                results['passed'] = 1
                results['failed'] = 0
            else:
                results['passed'] = 0
                results['failed'] = 1
        
        return results
    
    def _get_supported_frameworks(self) -> List[str]:
        """Get list of supported test frameworks."""
        return self.supported_frameworks

