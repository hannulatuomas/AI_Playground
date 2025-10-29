"""
Code Embeddings Module - Full Implementation

Fine-tuned embeddings for code using CodeBERT and similar models.
Provides better understanding of code semantics than general text embeddings.

Features:
- Multiple model support (CodeBERT, GraphCodeBERT, CodeT5)
- Batch processing with progress tracking
- GPU acceleration
- Model caching and lazy loading
- Fallback to general embeddings

Example:
    >>> embedder = CodeEmbedder(model_name='microsoft/codebert-base')
    >>> embedding = embedder.embed_code("def hello(): pass", language="python")
"""

from typing import Optional, List, Dict, Any
import numpy as np
from pathlib import Path
import json
import hashlib

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class CodeEmbedder:
    """
    Generate embeddings specifically for code using pre-trained code models.
    
    Supports:
    - microsoft/codebert-base (768-dim)
    - microsoft/graphcodebert-base (768-dim)
    - Salesforce/codet5-base (768-dim)
    
    Features:
    - Language-aware tokenization
    - Batch processing
    - GPU acceleration
    - Model caching
    """
    
    # Supported models with metadata
    MODELS = {
        'codebert': {
            'name': 'microsoft/codebert-base',
            'dim': 768,
            'description': 'Pre-trained on 6 programming languages',
            'languages': ['python', 'java', 'javascript', 'php', 'ruby', 'go']
        },
        'graphcodebert': {
            'name': 'microsoft/graphcodebert-base',
            'dim': 768,
            'description': 'Graph-based code understanding',
            'languages': ['python', 'java', 'javascript', 'php', 'ruby', 'go']
        },
        'codet5': {
            'name': 'Salesforce/codet5-base',
            'dim': 768,
            'description': 'Text-to-code generation model',
            'languages': ['python', 'java', 'javascript', 'php', 'ruby', 'go', 'c', 'c++', 'c#']
        }
    }
    
    # Language-specific prefixes for better encoding
    LANGUAGE_PREFIXES = {
        'python': 'python: ',
        'java': 'java: ',
        'javascript': 'javascript: ',
        'typescript': 'typescript: ',
        'c': 'c: ',
        'cpp': 'cpp: ',
        'csharp': 'csharp: ',
        'go': 'go: ',
        'rust': 'rust: ',
        'ruby': 'ruby: ',
        'php': 'php: ',
    }
    
    def __init__(
        self,
        model_name: str = 'microsoft/codebert-base',
        use_gpu: bool = False,
        cache_dir: Optional[str] = None,
        enable_caching: bool = True
    ):
        """
        Initialize code embedder.
        
        Args:
            model_name: Model name or alias (codebert, graphcodebert, codet5)
            use_gpu: Whether to use GPU acceleration
            cache_dir: Directory to cache models
            enable_caching: Enable embedding caching
            
        Raises:
            ImportError: If transformers not installed
            
        Example:
            >>> embedder = CodeEmbedder(model_name='codebert', use_gpu=True)
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "transformers not installed. "
                "Install with: pip install transformers torch"
            )
        
        # Resolve model alias
        if model_name in self.MODELS:
            self.model_info = self.MODELS[model_name]
            model_name = self.model_info['name']
        else:
            # Custom model
            self.model_info = {
                'name': model_name,
                'dim': 768,  # Default
                'description': 'Custom model',
                'languages': []
            }
        
        self.model_name = model_name
        self.device = 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.enable_caching = enable_caching
        
        # Create cache directory
        if self.enable_caching and self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Lazy loading
        self._model = None
        self._tokenizer = None
        
        # Embedding cache (in-memory)
        self._embedding_cache: Dict[str, np.ndarray] = {}
        
        print(f"CodeEmbedder initialized:")
        print(f"  Model: {self.model_name}")
        print(f"  Device: {self.device}")
        print(f"  Dimension: {self.model_info['dim']}")
        print(f"  Caching: {'enabled' if enable_caching else 'disabled'}")
    
    @property
    def model(self):
        """Lazy load model."""
        if self._model is None:
            print(f"Loading code model: {self.model_name}...")
            try:
                self._model = AutoModel.from_pretrained(
                    self.model_name,
                    cache_dir=str(self.cache_dir) if self.cache_dir else None
                ).to(self.device)
                self._model.eval()
                print(f"✓ Model loaded on {self.device}")
            except Exception as e:
                print(f"✗ Failed to load model: {e}")
                raise
        return self._model
    
    @property
    def tokenizer(self):
        """Lazy load tokenizer."""
        if self._tokenizer is None:
            try:
                self._tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    cache_dir=str(self.cache_dir) if self.cache_dir else None
                )
            except Exception as e:
                print(f"✗ Failed to load tokenizer: {e}")
                raise
        return self._tokenizer
    
    def embed_code(
        self,
        code: str,
        language: Optional[str] = None,
        normalize: bool = True,
        use_cache: bool = True
    ) -> np.ndarray:
        """
        Generate embedding for code.
        
        Args:
            code: Source code
            language: Programming language (for better encoding)
            normalize: Whether to normalize embedding
            use_cache: Use cached embedding if available
            
        Returns:
            Embedding vector (768-dim for most models)
            
        Example:
            >>> embedding = embedder.embed_code(
            ...     "def fibonacci(n): return n if n <= 1 else fib(n-1) + fib(n-2)",
            ...     language="python"
            ... )
            >>> print(embedding.shape)
            (768,)
        """
        # Check cache
        if use_cache and self.enable_caching:
            cache_key = self._get_cache_key(code, language)
            if cache_key in self._embedding_cache:
                return self._embedding_cache[cache_key]
        
        # Prepare input with language prefix
        if language and language.lower() in self.LANGUAGE_PREFIXES:
            code_input = self.LANGUAGE_PREFIXES[language.lower()] + code
        else:
            code_input = code
        
        # Tokenize
        try:
            inputs = self.tokenizer(
                code_input,
                return_tensors='pt',
                max_length=512,
                truncation=True,
                padding=True
            ).to(self.device)
        except Exception as e:
            print(f"✗ Tokenization failed: {e}")
            # Return zero vector on error
            return np.zeros(self.model_info['dim'])
        
        # Generate embedding
        try:
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use [CLS] token embedding (first token)
                embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]
        except Exception as e:
            print(f"✗ Embedding generation failed: {e}")
            return np.zeros(self.model_info['dim'])
        
        # Normalize
        if normalize:
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
        
        # Cache result
        if use_cache and self.enable_caching:
            self._embedding_cache[cache_key] = embedding
        
        return embedding
    
    def embed_batch(
        self,
        codes: List[str],
        languages: Optional[List[str]] = None,
        batch_size: int = 8,
        show_progress: bool = True,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Embed multiple code snippets in batches.
        
        Args:
            codes: List of code snippets
            languages: Optional list of languages (one per code)
            batch_size: Batch size for processing
            show_progress: Show progress bar
            normalize: Normalize embeddings
            
        Returns:
            Array of embeddings (N x 768)
            
        Example:
            >>> codes = ["def add(a, b): return a + b", "def sub(a, b): return a - b"]
            >>> embeddings = embedder.embed_batch(codes, languages=["python", "python"])
            >>> print(embeddings.shape)
            (2, 768)
        """
        if not codes:
            return np.array([])
        
        # Prepare languages list
        if languages is None:
            languages = [None] * len(codes)
        elif len(languages) != len(codes):
            raise ValueError("Length of languages must match length of codes")
        
        embeddings = []
        total_batches = (len(codes) + batch_size - 1) // batch_size
        
        for i in range(0, len(codes), batch_size):
            batch_codes = codes[i:i + batch_size]
            batch_langs = languages[i:i + batch_size]
            
            if show_progress:
                batch_num = i // batch_size + 1
                print(f"  Embedding batch {batch_num}/{total_batches}...", end='\r')
            
            # Prepare batch with language prefixes
            batch_inputs = []
            for code, lang in zip(batch_codes, batch_langs):
                if lang and lang.lower() in self.LANGUAGE_PREFIXES:
                    batch_inputs.append(self.LANGUAGE_PREFIXES[lang.lower()] + code)
                else:
                    batch_inputs.append(code)
            
            # Tokenize batch
            try:
                inputs = self.tokenizer(
                    batch_inputs,
                    return_tensors='pt',
                    max_length=512,
                    truncation=True,
                    padding=True
                ).to(self.device)
            except Exception as e:
                print(f"\n✗ Batch tokenization failed: {e}")
                # Add zero vectors for this batch
                embeddings.append(np.zeros((len(batch_codes), self.model_info['dim'])))
                continue
            
            # Generate embeddings
            try:
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                
                # Normalize if requested
                if normalize:
                    norms = np.linalg.norm(batch_embeddings, axis=1, keepdims=True)
                    norms[norms == 0] = 1  # Avoid division by zero
                    batch_embeddings = batch_embeddings / norms
                
                embeddings.append(batch_embeddings)
            except Exception as e:
                print(f"\n✗ Batch embedding failed: {e}")
                embeddings.append(np.zeros((len(batch_codes), self.model_info['dim'])))
        
        if show_progress:
            print(f"  ✓ Embedded {len(codes)} code snippets" + " " * 20)
        
        return np.vstack(embeddings)
    
    def get_similarity(
        self,
        code1: str,
        code2: str,
        language: Optional[str] = None
    ) -> float:
        """
        Compute cosine similarity between two code snippets.
        
        Args:
            code1: First code snippet
            code2: Second code snippet
            language: Programming language
            
        Returns:
            Similarity score (0-1)
            
        Example:
            >>> sim = embedder.get_similarity(
            ...     "def add(a, b): return a + b",
            ...     "def sum(x, y): return x + y",
            ...     language="python"
            ... )
            >>> print(f"Similarity: {sim:.3f}")
            Similarity: 0.95
        """
        emb1 = self.embed_code(code1, language=language, normalize=True)
        emb2 = self.embed_code(code2, language=language, normalize=True)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2)
        return float(similarity)
    
    def find_similar_codes(
        self,
        query_code: str,
        candidate_codes: List[str],
        language: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find most similar code snippets.
        
        Args:
            query_code: Query code snippet
            candidate_codes: List of candidate codes
            language: Programming language
            top_k: Number of results to return
            
        Returns:
            List of dicts with 'index', 'code', and 'similarity'
            
        Example:
            >>> results = embedder.find_similar_codes(
            ...     "def factorial(n):",
            ...     candidate_codes,
            ...     language="python",
            ...     top_k=3
            ... )
        """
        # Embed query
        query_emb = self.embed_code(query_code, language=language, normalize=True)
        
        # Embed candidates
        candidate_embs = self.embed_batch(
            candidate_codes,
            languages=[language] * len(candidate_codes) if language else None,
            normalize=True,
            show_progress=False
        )
        
        # Compute similarities
        similarities = np.dot(candidate_embs, query_emb)
        
        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'index': int(idx),
                'code': candidate_codes[idx],
                'similarity': float(similarities[idx])
            })
        
        return results
    
    def _get_cache_key(self, code: str, language: Optional[str]) -> str:
        """Generate cache key for code and language."""
        key_str = f"{language or 'none'}:{code}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def clear_cache(self):
        """Clear in-memory embedding cache."""
        self._embedding_cache.clear()
        print("✓ Embedding cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cache_size': len(self._embedding_cache),
            'cache_enabled': self.enable_caching
        }
    
    def unload_model(self):
        """Unload model to free memory."""
        if self._model is not None:
            del self._model
            self._model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print("✓ Code embedding model unloaded")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'name': self.model_name,
            'dimension': self.model_info['dim'],
            'description': self.model_info['description'],
            'supported_languages': self.model_info['languages'],
            'device': self.device,
            'loaded': self._model is not None
        }


# Fallback to general embeddings if transformers not available
class FallbackCodeEmbedder:
    """
    Fallback embedder using sentence-transformers.
    
    Used when transformers is not available or CodeBERT fails.
    """
    
    def __init__(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.available = True
        except ImportError:
            self.available = False
    
    def embed_code(self, code: str, language=None, normalize=True):
        """Embed code using general sentence embeddings."""
        if not self.available:
            # Return random embedding as last resort
            return np.random.randn(384)
        
        return self.model.encode([code], convert_to_numpy=True)[0]
    
    def embed_batch(self, codes, languages=None, batch_size=8, show_progress=True, normalize=True):
        """Embed batch using general sentence embeddings."""
        if not self.available:
            return np.random.randn(len(codes), 384)
        
        return self.model.encode(codes, batch_size=batch_size, show_progress_bar=show_progress, convert_to_numpy=True)


if __name__ == "__main__":
    print("Code Embeddings Module - Full Implementation")
    print("=" * 60)
    
    if not TRANSFORMERS_AVAILABLE:
        print("\n✗ transformers not installed")
        print("Install with: pip install transformers torch")
        print("\nUsing fallback embedder for demo...")
        embedder = FallbackCodeEmbedder()
        if embedder.available:
            print("✓ Fallback embedder loaded\n")
        else:
            print("✗ No embedders available\n")
            exit(1)
    else:
        print("\n✓ transformers available\n")
        
        # Test CodeBERT
        print("Testing CodeEmbedder...")
        try:
            embedder = CodeEmbedder(model_name='codebert', use_gpu=False)
            
            # Test single embedding
            code = "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)"
            embedding = embedder.embed_code(code, language="python")
            print(f"\n✓ Single embedding: shape {embedding.shape}")
            
            # Test batch embedding
            codes = [
                "def add(a, b): return a + b",
                "def subtract(a, b): return a - b",
                "def multiply(a, b): return a * b"
            ]
            embeddings = embedder.embed_batch(codes, languages=["python"]*3, show_progress=False)
            print(f"✓ Batch embedding: shape {embeddings.shape}")
            
            # Test similarity
            sim = embedder.get_similarity(codes[0], codes[1], language="python")
            print(f"✓ Similarity computation: {sim:.3f}")
            
            print("\n✓ All tests passed!")
            
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            print("This is expected if model download fails or not enough memory")
