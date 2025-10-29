/**
 * GlobalSearchService - Search Across All Entities
 * 
 * Features:
 * - Search requests, collections, environments, variables, history
 * - Fuzzy matching
 * - Category filtering
 * - Result ranking
 * - Search history
 */

export interface SearchableEntity {
  id: string;
  type: 'request' | 'collection' | 'environment' | 'variable' | 'history' | 'favorite' | 'tab';
  title: string;
  description?: string;
  content?: string;
  metadata?: Record<string, any>;
  tags?: string[];
  path?: string; // Breadcrumb path
  lastModified?: number;
  lastAccessed?: number;
}

export interface SearchResult {
  entity: SearchableEntity;
  score: number;
  matches: string[]; // What matched (title, description, content, etc.)
  highlights: string[]; // Highlighted snippets
}

export interface SearchFilters {
  types?: SearchableEntity['type'][];
  tags?: string[];
  dateFrom?: number;
  dateTo?: number;
  collections?: string[];
}

export class GlobalSearchService {
  private searchHistory: string[];
  private maxHistorySize: number;
  private indexUpdateCallbacks: Map<string, () => Promise<SearchableEntity[]>>;

  constructor() {
    this.searchHistory = [];
    this.maxHistorySize = 50;
    this.indexUpdateCallbacks = new Map();
  }

  /**
   * Register a callback to get entities of a specific type
   */
  registerIndexer(type: SearchableEntity['type'], callback: () => Promise<SearchableEntity[]>): void {
    this.indexUpdateCallbacks.set(type, callback);
  }

  /**
   * Search across all indexed entities
   */
  async search(query: string, filters?: SearchFilters): Promise<SearchResult[]> {
    if (!query.trim()) {
      return [];
    }

    this.addToHistory(query);

    // Get all entities
    const allEntities = await this.getAllEntities(filters);

    // Search and score
    const results: SearchResult[] = [];
    const lowerQuery = query.toLowerCase();

    for (const entity of allEntities) {
      const result = this.matchEntity(entity, lowerQuery);
      if (result.score > 0) {
        results.push(result);
      }
    }

    // Sort by score (descending)
    return results.sort((a, b) => b.score - a.score);
  }

  /**
   * Search with suggestions
   */
  async searchWithSuggestions(query: string): Promise<{ results: SearchResult[]; suggestions: string[] }> {
    const results = await this.search(query);
    const suggestions = this.generateSuggestions(query);

    return { results, suggestions };
  }

  /**
   * Get search history
   */
  getSearchHistory(): string[] {
    return [...this.searchHistory];
  }

  /**
   * Clear search history
   */
  clearSearchHistory(): void {
    this.searchHistory = [];
  }

  /**
   * Get all entities based on filters
   */
  private async getAllEntities(filters?: SearchFilters): Promise<SearchableEntity[]> {
    const entities: SearchableEntity[] = [];

    // Get entities from registered indexers
    for (const [type, callback] of this.indexUpdateCallbacks.entries()) {
      // Skip if filtered out
      if (filters?.types && !filters.types.includes(type as SearchableEntity['type'])) {
        continue;
      }

      try {
        const typeEntities = await callback();
        entities.push(...typeEntities);
      } catch (error) {
        console.error(`Error indexing ${type}:`, error);
      }
    }

    // Apply additional filters
    return this.applyFilters(entities, filters);
  }

  /**
   * Apply filters to entities
   */
  private applyFilters(entities: SearchableEntity[], filters?: SearchFilters): SearchableEntity[] {
    if (!filters) return entities;

    let filtered = entities;

    // Filter by tags
    if (filters.tags && filters.tags.length > 0) {
      filtered = filtered.filter(entity =>
        entity.tags?.some(tag => filters.tags!.includes(tag))
      );
    }

    // Filter by date range
    if (filters.dateFrom || filters.dateTo) {
      filtered = filtered.filter(entity => {
        const date = entity.lastModified || entity.lastAccessed || 0;
        if (filters.dateFrom && date < filters.dateFrom) return false;
        if (filters.dateTo && date > filters.dateTo) return false;
        return true;
      });
    }

    // Filter by collections
    if (filters.collections && filters.collections.length > 0) {
      filtered = filtered.filter(entity =>
        filters.collections!.some(col => entity.path?.includes(col))
      );
    }

    return filtered;
  }

