"""
Query Cache Manager

Provides caching for RAG search queries to improve performance.
Supports:
- LRU/LFU/FIFO eviction strategies
- TTL (time-to-live) for cache entries
- Semantic similarity-based cache hits
- Persistent cache to disk
- Cache statistics and monitoring

Features:
- Fast query lookups
- Configurable TTL
- Memory-efficient storage
- Thread-safe operations
"""

import hashlib
import pickle
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
import threading
import numpy as np


@dataclass
class QueryCacheEntry:
    """Single query cache entry with metadata."""
    query_hash: str
    query_text: str
    results: List[Dict[str, Any]]
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl_seconds: float = 3600.0
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        age = time.time() - self.created_at
        return age > self.ttl_seconds


@dataclass
class CacheStats:
    """Query cache statistics."""
    hits: int = 0
    misses: int = 0
    expirations: int = 0
    evictions: int = 0
    total_queries: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'expirations': self.expirations,
            'evictions': self.evictions,
            'total_queries': self.total_queries,
            'hit_rate': f"{self.hit_rate:.2%}"
        }


class QueryCache:
    """
    Cache for RAG search queries with TTL and eviction strategies.
    
    Caches search results to avoid repeated vector searches.
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        ttl_seconds: float = 3600.0,
        strategy: str = 'lru',
        cache_dir: Optional[str] = None,
        enable_persistence: bool = True,
        enable_similarity_matching: bool = False,
        similarity_threshold: float = 0.95
    ):
        """
        Initialize query cache.
        
        Args:
            max_size: Maximum number of cached queries
            ttl_seconds: Time-to-live for cache entries (default: 1 hour)
            strategy: Eviction strategy ('lru', 'lfu', 'fifo')
            cache_dir: Directory for persistent cache
            enable_persistence: Whether to save cache to disk
            enable_similarity_matching: Use embedding similarity for cache hits
            similarity_threshold: Minimum similarity for cache hit
        
        Example:
            >>> cache = QueryCache(
            ...     max_size=500,
            ...     ttl_seconds=3600,
            ...     strategy='lru'
            ... )
            >>> results = cache.get("authentication code")
            >>> if results is None:
            ...     results = perform_search("authentication code")
            ...     cache.put("authentication code", results)
        """
        if strategy not in ['lru', 'lfu', 'fifo']:
            raise ValueError(f"Invalid strategy: {strategy}")
        
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.strategy = strategy
        self.enable_persistence = enable_persistence
        self.enable_similarity_matching = enable_similarity_matching
        self.similarity_threshold = similarity_threshold
        
        # Cache storage
        self._cache: OrderedDict[str, QueryCacheEntry] = OrderedDict()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.stats = CacheStats()
        
        # Persistence
        self.cache_dir = Path(cache_dir) if cache_dir else Path("data/query_cache")
        if self.enable_persistence:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.cache_file = self.cache_dir / f"query_cache_{strategy}.pkl"
            self._load_from_disk()
        
        # For similarity matching (if enabled)
        self._embedding_model = None
        if enable_similarity_matching:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                print("Warning: sentence-transformers not available, similarity matching disabled")
                self.enable_similarity_matching = False
    
    def get(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached results for query.
        
        Args:
            query: Search query
        
        Returns:
            Cached results or None if not found
        
        Example:
            >>> results = cache.get("JWT authentication")
            >>> if results is not None:
            ...     print(f"Cache hit! Found {len(results)} results")
        """
        query_hash = self._hash_query(query)
        
        with self._lock:
            self.stats.total_queries += 1
            
            # Exact match
            if query_hash in self._cache:
                entry = self._cache[query_hash]
                
                # Check expiration
                if entry.is_expired():
                    self._cache.pop(query_hash)
                    self.stats.expirations += 1
                    self.stats.misses += 1
                    return None
                
                # Update access metadata
                entry.last_accessed = time.time()
                entry.access_count += 1
                
                # Move to end for LRU
                if self.strategy == 'lru':
                    self._cache.move_to_end(query_hash)
                
                self.stats.hits += 1
                return entry.results
            
            # Try similarity matching if enabled
            if self.enable_similarity_matching and self._embedding_model:
                similar_entry = self._find_similar_query(query)
                if similar_entry:
                    # Update access metadata
                    similar_entry.last_accessed = time.time()
                    similar_entry.access_count += 1
                    self.stats.hits += 1
                    return similar_entry.results
            
            self.stats.misses += 1
            return None
    
    def put(
        self,
        query: str,
        results: List[Dict[str, Any]],
        ttl_seconds: Optional[float] = None
    ) -> None:
        """
        Store query results in cache.
        
        Args:
            query: Search query
            results: Search results to cache
            ttl_seconds: Custom TTL for this entry (overrides default)
        
        Example:
            >>> results = [{"content": "...", "score": 0.9}]
            >>> cache.put("authentication", results)
        """
        query_hash = self._hash_query(query)
        ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds
        
        with self._lock:
            # Check if we need to evict
            self._evict_expired()
            while len(self._cache) >= self.max_size and self._cache:
                self._evict_one()
            
            # Create entry
            entry = QueryCacheEntry(
                query_hash=query_hash,
                query_text=query,
                results=results,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                ttl_seconds=ttl
            )
            
            # Store entry
            self._cache[query_hash] = entry
    
    def invalidate(self, query: str) -> bool:
        """
        Remove specific query from cache.
        
        Args:
            query: Query to invalidate
        
        Returns:
            True if entry was removed
        
        Example:
            >>> cache.invalidate("outdated query")
        """
        query_hash = self._hash_query(query)
        
        with self._lock:
            if query_hash in self._cache:
                self._cache.pop(query_hash)
                return True
            return False
    
    def clear(self) -> None:
        """
        Clear all cache entries.
        
        Example:
            >>> cache.clear()
            >>> print("Cache cleared")
        """
        with self._lock:
            self._cache.clear()
            self.stats = CacheStats()
    
    def clear_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        
        Example:
            >>> removed = cache.clear_expired()
            >>> print(f"Removed {removed} expired entries")
        """
        with self._lock:
            return self._evict_expired()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        
        Example:
            >>> stats = cache.get_stats()
            >>> print(f"Hit rate: {stats['hit_rate']}")
            >>> print(f"Total queries: {stats['total_queries']}")
        """
        with self._lock:
            stats_dict = self.stats.to_dict()
            stats_dict['current_size'] = len(self._cache)
            stats_dict['max_size'] = self.max_size
            return stats_dict
    
    def resize(self, new_max_size: int) -> None:
        """
        Resize cache capacity.
        
        Args:
            new_max_size: New maximum cache size
        
        Example:
            >>> cache.resize(2000)
        """
        with self._lock:
            self.max_size = new_max_size
            
            # Evict if necessary
            while len(self._cache) > self.max_size:
                self._evict_one()
    
    def save_to_disk(self) -> None:
        """
        Save cache to disk.
        
        Example:
            >>> cache.save_to_disk()
        """
        if not self.enable_persistence:
            return
        
        with self._lock:
            try:
                # Remove expired entries before saving
                self._evict_expired()
                
                # Prepare data for pickling
                cache_data = {
                    'entries': dict(self._cache),
                    'stats': self.stats,
                    'max_size': self.max_size,
                    'ttl_seconds': self.ttl_seconds,
                    'strategy': self.strategy,
                    'saved_at': datetime.now().isoformat()
                }
                
                # Save to disk
                with open(self.cache_file, 'wb') as f:
                    pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
                
                print(f"✓ Query cache saved to {self.cache_file} "
                      f"({len(self._cache)} entries)")
                
            except Exception as e:
                print(f"Warning: Could not save query cache: {e}")
    
    def _load_from_disk(self) -> None:
        """Load cache from disk."""
        if not self.cache_file.exists():
            return
        
        try:
            with open(self.cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Restore cache
            self._cache = OrderedDict(cache_data['entries'])
            self.stats = cache_data['stats']
            
            # Remove expired entries
            expired = self._evict_expired()
            
            # Validate and trim if needed
            if len(self._cache) > self.max_size:
                while len(self._cache) > self.max_size:
                    self._evict_one()
            
            saved_at = cache_data.get('saved_at', 'unknown')
            print(f"✓ Loaded query cache from disk: {len(self._cache)} entries "
                  f"({expired} expired, saved at {saved_at})")
            
        except Exception as e:
            print(f"Warning: Could not load query cache: {e}")
            self._cache = OrderedDict()
            self.stats = CacheStats()
    
    def _evict_expired(self) -> int:
        """Remove all expired entries. Returns count of removed entries."""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            self._cache.pop(key)
            self.stats.expirations += 1
        
        return len(expired_keys)
    
    def _evict_one(self) -> None:
        """Evict one entry based on strategy."""
        if not self._cache:
            return
        
        if self.strategy == 'lru':
            # Remove least recently used (first item)
            self._cache.popitem(last=False)
        
        elif self.strategy == 'lfu':
            # Remove least frequently used
            min_key = min(self._cache.keys(),
                         key=lambda k: self._cache[k].access_count)
            self._cache.pop(min_key)
        
        elif self.strategy == 'fifo':
            # Remove oldest (first item)
            self._cache.popitem(last=False)
        
        # Update statistics
        self.stats.evictions += 1
    
    def _hash_query(self, query: str) -> str:
        """Generate hash for query."""
        return hashlib.sha256(query.lower().strip().encode('utf-8')).hexdigest()
    
    def _find_similar_query(self, query: str) -> Optional[QueryCacheEntry]:
        """Find similar query in cache using embedding similarity."""
        if not self._embedding_model or not self._cache:
            return None
        
        try:
            # Encode query
            query_embedding = self._embedding_model.encode([query])[0]
            
            # Check cache entries
            best_similarity = 0.0
            best_entry = None
            
            for entry in self._cache.values():
                # Skip expired entries
                if entry.is_expired():
                    continue
                
                # Encode cached query
                cached_embedding = self._embedding_model.encode([entry.query_text])[0]
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, cached_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(cached_embedding)
                )
                
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_entry = entry
            
            return best_entry
            
        except Exception as e:
            print(f"Warning: Similarity matching failed: {e}")
            return None
    
    def __del__(self):
        """Save cache on cleanup."""
        if self.enable_persistence:
            try:
                self.save_to_disk()
            except:
                pass


