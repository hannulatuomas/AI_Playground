// Schema Refactoring Service
// Handles API schema updates, version comparison, and automatic request migration

import type { Collection, Request } from '../../types/models';

interface SchemaChange {
  type: 'added' | 'removed' | 'modified' | 'deprecated';
  severity: 'breaking' | 'warning' | 'info';
  path: string;
  oldValue?: any;
  newValue?: any;
  message: string;
}

interface RefactoringResult {
  changes: SchemaChange[];
  migratedRequests: Request[];
  breakingChanges: SchemaChange[];
  warnings: SchemaChange[];
  summary: {
    totalChanges: number;
    breakingCount: number;
    warningCount: number;
    infoCount: number;
  };
}

interface SchemaVersion {
  version: string;
  spec: any;
  timestamp: Date;
}

export class SchemaRefactoring {
  /**
   * Compare two OpenAPI schemas and detect changes
   */
  compareSchemas(
    oldSpec: any,
    newSpec: any
  ): SchemaChange[] {
    const changes: SchemaChange[] = [];

    // Compare info
    if (oldSpec.info?.version !== newSpec.info?.version) {
      changes.push({
        type: 'modified',
        severity: 'info',
        path: 'info.version',
        oldValue: oldSpec.info?.version,
        newValue: newSpec.info?.version,
        message: `API version changed from ${oldSpec.info?.version} to ${newSpec.info?.version}`,
      });
    }

    // Compare servers/base URLs
    const oldServers = this.extractServers(oldSpec);
    const newServers = this.extractServers(newSpec);
    if (JSON.stringify(oldServers) !== JSON.stringify(newServers)) {
      changes.push({
        type: 'modified',
        severity: 'warning',
        path: 'servers',
        oldValue: oldServers,
        newValue: newServers,
        message: 'Server URLs have changed',
      });
    }

    // Compare paths
    const pathChanges = this.comparePaths(oldSpec, newSpec);
    changes.push(...pathChanges);

    // Compare security schemes
    const securityChanges = this.compareSecuritySchemes(oldSpec, newSpec);
    changes.push(...securityChanges);

    return changes;
  }

  /**
   * Compare API paths
   */
  private comparePaths(oldSpec: any, newSpec: any): SchemaChange[] {
    const changes: SchemaChange[] = [];
    const oldPaths = oldSpec.paths || {};
    const newPaths = newSpec.paths || {};

    const allPaths = new Set([...Object.keys(oldPaths), ...Object.keys(newPaths)]);

    for (const path of allPaths) {
      const oldPath = oldPaths[path];
      const newPath = newPaths[path];

      // Path removed
      if (oldPath && !newPath) {
        changes.push({
          type: 'removed',
          severity: 'breaking',
          path: `paths.${path}`,
          oldValue: oldPath,
          message: `Endpoint removed: ${path}`,
        });
        continue;
      }

      // Path added
      if (!oldPath && newPath) {
        changes.push({
          type: 'added',
          severity: 'info',
          path: `paths.${path}`,
          newValue: newPath,
          message: `New endpoint added: ${path}`,
        });
        continue;
      }

      // Compare operations
      const operationChanges = this.compareOperations(path, oldPath, newPath);
      changes.push(...operationChanges);
    }

    return changes;
  }

  /**
   * Compare operations within a path
   */
  private compareOperations(
    path: string,
    oldPath: any,
    newPath: any
  ): SchemaChange[] {
    const changes: SchemaChange[] = [];
    const methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options'];

    for (const method of methods) {
      const oldOp = oldPath[method];
      const newOp = newPath[method];

      // Operation removed
      if (oldOp && !newOp) {
        changes.push({
          type: 'removed',
          severity: 'breaking',
          path: `paths.${path}.${method}`,
          oldValue: oldOp,
          message: `Operation removed: ${method.toUpperCase()} ${path}`,
        });
        continue;
      }

      // Operation added
      if (!oldOp && newOp) {
        changes.push({
          type: 'added',
          severity: 'info',
          path: `paths.${path}.${method}`,
          newValue: newOp,
          message: `New operation added: ${method.toUpperCase()} ${path}`,
        });
        continue;
      }

      if (oldOp && newOp) {
        // Check deprecation
        if (!oldOp.deprecated && newOp.deprecated) {
          changes.push({
            type: 'deprecated',
            severity: 'warning',
            path: `paths.${path}.${method}`,
            message: `Operation deprecated: ${method.toUpperCase()} ${path}`,
          });
        }

        // Compare parameters
        const paramChanges = this.compareParameters(
          `paths.${path}.${method}`,
          oldOp.parameters || [],
          newOp.parameters || []
        );
        changes.push(...paramChanges);

        // Compare request body
        const bodyChanges = this.compareRequestBody(
          `paths.${path}.${method}`,
          oldOp.requestBody,
          newOp.requestBody
        );
        changes.push(...bodyChanges);

        // Compare responses
        const responseChanges = this.compareResponses(
          `paths.${path}.${method}`,
          oldOp.responses,
          newOp.responses
        );
        changes.push(...responseChanges);
      }
    }

    return changes;
  }

