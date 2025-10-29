"""
Unit tests for Python Language-Specific Agents.

Tests for Python code analyzer, builder, editor, planner, tester,
debug, documentation, and project initialization agents.
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
def mock_tool_registry():
    """Create a mock tool registry."""
    registry = Mock()
    return registry


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing."""
    return '''
def calculate_sum(a: int, b: int) -> int:
    """Calculate sum of two numbers."""
    return a + b

def main():
    result = calculate_sum(5, 3)
    print(f"Result: {result}")
'''


# =============================================================================
# Python Agent Tests
# =============================================================================

class TestPythonCodeAnalyzer:
    """Tests for Python Code Analyzer Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Python code analyzer initialization."""
        from agents.languages.python.code_analyzer import PythonCodeAnalyzerAgent
        
        agent = PythonCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "code_analyzer_python"
        assert "Python" in agent.description or "python" in agent.description
        assert agent.llm_router == mock_llm_router
    
    def test_execute_analyze_code(self, mock_llm_router, sample_python_code):
        """Test code analysis execution."""
        from agents.languages.python.code_analyzer import PythonCodeAnalyzerAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Code analysis: Good structure, follows PEP 8'
        }
        
        agent = PythonCodeAnalyzerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute(f"Analyze this code: {sample_python_code}", {})
        
        assert result is not None


class TestPythonBuildAgent:
    """Tests for Python Build Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Python build agent initialization."""
        from agents.languages.python.build_agent import PythonBuildAgent
        
        agent = PythonBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "python_build"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_build_task(self, mock_llm_router):
        """Test build task execution."""
        from agents.languages.python.build_agent import PythonBuildAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Build completed successfully'
        }
        
        agent = PythonBuildAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Build the Python project", {})
        
        assert result is not None


class TestPythonCodeEditor:
    """Tests for Python Code Editor Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Python code editor initialization."""
        from agents.languages.python.code_editor import PythonCodeEditorAgent
        
        agent = PythonCodeEditorAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "code_editor_python"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_edit_code(self, mock_llm_router, sample_python_code):
        """Test code editing execution."""
        from agents.languages.python.code_editor import PythonCodeEditorAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Code edited successfully'
        }
        
        agent = PythonCodeEditorAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute(f"Add error handling to: {sample_python_code}", {})
        
        assert result is not None


class TestPythonCodePlanner:
    """Tests for Python Code Planner Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Python code planner initialization."""
        from agents.languages.python.code_planner import PythonCodePlannerAgent
        
        agent = PythonCodePlannerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "code_planner_python"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_plan_code(self, mock_llm_router):
        """Test code planning execution."""
        from agents.languages.python.code_planner import PythonCodePlannerAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Plan: Create main module, implement functions, add tests'
        }
        
        agent = PythonCodePlannerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Plan implementation of a REST API", {})
        
        assert result is not None


class TestPythonCodeTester:
    """Tests for Python Code Tester Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Python code tester initialization."""
        from agents.languages.python.code_tester import PythonCodeTesterAgent
        
        agent = PythonCodeTesterAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "code_tester_python"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_test_code(self, mock_llm_router):
        """Test code testing execution."""
        from agents.languages.python.code_tester import PythonCodeTesterAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'All tests passed'
        }
        
        agent = PythonCodeTesterAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Run unit tests", {})
        
        assert result is not None


class TestPythonDebugAgent:
    """Tests for Python Debug Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Python debug agent initialization."""
        from agents.languages.python.debug_agent import PythonDebugAgent
        
        agent = PythonDebugAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "debug_agent_python"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_debug_code(self, mock_llm_router):
        """Test debugging execution."""
        from agents.languages.python.debug_agent import PythonDebugAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Bug found: IndexError at line 10'
        }
        
        agent = PythonDebugAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Debug IndexError in main function", {})
        
        assert result is not None


class TestPythonDocumentationAgent:
    """Tests for Python Documentation Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Python documentation agent initialization."""
        from agents.languages.python.documentation_agent import PythonDocumentationAgent
        
        agent = PythonDocumentationAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "documentation_agent_python"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_generate_docs(self, mock_llm_router, sample_python_code):
        """Test documentation generation."""
        from agents.languages.python.documentation_agent import PythonDocumentationAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Documentation generated'
        }
        
        agent = PythonDocumentationAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute(f"Generate documentation for: {sample_python_code}", {})
        
        assert result is not None


class TestPythonProjectInitAgent:
    """Tests for Python Project Init Agent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Python project init agent initialization."""
        from agents.languages.python.project_init_agent import PythonProjectInitAgent
        
        agent = PythonProjectInitAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "project_init_python"
        assert agent.llm_router == mock_llm_router
    
    def test_execute_init_project(self, mock_llm_router):
        """Test project initialization."""
        from agents.languages.python.project_init_agent import PythonProjectInitAgent
        
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Project initialized'
        }
        
        agent = PythonProjectInitAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Initialize a new Flask project", {})
        
        assert result is not None
