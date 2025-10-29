
"""
Unit tests for C# Language-Specific Agents.

Tests for C# code analyzer and build agents.
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
# C# Agent Tests
# =============================================================================

class TestCSharpCodeAnalyzer:
    """Tests for C# Code Analyzer Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test C# code analyzer initialization."""
        from agents.languages.csharp.code_analyzer import CSharpCodeAnalyzerAgent
        
        agent = CSharpCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "code_analyzer_csharp"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_analyze_code(self, mock_llm_router):
        """Test C# code analysis."""
        from agents.languages.csharp.code_analyzer import CSharpCodeAnalyzerAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'C# code analysis complete'
        }
        
        agent = CSharpCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Analyze C# code", {})
        
        assert result is not None


class TestCSharpBuildAgent:
    """Tests for C# Build Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test C# build agent initialization."""
        from agents.languages.csharp.build_agent import CSharpBuildAgent
        
        agent = CSharpBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "csharp_build"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_build_task(self, mock_llm_router):
        """Test C# build task execution."""
        from agents.languages.csharp.build_agent import CSharpBuildAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'C# build completed'
        }
        
        agent = CSharpBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Build the C# project", {})
        
        assert result is not None
