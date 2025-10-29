
"""
Unit tests for C++ Language-Specific Agents.

Tests for C++ code analyzer and build agents.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path


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


@pytest.fixture
def sample_cpp_code():
    """Sample C++ code for testing."""
    return '''
#include <iostream>

int calculateSum(int a, int b) {
    return a + b;
}

int main() {
    int result = calculateSum(5, 3);
    std::cout << "Result: " << result << std::endl;
    return 0;
}
'''


# =============================================================================
# C++ Agent Tests
# =============================================================================

class TestCppCodeAnalyzer:
    """Tests for C++ Code Analyzer Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test C++ code analyzer initialization."""
        from agents.languages.cpp.code_analyzer import CPPCodeAnalyzerAgent
        
        agent = CPPCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "code_analyzer_cpp"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_analyze_code(self, mock_llm_router, sample_cpp_code):
        """Test C++ code analysis."""
        from agents.languages.cpp.code_analyzer import CPPCodeAnalyzerAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'C++ code analysis complete'
        }
        
        agent = CPPCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute(f"Analyze this C++ code: {sample_cpp_code}", {})
        
        assert result is not None


class TestCPPBuildAgent:
    """Tests for C++ Build Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test C++ build agent initialization."""
        from agents.languages.cpp.build_agent import CPPBuildAgent
        
        agent = CPPBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "cpp_build"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_build_task(self, mock_llm_router):
        """Test C++ build task execution."""
        from agents.languages.cpp.build_agent import CPPBuildAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'C++ build completed'
        }
        
        agent = CPPBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Build the C++ project with CMake", {})
        
        assert result is not None
