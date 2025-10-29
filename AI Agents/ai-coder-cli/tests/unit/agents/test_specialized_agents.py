
"""
Unit tests for Specialized Agents.

Tests for web search, database, git, and other specialized agents.
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestWebSearchAgent:
    """Test suite for Web Search Agent."""
    
    @pytest.fixture
    def web_search_agent(self, mock_llm_router, mock_tool_registry):
        """Create a web search agent for testing."""
        from agents.web_search import WebSearchAgent
        
        return WebSearchAgent(
            name='web_search',
            description='Web search agent',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
    
    def test_initialization(self, web_search_agent):
        """Test web search agent initialization."""
        assert web_search_agent.name == 'web_search'
    
    @pytest.mark.requires_web
    def test_execute_search(self, web_search_agent, mock_llm_router, sample_task_context):
        """Test executing a web search."""
        task = "Search for Python best practices"
        
        # Mock LLM response
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Found information about Python best practices'
        }
        
        result = web_search_agent.execute(task, sample_task_context)
        
        assert 'success' in result


@pytest.mark.unit
class TestDatabaseAgent:
    """Test suite for Database Agent."""
    
    @pytest.fixture
    def database_agent(self, mock_llm_router, mock_tool_registry):
        """Create a database agent for testing."""
        from agents.database import DatabaseAgent
        
        return DatabaseAgent(
            name='database',
            description='Database agent',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
    
    def test_initialization(self, database_agent):
        """Test database agent initialization."""
        assert database_agent.name == 'database'
    
    @pytest.mark.requires_db
    def test_execute_query(self, database_agent, mock_llm_router, sample_task_context):
        """Test executing a database query."""
        task = "Query users table"
        
        # Mock LLM response
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'SELECT * FROM users'
        }
        
        result = database_agent.execute(task, sample_task_context)
        
        assert 'success' in result


@pytest.mark.unit
class TestGitAgent:
    """Test suite for Git Agent."""
    
    @pytest.fixture
    def git_agent(self, mock_llm_router, mock_tool_registry):
        """Create a git agent for testing."""
        from agents.git_agent import GitAgent
        
        return GitAgent(
            name='git',
            description='Git agent',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
    
    def test_initialization(self, git_agent):
        """Test git agent initialization."""
        assert git_agent.name == 'git'
    
    def test_execute_git_command(self, git_agent, mock_llm_router, sample_task_context):
        """Test executing a git command."""
        task = "Commit changes with message 'Initial commit'"
        
        # Mock LLM response
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Changes committed successfully'
        }
        
        result = git_agent.execute(task, sample_task_context)
        
        assert 'success' in result


@pytest.mark.unit
class TestDataAnalysisAgent:
    """Test suite for Data Analysis Agent."""
    
    @pytest.fixture
    def data_analysis_agent(self, mock_llm_router, mock_tool_registry):
        """Create a data analysis agent for testing."""
        from agents.data_analysis import DataAnalysisAgent
        
        return DataAnalysisAgent(
            name='data_analysis',
            description='Data analysis agent',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
    
    def test_initialization(self, data_analysis_agent):
        """Test data analysis agent initialization."""
        assert data_analysis_agent.name == 'data_analysis'
    
    def test_execute_analysis(self, data_analysis_agent, mock_llm_router, sample_task_context):
        """Test executing data analysis."""
        task = "Analyze sales data"
        
        # Mock LLM response
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Analysis completed: Average sales: $1000'
        }
        
        result = data_analysis_agent.execute(task, sample_task_context)
        
        assert 'success' in result
