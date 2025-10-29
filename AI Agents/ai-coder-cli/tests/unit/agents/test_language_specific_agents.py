"""
Unit tests for Language-Specific Agents.

NOTE: This file has been split into separate test files for better performance and maintainability:
- test_python_agents.py - Python language agents (8 agent types)
- test_cpp_agents.py - C++ language agents
- test_csharp_agents.py - C# language agents
- test_web_agents.py - Web/JS/TS language agents
- test_shell_agents.py - Shell script agents
- test_powershell_agents.py - PowerShell agents  
- test_batch_agents.py - Batch script agents

This split allows for:
1. Faster parallel test execution
2. Better test isolation
3. Easier maintenance and navigation
4. Independent test running per language

To run tests for a specific language:
    pytest tests/unit/agents/test_python_agents.py
    pytest tests/unit/agents/test_cpp_agents.py
    etc.

To run all language-specific agent tests:
    pytest tests/unit/agents/test_*_agents.py
"""

# Import all test classes for backward compatibility
# This allows the test suite to still find and run all tests from this file
try:
    from .test_python_agents import *
    from .test_cpp_agents import *
    from .test_csharp_agents import *
    from .test_web_agents import *
    from .test_shell_agents import *
    from .test_powershell_agents import *
    from .test_batch_agents import *
except ImportError:
    # If imports fail, tests can still be run from individual files
    pass
