// Request Cache Service with TTL and Invalidation
import crypto from 'crypto';

export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
  key: string;
  tags: string[];
}

export interface CacheOptions {
  ttl?: number; // Time to live in milliseconds (default: 5 minutes)
  tags?: string[]; // Tags for cache invalidation
  maxSize?: number; // Maximum cache size in MB (default: 50MB)
  enabled?: boolean; // Enable/disable caching (default: true)
}

export interface CacheStats {
  hits: number;
  misses: number;
  size: number;
  entries: number;
  hitRate: number;
}

export class CacheService {
  private cache: Map<string, CacheEntry<any>>;
  private stats: { hits: number; misses: number };
  private maxSize: number; // in bytes
  private currentSize: number;
  private enabled: boolean;
  private defaultTTL: number;

  constructor(options: CacheOptions = {}) {
    this.cache = new Map();
    this.stats = { hits: 0, misses: 0 };
    this.maxSize = (options.maxSize || 50) * 1024 * 1024; // Convert MB to bytes
    this.currentSize = 0;
    this.enabled = options.enabled !== false;
    this.defaultTTL = options.ttl || 5 * 60 * 1000; // 5 minutes default
  }

  /**
   * Generate cache key from request data
   */
  generateKey(
    url: string,
    method: string,
    params?: Record<string, any>,
    headers?: Record<string, string>,
    body?: any
  ): string {
    const data = {
      url,
      method: method.toUpperCase(),
      params: params || {},
      // Only include cache-relevant headers
      headers: this.filterHeaders(headers || {}),
      body: body || null,
    };

    const hash = crypto
      .createHash('sha256')
      .update(JSON.stringify(data))
      .digest('hex');

    return hash;
  }

  /**
   * Filter headers to only include cache-relevant ones
   */
  private filterHeaders(headers: Record<string, string>): Record<string, string> {
    const cacheRelevantHeaders = [
      'accept',
      'accept-language',
      'authorization',
      'content-type',
    ];

    const filtered: Record<string, string> = {};
    Object.entries(headers).forEach(([key, value]) => {
      if (cacheRelevantHeaders.includes(key.toLowerCase())) {
        filtered[key.toLowerCase()] = value;
      }
    });

    return filtered;
  }

  /**
   * Get cached data
   */
  get<T>(key: string): T | null {
    if (!this.enabled) {
      return null;
    }

    const entry = this.cache.get(key);

    if (!entry) {
      this.stats.misses++;
      return null;
    }

    // Check if expired
    const now = Date.now();
    if (now - entry.timestamp > entry.ttl) {
      this.delete(key);
      this.stats.misses++;
      return null;
    }

    this.stats.hits++;
    return entry.data as T;
  }

  /**
   * Set cached data
   */
  set<T>(key: string, data: T, options: CacheOptions = {}): boolean {
    if (!this.enabled) {
      return false;
    }

    const ttl = options.ttl || this.defaultTTL;
    const tags = options.tags || [];

    // Calculate size
    const dataSize = this.calculateSize(data);

    // Check if adding this entry would exceed max size
    if (this.currentSize + dataSize > this.maxSize) {
      this.evictLRU(dataSize);
    }

    // Delete old entry if exists
    if (this.cache.has(key)) {
      this.delete(key);
    }

    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttl,
      key,
      tags,
    };

    this.cache.set(key, entry);
    this.currentSize += dataSize;

    return true;
  }

  /**
   * Delete cached entry
   */
  delete(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) {
      return false;
    }

    const size = this.calculateSize(entry.data);
    this.currentSize -= size;
    this.cache.delete(key);

    return true;
  }

  /**
   * Clear all cache
   */
  clear(): void {
    this.cache.clear();
    this.currentSize = 0;
    this.stats = { hits: 0, misses: 0 };
  }

  /**
   * Invalidate cache by tags
   */
  invalidateByTags(tags: string[]): number {
    let count = 0;
    const keysToDelete: string[] = [];

    this.cache.forEach((entry, key) => {
      if (entry.tags.some(tag => tags.includes(tag))) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => {
      if (this.delete(key)) {
        count++;
      }
    });

    return count;
  }

  /**
   * Invalidate cache by URL pattern
   */
  invalidateByPattern(pattern: RegExp): number {
    let count = 0;
    const keysToDelete: string[] = [];

    this.cache.forEach((entry, key) => {
      // We can't directly match the URL from the hash, so we store it in tags
      const urlTag = entry.tags.find(tag => tag.startsWith('url:'));
      if (urlTag && pattern.test(urlTag.substring(4))) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => {
      if (this.delete(key)) {
        count++;
      }
    });

    return count;
  }

  /**
   * Clean expired entries
   */
  cleanExpired(): number {
    let count = 0;
    const now = Date.now();
    const keysToDelete: string[] = [];

    this.cache.forEach((entry, key) => {
      if (now - entry.timestamp > entry.ttl) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => {
      if (this.delete(key)) {
        count++;
      }
    });

    return count;
  }

  /**
   * Evict least recently used entries to make space
   */
  private evictLRU(requiredSpace: number): void {
    // Sort entries by timestamp (oldest first)
    const entries = Array.from(this.cache.entries()).sort(
      (a, b) => a[1].timestamp - b[1].timestamp
    );

    let freedSpace = 0;
    for (const [key, entry] of entries) {
      const size = this.calculateSize(entry.data);
      this.cache.delete(key);
      this.currentSize -= size;
      freedSpace += size;

      if (freedSpace >= requiredSpace) {
        break;
      }
    }
  }

  /**
   * Calculate size of data in bytes
   */
  private calculateSize(data: any): number {
    try {
      const str = JSON.stringify(data);
      return new Blob([str]).size;
    } catch {
      return 0;
    }
  }

  /**
   * Get cache statistics
   */
  getStats(): CacheStats {
    const total = this.stats.hits + this.stats.misses;
    const hitRate = total > 0 ? (this.stats.hits / total) * 100 : 0;

    return {
      hits: this.stats.hits,
      misses: this.stats.misses,
      size: this.currentSize,
      entries: this.cache.size,
      hitRate: Math.round(hitRate * 100) / 100,
    };
  }

  /**
   * Enable caching
   */
  enable(): void {
    this.enabled = true;
  }

  /**
   * Disable caching
   */
  disable(): void {
    this.enabled = false;
  }

  /**
   * Check if caching is enabled
   */
  isEnabled(): boolean {
    return this.enabled;
  }

  /**
   * Set default TTL
   */
  setDefaultTTL(ttl: number): void {
    this.defaultTTL = ttl;
  }

  /**
   * Get default TTL
   */
  getDefaultTTL(): number {
    return this.defaultTTL;
  }

  /**
   * Set max cache size in MB
   */
  setMaxSize(sizeMB: number): void {
    this.maxSize = sizeMB * 1024 * 1024;
    
    // Evict if current size exceeds new max
    if (this.currentSize > this.maxSize) {
      this.evictLRU(this.currentSize - this.maxSize);
    }
  }

  /**
   * Get max cache size in MB
   */
  getMaxSize(): number {
    return this.maxSize / (1024 * 1024);
  }
}

// Singleton instance
let cacheServiceInstance: CacheService | null = null;

export function getCacheService(options?: CacheOptions): CacheService {
  if (!cacheServiceInstance) {
    cacheServiceInstance = new CacheService(options);
  }
  return cacheServiceInstance;
}
