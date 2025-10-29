import React, { useState } from 'react';
import { FieldTooltip } from './FieldTooltip';
import { useTableColumns } from './useTableColumns';
import { useConnectionContext } from './ConnectionContext';
import { DbTableSchema } from '../schemaTypes';
import { getApiUrl } from '../apiConfig';

interface SchemaCellProps {
  uid: string | null;
}

const SchemaCell: React.FC<SchemaCellProps> = ({ uid: initialUid }) => {
  const { connections } = useConnectionContext();
  const [uid, setUid] = useState<string | null>(initialUid ?? (connections[0]?.uid ?? null));
  const [tables, setTables] = useState<DbTableSchema[]>([]);
  const [tablesLoading, setTablesLoading] = useState(false);
  const [tablesError, setTablesError] = useState<string | null>(null);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [showSchema, setShowSchema] = useState(false);
  const [tablesFetched, setTablesFetched] = useState(false);

  // Lazy-load columns only when needed
  const { columns, loading: columnsLoading, error: columnsError } = useTableColumns(
    uid,
    showSchema && selectedTable ? selectedTable : null,
    showSchema && !!selectedTable
  );

  const fetchTables = async () => {
    if (!uid) return;
    setTablesLoading(true);
    setTablesError(null);
    setTables([]);
    setSelectedTable('');
    setShowSchema(false);
    try {
      // Find the full connection object if possible
      const connObj = connections.find(c => c.uid === uid) || null;
      let body: any;
      if (connObj) {
        // Always send the full connection object, including uid
        body = { ...connObj };
      } else {
        // If we can't find the connection, disable the fetch button and show an error
        setTablesError('Connection details not found for this UID. Please reselect or recreate the connection.');
        setTablesLoading(false);
        return;
      }
      const res = await fetch(getApiUrl('schema/tables'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      if (data.success && Array.isArray(data.tables)) {
        setTables(data.tables.map((t: string) => ({ table: t, columns: [] })));
        setTablesFetched(true);
      } else {
        setTablesError(data.error || 'Failed to fetch tables');
        setTables([]);
        setTablesFetched(false);
      }
    } catch (err: any) {
      setTablesError(err.message || 'Failed to fetch tables');
      setTables([]);
      setTablesFetched(false);
    } finally {
      setTablesLoading(false);
    }
  };

  // Reset state if connection changes
  React.useEffect(() => {
    setTables([]);
    setTablesFetched(false);
    setTablesError(null);
    setSelectedTable('');
    setShowSchema(false);
  }, [uid]);

  return (
    <div className="schema-cell" style={{ padding: 16, background: 'var(--color-bg-alt)', borderRadius: 8, border: '1px solid var(--color-border-light)', margin: '12px 0' }}>
      <div style={{ marginBottom: 10, display: 'flex', alignItems: 'center', gap: 12 }}>
        <label style={{ fontWeight: 500 }} htmlFor="conn-select">Connection:
          <FieldTooltip id="schema-conn-tooltip" text="Choose a database connection. Only connections with schema support are listed." />
        </label>
        <select
          id="conn-select"
          value={uid ?? ''}
          onChange={e => {
            setUid(e.target.value || null);
          }}
          style={{ padding: '4px 10px', borderRadius: 4, border: '1px solid var(--color-border-accent)', minWidth: 160 }}
        >
          <option value="" disabled>
            {connections.length === 0 ? 'No connections available' : 'Select connection'}
          </option>
          {connections.map(c => (
            <option key={c.uid} value={c.uid}>{c.displayName || `${c.type}://${c.host || ''}${c.database ? '/' + c.database : ''}`}</option>
          ))}
        </select>
        {uid && (
          <button
            className="schemaAddButton"
            style={{ marginLeft: 12 }}
            onClick={fetchTables}
            disabled={tablesLoading}
          >
            {tablesLoading ? 'Fetching Tables...' : 'Fetch Tables'}
          </button>
        )} 
        {tablesFetched && tables.length > 0 && (
          <>
            <label style={{ fontWeight: 500, marginLeft: 12 }} htmlFor="table-select">Table:
              <FieldTooltip id="schema-table-tooltip" text="Select a table to view its schema." />
            </label>
            <select
              id="table-select"
              value={selectedTable}
              onChange={e => {
                setSelectedTable(e.target.value);
                setShowSchema(false);
              }}
              style={{ marginLeft: 8, padding: '4px 10px', borderRadius: 4, border: '1px solid var(--color-border-accent)', minWidth: 120 }}
              disabled={tables.length === 0}
            >
              <option value="" disabled>
                Choose a table
              </option>
              {[...tables]
  .sort((a, b) =>
    a.table.localeCompare(b.table, undefined, { sensitivity: 'base', numeric: true })
  )
  .map(t => (
    <option key={t.table} value={t.table}>{t.table}</option>
  ))}
            </select>
            <button
              className="schemaAddButton"
              data-testid="schema-add-btn"
              onClick={() => setShowSchema(true)}
              disabled={!selectedTable}
            >
              Show Schema
            </button>
          </>
        )}
      </div>
      {tablesError && (
        <div style={{ color: 'red', marginBottom: 8 }}>
          <span>Error: {tablesError}</span>
          <button className="schemaRetryButton" onClick={fetchTables}>
            Retry
          </button>
        </div>
      )}
      <div style={{ color: '#888', fontSize: 12, marginBottom: 4 }}>
        <FieldTooltip id="schema-cell-help" text="A schema describes the structure of a table: columns, types, and nullability. Use this cell to inspect table schemas." />
      </div>
      {tablesFetched && tables.length === 0 && !tablesError && (
        <div style={{ color: 'var(--color-disabled-text)', marginBottom: 8 }}>
          No tables found for this connection. Please check your database or connection settings.
        </div>
      )}
      {showSchema && selectedTable && (
        <div style={{ background: 'var(--color-bg)', border: '1px solid var(--color-border-light)', borderRadius: 6, padding: 12, marginTop: 8 }}>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>Schema for <span style={{ color: 'var(--color-primary)' }}>{selectedTable}</span>:
            <FieldTooltip id="schema-schema-tooltip" text="This table shows the columns, types, and nullability for the selected table. See documentation for more info." />
            <a href="https://en.wikipedia.org/wiki/Database_schema" target="_blank" rel="noopener noreferrer" style={{ marginLeft: 8, fontSize: 12, color: 'var(--color-primary)', textDecoration: 'underline' }}>Schema Docs</a>
          </div>
          {columnsError && (
            <div style={{ color: 'var(--color-error)', marginBottom: 8 }}>Error: {columnsError}</div>
          )}
          {columnsLoading && (
            <div style={{ color: 'var(--color-disabled-text)', marginBottom: 8 }}>Loading columns...</div>
          )}
          {!columnsLoading && columns && columns.length > 0 && (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', padding: 4, borderBottom: '1px solid var(--color-border-light)' }}>Column Name</th>
                  <th style={{ textAlign: 'left', padding: 4, borderBottom: '1px solid var(--color-border-light)' }}>Type</th>
                  <th style={{ textAlign: 'left', padding: 4, borderBottom: '1px solid var(--color-border-light)' }}>Nullable</th>
                </tr>
              </thead>
              <tbody>
                {columns.map((col, i) => (
                  <tr key={col.name + i}>
                    <td style={{ padding: 4, borderBottom: '1px solid var(--color-bg-alt)' }}>{col.name}</td>
                    <td style={{ padding: 4, borderBottom: '1px solid var(--color-bg-alt)' }}>{col.type ?? '-'}</td>
                    <td style={{ padding: 4, borderBottom: '1px solid var(--color-bg-alt)' }}>{col.nullable === false ? 'No' : 'Yes'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {!columnsLoading && columns && columns.length === 0 && !columnsError && (
            <div style={{ color: 'var(--color-disabled-text)' }}>No columns found.</div>
          )}
        </div>
      )}
    </div>
  );
};

export default SchemaCell;
