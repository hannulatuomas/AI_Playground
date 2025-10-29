import React, { useState, useEffect } from 'react';
import CellResultsTable from './CellResultsTable';
import { FieldTooltip } from './FieldTooltip';
import NotebookCellOutput from './NotebookCellOutput';

interface MongoDBCellProps {
  value: string;
  onChange: (v: string) => void;
  onRun?: () => void;
  executing?: boolean;
  error?: string | null;
  result?: any[];
  schemaTables?: import('../schemaTypes').DbTableSchema[];
  onVisualize?: (data: any[]) => void;
}

export const MongoDBCell: React.FC<MongoDBCellProps> = function MongoDBCell({ value, onChange, onRun, executing, error, result, schemaTables, onVisualize }) {
  const [collection, setCollection] = useState('');
  const [queryType, setQueryType] = useState<'find' | 'aggregate'>('find');
  const [query, setQuery] = useState('{}');
  const [validationError, setValidationError] = useState<string | null>(null);

  // Live validation on input changes
  useEffect(() => {
    setValidationError(validate());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [collection, queryType, query]);

  useEffect(() => {
    if (schemaTables && schemaTables.length && !collection) {
      setCollection(schemaTables[0].table);
    }
  }, [schemaTables]);

  const validate = () => {
    if (!collection) return 'Please select a collection.';
    try {
      const parsed = JSON.parse(query);
      if (queryType === 'find' && (typeof parsed !== 'object' || Array.isArray(parsed))) {
        return 'Find query must be a JSON object.';
      }
      if (queryType === 'aggregate' && !Array.isArray(parsed)) {
        return 'Aggregate pipeline must be a JSON array.';
      }
    } catch (e) {
      return 'Query must be valid JSON.';
    }
    return null;
  };

  const handleRun = () => {
    const err = validate();
    setValidationError(err);
    if (err) return;
    const payload = JSON.stringify({ collection, queryType, query });
    onChange(payload);
    onRun && onRun();
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center',marginBottom: 10 }}>
        <label htmlFor="mongodb-collection-select">
          Collection
          <FieldTooltip id="mongodb-collection-tooltip" text="Select the MongoDB collection to query." />
        </label>
        <select id="mongodb-collection-select" value={collection} onChange={e => setCollection(e.target.value)}
          aria-label="Select MongoDB collection">
          {schemaTables && schemaTables.map(t => <option key={t.table} value={t.table}>{t.table}</option>)}
        </select>
        <label htmlFor="mongodb-type-select">
          Type
          <FieldTooltip id="mongodb-type-tooltip" text="Choose between a find (object) or aggregate (pipeline) query." />
        </label>
        <select id="mongodb-type-select" value={queryType} onChange={e => setQueryType(e.target.value as 'find' | 'aggregate')}
          aria-label="Select query type" aria-describedby="mongodb-type-tooltip" style={{ backgroundColor: 'var(--color-bg)', color: 'var(--color-text)', border: '1px solid var(--color-border)', borderRadius: 4, padding: 6, fontSize: 14, fontFamily: 'inherit', marginLeft: 10 }}>
          <option value="find">find</option>
          <option value="aggregate">aggregate</option>
        </select>
        <button onClick={handleRun} disabled={executing || !!validationError} style={{ background: 'var(--color-primary)', color: 'var(--color-text-light)', border: 'none', borderRadius: 5, padding: '0 12px', fontWeight: 600, fontSize: 16, cursor: executing || !!validationError ? 'not-allowed' : 'pointer', height: 32, marginLeft: 10 }}
          aria-label="Run MongoDB query">Run</button>
      </div>
      <div style={{ marginBottom: 10 }}>
        <label htmlFor="mongodb-query-textarea">
          Query/Pipeline (JSON)
          <FieldTooltip
            id="mongodb-query-tooltip"
            text={queryType === 'find'
              ? 'Enter a MongoDB find query as a JSON object. E.g. { "field": "value" }'
              : 'Enter an aggregation pipeline as a JSON array. E.g. [{ "$match": {}}]'}
          />
        </label>
        <textarea
          id="mongodb-query-textarea"
          rows={4}
          style={{ width: '100%', fontFamily: 'monospace', fontSize: 14, borderRadius: 4, border: '1px solid var(--color-border-accent)', marginTop: 4, padding: 6 }}
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder={queryType === 'find' ? '{ "field": "value" }' : '[{ "$match": {}}]'}
          aria-label="MongoDB query input"
          aria-describedby="mongodb-query-desc"
        />
        <div id="mongodb-query-desc" style={{ fontSize: 12, color: 'var(--color-disabled-text)', marginTop: 2 }}>
          {queryType === 'find' ? 'Enter a MongoDB find query as a JSON object. E.g. { "field": "value" }' : 'Enter an aggregation pipeline as a JSON array. E.g. [{ "$match": {}}]'}
        </div>
        {validationError && (
          <div style={{ color: 'var(--color-error)', fontSize: 14, marginTop: 4 }} aria-live="polite">{validationError}</div>
        )}
      </div>
      <NotebookCellOutput executing={executing} error={error} result={result} onVisualize={onVisualize} />
    </div>
  );
};


