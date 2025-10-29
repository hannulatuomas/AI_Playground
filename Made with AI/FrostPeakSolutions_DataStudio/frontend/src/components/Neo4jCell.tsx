import React, { useState, useEffect } from 'react';
import CellResultsTable from './CellResultsTable';
import { FieldTooltip } from './FieldTooltip';
import NotebookCellOutput from './NotebookCellOutput';

interface Neo4jCellProps {
  value: string;
  onChange: (v: string) => void;
  onRun?: () => void;
  executing?: boolean;
  error?: string | null;
  result?: any[];
  schemaTables?: import('../schemaTypes').DbTableSchema[];
  onVisualize?: (data: any[]) => void;
}

export const Neo4jCell: React.FC<Neo4jCellProps> = function Neo4jCell({ value, onChange, onRun, executing, error, result, schemaTables, onVisualize }) {
  const [label, setLabel] = useState('');
  const [cypher, setCypher] = useState('MATCH (n) RETURN n LIMIT 10');
  const [validationError, setValidationError] = useState<string | null>(null);

  // Live validation on input changes
  useEffect(() => {
    setValidationError(validate());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [label, cypher]);

  useEffect(() => {
    if (schemaTables && schemaTables.length && !label) {
      setLabel(schemaTables[0].table);
    }
  }, [schemaTables]);

  const validate = () => {
    if (!label) return 'Please select a label.';
    if (!cypher.trim()) return 'Cypher query cannot be empty.';
    // Optionally: check for basic Cypher structure
    if (!/match|return/i.test(cypher)) return 'Query should contain MATCH and RETURN.';
    return null;
  };

  const handleRun = () => {
    const err = validate();
    setValidationError(err);
    if (err) return;
    const payload = JSON.stringify({ label, cypher });
    onChange(payload);
    onRun && onRun();
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 10 }}>
        <label htmlFor="neo4j-label-select">
          Label
          <FieldTooltip id="neo4j-label-tooltip" text="Select the node label (table equivalent) to query." />
        </label>
        <select id="neo4j-label-select" value={label} onChange={e => setLabel(e.target.value)}
          aria-label="Select Neo4j label" aria-describedby="neo4j-label-tooltip"
          style={{ backgroundColor: 'var(--color-bg)', color: 'var(--color-text)', border: '1px solid var(--color-border)', borderRadius: 4, padding: 6 }}>
          {schemaTables && schemaTables.map(t => <option key={t.table} value={t.table}>{t.table}</option>)}
        </select>
        <button onClick={handleRun} disabled={executing || !!validationError}
          style={{ backgroundColor: 'var(--color-primary)', color: 'var(--color-text-light)', border: 'none', borderRadius: 5, padding: '0 12px', fontWeight: 600, fontSize: 16, cursor: executing || !!validationError ? 'not-allowed' : 'pointer', height: 32 }}
          aria-label="Run Neo4j query">▶ Run</button>
      </div>
      <div style={{ marginBottom: 10 }}>
        <label htmlFor="neo4j-cypher-textarea" aria-label="Cypher Query">
          Cypher Query
          <FieldTooltip id="neo4j-cypher-tooltip" text="Enter a Neo4j Cypher query. E.g. MATCH (n) RETURN n LIMIT 10" />
        </label>
        <textarea
          id="neo4j-cypher-textarea"
          rows={4}
          style={{ width: '100%', fontFamily: 'monospace', fontSize: 14, borderRadius: 4, border: '1px solid var(--color-border-accent)', marginTop: 4, padding: 6 }}
          value={cypher}
          onChange={e => setCypher(e.target.value)}
          placeholder={'MATCH (n) RETURN n LIMIT 10'}
          aria-label="Neo4j Cypher query input"
          aria-describedby="neo4j-cypher-desc"
        />
        <div id="neo4j-cypher-desc" style={{ fontSize: 12, color: 'var(--color-disabled-text)', marginTop: 2 }}>
          Enter a Neo4j Cypher query. Example: MATCH (n) RETURN n LIMIT 10
        </div>
        {validationError && (
          <div style={{ color: 'var(--color-error)', fontSize: 14, marginTop: 4 }} aria-live="polite">{validationError}</div>
        )}
      </div>
      <NotebookCellOutput executing={executing} error={error} result={result} onVisualize={onVisualize} />
    </div>
  );
};


