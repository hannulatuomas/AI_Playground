
"""
Comprehensive unit tests for Embeddings Tool.

Tests for embedding generation, batch processing, similarity calculations,
and error handling.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from typing import List


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_ollama_client():
    """Create a mock Ollama client."""
    client = Mock()
    client.embeddings = Mock(return_value={
        'embedding': [0.1, 0.2, 0.3, 0.4, 0.5] * 153  # 768 dimensions (768/5)
    })
    client.list = Mock(return_value={
        'models': [
            {'name': 'nomic-embed-text:latest'},
            {'name': 'llama3.2:3b'}
        ]
    })
    return client


@pytest.fixture
def embedding_generator(mock_ollama_client):
    """Create an embedding generator with mocked client."""
    from tools.embeddings import EmbeddingGenerator
    
    with patch('ollama.Client', return_value=mock_ollama_client):
        generator = EmbeddingGenerator(
            model="nomic-embed-text:latest",
            host="http://localhost:11434"
        )
        generator.client = mock_ollama_client
        return generator


# =============================================================================
# EmbeddingGenerator Initialization Tests
# =============================================================================

class TestEmbeddingGeneratorInitialization:
    """Tests for EmbeddingGenerator initialization."""
    
    def test_default_initialization(self, mock_ollama_client):
        """Test initialization with default parameters."""
        from tools.embeddings import EmbeddingGenerator
        
        with patch('ollama.Client', return_value=mock_ollama_client):
            generator = EmbeddingGenerator()
        
        assert generator.model == "nomic-embed-text:latest"
        assert generator.host == "http://localhost:11434"
        assert generator.timeout == 120
    
    def test_custom_initialization(self, mock_ollama_client):
        """Test initialization with custom parameters."""
        from tools.embeddings import EmbeddingGenerator
        
        with patch('ollama.Client', return_value=mock_ollama_client):
            generator = EmbeddingGenerator(
                model="custom-model:latest",
                host="http://custom-host:8080",
                timeout=60
            )
        
        assert generator.model == "custom-model:latest"
        assert generator.host == "http://custom-host:8080"
        assert generator.timeout == 60
    
    def test_model_verification(self, mock_ollama_client):
        """Test model availability verification."""
        from tools.embeddings import EmbeddingGenerator
        
        with patch('ollama.Client', return_value=mock_ollama_client):
            generator = EmbeddingGenerator()
            # Should not raise exception
            assert generator.client is not None


# =============================================================================
# Single Embedding Generation Tests
# =============================================================================

class TestSingleEmbeddingGeneration:
    """Tests for generating single embeddings."""
    
    def test_generate_single_embedding(self, embedding_generator):
        """Test generating embedding for single text."""
        text = "This is a test sentence."
        
        embedding = embedding_generator.generate(text)
        
        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
    
    def test_generate_with_normalization(self, embedding_generator):
        """Test generating normalized embedding."""
        text = "Test text for normalization"
        
        embedding = embedding_generator.generate(text, normalize=True)
        
        assert embedding is not None
        # Check if normalized (L2 norm should be close to 1)
        norm = sum(x * x for x in embedding) ** 0.5
        assert abs(norm - 1.0) < 0.01
    
    def test_generate_without_normalization(self, embedding_generator):
        """Test generating unnormalized embedding."""
        text = "Test text without normalization"
        
        embedding = embedding_generator.generate(text, normalize=False)
        
        assert embedding is not None
        assert isinstance(embedding, list)
    
    def test_generate_empty_text(self, embedding_generator):
        """Test generating embedding for empty text."""
        embedding = embedding_generator.generate("")
        
        # Should still generate embedding
        assert embedding is not None
        assert isinstance(embedding, list)
    
    def test_generate_long_text(self, embedding_generator):
        """Test generating embedding for long text."""
        long_text = "This is a very long sentence. " * 100
        
        embedding = embedding_generator.generate(long_text)
        
        assert embedding is not None
        assert isinstance(embedding, list)


# =============================================================================
# Batch Embedding Generation Tests
# =============================================================================

class TestBatchEmbeddingGeneration:
    """Tests for batch embedding generation."""
    
    def test_generate_batch_embeddings(self, embedding_generator):
        """Test generating embeddings for multiple texts."""
        texts = [
            "First sentence",
            "Second sentence",
            "Third sentence"
        ]
        
        embeddings = embedding_generator.generate(texts)
        
        assert embeddings is not None
        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)
        assert all(isinstance(emb, list) for emb in embeddings)
    
    def test_generate_batch_with_batch_size(self, embedding_generator):
        """Test batch generation with custom batch size."""
        texts = ["Text {}".format(i) for i in range(10)]
        
        embeddings = embedding_generator.generate_batch(
            texts,
            batch_size=3
        )
        
        assert embeddings is not None
        assert len(embeddings) == len(texts)
    
    def test_generate_batch_empty_list(self, embedding_generator):
        """Test generating embeddings for empty list."""
        embeddings = embedding_generator.generate_batch([])
        
        assert embeddings == []
    
    def test_generate_batch_single_item(self, embedding_generator):
        """Test batch generation with single item."""
        texts = ["Single text"]
        
        embeddings = embedding_generator.generate_batch(texts)
        
        assert len(embeddings) == 1
        assert isinstance(embeddings[0], list)
    
    def test_generate_batch_large_dataset(self, embedding_generator):
        """Test batch generation with large dataset."""
        texts = ["Document {}".format(i) for i in range(100)]
        
        embeddings = embedding_generator.generate_batch(
            texts,
            batch_size=10
        )
        
        assert len(embeddings) == 100


# =============================================================================
# Normalization Tests
# =============================================================================

class TestNormalization:
    """Tests for embedding normalization."""
    
    def test_normalize_vector(self, embedding_generator):
        """Test normalizing a vector."""
        vector = [3.0, 4.0]  # Should normalize to [0.6, 0.8]
        
        normalized = embedding_generator._normalize(vector)
        
        assert abs(normalized[0] - 0.6) < 0.01
        assert abs(normalized[1] - 0.8) < 0.01
    
    def test_normalize_zero_vector(self, embedding_generator):
        """Test normalizing zero vector."""
        vector = [0.0, 0.0, 0.0]
        
        normalized = embedding_generator._normalize(vector)
        
        # Should return original vector
        assert normalized == vector
    
    def test_normalized_embedding_magnitude(self, embedding_generator):
        """Test that normalized embeddings have unit magnitude."""
        text = "Test normalization"
        
        embedding = embedding_generator.generate(text, normalize=True)
        
        # Calculate magnitude
        magnitude = sum(x * x for x in embedding) ** 0.5
        
        assert abs(magnitude - 1.0) < 0.01


# =============================================================================
# Dimension Tests
# =============================================================================

class TestEmbeddingDimensions:
    """Tests for embedding dimensions."""
    
    def test_get_dimension(self, embedding_generator):
        """Test getting embedding dimension."""
        dimension = embedding_generator.get_dimension()
        
        assert dimension > 0
        assert isinstance(dimension, int)
    
    def test_consistent_dimensions(self, embedding_generator):
        """Test that all embeddings have consistent dimensions."""
        texts = ["Text 1", "Text 2", "Text 3"]
        
        embeddings = embedding_generator.generate(texts)
        
        dimensions = [len(emb) for emb in embeddings]
        assert len(set(dimensions)) == 1  # All same dimension


# =============================================================================
# Similarity Calculation Tests
# =============================================================================

class TestSimilarityCalculations:
    """Tests for similarity calculations."""
    
    def test_cosine_similarity_identical(self, embedding_generator):
        """Test cosine similarity between identical vectors."""
        embedding = [1.0, 2.0, 3.0]
        
        similarity = embedding_generator.similarity(
            embedding,
            embedding,
            metric="cosine"
        )
        
        assert abs(similarity - 1.0) < 0.01
    
    def test_cosine_similarity_orthogonal(self, embedding_generator):
        """Test cosine similarity between orthogonal vectors."""
        emb1 = [1.0, 0.0, 0.0]
        emb2 = [0.0, 1.0, 0.0]
        
        similarity = embedding_generator.similarity(
            emb1,
            emb2,
            metric="cosine"
        )
        
        assert abs(similarity) < 0.01  # Should be ~0
    
    def test_euclidean_similarity(self, embedding_generator):
        """Test Euclidean distance similarity."""
        emb1 = [1.0, 2.0, 3.0]
        emb2 = [1.0, 2.0, 3.0]
        
        similarity = embedding_generator.similarity(
            emb1,
            emb2,
            metric="euclidean"
        )
        
        # Identical vectors should have high similarity
        assert similarity > 0.9
    
    def test_similarity_different_dimensions_error(self, embedding_generator):
        """Test error when comparing different dimensional embeddings."""
        emb1 = [1.0, 2.0]
        emb2 = [1.0, 2.0, 3.0]
        
        with pytest.raises(ValueError):
            embedding_generator.similarity(emb1, emb2)
    
    def test_similarity_unsupported_metric(self, embedding_generator):
        """Test error with unsupported similarity metric."""
        emb1 = [1.0, 2.0]
        emb2 = [1.0, 2.0]
        
        with pytest.raises(ValueError):
            embedding_generator.similarity(
                emb1,
                emb2,
                metric="unsupported_metric"
            )
    
    def test_semantic_similarity(self, embedding_generator):
        """Test semantic similarity between related texts."""
        text1 = "The cat sat on the mat"
        text2 = "A feline rested on the rug"
        
        emb1 = embedding_generator.generate(text1)
        emb2 = embedding_generator.generate(text2)
        
        similarity = embedding_generator.similarity(emb1, emb2)
        
        # Related texts should have some similarity
        assert similarity > 0.0


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling."""
    
    def test_generate_connection_error(self, embedding_generator):
        """Test handling connection errors."""
        embedding_generator.client.embeddings = Mock(
            side_effect=ConnectionError("Cannot connect to Ollama")
        )
        
        with pytest.raises(RuntimeError):
            embedding_generator.generate("Test text")
    
    def test_generate_no_embedding_returned(self, embedding_generator):
        """Test handling when no embedding is returned."""
        embedding_generator.client.embeddings = Mock(
            return_value={'embedding': []}
        )
        
        with pytest.raises(RuntimeError):
            embedding_generator.generate("Test text")
    
    def test_model_verification_failure(self, mock_ollama_client):
        """Test handling model verification failure."""
        from tools.embeddings import EmbeddingGenerator
        
        mock_ollama_client.list = Mock(side_effect=Exception("Connection failed"))
        
        with patch('ollama.Client', return_value=mock_ollama_client):
            # Should log warning but not raise exception
            generator = EmbeddingGenerator()
            assert generator is not None


