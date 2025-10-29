/**
 * ChangelogGeneratorService - API Changelog Generator
 * 
 * Generates changelogs from API version comparisons
 * Detects breaking changes, new endpoints, deprecated features
 */

import type { OpenAPISpec } from './OpenAPIGeneratorService';

export interface ChangelogEntry {
  version: string;
  date: string;
  changes: Change[];
}

export interface Change {
  type: 'added' | 'changed' | 'deprecated' | 'removed' | 'fixed' | 'security';
  category: 'endpoint' | 'parameter' | 'response' | 'schema' | 'auth' | 'general';
  description: string;
  breaking?: boolean;
  path?: string;
  method?: string;
}

export class ChangelogGeneratorService {
  /**
   * Generate changelog by comparing two OpenAPI specs
   */
  generateChangelog(oldSpec: OpenAPISpec, newSpec: OpenAPISpec): ChangelogEntry {
    const changes: Change[] = [];

    // Compare endpoints
    changes.push(...this.compareEndpoints(oldSpec, newSpec));

    // Compare schemas
    changes.push(...this.compareSchemas(oldSpec, newSpec));

    // Compare security
    changes.push(...this.compareSecurity(oldSpec, newSpec));

    return {
      version: newSpec.info.version,
      date: new Date().toISOString().split('T')[0],
      changes,
    };
  }

  /**
   * Compare endpoints between specs
   */
  private compareEndpoints(oldSpec: OpenAPISpec, newSpec: OpenAPISpec): Change[] {
    const changes: Change[] = [];
    const oldPaths = new Set(Object.keys(oldSpec.paths));
    const newPaths = new Set(Object.keys(newSpec.paths));

    // Find new endpoints
    for (const path of newPaths) {
      if (!oldPaths.has(path)) {
        const methods = Object.keys(newSpec.paths[path]).filter(m => m !== 'parameters');
        for (const method of methods) {
          changes.push({
            type: 'added',
            category: 'endpoint',
            description: `New endpoint: ${method.toUpperCase()} ${path}`,
            path,
            method,
          });
        }
      } else {
        // Compare methods for existing paths
        changes.push(...this.compareMethods(path, oldSpec.paths[path], newSpec.paths[path]));
      }
    }

    // Find removed endpoints
    for (const path of oldPaths) {
      if (!newPaths.has(path)) {
        const methods = Object.keys(oldSpec.paths[path]).filter(m => m !== 'parameters');
        for (const method of methods) {
          changes.push({
            type: 'removed',
            category: 'endpoint',
            description: `Removed endpoint: ${method.toUpperCase()} ${path}`,
            breaking: true,
            path,
            method,
          });
        }
      }
    }

    return changes;
  }

  /**
   * Compare methods for a path
   */
  private compareMethods(path: string, oldPathItem: any, newPathItem: any): Change[] {
    const changes: Change[] = [];
    const oldMethods = new Set(Object.keys(oldPathItem).filter(m => m !== 'parameters'));
    const newMethods = new Set(Object.keys(newPathItem).filter(m => m !== 'parameters'));

    // New methods
    for (const method of newMethods) {
      if (!oldMethods.has(method)) {
        changes.push({
          type: 'added',
          category: 'endpoint',
          description: `New method: ${method.toUpperCase()} ${path}`,
          path,
          method,
        });
      } else {
        // Compare operation details
        changes.push(...this.compareOperations(path, method, oldPathItem[method], newPathItem[method]));
      }
    }

    // Removed methods
    for (const method of oldMethods) {
      if (!newMethods.has(method)) {
        changes.push({
          type: 'removed',
          category: 'endpoint',
          description: `Removed method: ${method.toUpperCase()} ${path}`,
          breaking: true,
          path,
          method,
        });
      }
    }

    return changes;
  }

  /**
   * Compare operations
   */
  private compareOperations(path: string, method: string, oldOp: any, newOp: any): Change[] {
    const changes: Change[] = [];

    // Compare parameters
    changes.push(...this.compareParameters(path, method, oldOp.parameters || [], newOp.parameters || []));

    // Compare request body
    if (oldOp.requestBody && !newOp.requestBody) {
      changes.push({
        type: 'removed',
        category: 'parameter',
        description: `Removed request body for ${method.toUpperCase()} ${path}`,
        breaking: true,
        path,
        method,
      });
    } else if (!oldOp.requestBody && newOp.requestBody) {
      changes.push({
        type: 'added',
        category: 'parameter',
        description: `Added request body for ${method.toUpperCase()} ${path}`,
        path,
        method,
      });
    }

    // Compare responses
    changes.push(...this.compareResponses(path, method, oldOp.responses || {}, newOp.responses || {}));

    // Check for deprecation
    if (!oldOp.deprecated && newOp.deprecated) {
      changes.push({
        type: 'deprecated',
        category: 'endpoint',
        description: `Deprecated: ${method.toUpperCase()} ${path}`,
        path,
        method,
      });
    }

    return changes;
  }

