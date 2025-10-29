// File state (listing, refresh) is managed by the global file context; this component only previews a single file
import React, { useEffect, useState } from 'react';
import { getApiUrl } from '../apiConfig';
import * as Papa from 'papaparse';

interface FilePreviewProps {
  fileId: string;
  onClose: () => void;
}



function inferType(val: string): string {
  if (val === '' || val == null) return 'string';
  if (!isNaN(Number(val))) return val.includes('.') ? 'float' : 'int';
  if (val.toLowerCase() === 'true' || val.toLowerCase() === 'false') return 'boolean';
  // ISO date check
  if (/^\d{4}-\d{2}-\d{2}/.test(val)) return 'date';
  return 'string';
}

import { useFileContext } from './FileContext';
import { useFileSchema } from './useFileSchema';
import FileSchemaEditor from './FileSchemaEditor';
import { FileColumnSchema } from '../schemaTypes';
import SchemaStatusBadge from './SchemaStatusBadge';
import SchemaUnconfirmedBanner from './SchemaUnconfirmedBanner';

export default function FilePreview({ fileId, onClose }: FilePreviewProps) {
  const { files } = useFileContext();
  const file = files.find(f => f.id === fileId);
  if (!file) return <div style={{ padding: 24 }}>File not found.</div>;
  const { filename, type } = file;
  const { loadSchemaOverride, saveSchemaOverride, setStatus, status } = useFileSchema(fileId);


  const [content, setContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [schema, setSchema] = useState<{ name: string; type: string }[] | null>(null);
  const [editingSchema, setEditingSchema] = useState<{ name: string; type: string }[] | null>(null);
  const [editing, setEditing] = useState(false);
  const [xmlRoot, setXmlRoot] = useState<string | null>(null);

  // fileId === backend filename; always use fileId for backend operations
  useEffect(() => {
    fetch(getApiUrl(`files/${encodeURIComponent(fileId)}`))
      .then(res => res.ok ? res.text() : Promise.reject('Failed to fetch file'))
      .then(text => {
        setContent(text);
        if (type === 'csv') {
          const parsed = Papa.parse(text, { header: true, preview: 20 });
          if (parsed.meta.fields && parsed.data && Array.isArray(parsed.data)) {
            const types = parsed.meta.fields.map((f: string) => {
              // Get first non-empty value
              const vals = parsed.data.map((row: any) => row[f]).filter((v: string) => v !== undefined && v !== null && v !== '');
              const sample = vals[0];
              return { name: f, type: sample ? inferType(sample) : 'string' };
            });
            setSchema(types);
          }
        } else if (type && ['json'].includes(type)) {
          // Preview JSON using backend preview endpoint
          fetch(getApiUrl(`files/${encodeURIComponent(fileId)}/preview?lines=20`))
            .then(res => res.ok ? res.json() : Promise.reject('Failed to preview JSON file'))
            .then(data => {
              if (data.success && Array.isArray(data.rows) && data.rows.length > 0) {
                // Infer columns and types from sample
                const firstRow = data.rows[0];
                const columns = Object.keys(firstRow);
                const types = columns.map((col: string) => {
                  const sampleVal = data.rows.find((row: any) => row[col] !== undefined && row[col] !== null)?.[col];
                  return { name: col, type: sampleVal ? inferType(String(sampleVal)) : 'string' };
                });
                setSchema(types);
                setContent(JSON.stringify(data.rows, null, 2));
              } else {
                setSchema(null);
                setContent('No data');
              }
            })
            .catch(e => setError(String(e)));
        } else if (type === 'xml') {
          // Basic root element extraction
          const match = text.match(/<([\w-]+)[^>]*>/);
          setXmlRoot(match ? match[1] : null);
        }
      })
      .catch(e => setError(String(e)));
  }, [fileId, type]);

  return (
    <div style={{ padding: 24, background: 'var(--color-bg)', borderRadius: 8, boxShadow: '0 2px 12px var(--color-shadow)', maxWidth: 700, margin: '32px auto', position: 'relative' }}>
      <button onClick={onClose} style={{ position: 'absolute', right: 12, top: 12, background: 'var(--color-bg-alt)', border: 'none', borderRadius: 4, padding: '2px 10px', color: 'var(--color-text)' }}>Close</button>
      <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', color: 'var(--color-text)' }}>
        {file.filename}
        <SchemaStatusBadge status={status} style={{ marginLeft: 12 }} />
      </h3>
      {status === 'unconfirmed' && <SchemaUnconfirmedBanner style={{ background: 'var(--color-warning-bg)', color: 'var(--color-text)', padding: '8px 12px', borderRadius: 4, marginBottom: 12 }} />}

      <button
        style={{ background: 'var(--color-warning-bg)', color: 'var(--color-primary)', border: '1px solid var(--color-warning-border)', borderRadius: 4, padding: '4px 8px', fontSize: 14, marginBottom: 10, cursor: 'pointer' }}
        title="Import to Chart"
        // fileId === backend filename; prefer fileId for chart import
        onClick={() => window.dispatchEvent(new CustomEvent('openChartImportModal', { detail: { fileId, type } }))}
      >
        📊 Import to Chart
      </button>
      {['xml', 'json'].includes(type) && schema && (
  <FileSchemaEditor
    fileId={fileId}
    initialSchema={schema}
    status={status}
    editing={editing}
    setEditing={setEditing}
    onSave={(newSchema: FileColumnSchema[]) => {
      setSchema(newSchema);
      saveSchemaOverride(newSchema);
      setStatus('confirmed');
    }}
    onCancel={() => {
      setEditing(false);
    }}
  />
)}
      {/* CSV table preview */}
      {type && type === 'csv' && schema && content && (
        (() => {
          const parsed = Papa.parse(content, { header: true, preview: 10 });
          const rows = Array.isArray(parsed.data) ? parsed.data.slice(0, 10) : [];
          const useSchema = editing ? (editingSchema ?? schema) : schema;
          if (!rows.length) return null;
          return (
            <div style={{ marginBottom: 12 }}>
              <b>Sample Data:</b>
              <table style={{ borderCollapse: 'collapse', marginTop: 6 }}>
                <tbody>
                  {rows.map((row: any, i: number) => (
                    <tr key={i}>
                      {useSchema.map(col => (
                        <td key={col.name} style={{ border: '1px solid var(--color-border)', padding: '2px 8px', fontFamily: 'monospace', fontSize: 13 }}>{row[col.name]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        })()
      )}
      {/* XML table preview */}
      {type && type === 'xml' && content && (
        (() => {
          // Very basic: extract first 3 top-level elements
          const matches = Array.from(content.matchAll(/<([\w-]+)[^>]*>(.*?)<\/\1>/gs));
          if (!matches.length) return null;
          const headers = Array.from(new Set(matches.slice(0, 3).map(m => m[1])));
          return (
            <div style={{ marginBottom: 12 }}>
              <b>Sample XML Elements:</b>
              <table style={{ borderCollapse: 'collapse', marginTop: 6 }}>
                <thead>
                  <tr>
                    {headers.map(h => <th key={h} style={{ border: '1px solid var(--color-border-accent)', padding: '2px 8px', background: 'var(--color-bg-alt)' }}>{h}</th>)}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    {matches.slice(0, 3).map((m, i) => <td key={i} style={{ border: '1px solid var(--color-border)', padding: '2px 8px', fontFamily: 'monospace', fontSize: 13 }}>{m[2].slice(0, 100)}</td>)}
                  </tr>
                </tbody>
              </table>
            </div>
          );
        })()
      )}
      {type && type === 'xml' && xmlRoot && (
        <div style={{ marginBottom: 12, color: 'var(--color-accent)' }}>
          <b>XML root element:</b> {xmlRoot}
        </div>
      )}
      {error ? (
        <div style={{ color: 'var(--color-error)' }}>{error}</div>
      ) : (
        <pre style={{ maxHeight: 400, overflow: 'auto', background: 'var(--color-panel)', padding: 12, borderRadius: 6, fontSize: 14 }}>
          {content.slice(0, 5000)}
        </pre>
      )}
      {content.length > 5000 && <div style={{ color: 'var(--color-disabled-text)', fontSize: 13 }}>Preview truncated...</div>}
    </div>
  );
}
