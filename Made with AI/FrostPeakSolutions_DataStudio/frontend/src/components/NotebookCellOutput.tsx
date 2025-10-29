import React from 'react';
import CellResultsTable from './CellResultsTable';

interface NotebookCellOutputProps {
  executing?: boolean;
  error?: string | null;
  result?: any[];
  onVisualize?: (data: any[]) => void;
}

/**
 * Modular output display for notebook cells (results, loading, error)
 */
const NotebookCellOutput: React.FC<NotebookCellOutputProps> = ({ executing, error, result, onVisualize }) => {
  return (
    <div role="region" aria-label="Cell output area">
      {executing && (
        <div style={{ color: 'var(--color-primary)', fontWeight: 500, margin: '16px 0' }} aria-live="polite">Running query...</div>
      )}
      {error && (
        <div style={{ background: 'var(--color-error-light)', color: 'var(--color-error)', border: '1px solid var(--color-border-light)', borderRadius: 5, marginTop: 12, padding: '10px 14px', fontWeight: 500, fontSize: 15 }} aria-live="polite">{error}</div>
      )}
      {Array.isArray(result) && result.length > 0 && (
        <CellResultsTable results={result} onVisualize={onVisualize} />
      )}
    </div>
  );
};

export default NotebookCellOutput;
