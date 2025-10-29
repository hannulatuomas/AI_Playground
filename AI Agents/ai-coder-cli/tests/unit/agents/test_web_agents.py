
"""
Unit tests for Web Language-Specific Agents.

Tests for Web/JS/TS code analyzer and build agents for HTML, CSS, JavaScript, and TypeScript.
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
# Web Agent Tests
# =============================================================================

class TestWebCodeAnalyzer:
    """Tests for Web Code Analyzer Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Web code analyzer initialization."""
        from agents.languages.web.code_analyzer import WebJSTSCodeAnalyzerAgent
        
        agent = WebJSTSCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "code_analyzer_web"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_analyze_html(self, mock_llm_router):
        """Test web code analysis."""
        from agents.languages.web.code_analyzer import WebJSTSCodeAnalyzerAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Web code analysis complete'
        }
        
        agent = WebJSTSCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Analyze HTML/CSS/JavaScript code", {})
        
        assert result is not None


class TestWebJSTSBuildAgent:
    """Tests for Web Build Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Web build agent initialization."""
        from agents.languages.web.build_agent import WebJSTSBuildAgent
        
        agent = WebJSTSBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "web_build"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_build_frontend(self, mock_llm_router):
        """Test web build execution."""
        from agents.languages.web.build_agent import WebJSTSBuildAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Frontend build complete'
        }
        
        agent = WebJSTSBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Build React application", {})
        
        assert result is not None
