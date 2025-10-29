"""
Test Runner Module

Executes tests and collects results.
"""

import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class TestResult:
    """Result of a single test."""
    __test__ = False  # Not a pytest test class
    name: str
    passed: bool
    duration: float = 0.0
    error: Optional[str] = None
    output: Optional[str] = None


@dataclass
class TestResults:
    """Results of test execution."""
    __test__ = False  # Not a pytest test class
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration: float = 0.0
    coverage: float = 0.0
    test_results: List[TestResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class TestRunner:
    """Runs tests and collects results."""
    __test__ = False  # Not a pytest test class
    
    def __init__(self):
        """Initialize test runner."""
        self.framework_commands = {
            'pytest': ['pytest', '--verbose', '--tb=short'],
            'unittest': ['python', '-m', 'unittest', 'discover'],
            'jest': ['npm', 'test', '--', '--verbose'],
            'mocha': ['npx', 'mocha'],
            'xunit': ['dotnet', 'test'],
            'gtest': ['./run_tests'],
        }
    
    def run_tests(self, project_path: str, language: str,
                 framework: Optional[str] = None,
                 test_files: Optional[List[str]] = None) -> TestResults:
        """
        Run tests for a project.
        
        Args:
            project_path: Path to project
            language: Programming language
            framework: Test framework
            test_files: Specific test files to run (optional)
            
        Returns:
            TestResults with execution results
        """
        if not framework:
            framework = self._detect_framework(project_path, language)
        
        # Build command
        command = self._build_command(framework, test_files)
        
        if not command:
            return TestResults(errors=[f"Unknown test framework: {framework}"])
        
        # Execute tests
        try:
            result = subprocess.run(
                command,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse results
            return self._parse_results(result, framework)
            
        except subprocess.TimeoutExpired:
            return TestResults(errors=["Test execution timed out"])
        except Exception as e:
            return TestResults(errors=[f"Test execution failed: {str(e)}"])
    
    def run_single_test(self, test_file: str, test_name: str,
                       language: str, framework: str) -> TestResult:
        """
        Run a single test.
        
        Args:
            test_file: Path to test file
            test_name: Name of test to run
            language: Programming language
            framework: Test framework
            
        Returns:
            TestResult for the single test
        """
        command = self._build_single_test_command(
            framework, test_file, test_name
        )
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return TestResult(
                name=test_name,
                passed=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None
            )
            
        except Exception as e:
            return TestResult(
                name=test_name,
                passed=False,
                error=str(e)
            )
    
    def get_coverage(self, project_path: str, language: str,
                    framework: str) -> float:
        """
        Get test coverage percentage.
        
        Args:
            project_path: Path to project
            language: Programming language
            framework: Test framework
            
        Returns:
            Coverage percentage (0-100)
        """
        coverage_command = self._build_coverage_command(language, framework)
        
        if not coverage_command:
            return 0.0
        
        try:
            result = subprocess.run(
                coverage_command,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return self._parse_coverage(result.stdout, language)
            
        except Exception:
            return 0.0
    
    def _detect_framework(self, project_path: str, language: str) -> str:
        """Detect test framework from project."""
        path = Path(project_path)
        
        if language == 'python':
            if (path / 'pytest.ini').exists() or 'pytest' in self._read_requirements(path):
                return 'pytest'
            return 'unittest'
        
        elif language in ['javascript', 'typescript']:
            pkg_json = path / 'package.json'
            if pkg_json.exists():
                try:
                    with open(pkg_json, 'r') as f:
                        data = json.load(f)
                        deps = {**data.get('dependencies', {}),
                               **data.get('devDependencies', {})}
                        
                        if 'jest' in deps:
                            return 'jest'
                        elif 'mocha' in deps:
                            return 'mocha'
                except:
                    pass
            return 'jest'
        
        elif language == 'csharp':
            return 'xunit'
        
        elif language == 'cpp':
            return 'gtest'
        
        return 'unittest'
    
    def _read_requirements(self, path: Path) -> str:
        """Read requirements.txt content."""
        req_file = path / 'requirements.txt'
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    return f.read()
            except:
                pass
        return ""
    
    def _build_command(self, framework: str, 
                      test_files: Optional[List[str]]) -> List[str]:
        """Build test command."""
        command = self.framework_commands.get(framework, [])
        
        if not command:
            return []
        
        # Add specific test files if provided
        if test_files:
            command.extend(test_files)
        
        return command
    
    def _build_single_test_command(self, framework: str, 
                                   test_file: str, test_name: str) -> List[str]:
        """Build command for single test."""
        if framework == 'pytest':
            return ['pytest', test_file, '-k', test_name, '-v']
        elif framework == 'jest':
            return ['npm', 'test', '--', test_file, '-t', test_name]
        elif framework == 'unittest':
            return ['python', '-m', 'unittest', f"{test_file}.{test_name}"]
        else:
            return []
    
    def _build_coverage_command(self, language: str, 
                               framework: str) -> List[str]:
        """Build coverage command."""
        if language == 'python':
            if framework == 'pytest':
                return ['pytest', '--cov', '--cov-report=term']
            else:
                return ['coverage', 'run', '-m', 'unittest', 'discover']
        
        elif language in ['javascript', 'typescript']:
            return ['npm', 'test', '--', '--coverage']
        
        return []
    
    def _parse_results(self, result: subprocess.CompletedProcess,
                      framework: str) -> TestResults:
        """Parse test results from output."""
        results = TestResults()
        
        output = result.stdout + result.stderr
        
        if framework == 'pytest':
            results = self._parse_pytest_output(output)
        elif framework == 'jest':
            results = self._parse_jest_output(output)
        elif framework == 'unittest':
            results = self._parse_unittest_output(output)
        else:
            # Generic parsing
            results.total = output.count('test')
            results.passed = output.count('PASS') + output.count('OK')
            results.failed = output.count('FAIL') + output.count('ERROR')
        
        return results
    
    def _parse_pytest_output(self, output: str) -> TestResults:
        """Parse pytest output."""
        results = TestResults()
        
        # Extract summary line
        summary_match = re.search(
            r'(\d+) passed(?:, (\d+) failed)?(?:, (\d+) skipped)?',
            output
        )
        
        if summary_match:
            results.passed = int(summary_match.group(1))
            results.failed = int(summary_match.group(2) or 0)
            results.skipped = int(summary_match.group(3) or 0)
            results.total = results.passed + results.failed + results.skipped
        
        # Extract duration
        duration_match = re.search(r'in ([\d.]+)s', output)
        if duration_match:
            results.duration = float(duration_match.group(1))
        
        # Extract coverage
        coverage_match = re.search(r'TOTAL\s+.*?(\d+)%', output)
        if coverage_match:
            results.coverage = float(coverage_match.group(1))
        
        # Extract individual test results
        test_matches = re.finditer(
            r'(test_\w+).*?(PASSED|FAILED)',
            output
        )
        
        for match in test_matches:
            results.test_results.append(TestResult(
                name=match.group(1),
                passed=match.group(2) == 'PASSED'
            ))
        
        return results
    
    def _parse_jest_output(self, output: str) -> TestResults:
        """Parse Jest output."""
        results = TestResults()
        
        # Extract summary
        summary_match = re.search(
            r'Tests:\s+(?:(\d+) failed,\s+)?(\d+) passed,\s+(\d+) total',
            output
        )
        
        if summary_match:
            results.failed = int(summary_match.group(1) or 0)
            results.passed = int(summary_match.group(2))
            results.total = int(summary_match.group(3))
        
        # Extract duration
        duration_match = re.search(r'Time:\s+([\d.]+)\s*s', output)
        if duration_match:
            results.duration = float(duration_match.group(1))
        
        # Extract coverage
        coverage_match = re.search(r'All files\s+\|\s+([\d.]+)', output)
        if coverage_match:
            results.coverage = float(coverage_match.group(1))
        
        return results
    
    def _parse_unittest_output(self, output: str) -> TestResults:
        """Parse unittest output."""
        results = TestResults()
        
        # Count dots (passed), F (failed), E (error)
        results.passed = output.count('.')
        results.failed = output.count('F') + output.count('E')
        results.total = results.passed + results.failed
        
        # Extract duration
        duration_match = re.search(r'Ran \d+ tests? in ([\d.]+)s', output)
        if duration_match:
            results.duration = float(duration_match.group(1))
        
        return results
    
    def _parse_coverage(self, output: str, language: str) -> float:
        """Parse coverage percentage from output."""
        if language == 'python':
            # Look for coverage percentage
            match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
            if match:
                return float(match.group(1))
        
        elif language in ['javascript', 'typescript']:
            # Jest coverage format
            match = re.search(r'All files\s+\|\s+([\d.]+)', output)
            if match:
                return float(match.group(1))
        
        return 0.0
