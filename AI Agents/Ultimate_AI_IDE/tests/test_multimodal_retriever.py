"""
Tests for Multi-Modal Retriever

Tests for v1.6.0 Advanced RAG features.
"""

import pytest
import os
import tempfile
import numpy as np

from src.modules.context_manager import MultiModalRetriever, MultiModalResult


class TestMultiModalRetriever:
    """Test multi-modal retriever functionality."""
    
    @pytest.fixture
    def retriever(self):
        """Create retriever instance."""
        return MultiModalRetriever()
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_code_file(self, temp_dir):
        """Create sample code file."""
        file_path = os.path.join(temp_dir, "test.py")
        with open(file_path, 'w') as f:
            f.write("""
def process_data(data):
    return [x * 2 for x in data]
""")
        return file_path
    
    @pytest.fixture
    def sample_doc_file(self, temp_dir):
        """Create sample documentation file."""
        file_path = os.path.join(temp_dir, "README.md")
        with open(file_path, 'w') as f:
            f.write("""
# Test Project

This is a test project for data processing.
""")
        return file_path
    
    def test_retriever_initialization(self, retriever):
        """Test retriever initialization."""
        assert retriever.code_embedder is not None
        assert retriever.doc_embedder is not None
        assert retriever.code_weight == 0.6
        assert retriever.doc_weight == 0.4
        assert len(retriever.code_index) == 0
        assert len(retriever.doc_index) == 0
    
    def test_index_code_file_mock(self, retriever, sample_code_file, monkeypatch):
        """Test code file indexing (mocked)."""
        def mock_embed_file(file_path, chunk_size=100):
            return [("chunk1", np.random.rand(768))]
        
        monkeypatch.setattr(retriever.code_embedder, 'embed_file', mock_embed_file)
        
        success = retriever.index_code_file(sample_code_file)
        assert success
        assert sample_code_file in retriever.code_index
        assert sample_code_file in retriever.code_metadata
    
    def test_index_doc_file_mock(self, retriever, sample_doc_file, monkeypatch):
        """Test doc file indexing (mocked)."""
        # Mock the generate_embedding method
        def mock_generate_embedding(text):
            return np.random.rand(384).tolist()
        
        monkeypatch.setattr(retriever.doc_embedder, 'generate_embedding', mock_generate_embedding)
        
        success = retriever.index_doc_file(sample_doc_file)
        assert success
        assert sample_doc_file in retriever.doc_index
        assert sample_doc_file in retriever.doc_metadata
    
    def test_retrieve_code_and_docs_mock(self, retriever, monkeypatch):
        """Test retrieval (mocked)."""
        # Setup mock indices
        retriever.code_index["test.py"] = [
            ("def add(a, b): return a + b", np.array([1.0, 0.0, 0.0]))
        ]
        retriever.code_metadata["test.py"] = {'type': 'code'}
        
        retriever.doc_index["README.md"] = [
            ("This is documentation", np.array([0.0, 1.0, 0.0]))
        ]
        retriever.doc_metadata["README.md"] = {'type': 'doc'}
        
        def mock_embed_code(code):
            return np.array([1.0, 0.0, 0.0])
        
        def mock_generate_embedding(text):
            return [0.0, 1.0, 0.0]
        
        monkeypatch.setattr(retriever.code_embedder, 'embed_code', mock_embed_code)
        monkeypatch.setattr(retriever.doc_embedder, 'generate_embedding', mock_generate_embedding)
        
        results = retriever.retrieve_code_and_docs("test query", top_k=5)
        assert isinstance(results, list)
        assert all(isinstance(r, MultiModalResult) for r in results)
    
    def test_cross_modal_search_modes(self, retriever, monkeypatch):
        """Test different search modes."""
        def mock_retrieve(query, top_k, code_only=False, docs_only=False):
            if code_only:
                return [MultiModalResult("code", "code", "test.py", 0.9, {})]
            elif docs_only:
                return [MultiModalResult("doc", "doc", "README.md", 0.8, {})]
            else:
                return [
                    MultiModalResult("code", "code", "test.py", 0.9, {}),
                    MultiModalResult("doc", "doc", "README.md", 0.8, {})
                ]
        
        monkeypatch.setattr(retriever, 'retrieve_code_and_docs', mock_retrieve)
        
        # Test code only
        results = retriever.cross_modal_search("test", mode='code')
        assert len(results) == 1
        assert results[0].source_type == "code"
        
        # Test docs only
        results = retriever.cross_modal_search("test", mode='docs')
        assert len(results) == 1
        assert results[0].source_type == "doc"
        
        # Test both
        results = retriever.cross_modal_search("test", mode='both')
        assert len(results) == 2
    
    def test_combine_results(self, retriever):
        """Test result combination strategies."""
        code_results = [
            MultiModalResult("code1", "code", "test1.py", 0.9, {}),
            MultiModalResult("code2", "code", "test2.py", 0.8, {})
        ]
        doc_results = [
            MultiModalResult("doc1", "doc", "README.md", 0.85, {}),
            MultiModalResult("doc2", "doc", "GUIDE.md", 0.75, {})
        ]
        
        # Test interleave
        combined = retriever.combine_results(code_results, doc_results, 'interleave')
        assert len(combined) == 4
        assert combined[0].content == "code1"
        assert combined[1].content == "doc1"
        
        # Test code first
        combined = retriever.combine_results(code_results, doc_results, 'code_first')
        assert combined[0].content == "code1"
        assert combined[2].content == "doc1"
        
        # Test doc first
        combined = retriever.combine_results(code_results, doc_results, 'doc_first')
        assert combined[0].content == "doc1"
        assert combined[2].content == "code1"
    
    def test_set_weights(self, retriever):
        """Test weight adjustment."""
        retriever.set_weights(0.7, 0.3)
        assert retriever.code_weight == 0.7
        assert retriever.doc_weight == 0.3
    
    def test_get_statistics(self, retriever):
        """Test statistics retrieval."""
        retriever.code_index["test.py"] = [("chunk1", np.array([1.0])), ("chunk2", np.array([2.0]))]
        retriever.doc_index["README.md"] = [("doc1", np.array([3.0]))]
        
        stats = retriever.get_statistics()
        assert stats['code_files'] == 1
        assert stats['doc_files'] == 1
        assert stats['code_chunks'] == 2
        assert stats['doc_chunks'] == 1
        assert stats['total_chunks'] == 3
    
    def test_clear_index(self, retriever):
        """Test index clearing."""
        retriever.code_index["test.py"] = [("chunk", np.array([1.0]))]
        retriever.doc_index["README.md"] = [("doc", np.array([2.0]))]
        
        # Clear code only
        retriever.clear_index('code')
        assert len(retriever.code_index) == 0
        assert len(retriever.doc_index) == 1
        
        # Clear doc only
        retriever.clear_index('doc')
        assert len(retriever.doc_index) == 0
        
        # Clear both
        retriever.code_index["test.py"] = [("chunk", np.array([1.0]))]
        retriever.doc_index["README.md"] = [("doc", np.array([2.0]))]
        retriever.clear_index()
        assert len(retriever.code_index) == 0
        assert len(retriever.doc_index) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
