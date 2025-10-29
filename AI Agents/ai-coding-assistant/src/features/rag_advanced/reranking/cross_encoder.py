"""
Cross-Encoder Reranking Module - Full Implementation

Provides precise reranking of search results using cross-encoder models.
Cross-encoders process query+document pairs for more accurate relevance scoring.

Features:
- Multiple cross-encoder model support
- Batch reranking for efficiency
- Score normalization and calibration
- Fallback to bi-encoder scores
- Caching for repeated queries

Example:
    >>> reranker = CrossEncoderReranker()
    >>> reranked = reranker.rerank(query, results, top_k=5)
"""

from typing import List, Dict, Optional, Any, Tuple
import numpy as np
from pathlib import Path
import time

try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False


class CrossEncoderReranker:
    """
    Cross-encoder based reranking for improved precision.
    
    Cross-encoders provide more accurate relevance scoring than bi-encoders
    by processing query-document pairs jointly, but are slower.
    
    Features:
    - Multiple model support
    - Batch processing
    - Score calibration
    - Performance monitoring
    """
    
    # Supported cross-encoder models
    MODELS = {
        'ms-marco-mini': {
            'name': 'cross-encoder/ms-marco-MiniLM-L-6-v2',
            'description': 'Fast, good for general text',
            'size': '80MB',
            'speed': 'fast'
        },
        'ms-marco-base': {
            'name': 'cross-encoder/ms-marco-MiniLM-L-12-v2',
            'description': 'Better quality, slower',
            'size': '120MB',
            'speed': 'medium'
        },
        'qnli': {
            'name': 'cross-encoder/qnli-distilroberta-base',
            'description': 'Question-answer focused',
            'size': '250MB',
            'speed': 'medium'
        }
    }
    
    def __init__(
        self,
        model_name: str = 'ms-marco-mini',
        batch_size: int = 32,
        use_cache: bool = True,
        score_threshold: Optional[float] = None
    ):
        """
        Initialize cross-encoder reranker.
        
        Args:
            model_name: Model name or alias
            batch_size: Batch size for reranking
            use_cache: Enable result caching
            score_threshold: Minimum score for results
            
        Raises:
            ImportError: If sentence-transformers not installed
            
        Example:
            >>> reranker = CrossEncoderReranker('ms-marco-mini')
        """
        if not CROSS_ENCODER_AVAILABLE:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
        
        # Resolve model alias
        if model_name in self.MODELS:
            self.model_info = self.MODELS[model_name]
            model_name = self.model_info['name']
        else:
            self.model_info = {
                'name': model_name,
                'description': 'Custom model',
                'size': 'unknown',
                'speed': 'unknown'
            }
        
        self.model_name = model_name
        self.batch_size = batch_size
        self.use_cache = use_cache
        self.score_threshold = score_threshold
        
        # Lazy loading
        self._model = None
        
        # Cache for repeated queries
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        
        # Performance monitoring
        self.stats = {
            'total_reranks': 0,
            'total_pairs': 0,
            'total_time': 0.0,
            'cache_hits': 0
        }
        
        print(f"CrossEncoderReranker initialized:")
        print(f"  Model: {self.model_name}")
        print(f"  Batch size: {batch_size}")
        print(f"  Caching: {'enabled' if use_cache else 'disabled'}")
    
    @property
    def model(self):
        """Lazy load cross-encoder model."""
        if self._model is None:
            print(f"Loading cross-encoder model: {self.model_name}...")
            try:
                self._model = CrossEncoder(self.model_name)
                print(f"✓ Model loaded")
            except Exception as e:
                print(f"✗ Failed to load model: {e}")
                raise
        return self._model
    
    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: Optional[int] = None,
        return_scores: bool = True,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Rerank results using cross-encoder.
        
        Args:
            query: Search query
            results: List of results to rerank
            top_k: Number of results to return (None = all)
            return_scores: Include cross-encoder scores
            use_cache: Use cached scores if available
            
        Returns:
            Reranked results with optional scores
            
        Example:
            >>> results = retriever.retrieve("authentication")
            >>> reranked = reranker.rerank("authentication", results, top_k=5)
        """
        if not results:
            return []
        
        start_time = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(query, results)
        if use_cache and self.use_cache and cache_key in self._cache:
            self.stats['cache_hits'] += 1
            return self._cache[cache_key][:top_k] if top_k else self._cache[cache_key]
        
        # Prepare query-document pairs
        pairs = []
        for result in results:
            # Extract text content
            content = self._extract_content(result)
            pairs.append([query, content])
        
        # Batch predict scores
        try:
            scores = self.model.predict(
                pairs,
                batch_size=self.batch_size,
                show_progress_bar=False
            )
        except Exception as e:
            print(f"Warning: Reranking failed: {e}")
            # Return original results
            return results[:top_k] if top_k else results
        
        # Update results with cross-encoder scores
        reranked_results = []
        for i, result in enumerate(results):
            new_result = result.copy()
            ce_score = float(scores[i])
            
            # Store original score
            if 'score' in result:
                new_result['original_score'] = result['score']
            
            # Apply threshold
            if self.score_threshold is not None and ce_score < self.score_threshold:
                continue
            
            new_result['ce_score'] = ce_score
            new_result['score'] = ce_score  # Use CE score as primary
            
            if return_scores:
                new_result['scores'] = {
                    'cross_encoder': ce_score,
                    'original': result.get('score', 0.0)
                }
            
            reranked_results.append(new_result)
        
        # Sort by cross-encoder score
        reranked_results.sort(key=lambda x: x['ce_score'], reverse=True)
        
        # Limit to top_k
        if top_k:
            reranked_results = reranked_results[:top_k]
        
        # Cache results
        if self.use_cache:
            self._cache[cache_key] = reranked_results
        
        # Update stats
        elapsed = time.time() - start_time
        self.stats['total_reranks'] += 1
        self.stats['total_pairs'] += len(pairs)
        self.stats['total_time'] += elapsed
        
        return reranked_results
    
    def rerank_with_fusion(
        self,
        query: str,
        results: List[Dict[str, Any]],
        fusion_weight: float = 0.7,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank with score fusion (combine original + CE scores).
        
        Args:
            query: Search query
            results: Results to rerank
            fusion_weight: Weight for CE score (0-1), rest for original
            top_k: Number of results
            
        Returns:
            Reranked results with fused scores
            
        Example:
            >>> # 70% CE score, 30% original score
            >>> reranked = reranker.rerank_with_fusion(query, results, fusion_weight=0.7)
        """
        if not (0 <= fusion_weight <= 1):
            raise ValueError("fusion_weight must be between 0 and 1")
        
        # Get CE scores
        reranked = self.rerank(query, results, top_k=None, return_scores=True)
        
        # Normalize scores to 0-1 range
        if reranked:
            ce_scores = [r['ce_score'] for r in reranked]
            orig_scores = [r.get('original_score', 0.5) for r in reranked]
            
            # Min-max normalization
            ce_min, ce_max = min(ce_scores), max(ce_scores)
            orig_min, orig_max = min(orig_scores), max(orig_scores)
            
            ce_range = ce_max - ce_min if ce_max > ce_min else 1.0
            orig_range = orig_max - orig_min if orig_max > orig_min else 1.0
            
            for r in reranked:
                ce_norm = (r['ce_score'] - ce_min) / ce_range
                orig_norm = (r.get('original_score', 0.5) - orig_min) / orig_range
                
                # Fuse scores
                fused_score = (
                    fusion_weight * ce_norm +
                    (1 - fusion_weight) * orig_norm
                )
                
                r['fused_score'] = fused_score
                r['score'] = fused_score
            
            # Re-sort by fused score
            reranked.sort(key=lambda x: x['fused_score'], reverse=True)
        
        return reranked[:top_k] if top_k else reranked
    
    def rerank_reciprocal_rank_fusion(
        self,
        query: str,
        results: List[Dict[str, Any]],
        k: int = 60,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank using Reciprocal Rank Fusion (RRF).
        
        Combines original ranking with CE ranking using RRF formula.
        
        Args:
            query: Search query
            results: Results to rerank
            k: RRF constant (typically 60)
            top_k: Number of results
            
        Returns:
            Reranked results with RRF scores
        """
        # Get CE scores
        ce_ranked = self.rerank(query, results, top_k=None)
        
        # Create ID mapping
        result_map = {r.get('chunk_id', i): r for i, r in enumerate(results)}
        
        # Calculate RRF scores
        rrf_scores = {}
        
        # Original ranking
        for rank, result in enumerate(results, 1):
            result_id = result.get('chunk_id', id(result))
            rrf_scores[result_id] = 1.0 / (k + rank)
        
        # CE ranking
        for rank, result in enumerate(ce_ranked, 1):
            result_id = result.get('chunk_id', id(result))
            rrf_scores[result_id] = rrf_scores.get(result_id, 0) + 1.0 / (k + rank)
        
        # Create final results with RRF scores
        final_results = []
        for result_id, rrf_score in rrf_scores.items():
            if result_id in result_map:
                result = result_map[result_id].copy()
                result['rrf_score'] = rrf_score
                result['score'] = rrf_score
                final_results.append(result)
        
        # Sort by RRF score
        final_results.sort(key=lambda x: x['rrf_score'], reverse=True)
        
        return final_results[:top_k] if top_k else final_results
    
    def _extract_content(self, result: Dict[str, Any]) -> str:
        """Extract text content from result for reranking."""
        # Try different content fields
        content = result.get('content', '')
        if not content:
            content = result.get('chunk', '')
        if not content:
            content = result.get('text', '')
        if not content:
            # Fallback to concatenating metadata
            content = f"{result.get('file_path', '')} {result.get('function_name', '')}"
        
        # Truncate if too long (cross-encoders have token limits)
        max_length = 500
        if len(content) > max_length:
            content = content[:max_length]
        
        return content
    
    def _get_cache_key(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Generate cache key for query and results."""
        import hashlib
        result_ids = [r.get('chunk_id', str(i)) for i, r in enumerate(results)]
        key_str = f"{query}::{','.join(result_ids[:20])}"  # Limit for key size
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def clear_cache(self):
        """Clear reranking cache."""
        self._cache.clear()
        print("✓ Reranking cache cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get reranking statistics."""
        stats = self.stats.copy()
        
        if stats['total_reranks'] > 0:
            stats['avg_pairs_per_rerank'] = stats['total_pairs'] / stats['total_reranks']
            stats['avg_time_per_rerank'] = stats['total_time'] / stats['total_reranks']
        else:
            stats['avg_pairs_per_rerank'] = 0.0
            stats['avg_time_per_rerank'] = 0.0
        
        stats['cache_size'] = len(self._cache)
        stats['cache_hit_rate'] = (
            stats['cache_hits'] / stats['total_reranks']
            if stats['total_reranks'] > 0 else 0.0
        )
        
        return stats
    
    def reset_statistics(self):
        """Reset performance statistics."""
        self.stats = {
            'total_reranks': 0,
            'total_pairs': 0,
            'total_time': 0.0,
            'cache_hits': 0
        }
        print("✓ Statistics reset")


if __name__ == "__main__":
    print("Cross-Encoder Reranking Module")
    print("=" * 60)
    print("\nThis module provides precise reranking using cross-encoders.")
    print("\nFeatures:")
    print("  - More accurate than bi-encoder scoring")
    print("  - Multiple model support")
    print("  - Score fusion strategies")
    print("  - Reciprocal Rank Fusion (RRF)")
    print("\nExample usage:")
    print("""
    from features.rag_advanced.reranking import CrossEncoderReranker
    
    reranker = CrossEncoderReranker('ms-marco-mini')
    
    # Simple reranking
    reranked = reranker.rerank(query, results, top_k=5)
    
    # With score fusion
    reranked = reranker.rerank_with_fusion(query, results, fusion_weight=0.7)
    
    # With RRF
    reranked = reranker.rerank_reciprocal_rank_fusion(query, results)
    """)
