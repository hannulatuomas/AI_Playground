// Tests for CacheService
import { CacheService } from '../src/main/services/CacheService';

describe('CacheService', () => {
  let cacheService: CacheService;

  beforeEach(() => {
    cacheService = new CacheService({
      ttl: 1000, // 1 second for testing
      maxSize: 1, // 1 MB
      enabled: true,
    });
  });

  afterEach(() => {
    cacheService.clear();
  });

  describe('Basic Operations', () => {
    test('should generate consistent cache keys', () => {
      const key1 = cacheService.generateKey('https://api.example.com/users', 'GET');
      const key2 = cacheService.generateKey('https://api.example.com/users', 'GET');
      expect(key1).toBe(key2);
    });

    test('should generate different keys for different URLs', () => {
      const key1 = cacheService.generateKey('https://api.example.com/users', 'GET');
      const key2 = cacheService.generateKey('https://api.example.com/posts', 'GET');
      expect(key1).not.toBe(key2);
    });

    test('should generate different keys for different methods', () => {
      const key1 = cacheService.generateKey('https://api.example.com/users', 'GET');
      const key2 = cacheService.generateKey('https://api.example.com/users', 'POST');
      expect(key1).not.toBe(key2);
    });

    test('should set and get cached data', () => {
      const key = cacheService.generateKey('https://api.example.com/users', 'GET');
      const data = { users: [{ id: 1, name: 'John' }] };

      cacheService.set(key, data);
      const cached = cacheService.get(key);

      expect(cached).toEqual(data);
    });

    test('should return null for non-existent keys', () => {
      const key = cacheService.generateKey('https://api.example.com/nonexistent', 'GET');
      const cached = cacheService.get(key);

      expect(cached).toBeNull();
    });

    test('should delete cached entries', () => {
      const key = cacheService.generateKey('https://api.example.com/users', 'GET');
      const data = { users: [] };

      cacheService.set(key, data);
      expect(cacheService.get(key)).toEqual(data);

      cacheService.delete(key);
      expect(cacheService.get(key)).toBeNull();
    });

    test('should clear all cache', () => {
      const key1 = cacheService.generateKey('https://api.example.com/users', 'GET');
      const key2 = cacheService.generateKey('https://api.example.com/posts', 'GET');

      cacheService.set(key1, { users: [] });
      cacheService.set(key2, { posts: [] });

      cacheService.clear();

      expect(cacheService.get(key1)).toBeNull();
      expect(cacheService.get(key2)).toBeNull();
    });
  });

  describe('TTL (Time To Live)', () => {
    test('should expire entries after TTL', async () => {
      const key = cacheService.generateKey('https://api.example.com/users', 'GET');
      const data = { users: [] };

      cacheService.set(key, data, { ttl: 100 }); // 100ms TTL

      // Should be available immediately
      expect(cacheService.get(key)).toEqual(data);

      // Wait for expiration
      await new Promise(resolve => setTimeout(resolve, 150));

      // Should be expired
      expect(cacheService.get(key)).toBeNull();
    });

    test('should use default TTL when not specified', async () => {
      const key = cacheService.generateKey('https://api.example.com/users', 'GET');
      const data = { users: [] };

      cacheService.set(key, data); // Use default TTL (1000ms)

      // Should be available immediately
      expect(cacheService.get(key)).toEqual(data);

      // Wait but not past default TTL
      await new Promise(resolve => setTimeout(resolve, 500));
      expect(cacheService.get(key)).toEqual(data);

      // Wait past default TTL
      await new Promise(resolve => setTimeout(resolve, 600));
      expect(cacheService.get(key)).toBeNull();
    });

    test('should clean expired entries', async () => {
      const key1 = cacheService.generateKey('https://api.example.com/users', 'GET');
      const key2 = cacheService.generateKey('https://api.example.com/posts', 'GET');

      cacheService.set(key1, { users: [] }, { ttl: 100 });
      cacheService.set(key2, { posts: [] }, { ttl: 2000 });

      await new Promise(resolve => setTimeout(resolve, 150));

      const cleaned = cacheService.cleanExpired();
      expect(cleaned).toBe(1); // Only key1 should be cleaned

      expect(cacheService.get(key1)).toBeNull();
      expect(cacheService.get(key2)).toEqual({ posts: [] });
    });
  });

  describe('Cache Tags', () => {
    test('should invalidate cache by tags', () => {
      const key1 = cacheService.generateKey('https://api.example.com/users/1', 'GET');
      const key2 = cacheService.generateKey('https://api.example.com/users/2', 'GET');
      const key3 = cacheService.generateKey('https://api.example.com/posts/1', 'GET');

      cacheService.set(key1, { user: { id: 1 } }, { tags: ['users', 'user:1'] });
      cacheService.set(key2, { user: { id: 2 } }, { tags: ['users', 'user:2'] });
      cacheService.set(key3, { post: { id: 1 } }, { tags: ['posts', 'post:1'] });

      const invalidated = cacheService.invalidateByTags(['users']);
      expect(invalidated).toBe(2);

      expect(cacheService.get(key1)).toBeNull();
      expect(cacheService.get(key2)).toBeNull();
      expect(cacheService.get(key3)).toEqual({ post: { id: 1 } });
    });

    test('should invalidate cache by URL pattern', () => {
      const key1 = cacheService.generateKey('https://api.example.com/users/1', 'GET');
      const key2 = cacheService.generateKey('https://api.example.com/users/2', 'GET');
      const key3 = cacheService.generateKey('https://api.example.com/posts/1', 'GET');

      cacheService.set(key1, { user: { id: 1 } }, { tags: ['url:https://api.example.com/users/1'] });
      cacheService.set(key2, { user: { id: 2 } }, { tags: ['url:https://api.example.com/users/2'] });
      cacheService.set(key3, { post: { id: 1 } }, { tags: ['url:https://api.example.com/posts/1'] });

      const invalidated = cacheService.invalidateByPattern(/users/);
      expect(invalidated).toBe(2);

      expect(cacheService.get(key1)).toBeNull();
      expect(cacheService.get(key2)).toBeNull();
      expect(cacheService.get(key3)).toEqual({ post: { id: 1 } });
    });
  });

  describe('Cache Statistics', () => {
    test('should track cache hits and misses', () => {
      const key = cacheService.generateKey('https://api.example.com/users', 'GET');
      const data = { users: [] };

      // Miss
      cacheService.get(key);
      let stats = cacheService.getStats();
      expect(stats.hits).toBe(0);
      expect(stats.misses).toBe(1);

      // Set and hit
      cacheService.set(key, data);
      cacheService.get(key);
      stats = cacheService.getStats();
      expect(stats.hits).toBe(1);
      expect(stats.misses).toBe(1);

      // Another hit
      cacheService.get(key);
      stats = cacheService.getStats();
      expect(stats.hits).toBe(2);
      expect(stats.misses).toBe(1);
    });

    test('should calculate hit rate correctly', () => {
      const key = cacheService.generateKey('https://api.example.com/users', 'GET');
      const data = { users: [] };

      cacheService.set(key, data);

      // 3 hits, 1 miss = 75% hit rate
      cacheService.get(key);
      cacheService.get(key);
      cacheService.get(key);
      cacheService.get('nonexistent');

      const stats = cacheService.getStats();
      expect(stats.hitRate).toBe(75);
    });

    test('should track cache size', () => {
      const key = cacheService.generateKey('https://api.example.com/users', 'GET');
      const data = { users: [{ id: 1, name: 'John Doe' }] };

      cacheService.set(key, data);
      const stats = cacheService.getStats();

      expect(stats.entries).toBe(1);
      expect(stats.size).toBeGreaterThan(0);
    });
  });

  describe('Cache Size Management', () => {
    test('should evict old entries when max size exceeded', () => {
      // Create a small cache
      const smallCache = new CacheService({ maxSize: 0.001 }); // Very small cache

      const key1 = smallCache.generateKey('https://api.example.com/1', 'GET');
      const key2 = smallCache.generateKey('https://api.example.com/2', 'GET');
      const key3 = smallCache.generateKey('https://api.example.com/3', 'GET');

      const largeData = { data: 'x'.repeat(1000) }; // ~1KB

      smallCache.set(key1, largeData);
      smallCache.set(key2, largeData);
      smallCache.set(key3, largeData); // This should trigger eviction

      // First entry should be evicted (LRU)
      expect(smallCache.get(key1)).toBeNull();
    });
  });

  describe('Enable/Disable', () => {
    test('should not cache when disabled', () => {
      cacheService.disable();

      const key = cacheService.generateKey('https://api.example.com/users', 'GET');
      const data = { users: [] };

      const result = cacheService.set(key, data);
      expect(result).toBe(false);
      expect(cacheService.get(key)).toBeNull();
    });

    test('should cache when enabled', () => {
      cacheService.enable();

      const key = cacheService.generateKey('https://api.example.com/users', 'GET');
      const data = { users: [] };

      const result = cacheService.set(key, data);
      expect(result).toBe(true);
      expect(cacheService.get(key)).toEqual(data);
    });

    test('should check enabled status', () => {
      expect(cacheService.isEnabled()).toBe(true);

      cacheService.disable();
      expect(cacheService.isEnabled()).toBe(false);

      cacheService.enable();
      expect(cacheService.isEnabled()).toBe(true);
    });
  });

  describe('Configuration', () => {
    test('should set and get default TTL', () => {
      cacheService.setDefaultTTL(5000);
      expect(cacheService.getDefaultTTL()).toBe(5000);
    });

    test('should set and get max size', () => {
      cacheService.setMaxSize(100);
      expect(cacheService.getMaxSize()).toBe(100);
    });
  });
});
