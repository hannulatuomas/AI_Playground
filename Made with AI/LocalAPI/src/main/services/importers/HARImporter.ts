// HAR (HTTP Archive) Importer
import type {
  Importer,
  ImportExportFormat,
  ImportExportOptions,
  ImportResult,
} from '../../../types/import-export';
import type { Request, HttpMethod, RequestBody } from '../../../types/models';

/**
 * HAR File Importer
 * Imports HTTP Archive format (.har files)
 */
export class HARImporter implements Importer {
  readonly format: ImportExportFormat = 'har';
  readonly name = 'HAR (HTTP Archive)';
  readonly description = 'Import HAR files from browser network recordings';
  readonly fileExtensions = ['.har'];

  /**
   * Check if content can be imported
   */
  canImport(content: string): boolean {
    try {
      const json = JSON.parse(content);
      return !!(json.log && json.log.entries);
    } catch {
      return false;
    }
  }

  /**
   * Import HAR file
   */
  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const har = JSON.parse(content);
      const entries = har.log?.entries || [];

      const requests: Request[] = [];

      for (const entry of entries) {
        const request = this.convertEntry(entry);
        if (request) {
          requests.push(request);
        }
      }

      console.log(`[HARImporter] Imported ${requests.length} requests`);

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
      console.error('[HARImporter] Import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import HAR file',
        ],
      };
    }
  }

  /**
   * Convert HAR entry to Request
   */
  private convertEntry(entry: any): Request | null {
    try {
      const req = entry.request;
      if (!req) return null;

      // Extract method and URL
      const method = req.method?.toUpperCase() as HttpMethod;
      const url = req.url;

      if (!method || !url) return null;

      // Extract headers
      const headers = (req.headers || []).map((h: any) => ({
        key: h.name,
        value: h.value,
        enabled: true,
      }));

      // Extract query params
      const queryParams = (req.queryString || []).map((q: any) => ({
        key: q.name,
        value: q.value,
        enabled: true,
      }));

      // Extract body
      let body: RequestBody | undefined;
      if (req.postData) {
        const mimeType = req.postData.mimeType || '';
        if (mimeType.includes('json')) {
          body = {
            type: 'raw' as const,
            content: req.postData.text || '',
          };
        } else if (mimeType.includes('form-urlencoded')) {
          body = {
            type: 'x-www-form-urlencoded' as const,
            content: req.postData.text || '',
          };
        } else if (mimeType.includes('form-data')) {
          body = {
            type: 'form-data' as const,
            content: req.postData.text || '',
          };
        } else {
          body = {
            type: 'raw' as const,
            content: req.postData.text || '',
          };
        }
      }

      // Create request
      const request: Request = {
        id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: `${method} ${new URL(url).pathname}`,
        description: `Imported from HAR - ${entry.startedDateTime || ''}`,
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
      console.error('[HARImporter] Error converting entry:', error);
      return null;
    }
  }

  /**
   * Get example HAR content
   */
  getExample(): string {
    return JSON.stringify(
      {
        log: {
          version: '1.2',
          creator: { name: 'LocalAPI', version: '1.0' },
          entries: [
            {
              startedDateTime: '2024-01-01T00:00:00.000Z',
              request: {
                method: 'GET',
                url: 'https://api.example.com/users',
                headers: [
                  { name: 'Accept', value: 'application/json' },
                ],
                queryString: [],
              },
              response: {
                status: 200,
                statusText: 'OK',
              },
            },
          ],
        },
      },
      null,
      2
    );
  }
}
