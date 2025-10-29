"""
Rule Manager Module

Manages coding rules and best practices.
Phase 4 implementation.
"""

from .manager import RuleManager, Rule, RuleScope, RuleCategory
from .validator import RuleValidator, ValidationResult, Violation
from .parser import RuleParser
from .defaults import DefaultRules

__all__ = [
    'RuleManager',
    'Rule',
    'RuleScope',
    'RuleCategory',
    'RuleValidator',
    'ValidationResult',
    'Violation',
    'RuleParser',
    'DefaultRules'
]