  /**
   * Compare parameters
   */
  private compareParameters(
    basePath: string,
    oldParams: any[],
    newParams: any[]
  ): SchemaChange[] {
    const changes: SchemaChange[] = [];

    const oldParamMap = new Map(oldParams.map(p => [p.name + p.in, p]));
    const newParamMap = new Map(newParams.map(p => [p.name + p.in, p]));

    // Check for removed parameters
    for (const [key, oldParam] of oldParamMap) {
      if (!newParamMap.has(key)) {
        changes.push({
          type: 'removed',
          severity: oldParam.required ? 'breaking' : 'warning',
          path: `${basePath}.parameters.${oldParam.name}`,
          oldValue: oldParam,
          message: `Parameter removed: ${oldParam.name} (${oldParam.in})${oldParam.required ? ' [REQUIRED]' : ''}`,
        });
      }
    }

    // Check for added parameters
    for (const [key, newParam] of newParamMap) {
      const oldParam = oldParamMap.get(key);
      
      if (!oldParam) {
        changes.push({
          type: 'added',
          severity: newParam.required ? 'breaking' : 'info',
          path: `${basePath}.parameters.${newParam.name}`,
          newValue: newParam,
          message: `Parameter added: ${newParam.name} (${newParam.in})${newParam.required ? ' [REQUIRED]' : ''}`,
        });
      } else {
        // Check if required status changed
        if (!oldParam.required && newParam.required) {
          changes.push({
            type: 'modified',
            severity: 'breaking',
            path: `${basePath}.parameters.${newParam.name}`,
            oldValue: oldParam,
            newValue: newParam,
            message: `Parameter now required: ${newParam.name}`,
          });
        }
      }
    }

    return changes;
  }

  /**
   * Compare request body
   */
  private compareRequestBody(
    basePath: string,
    oldBody: any,
    newBody: any
  ): SchemaChange[] {
    const changes: SchemaChange[] = [];

    if (oldBody && !newBody) {
      changes.push({
        type: 'removed',
        severity: 'breaking',
        path: `${basePath}.requestBody`,
        oldValue: oldBody,
        message: 'Request body removed',
      });
    } else if (!oldBody && newBody) {
      changes.push({
        type: 'added',
        severity: newBody.required ? 'breaking' : 'warning',
        path: `${basePath}.requestBody`,
        newValue: newBody,
        message: `Request body added${newBody.required ? ' [REQUIRED]' : ''}`,
      });
    } else if (oldBody && newBody) {
      if (!oldBody.required && newBody.required) {
        changes.push({
          type: 'modified',
          severity: 'breaking',
          path: `${basePath}.requestBody`,
          message: 'Request body now required',
        });
      }
    }

    return changes;
  }

  /**
   * Compare responses
   */
  private compareResponses(
    basePath: string,
    oldResponses: any,
    newResponses: any
  ): SchemaChange[] {
    const changes: SchemaChange[] = [];

    if (!oldResponses || !newResponses) return changes;

    const oldCodes = Object.keys(oldResponses);
    const newCodes = Object.keys(newResponses);

    // Check for removed response codes
    for (const code of oldCodes) {
      if (!newResponses[code]) {
        changes.push({
          type: 'removed',
          severity: 'warning',
          path: `${basePath}.responses.${code}`,
          message: `Response code removed: ${code}`,
        });
      }
    }

    // Check for added response codes
    for (const code of newCodes) {
      if (!oldResponses[code]) {
        changes.push({
          type: 'added',
          severity: 'info',
          path: `${basePath}.responses.${code}`,
          message: `Response code added: ${code}`,
        });
      }
    }

    return changes;
  }

  /**
   * Compare security schemes
   */
  private compareSecuritySchemes(oldSpec: any, newSpec: any): SchemaChange[] {
    const changes: SchemaChange[] = [];

    const oldSchemes = this.extractSecuritySchemes(oldSpec);
    const newSchemes = this.extractSecuritySchemes(newSpec);

    const allSchemes = new Set([...Object.keys(oldSchemes), ...Object.keys(newSchemes)]);

    for (const schemeName of allSchemes) {
      const oldScheme = oldSchemes[schemeName];
      const newScheme = newSchemes[schemeName];

      if (oldScheme && !newScheme) {
        changes.push({
          type: 'removed',
          severity: 'breaking',
          path: `securitySchemes.${schemeName}`,
          message: `Security scheme removed: ${schemeName}`,
        });
      } else if (!oldScheme && newScheme) {
        changes.push({
          type: 'added',
          severity: 'info',
          path: `securitySchemes.${schemeName}`,
          message: `Security scheme added: ${schemeName}`,
        });
      }
    }

    return changes;
  }

