"""
Prompt Manager Module

Manages reusable prompts and templates.
Phase 3 implementation.
"""

from .manager import PromptManager, Prompt
from .template_engine import TemplateEngine
from .defaults import DefaultPrompts

__all__ = [
    'PromptManager',
    'Prompt',
    'TemplateEngine',
    'DefaultPrompts'
]
