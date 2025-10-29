import React, { useEffect, useState } from 'react';
import { getApiUrl } from '../apiConfig';
import * as Papa from 'papaparse';
import { FileColumnSchema } from '../schemaTypes';
import FileSchemaEditor from './FileSchemaEditor';
import SchemaStatusBadge from './SchemaStatusBadge';

import { useFileContext } from './FileContext';
import { useFileSchema } from './useFileSchema';
import SchemaUnconfirmedBanner from './SchemaUnconfirmedBanner';

interface Props {
  fileId: string;
}

function inferType(val: string): string {
  if (val === '' || val == null) return 'string';
  if (!isNaN(Number(val))) return val.includes('.') ? 'float' : 'int';
  if (val.toLowerCase() === 'true' || val.toLowerCase() === 'false') return 'boolean';
  if (/^\d{4}-\d{2}-\d{2}/.test(val)) return 'date';
  return 'string';
}


export default function NotebookCellFileSchemaPreview({ fileId }: Props) {
  const { files } = useFileContext();
  const file = files.find(f => f.id === fileId);
  if (!file) return <div style={{ padding: 24 }}>File not found.</div>;
  // Only use fileId for all schema logic; filename/type only for display or fetch
  const { filename, type } = file;
  const [content, setContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [schema, setSchema] = useState<FileColumnSchema[] | null>(null);
  const [editingSchema, setEditingSchema] = useState<FileColumnSchema[] | null>(null);
  const [editing, setEditing] = useState(false);
  const [validationError, setValidationError] = useState<string|null>(null);

  // Use the new hook for schema logic
  const { loadSchemaOverride, saveSchemaOverride, setStatus, status } = useFileSchema(fileId);

  // Set status to 'editing' when editing begins
  useEffect(() => {
    if (editing) {
      setStatus('editing');
    }
  }, [editing, setStatus]);

  // When schema is saved, set status to 'confirmed'
  function handleSaveSchema() {
    if (editingSchema) {
      setSchema(editingSchema);
      saveSchemaOverride(editingSchema);
      setEditing(false);
    }
  }


  // Validate schema edits
  useEffect(() => {
    if (!editing || !editingSchema) { setValidationError(null); return; }
    const names = editingSchema.map(c => c.name.trim());
    const nameSet = new Set(names);
    if (names.some(n => !n)) setValidationError('Column names cannot be empty.');
    else if (nameSet.size !== names.length) setValidationError('Duplicate column names are not allowed.');
    else if (editingSchema.some(c => !c.type)) setValidationError('All columns must have a type.');
    else setValidationError(null);
  }, [editing, editingSchema]);

  useEffect(() => {
    if (!fileId) return;
    if (!file) { setError('File not found'); return; }
    if (["csv", "xml", "json"].includes(file.type)) {
      fetch(getApiUrl(`files/${encodeURIComponent(fileId)}/preview?lines=20`))
        .then(res => res.ok ? res.json() : Promise.reject('Failed to preview JSON file'))
        .then(data => {
          if (data.success && Array.isArray(data.rows) && data.rows.length > 0) {
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
      return;
    }
    fetch(getApiUrl(`files/${encodeURIComponent(fileId)}`))
      .then(res => res.ok ? res.text() : Promise.reject('Failed to fetch file'))
      .then(text => {
        setContent(text);
        if (file.type === 'csv') {
          const parsed = Papa.parse(text, { header: true, preview: 20 });
          if (parsed.meta.fields && parsed.data && Array.isArray(parsed.data)) {
            let types = parsed.meta.fields.map((f: string) => {
              const vals = parsed.data.map((row: any) => row[f]).filter((v: string) => v !== undefined && v !== null && v !== '');
              const sample = vals[0];
              return { name: f, type: sample ? inferType(sample) : 'string' };
            });
            const override = loadSchemaOverride();
            if (override) types = override;
            setSchema(types);
          }
        }
      })
      .catch(e => setError(String(e)));
  }, [fileId, file]);

  return (
    <div className="file-schema-preview">
      <div className="file-schema-header">
        <b className="file-schema-title">File Schema & Sample Data for: {file.filename}</b>
        <SchemaStatusBadge status={status} className="schema-status-badge" />
      </div>
      {status === 'unconfirmed' && <SchemaUnconfirmedBanner />}
      {error && <div className="error-message">{error}</div>}
      {type === 'csv' && schema && (
        <div className="file-schema-editor-container">
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
        </div>
      )}
      {/* CSV sample preview */}
      {type === 'csv' && schema && content && (
        (() => {
          const parsed = Papa.parse(content, { header: true, preview: 10 });
          const rows = Array.isArray(parsed.data) ? parsed.data.slice(0, 10) : [];
          const useSchema = editing ? (editingSchema ?? schema) : schema;
          if (!rows.length) return null;
          return (
            <div className="sample-data-container">
              <b className="sample-data-title">Sample Data:</b>
              <table className="sample-data-table">
                <tbody>
                  {rows.map((row: any, i: number) => (
                    <tr key={i}>
                      {useSchema.map(col => (
                        <td key={col.name} className="sample-data-cell">{row[col.name]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        })()
      )}
    </div>
  );
}
