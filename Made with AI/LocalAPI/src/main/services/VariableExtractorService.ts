// Variable Extractor Service for LocalAPI
// Handles extraction of variables from responses (JSON, XML, Headers)

import * as xml2js from 'xml2js';
import type { Variable, VariableScope, Response } from '../../types/models';

// Use require for jsonpath to ensure compatibility
const jsonpath = require('jsonpath');

export interface ExtractionRule {
  id: string;
  name: string;
  enabled: boolean;
  source: 'body' | 'header';
  extractionType: 'jsonpath' | 'xpath' | 'regex' | 'header';
  pattern: string;
  variableName: string;
  scope: VariableScope;
  description?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ExtractionResult {
  variableName: string;
  value: any;
  scope: VariableScope;
  source: string;
  path: string;
  success: boolean;
  error?: string;
}

export interface VariableHistory {
  id: string;
  variableName: string;
  oldValue: any;
  newValue: any;
  scope: VariableScope;
  source: string;
  timestamp: Date;
  requestId?: string;
}

export class VariableExtractorService {
  private extractionRules: Map<string, ExtractionRule> = new Map();
  private variableHistory: VariableHistory[] = [];
  private maxHistorySize = 1000;
  private xmlParser: xml2js.Parser;

  constructor() {
    // Reuse single parser instance to avoid memory leaks
    this.xmlParser = new xml2js.Parser({ explicitArray: false });
  }

  /**
   * Extract value from JSON response using JSONPath
   */
  extractFromJSON(
    body: any,
    path: string,
    variableName: string,
    scope: VariableScope = 'global'
  ): ExtractionResult {
    try {
      const parsedBody = typeof body === 'string' ? JSON.parse(body) : body;
      const results = jsonpath.query(parsedBody, path);

      if (results.length === 0) {
        return {
          variableName,
          value: null,
          scope,
          source: 'json',
          path,
          success: false,
          error: 'No matches found for JSONPath expression',
        };
      }

      // Return first result if single value, or array if multiple
      const value = results.length === 1 ? results[0] : results;

      return {
        variableName,
        value,
        scope,
        source: 'json',
        path,
        success: true,
      };
    } catch (error) {
      return {
        variableName,
        value: null,
        scope,
        source: 'json',
        path,
        success: false,
        error: error instanceof Error ? error.message : 'Failed to extract from JSON',
      };
    }
  }