if __name__ == "__main__":
    print("=== Query Cache Manager Tests ===\n")
    
    # Create test cache
    cache = QueryCache(
        max_size=5,
        ttl_seconds=3600,
        strategy='lru',
        cache_dir='data/test_query_cache',
        enable_persistence=False,
        enable_similarity_matching=False
    )
    
    # Test 1: Basic put/get
    print("1. Basic Operations:")
    test_results = [
        {"content": "test result 1", "score": 0.9},
        {"content": "test result 2", "score": 0.8}
    ]
    cache.put("test query", test_results)
    retrieved = cache.get("test query")
    assert retrieved is not None
    assert len(retrieved) == 2
    print("   ✓ Put/Get works")
    
    # Test 2: Cache miss
    print("\n2. Cache Miss:")
    result = cache.get("nonexistent query")
    assert result is None
    print("   ✓ Miss detection works")
    
    # Test 3: Eviction
    print("\n3. Eviction (LRU):")
    for i in range(10):
        cache.put(f"query {i}", [{"content": f"result {i}"}])
    stats = cache.get_stats()
    print(f"   Entries: {stats['current_size']} (max: 5)")
    print(f"   Evictions: {stats['evictions']}")
    assert stats['current_size'] == 5
    print("   ✓ Eviction works")
    
    # Test 4: Hit rate
    print("\n4. Hit Rate:")
    for _ in range(5):
        cache.get("query 9")  # Hit
        cache.get("nonexistent")  # Miss
    stats = cache.get_stats()
    print(f"   Hit rate: {stats['hit_rate']}")
    print("   ✓ Hit rate tracking works")
    
    # Test 5: TTL expiration
    print("\n5. TTL Expiration:")
    cache.clear()
    cache.put("short lived", [{"content": "temp"}], ttl_seconds=1)
    result = cache.get("short lived")
    assert result is not None
    print("   ✓ Entry accessible immediately")
    time.sleep(2)
    result = cache.get("short lived")
    assert result is None
    print("   ✓ Entry expired after TTL")
    
    # Test 6: Clear expired
    print("\n6. Clear Expired:")
    for i in range(3):
        cache.put(f"temp {i}", [{"content": f"result {i}"}], ttl_seconds=1)
    time.sleep(2)
    removed = cache.clear_expired()
    print(f"   Removed {removed} expired entries")
    print("   ✓ Expired cleanup works")
    
    # Test 7: Statistics
    print("\n7. Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print("   ✓ Statistics work")
    
    print("\n✓ All query cache tests passed!")