  /**
   * Compare parameters
   */
  private compareParameters(path: string, method: string, oldParams: any[], newParams: any[]): Change[] {
    const changes: Change[] = [];
    const oldParamMap = new Map(oldParams.map(p => [p.name + p.in, p]));
    const newParamMap = new Map(newParams.map(p => [p.name + p.in, p]));

    // New parameters
    for (const [key, param] of newParamMap) {
      if (!oldParamMap.has(key)) {
        changes.push({
          type: 'added',
          category: 'parameter',
          description: `New ${param.in} parameter '${param.name}' for ${method.toUpperCase()} ${path}`,
          breaking: param.required,
          path,
          method,
        });
      } else {
        // Check if required changed
        const oldParam = oldParamMap.get(key);
        if (!oldParam.required && param.required) {
          changes.push({
            type: 'changed',
            category: 'parameter',
            description: `Parameter '${param.name}' is now required for ${method.toUpperCase()} ${path}`,
            breaking: true,
            path,
            method,
          });
        }
      }
    }

    // Removed parameters
    for (const [key, param] of oldParamMap) {
      if (!newParamMap.has(key)) {
        changes.push({
          type: 'removed',
          category: 'parameter',
          description: `Removed ${param.in} parameter '${param.name}' from ${method.toUpperCase()} ${path}`,
          breaking: true,
          path,
          method,
        });
      }
    }

    return changes;
  }

  /**
   * Compare responses
   */
  private compareResponses(path: string, method: string, oldResponses: any, newResponses: any): Change[] {
    const changes: Change[] = [];
    const oldStatuses = new Set(Object.keys(oldResponses));
    const newStatuses = new Set(Object.keys(newResponses));

    // New response codes
    for (const status of newStatuses) {
      if (!oldStatuses.has(status)) {
        changes.push({
          type: 'added',
          category: 'response',
          description: `New ${status} response for ${method.toUpperCase()} ${path}`,
          path,
          method,
        });
      }
    }

    // Removed response codes
    for (const status of oldStatuses) {
      if (!newStatuses.has(status)) {
        changes.push({
          type: 'removed',
          category: 'response',
          description: `Removed ${status} response from ${method.toUpperCase()} ${path}`,
          breaking: status.startsWith('2'),
          path,
          method,
        });
      }
    }

    return changes;
  }

  /**
   * Compare schemas
   */
  private compareSchemas(oldSpec: OpenAPISpec, newSpec: OpenAPISpec): Change[] {
    const changes: Change[] = [];
    const oldSchemas = oldSpec.components?.schemas || {};
    const newSchemas = newSpec.components?.schemas || {};

    const oldNames = new Set(Object.keys(oldSchemas));
    const newNames = new Set(Object.keys(newSchemas));

    // New schemas
    for (const name of newNames) {
      if (!oldNames.has(name)) {
        changes.push({
          type: 'added',
          category: 'schema',
          description: `New schema: ${name}`,
        });
      }
    }

    // Removed schemas
    for (const name of oldNames) {
      if (!newNames.has(name)) {
        changes.push({
          type: 'removed',
          category: 'schema',
          description: `Removed schema: ${name}`,
          breaking: true,
        });
      }
    }

    return changes;
  }

  /**
   * Compare security schemes
   */
  private compareSecurity(oldSpec: OpenAPISpec, newSpec: OpenAPISpec): Change[] {
    const changes: Change[] = [];
    const oldSchemes = oldSpec.components?.securitySchemes || {};
    const newSchemes = newSpec.components?.securitySchemes || {};

    const oldNames = new Set(Object.keys(oldSchemes));
    const newNames = new Set(Object.keys(newSchemes));

    // New security schemes
    for (const name of newNames) {
      if (!oldNames.has(name)) {
        changes.push({
          type: 'added',
          category: 'auth',
          description: `New authentication method: ${name}`,
        });
      }
    }

    // Removed security schemes
    for (const name of oldNames) {
      if (!newNames.has(name)) {
        changes.push({
          type: 'removed',
          category: 'auth',
          description: `Removed authentication method: ${name}`,
          breaking: true,
        });
      }
    }

    return changes;
  }

  /**
   * Format changelog as Markdown
   */
  formatAsMarkdown(changelog: ChangelogEntry): string {
    const sections: string[] = [];

    sections.push(`## [${changelog.version}] - ${changelog.date}\n`);

    // Group changes by type
    const grouped = this.groupChangesByType(changelog.changes);

    for (const [type, changes] of Object.entries(grouped)) {
      if (changes.length === 0) continue;

      sections.push(`### ${this.capitalizeFirst(type)}\n`);

      for (const change of changes) {
        const breaking = change.breaking ? ' **[BREAKING]**' : '';
        sections.push(`- ${change.description}${breaking}`);
      }

      sections.push('');
    }

    return sections.join('\n');
  }

  /**
   * Group changes by type
   */
  private groupChangesByType(changes: Change[]): Record<string, Change[]> {
    const grouped: Record<string, Change[]> = {
      added: [],
      changed: [],
      deprecated: [],
      removed: [],
      fixed: [],
      security: [],
    };

    for (const change of changes) {
      grouped[change.type].push(change);
    }

    return grouped;
  }

  /**
   * Get breaking changes only
   */
  getBreakingChanges(changelog: ChangelogEntry): Change[] {
    return changelog.changes.filter(c => c.breaking);
  }

  private capitalizeFirst(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
}