  /**
   * Migrate collection to new schema
   */
  async migrateCollection(
    collection: Collection,
    oldSpec: any,
    newSpec: any
  ): Promise<RefactoringResult> {
    const changes = this.compareSchemas(oldSpec, newSpec);
    const migratedRequests: Request[] = [];

    // Migrate each request
    for (const request of collection.requests || []) {
      const migrated = this.migrateRequest(request, changes, newSpec);
      migratedRequests.push(migrated);
    }

    // Categorize changes
    const breakingChanges = changes.filter(c => c.severity === 'breaking');
    const warnings = changes.filter(c => c.severity === 'warning');

    return {
      changes,
      migratedRequests,
      breakingChanges,
      warnings,
      summary: {
        totalChanges: changes.length,
        breakingCount: breakingChanges.length,
        warningCount: warnings.length,
        infoCount: changes.filter(c => c.severity === 'info').length,
      },
    };
  }

  /**
   * Migrate a single request
   */
  private migrateRequest(
    request: Request,
    changes: SchemaChange[],
    newSpec: any
  ): Request {
    const migrated = { ...request };

    // Update server URL if changed
    const serverChange = changes.find(c => c.path === 'servers');
    if (serverChange && serverChange.newValue) {
      const newServers = serverChange.newValue as string[];
      if (newServers.length > 0) {
        // Replace old base URL with new one
        const oldBase = this.extractBaseUrl(request.url);
        const newBase = newServers[0];
        migrated.url = request.url.replace(oldBase, newBase);
      }
    }

    // Add deprecation warning to description
    const deprecationChange = changes.find(
      c => c.type === 'deprecated' && c.path.includes(request.method.toLowerCase())
    );
    if (deprecationChange) {
      migrated.description = `⚠️ **DEPRECATED**\n\n${request.description || ''}`;
    }

    // Remove deprecated parameters
    const removedParams = changes.filter(
      c => c.type === 'removed' && c.path.includes('parameters')
    );
    for (const change of removedParams) {
      const paramName = change.path.split('.').pop();
      migrated.queryParams = migrated.queryParams?.filter(p => p.key !== paramName) || [];
      migrated.headers = migrated.headers?.filter(h => h.key !== paramName) || [];
    }

    return migrated;
  }

  /**
   * Extract servers from spec
   */
  private extractServers(spec: any): string[] {
    if (spec.openapi && spec.servers) {
      return spec.servers.map((s: any) => s.url);
    } else if (spec.swagger) {
      const scheme = spec.schemes?.[0] || 'http';
      const host = spec.host || 'localhost';
      const basePath = spec.basePath || '';
      return [`${scheme}://${host}${basePath}`];
    }
    return [];
  }

  /**
   * Extract security schemes from spec
   */
  private extractSecuritySchemes(spec: any): Record<string, any> {
    if (spec.openapi) {
      return spec.components?.securitySchemes || {};
    } else if (spec.swagger) {
      return spec.securityDefinitions || {};
    }
    return {};
  }

  /**
   * Extract base URL from full URL
   */
  private extractBaseUrl(url: string): string {
    try {
      const urlObj = new URL(url);
      return `${urlObj.protocol}//${urlObj.host}`;
    } catch {
      return url.split('/').slice(0, 3).join('/');
    }
  }

  /**
   * Generate migration report
   */
  generateReport(result: RefactoringResult): string {
    let report = '# Schema Migration Report\n\n';
    report += `**Generated:** ${new Date().toISOString()}\n\n`;
    report += `## Summary\n\n`;
    report += `- **Total Changes:** ${result.summary.totalChanges}\n`;
    report += `- **Breaking Changes:** ${result.summary.breakingCount}\n`;
    report += `- **Warnings:** ${result.summary.warningCount}\n`;
    report += `- **Info:** ${result.summary.infoCount}\n\n`;

    if (result.breakingChanges.length > 0) {
      report += `## ⚠️ Breaking Changes\n\n`;
      for (const change of result.breakingChanges) {
        report += `- **${change.message}**\n`;
        report += `  - Path: \`${change.path}\`\n`;
        report += `  - Type: ${change.type}\n\n`;
      }
    }

    if (result.warnings.length > 0) {
      report += `## ⚡ Warnings\n\n`;
      for (const change of result.warnings) {
        report += `- ${change.message}\n`;
        report += `  - Path: \`${change.path}\`\n\n`;
      }
    }

    report += `## Migration Actions\n\n`;
    report += `- ${result.migratedRequests.length} requests migrated\n`;
    report += `- Review breaking changes before deploying\n`;
    report += `- Update tests for modified endpoints\n`;

    return report;
  }
}

// Singleton instance
let schemaRefactoringInstance: SchemaRefactoring | null = null;

export function getSchemaRefactoring(): SchemaRefactoring {
  if (!schemaRefactoringInstance) {
    schemaRefactoringInstance = new SchemaRefactoring();
  }
  return schemaRefactoringInstance;
}
