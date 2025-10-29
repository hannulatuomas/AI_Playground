
"""
Unit tests for Cache System.

Tests the caching mechanism for LLM responses and other data including:
- Cache backends (Memory, File)
- Cache entries with TTL
- Cache statistics
- Eviction policies
- Pattern matching
"""

import pytest
from unittest.mock import Mock, patch
import time
import tempfile
from pathlib import Path


# =============================================================================
# Cache Entry Tests
# =============================================================================

@pytest.mark.unit
class TestCacheEntry:
    """Test suite for CacheEntry dataclass."""
    
    def test_cache_entry_creation(self):
        """Test creating a cache entry."""
        from core.cache import CacheEntry
        
        entry = CacheEntry(
            key='test_key',
            value='test_value',
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            ttl=60,
            size_bytes=100,
            metadata={}
        )
        
        assert entry.key == 'test_key'
        assert entry.value == 'test_value'
        assert entry.ttl == 60
    
    def test_cache_entry_is_expired(self):
        """Test cache entry expiration checking."""
        from core.cache import CacheEntry
        
        # Create expired entry
        expired_entry = CacheEntry(
            key='expired',
            value='value',
            created_at=time.time() - 120,  # 2 minutes ago
            accessed_at=time.time(),
            access_count=0,
            ttl=60,  # 1 minute TTL
            size_bytes=100,
            metadata={}
        )
        
        assert expired_entry.is_expired() is True
        
        # Create non-expired entry
        valid_entry = CacheEntry(
            key='valid',
            value='value',
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            ttl=60,
            size_bytes=100,
            metadata={}
        )
        
        assert valid_entry.is_expired() is False
    
    def test_cache_entry_no_ttl(self):
        """Test cache entry with no TTL never expires."""
        from core.cache import CacheEntry
        
        entry = CacheEntry(
            key='no_ttl',
            value='value',
            created_at=time.time() - 1000,  # Long time ago
            accessed_at=time.time(),
            access_count=0,
            ttl=None,  # No TTL
            size_bytes=100,
            metadata={}
        )
        
        assert entry.is_expired() is False
    
    def test_cache_entry_update_access(self):
        """Test updating access statistics."""
        from core.cache import CacheEntry
        
        entry = CacheEntry(
            key='test',
            value='value',
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            ttl=60,
            size_bytes=100,
            metadata={}
        )
        
        initial_accessed_at = entry.accessed_at
        initial_count = entry.access_count
        
        time.sleep(0.01)  # Small delay
        entry.update_access()
        
        assert entry.accessed_at > initial_accessed_at
        assert entry.access_count == initial_count + 1


# =============================================================================
# Memory Cache Backend Tests
# =============================================================================

