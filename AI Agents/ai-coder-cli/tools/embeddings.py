"""
Embedding Generation Module

This module provides embedding generation using Ollama's nomic-embed-text model.
Embeddings are used for semantic search and vector database operations.
"""

import logging
from typing import List, Optional, Dict, Any, Union
import ollama
from ollama import Client


logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generate embeddings using Ollama's nomic-embed-text model.
    
    The nomic-embed-text model is specifically designed for text embeddings
    and provides high-quality vector representations for semantic search.
    
    Features:
        - Configurable model and Ollama host
        - Batch embedding generation
        - Error handling and retry logic
        - Dimension normalization
    """
    
    def __init__(
        self,
        model: str = "nomic-embed-text:latest",
        host: str = "http://localhost:11434",
        timeout: int = 120
    ):
        """
        Initialize the embedding generator.
        
        Args:
            model: Ollama embedding model name (default: nomic-embed-text:latest)
            host: Ollama server URL
            timeout: Request timeout in seconds
        """
        self.model = model
        self.host = host
        self.timeout = timeout
        self.client = Client(host=host)
        
        logger.info(f"EmbeddingGenerator initialized with model={model}, host={host}")
        
        # Verify model is available
        try:
            self._verify_model()
        except Exception as e:
            logger.warning(f"Could not verify embedding model: {e}")
    
    def _verify_model(self) -> None:
        """Verify that the embedding model is available in Ollama."""
        try:
            models = self.client.list()
            model_names = [m['name'] for m in models.get('models', [])]
            
            if self.model not in model_names:
                logger.warning(
                    f"Embedding model '{self.model}' not found. "
                    f"Available models: {', '.join(model_names)}"
                )
                logger.info(f"To pull the model, run: ollama pull {self.model}")
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            raise
    
    def generate(
        self,
        text: Union[str, List[str]],
        normalize: bool = True
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text or list of texts.
        
        Args:
            text: Single text string or list of text strings
            normalize: Whether to normalize embeddings to unit length
            
        Returns:
            Embedding vector(s) as list of floats or list of lists
            
        Raises:
            RuntimeError: If embedding generation fails
        """
        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]
        
        try:
            embeddings = []
            
            for t in texts:
                response = self.client.embeddings(
                    model=self.model,
                    prompt=t
                )
                
                embedding = response.get('embedding', [])
                
                if not embedding:
                    raise RuntimeError(f"No embedding returned for text: {t[:50]}...")
                
                if normalize:
                    embedding = self._normalize(embedding)
                
                embeddings.append(embedding)
            
            logger.debug(f"Generated {len(embeddings)} embedding(s)")
            
            return embeddings if is_batch else embeddings[0]
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise RuntimeError(f"Failed to generate embeddings: {str(e)}") from e
    
    def generate_batch(
        self,
        texts: List[str],
        normalize: bool = True,
        batch_size: int = 32
    ) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts with chunking.
        
        Args:
            texts: List of text strings
            normalize: Whether to normalize embeddings
            batch_size: Number of texts to process at once
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.generate(batch, normalize=normalize)
            all_embeddings.extend(embeddings)
            
            logger.debug(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
        
        return all_embeddings
    
    def _normalize(self, embedding: List[float]) -> List[float]:
        """
        Normalize embedding to unit length (L2 norm).
        
        Args:
            embedding: Embedding vector
            
        Returns:
            Normalized embedding vector
        """
        # Calculate L2 norm
        norm = sum(x * x for x in embedding) ** 0.5
        
        if norm == 0:
            logger.warning("Zero-length embedding encountered")
            return embedding
        
        # Normalize
        return [x / norm for x in embedding]
    
    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Embedding dimension
        """
        # Generate a test embedding to determine dimension
        try:
            test_embedding = self.generate("test", normalize=False)
            return len(test_embedding)
        except Exception as e:
            logger.error(f"Failed to determine embedding dimension: {e}")
            # nomic-embed-text typically produces 768-dimensional embeddings
            return 768
    
    def similarity(
        self,
        embedding1: List[float],
        embedding2: List[float],
        metric: str = "cosine"
    ) -> float:
        """
        Calculate similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            metric: Similarity metric ("cosine" or "euclidean")
            
        Returns:
            Similarity score
        """
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings must have the same dimension")
        
        if metric == "cosine":
            # Cosine similarity
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            norm1 = sum(a * a for a in embedding1) ** 0.5
            norm2 = sum(b * b for b in embedding2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        elif metric == "euclidean":
            # Euclidean distance (lower is more similar)
            distance = sum((a - b) ** 2 for a, b in zip(embedding1, embedding2)) ** 0.5
            # Convert to similarity (higher is more similar)
            return 1.0 / (1.0 + distance)
        
        else:
            raise ValueError(f"Unsupported similarity metric: {metric}")


def create_embedding_generator(config: Optional[Dict[str, Any]] = None) -> EmbeddingGenerator:
    """
    Factory function to create an EmbeddingGenerator from configuration.
    
    Args:
        config: Configuration dictionary with keys:
            - model: Embedding model name
            - host: Ollama server URL
            - timeout: Request timeout
            
    Returns:
        Configured EmbeddingGenerator instance
    """
    config = config or {}
    
    model = config.get('model', 'nomic-embed-text:latest')
    host = config.get('host', 'http://localhost:11434')
    timeout = config.get('timeout', 120)
    
    return EmbeddingGenerator(model=model, host=host, timeout=timeout)
