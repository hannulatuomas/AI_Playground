"""
API Tester

Tests API endpoints and validates responses.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json


@dataclass
class TestCase:
    """API test case."""
    name: str
    method: str
    endpoint: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict] = None
    expected_status: int = 200
    expected_response: Optional[Dict] = None


@dataclass
class TestResult:
    """Result of API test."""
    test_name: str
    passed: bool
    status_code: Optional[int] = None
    response: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0


class APITester:
    """Tests API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API tester.
        
        Args:
            base_url: Base URL of API
        """
        self.base_url = base_url.rstrip('/')
        self.test_cases: List[TestCase] = []
    
    def add_test(self, test_case: TestCase):
        """Add a test case."""
        self.test_cases.append(test_case)
    
    def generate_tests(self, endpoints: List[Dict]) -> List[TestCase]:
        """
        Generate test cases for endpoints.
        
        Args:
            endpoints: List of endpoint definitions
            
        Returns:
            List of generated test cases
        """
        tests = []
        
        for endpoint in endpoints:
            method = endpoint.get('method', 'GET')
            path = endpoint.get('path', '/')
            
            # Generate basic test
            test = TestCase(
                name=f"Test {method} {path}",
                method=method,
                endpoint=path,
                expected_status=200
            )
            tests.append(test)
            
            # Generate auth test if required
            if endpoint.get('auth_required'):
                auth_test = TestCase(
                    name=f"Test {method} {path} - Unauthorized",
                    method=method,
                    endpoint=path,
                    expected_status=401
                )
                tests.append(auth_test)
        
        return tests
    
    def run_tests(self, test_cases: Optional[List[TestCase]] = None) -> List[TestResult]:
        """
        Run API tests.
        
        Args:
            test_cases: Test cases to run (uses self.test_cases if None)
            
        Returns:
            List of test results
        """
        if test_cases is None:
            test_cases = self.test_cases
        
        results = []
        
        for test in test_cases:
            result = self._run_single_test(test)
            results.append(result)
        
        return results
    
    def _run_single_test(self, test: TestCase) -> TestResult:
        """Run a single test case."""
        import time
        
        try:
            import requests
        except ImportError:
            return TestResult(
                test_name=test.name,
                passed=False,
                error="requests library not installed"
            )
        
        url = f"{self.base_url}{test.endpoint}"
        
        start_time = time.time()
        
        try:
            response = requests.request(
                method=test.method,
                url=url,
                headers=test.headers,
                json=test.body,
                timeout=10
            )
            
            duration = (time.time() - start_time) * 1000
            
            # Check status code
            status_match = response.status_code == test.expected_status
            
            # Check response if expected
            response_match = True
            if test.expected_response:
                try:
                    actual_response = response.json()
                    response_match = actual_response == test.expected_response
                except:
                    response_match = False
            
            passed = status_match and response_match
            
            return TestResult(
                test_name=test.name,
                passed=passed,
                status_code=response.status_code,
                response=response.text[:200],
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            
            return TestResult(
                test_name=test.name,
                passed=False,
                error=str(e),
                duration_ms=duration
            )
    
    def generate_test_report(self, results: List[TestResult]) -> str:
        """Generate test report."""
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        
        report = f"""
API Test Report
===============

Total Tests: {total}
Passed: {passed}
Failed: {failed}
Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%

Test Results:
"""
        
        for result in results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            report += f"\n{status} - {result.test_name}"
            
            if result.status_code:
                report += f" (Status: {result.status_code})"
            
            if result.duration_ms:
                report += f" ({result.duration_ms:.0f}ms)"
            
            if result.error:
                report += f"\n  Error: {result.error}"
        
        return report
