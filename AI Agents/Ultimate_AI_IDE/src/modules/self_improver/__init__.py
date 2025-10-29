"""
Self-Improver Module

Learns from errors and improves over time.
Phase 4 implementation.
"""

from .logger import EventLogger, LogEntry
from .analyzer import PatternAnalyzer, ErrorPattern, SuccessPattern
from .learner import Learner, Insight
from .adapter import Adapter, Adaptation

__all__ = [
    'EventLogger',
    'LogEntry',
    'PatternAnalyzer',
    'ErrorPattern',
    'SuccessPattern',
    'Learner',
    'Insight',
    'Adapter',
    'Adaptation'
]
