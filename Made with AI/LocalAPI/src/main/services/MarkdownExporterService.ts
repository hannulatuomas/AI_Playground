/**
 * MarkdownExporterService - Markdown Documentation Exporter
 * 
 * Exports API documentation in Markdown format
 * Compatible with GitHub, GitLab, and other Markdown renderers
 */

import type { OpenAPISpec } from './OpenAPIGeneratorService';

export interface MarkdownOptions {
  includeTableOfContents?: boolean;
  includeExamples?: boolean;
  includeSchemas?: boolean;
  format?: 'github' | 'gitlab' | 'standard';
}

export class MarkdownExporterService {
  /**
   * Export OpenAPI spec as Markdown
   */
  exportToMarkdown(spec: OpenAPISpec, options: MarkdownOptions = {}): string {
    const sections: string[] = [];

    // Title and version
    sections.push(`# ${spec.info.title}`);
    sections.push(`\n**Version:** ${spec.info.version}\n`);

    if (spec.info.description) {
      sections.push(`${spec.info.description}\n`);
    }

    // Table of contents
    if (options.includeTableOfContents !== false) {
      sections.push(this.generateTableOfContents(spec));
    }

    // Overview
    sections.push(this.generateOverview(spec));

    // Authentication
    if (spec.components?.securitySchemes) {
      sections.push(this.generateAuthentication(spec.components.securitySchemes));
    }

    // Endpoints
    sections.push(this.generateEndpoints(spec, options));

    // Schemas
    if (options.includeSchemas && spec.components?.schemas) {
      sections.push(this.generateSchemas(spec.components.schemas));
    }

    return sections.join('\n');
  }

  private generateTableOfContents(spec: OpenAPISpec): string {
    const toc: string[] = ['\n## Table of Contents\n'];

    toc.push('- [Overview](#overview)');

    if (spec.components?.securitySchemes) {
      toc.push('- [Authentication](#authentication)');
    }

    toc.push('- [Endpoints](#endpoints)');

    for (const path of Object.keys(spec.paths)) {
      const slug = this.slugify(path);
      toc.push(`  - [${path}](#${slug})`);
    }

    if (spec.components?.schemas) {
      toc.push('- [Schemas](#schemas)');
    }

    return toc.join('\n') + '\n';
  }

  private generateOverview(spec: OpenAPISpec): string {
    const sections: string[] = ['\n## Overview\n'];

    if (spec.servers && spec.servers.length > 0) {
      sections.push('### Base URLs\n');
      for (const server of spec.servers) {
        sections.push(`- \`${server.url}\`${server.description ? ` - ${server.description}` : ''}`);
      }
      sections.push('');
    }

    if (spec.info.contact) {
      sections.push('### Contact\n');
      if (spec.info.contact.name) {
        sections.push(`**Name:** ${spec.info.contact.name}`);
      }
      if (spec.info.contact.email) {
        sections.push(`**Email:** ${spec.info.contact.email}`);
      }
      if (spec.info.contact.url) {
        sections.push(`**URL:** ${spec.info.contact.url}`);
      }
      sections.push('');
    }

    return sections.join('\n');
  }

  private generateAuthentication(securitySchemes: Record<string, any>): string {
    const sections: string[] = ['\n## Authentication\n'];

    for (const [name, scheme] of Object.entries(securitySchemes)) {
      sections.push(`### ${name}\n`);
      sections.push(`**Type:** ${scheme.type}\n`);

      if (scheme.scheme) {
        sections.push(`**Scheme:** ${scheme.scheme}\n`);
      }

      if (scheme.bearerFormat) {
        sections.push(`**Bearer Format:** ${scheme.bearerFormat}\n`);
      }

      if (scheme.description) {
        sections.push(`${scheme.description}\n`);
      }
    }

    return sections.join('\n');
  }

  private generateEndpoints(spec: OpenAPISpec, options: MarkdownOptions): string {
    const sections: string[] = ['\n## Endpoints\n'];

    for (const [path, pathItem] of Object.entries(spec.paths)) {
      sections.push(`### ${path}\n`);

      for (const [method, operation] of Object.entries(pathItem)) {
        if (method === 'parameters') continue;
        sections.push(this.generateOperation(path, method, operation as any, options));
      }
    }

    return sections.join('\n');
  }

  private generateOperation(path: string, method: string, operation: any, options: MarkdownOptions): string {
    const sections: string[] = [];

    sections.push(`#### ${method.toUpperCase()} ${path}\n`);

    if (operation.summary) {
      sections.push(`**Summary:** ${operation.summary}\n`);
    }

    if (operation.description) {
      sections.push(`${operation.description}\n`);
    }

    // Parameters
    if (operation.parameters && operation.parameters.length > 0) {
      sections.push('**Parameters:**\n');
      sections.push('| Name | In | Type | Required | Description |');
      sections.push('|------|-------|------|----------|-------------|');

      for (const param of operation.parameters) {
        sections.push(
          `| \`${param.name}\` | ${param.in} | \`${param.schema?.type || 'any'}\` | ${param.required ? 'Yes' : 'No'} | ${param.description || ''} |`
        );
      }
      sections.push('');
    }

    // Request Body
    if (operation.requestBody) {
      sections.push('**Request Body:**\n');
      const content = operation.requestBody.content || {};

      for (const [contentType, mediaType] of Object.entries(content)) {
        sections.push(`*${contentType}*\n`);

        if (options.includeExamples && (mediaType as any).example) {
          sections.push('```json');
          sections.push(JSON.stringify((mediaType as any).example, null, 2));
          sections.push('```\n');
        }
      }
    }

    // Responses
    if (operation.responses) {
      sections.push('**Responses:**\n');

      for (const [status, response] of Object.entries(operation.responses)) {
        sections.push(`**${status}** - ${(response as any).description || ''}\n`);

        if ((response as any).content && options.includeExamples) {
          for (const [contentType, mediaType] of Object.entries((response as any).content)) {
            if ((mediaType as any).example) {
              sections.push('```json');
              sections.push(JSON.stringify((mediaType as any).example, null, 2));
              sections.push('```\n');
            }
          }
        }
      }
    }

    sections.push('---\n');
    return sections.join('\n');
  }

  private generateSchemas(schemas: Record<string, any>): string {
    const sections: string[] = ['\n## Schemas\n'];

    for (const [name, schema] of Object.entries(schemas)) {
      sections.push(`### ${name}\n`);
      sections.push('```json');
      sections.push(JSON.stringify(schema, null, 2));
      sections.push('```\n');
    }

    return sections.join('\n');
  }

  private slugify(text: string): string {
    return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  }
}
