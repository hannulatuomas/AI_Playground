import React, { useState } from 'react';

interface Snippet {
  id: string;
  title: string;
  sql: string;
}

export default function SnippetsPanel({ onInsert }: { onInsert: (sql: string) => void }) {
  const [snippets, setSnippets] = useState<Snippet[]>(() => {
    try {
      return JSON.parse(localStorage.getItem('snippets') || '[]');
    } catch {
      return [];
    }
  });
  const [title, setTitle] = useState('');
  const [sql, setSQL] = useState('');

  const saveSnippet = () => {
    if (!title.trim() || !sql.trim()) return;
    const newSnip = { id: Date.now().toString(), title, sql };
    const updated = [...snippets, newSnip];
    setSnippets(updated);
    localStorage.setItem('snippets', JSON.stringify(updated));
    setTitle('');
    setSQL('');
  };

  const deleteSnippet = (id: string) => {
    const updated = snippets.filter(s => s.id !== id);
    setSnippets(updated);
    localStorage.setItem('snippets', JSON.stringify(updated));
  };

  return (
    <div style={{ marginTop: 24 }}>
      <div style={{
        marginBottom: 16,
        padding: '12px 10px',
        border: '1px solid var(--color-border)',
        borderRadius: 6,
        background: 'var(--color-bg-alt)',
        display: 'flex',
        flexDirection: 'column',
        gap: 10,
        width: '100%',
        boxSizing: 'border-box',
        minWidth: 0
      }}>
        <div style={{ width: '100%', boxSizing: 'border-box', minWidth: 0 }}>
          <input
            id="snippet-title"
            aria-label="Snippet title"
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="Title"
            style={{
              width: '100%',
              boxSizing: 'border-box',
              padding: '6px 8px',
              fontSize: 14,
              borderRadius: 4,
              border: '1px solid var(--color-border-accent)',
              marginBottom: 2,
              fontFamily: 'monospace',
              display: 'block',
              background: 'var(--color-panel)',
            }}
          />
        </div>
        <label style={{ fontSize: 13, marginBottom: 2 }} htmlFor="snippet-sql">Query:</label>
        <div style={{ width: '100%', boxSizing: 'border-box' }}>
          <textarea
            id="snippet-sql"
            aria-label="SQL query"
            value={sql}
            onChange={e => setSQL(e.target.value)}
            placeholder="SQL query"
            rows={4}
            style={{
              width: '100%',
              boxSizing: 'border-box',
              fontFamily: 'monospace',
              fontSize: 14,
              borderRadius: 4,
              border: '1px solid var(--color-border-accent)',
              resize: 'vertical',
              minHeight: 60,
              marginBottom: 2,
              background: 'var(--color-panel)',
              padding: '6px 8px',
              display: 'block',
            }}
          />
        </div>
        <button
          onClick={saveSnippet}
          style={{ alignSelf: 'flex-end', marginTop: 4, padding: '6px 18px', borderRadius: 4, background: 'var(--color-primary)', color: 'var(--color-text-light)', fontWeight: 600, fontSize: 14, border: 'none', cursor: 'pointer' }}
        >Save</button>
      </div>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {snippets.map(sn => (
          <li key={sn.id} style={{ marginBottom: 6, display: 'flex', alignItems: 'center' }}>
            <span style={{ flex: 1, fontFamily: 'monospace', fontSize: 14 }}>{sn.title}</span>
            <button style={{ marginLeft: 8, background: 'var(--color-primary-light)', border: 'none', borderRadius: 4, padding: '2px 8px', color: 'var(--color-primary)', fontWeight: 500 }} onClick={() => onInsert(sn.sql)}>Insert</button>
            <button style={{ marginLeft: 4, color: 'var(--color-error)', background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => deleteSnippet(sn.id)} title="Delete">🗑️</button>
          </li>
        ))}
        {snippets.length === 0 && <li style={{ color: 'var(--color-disabled-text)' }}>No saved snippets.</li>}
      </ul>
    </div>
  );
}
