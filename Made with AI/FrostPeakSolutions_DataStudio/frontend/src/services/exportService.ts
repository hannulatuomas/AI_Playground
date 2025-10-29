// Service functions for calling backend export endpoints
import { ExportFormat, ExportOptions, QueryResult, Notebook } from '../types';

const BASE_URL = '/api';

export async function exportQueryResult(result: QueryResult, options: ExportOptions): Promise<Blob> {
    const res = await fetch(`${BASE_URL}/query/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ result, options }),
    });
    if (!res.ok) throw new Error('Failed to export query result');
    const blob = await res.blob();
    return blob;
}

export async function exportNotebook(notebook: Notebook, options: ExportOptions): Promise<Blob> {
    const res = await fetch(`${BASE_URL}/notebook/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notebook, options }),
    });
    if (!res.ok) throw new Error('Failed to export notebook');
    const blob = await res.blob();
    return blob;
}

export async function exportChartData(result: QueryResult, options: ExportOptions): Promise<Blob> {
    const res = await fetch(`${BASE_URL}/chart/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ result, options }),
    });
    if (!res.ok) throw new Error('Failed to export chart data');
    const blob = await res.blob();
    return blob;
}

// Helper for triggering file downloads
export function triggerFileDownload(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }, 0);
}
