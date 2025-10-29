"""
Unit tests for new infrastructure tools.

Tests for:
- ProjectManagementTool
- ChatHistoryTool
- DependencyTrackingTool
- ContextCacheTool
- GitCommitEnhancedTool
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import json
from datetime import datetime

from tools import (
    ProjectManagementTool,
    ChatHistoryTool,
    DependencyTrackingTool,
    ContextCacheTool,
    GitCommitEnhancedTool
)


class TestProjectManagementTool:
    """Tests for ProjectManagementTool."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_project):
        """Create a ProjectManagementTool instance."""
        return ProjectManagementTool({'project_root': temp_project})
    
    def test_tool_initialization(self, tool):
        """Test tool initialization."""
        assert tool.name == 'project_management'
        assert tool.description == 'Project-level state and memory management'
    
    def test_save_and_load_memory(self, tool):
        """Test saving and loading memory."""
        # Save memory
        result = tool.invoke({
            'action': 'save_memory',
            'key': 'test_key',
            'data': {'value': 'test_data'}
        })
        
        assert result['success'] is True
        assert result['key'] == 'test_key'
        
        # Load memory
        result = tool.invoke({
            'action': 'load_memory',
            'key': 'test_key'
        })
        
        assert result['success'] is True
        assert result['data'] == {'value': 'test_data'}
    
    def test_save_and_load_todo(self, tool):
        """Test saving and loading TODO lists."""
        todos = [
            {'task': 'Task 1', 'status': 'pending'},
            {'task': 'Task 2', 'status': 'completed'}
        ]
        
        # Save TODO
        result = tool.invoke({
            'action': 'save_todo',
            'name': 'my_todos',
            'todos': todos
        })
        
        assert result['success'] is True
        assert result['count'] == 2
        
        # Load TODO
        result = tool.invoke({
            'action': 'load_todo',
            'name': 'my_todos'
        })
        
        assert result['success'] is True
        assert len(result['todos']) == 2
    
    def test_save_and_load_preference(self, tool):
        """Test saving and loading preferences."""
        # Save preference
        result = tool.invoke({
            'action': 'save_preference',
            'key': 'theme',
            'value': 'dark'
        })
        
        assert result['success'] is True
        
        # Load preference
        result = tool.invoke({
            'action': 'load_preference',
            'key': 'theme'
        })
        
        assert result['success'] is True
        assert result['value'] == 'dark'
    
    def test_list_todos(self, tool):
        """Test listing TODO lists."""
        # Save multiple TODO lists
        tool.invoke({
            'action': 'save_todo',
            'name': 'list1',
            'todos': [{'task': 'Task 1'}]
        })
        
        tool.invoke({
            'action': 'save_todo',
            'name': 'list2',
            'todos': [{'task': 'Task 2'}]
        })
        
        # List todos
        result = tool.invoke({'action': 'list_todos'})
        
        assert result['success'] is True
        assert len(result['todos']) == 2
    
    def test_clear_memory(self, tool):
        """Test clearing memory."""
        # Save memory
        tool.invoke({
            'action': 'save_memory',
            'key': 'test_key',
            'data': {'value': 'test'}
        })
        
        # Clear specific key
        result = tool.invoke({
            'action': 'clear_memory',
            'key': 'test_key'
        })
        
        assert result['success'] is True
        
        # Verify cleared
        result = tool.invoke({
            'action': 'load_memory',
            'key': 'test_key'
        })
        
        assert result['success'] is False


