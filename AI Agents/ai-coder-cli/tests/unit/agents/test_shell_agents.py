
"""
Unit tests for Shell Script Language-Specific Agents.

Tests for Shell script code analyzer and build agents.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_llm_router():
    """Create a mock LLM router."""
    router = Mock()
    router.query.return_value = {
        'success': True,
        'response': 'Mock LLM response',
        'model': 'llama3.2:3b'
    }
    return router


# =============================================================================
# Shell Script Agent Tests
# =============================================================================

class TestShellCodeAnalyzer:
    """Tests for Shell Script Code Analyzer Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Shell code analyzer initialization."""
        from agents.languages.shell.code_analyzer import ShellCodeAnalyzerAgent
        
        agent = ShellCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "code_analyzer_shell"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_analyze_script(self, mock_llm_router):
        """Test shell script analysis."""
        from agents.languages.shell.code_analyzer import ShellCodeAnalyzerAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Shell script analysis complete'
        }
        
        agent = ShellCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Analyze shell script for best practices", {})
        
        assert result is not None


class TestShellBuildAgent:
    """Tests for Shell Build Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Shell build agent initialization."""
        from agents.languages.shell.build_agent import ShellBuildAgent
        
        agent = ShellBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "shell_build"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_build_task(self, mock_llm_router):
        """Test Shell build task execution."""
        from agents.languages.shell.build_agent import ShellBuildAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Shell build completed'
        }
        
        agent = ShellBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Execute shell build script", {})
        
        assert result is not None
