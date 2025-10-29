
"""
Unit tests for PowerShell Language-Specific Agents.

Tests for PowerShell code analyzer and build agents.
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
# PowerShell Agent Tests
# =============================================================================

class TestPowerShellCodeAnalyzer:
    """Tests for PowerShell Code Analyzer Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test PowerShell code analyzer initialization."""
        from agents.languages.powershell.code_analyzer import PowerShellCodeAnalyzerAgent
        
        agent = PowerShellCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "code_analyzer_powershell"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_analyze_script(self, mock_llm_router):
        """Test PowerShell script analysis."""
        from agents.languages.powershell.code_analyzer import PowerShellCodeAnalyzerAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'PowerShell script analysis complete'
        }
        
        agent = PowerShellCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Analyze PowerShell script", {})
        
        assert result is not None


class TestPowerShellBuildAgent:
    """Tests for PowerShell Build Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test PowerShell build agent initialization."""
        from agents.languages.powershell.build_agent import PowerShellBuildAgent
        
        agent = PowerShellBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "powershell_build"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_build_task(self, mock_llm_router):
        """Test PowerShell build task execution."""
        from agents.languages.powershell.build_agent import PowerShellBuildAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'PowerShell build completed'
        }
        
        agent = PowerShellBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Execute PowerShell build script", {})
        
        assert result is not None
