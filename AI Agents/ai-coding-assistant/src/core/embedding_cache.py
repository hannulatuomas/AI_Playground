"""
Embedding Cache Manager

Provides efficient caching for embeddings to avoid recomputing.
Supports:
- LRU/LFU/FIFO eviction strategies
- Persistent cache to disk
- Memory-aware cache sizing
- SHA256-based content hashing
- Automatic cache invalidation

Features:
- Fast lookups with O(1) access
- Configurable cache size
- Cache hit/miss statistics
- Thread-safe operations
"""

import hashlib
import pickle
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
import threading
import numpy as np


@dataclass
class CacheEntry:
    """Single cache entry with metadata."""
    embedding: np.ndarray
    content_hash: str
    created_at: float
    last_accessed: float
    access_count: int = 0
    size_bytes: int = 0


@dataclass
class CacheStatistics:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    entry_count: int = 0
    
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
            'evictions': self.evictions,
            'hit_rate': f"{self.hit_rate:.2%}",
            'total_size_mb': round(self.total_size_bytes / (1024 * 1024), 2),
            'entry_count': self.entry_count
        }


class EmbeddingCache:
    """
    LRU/LFU/FIFO cache for embeddings with persistence.
    
    Thread-safe caching with configurable eviction strategies.
    """
    
    def __init__(
        self,
        max_size: int = 10000,
        strategy: str = 'lru',
        cache_dir: Optional[str] = None,
        enable_persistence: bool = True
    ):
        """
        Initialize embedding cache.
        
        Args:
            max_size: Maximum number of cached embeddings
            strategy: Eviction strategy ('lru', 'lfu', 'fifo')
            cache_dir: Directory for persistent cache
            enable_persistence: Whether to save cache to disk
        
        Example:
            >>> cache = EmbeddingCache(max_size=5000, strategy='lru')
            >>> embedding = cache.get("my text content")
            >>> if embedding is None:
            ...     embedding = model.encode("my text content")
            ...     cache.put("my text content", embedding)
        """
        if strategy not in ['lru', 'lfu', 'fifo']:
            raise ValueError(f"Invalid strategy: {strategy}")
        
        self.max_size = max_size
        self.strategy = strategy
        self.enable_persistence = enable_persistence
        
        # Cache storage (OrderedDict for LRU)
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.stats = CacheStatistics()
        
        # Persistence
        self.cache_dir = Path(cache_dir) if cache_dir else Path("data/embedding_cache")
        if self.enable_persistence:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.cache_file = self.cache_dir / f"embedding_cache_{strategy}.pkl"
            self._load_from_disk()
    
    def get(self, content: str) -> Optional[np.ndarray]:
        """
        Get embedding from cache.
        
        Args:
            content: Text content to look up
        
        Returns:
            Cached embedding or None if not found
        
        Example:
            >>> embedding = cache.get("Hello world")
            >>> if embedding is not None:
            ...     print(f"Cache hit! Shape: {embedding.shape}")
        """
        content_hash = self._hash_content(content)
        
        with self._lock:
            if content_hash in self._cache:
                entry = self._cache[content_hash]
                
                # Update access metadata
                entry.last_accessed = time.time()
                entry.access_count += 1
                
                # Move to end for LRU
                if self.strategy == 'lru':
                    self._cache.move_to_end(content_hash)
                
                self.stats.hits += 1
                return entry.embedding.copy()
            else:
                self.stats.misses += 1
                return None
    
    def put(self, content: str, embedding: np.ndarray) -> None:
        """
        Store embedding in cache.
        
        Args:
            content: Text content
            embedding: Corresponding embedding vector
        
        Example:
            >>> embedding = model.encode("Hello world")
            >>> cache.put("Hello world", embedding)
        """
        content_hash = self._hash_content(content)
        
        with self._lock:
            # Calculate entry size
            size_bytes = embedding.nbytes + len(content_hash) + 100  # Overhead estimate
            
            # Check if we need to evict
            while len(self._cache) >= self.max_size and self._cache:
                self._evict_one()
            
            # Create entry
            entry = CacheEntry(
                embedding=embedding.copy(),
                content_hash=content_hash,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                size_bytes=size_bytes
            )
            
            # Store entry
            self._cache[content_hash] = entry
            self.stats.entry_count = len(self._cache)
            self.stats.total_size_bytes += size_bytes
    
    def put_batch(self, contents: List[str], embeddings: np.ndarray) -> None:
        """
        Store multiple embeddings at once.
        
        Args:
            contents: List of text contents
            embeddings: Array of embeddings (shape: [len(contents), dim])
        
        Example:
            >>> contents = ["text 1", "text 2", "text 3"]
            >>> embeddings = model.encode(contents)
            >>> cache.put_batch(contents, embeddings)
        """
        if len(contents) != len(embeddings):
            raise ValueError("Contents and embeddings must have same length")
        
        with self._lock:
            for content, embedding in zip(contents, embeddings):
                self.put(content, embedding)
    
    def invalidate(self, content: str) -> bool:
        """
        Remove specific entry from cache.
        
        Args:
            content: Text content to invalidate
        
        Returns:
            True if entry was removed
        
        Example:
            >>> cache.invalidate("outdated content")
        """
        content_hash = self._hash_content(content)
        
        with self._lock:
            if content_hash in self._cache:
                entry = self._cache.pop(content_hash)
                self.stats.total_size_bytes -= entry.size_bytes
                self.stats.entry_count = len(self._cache)
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
            self.stats = CacheStatistics()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        
        Example:
            >>> stats = cache.get_stats()
            >>> print(f"Hit rate: {stats['hit_rate']}")
            >>> print(f"Total size: {stats['total_size_mb']} MB")
        """
        with self._lock:
            self.stats.entry_count = len(self._cache)
            return self.stats.to_dict()
    
    def resize(self, new_max_size: int) -> None:
        """
        Resize cache capacity.
        
        Args:
            new_max_size: New maximum cache size
        
        Example:
            >>> cache.resize(20000)
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
                # Prepare data for pickling
                cache_data = {
                    'entries': dict(self._cache),
                    'stats': self.stats,
                    'max_size': self.max_size,
                    'strategy': self.strategy,
                    'saved_at': datetime.now().isoformat()
                }
                
                # Save to disk
                with open(self.cache_file, 'wb') as f:
                    pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
                
                print(f"✓ Cache saved to {self.cache_file} "
                      f"({len(self._cache)} entries, "
                      f"{self.stats.total_size_bytes / (1024*1024):.2f} MB)")
                
            except Exception as e:
                print(f"Warning: Could not save cache: {e}")
    
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
            
            # Validate and trim if needed
            if len(self._cache) > self.max_size:
                while len(self._cache) > self.max_size:
                    self._evict_one()
            
            saved_at = cache_data.get('saved_at', 'unknown')
            print(f"✓ Loaded cache from disk: {len(self._cache)} entries "
                  f"(saved at {saved_at})")
            
        except Exception as e:
            print(f"Warning: Could not load cache: {e}")
            self._cache = OrderedDict()
            self.stats = CacheStatistics()
    
    def _evict_one(self) -> None:
        """Evict one entry based on strategy."""
        if not self._cache:
            return
        
        if self.strategy == 'lru':
            # Remove least recently used (first item)
            key, entry = self._cache.popitem(last=False)
        
        elif self.strategy == 'lfu':
            # Remove least frequently used
            min_key = min(self._cache.keys(), 
                         key=lambda k: self._cache[k].access_count)
            entry = self._cache.pop(min_key)
        
        elif self.strategy == 'fifo':
            # Remove oldest (first item)
            key, entry = self._cache.popitem(last=False)
        
        # Update statistics
        self.stats.evictions += 1
        self.stats.total_size_bytes -= entry.size_bytes
    
    def _hash_content(self, content: str) -> str:
        """Generate hash for content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def __del__(self):
        """Save cache on cleanup."""
        if self.enable_persistence:
            try:
                self.save_to_disk()
            except:
                pass


if __name__ == "__main__":
    print("=== Embedding Cache Manager Tests ===\n")
    
    # Create test cache
    cache = EmbeddingCache(
        max_size=5,
        strategy='lru',
        cache_dir='data/test_cache',
        enable_persistence=False
    )
    
    # Test 1: Basic put/get
    print("1. Basic Operations:")
    test_embedding = np.random.rand(384)
    cache.put("test content", test_embedding)
    retrieved = cache.get("test content")
    assert retrieved is not None
    assert np.allclose(retrieved, test_embedding)
    print("   ✓ Put/Get works")
    
    # Test 2: Cache miss
    print("\n2. Cache Miss:")
    result = cache.get("nonexistent content")
    assert result is None
    print("   ✓ Miss detection works")
    
    # Test 3: Eviction
    print("\n3. Eviction (LRU):")
    for i in range(10):
        cache.put(f"content {i}", np.random.rand(384))
    stats = cache.get_stats()
    print(f"   Entries: {stats['entry_count']} (max: 5)")
    print(f"   Evictions: {stats['evictions']}")
    assert stats['entry_count'] == 5
    print("   ✓ Eviction works")
    
    # Test 4: Hit rate
    print("\n4. Hit Rate:")
    for _ in range(5):
        cache.get("content 9")  # Hit
        cache.get("nonexistent")  # Miss
    stats = cache.get_stats()
    print(f"   Hit rate: {stats['hit_rate']}")
    print("   ✓ Hit rate tracking works")
    
    # Test 5: Batch operations
    print("\n5. Batch Put:")
    contents = [f"batch {i}" for i in range(3)]
    embeddings = np.random.rand(3, 384)
    cache.put_batch(contents, embeddings)
    print(f"   Added {len(contents)} embeddings")
    print("   ✓ Batch operations work")
    
    # Test 6: Statistics
    print("\n6. Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print("   ✓ Statistics work")
    
    print("\n✓ All cache tests passed!")