@pytest.mark.unit
class TestMemoryCacheBackend:
    """Test suite for MemoryCacheBackend."""
    
    @pytest.fixture
    def backend(self):
        """Create a memory cache backend."""
        from core.cache import MemoryCacheBackend
        return MemoryCacheBackend(max_size=10)
    
    def test_backend_initialization(self, backend):
        """Test backend initialization."""
        assert backend.max_size == 10
        assert backend.size() == 0
    
    def test_set_and_get(self, backend):
        """Test setting and getting entries."""
        from core.cache import CacheEntry
        
        entry = CacheEntry(
            key='test',
            value='value',
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            ttl=60,
            size_bytes=100,
            metadata={}
        )
        
        assert backend.set('test', entry) is True
        retrieved = backend.get('test')
        
        assert retrieved is not None
        assert retrieved.key == 'test'
        assert retrieved.value == 'value'
    
    def test_lru_eviction(self, backend):
        """Test LRU eviction policy."""
        from core.cache import CacheEntry
        
        # Fill cache beyond max_size
        for i in range(15):
            entry = CacheEntry(
                key=f'key{i}',
                value=f'value{i}',
                created_at=time.time(),
                accessed_at=time.time(),
                access_count=0,
                ttl=60,
                size_bytes=100,
                metadata={}
            )
            backend.set(f'key{i}', entry)
        
        # Should have evicted oldest entries
        assert backend.size() == 10
        # Oldest entries should be gone
        assert backend.get('key0') is None
        assert backend.get('key1') is None
        # Newest entries should exist
        assert backend.get('key14') is not None
    
    def test_delete(self, backend):
        """Test deleting entries."""
        from core.cache import CacheEntry
        
        entry = CacheEntry(
            key='delete_test',
            value='value',
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            ttl=60,
            size_bytes=100,
            metadata={}
        )
        
        backend.set('delete_test', entry)
        assert backend.get('delete_test') is not None
        
        assert backend.delete('delete_test') is True
        assert backend.get('delete_test') is None
    
    def test_clear(self, backend):
        """Test clearing all entries."""
        from core.cache import CacheEntry
        
        for i in range(5):
            entry = CacheEntry(
                key=f'key{i}',
                value=f'value{i}',
                created_at=time.time(),
                accessed_at=time.time(),
                access_count=0,
                ttl=60,
                size_bytes=100,
                metadata={}
            )
            backend.set(f'key{i}', entry)
        
        assert backend.size() == 5
        assert backend.clear() is True
        assert backend.size() == 0
    
    def test_keys_without_pattern(self, backend):
        """Test getting all keys."""
        from core.cache import CacheEntry
        
        for i in range(3):
            entry = CacheEntry(
                key=f'key{i}',
                value=f'value{i}',
                created_at=time.time(),
                accessed_at=time.time(),
                access_count=0,
                ttl=60,
                size_bytes=100,
                metadata={}
            )
            backend.set(f'key{i}', entry)
        
        keys = backend.keys()
        assert len(keys) == 3
        assert 'key0' in keys
        assert 'key1' in keys
        assert 'key2' in keys
    
    def test_keys_with_pattern(self, backend):
        """Test getting keys matching pattern."""
        from core.cache import CacheEntry
        
        for i in range(5):
            entry = CacheEntry(
                key=f'test_{i}',
                value=f'value{i}',
                created_at=time.time(),
                accessed_at=time.time(),
                access_count=0,
                ttl=60,
                size_bytes=100,
                metadata={}
            )
            backend.set(f'test_{i}', entry)
        
        # Add some other keys
        for i in range(2):
            entry = CacheEntry(
                key=f'other_{i}',
                value=f'value{i}',
                created_at=time.time(),
                accessed_at=time.time(),
                access_count=0,
                ttl=60,
                size_bytes=100,
                metadata={}
            )
            backend.set(f'other_{i}', entry)
        
        # Pattern match
        test_keys = backend.keys('test_*')
        assert len(test_keys) == 5


# =============================================================================
# File Cache Backend Tests
# =============================================================================

