// Chart Exporter for exporting chart data or images
import { ExportFormat, ExportOptions, QueryResult, ChartExportOptions } from '../../typesExportImport';

// For data export (uses same logic as query result)
export function exportChartData(result: QueryResult, options: ExportOptions): string {
    // Reuse query result export logic for chart data
    // (In real use, import and call exportQueryResult if needed)
    switch (options.format) {
        case ExportFormat.JSON:
            return options.prettyPrint
                ? JSON.stringify(result, null, 2)
                : JSON.stringify(result);
        case ExportFormat.CSV:
            // Simple CSV export logic (reuse or improve as needed)
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
        case ExportFormat.XML:
            let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<results>\n';
            for (const row of result.rows) {
                xml += '  <row>\n';
                result.columns.forEach((col, idx) => {
                    xml += `    <${col.name}>${row[idx] !== undefined && row[idx] !== null ? row[idx] : ''}</${col.name}>\n`;
                });
                xml += '  </row>\n';
            }
            xml += '</results>\n';
            return xml;
        default:
            throw new Error(`Unsupported export format for chart data: ${options.format}`);
    }
}

// For image export, this is a placeholder (real image export is frontend-driven)
export function exportChartImage(options: ChartExportOptions): Buffer | null {
    // Not implemented server-side; handled in frontend
    return null;
}
