
"""
Language-specific agent implementations.

This package contains agent implementations organized by programming language.
"""

# Import all language-specific agent modules
from . import python
from . import csharp
from . import cpp
from . import web
from . import shell
from . import powershell
from . import batch

__all__ = [
    'python',
    'csharp',
    'cpp',
    'web',
    'shell',
    'powershell',
    'batch',
]
