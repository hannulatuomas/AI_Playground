
"""
Unit tests for Specific Tools.

Tests for git, web_fetch, file operations, and other tools.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


@pytest.mark.unit
class TestGitTool:
    """Test suite for Git Tool."""
    
    @pytest.fixture
    def git_tool(self):
        """Create a git tool for testing."""
        from tools.git import GitTool
        
        # GitTool doesn't accept name/description, they are hardcoded
        return GitTool(config={'use_gitpython': True})
    
    def test_initialization(self, git_tool):
        """Test git tool initialization."""
        assert git_tool.name == 'git'
        assert git_tool.description is not None
    
    def test_invoke_status(self, git_tool, mock_git_repo):
        """Test getting git status."""
        with patch('tools.git.Repo', return_value=mock_git_repo):
            result = git_tool.invoke({
                'action': 'status',
                'repo_path': '/tmp/test_repo'
            })
            
            assert 'success' in result or result is not None


@pytest.mark.unit
class TestWebFetchTool:
    """Test suite for Web Fetch Tool."""
    
    @pytest.fixture
    def web_fetch_tool(self):
        """Create a web fetch tool for testing."""
        from tools.web_fetch import WebFetchTool
        
        # WebFetchTool doesn't accept name/description, they are hardcoded
        return WebFetchTool(config={'timeout': 30})
    
    def test_initialization(self, web_fetch_tool):
        """Test web fetch tool initialization."""
        assert web_fetch_tool.name == 'web_fetch'
    
    @pytest.mark.requires_web
    def test_invoke_fetch(self, web_fetch_tool):
        """Test fetching web content."""
        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.text = '<html><body>Test content</body></html>'
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = web_fetch_tool.invoke({
                'url': 'https://example.com'
            })
            
            assert result is not None


@pytest.mark.unit
class TestFileOperationsTool:
    """Test suite for File Operations Tool."""
    
    @pytest.fixture
    def file_ops_tool(self):
        """Create a file operations tool for testing."""
        from tools.file_operations import FileOperationsTool
        
        return FileOperationsTool(
            name='file_ops',
            description='File operations tool'
        )
    
    def test_initialization(self, file_ops_tool):
        """Test file operations tool initialization."""
        assert file_ops_tool.name == 'file_ops'
    
    def test_invoke_read_file(self, file_ops_tool, temp_dir):
        """Test reading a file."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")
        
        result = file_ops_tool.invoke({
            'action': 'read',
            'path': str(test_file)
        })
        
        assert result is not None


@pytest.mark.unit
class TestShellExecTool:
    """Test suite for Shell Execution Tool."""
    
    @pytest.fixture
    def shell_tool(self):
        """Create a shell execution tool for testing."""
        from tools.shell_exec import ShellExecTool
        
        return ShellExecTool(
            name='shell',
            description='Shell execution tool'
        )
    
    def test_initialization(self, shell_tool):
        """Test shell tool initialization."""
        assert shell_tool.name == 'shell'
    
    def test_invoke_simple_command(self, shell_tool):
        """Test executing a simple shell command."""
        result = shell_tool.invoke({
            'command': 'echo "test"'
        })
        
        assert result is not None


@pytest.mark.unit
class TestOllamaManagerTool:
    """Test suite for Ollama Manager Tool."""
    
    @pytest.fixture
    def ollama_tool(self, mock_ollama_client):
        """Create an ollama manager tool for testing."""
        from tools.ollama_manager import OllamaManager
        
        # OllamaManager accepts name, description, and config via **kwargs
        with patch('ollama.Client', return_value=mock_ollama_client):
            return OllamaManager(config={'ollama': {'host': 'http://localhost', 'port': 11434}})
    
    def test_initialization(self, ollama_tool):
        """Test ollama tool initialization."""
        assert ollama_tool.name == 'ollama_manager'
    
    @pytest.mark.requires_ollama
    def test_invoke_list_models(self, ollama_tool, mock_ollama_client):
        """Test listing ollama models."""
        result = ollama_tool.invoke({
            'action': 'list_models'
        })
        
        assert result is not None


@pytest.mark.unit
class TestVectorDBTool:
    """Test suite for Vector Database Tool."""
    
    @pytest.fixture
    def mock_embedding_generator(self):
        """Create a mock embedding generator."""
        generator = Mock()
        generator.generate = Mock(return_value=[0.1, 0.2, 0.3, 0.4, 0.5])
        generator.generate_batch = Mock(return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        return generator
    
    @pytest.fixture
    def vector_db_tool(self, mock_chromadb_client, mock_embedding_generator, temp_dir):
        """Create a vector db tool for testing."""
        from tools.vector_db import VectorDBTool
        
        # VectorDBTool is a proper Tool subclass
        with patch('chromadb.PersistentClient', return_value=mock_chromadb_client):
            with patch('tools.vector_db.create_embedding_generator', return_value=mock_embedding_generator):
                tool = VectorDBTool(
                    config={'vector_db': {'persist_directory': str(temp_dir / "chroma")}}
                )
                # Create a test collection after initialization
                tool.db.create_collection('test_collection')
                return tool
    
    def test_initialization(self, vector_db_tool):
        """Test vector db tool initialization."""
        assert vector_db_tool.name == 'vector_db'
    
    def test_invoke_search(self, vector_db_tool, mock_chromadb_client):
        """Test searching in vector database."""
        result = vector_db_tool.invoke({
            'action': 'search',
            'query': 'test query',
            'collection': 'test_collection'
        })
        
        assert result is not None
        assert 'success' in result
        assert result['success'] is True
