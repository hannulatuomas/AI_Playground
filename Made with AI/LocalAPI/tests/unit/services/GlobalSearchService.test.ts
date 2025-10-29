/**
 * GlobalSearchService Unit Tests
 * Tests global search functionality across all entities
 */

import { GlobalSearchService, type SearchableEntity, type SearchFilters } from '../../../src/main/services/GlobalSearchService';

describe('GlobalSearchService', () => {
  let service: GlobalSearchService;

  beforeEach(() => {
    service = new GlobalSearchService();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Search', () => {
    it('should return empty results for empty query', async () => {
      const results = await service.search('');
      expect(results).toEqual([]);
    });

    it('should return empty results for whitespace query', async () => {
      const results = await service.search('   ');
      expect(results).toEqual([]);
    });

    it('should search with query', async () => {
      // Register mock indexer
      service.registerIndexer('request', async () => [
        {
          id: 'req-1',
          type: 'request',
          title: 'Get Users API',
          description: 'Fetch all users',
        },
      ]);

      const results = await service.search('users');
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].entity.title).toContain('Users');
    });

    it('should perform case-insensitive search', async () => {
      service.registerIndexer('request', async () => [
        {
          id: 'req-1',
          type: 'request',
          title: 'Test Request',
        },
      ]);

      const lowerResults = await service.search('test');
      const upperResults = await service.search('TEST');
      
      expect(lowerResults.length).toBe(upperResults.length);
    });
  });

  describe('Entity Indexing', () => {
    it('should register indexer for entity type', () => {
      const mockIndexer = jest.fn().mockResolvedValue([]);
      
      service.registerIndexer('request', mockIndexer);
      
      // Indexer should be registered (will be called on search)
      expect(() => service.registerIndexer('request', mockIndexer)).not.toThrow();
    });

    it('should register multiple entity types', () => {
      service.registerIndexer('request', async () => []);
      service.registerIndexer('collection', async () => []);
      service.registerIndexer('environment', async () => []);
      
      // All should be registered without error
      expect(service).toBeDefined();
    });

    it('should call indexer on search', async () => {
      const mockIndexer = jest.fn().mockResolvedValue([
        {
          id: 'req-1',
          type: 'request',
          title: 'Test',
        },
      ]);
      
      service.registerIndexer('request', mockIndexer);
      await service.search('test');
      
      expect(mockIndexer).toHaveBeenCalled();
    });
  });

  describe('Search Filters', () => {
    beforeEach(() => {
      service.registerIndexer('request', async () => [
        { id: 'req-1', type: 'request', title: 'API Request' },
      ]);
      service.registerIndexer('collection', async () => [
        { id: 'col-1', type: 'collection', title: 'API Collection' },
      ]);
    });

    it('should filter by entity type', async () => {
      const filters: SearchFilters = { types: ['request'] };
      const results = await service.search('api', filters);
      
      expect(results.every(r => r.entity.type === 'request')).toBe(true);
    });

    it('should support multiple type filters', async () => {
      const filters: SearchFilters = { types: ['request', 'collection'] };
      const results = await service.search('api', filters);
      
      expect(results.length).toBeGreaterThan(0);
    });

    it('should filter by tags', async () => {
      service.registerIndexer('request', async () => [
        { id: 'req-1', type: 'request', title: 'Test', tags: ['important'] },
      ]);

      const filters: SearchFilters = { tags: ['important'] };
      const results = await service.search('test', filters);
      
      expect(results.length).toBeGreaterThan(0);
    });
  });

  describe('Search Results', () => {
    it('should return results with scores', async () => {
      service.registerIndexer('request', async () => [
        { id: 'req-1', type: 'request', title: 'Test Request' },
      ]);

      const results = await service.search('test');
      
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].score).toBeGreaterThan(0);
    });

    it('should return results sorted by score', async () => {
      service.registerIndexer('request', async () => [
        { id: 'req-1', type: 'request', title: 'Test' },
        { id: 'req-2', type: 'request', title: 'Test Request' },
        { id: 'req-3', type: 'request', title: 'Some other test thing' },
      ]);

      const results = await service.search('test');
      
      // Results should be sorted by score descending
      for (let i = 0; i < results.length - 1; i++) {
        expect(results[i].score).toBeGreaterThanOrEqual(results[i + 1].score);
      }
    });

    it('should include match information', async () => {
      service.registerIndexer('request', async () => [
        { id: 'req-1', type: 'request', title: 'User API', description: 'Get users' },
      ]);

      const results = await service.search('user');
      
      expect(results[0].matches).toBeDefined();
      expect(Array.isArray(results[0].matches)).toBe(true);
    });

    it('should include highlights', async () => {
      service.registerIndexer('request', async () => [
        { id: 'req-1', type: 'request', title: 'Test Request' },
      ]);

      const results = await service.search('test');
      
      expect(results[0].highlights).toBeDefined();
      expect(Array.isArray(results[0].highlights)).toBe(true);
    });
  });

  describe('Search History', () => {
    it('should track search history', async () => {
      await service.search('query1');
      await service.search('query2');
      
      const history = service.getSearchHistory();
      
      expect(history).toContain('query1');
      expect(history).toContain('query2');
    });

    it('should limit history size', async () => {
      // Search many times
      for (let i = 0; i < 60; i++) {
        await service.search(`query${i}`);
      }
      
      const history = service.getSearchHistory();
      expect(history.length).toBeLessThanOrEqual(50); // Max 50
    });

    it('should clear search history', () => {
      service.clearSearchHistory();
      
      const history = service.getSearchHistory();
      expect(history).toHaveLength(0);
    });

    it('should not add empty queries to history', async () => {
      await service.search('');
      
      const history = service.getSearchHistory();
      expect(history).toHaveLength(0);
    });
  });

  describe('Search with Suggestions', () => {
    it('should return results and suggestions', async () => {
      service.registerIndexer('request', async () => [
        { id: 'req-1', type: 'request', title: 'User API' },
      ]);

      const { results, suggestions } = await service.searchWithSuggestions('user');
      
      expect(results).toBeDefined();
      expect(suggestions).toBeDefined();
      expect(Array.isArray(results)).toBe(true);
      expect(Array.isArray(suggestions)).toBe(true);
    });

    it('should provide search suggestions', async () => {
      await service.search('user');
      await service.search('user api');
      
      const { suggestions } = await service.searchWithSuggestions('us');
      
      expect(suggestions.length).toBeGreaterThan(0);
    });
  });

  describe('Entity Types', () => {
    it('should search across all entity types', async () => {
      service.registerIndexer('request', async () => [
        { id: 'req-1', type: 'request', title: 'API Request' },
      ]);
      service.registerIndexer('collection', async () => [
        { id: 'col-1', type: 'collection', title: 'API Collection' },
      ]);
      service.registerIndexer('environment', async () => [
        { id: 'env-1', type: 'environment', title: 'API Environment' },
      ]);

      const results = await service.search('api');
      
      const types = new Set(results.map(r => r.entity.type));
      expect(types.size).toBeGreaterThan(1);
    });

    it('should support all entity types', () => {
      const types: SearchableEntity['type'][] = [
        'request',
        'collection',
        'environment',
        'variable',
        'history',
        'favorite',
        'tab',
      ];

      types.forEach(type => {
        expect(() => service.registerIndexer(type, async () => [])).not.toThrow();
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle special characters', async () => {
      service.registerIndexer('request', async () => [
        { id: 'req-1', type: 'request', title: 'Test @ API' },
      ]);

      const results = await service.search('@');
      expect(Array.isArray(results)).toBe(true);
    });

    it('should handle very long queries', async () => {
      const longQuery = 'a'.repeat(1000);
      const results = await service.search(longQuery);
      
      expect(Array.isArray(results)).toBe(true);
    });

    it('should handle unicode characters', async () => {
      service.registerIndexer('request', async () => [
        { id: 'req-1', type: 'request', title: 'Test 日本語' },
      ]);

      const results = await service.search('日本語');
      expect(results.length).toBeGreaterThan(0);
    });

    it('should handle indexer errors gracefully', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      
      service.registerIndexer('request', async () => {
        throw new Error('Indexer error');
      });

      // Should not throw, just log error
      const results = await service.search('test');
      expect(results).toEqual([]);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining('Error indexing'),
        expect.any(Error)
      );
      
      consoleErrorSpy.mockRestore();
    });
  });

  describe('Fuzzy Matching', () => {
    it('should find partial matches', async () => {
      service.registerIndexer('request', async () => [
        { id: 'req-1', type: 'request', title: 'User Profile API' },
      ]);

      const results = await service.search('prof');
      expect(results.length).toBeGreaterThan(0);
    });

    it('should match in description', async () => {
      service.registerIndexer('request', async () => [
        {
          id: 'req-1',
          type: 'request',
          title: 'API',
          description: 'Get user profile data',
        },
      ]);

      const results = await service.search('profile');
      expect(results.length).toBeGreaterThan(0);
    });

    it('should match in content', async () => {
      service.registerIndexer('request', async () => [
        {
          id: 'req-1',
          type: 'request',
          title: 'API',
          content: 'This endpoint returns user data',
        },
      ]);

      const results = await service.search('endpoint');
      expect(results.length).toBeGreaterThan(0);
    });
  });
});
