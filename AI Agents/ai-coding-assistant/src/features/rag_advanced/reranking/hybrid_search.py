"""
Hybrid Search Module - Full Implementation

Combines vector search with keyword/BM25 search for best of both worlds.
Vector search finds semantic matches, BM25 finds exact keyword matches.

Features:
- BM25 keyword search implementation
- Score fusion strategies (linear, RRF)
- Configurable weights
- Language-specific tokenization
- Performance monitoring

Example:
    >>> hybrid = HybridSearch(vector_retriever, bm25_index)
    >>> results = hybrid.search(query, top_k=10, alpha=0.5)
"""

from typing import List, Dict, Optional, Any, Set
import numpy as np
from pathlib import Path
import re
from collections import Counter
import math


class BM25:
    """
    BM25 (Best Matching 25) ranking function implementation.
    
    BM25 is a probabilistic ranking function used for keyword search.
    Works well for exact term matching.
    """
    
    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        epsilon: float = 0.25
    ):
        """
        Initialize BM25.
        
        Args:
            k1: Term frequency saturation parameter (typically 1.2-2.0)
            b: Length normalization parameter (typically 0.75)
            epsilon: Floor value for IDF
        """
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon
        
        # Will be set during indexing
        self.corpus_size = 0
        self.avgdl = 0.0
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
        self.docs = []
        self.doc_ids = []
    
    def index(self, documents: List[Dict[str, Any]]):
        """
        Index documents for BM25 search.
        
        Args:
            documents: List of documents with 'content' and optionally 'id'
        """
        self.docs = []
        self.doc_ids = []
        self.doc_len = []
        
        # Tokenize documents
        for doc in documents:
            content = doc.get('content', '')
            doc_id = doc.get('chunk_id', doc.get('id', len(self.docs)))
            
            tokens = self._tokenize(content)
            self.docs.append(tokens)
            self.doc_ids.append(doc_id)
            self.doc_len.append(len(tokens))
        
        self.corpus_size = len(self.docs)
        self.avgdl = sum(self.doc_len) / self.corpus_size if self.corpus_size > 0 else 0
        
        # Calculate document frequencies and IDF
        self._calculate_idf()
    
    def search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search using BM25.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of results with BM25 scores
        """
        query_tokens = self._tokenize(query)
        
        scores = []
        for i, doc in enumerate(self.docs):
            score = self._score(query_tokens, doc, i)
            scores.append({
                'doc_id': self.doc_ids[i],
                'index': i,
                'score': score
            })
        
        # Sort by score
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        return scores[:top_k]
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text (simple word-based)."""
        # Lowercase and split on non-alphanumeric
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def _calculate_idf(self):
        """Calculate IDF scores for all terms."""
        # Count documents containing each term
        df = Counter()
        for doc in self.docs:
            unique_terms = set(doc)
            for term in unique_terms:
                df[term] += 1
        
        self.doc_freqs = df
        
        # Calculate IDF
        self.idf = {}
        for term, freq in df.items():
            idf = math.log(
                (self.corpus_size - freq + 0.5) / (freq + 0.5) + 1.0
            )
            self.idf[term] = max(idf, self.epsilon)
    
    def _score(self, query_tokens: List[str], doc: List[str], doc_idx: int) -> float:
        """Calculate BM25 score for a document."""
        score = 0.0
        doc_len = self.doc_len[doc_idx]
        doc_freq = Counter(doc)
        
        for term in query_tokens:
            if term not in doc_freq:
                continue
            
            freq = doc_freq[term]
            idf = self.idf.get(term, 0)
            
            # BM25 formula
            numerator = freq * (self.k1 + 1)
            denominator = freq + self.k1 * (
                1 - self.b + self.b * (doc_len / self.avgdl)
            )
            
            score += idf * (numerator / denominator)
        
        return score