class TestChatHistoryTool:
    """Tests for ChatHistoryTool."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_project):
        """Create a ChatHistoryTool instance."""
        return ChatHistoryTool({'project_root': temp_project})
    
    def test_tool_initialization(self, tool):
        """Test tool initialization."""
        assert tool.name == 'chat_history'
        assert tool.description == 'Chat history and context summary management'
    
    def test_create_session(self, tool):
        """Test creating a chat session."""
        result = tool.invoke({
            'action': 'create_session',
            'session_id': 'test_session',
            'metadata': {'user': 'john'}
        })
        
        assert result['success'] is True
        assert result['session_id'] == 'test_session'
    
    def test_save_and_load_message(self, tool):
        """Test saving and loading messages."""
        # Create session
        tool.invoke({
            'action': 'create_session',
            'session_id': 'test_session'
        })
        
        # Save message
        result = tool.invoke({
            'action': 'save_message',
            'session_id': 'test_session',
            'message': {
                'role': 'user',
                'content': 'Hello!',
                'timestamp': datetime.now().isoformat()
            }
        })
        
        assert result['success'] is True
        
        # Load history
        result = tool.invoke({
            'action': 'load_history',
            'session_id': 'test_session'
        })
        
        assert result['success'] is True
        assert len(result['messages']) == 1
        assert result['messages'][0]['content'] == 'Hello!'
    
    def test_save_and_load_summary(self, tool):
        """Test saving and loading summaries."""
        # Save summary
        result = tool.invoke({
            'action': 'save_summary',
            'session_id': 'test_session',
            'summary': 'Discussion about project X'
        })
        
        assert result['success'] is True
        
        # Load summary
        result = tool.invoke({
            'action': 'load_summary',
            'session_id': 'test_session'
        })
        
        assert result['success'] is True
        assert result['summary'] == 'Discussion about project X'
    
    def test_list_sessions(self, tool):
        """Test listing sessions."""
        # Create multiple sessions
        tool.invoke({
            'action': 'create_session',
            'session_id': 'session1'
        })
        
        tool.invoke({
            'action': 'create_session',
            'session_id': 'session2'
        })
        
        # List sessions
        result = tool.invoke({'action': 'list_sessions'})
        
        assert result['success'] is True
        assert result['total_count'] == 2


class TestContextCacheTool:
    """Tests for ContextCacheTool."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_project):
        """Create a ContextCacheTool instance."""
        return ContextCacheTool({'project_root': temp_project})
    
    def test_tool_initialization(self, tool):
        """Test tool initialization."""
        assert tool.name == 'context_cache'
        assert tool.description == 'Context management and result caching'
    
    def test_cache_and_get_result(self, tool):
        """Test caching and retrieving results."""
        # Cache result
        result = tool.invoke({
            'action': 'cache_result',
            'operation': 'test_op',
            'params_dict': {'param': 'value'},
            'result': {'data': 'cached_data'},
            'ttl_seconds': 3600
        })
        
        assert result['success'] is True
        
        # Get cached result
        result = tool.invoke({
            'action': 'get_cached',
            'operation': 'test_op',
            'params_dict': {'param': 'value'}
        })
        
        assert result['success'] is True
        assert result['cached'] is True
        assert result['result'] == {'data': 'cached_data'}
    
    def test_save_and_load_context(self, tool):
        """Test saving and loading context."""
        # Save context
        result = tool.invoke({
            'action': 'save_context',
            'context_type': 'result',
            'name': 'test_result',
            'data': {'value': 'test'}
        })
        
        assert result['success'] is True
        
        # Load context
        result = tool.invoke({
            'action': 'load_context',
            'context_type': 'result',
            'name': 'test_result'
        })
        
        assert result['success'] is True
        assert 'context' in result
    
    def test_clean_cache(self, tool):
        """Test cleaning expired cache."""
        result = tool.invoke({'action': 'clean_cache'})
        
        assert result['success'] is True
        assert 'removed_count' in result


class TestDependencyTrackingTool:
    """Tests for DependencyTrackingTool."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project with sample files."""
        temp_dir = tempfile.mkdtemp()
        
        # Create sample Python files
        (Path(temp_dir) / 'main.py').write_text(
            'import module1\nfrom module2 import func\n\ndef main():\n    pass'
        )
        
        (Path(temp_dir) / 'module1.py').write_text(
            'def helper():\n    pass'
        )
        
        (Path(temp_dir) / 'module2.py').write_text(
            'def func():\n    pass'
        )
        
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_project):
        """Create a DependencyTrackingTool instance."""
        return DependencyTrackingTool({'project_root': temp_project})
    
    def test_tool_initialization(self, tool):
        """Test tool initialization."""
        assert tool.name == 'dependency_tracking'
        assert tool.description == 'Multi-language codebase dependency analysis'
    
    def test_analyze_dependencies(self, tool):
        """Test dependency analysis."""
        result = tool.invoke({'action': 'analyze'})
        
        assert result['success'] is True
        assert 'stats' in result
    
    def test_get_stats(self, tool):
        """Test getting dependency statistics."""
        # Analyze first
        tool.invoke({'action': 'analyze'})
        
        # Get stats
        result = tool.invoke({'action': 'get_stats'})
        
        assert result['success'] is True
        assert 'stats' in result


class TestGitCommitEnhancedTool:
    """Tests for GitCommitEnhancedTool."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary git repository."""
        import subprocess
        
        temp_dir = tempfile.mkdtemp()
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=temp_dir, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_dir, check=True)
        
        # Create initial commit
        (Path(temp_dir) / 'README.md').write_text('# Test Project')
        subprocess.run(['git', 'add', '.'], cwd=temp_dir, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=temp_dir, check=True)
        
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_repo):
        """Create a GitCommitEnhancedTool instance."""
        return GitCommitEnhancedTool({'project_root': temp_repo, 'repo_path': temp_repo})
    
    def test_tool_initialization(self, tool):
        """Test tool initialization."""
        assert tool.name == 'git_commit_enhanced'
        assert tool.description == 'Enhanced git commit practices with detailed messages'
    
    def test_get_staged_changes(self, tool, temp_repo):
        """Test getting staged changes."""
        # Stage a file
        import subprocess
        test_file = Path(temp_repo) / 'test.txt'
        test_file.write_text('test content')
        subprocess.run(['git', 'add', 'test.txt'], cwd=temp_repo, check=True)
        
        # Get staged changes
        result = tool.invoke({'action': 'get_staged_changes'})
        
        assert result['success'] is True
        assert 'changes' in result
    
    def test_generate_message(self, tool):
        """Test generating conventional commit message."""
        result = tool.invoke({
            'action': 'generate_message',
            'message_type': 'feat',
            'scope': 'auth',
            'description': 'Add login functionality'
        })
        
        assert result['success'] is True
        assert result['message'] == 'feat(auth): Add login functionality'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
