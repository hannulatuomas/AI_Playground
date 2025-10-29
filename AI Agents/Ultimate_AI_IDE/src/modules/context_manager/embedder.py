"""
Code Embedder

Generates vector embeddings for code using sentence transformers.
Note: This is a simplified implementation. For production, use sentence-transformers library.
"""

from typing import List, Optional
import hashlib
import json


class CodeEmbedder:
    """Generates embeddings for code."""
    
    def __init__(self, model_name: str = "simple"):
        """
        Initialize embedder.
        
        Args:
            model_name: Name of embedding model (simplified for now)
        """
        self.model_name = model_name
        self.embedding_dim = 384  # Standard dimension
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        # Simplified embedding: Use hash-based approach
        # In production, use sentence-transformers or similar
        return self._simple_embedding(text)
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        return [self.generate_embedding(text) for text in texts]
    
    def _simple_embedding(self, text: str) -> List[float]:
        """
        Simple hash-based embedding (for testing without dependencies).
        
        In production, replace with:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode(text)
        """
        # Normalize text
        text = text.lower().strip()
        
        # Create multiple hashes for different dimensions
        embedding = []
        for i in range(self.embedding_dim):
            # Use hash with different seeds
            hash_input = f"{text}_{i}".encode('utf-8')
            hash_val = int(hashlib.md5(hash_input).hexdigest(), 16)
            # Normalize to [-1, 1]
            normalized = (hash_val % 2000 - 1000) / 1000.0
            embedding.append(normalized)
        
        return embedding
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score between -1 and 1
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")
        
        # Dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Magnitudes
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def save_embedding(self, embedding: List[float], file_path: str):
        """Save embedding to file."""
        with open(file_path, 'w') as f:
            json.dump(embedding, f)
    
    def load_embedding(self, file_path: str) -> List[float]:
        """Load embedding from file."""
        with open(file_path, 'r') as f:
            return json.load(f)


class EmbeddingIndex:
    """Simple in-memory embedding index."""
    
    def __init__(self):
        """Initialize index."""
        self.embeddings: List[List[float]] = []
        self.metadata: List[dict] = []
        self.embedder = CodeEmbedder()
    
    def add(self, text: str, metadata: dict):
        """
        Add text and its embedding to index.
        
        Args:
            text: Text to embed and index
            metadata: Associated metadata
        """
        embedding = self.embedder.generate_embedding(text)
        self.embeddings.append(embedding)
        self.metadata.append(metadata)
    
    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """
        Search for similar items.
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of metadata dicts with similarity scores
        """
        if not self.embeddings:
            return []
        
        query_embedding = self.embedder.generate_embedding(query)
        
        # Calculate similarities
        similarities = []
        for i, emb in enumerate(self.embeddings):
            sim = self.embedder.cosine_similarity(query_embedding, emb)
            similarities.append((sim, i))
        
        # Sort by similarity
        similarities.sort(reverse=True)
        
        # Return top_k results
        results = []
        for sim, idx in similarities[:top_k]:
            result = self.metadata[idx].copy()
            result['similarity'] = sim
            results.append(result)
        
        return results
    
    def clear(self):
        """Clear the index."""
        self.embeddings = []
        self.metadata = []
    
    def size(self) -> int:
        """Get number of items in index."""
        return len(self.embeddings)