  /**
   * Match entity against query and calculate score
   */
  private matchEntity(entity: SearchableEntity, lowerQuery: string): SearchResult {
    let score = 0;
    const matches: string[] = [];
    const highlights: string[] = [];

    // Title match (highest priority)
    const lowerTitle = entity.title.toLowerCase();
    if (lowerTitle === lowerQuery) {
      score += 100;
      matches.push('title');
      highlights.push(this.highlightMatch(entity.title, lowerQuery));
    } else if (lowerTitle.startsWith(lowerQuery)) {
      score += 50;
      matches.push('title');
      highlights.push(this.highlightMatch(entity.title, lowerQuery));
    } else if (lowerTitle.includes(lowerQuery)) {
      score += 25;
      matches.push('title');
      highlights.push(this.highlightMatch(entity.title, lowerQuery));
    }

    // Description match
    if (entity.description) {
      const lowerDesc = entity.description.toLowerCase();
      if (lowerDesc.includes(lowerQuery)) {
        score += 15;
        matches.push('description');
        highlights.push(this.getSnippet(entity.description, lowerQuery));
      }
    }

    // Content match
    if (entity.content) {
      const lowerContent = entity.content.toLowerCase();
      if (lowerContent.includes(lowerQuery)) {
        score += 10;
        matches.push('content');
        highlights.push(this.getSnippet(entity.content, lowerQuery));
      }
    }

    // Tags match
    if (entity.tags) {
      for (const tag of entity.tags) {
        if (tag.toLowerCase().includes(lowerQuery)) {
          score += 20;
          matches.push('tag');
          highlights.push(tag);
        }
      }
    }

    // Path match (breadcrumb)
    if (entity.path) {
      const lowerPath = entity.path.toLowerCase();
      if (lowerPath.includes(lowerQuery)) {
        score += 5;
        matches.push('path');
      }
    }

    // Metadata match
    if (entity.metadata) {
      for (const [key, value] of Object.entries(entity.metadata)) {
        const strValue = String(value).toLowerCase();
        if (strValue.includes(lowerQuery)) {
          score += 3;
          matches.push(`metadata.${key}`);
        }
      }
    }

    // Fuzzy match bonus (consecutive characters)
    const fuzzyScore = this.calculateFuzzyScore(entity.title, lowerQuery);
    score += fuzzyScore;

    // Recency bonus
    if (entity.lastAccessed) {
      const daysSinceAccess = (Date.now() - entity.lastAccessed) / (1000 * 60 * 60 * 24);
      if (daysSinceAccess < 1) score += 10;
      else if (daysSinceAccess < 7) score += 5;
      else if (daysSinceAccess < 30) score += 2;
    }

    return {
      entity,
      score,
      matches: [...new Set(matches)],
      highlights: highlights.slice(0, 3), // Limit to 3 highlights
    };
  }

  /**
   * Calculate fuzzy match score
   */
  private calculateFuzzyScore(text: string, query: string): number {
    let score = 0;
    let queryIndex = 0;
    const lowerText = text.toLowerCase();

    for (let i = 0; i < lowerText.length && queryIndex < query.length; i++) {
      if (lowerText[i] === query[queryIndex]) {
        score += 2;
        queryIndex++;
      }
    }

    return queryIndex === query.length ? score : 0;
  }

  /**
   * Highlight matching text
   */
  private highlightMatch(text: string, query: string): string {
    const lowerText = text.toLowerCase();
    const index = lowerText.indexOf(query);

    if (index === -1) return text;

    return (
      text.substring(0, index) +
      '<mark>' +
      text.substring(index, index + query.length) +
      '</mark>' +
      text.substring(index + query.length)
    );
  }

  /**
   * Get snippet with context around match
   */
  private getSnippet(text: string, query: string, contextLength: number = 50): string {
    const lowerText = text.toLowerCase();
    const index = lowerText.indexOf(query);

    if (index === -1) return text.substring(0, 100) + '...';

    const start = Math.max(0, index - contextLength);
    const end = Math.min(text.length, index + query.length + contextLength);

    let snippet = text.substring(start, end);
    if (start > 0) snippet = '...' + snippet;
    if (end < text.length) snippet = snippet + '...';

    return this.highlightMatch(snippet, query);
  }

  /**
   * Generate search suggestions
   */
  private generateSuggestions(query: string): string[] {
    const suggestions: string[] = [];

    // Add recent searches that match
    const lowerQuery = query.toLowerCase();
    for (const historyItem of this.searchHistory) {
      if (historyItem.toLowerCase().includes(lowerQuery) && historyItem !== query) {
        suggestions.push(historyItem);
      }
    }

    // Common search patterns
    const patterns = [
      'GET ',
      'POST ',
      'PUT ',
      'DELETE ',
      'PATCH ',
      '/api/',
      'auth',
      'user',
      'test',
      'prod',
    ];

    for (const pattern of patterns) {
      if (pattern.toLowerCase().startsWith(lowerQuery) || lowerQuery.includes(pattern.toLowerCase())) {
        suggestions.push(pattern);
      }
    }

    return [...new Set(suggestions)].slice(0, 5);
  }

  /**
   * Add query to search history
   */
  private addToHistory(query: string): void {
    // Remove if already exists
    this.searchHistory = this.searchHistory.filter(q => q !== query);

    // Add to beginning
    this.searchHistory.unshift(query);

    // Limit size
    if (this.searchHistory.length > this.maxHistorySize) {
      this.searchHistory.pop();
    }
  }

  /**
   * Get search statistics
   */
  getStatistics(): { totalQueries: number; uniqueQueries: number; topQueries: string[] } {
    const queryCounts = new Map<string, number>();

    for (const query of this.searchHistory) {
      queryCounts.set(query, (queryCounts.get(query) || 0) + 1);
    }

    const topQueries = Array.from(queryCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([query]) => query);

    return {
      totalQueries: this.searchHistory.length,
      uniqueQueries: queryCounts.size,
      topQueries,
    };
  }
}
