import React, { useState } from 'react';
import { useTheme } from './ThemeContext';
import ConnectionPanel from './ConnectionPanel';
// FilePanel uses global file context for file state and refresh
import FilePanel from './FilePanel';
import NotebookList from './NotebookList';
import SnippetsPanel from './SnippetsPanel';
import './Sidebar.css';

interface SidebarProps {
  onFileSelect: (fileId: string) => void;
  onOpenNotebook?: (id: string) => void;
  onInsertSnippet?: (sql: string) => void;
  refreshKey?: any;
  setRefreshKey?: React.Dispatch<React.SetStateAction<number>>;
}

// Sidebar always takes full height of viewport and allows scrolling if needed
export default function Sidebar({ onFileSelect, onOpenNotebook, onInsertSnippet, refreshKey, setRefreshKey }: SidebarProps) {
  const { theme, toggleTheme } = useTheme();
  const [showPanel, setShowPanel] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Close sidebar on navigation (mobile)
  React.useEffect(() => {
    if (sidebarOpen && window.innerWidth > 800) setSidebarOpen(false);
    const handleResize = () => {
      if (window.innerWidth > 800 && sidebarOpen) setSidebarOpen(false);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [sidebarOpen]);
  // Handler for creating a new notebook
  function handleNewNotebook() {
    const id = Math.random().toString(36).slice(2, 10);
    const meta = { id, title: 'Untitled Notebook', description: '', lastModified: Date.now() };
    localStorage.setItem('notebook:' + id, JSON.stringify(meta));
    localStorage.setItem('notebook:' + id + ':cells', JSON.stringify({ cells: [{ id: Math.random().toString(36).slice(2, 10), type: 'sql', value: '', collapsed: false }], meta }));
    if (onOpenNotebook) onOpenNotebook(id);
    if (setRefreshKey) setRefreshKey(k => k + 1);
  }
  const { connections, selected, setSelected, removeConnection } = require('./ConnectionContext').useConnectionContext();
  
  // SSR-safe screen width check
  const isMobile = typeof window !== 'undefined' && window.innerWidth <= 800;

  return (
    <>
      {/* Hamburger button for mobile */}
      <button
        className="sidebarHamburger"
        aria-label={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
        aria-pressed={sidebarOpen}
        onClick={() => setSidebarOpen(v => !v)}
        tabIndex={0}
        style={{ position: 'fixed', top: 18, left: 14, display: isMobile ? 'flex' : 'none' }}
      >
        {sidebarOpen ? '✖' : '☰'}
      </button>
      {/* Overlay for mobile when sidebar is open */}
      {isMobile && sidebarOpen && (
        <div
          className="sidebarOverlay sidebarVisible"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close sidebar overlay"
          tabIndex={-1}
        />
      )}
      <aside
        className={`sidebarContainer${isMobile ? (sidebarOpen ? ' sidebarVisible' : ' sidebarCollapsed') : ''}`}
        tabIndex={-1}
        aria-hidden={isMobile && !sidebarOpen}
        style={{
          ...(isMobile && !sidebarOpen ? { pointerEvents: 'none' } : {}),
        }}
      >
      <button
        onClick={toggleTheme}
        aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
        title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
        style={{
          display: 'block',
          margin: '12px auto 20px auto',
          padding: '8px 20px',
          background: 'var(--color-panel)',
          color: 'var(--color-text)',
          border: '1px solid var(--color-border)',
          borderRadius: 6,
          fontWeight: 600,
          fontSize: 15,
          boxShadow: '0 1px 3px var(--color-shadow)',
          cursor: 'pointer',
          transition: 'background 0.15s',
        }}
      >
        {theme === 'light' ? '🌞 Light' : '🌙 Dark'} Mode
      </button>
      <button
        onClick={() => setShowPanel(s => !s)}
        style={{
          display: 'block',
          marginBottom: 12,
          padding: '8px 20px',
          background: 'var(--color-primary)',
          color: 'var(--color-text-light)',
          border: 'none',
          borderRadius: 6,
          fontWeight: 600,
          fontSize: 15,
          boxShadow: '0 1px 3px var(--color-shadow)',
          cursor: 'pointer',
          transition: 'background 0.15s',
        }}
      >
        {showPanel ? 'Hide' : 'Add'} Connection
      </button>
      {showPanel && <ConnectionPanel />}
      <h2 style={{ fontSize: 20, margin: '24px 0 16px 0' }}>Connections</h2>
      {/* List connections here */}
      <ul style={{ listStyle: 'none', padding: 0, marginBottom: 24 }}>
        {connections && connections.length > 0 ? connections.map((c: import('./ConnectionContext').DBConnection, i: number) => (
          <li key={i} style={{ marginBottom: 6, display: 'flex', alignItems: 'center' }}>
            <input type="radio" checked={selected === i} onChange={() => setSelected(i)} style={{ marginRight: 8 }} />
            <span style={{ fontFamily: 'monospace', fontSize: 14, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 170 }} title={c.displayName?.trim() || ''}>
              {c.displayName?.trim()
                ? c.displayName
                : (['postgres','mysql','sqlserver','oracle'].includes(c.type)
                    ? `${c.type}://${c.user}@${c.host}:${c.port}/${c.database}`
                    : c.type === 'sqlite'
                      ? `sqlite: ${c.file}`
                      : c.type === 'mongodb'
                        ? c.mongoUri
                          ? `MongoDB: ${c.mongoUri}`
                          : `MongoDB://${c.user || ''}@${c.host || ''}:${c.port || ''}/${c.database || ''}`
                        : c.type === 'neo4j'
                          ? c.neo4jUri
                            ? `Neo4j: ${c.neo4jUri}`
                            : `Neo4j://${c.neo4jUser || c.user || ''}@${c.host || ''}:${c.port || ''}`
                          : ''
                  )
              }
            </span>
            <button
              style={{
                marginLeft: 8,
                background: 'var(--color-error)',
                color: 'var(--color-text-light)',
                border: 'none',
                borderRadius: 4,
                padding: '2px 6px',
                fontSize: 16,
                cursor: 'pointer',
              }}
              title={`Delete connection${c.displayName ? `: ${c.displayName}` : ''}`}
              aria-label={`Delete connection${c.displayName ? `: ${c.displayName}` : ''}`}
              onClick={() => removeConnection(i)}
            >
              <span role="img" aria-label="Delete">🗑️</span>
            </button>
          </li>
        )) : (
          <li style={{ color: 'var(--color-disabled-text)', fontSize: 14 }}>No saved connections.</li>
        )}
      </ul>
      <div style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, margin: '24px 0 12px 0' }}>File Explorer</h2>
        <FilePanel onSelect={onFileSelect} />
      </div>
      <div>
        <h2 style={{ fontSize: 18, margin: '24px 0 12px 0' }}>Saved Notebooks</h2>
        <NotebookList onOpen={onOpenNotebook || (() => {})} onNewNotebook={handleNewNotebook} refreshKey={refreshKey} />
      </div>
      <div style={{ marginTop: 32 }}>
        <h2 style={{ fontSize: 18, margin: '24px 0 12px 0' }}>Query Snippets</h2>
        <SnippetsPanel onInsert={onInsertSnippet || (() => {})} />
      </div>
    </aside>
    </>
  );
}
