// XML Exporter for QueryResult
import { QueryResult, ExportOptions } from '../../typesExportImport';

export function exportAsXml(result: QueryResult, options: ExportOptions): string {
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
}