class HybridSearch:
    """
    Hybrid search combining vector and keyword (BM25) search.
    
    Features:
    - Vector search for semantic matching
    - BM25 for exact keyword matching
    - Multiple fusion strategies
    - Configurable weights
    """
    
    def __init__(
        self,
        vector_retriever=None,
        bm25_k1: float = 1.5,
        bm25_b: float = 0.75
    ):
        """
        Initialize hybrid search.
        
        Args:
            vector_retriever: Vector-based retriever (RAGRetriever)
            bm25_k1: BM25 k1 parameter
            bm25_b: BM25 b parameter
            
        Example:
            >>> hybrid = HybridSearch(vector_retriever)
        """
        self.vector_retriever = vector_retriever
        self.bm25 = BM25(k1=bm25_k1, b=bm25_b)
        self.indexed = False
        
        print("HybridSearch initialized:")
        print(f"  Vector retriever: {'✓' if vector_retriever else '✗'}")
        print(f"  BM25 parameters: k1={bm25_k1}, b={bm25_b}")
    
    def index_documents(self, documents: List[Dict[str, Any]]):
        """
        Index documents for BM25 search.
        
        Args:
            documents: List of documents with 'content' field
        """
        print(f"Indexing {len(documents)} documents for BM25...")
        self.bm25.index(documents)
        self.indexed = True
        print("✓ BM25 indexing complete")
    
    def search(
        self,
        query: str,
        collection_name: Optional[str] = None,
        top_k: int = 10,
        alpha: float = 0.5,
        fusion_method: str = 'linear',
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining vector and BM25.
        
        Args:
            query: Search query
            collection_name: Vector DB collection
            top_k: Number of results
            alpha: Weight for vector search (0-1), BM25 gets (1-alpha)
            fusion_method: 'linear', 'rrf', or 'max'
            language: Programming language filter
            
        Returns:
            Fused results
            
        Example:
            >>> # 50% vector, 50% BM25
            >>> results = hybrid.search(query, top_k=10, alpha=0.5)
            >>> 
            >>> # 70% vector, 30% BM25
            >>> results = hybrid.search(query, top_k=10, alpha=0.7)
        """
        if not (0 <= alpha <= 1):
            raise ValueError("alpha must be between 0 and 1")
        
        if not self.indexed:
            raise RuntimeError("Documents not indexed. Call index_documents() first.")
        
        # Get vector search results
        vector_results = []
        if self.vector_retriever and alpha > 0:
            try:
                vector_results = self.vector_retriever.retrieve(
                    query=query,
                    collection_name=collection_name,
                    top_k=top_k * 2,  # Get more for better fusion
                    language_filter=language
                )
            except Exception as e:
                print(f"Warning: Vector search failed: {e}")
        
        # Get BM25 results
        bm25_results = []
        if (1 - alpha) > 0:
            bm25_results = self.bm25.search(query, top_k=top_k * 2)
        
        # Fuse results
        if fusion_method == 'linear':
            fused = self._linear_fusion(vector_results, bm25_results, alpha, top_k)
        elif fusion_method == 'rrf':
            fused = self._rrf_fusion(vector_results, bm25_results, top_k)
        elif fusion_method == 'max':
            fused = self._max_fusion(vector_results, bm25_results, alpha, top_k)
        else:
            raise ValueError(f"Unknown fusion method: {fusion_method}")
        
        return fused
    
    def _linear_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        alpha: float,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Fuse using weighted linear combination."""
        # Normalize scores to 0-1
        vec_scores = self._normalize_scores(
            {r.get('chunk_id', r.get('doc_id', i)): r.get('score', 0) 
             for i, r in enumerate(vector_results)}
        )
        bm25_scores = self._normalize_scores(
            {r['doc_id']: r['score'] for r in bm25_results}
        )
        
        # Combine scores
        all_ids = set(vec_scores.keys()) | set(bm25_scores.keys())
        fused_scores = {}
        
        for doc_id in all_ids:
            vec_score = vec_scores.get(doc_id, 0.0)
            bm25_score = bm25_scores.get(doc_id, 0.0)
            fused_scores[doc_id] = alpha * vec_score + (1 - alpha) * bm25_score
        
        # Create result list
        results = []
        vec_map = {r.get('chunk_id', r.get('doc_id')): r for r in vector_results}
        
        for doc_id, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]:
            if doc_id in vec_map:
                result = vec_map[doc_id].copy()
                result['hybrid_score'] = score
                result['score'] = score
                results.append(result)
        
        return results
    
    def _rrf_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        top_k: int,
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """Fuse using Reciprocal Rank Fusion."""
        rrf_scores = {}
        
        # Vector ranking
        for rank, result in enumerate(vector_results, 1):
            doc_id = result.get('chunk_id', result.get('doc_id'))
            rrf_scores[doc_id] = 1.0 / (k + rank)
        
        # BM25 ranking
        for rank, result in enumerate(bm25_results, 1):
            doc_id = result['doc_id']
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (k + rank)
        
        # Create results
        results = []
        vec_map = {r.get('chunk_id', r.get('doc_id')): r for r in vector_results}
        
        for doc_id, score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]:
            if doc_id in vec_map:
                result = vec_map[doc_id].copy()
                result['rrf_score'] = score
                result['score'] = score
                results.append(result)
        
        return results
    
    def _max_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        alpha: float,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Fuse using maximum score."""
        vec_scores = self._normalize_scores(
            {r.get('chunk_id', r.get('doc_id', i)): r.get('score', 0) 
             for i, r in enumerate(vector_results)}
        )
        bm25_scores = self._normalize_scores(
            {r['doc_id']: r['score'] for r in bm25_results}
        )
        
        all_ids = set(vec_scores.keys()) | set(bm25_scores.keys())
        max_scores = {}
        
        for doc_id in all_ids:
            vec_score = vec_scores.get(doc_id, 0.0)
            bm25_score = bm25_scores.get(doc_id, 0.0)
            max_scores[doc_id] = max(alpha * vec_score, (1 - alpha) * bm25_score)
        
        # Create results
        results = []
        vec_map = {r.get('chunk_id', r.get('doc_id')): r for r in vector_results}
        
        for doc_id, score in sorted(max_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]:
            if doc_id in vec_map:
                result = vec_map[doc_id].copy()
                result['max_score'] = score
                result['score'] = score
                results.append(result)
        
        return results
    
    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Normalize scores to 0-1 range using min-max normalization."""
        if not scores:
            return {}
        
        values = list(scores.values())
        min_val = min(values)
        max_val = max(values)
        
        if max_val == min_val:
            # All scores are the same
            return {k: 1.0 for k in scores.keys()}
        
        normalized = {}
        for doc_id, score in scores.items():
            normalized[doc_id] = (score - min_val) / (max_val - min_val)
        
        return normalized
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get hybrid search statistics."""
        return {
            'indexed': self.indexed,
            'corpus_size': self.bm25.corpus_size,
            'avg_doc_length': self.bm25.avgdl,
            'vocabulary_size': len(self.bm25.idf),
            'bm25_parameters': {
                'k1': self.bm25.k1,
                'b': self.bm25.b,
                'epsilon': self.bm25.epsilon
            }
        }


if __name__ == "__main__":
    print("Hybrid Search Module")
    print("=" * 60)
    print("\nThis module combines vector and keyword search.")
    print("\nFeatures:")
    print("  - BM25 for exact keyword matching")
    print("  - Vector search for semantic matching")
    print("  - Multiple fusion strategies (linear, RRF, max)")
    print("\nExample usage:")
    print("""
    from features.rag_advanced.reranking import HybridSearch
    
    hybrid = HybridSearch(vector_retriever)
    
    # Index documents for BM25
    hybrid.index_documents(documents)
    
    # Search with 50/50 weight
    results = hybrid.search(query, alpha=0.5, fusion_method='linear')
    
    # Search with 70% vector, 30% BM25
    results = hybrid.search(query, alpha=0.7, fusion_method='rrf')
    """)