# =============================================================================
# Factory Function Tests
# =============================================================================

class TestFactoryFunction:
    """Tests for factory function."""
    
    def test_create_embedding_generator_default(self, mock_ollama_client):
        """Test creating generator with default config."""
        from tools.embeddings import create_embedding_generator
        
        with patch('ollama.Client', return_value=mock_ollama_client):
            generator = create_embedding_generator()
        
        assert generator is not None
        assert generator.model == "nomic-embed-text:latest"
    
    def test_create_embedding_generator_custom_config(self, mock_ollama_client):
        """Test creating generator with custom config."""
        from tools.embeddings import create_embedding_generator
        
        config = {
            'model': 'custom-model:v1',
            'host': 'http://custom:8080',
            'timeout': 90
        }
        
        with patch('ollama.Client', return_value=mock_ollama_client):
            generator = create_embedding_generator(config)
        
        assert generator.model == 'custom-model:v1'
        assert generator.host == 'http://custom:8080'
        assert generator.timeout == 90
    
    def test_create_embedding_generator_none_config(self, mock_ollama_client):
        """Test creating generator with None config."""
        from tools.embeddings import create_embedding_generator
        
        with patch('ollama.Client', return_value=mock_ollama_client):
            generator = create_embedding_generator(None)
        
        assert generator is not None


# =============================================================================
# Integration Tests
# =============================================================================

class TestEmbeddingIntegration:
    """Integration tests for embeddings."""
    
    def test_end_to_end_workflow(self, embedding_generator):
        """Test complete embedding workflow."""
        # Generate embeddings for documents
        documents = [
            "Python is a programming language",
            "Java is used for enterprise applications",
            "JavaScript runs in web browsers"
        ]
        
        embeddings = embedding_generator.generate(documents)
        
        # Calculate similarities
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = embedding_generator.similarity(
                    embeddings[i],
                    embeddings[j]
                )
                similarities.append(sim)
        
        assert len(similarities) == 3  # 3 pairs
        assert all(isinstance(s, float) for s in similarities)

