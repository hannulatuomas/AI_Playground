// Types for notebook, cell, result, and export formats (backend)
// Extend and share with frontend as needed

export enum ExportFormat {
    JSON = 'json',
    CSV = 'csv',
    XML = 'xml',
}

export interface NotebookCell {
    id: string;
    type: 'sql' | 'chart' | 'markdown' | string;
    content: any;
    result?: QueryResult;
}

export interface Notebook {
    id: string;
    name: string;
    createdAt: string;
    updatedAt: string;
    cells: NotebookCell[];
    metadata?: Record<string, any>;
}

export interface QueryResult {
    columns: Array<{ name: string; type: string; nullable?: boolean }>;
    rows: any[][];
    rowCount: number;
    executionTimeMs?: number;
}

export interface ExportOptions {
    format: ExportFormat;
    includeHeaders?: boolean;
    prettyPrint?: boolean;
}

// Chart export types
export interface ChartExportOptions {
    asImage?: boolean;
    imageFormat?: 'png' | 'svg';
}
