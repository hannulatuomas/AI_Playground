"""
Integration tests for Tool System.

Tests interactions between different tools and components.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


@pytest.mark.integration
class TestVectorDBEmbeddingIntegration:
    """Test Vector DB integration with Embeddings."""
    
    @pytest.fixture
    def vector_db_with_embeddings(self, mock_chromadb_client, temp_dir):
        """Create vector DB with real embedding generator mock."""
        from tools.vector_db import VectorDBTool
        
        # Mock embedding generator
        mock_generator = Mock()
        mock_generator.generate = Mock(return_value=[0.1, 0.2, 0.3, 0.4, 0.5])
        mock_generator.generate_batch = Mock(return_value=[
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9]
        ])
        
        with patch('chromadb.PersistentClient', return_value=mock_chromadb_client):
            with patch('tools.vector_db.create_embedding_generator', return_value=mock_generator):
                tool = VectorDBTool(
                    config={'vector_db': {'persist_directory': str(temp_dir / "chroma")}}
                )
                return tool, mock_generator
    
    def test_add_and_search_documents(self, vector_db_with_embeddings):
        """Test adding documents and searching."""
        tool, mock_generator = vector_db_with_embeddings
        
        # Create collection
        result = tool.invoke({
            'action': 'create_collection',
            'collection': 'test_docs'
        })
        assert result['success']
        
        # Add documents
        result = tool.invoke({
            'action': 'add_documents',
            'collection': 'test_docs',
            'documents': ['Document 1', 'Document 2', 'Document 3'],
            'metadatas': [
                {'source': 'file1.txt'},
                {'source': 'file2.txt'},
                {'source': 'file3.txt'}
            ]
        })
        assert result['success']
        assert result['count'] == 3
        
        # Verify embeddings were generated
        assert mock_generator.generate_batch.called
        
        # Search documents
        result = tool.invoke({
            'action': 'search',
            'collection': 'test_docs',
            'query': 'test query',
            'n_results': 2
        })
        assert result['success']
        assert 'results' in result


@pytest.mark.integration
class TestFileToolsIntegration:
    """Test File Operations and File I/O integration."""
    
    @pytest.fixture
    def file_tools(self, temp_dir):
        """Create file operation tools."""
        from tools.file_operations import FileOperationsTool
        from tools.file_io import FileIOTool
        
        file_ops = FileOperationsTool(
            name='file_ops',
            description='File operations'
        )
        
        file_io = FileIOTool(
            name='file_io',
            description='File I/O',
            config={'working_dir': str(temp_dir)}
        )
        
        return {
            'file_ops': file_ops,
            'file_io': file_io,
            'temp_dir': temp_dir
        }
    
    def test_create_and_read_file(self, file_tools):
        """Test creating and reading files."""
        file_ops = file_tools['file_ops']
        file_io = file_tools['file_io']
        temp_dir = file_tools['temp_dir']
        
        test_file = temp_dir / "test.txt"
        test_content = "Hello, World!"
        
        # Create file using file_ops
        result = file_ops.invoke({
            'action': 'write',
            'path': str(test_file),
            'content': test_content
        })
        assert result is not None
        
        # Read file using file_io
        result = file_io.invoke({
            'action': 'read',
            'path': str(test_file)
        })
        assert result is not None
    
    def test_file_operations_workflow(self, file_tools):
        """Test a complete file operations workflow."""
        file_ops = file_tools['file_ops']
        temp_dir = file_tools['temp_dir']
        
        # Create a directory
        new_dir = temp_dir / "project"
        new_dir.mkdir(exist_ok=True)
        
        # Create multiple files
        files = ['file1.py', 'file2.py', 'readme.md']
        for filename in files:
            file_path = new_dir / filename
            result = file_ops.invoke({
                'action': 'write',
                'path': str(file_path),
                'content': f'Content of {filename}'
            })
            assert result is not None
        
        # List files
        result = file_ops.invoke({
            'action': 'list',
            'path': str(new_dir)
        })
        assert result is not None


@pytest.mark.integration
class TestGitShellIntegration:
    """Test Git Tool integration with Shell Execution."""
    
    @pytest.fixture
    def git_shell_tools(self, temp_project_dir, mock_git_repo):
        """Create git and shell tools."""
        from tools.git import GitTool
        from tools.shell_exec import ShellExecTool
        
        git_tool = GitTool(config={'use_gitpython': True})
        shell_tool = ShellExecTool(
            name='shell',
            description='Shell execution'
        )
        
        return {
            'git': git_tool,
            'shell': shell_tool,
            'project_dir': temp_project_dir,
            'mock_repo': mock_git_repo
        }
    
    def test_git_status_and_shell(self, git_shell_tools):
        """Test git status check."""
        git_tool = git_shell_tools['git']
        project_dir = git_shell_tools['project_dir']
        mock_repo = git_shell_tools['mock_repo']
        
        with patch('tools.git.Repo', return_value=mock_repo):
            result = git_tool.invoke({
                'action': 'status',
                'repo_path': str(project_dir)
            })
            assert result is not None


@pytest.mark.integration
class TestToolRegistryIntegration:
    """Test Tool Registry with multiple tools."""
    
    @pytest.fixture
    def registry_with_tools(self, temp_dir):
        """Create registry with various tools."""
        from tools.registry import ToolRegistry
        from tools.git import GitTool
        from tools.shell_exec import ShellExecTool
        from tools.file_operations import FileOperationsTool
        
        registry = ToolRegistry()
        
        # Register tools
        git_tool = GitTool(config={})
        shell_tool = ShellExecTool(name='shell', description='Shell')
        file_tool = FileOperationsTool(name='file_ops', description='File ops')
        
        registry.register(git_tool)
        registry.register(shell_tool)
        registry.register(file_tool)
        
        return registry
    
    def test_registry_operations(self, registry_with_tools):
        """Test registry with multiple tools."""
        registry = registry_with_tools
        
        # List tools
        tools = registry.list_tools()
        assert len(tools) >= 3
        assert 'git' in tools
        assert 'shell' in tools
        assert 'file_ops' in tools
        
        # Get specific tool
        git_tool = registry.get('git')
        assert git_tool is not None
        assert git_tool.name == 'git'
        
        # Get all tools
        all_tools = registry.list_all()
        assert len(all_tools) >= 3
    
    def test_registry_invoke_tools(self, registry_with_tools):
        """Test invoking tools through registry."""
        registry = registry_with_tools
        
        # Get shell tool
        shell_tool = registry.get('shell')
        assert shell_tool is not None
        
        # Invoke simple command
        result = shell_tool.invoke({
            'command': 'echo "test"'
        })
        assert result is not None


@pytest.mark.integration
class TestWebFetchWithCache:
    """Test Web Fetch Tool integration with caching."""
    
    @pytest.fixture
    def web_tool_with_cache(self, temp_dir):
        """Create web fetch tool with cache."""
        from tools.web_fetch import WebFetchTool
        from core.cache import Cache, FileCacheBackend
        
        backend = FileCacheBackend(cache_dir=str(temp_dir / "cache"))
        cache = Cache(backend=backend, default_ttl=3600)
        web_tool = WebFetchTool(config={'timeout': 30, 'cache': cache})
        
        return {
            'web_tool': web_tool,
            'cache': cache
        }
    
    def test_web_fetch_with_cache(self, web_tool_with_cache):
        """Test web fetching with caching."""
        web_tool = web_tool_with_cache['web_tool']
        
        with patch('httpx.get') as mock_get:
            # Mock HTTP response
            mock_response = Mock()
            mock_response.text = '<html><body>Test content</body></html>'
            mock_response.status_code = 200
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value = mock_response
            
            # First fetch
            result1 = web_tool.invoke({
                'url': 'https://example.com'
            })
            assert result1 is not None
            
            # Second fetch (should use cache if implemented)
            result2 = web_tool.invoke({
                'url': 'https://example.com'
            })
            assert result2 is not None
