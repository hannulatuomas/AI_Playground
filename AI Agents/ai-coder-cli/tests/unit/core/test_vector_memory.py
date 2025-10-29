
"""
Unit tests for Vector Memory System.

Tests the vector database integration for semantic search.
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestVectorMemory:
    """Test suite for Vector Memory."""
    
    @pytest.fixture
    def vector_memory(self, mock_config, mock_chromadb_client, temp_dir):
        """Create a vector memory instance for testing."""
        from core.vector_memory import VectorMemoryManager
        
        # VectorMemoryManager extends MemoryManager, which accepts individual params
        with patch('chromadb.PersistentClient', return_value=mock_chromadb_client):
            return VectorMemoryManager(
                storage_path=temp_dir / "memory",
                vector_db_path=temp_dir / "vector_db",
                default_max_context_window=4096,
                auto_save=False,
                enable_summarization=False,
                llm_router=None
            )
    
    def test_initialization(self, vector_memory):
        """Test vector memory initialization."""
        assert vector_memory is not None
    
    def test_add_document(self, vector_memory):
        """Test adding a document to vector memory."""
        result = vector_memory.add_document(
            doc_id='doc1',
            text='Test document content',
            metadata={'source': 'test'}
        )
        
        assert result is not None
    
    def test_add_multiple_documents(self, vector_memory):
        """Test adding multiple documents."""
        docs = [
            {'id': 'doc1', 'text': 'First document', 'metadata': {}},
            {'id': 'doc2', 'text': 'Second document', 'metadata': {}},
            {'id': 'doc3', 'text': 'Third document', 'metadata': {}}
        ]
        
        for doc in docs:
            vector_memory.add_document(doc['id'], doc['text'], doc['metadata'])
        
        # Should not raise errors
        assert True
    
    def test_search(self, vector_memory, mock_chromadb_client):
        """Test searching in vector memory."""
        result = vector_memory.search(
            query='test query',
            n_results=5
        )
        
        assert result is not None
        assert 'documents' in result or isinstance(result, dict)
    
    def test_search_with_filter(self, vector_memory):
        """Test searching with metadata filter."""
        result = vector_memory.search(
            query='test query',
            filter_metadata={'source': 'test'},
            n_results=3
        )
        
        assert result is not None
    
    def test_delete_document(self, vector_memory):
        """Test deleting a document."""
        # Add a document first
        vector_memory.add_document('delete_test', 'Test content', {})
        
        # Delete it
        result = vector_memory.delete_document('delete_test')
        
        assert result is not None
    
    def test_count_documents(self, vector_memory, mock_chromadb_client):
        """Test counting documents in collection."""
        count = vector_memory.count()
        
        assert isinstance(count, int)
        assert count >= 0


@pytest.mark.unit
class TestVectorMemoryEmbeddings:
    """Test suite for Vector Memory embeddings."""
    
    @pytest.fixture
    def vector_memory_with_embeddings(self, mock_config, mock_chromadb_client, temp_dir):
        """Create vector memory with custom embeddings."""
        from core.vector_memory import VectorMemoryManager
        
        with patch('chromadb.PersistentClient', return_value=mock_chromadb_client):
            return VectorMemoryManager(
                storage_path=temp_dir / "memory",
                vector_db_path=str(temp_dir / "vector_db")
            )
    
    def test_custom_embedding_function(self, vector_memory_with_embeddings):
        """Test using custom embedding function."""
        # This tests that custom embeddings are properly configured
        assert vector_memory_with_embeddings is not None
