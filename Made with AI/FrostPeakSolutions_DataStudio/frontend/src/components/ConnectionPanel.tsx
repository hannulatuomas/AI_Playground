import React, { useState, useRef } from 'react';
import type { DBType, ConnectionForm } from '../utils/connectionValidation';
import { validateField, validateForm, parseConnStr } from '../utils/connectionValidation';
import { useConnectionContext, DBConnection } from './ConnectionContext';
import { FieldTooltip } from './FieldTooltip';

export default function ConnectionPanel() {
  const { connections, addConnection, selected, setSelected } = useConnectionContext();
  // Use the centralized ConnectionForm type from utils/connectionValidation
  const [form, setForm] = useState<ConnectionForm>({ uid: '', type: 'postgres', displayName: '' });
const [status, setStatus] = useState<string>('');
const [useConnStr, setUseConnStr] = useState(false);
const [connStr, setConnStr] = useState('');

// Advanced/optional fields UI state
const [showAdvanced, setShowAdvanced] = useState(false);

// --- Validation State ---
const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

// --- Validation Logic ---
// (moved to utils/connectionValidation)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm(f => {
      // Always keep port as number or undefined
      if (name === 'port') {
        const portNum = value === '' ? undefined : Number(value);
        return { ...f, port: isNaN(portNum as number) ? undefined : portNum };
      }
      return { ...f, [name]: value };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  // --- Validate before submit ---
  const currentErrors = validateForm(form, useConnStr, connStr);
  setFieldErrors(currentErrors);
  if (Object.keys(currentErrors).length > 0) {
    setStatus('Please fix the errors above.');
    return;
  }
  setStatus('Testing connection...');
  let payload: ConnectionForm = { ...form, port: form.port ? Number(form.port) : undefined };
  
  if (useConnStr && connStr) {
    const parsed = parseConnStr(form.type, connStr);
    // Retain displayName from form, override others from parsed connStr
    payload = { 
        ...form, // keep advanced options, type, displayName
        ...parsed, // override core fields from connStr
        uid: form.uid // ensure uid isn't overwritten if parsed returns it
    }; 
    // If parseConnStr returns a type, ensure it's compatible or handle, but generally form.type is leading
    payload.type = form.type; 
    if (form.type === 'sqlserver' && parsed.host) { // SQL Server specific: server vs host
        payload.host = parsed.host; // use 'host' as canonical from parseConnStr
        delete (payload as any).server;
    }
  } else {
    // Not using connStr, ensure payload is built correctly from form fields
    if (form.type === 'sqlserver') {
      payload.host = form.server || form.host || ''; // Prefer form.server if set, then form.host
      delete (payload as any).server; // Send 'host' to backend
    }
  }
  
  // Clean up undefined optional fields to avoid sending them if empty
  Object.keys(payload).forEach(key => {
    if (payload[key as keyof ConnectionForm] === undefined || payload[key as keyof ConnectionForm] === '') {
        if (!['displayName', 'uid', 'type'].includes(key) && !(useConnStr && key === 'mongoUri') && !(useConnStr && key === 'neo4jUri')) {
             // Allow empty uid and type. Allow empty mongoUri/neo4jUri if connStr is used.
             // displayName can be empty if not required by specific DB type, but validation should catch it.
        }
    }
  });


  try {
    const res = await fetch('/api/connections', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await res.json();
    if (result.success) {
      setStatus('Connection successful!');
      const finalConnection = result.connection ? result.connection : { ...payload, uid: result.uid || Date.now().toString() };
      addConnection(finalConnection);
      // Reset form partially, keep type
      setForm({ uid: '', type: form.type, displayName: '' });
      setConnStr('');
      setFieldErrors({});
      setShowAdvanced(false);
    } else {
      setStatus('Failed: ' + result.error);
    }
  } catch (err) {
    setStatus('Error: ' + (err as any).message);
  }
};

return (
  <div style={{ border: '1px solid #dce6ef', padding: 28, maxWidth: 460, background: '#f7fafd', borderRadius: 16, boxShadow: '0 2px 12px #1976d220', margin: '0 auto' }}>
    <h2 style={{ fontSize: 22, marginBottom: 18, color: '#1976d2', fontWeight: 700, letterSpacing: 0.5 }}>Add Database Connection</h2>
    <form onSubmit={handleSubmit} style={{ marginBottom: 22, padding: '0 5px', maxWidth: 400, width: '100%', boxSizing: 'border-box' }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 14, width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
        <label style={{ fontWeight: 600, color: '#1976d2', fontSize: 15, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
          Database Type:
          <FieldTooltip id="dbtype-tip" text="Select the type of database you want to connect to." />
          <select name="type" value={form.type} onChange={(e) => {
            handleChange(e);
            setFieldErrors({}); // Clear errors on type change
            // Reset specific fields that might not be relevant for the new type
            setForm(f => ({
                uid: '', // Reset uid
                type: e.target.value as DBType, // Set new type
                displayName: f.displayName, // Keep display name
                // Clear other potentially incompatible fields
                host: undefined, server: undefined, port: undefined, user: undefined, password: undefined,
                database: undefined, file: undefined, mongoUri: undefined, neo4jUri: undefined,
                neo4jUser: undefined, neo4jPassword: undefined,
                // Keep advanced options or clear them as needed
                // schema: undefined, connectTimeout: undefined, ...
            }));
          }} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box' }}>
            <option value="postgres">PostgreSQL</option>
            <option value="sqlite">SQLite</option>
            <option value="mysql">MySQL</option>
            <option value="sqlserver">SQL Server</option>
            <option value="oracle">Oracle</option>
            <option value="mongodb">MongoDB</option>
            <option value="neo4j">Neo4j</option>
          </select>
        </label>
      </div>
      <button
        type="button" // Important: prevent form submission
        style={{ marginTop: 18, marginBottom: 18, padding: '8px 20px', borderRadius: 6, border: 'none', background: '#1976d2', color: 'var(--color-text-light)', fontWeight: 600, fontSize: 15, boxShadow: '0 1px 3px #1976d220', cursor: 'pointer', transition: 'background 0.15s' }}
        onClick={() => {
            setUseConnStr(v => !v);
            setFieldErrors({}); // Clear errors on mode switch
        }}
      >
        {useConnStr ? 'Switch to Form Fields' : 'Use Connection String'}
      </button>
      
      {/* DisplayName input - common to both modes, but shown conditionally */}
      {/* For Connection String mode, it's part of that block. For Form Fields, it's separate. */}
      <div style={{ marginBottom: 12, marginTop: useConnStr ? 0 : 6, width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
        <label style={{ fontWeight: 600, color: '#1976d2', fontSize: 15, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
          Display Name:
           <FieldTooltip id="displayname-tip" text="A friendly name to identify this connection (e.g. ‘Production Postgres’)." />
           <input
             name="displayName"
             value={form.displayName}
            onChange={handleChange}
            // required // Validation handles this
            style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 12px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.displayName ? '#e57373' : '#b6d4fa' }}
            placeholder="e.g. My Production PG"
          />
          {fieldErrors.displayName && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.displayName}</span>}
        </label>
      </div>

      {useConnStr ? (
        <div style={{ marginBottom: 14, marginTop: 6, width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
          <label style={{ fontWeight: 600, color: '#1976d2', fontSize: 15, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
            Connection String:
            <FieldTooltip id="connstr-tip" text="Paste the full connection string (URI or key-value format) for your database." />
            <input
              type="text"
              name="connectionString" // This name is not used in form state, connStr is separate
              value={connStr}
              onChange={e => {
                setConnStr(e.target.value);
                // Attempt to parse and populate form fields for preview/defaults
                const parsedFields = parseConnStr(form.type, e.target.value);
                setForm(f => ({...f, ...parsedFields}));
              }}
              // required // Validation handles this
              style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 12px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.connStr ? '#e57373' : '#b6d4fa' }}
              placeholder="Paste or type your full database connection string here"
            />
            {fieldErrors.connStr && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.connStr}</span>}
           </label>
        </div>
      ) : (
        <>
          {/* Database specific fields when not using connection string */}
          {['postgres', 'mysql', 'oracle'].includes(form.type) && (
            <>
              <div style={{ marginBottom: 12, marginTop: 6 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Host:
                  <FieldTooltip id="host-tip" text="The hostname or IP address of your database server." />
                  <input name="host" value={form.host || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.host ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.host && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.host}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Port:
                  <FieldTooltip id="port-tip" text="The port number your database server is listening on." />
                  <input name="port" type="number" value={form.port || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.port ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.port && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.port}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  User:
                  <FieldTooltip id="user-tip" text="The username to use for database authentication." />
                  <input name="user" value={form.user || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.user ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.user && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.user}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Password:
                  <FieldTooltip id="password-tip" text="The password to use for database authentication." />
                  <input name="password" type="password" value={form.password || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.password ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.password && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.password}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Database:
                  <FieldTooltip id="database-tip" text="The name of the database to connect to." />
                  <input name="database" value={form.database || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.database ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.database && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.database}</span>}
                </label>
              </div>
            </>
          )}
          {form.type === 'sqlserver' && (
            <>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Server:
                   <FieldTooltip id="server-tip" text="The SQL Server address or hostname." />
                   <input name="server" value={form.server || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.server ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.server && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.server}</span>}
                </label>
              </div>
               <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Port:
                  <FieldTooltip id="port-tip" text="The port number your database server is listening on." />
                  <input name="port" type="number" value={form.port || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.port ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.port && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.port}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  User:
                  <FieldTooltip id="user-tip" text="The username to use for database authentication." />
                  <input name="user" value={form.user || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.user ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.user && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.user}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Password:
                  <FieldTooltip id="password-tip" text="The password to use for database authentication." />
                  <input name="password" type="password" value={form.password || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.password ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.password && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.password}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Database:
                  <FieldTooltip id="database-tip" text="The name of the database to connect to." />
                  <input name="database" value={form.database || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.database ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.database && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.database}</span>}
                </label>
              </div>
            </>
          )}
          {form.type === 'sqlite' && (
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                File Path:
                <FieldTooltip id="sqlite-file-tip" text="The full path to your SQLite database file." />
                <input name="file" value={form.file || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.file ? '#e57373' : '#b6d4fa' }} />
                {fieldErrors.file && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.file}</span>}
              </label>
            </div>
          )}
          {form.type === 'mongodb' && (
            <>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Host:
                  <FieldTooltip id="host-tip" text="The hostname or IP address of your MongoDB server." />
                  <input name="host" value={form.host || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.host ? '#e57373' : '#b6d4fa' }} />
                   {fieldErrors.host && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.host}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Port:
                  <FieldTooltip id="port-tip" text="The port number your MongoDB server is listening on." />
                  <input name="port" type="number" value={form.port || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.port ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.port && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.port}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  User:
                  <FieldTooltip id="user-tip" text="The username to use for MongoDB authentication." />
                  <input name="user" value={form.user || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.user ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.user && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.user}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Password:
                  <FieldTooltip id="password-tip" text="The password to use for MongoDB authentication." />
                  <input name="password" type="password" value={form.password || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.password ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.password && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.password}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Database:
                  <FieldTooltip id="database-tip" text="The name of the MongoDB database to connect to." />
                  <input name="database" value={form.database || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.database ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.database && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.database}</span>}
                </label>
              </div>
            </>
          )}
          {form.type === 'neo4j' && (
            <>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Host:
                  <FieldTooltip id="host-tip" text="The hostname or IP address of your Neo4j server." />
                  <input name="host" value={form.host || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.host ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.host && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.host}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Port:
                  <FieldTooltip id="port-tip" text="The port number your Neo4j server is listening on." />
                  <input name="port" type="number" value={form.port || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.port ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.port && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.port}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  User:
                   <FieldTooltip id="neo4juser-tip" text="The username for Neo4j authentication." />
                   <input name="neo4jUser" value={form.neo4jUser || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.neo4jUser ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.neo4jUser && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.neo4jUser}</span>}
                </label>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  Password:
                   <FieldTooltip id="neo4jpass-tip" text="The password for Neo4j authentication." />
                   <input name="neo4jPassword" type="password" value={form.neo4jPassword || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box', borderColor: fieldErrors.neo4jPassword ? '#e57373' : '#b6d4fa' }} />
                  {fieldErrors.neo4jPassword && <span style={{ color: '#e53935', fontSize: 13, marginTop: 2 }}>{fieldErrors.neo4jPassword}</span>}
                </label>
              </div>
            </>
          )}
          {/* Optional Fields - Collapsed by default */}
          <div style={{ marginBottom: 18, marginTop: 10 }}>
            <button
              type="button"
              onClick={() => setShowAdvanced(v => !v)}
              style={{ background: '#e3f2fd', color: '#1976d2', border: 'none', borderRadius: 5, padding: '5px 14px', fontWeight: 600, fontSize: 14, cursor: 'pointer', marginBottom: 4 }}
            >
              {showAdvanced ? 'Hide Optional' : 'Show Optional'}
            </button>
            {showAdvanced && (
              <div style={{ marginTop: 0, border: '1px solid var(--color-border-accent)', borderRadius: 6, background: '#f4f9fd', padding: '18px 8px 18px 8px', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 10 }}>
                {/* Universal optional fields */}
                <div style={{ marginBottom: 10 }}>
                  <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>SSL/Encrypt:
                    <FieldTooltip id="ssl-tip" text="Enable SSL or encryption for the connection." />
                    <select name="ssl" value={form.ssl ?? ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box' }}>
                      <option value="">(default)</option>
                      <option value="true">true</option>
                      <option value="false">false</option>
                    </select>
                  </label>
                </div>
                <div style={{ marginBottom: 10 }}>
                  <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>Schema:
                    <FieldTooltip id="schema-tip" text="(Optional) Default schema to use." />
                    <input name="schema" value={form.schema || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box' }} placeholder="(optional)" />
                  </label>
                </div>
                <div style={{ marginBottom: 10 }}>
                  <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>Connect Timeout (ms):
                    <FieldTooltip id="timeout-tip" text="(Optional) Connection timeout in milliseconds." />
                    <input name="connectTimeout" type="number" value={form.connectTimeout || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box' }} placeholder="(optional)" />
                  </label>
                </div>
                <div style={{ marginBottom: 10 }}>
                  <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>Application Name:
                    <FieldTooltip id="appname-tip" text="(Optional) Name for this application in DB logs." />
                    <input name="applicationName" value={form.applicationName || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box' }} placeholder="(optional)" />
                  </label>
                </div>
                <div style={{ marginBottom: 10 }}>
                  <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>Options (JSON):
                    <FieldTooltip id="options-tip" text="(Optional) Additional connection options as JSON." />
                    <input name="options" value={form.options || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box' }} placeholder='e.g. {"application_name": "myapp"}' />
                  </label>
                </div>
                {/* DB-specific optional fields */}
                {form.type === 'postgres' && (
                  <div style={{ marginBottom: 10 }}>
                    <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>Search Path:
                       <FieldTooltip id="searchpath-tip" text="(Optional) Comma-separated list of schemas to search by default." />
                       <input name="searchPath" value={form.searchPath || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box' }} placeholder="(optional)" />
                    </label>
                  </div>
                )}
                {form.type === 'mysql' && (
                  <div style={{ marginBottom: 10 }}>
                    <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>Charset:
                      <FieldTooltip id="charset-tip" text="(Optional) Character set for the connection." />
                      <input name="charset" value={form.charset || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box' }} placeholder="(optional)" />
                    </label>
                  </div>
                )}
                {form.type === 'sqlserver' && (
                  <>
                    <div style={{ marginBottom: 10 }}>
                      <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>Encrypt:
                        <FieldTooltip id="encrypt-tip" text="Enable encryption for the connection." />
                        <select name="encrypt" value={form.encrypt ?? ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box' }}>
                          <option value="">(default)</option>
                          <option value="true">true</option>
                          <option value="false">false</option>
                        </select>
                      </label>
                    </div>
                    <div style={{ marginBottom: 10 }}>
                      <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>Trust Server Certificate:
                        <FieldTooltip id="trustcert-tip" text="Trust the server certificate (for self-signed certs)." />
                        <select name="trustServerCertificate" value={form.trustServerCertificate ?? ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box' }}>
                          <option value="">(default)</option>
                          <option value="true">true</option>
                          <option value="false">false</option>
                        </select>
                      </label>
                    </div>
                  </>
                )}
                {form.type === 'mongodb' && (
                  <div style={{ marginBottom: 10 }}>
                    <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>Replica Set:
                      <FieldTooltip id="replicaset-tip" text="(Optional) Name of the MongoDB replica set, if applicable." />
                      <input name="replicaSet" value={form.replicaSet || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box' }} placeholder="(optional)" title="MongoDB: Name of the replica set (if using a replica set deployment)." />
                    </label>
                  </div>
                )}
                {form.type === 'neo4j' && (
                  <div style={{ marginBottom: 10 }}>
                    <label style={{ fontWeight: 500, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>Database (Neo4j):
                      <FieldTooltip id="neo4jdb-tip" text="(Optional) Database name for Neo4j (multi-database setups)." />
                      <input name="neo4jDatabase" value={form.neo4jDatabase || ''} onChange={handleChange} style={{ borderRadius: 5, border: '1px solid var(--color-border-accent)', padding: '5px 10px', fontSize: 15, width: '100%', boxSizing: 'border-box' }} placeholder="(optional)" title="Neo4j: Database name (if using multi-database setup)." />
                    </label>
                  </div>
                )}
              </div>
            )}
          </div>
        </>
      )}
      <button type="submit" style={{ padding: '12px 25px', borderRadius: 8, border: 'none', background: 'var(--color-success)', color: 'var(--color-text-light)', fontWeight: 700, fontSize: 16, boxShadow: '0 2px 5px var(--color-success-shadow)', cursor: 'pointer', transition: 'background 0.15s', width: '100%', marginTop: 10 }}>
        Test & Add Connection
      </button>
    </form>
    {status && <div style={{ marginTop: 15, padding: '10px 15px', borderRadius: 6, background: status.startsWith('Connection successful') ? '#e8f5e9' : '#ffebee', color: status.startsWith('Connection successful') ? '#2e7d32' : '#c62828', border: `1px solid ${status.startsWith('Connection successful') ? 'var(--color-success-border)' : 'var(--color-error-border)'}`, textAlign: 'center' }}>{status}</div>}
  </div>
);
}