@pytest.mark.unit
class TestFileCacheBackend:
    """Test suite for FileCacheBackend."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_backend_initialization(self, temp_cache_dir):
        """Test file backend initialization."""
        from core.cache import FileCacheBackend
        
        backend = FileCacheBackend(temp_cache_dir)
        assert backend.cache_dir.exists()
    
    def test_set_and_get(self, temp_cache_dir):
        """Test setting and getting entries from file."""
        from core.cache import FileCacheBackend, CacheEntry
        
        backend = FileCacheBackend(temp_cache_dir)
        
        entry = CacheEntry(
            key='file_test',
            value={'data': 'complex_value'},
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            ttl=60,
            size_bytes=100,
            metadata={'source': 'test'}
        )
        
        assert backend.set('file_test', entry) is True
        retrieved = backend.get('file_test')
        
        assert retrieved is not None
        assert retrieved.key == 'file_test'
        assert retrieved.value == {'data': 'complex_value'}
        assert retrieved.access_count == 1  # Updated on access
    
    def test_persistence(self, temp_cache_dir):
        """Test that cache persists across backend instances."""
        from core.cache import FileCacheBackend, CacheEntry
        
        # Create and populate backend
        backend1 = FileCacheBackend(temp_cache_dir)
        entry = CacheEntry(
            key='persist_test',
            value='persistent_value',
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            ttl=60,
            size_bytes=100,
            metadata={}
        )
        backend1.set('persist_test', entry)
        
        # Create new backend instance pointing to same dir
        backend2 = FileCacheBackend(temp_cache_dir)
        retrieved = backend2.get('persist_test')
        
        assert retrieved is not None
        assert retrieved.value == 'persistent_value'


# =============================================================================
# Cache Interface Tests
# =============================================================================

@pytest.mark.unit
class TestCache:
    """Test suite for main Cache interface."""
    
    @pytest.fixture
    def cache(self):
        """Create a cache instance for testing."""
        from core.cache import Cache, MemoryCacheBackend
        
        backend = MemoryCacheBackend(max_size=100)
        return Cache(backend=backend, default_ttl=60, enable_stats=True)
    
    def test_initialization(self, cache):
        """Test cache initialization."""
        assert cache is not None
        assert cache.default_ttl == 60
        assert cache.enable_stats is True
    
    def test_set_and_get(self, cache):
        """Test setting and getting cache values."""
        cache.set('key1', 'value1')
        value = cache.get('key1')
        
        assert value == 'value1'
    
    def test_get_nonexistent_key(self, cache):
        """Test getting non-existent key returns None."""
        value = cache.get('nonexistent')
        
        assert value is None
    
    def test_get_with_default(self, cache):
        """Test getting non-existent key returns default value."""
        value = cache.get('nonexistent', default='default_value')
        
        assert value == 'default_value'
    
    def test_cache_expiration(self):
        """Test cache TTL expiration."""
        from core.cache import Cache, MemoryCacheBackend
        
        backend = MemoryCacheBackend(max_size=10)
        short_ttl_cache = Cache(backend=backend, default_ttl=1)
        
        short_ttl_cache.set('expire_test', 'value')
        
        # Wait for expiration
        time.sleep(1.2)
        
        value = short_ttl_cache.get('expire_test')
        
        # Should be None after expiration
        assert value is None
    
    def test_cache_max_size(self):
        """Test cache respects max size."""
        from core.cache import Cache, MemoryCacheBackend
        
        backend = MemoryCacheBackend(max_size=5)
        small_cache = Cache(backend=backend, default_ttl=60)
        
        # Add more items than max_size
        for i in range(10):
            small_cache.set(f'key{i}', f'value{i}')
        
        # Cache size should not exceed max_size
        assert small_cache.size() <= 5
    
    def test_clear_cache(self, cache):
        """Test clearing all cache entries."""
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        cache.clear()
        
        assert cache.get('key1') is None
        assert cache.get('key2') is None
        assert cache.size() == 0
    
    def test_delete_key(self, cache):
        """Test deleting specific key."""
        cache.set('delete_test', 'value')
        assert cache.get('delete_test') == 'value'
        
        cache.delete('delete_test')
        
        assert cache.get('delete_test') is None
    
    def test_has_key(self, cache):
        """Test checking if key exists."""
        cache.set('exists', 'value')
        
        assert cache.has('exists') is True
        assert cache.has('nonexistent') is False
    
    def test_cache_size(self, cache):
        """Test getting cache size."""
        cache.clear()
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        assert cache.size() == 2
    
    def test_cache_statistics(self, cache):
        """Test cache statistics tracking."""
        cache.clear()
        
        # Test hits and misses
        cache.set('test', 'value')
        cache.get('test')  # Hit
        cache.get('nonexistent')  # Miss
        
        stats = cache.get_stats()
        assert stats['hits'] >= 1
        assert stats['misses'] >= 1
        assert stats['sets'] >= 1
    
    def test_set_with_custom_ttl(self, cache):
        """Test setting entry with custom TTL."""
        cache.set('custom_ttl', 'value', ttl=120)
        
        # Value should be there
        assert cache.get('custom_ttl') == 'value'
    
    def test_set_complex_value(self, cache):
        """Test setting complex Python objects."""
        complex_value = {
            'nested': {
                'data': [1, 2, 3],
                'info': 'test'
            }
        }
        
        cache.set('complex', complex_value)
        retrieved = cache.get('complex')
        
        assert retrieved == complex_value
    
    def test_cache_hit_rate(self, cache):
        """Test calculating cache hit rate."""
        cache.clear()
        
        cache.set('test1', 'value1')
        cache.set('test2', 'value2')
        
        # 2 hits
        cache.get('test1')
        cache.get('test2')
        
        # 1 miss
        cache.get('nonexistent')
        
        hit_rate = cache.get_hit_rate()
        # Hit rate should be around 66% (2/3)
        assert hit_rate > 0.6 and hit_rate < 0.7
