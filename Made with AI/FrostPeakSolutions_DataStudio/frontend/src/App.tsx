import React, { useState } from 'react';
import { getApiUrl } from './apiConfig';
import Sidebar from './components/Sidebar';
import ResizablePanel from './components/ResizablePanel';
import NotebookEditor from './components/NotebookEditor';
import { ConnectionProvider, useConnectionContext } from './components/ConnectionContext';
import { FileProvider } from './components/FileContext';
import { ThemeProvider } from './components/ThemeContext';

interface NotebookMeta {
  id: string;
  title: string;
  description: string;
  lastModified: number;
}

function MainApp() {
  // --- Snippet insertion state ---
  const [windowWidth, setWindowWidth] = React.useState(
    typeof window !== 'undefined' ? window.innerWidth : 1200
  );
  React.useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  const [selectedCellIdx, setSelectedCellIdx] = useState<number | null>(null);
  const [results, setResults] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
// Only show connection error in the info bar, not in ResultsPanel or NotebookEditor
  const { connections, selected, setSelected } = useConnectionContext();
  // Use UID for selection
  const [selectedConnectionUid, setSelectedConnectionUid] = React.useState<string | null>(null);
  // Keep selectedConnectionUid in sync with selected (legacy index) for now
  React.useEffect(() => {
    if (selected !== null && connections[selected]) {
      setSelectedConnectionUid(connections[selected].uid);
    }
  }, [selected, connections]);
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);
  const [notebookCells, setNotebookCells] = useState<any[] | null>(null);
  const [notebookMeta, setNotebookMeta] = useState<NotebookMeta | null>(null);
  const [notebookGroups, setNotebookGroups] = useState<any[] | null>(null);
  const [refreshKey, setRefreshKey] = useState(0); // for Sidebar/NotebookList refresh

  const handleRunQuery = async (sql: string, opts?: { params?: any, conn?: any, file?: any }) => {
    setError(null);
    setResults([]);
    // Prefer file if selected, else DB connection
    if (selectedFileId) {
      const { files } = require('./components/FileContext').useFileContext();
      const file = files.find((f: any) => f.id === selectedFileId);
      if (!file) {
        setError('Selected file not found.');
        return;
      }
      try {
        const res = await fetch(getApiUrl('query'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type: file.type, file: file.filename, sql, params: opts?.params }),
        });
        const result = await res.json();
        if (result.success) {
          setResults(result.rows);
        } else {
          setError(result.error || 'Query failed');
        }
      } catch (err: any) {
        setError(err.message);
      }
      return;
    }
    if (selected === null || !connections[selected]) {
      setError('Please select a database connection or file.');
      return;
    }
    const conn = connections[selected];
    try {
      
const res = await fetch(getApiUrl('query'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...conn, sql, params: opts?.params }),
      });
      const result = await res.json();
      if (result.success) {
        setResults(result.rows);
      } else {
        setError(result.error || 'Query failed');
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Handler to open notebook by id from localStorage
  const handleOpenNotebook = (id: string) => {
    const metaStr = localStorage.getItem('notebook:' + id);
    if (!metaStr) return;
    const cellsStr = localStorage.getItem('notebook:' + id + ':cells');
    if (cellsStr) {
      try {
        const parsed = JSON.parse(cellsStr);
        if (parsed && Array.isArray(parsed.cells) && parsed.meta) {
          setNotebookCells(parsed.cells);
          setNotebookMeta(parsed.meta);
          setNotebookGroups(parsed.groups && Array.isArray(parsed.groups) ? parsed.groups : []);
        }
      } catch {
        setNotebookCells(null);
        setNotebookMeta(JSON.parse(metaStr));
        setNotebookGroups([]);
      }
    } else {
      setNotebookMeta(JSON.parse(metaStr));
      setNotebookCells(null);
      setNotebookGroups([]);
    }
  };

  // Handler to update notebook cells/meta from NotebookEditor (for saving in localStorage)
  const handleNotebookUpdate = (cells: any[], meta: NotebookMeta, groups: any[] = []) => {
    setNotebookCells(cells);
    setNotebookMeta(meta);
    // Save cells, meta, and groups to localStorage for quick open
    localStorage.setItem('notebook:' + meta.id + ':cells', JSON.stringify({ cells, meta, groups }));
    // Save meta as well, including groups
    localStorage.setItem('notebook:' + meta.id, JSON.stringify({ ...meta, groups }));
  };

  // Insert snippet into selected cell
  const handleInsertSnippet = (sql: string) => {
    if (selectedCellIdx == null || !notebookCells || !notebookCells[selectedCellIdx]) return;
    const newCells = notebookCells.map((cell, idx) =>
      idx === selectedCellIdx ? { ...cell, value: cell.value + (cell.value ? '\n' : '') + sql } : cell
    );
    setNotebookCells(newCells);
    if (notebookMeta) handleNotebookUpdate(newCells, notebookMeta);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'sans-serif', overflow: 'hidden' }}>
      {windowWidth > 800 ? (
        <ResizablePanel
          direction="horizontal"
          minSize={180}
          maxSize={400}
          initialSize={240}
          storageKey="sidebar-width"
        >
          <Sidebar
            onFileSelect={(fileId: string) => {
              setSelectedFileId(fileId);
              setNotebookCells(null);
              setNotebookMeta(null);
            }}
            onOpenNotebook={handleOpenNotebook}
            onInsertSnippet={handleInsertSnippet}
            refreshKey={refreshKey}
            setRefreshKey={setRefreshKey}
          />
        </ResizablePanel>
      ) : null}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, width: '100vw' }}>
        <div style={{ padding: 8, fontSize: 14, color: '#1976d2', minHeight: 24 }}>
          {selectedFileId ? (() => {
            const { files } = require('./components/FileContext').useFileContext();
            const file = files.find((f: any) => f.id === selectedFileId);
            return file ? (
              <>Querying file: <b>{file.filename}</b> ({file.type.toUpperCase()})</>
            ) : (
              <>File not found.</>
            );
          })() : selected !== null && connections[selected] ? (
            <>Using DB: <b>{connections[selected].type}</b></>
          ) : (
            'No connection or file selected.'
          )}
        </div>
        <NotebookEditor
          onRun={async (sql: string, opts?: { params?: any, conn?: any, file?: any }) => {
            // Prefer per-cell file if provided
            if (opts?.file) {
              try {
                const res = await fetch(getApiUrl('query'), {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ type: opts.file.type, file: opts.file.filename, sql, params: opts?.params }),
                });
                const result = await res.json();
                return result.success
                  ? { result: result.rows, error: null }
                  : { result: undefined, error: result.error || 'Query failed' };
              } catch (err: any) {
                return { result: undefined, error: err.message };
              }
            }
            // Prefer per-cell connection if provided
            if (opts?.conn) {
              try {
                const res = await fetch(getApiUrl('query'), {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ ...opts.conn, sql, params: opts?.params }),
                });
                const result = await res.json();
                return result.success
                  ? { result: result.rows, error: null }
                  : { result: undefined, error: result.error || 'Query failed' };
              } catch (err: any) {
                return { result: undefined, error: err.message };
              }
            }
            // Fallback to global selected file
            if (selectedFileId) {
              const { files } = require('./components/FileContext').useFileContext();
              const file = files.find((f: any) => f.id === selectedFileId);
              if (!file) {
                return { result: undefined, error: 'Selected file not found.' };
              }
              try {
                const res = await fetch(getApiUrl('query'), {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ type: file.type, file: file.filename, sql, params: opts?.params }),
                });
                const result = await res.json();
                return result.success
                  ? { result: result.rows, error: null }
                  : { result: undefined, error: result.error || 'Query failed' };
              } catch (err: any) {
                return { result: undefined, error: err.message };
              }
            }
            // Fallback to global selected connection (by UID)
            if (selectedConnectionUid && connections.length) {
              const conn = connections.find(c => c.uid === selectedConnectionUid);
              if (conn) {
                try {
                  const res = await fetch(getApiUrl('query'), {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ...conn, sql, params: opts?.params }),
                  });
                  const result = await res.json();
                  return result.success
                    ? { result: result.rows, error: null }
                    : { result: undefined, error: result.error || 'Query failed' };
                } catch (err: any) {
                  return { result: undefined, error: err.message };
                }
              }
            }
            // If nothing is available
            return { result: undefined, error: 'Please select a database connection or file.' };
          }}
          initialCells={notebookCells || undefined}
          initialMeta={notebookMeta || undefined}
          initialGroups={notebookGroups || undefined}
          onNotebookUpdate={handleNotebookUpdate}
          onCellSelect={setSelectedCellIdx}
          onMetaChange={() => setRefreshKey(k => k + 1)}
          selectedUid={selectedConnectionUid}
        />
      </main>
      {/* Mobile sidebar overlays content, not in flex row */}
      {windowWidth <= 800 && (
        <Sidebar
          onFileSelect={(fileId: string) => {
            setSelectedFileId(fileId);
            setNotebookCells(null);
            setNotebookMeta(null);
          }}
          onOpenNotebook={handleOpenNotebook}
          onInsertSnippet={handleInsertSnippet}
          refreshKey={refreshKey}
          setRefreshKey={setRefreshKey}
        />
      )}
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <ConnectionProvider>
        <FileProvider>
          <MainApp />
        </FileProvider>
      </ConnectionProvider>
    </ThemeProvider>
  );
}

export default App;
