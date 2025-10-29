
"""
Unit tests for Batch Script Language-Specific Agents.

Tests for Windows Batch script code analyzer and build agents.
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
# Batch Script Agent Tests
# =============================================================================

class TestBatchCodeAnalyzer:
    """Tests for Batch Script Code Analyzer Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Batch code analyzer initialization."""
        from agents.languages.batch.code_analyzer import BatchCodeAnalyzerAgent
        
        agent = BatchCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "code_analyzer_batch"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_analyze_script(self, mock_llm_router):
        """Test Batch script analysis."""
        from agents.languages.batch.code_analyzer import BatchCodeAnalyzerAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Batch script analysis complete'
        }
        
        agent = BatchCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Analyze batch script", {})
        
        assert result is not None


class TestBatchBuildAgent:
    """Tests for Batch Build Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Batch build agent initialization."""
        from agents.languages.batch.build_agent import BatchBuildAgent
        
        agent = BatchBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "batch_build"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_build_task(self, mock_llm_router):
        """Test Batch build task execution."""
        from agents.languages.batch.build_agent import BatchBuildAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Batch build completed'
        }
        
        agent = BatchBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Execute batch build script", {})
        
        assert result is not None
