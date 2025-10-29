// CSV Exporter for QueryResult
import { QueryResult, ExportOptions } from '../../typesExportImport';

export function exportAsCsv(result: QueryResult, options: ExportOptions): string {
    const rows = result.rows;
    const columns = result.columns.map(col => col.name);
    const includeHeaders = options.includeHeaders !== false;
    let csv = '';
    if (includeHeaders) {
        csv += columns.join(',') + '\n';
    }
    for (const row of rows) {
        csv += row.map(cell => (cell !== null && cell !== undefined ? JSON.stringify(cell) : '')).join(',') + '\n';
    }
    return csv;
}
