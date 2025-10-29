// Central export service entry point
import { ExportFormat, Notebook, QueryResult, ExportOptions } from '../../typesExportImport';
import { exportAsJson } from './jsonExporter';
import { exportAsCsv } from './csvExporter';
import { exportAsXml } from './xmlExporter';
import { exportNotebook } from './notebookExporter';
import { exportChartData, exportChartImage } from './chartExporter';

export { exportNotebook };
export { exportChartData, exportChartImage };

/**
 * Export a query result in the selected format (JSON, CSV, XML).
 */
export function exportQueryResult(result: QueryResult, options: ExportOptions): string {
    switch (options.format) {
        case ExportFormat.JSON:
            return exportAsJson(result, options);
        case ExportFormat.CSV:
            return exportAsCsv(result, options);
        case ExportFormat.XML:
            return exportAsXml(result, options);
        default:
            throw new Error(`Unsupported export format: ${options.format}`);
    }
}

// Add similar functions for notebook and chart export as needed.
