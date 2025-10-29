"""
Caching System

This module provides a comprehensive caching system for the AI Agent Console:
- LLM response caching
- Embedding caching
- Tool result caching
- Configurable cache backends (memory, file, Redis)
- TTL and size-based eviction
- Cache invalidation strategies
"""

import json
import hashlib
import logging
import time
import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import OrderedDict


logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached item."""
    key: str
    value: Any
    created_at: float
    accessed_at: float
    access_count: int
    ttl: Optional[int]  # Time to live in seconds
    size_bytes: int
    metadata: Dict[str, Any]
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.ttl is None:
            return False
        return (time.time() - self.created_at) > self.ttl
    
    def update_access(self) -> None:
        """Update access statistics."""
        self.accessed_at = time.time()
        self.access_count += 1


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get item from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, entry: CacheEntry) -> bool:
        """Set item in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete item from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all items from cache."""
        pass
    
    @abstractmethod
    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all keys matching pattern."""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get number of items in cache."""
        pass


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend using OrderedDict for LRU eviction."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize memory cache.
        
        Args:
            max_size: Maximum number of items in cache
        """
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get item from cache."""
        entry = self.cache.get(key)
        if entry:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry.update_access()
        return entry
    
    def set(self, key: str, entry: CacheEntry) -> bool:
        """Set item in cache."""
        try:
            # Remove if exists
            if key in self.cache:
                del self.cache[key]
            
            # Add to cache
            self.cache[key] = entry
            
            # Evict oldest if over max_size
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)  # Remove oldest
            
            return True
        except Exception as e:
            logger.error(f"Failed to set cache entry: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete item from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all items from cache."""
        self.cache.clear()
        return True
    
    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all keys matching pattern."""
        if pattern is None:
            return list(self.cache.keys())
        
        # Simple pattern matching (supports * wildcard)
        import re
        regex = re.compile(pattern.replace('*', '.*'))
        return [k for k in self.cache.keys() if regex.match(k)]
    
    def size(self) -> int:
        """Get number of items in cache."""
        return len(self.cache)


class FileCacheBackend(CacheBackend):
    """File-based cache backend for persistence."""
    
    def __init__(self, cache_dir: Path):
        """
        Initialize file cache.
        
        Args:
            cache_dir: Directory for cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, key: str) -> Path:
        """Get file path for cache key."""
        # Hash key to create valid filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get item from cache."""
        file_path = self._get_file_path(key)
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'rb') as f:
                entry = pickle.load(f)
            
            entry.update_access()
            
            # Save updated access info
            with open(file_path, 'wb') as f:
                pickle.dump(entry, f)
            
            return entry
        except Exception as e:
            logger.error(f"Failed to load cache entry: {e}")
            return None
    
    def set(self, key: str, entry: CacheEntry) -> bool:
        """Set item in cache."""
        file_path = self._get_file_path(key)
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(entry, f)
            return True
        except Exception as e:
            logger.error(f"Failed to save cache entry: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete item from cache."""
        file_path = self._get_file_path(key)
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception as e:
                logger.error(f"Failed to delete cache entry: {e}")
                return False
        return False
    
    def clear(self) -> bool:
        """Clear all items from cache."""
        try:
            for file_path in self.cache_dir.glob('*.cache'):
                file_path.unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all keys matching pattern."""
        # For file backend, we can't easily recover original keys
        # This would require storing a key mapping file
        logger.warning("File backend keys() not fully supported")
        return []
    
    def size(self) -> int:
        """Get number of items in cache."""
        return len(list(self.cache_dir.glob('*.cache')))


class Cache:
    """
    Main cache interface with support for multiple backends and cache types.
    
    Features:
    - Multiple cache backends (memory, file)
    - TTL-based expiration
    - Size-based eviction (LRU)
    - Cache statistics
    - Hit/miss tracking
    """
    
    def __init__(
        self,
        backend: CacheBackend,
        default_ttl: Optional[int] = 3600,  # 1 hour default
        enable_stats: bool = True
    ):
        """
        Initialize cache.
        
        Args:
            backend: Cache backend implementation
            default_ttl: Default TTL in seconds (None = no expiration)
            enable_stats: Enable cache statistics tracking
        """
        self.backend = backend
        self.default_ttl = default_ttl
        self.enable_stats = enable_stats
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0
        }
    
    def get(
        self,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get item from cache.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        entry = self.backend.get(key)
        
        if entry is None:
            if self.enable_stats:
                self.stats['misses'] += 1
            return default
        
        # Check expiration
        if entry.is_expired():
            self.backend.delete(key)
            if self.enable_stats:
                self.stats['misses'] += 1
                self.stats['evictions'] += 1
            return default
        
        if self.enable_stats:
            self.stats['hits'] += 1
        
        return entry.value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Set item in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None = use default)
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        if ttl is None:
            ttl = self.default_ttl
        
        # Calculate size
        try:
            size_bytes = len(pickle.dumps(value))
        except:
            size_bytes = 0
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            ttl=ttl,
            size_bytes=size_bytes,
            metadata=metadata or {}
        )
        
        success = self.backend.set(key, entry)
        
        if success and self.enable_stats:
            self.stats['sets'] += 1
        
        return success
    
    def delete(self, key: str) -> bool:
        """Delete item from cache."""
        success = self.backend.delete(key)
        if success and self.enable_stats:
            self.stats['deletes'] += 1
        return success
    
    def clear(self) -> bool:
        """Clear all items from cache."""
        return self.backend.clear()
    
    def size(self) -> int:
        """
        Get the number of items in cache.
        
        Returns:
            Number of items in cache
        """
        return self.backend.size()
    
    def has(self, key: str) -> bool:
        """
        Check if a key exists in cache.
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists and is not expired, False otherwise
        """
        entry = self.backend.get(key)
        if entry is None:
            return False
        
        # Check if expired
        if entry.is_expired():
            self.backend.delete(key)
            return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            **self.stats,
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'size': self.backend.size()
        }
    
    def generate_key(self, *args, **kwargs) -> str:
        """
        Generate cache key from arguments.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Create deterministic key from arguments
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()


class LLMResponseCache(Cache):
    """Specialized cache for LLM responses."""
    
    def generate_key(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate cache key for LLM request."""
        key_data = {
            'prompt': prompt,
            'model': model,
            'temperature': temperature,
            **kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return f"llm:{hashlib.md5(key_str.encode()).hexdigest()}"


class EmbeddingCache(Cache):
    """Specialized cache for embeddings."""
    
    def generate_key(
        self,
        text: str,
        model: str = "default"
    ) -> str:
        """Generate cache key for embedding request."""
        key_data = {
            'text': text,
            'model': model
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return f"embed:{hashlib.md5(key_str.encode()).hexdigest()}"


class CacheManager:
    """
    Manages multiple cache instances for different purposes.
    
    Provides:
    - LLM response cache
    - Embedding cache
    - General data cache
    """
    
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        use_memory: bool = True,
        use_file: bool = True,
        llm_cache_ttl: int = 86400,      # 24 hours
        embedding_cache_ttl: int = 604800,  # 7 days
        data_cache_ttl: int = 3600        # 1 hour
    ):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for file-based caches
            use_memory: Use in-memory cache
            use_file: Use file-based cache
            llm_cache_ttl: TTL for LLM responses
            embedding_cache_ttl: TTL for embeddings
            data_cache_ttl: TTL for general data
        """
        self.cache_dir = cache_dir or Path('./cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create cache backends
        if use_file:
            llm_backend = FileCacheBackend(self.cache_dir / 'llm')
            embedding_backend = FileCacheBackend(self.cache_dir / 'embeddings')
            data_backend = FileCacheBackend(self.cache_dir / 'data')
        else:
            llm_backend = MemoryCacheBackend(max_size=1000)
            embedding_backend = MemoryCacheBackend(max_size=10000)
            data_backend = MemoryCacheBackend(max_size=500)
        
        # Create specialized caches
        self.llm_cache = LLMResponseCache(llm_backend, default_ttl=llm_cache_ttl)
        self.embedding_cache = EmbeddingCache(embedding_backend, default_ttl=embedding_cache_ttl)
        self.data_cache = Cache(data_backend, default_ttl=data_cache_ttl)
        
        logger.info("Cache manager initialized")
    
    def clear_all(self) -> None:
        """Clear all caches."""
        self.llm_cache.clear()
        self.embedding_cache.clear()
        self.data_cache.clear()
        logger.info("All caches cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches."""
        return {
            'llm_cache': self.llm_cache.get_stats(),
            'embedding_cache': self.embedding_cache.get_stats(),
            'data_cache': self.data_cache.get_stats()
        }


def create_cache_manager(**kwargs) -> CacheManager:
    """
    Factory function to create CacheManager instance.
    
    Args:
        **kwargs: Arguments passed to CacheManager
        
    Returns:
        CacheManager instance
    """
    return CacheManager(**kwargs)
