
"""
Integration tests for Agent-Tool interactions.

Tests how agents interact with tools in realistic scenarios.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path


@pytest.mark.integration
class TestCodeEditorToolIntegration:
    """Test integration between code editor agent and file operations tool."""
    
    @pytest.fixture
    def setup_integration(self, mock_llm_router, mock_tool_registry, temp_project_dir):
        """Set up agent and tool for integration testing."""
        from agents.generic.generic_code_editor import GenericCodeEditor
        from tools.file_operations import FileOperationsTool
        
        # Create real file operations tool
        file_tool = FileOperationsTool(
            name='file_ops',
            description='File operations'
        )
        
        # Mock tool registry to return real file tool
        mock_tool_registry.get.return_value = file_tool
        
        # Create code editor agent
        agent = GenericCodeEditor(
            name='code_editor',
            description='Code editor',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
        
        return {
            'agent': agent,
            'file_tool': file_tool,
            'project_dir': temp_project_dir
        }
    
    def test_create_and_edit_file(self, setup_integration, mock_llm_router):
        """Test creating and editing a file through agent."""
        agent = setup_integration['agent']
        project_dir = setup_integration['project_dir']
        
        # Mock LLM to return file creation instructions
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Create file: test.py with content: print("Hello")'
        }
        
        task = "Create a Python file that prints Hello"
        context = {
            'project_path': str(project_dir),
            'language': 'python'
        }
        
        result = agent.execute(task, context)
        
        assert 'success' in result


@pytest.mark.integration
class TestGitAgentToolIntegration:
    """Test integration between git agent and git tool."""
    
    @pytest.fixture
    def setup_git_integration(self, mock_llm_router, mock_tool_registry, temp_project_dir, mock_git_repo):
        """Set up git agent and tool for integration testing."""
        from agents.git_agent import GitAgent
        from tools.git import GitTool
        
        # Create real git tool (GitTool hardcodes name and description)
        git_tool = GitTool(config={'use_gitpython': True})
        
        # Mock tool registry
        mock_tool_registry.get.return_value = git_tool
        
        # Create git agent
        agent = GitAgent(
            name='git',
            description='Git agent',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
        
        return {
            'agent': agent,
            'git_tool': git_tool,
            'repo': mock_git_repo,
            'project_dir': temp_project_dir
        }
    
    def test_commit_changes(self, setup_git_integration, mock_llm_router):
        """Test committing changes through git agent."""
        agent = setup_git_integration['agent']
        project_dir = setup_git_integration['project_dir']
        
        # Mock LLM response
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'git commit -m "Test commit"'
        }
        
        task = "Commit all changes with message 'Test commit'"
        context = {
            'project_path': str(project_dir),
            'repo_path': str(project_dir)
        }
        
        result = agent.execute(task, context)
        
        assert 'success' in result


@pytest.mark.integration
class TestWebSearchToolIntegration:
    """Test integration between web search agent and web tools."""
    
    @pytest.mark.requires_web
    def test_search_and_fetch(self, mock_llm_router, mock_tool_registry):
        """Test searching and fetching web content."""
        from agents.web_search import WebSearchAgent
        
        agent = WebSearchAgent(
            name='web_search',
            description='Web search',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
        
        # Mock LLM response
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Search results: Python best practices...'
        }
        
        task = "Find information about Python best practices"
        context = {}
        
        result = agent.execute(task, context)
        
        assert 'success' in result
