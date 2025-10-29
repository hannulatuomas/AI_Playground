"""
Documentation Manager Module

Automatic documentation generation and synchronization.
Phase 3 implementation.
"""

from .manager import DocManager, SyncReport
from .scanner import CodeScanner, CodeStructure
from .generator import DocGenerator, Documentation

__all__ = [
    'DocManager',
    'SyncReport',
    'CodeScanner',
    'CodeStructure',
    'DocGenerator',
    'Documentation'
]
