// JSON Exporter for QueryResult
import { QueryResult, ExportOptions } from '../../typesExportImport';

export function exportAsJson(result: QueryResult, options: ExportOptions): string {
    return options.prettyPrint
        ? JSON.stringify(result, null, 2)
        : JSON.stringify(result);
}
