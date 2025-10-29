// cURL Import/Export Handler
import type { 
  ImporterExporter, 
  ImportExportFormat, 
  ImportExportOptions, 
  ImportResult, 
  ExportResult 
} from '../../../types/import-export';
import type { Request, HttpMethod } from '../../../types/models';

export class CurlImporterExporter implements ImporterExporter {
  readonly format: ImportExportFormat = 'curl';
  readonly name = 'cURL';
  readonly description = 'cURL command format';
  readonly fileExtensions = ['.sh', '.txt'];

  /**
   * Check if content is a valid cURL command
   */
  canImport(content: string): boolean {
    const trimmed = content.trim();
    return trimmed.startsWith('curl ') || trimmed.includes('curl ');
  }

  /**
   * Import cURL command(s)
   */
  async import(content: string, options?: ImportExportOptions): Promise<ImportResult> {
    try {
      const result: ImportResult = {
        success: true,
        requests: [],
        errors: [],
        warnings: [],
        metadata: {
          format: this.format,
          itemCount: 0,
          importedAt: new Date(),
        },
      };

      // Split by newlines and filter curl commands
      const lines = content.split('\n');
      const curlCommands: string[] = [];
      let currentCommand = '';

      for (const line of lines) {
        const trimmed = line.trim();
        
        // Skip empty lines and comments
        if (!trimmed || trimmed.startsWith('#')) continue;
        
        // Check if line ends with backslash (continuation)
        if (trimmed.endsWith('\\')) {
          currentCommand += trimmed.slice(0, -1) + ' ';
        } else {
          currentCommand += trimmed;
          if (currentCommand.includes('curl ')) {
            curlCommands.push(currentCommand.trim());
            currentCommand = '';
          }
        }
      }

      // Parse each cURL command
      for (const curlCommand of curlCommands) {
        try {
          const request = this.parseCurlCommand(curlCommand);
          result.requests?.push(request);
        } catch (error) {
          result.warnings?.push(
            `Failed to parse command: ${error instanceof Error ? error.message : 'Unknown error'}`
          );
        }
      }

      result.metadata!.itemCount = result.requests?.length || 0;

      if (result.requests?.length === 0) {
        result.success = false;
        result.errors?.push('No valid cURL commands found');
      }

      return result;
    } catch (error) {
      return {
        success: false,
        errors: [`Import failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
        metadata: {
          format: this.format,
          itemCount: 0,
          importedAt: new Date(),
        },
      };
    }
  }

  /**
   * Export collections to cURL (exports all requests)
   */
  async exportCollections(
    collections: any[], 
    options?: ImportExportOptions
  ): Promise<ExportResult> {
    try {
      const allRequests: Request[] = [];
      
      for (const collection of collections) {
        if (collection.requests) {
          allRequests.push(...collection.requests);
        }
      }

      return this.exportRequests(allRequests, options);
    } catch (error) {
      return {
        success: false,
        format: this.format,
        errors: [`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
      };
    }
  }

  /**
   * Export a single request to cURL
   */
  async exportRequest(
    request: Request, 
    options?: ImportExportOptions
  ): Promise<ExportResult> {
    try {
      const curlCommand = this.generateCurlCommand(request);

      return {
        success: true,
        data: curlCommand,
        format: this.format,
        metadata: {
          exportedAt: new Date(),
          itemCount: 1,
          size: new Blob([curlCommand]).size,
        },
      };
    } catch (error) {
      return {
        success: false,
        format: this.format,
        errors: [`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
      };
    }
  }

  /**
   * Export multiple requests to cURL
   */
  async exportRequests(
    requests: Request[], 
    options?: ImportExportOptions
  ): Promise<ExportResult> {
    try {
      const curlCommands = requests.map((req, index) => {
        const comment = `# ${req.name || `Request ${index + 1}`}`;
        const curl = this.generateCurlCommand(req);
        return `${comment}\n${curl}`;
      });

      const output = curlCommands.join('\n\n');

      return {
        success: true,
        data: output,
        format: this.format,
        metadata: {
          exportedAt: new Date(),
          itemCount: requests.length,
          size: new Blob([output]).size,
        },
      };
    } catch (error) {
      return {
        success: false,
        format: this.format,
        errors: [`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
      };
    }
  }

  /**
   * Get example cURL command
   */
  getExample(): string {
    return `# Example GET request
curl -X GET 'https://api.example.com/users' \\
  -H 'Content-Type: application/json' \\
  -H 'Authorization: Bearer token123'

# Example POST request
curl -X POST 'https://api.example.com/users' \\
  -H 'Content-Type: application/json' \\
  -d '{"name":"John Doe","email":"john@example.com"}'`;
  }

  /**
   * Parse cURL command to Request object
   */
  private parseCurlCommand(curlCommand: string): Request {
    // Remove 'curl' prefix and normalize whitespace
    let cmd = curlCommand.replace(/^curl\s+/i, '').trim();
    
    // Initialize request object
    const request: Partial<Request> = {
      id: `req-${Date.now()}-${Math.random()}`,
      protocol: 'REST',
      method: 'GET',
      url: '',
      headers: [],
      queryParams: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    // Parse method (-X or --request)
    const methodMatch = cmd.match(/(?:-X|--request)\s+([A-Z]+)/i);
    if (methodMatch) {
      request.method = methodMatch[1].toUpperCase() as HttpMethod;
      cmd = cmd.replace(methodMatch[0], '');
    }

    // Parse headers (-H or --header)
    // Match both quoted and unquoted headers
    const headerRegex = /(?:-H|--header)\s+['"]?([^'"]+?)['"]?(?:\s|$|\\)/g;
    let headerMatch;
    const foundHeaders: string[] = [];
    while ((headerMatch = headerRegex.exec(cmd)) !== null) {
      const headerValue = headerMatch[1].trim();
      // Skip if this looks like it's part of another option
      if (headerValue.startsWith('-')) continue;
      
      const colonIndex = headerValue.indexOf(':');
      if (colonIndex > 0) {
        const key = headerValue.substring(0, colonIndex).trim();
        const value = headerValue.substring(colonIndex + 1).trim();
        request.headers?.push({ key, value, enabled: true });
        foundHeaders.push(headerMatch[0]);
      }
    }
    // Remove found headers from command
    foundHeaders.forEach(h => {
      cmd = cmd.replace(h, '');
    });

    // Parse data/body (-d, --data, --data-raw, --data-binary)
    // Use non-greedy match and handle nested quotes in JSON
    const dataMatch = cmd.match(/(?:-d|--data|--data-raw|--data-binary)\s+['"](.+?)['"]\s*$/);
    if (dataMatch) {
      request.body = {
        type: 'json',
        content: dataMatch[1],
      };
      cmd = cmd.replace(dataMatch[0], '');
    }

    // Parse URL (remaining quoted or unquoted string)
    const urlMatch = cmd.match(/['"]([^'"]+)['"]|(\S+)/);
    if (urlMatch) {
      request.url = urlMatch[1] || urlMatch[2];
      
      // Extract query params from URL
      const urlObj = new URL(request.url);
      urlObj.searchParams.forEach((value, key) => {
        request.queryParams?.push({ key, value, enabled: true });
      });
      
      // Remove query params from URL
      request.url = `${urlObj.origin}${urlObj.pathname}`;
    }

    // Generate name from method and URL
    request.name = `${request.method} ${request.url}`;

    if (!request.url) {
      throw new Error('No URL found in cURL command');
    }

    return request as Request;
  }

  /**
   * Generate cURL command from Request object
   */
  private generateCurlCommand(request: Request): string {
    const parts: string[] = ['curl'];

    // Add method if not GET
    if (request.method !== 'GET') {
      parts.push(`-X ${request.method}`);
    }

    // Build URL with query params
    let url = request.url;
    if (request.queryParams && request.queryParams.length > 0) {
      const params = request.queryParams
        .filter(p => p.enabled)
        .map(p => `${encodeURIComponent(p.key)}=${encodeURIComponent(p.value)}`)
        .join('&');
      url += `?${params}`;
    }
    parts.push(`'${url}'`);

    // Add headers
    if (request.headers) {
      request.headers
        .filter(h => h.enabled)
        .forEach(h => {
          parts.push(`-H '${h.key}: ${h.value}'`);
        });
    }

    // Add body
    if (request.body && request.body.content) {
      const bodyContent = request.body.content.replace(/'/g, "'\\''"); // Escape single quotes
      parts.push(`-d '${bodyContent}'`);
    }

    // Join with backslashes for multi-line format
    return parts.join(' \\\n  ');
  }
}
