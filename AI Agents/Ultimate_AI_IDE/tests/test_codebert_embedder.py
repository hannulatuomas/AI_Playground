"""
Tests for CodeBERT Embedder

Tests for v1.6.0 Advanced RAG features.
"""

import pytest
import os
import tempfile
from pathlib import Path
import numpy as np

from src.modules.context_manager import CodeBERTEmbedder, CodeBERTIndex


class TestCodeBERTEmbedder:
    """Test CodeBERT embedder functionality."""
    
    @pytest.fixture
    def embedder(self):
        """Create embedder instance."""
        return CodeBERTEmbedder()
    
    @pytest.fixture
    def sample_code(self):
        """Sample Python code."""
        return """
def hello_world():
    print("Hello, World!")
    return True

class MyClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
"""
    
    def test_embedder_initialization(self, embedder):
        """Test embedder initialization."""
        assert embedder.model_name == "microsoft/codebert-base"
        assert embedder.model is None  # Lazy loading
        assert embedder.device == "cpu"
        assert len(embedder.language_configs) > 0
    
    def test_get_model_info(self, embedder):
        """Test getting model info."""
        info = embedder.get_model_info()
        assert 'model_name' in info
        assert 'cache_dir' in info
        assert 'device' in info
        assert 'loaded' in info
        assert 'supported_languages' in info
        assert info['loaded'] == False  # Not loaded yet
    
    def test_embed_code_mock(self, embedder, sample_code, monkeypatch):
        """Test code embedding (mocked)."""
        # Mock the model loading and embedding
        def mock_lazy_load():
            embedder.model = "mock_model"
            embedder.tokenizer = "mock_tokenizer"
        
        def mock_embed(*args, **kwargs):
            return np.random.rand(768)  # CodeBERT embedding size
        
        monkeypatch.setattr(embedder, '_lazy_load_model', mock_lazy_load)
        monkeypatch.setattr(embedder, 'embed_code', mock_embed)
        
        embedding = embedder.embed_code(sample_code)
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 768
    
    def test_compare_embeddings_mock(self, embedder, monkeypatch):
        """Test embedding comparison (mocked)."""
        def mock_embed(code, language="python"):
            # Return different embeddings for different code
            if "hello" in code.lower():
                return np.array([1.0, 0.0, 0.0])
            else:
                return np.array([0.0, 1.0, 0.0])
        
        monkeypatch.setattr(embedder, 'embed_code', mock_embed)
        
        code1 = "def hello(): pass"
        code2 = "def hello(): return True"
        code3 = "def goodbye(): pass"
        
        # Similar code should have high similarity
        sim1 = embedder.compare_embeddings(code1, code2)
        assert sim1 > 0.9
        
        # Different code should have lower similarity
        sim2 = embedder.compare_embeddings(code1, code3)
        assert sim2 < 0.5


class TestCodeBERTIndex:
    """Test CodeBERT index functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_file(self, temp_dir):
        """Create sample Python file."""
        file_path = os.path.join(temp_dir, "test.py")
        with open(file_path, 'w') as f:
            f.write("""
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
""")
        return file_path
    
    @pytest.fixture
    def index(self, temp_dir):
        """Create index instance."""
        index_dir = os.path.join(temp_dir, "index")
        return CodeBERTIndex(index_dir)
    
    def test_index_initialization(self, index):
        """Test index initialization."""
        assert index.index_dir is not None
        assert isinstance(index.embedder, CodeBERTEmbedder)
        assert len(index.index) == 0
        assert len(index.metadata) == 0
    
    def test_index_file_mock(self, index, sample_file, monkeypatch):
        """Test file indexing (mocked)."""
        def mock_embed_file(file_path, chunk_size=100):
            return [
                ("chunk1", np.random.rand(768)),
                ("chunk2", np.random.rand(768))
            ]
        
        monkeypatch.setattr(index.embedder, 'embed_file', mock_embed_file)
        
        success = index.index_file(sample_file)
        assert success
        assert sample_file in index.index
        assert len(index.index[sample_file]) == 2
        assert sample_file in index.metadata
    
    def test_search_mock(self, index, sample_file, monkeypatch):
        """Test search (mocked)."""
        # Setup mock index
        index.index[sample_file] = [
            ("def add(a, b): return a + b", np.array([1.0, 0.0, 0.0])),
            ("def multiply(a, b): return a * b", np.array([0.0, 1.0, 0.0]))
        ]
        
        def mock_embed_code(code, language="python"):
            return np.array([1.0, 0.0, 0.0])  # Similar to first chunk
        
        monkeypatch.setattr(index.embedder, 'embed_code', mock_embed_code)
        
        results = index.search("addition function", top_k=2)
        assert len(results) > 0
        assert results[0][0] == sample_file
        assert "add" in results[0][1]
    
    def test_save_load(self, index, temp_dir):
        """Test saving and loading index."""
        # Add some data
        index.index["test.py"] = [
            ("chunk1", np.array([1.0, 2.0, 3.0])),
            ("chunk2", np.array([4.0, 5.0, 6.0]))
        ]
        index.metadata["test.py"] = {'chunks': 2}
        
        # Save
        success = index.save()
        assert success
        
        # Load in new index
        new_index = CodeBERTIndex(index.index_dir)
        success = new_index.load()
        assert success
        assert "test.py" in new_index.index
        assert len(new_index.index["test.py"]) == 2
        assert "test.py" in new_index.metadata


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
