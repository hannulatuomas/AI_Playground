// Notebook Exporter for full notebook export
import { Notebook, ExportFormat, ExportOptions } from '../../typesExportImport';

export function exportNotebook(notebook: Notebook, options: ExportOptions): string {
    switch (options.format) {
        case ExportFormat.JSON:
            return options.prettyPrint
                ? JSON.stringify(notebook, null, 2)
                : JSON.stringify(notebook);
        // CSV and XML for notebook (optional, not typical)
        default:
            throw new Error(`Unsupported export format for notebook: ${options.format}`);
    }
}
