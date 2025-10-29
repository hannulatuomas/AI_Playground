"""
Security Scanner Module

Comprehensive security analysis for projects including:
- Vulnerability scanning (CVE detection)
- Dependency security checking
- Insecure pattern detection
- Secret scanning
- Security reporting
"""

from .scanner import SecurityScanner
from .vulnerability_scanner import VulnerabilityScanner
from .dependency_checker import DependencyChecker
from .pattern_detector import PatternDetector
from .secret_scanner import SecretScanner
from .reporter import SecurityReporter

__all__ = [
    'SecurityScanner',
    'VulnerabilityScanner',
    'DependencyChecker',
    'PatternDetector',
    'SecretScanner',
    'SecurityReporter'
]

__version__ = '1.5.0'
