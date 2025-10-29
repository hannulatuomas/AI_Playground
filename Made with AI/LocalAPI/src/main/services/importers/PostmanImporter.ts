// Postman Collection Importer
import type {
  Importer,
  ImportExportFormat,
  ImportExportOptions,
  ImportResult,
} from '../../../types/import-export';
import type { Collection, Request, Environment, Variable, HttpMethod, RequestBody } from '../../../types/models';

interface PostmanCollection {
  info: {
    name: string;
    description?: string;
    schema: string;
    _postman_id?: string;
  };
  item: PostmanItem[];
  variable?: PostmanVariable[];
  auth?: any;
  event?: any[];
}

interface PostmanItem {
  name: string;
  description?: string;
  request?: PostmanRequest | string;
  item?: PostmanItem[];
  event?: any[];
  variable?: PostmanVariable[];
}

interface PostmanRequest {
  method: string;
  header?: Array<{ key: string; value: string; disabled?: boolean }>;
  url: PostmanUrl | string;
  body?: {
    mode: string;
    raw?: string;
    urlencoded?: Array<{ key: string; value: string; disabled?: boolean }>;
    formdata?: Array<{ key: string; value: string; type?: string; disabled?: boolean }>;
    graphql?: { query: string; variables?: string };
  };
  auth?: any;
  description?: string;
}

interface PostmanUrl {
  raw: string;
  protocol?: string;
  host?: string[];
  port?: string;
  path?: string[];
  query?: Array<{ key: string; value: string; disabled?: boolean }>;
  variable?: Array<{ key: string; value: string }>;
}

interface PostmanVariable {
  key: string;
  value: string;
  type?: string;
  disabled?: boolean;
}

/**
 * Postman Collection v2/v2.1 Importer
 */
export class PostmanImporter implements Importer {
  readonly format: ImportExportFormat = 'postman-v2.1';
  readonly name = 'Postman Collection';
  readonly description = 'Import Postman Collection v2.0 and v2.1 format';
  readonly fileExtensions = ['.json'];

  /**
   * Check if content can be imported
   */
  canImport(content: string): boolean {
    try {
      const json = JSON.parse(content);
      return (
        json.info &&
        json.info.schema &&
        json.info.schema.includes('postman')
      );
    } catch {
      return false;
    }
  }

  /**
   * Import Postman collection
   */
  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const postmanCollection: PostmanCollection = JSON.parse(content);

      // Convert to LocalAPI format
      const collections: Collection[] = [];
      const requests: Request[] = [];
      const variables: Variable[] = [];

