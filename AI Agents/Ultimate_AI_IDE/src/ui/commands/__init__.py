"""
CLI Command Modules

Modular command groups for the UAIDE CLI.
"""

from .mcp_commands import mcp
from .quality_commands import bloat, quality, context, index
from .workflow_commands import workflow, split, deadcode, automation

__all__ = [
    'mcp',
    'bloat',
    'quality',
    'context',
    'index',
    'workflow',
    'split',
    'deadcode',
    'automation'
]
