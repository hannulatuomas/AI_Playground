"""
Automated Testing Module

Provides comprehensive test generation, bug detection, and auto-fixing capabilities.
"""

from .test_generator import TestGenerator, CodeAnalyzer
from .code_analyzer import analyze_code

__all__ = ['TestGenerator', 'CodeAnalyzer', 'analyze_code']