      // Create main collection
      const collection: Collection = {
        id: postmanCollection.info._postman_id || `col-${Date.now()}`,
        name: postmanCollection.info.name,
        description: postmanCollection.info.description || '',
        requests: [],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      // Process items (requests and folders)
      const processedRequests = this.processItems(
        postmanCollection.item,
        collection.id,
        null
      );
      requests.push(...processedRequests);

      // Process collection variables
      if (postmanCollection.variable) {
        const collectionVars = this.processVariables(
          postmanCollection.variable,
          collection.id,
          'collection'
        );
        variables.push(...collectionVars);
      }

      collections.push(collection);

      console.log(
        `[PostmanImporter] Imported ${collections.length} collections, ${requests.length} requests, ${variables.length} variables`
      );

      return {
        success: true,
        collections,
        requests,
        variables,
        metadata: {
          format: this.format,
          itemCount: collections.length + requests.length,
          importedAt: new Date(),
        },
      };
    } catch (error) {
      console.error('[PostmanImporter] Import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import Postman collection',
        ],
      };
    }
  }

  /**
   * Process Postman items (requests and folders)
   */
  private processItems(
    items: PostmanItem[],
    collectionId: string,
    parentId: string | null
  ): Request[] {
    const requests: Request[] = [];

    for (const item of items) {
      // If item has sub-items, it's a folder
      if (item.item && item.item.length > 0) {
        // Process folder items recursively
        const folderRequests = this.processItems(
          item.item,
          collectionId,
          item.name
        );
        requests.push(...folderRequests);
      } else if (item.request) {
        // It's a request
        const request = this.convertRequest(item, collectionId, parentId);
        if (request) {
          requests.push(request);
        }
      }
    }

    return requests;
  }

  /**
   * Convert Postman request to LocalAPI request
   */
  private convertRequest(
    item: PostmanItem,
    collectionId: string,
    folder: string | null
  ): Request | null {
    try {
      const postmanRequest =
        typeof item.request === 'string'
          ? { method: 'GET', url: item.request }
          : item.request;

      if (!postmanRequest) return null;

      // Parse URL
      const url = this.parseUrl(postmanRequest.url);

      // Parse headers
      const headers = postmanRequest.header?.map((h) => ({
        key: h.key,
        value: h.value,
        enabled: !h.disabled,
      })) || [];

      // Parse query parameters
      const queryParams = this.parseQueryParams(postmanRequest.url);

      // Parse body
      const body = this.parseBody(postmanRequest.body);

      // Create request
      const request: Request = {
        id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: item.name,
        description: item.description || postmanRequest.description || '',
        protocol: 'REST' as const,
        method: postmanRequest.method.toUpperCase() as HttpMethod,
        url: url,
        headers: headers,
        queryParams: queryParams,
        body: body as RequestBody | undefined,
        collectionId: collectionId,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      return request;
    } catch (error) {
      console.error('[PostmanImporter] Error converting request:', error);
      return null;
    }
  }

  /**
   * Parse Postman URL
   */
  private parseUrl(url: PostmanUrl | string): string {
    if (typeof url === 'string') {
      return url;
    }

    if (url.raw) {
      return url.raw;
    }

    // Construct URL from parts
    const protocol = url.protocol || 'https';
    const host = url.host?.join('.') || 'localhost';
    const port = url.port ? `:${url.port}` : '';
    const path = url.path?.join('/') || '';

    return `${protocol}://${host}${port}/${path}`;
  }

  /**
   * Parse query parameters from URL
   */
  private parseQueryParams(url: PostmanUrl | string): Array<{
    key: string;
    value: string;
    enabled: boolean;
  }> {
    if (typeof url === 'string') {
      // Extract query params from string URL
      const urlObj = new URL(url);
      const params: Array<{ key: string; value: string; enabled: boolean }> = [];
      urlObj.searchParams.forEach((value, key) => {
        params.push({ key, value, enabled: true });
      });
      return params;
    }

    if (url.query) {
      return url.query.map((q) => ({
        key: q.key,
        value: q.value,
        enabled: !q.disabled,
      }));
    }

    return [];
  }

  /**
   * Parse request body
   */
  private parseBody(body?: PostmanRequest['body']): RequestBody | undefined {
    if (!body) return undefined;

    switch (body.mode) {
      case 'raw':
        return {
          type: 'raw' as const,
          content: body.raw || '',
        };

      case 'urlencoded':
        return {
          type: 'x-www-form-urlencoded' as const,
          content: JSON.stringify(body.urlencoded || []),
        };

      case 'formdata':
        return {
          type: 'form-data' as const,
          content: JSON.stringify(body.formdata || []),
        };

      case 'graphql':
        return {
          type: 'graphql' as const,
          content: JSON.stringify(body.graphql || {}),
        };

      default:
        return {
          type: 'raw' as const,
          content: '',
        };
    }
  }

  /**
   * Process Postman variables
   */
  private processVariables(
    variables: PostmanVariable[],
    collectionId: string,
    scope: 'global' | 'environment' | 'collection'
  ): Variable[] {
    return variables
      .filter((v) => !v.disabled)
      .map((v) => {
        const varType = v.type === 'number' || v.type === 'boolean' || v.type === 'secret' 
          ? v.type 
          : 'string';
        return {
          key: v.key,
          value: v.value,
          type: varType as 'string' | 'number' | 'boolean' | 'secret',
          scope: scope,
          enabled: true,
        };
      });
  }

  /**
   * Get example Postman collection
   */
  getExample(): string {
    return JSON.stringify(
      {
        info: {
          name: 'Example Collection',
          schema:
            'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
        },
        item: [
          {
            name: 'Get Users',
            request: {
              method: 'GET',
              header: [],
              url: {
                raw: 'https://api.example.com/users',
                protocol: 'https',
                host: ['api', 'example', 'com'],
                path: ['users'],
              },
            },
          },
        ],
      },
      null,
      2
    );
  }
}
