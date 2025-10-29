import React, { useEffect, useState } from 'react';

// Basic Notebook metadata type for localStorage
interface NotebookMeta {
  id: string;
  title: string;
  lastModified: number;
}

interface NotebookListProps {
  onOpen: (id: string) => void;
  onNewNotebook?: () => void;
  refreshKey?: any; // to force list refresh from parent
}

export default function NotebookList({ onOpen, onNewNotebook, refreshKey }: NotebookListProps) {
  const [notebooks, setNotebooks] = useState<NotebookMeta[]>([]);

  useEffect(() => {
    // Load notebooks from localStorage (for MVP)
    const items: NotebookMeta[] = [];
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith('notebook:')) {
        try {
          const meta = JSON.parse(localStorage.getItem(key) || '{}');
          if (meta && meta.id && meta.title) items.push(meta);
        } catch {}
      }
    });
    setNotebooks(items.sort((a, b) => b.lastModified - a.lastModified));
  }, [refreshKey]);

  const handleDelete = (id: string) => {
    localStorage.removeItem('notebook:' + id);
    setNotebooks(nbks => nbks.filter(n => n.id !== id));
  };

  return (
    <div style={{ marginTop: 8 }}>
      {onNewNotebook && (
        <button
          style={{ display: 'block', width: '100%', marginBottom: 10, padding: '6px 0', background: 'var(--color-primary)', color: 'var(--color-text-light)', border: 'none', borderRadius: 6, fontWeight: 600, fontSize: 14, cursor: 'pointer' }}
          onClick={onNewNotebook}
        >
          + New Notebook
        </button>
      )}
      <ul style={{ listStyle: 'none', padding: 0, marginTop: 0 }}>
        {notebooks.map(nb => (
          <li key={nb.id} style={{ marginBottom: 6, display: 'flex', alignItems: 'center' }}>
            <button
              style={{ fontFamily: 'monospace', fontSize: 14, background: 'var(--color-primary-light)', border: 'none', borderRadius: 4, padding: '4px 10px', flex: 1, textAlign: 'left' }}
              onClick={() => onOpen(nb.id)}
              title={nb.title}
            >
              {nb.title} <span style={{ color: 'var(--color-disabled-text)', fontSize: 12 }}>({new Date(nb.lastModified).toLocaleString()})</span>
            </button>
            <button
              style={{ marginLeft: 8, background: 'var(--color-error)', color: 'var(--color-text-light)', border: 'none', borderRadius: 4, padding: '2px 6px', fontSize: 16, cursor: 'pointer' }}
              onClick={() => handleDelete(nb.id)}
              title="Delete"
              aria-label={`Delete notebook ${nb.title}`}
            >
              <span role="img" aria-label="Delete">🗑️</span>
            </button>
          </li>
        ))}
        {notebooks.length === 0 && <li style={{ color: 'var(--color-disabled-text)' }}>No saved notebooks.</li>}
      </ul>
    </div>
  );
}
