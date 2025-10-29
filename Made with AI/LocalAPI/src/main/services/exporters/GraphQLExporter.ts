// GraphQL Schema Exporter
import type {
  Exporter,
  ImportExportFormat,
  ImportExportOptions,
  ExportResult,
} from '../../../types/import-export';
import type { Request } from '../../../types/models';

export class GraphQLExporter implements Exporter {
  readonly format: ImportExportFormat = 'graphql-schema';
  readonly name = 'GraphQL Schema';
  readonly description = 'Export as GraphQL SDL schema';
  readonly fileExtensions = ['.graphql', '.gql'];

  async exportCollections(collections: any[], options: ImportExportOptions = {}): Promise<ExportResult> {
    try {
      const queries: string[] = [];
      const mutations: string[] = [];

      for (const collection of collections) {
        for (const request of collection.requests) {
          if (request.name.toLowerCase().includes('mutation')) {
            mutations.push(`  ${request.name.replace(/[^a-zA-Z0-9]/g, '')}: String`);
          } else {
            queries.push(`  ${request.name.replace(/[^a-zA-Z0-9]/g, '')}: String`);
          }
        }
      }

      const schema = `type Query {\n${queries.join('\n') || '  _empty: String'}\n}\n\ntype Mutation {\n${mutations.join('\n') || '  _empty: String'}\n}`;

      return {
        success: true,
        data: schema,
        format: this.format,
        metadata: { exportedAt: new Date(), itemCount: queries.length + mutations.length, size: schema.length },
      };
    } catch (error) {
      return {
        success: false,
        format: this.format,
        errors: [error instanceof Error ? error.message : 'Export failed'],
      };
    }
  }

  async exportRequest(request: Request, options: ImportExportOptions = {}): Promise<ExportResult> {
    try {
      const data = request.body?.content || `query { ${request.name} }`;

      return {
        success: true,
        data,
        format: this.format,
        metadata: { exportedAt: new Date(), itemCount: 1, size: data.length },
      };
    } catch (error) {
      return {
        success: false,
        format: this.format,
        errors: [error instanceof Error ? error.message : 'Export failed'],
      };
    }
  }

  async exportRequests(requests: Request[], options: ImportExportOptions = {}): Promise<ExportResult> {
    try {
      const queries = requests.map(req => req.body?.content || `query { ${req.name} }`).join('\n\n');

      return {
        success: true,
        data: queries,
        format: this.format,
        metadata: { exportedAt: new Date(), itemCount: requests.length, size: queries.length },
      };
    } catch (error) {
      return {
        success: false,
        format: this.format,
        errors: [error instanceof Error ? error.message : 'Export failed'],
      };
    }
  }
}
