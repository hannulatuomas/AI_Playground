import React, { useState } from 'react';
import { FileColumnSchema } from '../schemaTypes';
import SchemaStatusBadge from './SchemaStatusBadge';

interface FileSchemaEditorProps {
  fileId: string;
  initialSchema: FileColumnSchema[];
  status: 'confirmed' | 'editing' | 'unconfirmed';
  onSave: (schema: FileColumnSchema[]) => void;
  onCancel: () => void;
  editing: boolean;
  setEditing: (editing: boolean) => void;
}

const defaultColumn: FileColumnSchema = { name: '', type: 'string' };

const columnTypes = ['string', 'number', 'boolean', 'date'];

function validateSchema(schema: FileColumnSchema[]): string | null {
  if (!schema.length) return 'Schema must have at least one column.';
  const names = new Set();
  for (const col of schema) {
    if (!col.name.trim()) return 'Column names cannot be empty.';
    if (names.has(col.name)) return `Duplicate column name: ${col.name}`;
    names.add(col.name);
    if (!columnTypes.includes(col.type)) return `Invalid column type: ${col.type}`;
  }
  return null;
}

const FileSchemaEditor: React.FC<FileSchemaEditorProps> = ({
  fileId,
  initialSchema,
  status,
  onSave,
  onCancel,
  editing,
  setEditing
}) => {
  const [schema, setSchema] = useState<FileColumnSchema[]>(initialSchema);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (idx: number, field: keyof FileColumnSchema, value: string) => {
    setSchema(sch => sch.map((col, i) => i === idx ? { ...col, [field]: value } : col));
    setError(null);
  };

  const handleAdd = () => {
    setSchema(sch => [...sch, { ...defaultColumn }]);
    setError(null);
  };

  const handleRemove = (idx: number) => {
    setSchema(sch => sch.filter((_, i) => i !== idx));
    setError(null);
  };

  const handleSave = () => {
    const err = validateSchema(schema);
    if (err) {
      setError(err);
      return;
    }
    onSave(schema);
    setEditing(false);
  };

  const handleCancel = () => {
    setSchema(initialSchema);
    setError(null);
    onCancel();
    setEditing(false);
  };

  return (
    <div style={{ border: '1px solid var(--color-border)', borderRadius: 7, padding: 18, background: 'var(--color-panel)', marginBottom: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 10 }}>
        <b style={{ flex: 1 }}>Edit File Schema</b>
        <SchemaStatusBadge status={status} />
      </div>
      <form onSubmit={e => { e.preventDefault(); handleSave(); }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', marginBottom: 8 }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', padding: '4px 8px' }}>Column Name</th>
              <th style={{ textAlign: 'left', padding: '4px 8px' }}>Type</th>
              <th style={{ padding: '4px 8px' }}></th>
            </tr>
          </thead>
          <tbody>
            {schema.map((col, idx) => (
              <tr key={idx}>
                <td style={{ padding: '4px 8px' }}>
                  <input
                    type="text"
                    value={col.name}
                    onChange={e => handleChange(idx, 'name', e.target.value)}
                    style={{ width: 140, fontSize: 14, borderRadius: 4, border: '1px solid var(--color-border-accent)', padding: '3px 8px' }}
                    required
                    aria-label={`Column name for column ${idx + 1}`}
                  />
                </td>
                <td style={{ padding: '4px 8px' }}>
                  <select
                    value={col.type}
                    onChange={e => handleChange(idx, 'type', e.target.value)}
                    style={{ width: 100, fontSize: 14, borderRadius: 4, border: '1px solid var(--color-border-accent)', padding: '3px 8px' }}
                    aria-label={`Column type for column ${idx + 1}`}
                  >
                    {columnTypes.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </td>
                <td style={{ padding: '4px 8px', textAlign: 'center' }}>
                  <button
                    type="button"
                    onClick={() => handleRemove(idx)}
                    style={{ background: 'var(--color-error)', color: 'var(--color-text-light)', border: 'none', borderRadius: 4, padding: '2px 8px', fontSize: 15, cursor: 'pointer' }}
                    aria-label={`Remove column ${idx + 1}`}
                    disabled={schema.length === 1}
                  >
                    &minus;
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
          <button type="button" onClick={handleAdd} style={{ background: 'var(--color-primary)', color: 'var(--color-text-light)', border: 'none', borderRadius: 4, padding: '2px 10px', fontSize: 15, cursor: 'pointer' }}>
            + Add Column
          </button>
        </div>
        {error && <div style={{ color: 'var(--color-error)', fontWeight: 500, marginBottom: 8 }}>{error}</div>}
        <div style={{ display: 'flex', gap: 10 }}>
          <button type="submit" style={{ background: 'var(--color-success)', color: 'var(--color-text-light)', border: 'none', borderRadius: 4, padding: '5px 18px', fontWeight: 600, fontSize: 15, cursor: 'pointer' }}>
            Save Schema
          </button>
          <button type="button" onClick={handleCancel} style={{ background: 'var(--color-bg-alt)', color: 'var(--color-primary)', border: 'none', borderRadius: 4, padding: '5px 18px', fontWeight: 600, fontSize: 15, cursor: 'pointer' }}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default FileSchemaEditor;
