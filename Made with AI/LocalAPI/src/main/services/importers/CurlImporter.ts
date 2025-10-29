// cURL Command Importer
import type {
  Importer,
  ImportExportFormat,
  ImportExportOptions,
  ImportResult,
} from '../../../types/import-export';
import type { Request, HttpMethod, RequestBody } from '../../../types/models';

/**
 * cURL Command Importer
 * Supports both bash and PowerShell cURL syntax
 */
export class CurlImporter implements Importer {
  readonly format: ImportExportFormat = 'curl';
  readonly name = 'cURL Command';
  readonly description = 'Import cURL commands (bash and PowerShell)';
  readonly fileExtensions = ['.sh', '.txt'];

  /**
   * Check if content can be imported
   */
  canImport(content: string): boolean {
    const trimmed = content.trim();
    return (
      trimmed.startsWith('curl ') ||
      trimmed.startsWith('curl.exe ') ||
      trimmed.includes('curl ')
    );
  }

  /**
   * Import cURL command
   */
  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const requests: Request[] = [];

      // Split by newlines and process each curl command
      const lines = content.split('\n');
      let currentCommand = '';

      for (const line of lines) {
        const trimmed = line.trim();

        // Skip empty lines and comments
        if (!trimmed || trimmed.startsWith('#')) continue;

        // Handle line continuation (\ or `)
        if (trimmed.endsWith('\\') || trimmed.endsWith('`')) {
          currentCommand += trimmed.slice(0, -1) + ' ';
          continue;
        }

        currentCommand += trimmed;

        // Process complete command
        if (currentCommand.includes('curl')) {
          const request = this.parseCurlCommand(currentCommand);
          if (request) {
            requests.push(request);
          }
          currentCommand = '';
        }
      }

      // Process any remaining command
      if (currentCommand.includes('curl')) {
        const request = this.parseCurlCommand(currentCommand);
        if (request) {
          requests.push(request);
        }
      }

      console.log(`[CurlImporter] Imported ${requests.length} requests`);

      return {
        success: true,
        requests,
        metadata: {
          format: this.format,
          itemCount: requests.length,
          importedAt: new Date(),
        },
      };
    } catch (error) {
      console.error('[CurlImporter] Import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import cURL command',
        ],
      };
    }
  }

  /**
   * Parse a single cURL command
   */
  private parseCurlCommand(command: string): Request | null {
    try {
      // Remove 'curl' or 'curl.exe' from start
      let cmd = command.replace(/^curl(\.exe)?\s+/, '').trim();

      // Extract URL (first non-flag argument or -u/--url value)
      let url = '';
      let method: HttpMethod = 'GET';
      const headers: Array<{ key: string; value: string; enabled: boolean }> = [];
      const queryParams: Array<{ key: string; value: string; enabled: boolean }> = [];
      let body: RequestBody | undefined;

      // Method (-X or --request) - parse this first
      const methodMatch = cmd.match(/(?:-X|--request)\s+['"]?(\w+)['"]?/i);
      if (methodMatch) {
        method = methodMatch[1].toUpperCase() as HttpMethod;
        cmd = cmd.replace(methodMatch[0], '');
      }

      // Parse URL - try --url flag first, then look for http(s):// anywhere
      const urlFlagMatch = cmd.match(/--url\s+['"]?([^'"\s]+)['"]?/);
      if (urlFlagMatch) {
        url = urlFlagMatch[1];
        cmd = cmd.replace(urlFlagMatch[0], '');
      } else {
        // Look for http(s):// URL anywhere in the command
        const httpMatch = cmd.match(/['"]?(https?:\/\/[^\s'"]+)['"]?/);
        if (httpMatch) {
          url = httpMatch[1];
          cmd = cmd.replace(httpMatch[0], '');
        }
      }

      // Headers (-H or --header)
      const headerRegex = /(?:-H|--header)\s+['"]([^'"]+)['"]/g;
      let headerMatch;
      while ((headerMatch = headerRegex.exec(cmd)) !== null) {
        const [key, value] = headerMatch[1].split(':').map((s) => s.trim());
        if (key && value) {
          headers.push({ key, value, enabled: true });
        }
      }

      // Data (-d, --data, --data-raw, --data-binary)
      const dataMatch = cmd.match(/(?:-d|--data|--data-raw|--data-binary)\s+['"]([^'"]+)['"]/);
      if (dataMatch) {
        body = {
          type: 'raw' as const,
          content: dataMatch[1],
        };
        // If data is present and no method specified, default to POST
        if (!methodMatch) {
          method = 'POST';
        }
      }

      // Form data (-F or --form)
      const formMatch = cmd.match(/(?:-F|--form)\s+['"]([^'"]+)['"]/);
      if (formMatch) {
        body = {
          type: 'form-data' as const,
          content: formMatch[1],
        };
        if (!methodMatch) {
          method = 'POST';
        }
      }

      // URL-encoded data (--data-urlencode)
      const urlencodedMatch = cmd.match(/--data-urlencode\s+['"]([^'"]+)['"]/);
      if (urlencodedMatch) {
        body = {
          type: 'x-www-form-urlencoded' as const,
          content: urlencodedMatch[1],
        };
        if (!methodMatch) {
          method = 'POST';
        }
      }

      if (!url) {
        console.warn('[CurlImporter] No URL found in cURL command');
        return null;
      }

      // Parse query parameters from URL
      try {
        const urlObj = new URL(url);
        urlObj.searchParams.forEach((value, key) => {
          queryParams.push({ key, value, enabled: true });
        });
        // Remove query params from URL
        url = `${urlObj.origin}${urlObj.pathname}`;
      } catch {
        // Invalid URL, keep as is
      }

      // Create request
      const request: Request = {
        id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: `${method} ${new URL(url).pathname}`,
        description: 'Imported from cURL',
        protocol: 'REST' as const,
        method,
        url,
        headers,
        queryParams,
        body,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      return request;
    } catch (error) {
      console.error('[CurlImporter] Error parsing cURL command:', error);
      return null;
    }
  }

  /**
   * Get example cURL command
   */
  getExample(): string {
    return `curl -X POST https://api.example.com/users \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer token123" \\
  -d '{"name": "John Doe", "email": "john@example.com"}'`;
  }
}
