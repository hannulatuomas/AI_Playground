#!/usr/bin/env python3
"""
Run All Tests - Cross-Platform Test Runner

Runs all test suites in the AI Coding Assistant project.
Works on Windows, Linux, and macOS.

Usage:
    python run_all_tests.py
    python run_all_tests.py --verbose
    python run_all_tests.py --stop-on-fail
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple


class TestRunner:
    """Cross-platform test runner for all test suites."""
    
    def __init__(self, verbose: bool = False, stop_on_fail: bool = False):
        """Initialize test runner."""
        self.verbose = verbose
        self.stop_on_fail = stop_on_fail
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def run_test_script(self, name: str, script_path: Path) -> bool:
        """
        Run a test script and return success status.
        
        Args:
            name: Test suite name
            script_path: Path to test script
            
        Returns:
            True if tests passed, False otherwise
        """
        if not script_path.exists():
            print(f"[SKIP] {name} - script not found")
            return None
        
        print(f"\nRunning {name}...")
        print("=" * 60)
        
        try:
            # Determine how to run the script
            if script_path.suffix == '.bat':
                if sys.platform == 'win32':
                    result = subprocess.run(
                        [str(script_path)],
                        shell=True,
                        cwd=script_path.parent.parent,
                        capture_output=not self.verbose
                    )
                else:
                    print(f"[SKIP] {name} - .bat files not supported on this platform")
                    return None
            elif script_path.suffix == '.py':
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    cwd=script_path.parent if script_path.parent.name == 'tests' else script_path.parent.parent,
                    capture_output=not self.verbose
                )
            else:
                print(f"[SKIP] {name} - unknown script type")
                return None
            
            passed = result.returncode == 0
            
            if passed:
                print(f"[PASS] {name}")
            else:
                print(f"[FAIL] {name}")
                if not self.verbose and result.stderr:
                    print(f"Error output:\n{result.stderr.decode('utf-8', errors='ignore')}")
            
            return passed
            
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            return False
    
    def run_all_tests(self) -> Tuple[int, int, int]:
        """
        Run all test suites.
        
        Returns:
            Tuple of (total, passed, failed)
        """
        self.start_time = time.time()
        
        print("=" * 60)
        print("AI Coding Assistant - Complete Test Suite")
        print("Version: 2.1.0")
        print("=" * 60)
        print()
        
        # Define all test suites
        test_suites = [
            ("Core Tests", Path("scripts/run_tests.bat")),
            ("RAG Tests", Path("tests/test_rag.py")),
            ("Advanced RAG Tests", Path("tests/test_rag_advanced.py")),
            ("Phase 9.2 Tests", Path("tests/test_phase_92.py")),
            ("Phase 9.3 Tests", Path("tests/test_phase_93.py")),
            ("Project Lifecycle Tests", Path("tests/test_templates.py")),
            ("Automated Testing Tests", Path("test_automated_testing.py")),
        ]
        
        total = 0
        passed = 0
        failed = 0
        
        for i, (name, script_path) in enumerate(test_suites, 1):
            print(f"\n[{i}/{len(test_suites)}] {name}")
            print("=" * 60)
            
            result = self.run_test_script(name, script_path)
            
            if result is None:
                # Skipped
                continue
            
            total += 1
            self.results.append((name, result))
            
            if result:
                passed += 1
            else:
                failed += 1
                if self.stop_on_fail:
                    print("\nStopping on first failure (--stop-on-fail)")
                    break
        
        self.end_time = time.time()
        
        return total, passed, failed
    
    def print_summary(self, total: int, passed: int, failed: int):
        """Print test summary."""
        duration = self.end_time - self.start_time
        
        print()
        print("=" * 60)
        print("Test Execution Complete")
        print("=" * 60)
        print()
        print(f"Duration: {duration:.2f} seconds")
        print()
        print("=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Total Test Suites: {total}")
        print(f"Passed:            {passed}")
        print(f"Failed:            {failed}")
        print()
        
        # Print individual results
        if self.results:
            print("Detailed Results:")
            for name, result in self.results:
                status = "✓ PASS" if result else "✗ FAIL"
                print(f"  {status}: {name}")
            print()
        
        # Final status
        if failed == 0:
            print("Result: ALL TESTS PASSED!")
            print("Status: ✓ SUCCESS")
        else:
            print("Result: SOME TESTS FAILED")
            print("Status: ✗ FAILURE")
            print()
            print("Please review the failed tests above.")
        
        print("=" * 60)
        print()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run all test suites for AI Coding Assistant"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show verbose output from tests'
    )
    parser.add_argument(
        '--stop-on-fail', '-s',
        action='store_true',
        help='Stop on first test failure'
    )
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent
    import os
    os.chdir(project_root)
    
    # Run tests
    runner = TestRunner(verbose=args.verbose, stop_on_fail=args.stop_on_fail)
    total, passed, failed = runner.run_all_tests()
    runner.print_summary(total, passed, failed)
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