  /**
   * Extract value from XML response using XPath-like syntax
   */
  async extractFromXML(
    body: string,
    xpath: string,
    variableName: string,
    scope: VariableScope = 'global'
  ): Promise<ExtractionResult> {
    try {
      const parsed = await this.xmlParser.parseStringPromise(body);

      // Simple XPath-like navigation (e.g., "root.element.subelement")
      const pathParts = xpath.replace(/^\//, '').split(/[./]/);
      let current: any = parsed;

      for (const part of pathParts) {
        if (part && current) {
          current = current[part];
        }
      }

      if (current === undefined) {
        return {
          variableName,
          value: null,
          scope,
          source: 'xml',
          path: xpath,
          success: false,
          error: 'No matches found for XPath expression',
        };
      }

      return {
        variableName,
        value: current,
        scope,
        source: 'xml',
        path: xpath,
        success: true,
      };
    } catch (error) {
      return {
        variableName,
        value: null,
        scope,
        source: 'xml',
        path: xpath,
        success: false,
        error: error instanceof Error ? error.message : 'Failed to extract from XML',
      };
    }
  }

  /**
   * Extract value from response headers
   */
  extractFromHeader(
    headers: Record<string, string>,
    headerName: string,
    variableName: string,
    scope: VariableScope = 'global'
  ): ExtractionResult {
    try {
      // Case-insensitive header lookup
      const headerKey = Object.keys(headers).find(
        (key) => key.toLowerCase() === headerName.toLowerCase()
      );

      if (!headerKey) {
        return {
          variableName,
          value: null,
          scope,
          source: 'header',
          path: headerName,
          success: false,
          error: `Header "${headerName}" not found`,
        };
      }

      return {
        variableName,
        value: headers[headerKey],
        scope,
        source: 'header',
        path: headerName,
        success: true,
      };
    } catch (error) {
      return {
        variableName,
        value: null,
        scope,
        source: 'header',
        path: headerName,
        success: false,
        error: error instanceof Error ? error.message : 'Failed to extract from header',
      };
    }
  }

  /**
   * Extract value using regex pattern
   */
  extractWithRegex(
    content: string,
    pattern: string,
    variableName: string,
    scope: VariableScope = 'global',
    source: 'body' | 'header' = 'body'
  ): ExtractionResult {
    try {
      const regex = new RegExp(pattern);
      const match = regex.exec(content);

      if (!match) {
        return {
          variableName,
          value: null,
          scope,
          source: `regex-${source}`,
          path: pattern,
          success: false,
          error: 'No matches found for regex pattern',
        };
      }

      // Return captured group if exists, otherwise full match
      const value = match[1] !== undefined ? match[1] : match[0];

      return {
        variableName,
        value,
        scope,
        source: `regex-${source}`,
        path: pattern,
        success: true,
      };
    } catch (error) {
      return {
        variableName,
        value: null,
        scope,
        source: `regex-${source}`,
        path: pattern,
        success: false,
        error: error instanceof Error ? error.message : 'Invalid regex pattern',
      };
    }
  }

  /**
   * Extract multiple variables from response using rules
   */
  async extractWithRules(
    response: Response,
    rules: ExtractionRule[]
  ): Promise<ExtractionResult[]> {
    const results: ExtractionResult[] = [];

    for (const rule of rules) {
      if (!rule.enabled) continue;

      let result: ExtractionResult | null = null;

      switch (rule.extractionType) {
        case 'jsonpath':
          if (rule.source === 'body') {
            result = this.extractFromJSON(
              response.body,
              rule.pattern,
              rule.variableName,
              rule.scope
            );
          }
          break;

        case 'xpath':
          if (rule.source === 'body' && typeof response.body === 'string') {
            result = await this.extractFromXML(
              response.body,
              rule.pattern,
              rule.variableName,
              rule.scope
            );
          }
          break;

        case 'regex':
          const content =
            rule.source === 'body'
              ? typeof response.body === 'string'
                ? response.body
                : JSON.stringify(response.body)
              : JSON.stringify(response.headers);
          result = this.extractWithRegex(
            content,
            rule.pattern,
            rule.variableName,
            rule.scope,
            rule.source
          );
          break;

        case 'header':
          if (rule.source === 'header') {
            result = this.extractFromHeader(
              response.headers,
              rule.pattern,
              rule.variableName,
              rule.scope
            );
          }
          break;
      }

      if (result) {
        results.push(result);
      }
    }

    return results;
  }

  /**
   * Add extraction rule
   */
  addRule(rule: Omit<ExtractionRule, 'id' | 'createdAt' | 'updatedAt'>): ExtractionRule {
    const newRule: ExtractionRule = {
      ...rule,
      id: this.generateId(),
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.extractionRules.set(newRule.id, newRule);
    return newRule;
  }

  /**
   * Update extraction rule
   */
  updateRule(id: string, updates: Partial<ExtractionRule>): ExtractionRule | null {
    const rule = this.extractionRules.get(id);
    if (!rule) return null;

    const updatedRule = {
      ...rule,
      ...updates,
      id: rule.id,
      createdAt: rule.createdAt,
      updatedAt: new Date(),
    };

    this.extractionRules.set(id, updatedRule);
    return updatedRule;
  }

  /**
   * Delete extraction rule
   */
  deleteRule(id: string): boolean {
    return this.extractionRules.delete(id);
  }

  /**
   * Get all extraction rules
   */
  getRules(): ExtractionRule[] {
    return Array.from(this.extractionRules.values());
  }

  /**
   * Get rule by ID
   */
  getRule(id: string): ExtractionRule | null {
    return this.extractionRules.get(id) || null;
  }

  /**
   * Record variable change in history
   */
  recordHistory(
    variableName: string,
    oldValue: any,
    newValue: any,
    scope: VariableScope,
    source: string,
    requestId?: string
  ): void {
    const historyEntry: VariableHistory = {
      id: this.generateId(),
      variableName,
      oldValue,
      newValue,
      scope,
      source,
      timestamp: new Date(),
      requestId,
    };

    this.variableHistory.unshift(historyEntry);

    // Limit history size
    if (this.variableHistory.length > this.maxHistorySize) {
      this.variableHistory = this.variableHistory.slice(0, this.maxHistorySize);
    }
  }

  /**
   * Get variable history
   */
  getHistory(variableName?: string, limit = 100): VariableHistory[] {
    let history = this.variableHistory;

    if (variableName) {
      history = history.filter((h) => h.variableName === variableName);
    }

    return history.slice(0, limit);
  }

  /**
   * Clear variable history
   */
  clearHistory(variableName?: string): void {
    if (variableName) {
      this.variableHistory = this.variableHistory.filter(
        (h) => h.variableName !== variableName
      );
    } else {
      this.variableHistory = [];
    }
  }

  /**
   * Detect content type and suggest extraction method
   */
  suggestExtractionMethod(response: Response): 'jsonpath' | 'xpath' | 'regex' | 'header' {
    const contentType =
      response.headers['content-type'] || response.headers['Content-Type'] || '';

    if (contentType.includes('application/json')) {
      return 'jsonpath';
    } else if (contentType.includes('xml')) {
      return 'xpath';
    } else {
      return 'regex';
    }
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Export rules to JSON
   */
  exportRules(): string {
    return JSON.stringify(Array.from(this.extractionRules.values()), null, 2);
  }

  /**
   * Import rules from JSON
   */
  importRules(json: string): number {
    try {
      const rules = JSON.parse(json) as ExtractionRule[];
      let imported = 0;

      for (const rule of rules) {
        this.extractionRules.set(rule.id, rule);
        imported++;
      }

      return imported;
    } catch (error) {
      throw new Error('Failed to import rules: Invalid JSON format');
    }
  }

  /**
   * Cleanup resources (for testing)
   */
  cleanup(): void {
    // Clear maps and arrays
    this.extractionRules.clear();
    this.variableHistory = [];
    // Parser will be garbage collected
  }
}

// Singleton instance
let instance: VariableExtractorService | null = null;

export function getVariableExtractorService(): VariableExtractorService {
  if (!instance) {
    instance = new VariableExtractorService();
  }
  return instance;
}
