"""
Core Module

Core orchestration and integration components.
Phase 5 implementation.
"""

from .orchestrator import UAIDE
from .event_bus import EventBus, Event

__all__ = [
    'UAIDE',
    'EventBus',
    'Event'
]
