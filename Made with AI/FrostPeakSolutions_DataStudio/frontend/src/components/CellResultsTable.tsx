import React, { useState, useRef } from 'react';
import { exportQueryResult, triggerFileDownload } from '../services/exportService';
import { ExportFormat, ExportOptions, QueryResult } from '../types';

interface CellResultsTableProps {
  results: any[];
  onVisualize?: (data: any[]) => void;
}


export default function CellResultsTable({ results, onVisualize }: CellResultsTableProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [columns, setColumns] = useState(() => (results.length ? Object.keys(results[0]) : []));
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const dragColIdx = useRef<number | null>(null);

  // Sorting logic
  const sortedResults = React.useMemo(() => {
    if (!sortKey) return results;
    const sorted = [...results].sort((a, b) => {
      if (a[sortKey] === b[sortKey]) return 0;
      if (a[sortKey] == null) return 1;
      if (b[sortKey] == null) return -1;
      if (typeof a[sortKey] === 'number' && typeof b[sortKey] === 'number') {
        return sortDirection === 'asc' ? a[sortKey] - b[sortKey] : b[sortKey] - a[sortKey];
      }
      return sortDirection === 'asc'
        ? String(a[sortKey]).localeCompare(String(b[sortKey]))
        : String(b[sortKey]).localeCompare(String(a[sortKey]));
    });
    return sorted;
  }, [results, sortKey, sortDirection]);

  // Drag-and-drop logic for columns
  function handleDragStart(idx: number) {
    dragColIdx.current = idx;
  }
  function handleDragOver(e: React.DragEvent<HTMLTableHeaderCellElement>, idx: number) {
    e.preventDefault();
    if (dragColIdx.current === null || dragColIdx.current === idx) return;
    const newColumns = [...columns];
    const [removed] = newColumns.splice(dragColIdx.current, 1);
    newColumns.splice(idx, 0, removed);
    setColumns(newColumns);
    dragColIdx.current = idx;
  }
  function handleDragEnd() {
    dragColIdx.current = null;
  }

  // Export state
  const [exportFormat, setExportFormat] = useState<ExportFormat>(ExportFormat.JSON);
  const [exporting, setExporting] = useState(false);

  // Helper to convert results[] to QueryResult for export
  function toQueryResult(): QueryResult {
    const columns = columnsFromResults(results);
    return {
      columns: columns.map(name => ({ name, type: typeof results[0]?.[name], nullable: true })),
      rows: results.map(row => columns.map(col => row[col])),
      rowCount: results.length,
    };
  }
  function columnsFromResults(rows: any[]): string[] {
    if (!rows.length) return [];
    return Object.keys(rows[0]);
  }

  const handleExport = async () => {
    setExporting(true);
    try {
      const queryResult = toQueryResult();
      const options: ExportOptions = {
        format: exportFormat,
        includeHeaders: true,
        prettyPrint: exportFormat === ExportFormat.JSON,
      };
      const blob = await exportQueryResult(queryResult, options);
      const filename = `query-results.${exportFormat}`;
      triggerFileDownload(blob, filename);
    } catch (err) {
      alert('Failed to export query results: ' + (err instanceof Error ? err.message : String(err)));
    } finally {
      setExporting(false);
    }
  };

  return (
    <div style={{ marginTop: 12, marginBottom: 8 }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 6 }}>
        <strong style={{ flex: 1 }}>Result Table</strong>
        <select
          value={exportFormat}
          onChange={e => setExportFormat(e.target.value as ExportFormat)}
          style={{ marginRight: 8, padding: '2px 8px', borderRadius: 4, border: '1px solid var(--color-border-accent)', fontSize: 14 }}
          aria-label="Select export format"
          aria-describedby="export-format-desc"
        >
          <option value={ExportFormat.JSON}>JSON</option>
          <option value={ExportFormat.CSV}>CSV</option>
          <option value={ExportFormat.XML}>XML</option>
        </select>
        <button
          onClick={handleExport}
          disabled={exporting || !results.length}
          style={{ background: 'var(--color-primary)', color: 'var(--color-text-light)', border: 'none', borderRadius: 5, padding: '2px 12px', cursor: 'pointer', fontSize: 15, marginRight: 8 }}
          title="Export query results"
          aria-label="Export query results"
        >
          {exporting ? 'Exporting…' : 'Export'}
        </button>
        <button
          onClick={() => setCollapsed(c => !c)}
          style={{ background: 'var(--color-primary-light)', border: '1px solid var(--color-border-accent)', borderRadius: 5, padding: '2px 12px', cursor: 'pointer', fontSize: 15, marginRight: 8 }}
          aria-label={collapsed ? 'Expand result table' : 'Collapse result table'}
        >
          {collapsed ? 'Expand' : 'Collapse'}
        </button>
        <button
          onClick={() => typeof onVisualize === 'function' && onVisualize(results)}
          style={{ background: 'var(--color-accent)', color: 'var(--color-text-light)', border: 'none', borderRadius: 5, padding: '2px 12px', cursor: 'pointer', fontSize: 15 }}
          title="Visualize as Chart"
          aria-label="Visualize results as chart"
          aria-describedby="visualize-button-desc"
        >
          Visualize as Chart
        </button>
      </div>
      {collapsed ? (
        <div style={{ color: 'var(--color-primary)', fontSize: 15, padding: '8px 0' }} role="region" aria-label="Result table summary">
          <b>{results.length}</b> rows, <b>{columns.length}</b> columns
          {columns.length ? (
            <span style={{ color: 'var(--color-disabled-text)', marginLeft: 12 }}>Columns: {columns.join(', ')}</span>
          ) : null}
        </div>
      ) : (
        <div style={{ width: '100%', overflow: 'auto', maxHeight: 320 }} role="region" aria-label="Query results table">
          <table style={{ borderCollapse: 'collapse', width: '100%' }}>
            <caption style={{ position: 'absolute', left: '-9999px' }}>Query results</caption>
            <thead>
              <tr>
                {columns.map((key, idx) => (
                  <th
                    key={key}
                    draggable
                    onDragStart={() => handleDragStart(idx)}
                    onDragOver={e => handleDragOver(e, idx)}
                    onDragEnd={handleDragEnd}
                    onDrop={handleDragEnd}
                    onClick={() => {
                      if (sortKey === key) {
                        setSortDirection(d => (d === 'asc' ? 'desc' : 'asc'));
                      } else {
                        setSortKey(key);
                        setSortDirection('asc');
                      }
                    }}
                    style={{
                      borderBottom: '1px solid var(--color-border)',
                      fontWeight: 600,
                      fontSize: 14,
                      color: 'var(--color-primary)',
                      padding: '4px 8px',
                      textAlign: 'left',
                      cursor: 'pointer',
                      background: sortKey === key ? 'var(--color-primary-light)' : 'var(--color-bg-alt)',
                      userSelect: 'none',
                      minWidth: 60,
                    }}
                    title="Drag to reorder, click to sort"
                    aria-label={`Column ${key}`}
                  >
                    {key}
                    {sortKey === key ? (sortDirection === 'asc' ? ' ▲' : ' ▼') : ''}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sortedResults.map((row, i) => (
                <tr key={i}>
                  {columns.map((col, j) => (
                    <td key={j} style={{ borderBottom: '1px solid var(--color-border)', fontSize: 14, color: 'var(--color-text)', padding: '4px 8px' }}>{String(row[col])}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
