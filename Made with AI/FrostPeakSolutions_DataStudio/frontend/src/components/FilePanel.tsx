import React, { useRef, useState, Suspense, useEffect } from 'react';
import { getApiUrl } from '../apiConfig';
import ReactDOM from 'react-dom';
import '../components/NotebookCellsGlobal.css';
import { useFileContext } from './FileContext';
import SchemaStatusBadge from './SchemaStatusBadge';

const FilePreview = React.lazy(() => import('./FilePreview'));

type FileType = 'csv' | 'xml' | 'json';

export default function FilePanel({ onSelect }: { onSelect: (fileId: string) => void }) {
  const [dragActive, setDragActive] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  // Dismiss error banner on Escape
  useEffect(() => {
    if (!uploadError) return;
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setUploadError(null);
    }
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [uploadError]);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const { files, refreshFiles, loading, schemaStatus } = useFileContext();
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [previewFileId, setPreviewFileId] = useState<string | null>(null);

  // Handle modal close on Escape or outside click
  useEffect(() => {
    if (!previewFileId) return;
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setPreviewFileId(null);
    }
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [previewFileId]);

  // File list is now managed by context

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement> | DragEvent) => {
    let filesToUpload: FileList | File[] | null = null;
    if ('dataTransfer' in e) {
      filesToUpload = e.dataTransfer && e.dataTransfer.files ? e.dataTransfer.files : null;
    } else {
      filesToUpload = e.target && e.target.files ? e.target.files : null;
    }
    if (!filesToUpload || filesToUpload.length === 0) return;
    setUploading(true);
    setUploadError(null);
    try {
      for (let i = 0; i < filesToUpload.length; i++) {
        const file = filesToUpload[i];
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch(getApiUrl('files'), { method: 'POST', body: formData });
        if (!res.ok) {
          throw new Error(`Failed to upload file: ${file.name}`);
        }
      }
      if (fileInputRef.current) fileInputRef.current.value = '';
      await refreshFiles();
    } catch (err: any) {
      setUploadError(err.message || 'File upload failed.');
    } finally {
      setUploading(false);
      setDragActive(false);
    }
  };

  // Drag and drop handlers
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };
  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
      handleUpload(e as any); // Cast to any to satisfy handleUpload's overloaded type, DragEvent is compatible
    }
  };

  const handleRemoveFile = async (fileId: string) => {
    const file = files.find(f => f.id === fileId);
    if (!file) return;
    if (!window.confirm(`Remove file '${file.filename}'?`)) return;
    // fileId === backend filename; always use fileId for backend operations
    await fetch(getApiUrl(`files/${encodeURIComponent(fileId)}`), { method: 'DELETE' });
    await refreshFiles();
    setSelectedFiles(selectedFiles => selectedFiles.filter(id => id !== fileId));
  }

  const handleBulkDelete = async () => {
    if (selectedFiles.length === 0) return;
    const fileNames = files.filter(f => selectedFiles.includes(f.id)).map(f => f.filename);
    if (!window.confirm(`Remove selected files?\n${fileNames.join('\n')}`)) return;
    for (const file of files) {
      if (selectedFiles.includes(file.id)) {
        // fileId === backend filename; always use fileId for backend operations
        await fetch(getApiUrl(`files/${encodeURIComponent(file.id)}`), { method: 'DELETE' });
      }
    }
    await refreshFiles();
    setSelectedFiles([]);
  };

  const handleCheckboxChange = (fileId: string, checked: boolean) => {
    setSelectedFiles(selectedFiles => checked
      ? [...selectedFiles, fileId]
      : selectedFiles.filter(id => id !== fileId)
    );
  };

  const allSelected = files.length > 0 && selectedFiles.length === files.length;
  const handleSelectAll = (checked: boolean) => {
    setSelectedFiles(checked ? files.map(f => f.id) : []);
  };

  const handleImportToChart = (fileId: string) => {
    const file = files.find(f => f.id === fileId);
    if (!file) return;
    window.dispatchEvent(new CustomEvent('openChartImportModal', { detail: { id: file.id, filename: file.filename, type: file.type } }));
  };

  return (
    <div 
      onDragOver={handleDragOver} 
      onDragLeave={handleDragLeave} 
      onDrop={handleDrop} 
      style={{ position: 'relative' }} // Added position: relative for the overlay
    >
      {/* Inline upload progress and error banners */}
      {uploading && (
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
          background: 'var(--color-primary-light)', color: 'var(--color-primary)', fontWeight: 600, padding: '8px 0', borderRadius: 8, marginBottom: 10, fontSize: 15
        }}
        aria-live="polite" aria-atomic="true">
          <span className="spinner" style={{ width: 20, height: 20, border: '3px solid #1976d2', borderTop: '3px solid #e3f2fd', borderRadius: '50%', display: 'inline-block', animation: 'spin 0.9s linear infinite' }} />
          Uploading file(s)...
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      )}
      {uploadError && (
        <div
          style={{ background: 'var(--color-error)', color: 'var(--color-text-light)', padding: '10px 18px', borderRadius: 8, marginBottom: 10, display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 15, boxShadow: '0 2px 8px #0002' }}
          role="alert"
          aria-live="assertive"
          tabIndex={0}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span role="img" aria-label="Error">❌</span>
            {uploadError}
          </span>
          <button
            style={{ marginLeft: 16, background: 'none', border: 'none', color: 'var(--color-text-light)', fontSize: 18, cursor: 'pointer', borderRadius: 4, padding: '2px 8px' }}
            aria-label="Dismiss error"
            title="Dismiss error"
            onClick={() => setUploadError(null)}
            onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') setUploadError(null); }}
          >
            ×
          </button>
        </div>
      )}
      <div style={{ position: 'absolute', left: -9999, top: 'auto', width: 1, height: 1, overflow: 'hidden' }} id="file-upload-instructions">
        Drag and drop files here or press Enter/Space to open the file picker. Use Tab to navigate.
      </div>
      {dragActive && (
        <div style={{ position: 'absolute', inset: 0, background: 'rgba(25, 118, 210, 0.1)', zIndex: 2, borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', pointerEvents: 'none' }}>
          <span style={{ color: 'var(--color-primary)', fontSize: 24, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span role="img" aria-label="Drop files">📂</span> Drop files to upload
          </span>
        </div>
      )}
      <div style={{ zIndex: 1, textAlign: 'center', pointerEvents: dragActive ? 'none' : undefined }}>
        <h3 style={{ fontSize: 16, marginBottom: 8 }}>Upload CSV/XML/JSON</h3>
        <div style={{ color: '#666', fontSize: 13, marginBottom: 10 }}>
          Drag and drop files here, or <span
            style={{ color: 'var(--color-primary)', textDecoration: 'underline', cursor: 'pointer', borderRadius: 4, outline: 'none' }}
            onClick={() => fileInputRef.current?.click()}
            tabIndex={0}
            role="button"
            aria-label="Open file picker"
            onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') fileInputRef.current?.click(); }}
            onFocus={e => e.currentTarget.style.boxShadow = '0 0 0 2px var(--color-primary)'}
            onBlur={e => e.currentTarget.style.boxShadow = 'none'}
          >browse</span>.

        </div>
        <div style={{ color: '#888', fontSize: 12 }}>
          (Press Enter/Space to open file picker. Use Tab to navigate.)
        </div>
      </div>
      <div aria-live="polite" aria-atomic="true" style={{ position: 'absolute', left: -9999, top: 'auto', width: 1, height: 1, overflow: 'hidden' }}>
        {uploading && 'Uploading file(s)...'}
        {uploadError && `Error: ${uploadError}`}
      </div>
      <label
        style={{
          display: 'inline-block',
          background: dragActive ? '#1565c0' : '#1976d2',
          color: 'var(--color-text-light)',
          borderRadius: 5,
          padding: '7px 18px',
          fontWeight: 600,
          fontSize: 15,
          cursor: 'pointer',
          marginBottom: 8,
          outline: dragActive ? '2px solid #42a5f5' : undefined,
          boxShadow: dragActive ? '0 0 0 2px #42a5f5' : undefined,
          transition: 'background 0.2s, outline 0.2s',
        }}
        htmlFor="file-upload-input"
        aria-label="Upload file area. Drag and drop or click to browse."
      >
        {dragActive ? 'Drop files to upload' : 'Upload File'}
        <input
          id="file-upload-input"
          type="file"
          accept=".csv,.xml,.json"
          multiple // Added multiple to allow selecting multiple files via browse, consistent with loop in handleUpload
          onChange={handleUpload}
          ref={fileInputRef}
          style={{ display: 'none' }}
          aria-label="Upload CSV, XML, or JSON file"
        />
      </label>
      {uploadError && <div style={{ color: '#b71c1c', margin: '6px 0', fontWeight: 500 }}>{uploadError}</div>}
      {uploading && <div style={{ color: 'var(--color-primary)', margin: '6px 0' }}>Uploading...</div>}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
        <input
          type="checkbox"
          checked={allSelected}
          aria-label="Select all files"
          onChange={e => handleSelectAll(e.target.checked)}
          style={{ accentColor: 'var(--color-primary)', width: 18, height: 18, cursor: 'pointer' }}
        />
        <span style={{ fontSize: 15, color: 'var(--color-primary)', fontWeight: 600 }}>Select All</span>
        {selectedFiles.length > 0 && (
          <button
            aria-label={`Delete selected files (${selectedFiles.length})`}
            style={{ background: 'var(--color-error)', color: 'var(--color-text-light)', border: 'none', borderRadius: 6, padding: '7px 18px', fontWeight: 600, fontSize: 15, cursor: 'pointer', marginBottom: 8, outline: 'none' }}
            onFocus={e => e.currentTarget.style.boxShadow = '0 0 0 2px var(--color-primary)'}
            onBlur={e => e.currentTarget.style.boxShadow = 'none'}
            onClick={handleBulkDelete}
            tabIndex={0}
            onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') handleBulkDelete(); }}
            autoFocus
          >
            Delete Selected ({selectedFiles.length})
          </button>
        )}
      </div>
      <ul style={{ listStyle: 'none', padding: 0, marginTop: 12 }}>
        {files.map(file => (
          <li key={file.id} style={{ marginBottom: 10, background: '#f8fafc', borderRadius: 6, padding: '8px 8px 4px 8px', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', boxShadow: '0 1px 2px #0001' }}>
            <div style={{ display: 'flex', flexDirection: 'row', gap: 4, marginBottom: 2, alignItems: 'center' }}>
              <input
                type="checkbox"
                checked={selectedFiles.includes(file.id)}
                aria-label={`Select file ${file.id}`}
                onChange={e => handleCheckboxChange(file.id, e.target.checked)}
                style={{ accentColor: 'var(--color-primary)', width: 18, height: 18, cursor: 'pointer', marginRight: 6 }}
                tabIndex={0}
              />
              <button
                style={{ background: 'var(--color-success-bg)', color: 'var(--color-success)', border: '1px solid var(--color-success-border)', borderRadius: 4, padding: '2px 6px', fontSize: 13, cursor: 'pointer', minWidth: 28, outline: 'none' }}
                title="Preview/Edit file"
                aria-label="Preview/Edit file"
                onClick={() => setPreviewFileId(file.id)}
                tabIndex={0}
                onFocus={e => e.currentTarget.style.boxShadow = '0 0 0 2px var(--color-primary)'}
                onBlur={e => e.currentTarget.style.boxShadow = 'none'}
              >
                <span role="img" aria-label="Preview/Edit">👁️</span>
              </button>
              <button
                style={{ background: 'var(--color-warning-bg)', color: 'var(--color-primary)', border: '1px solid var(--color-warning-border)', borderRadius: 4, padding: '2px 6px', fontSize: 13, cursor: 'pointer', minWidth: 28, outline: 'none' }}
                title="Import to Chart"
                aria-label="Import to Chart"
                onClick={() => handleImportToChart(file.id)}
                tabIndex={0}
                onFocus={e => e.currentTarget.style.boxShadow = '0 0 0 2px var(--color-primary)'}
                onBlur={e => e.currentTarget.style.boxShadow = 'none'}
              >
                <span role="img" aria-label="Import to Chart">📊</span>
              </button>
              <button
                style={{ background: 'var(--color-error)', color: 'var(--color-text-light)', border: 'none', borderRadius: 4, padding: '2px 6px', fontSize: 16, cursor: 'pointer', minWidth: 28, outline: 'none' }}
                title="Remove file"
                aria-label="Remove file"
                onClick={() => handleRemoveFile(file.id)}
                tabIndex={0}
                onFocus={e => e.currentTarget.style.boxShadow = '0 0 0 2px var(--color-primary)'}
                onBlur={e => e.currentTarget.style.boxShadow = 'none'}
              >
                <span role="img" aria-label="Remove">🗑️</span>
              </button>
              <span style={{ marginLeft: 8 }}>
                <SchemaStatusBadge status={schemaStatus[file.id] || 'unconfirmed'} />
              </span>
            </div>
            <button
              style={{ fontFamily: 'monospace', fontSize: 13, background: 'var(--color-primary-light)', border: 'none', borderRadius: 4, padding: '3px 8px', marginTop: 1, width: '100%', textAlign: 'left', cursor: 'pointer', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', outline: 'none' }}
              onClick={() => onSelect(file.id)}
              title={file.filename}
              aria-label={`Select file ${file.id}`}
              tabIndex={0}
              onFocus={e => e.currentTarget.style.boxShadow = '0 0 0 2px var(--color-primary)'}
              onBlur={e => e.currentTarget.style.boxShadow = 'none'}
            >
              {file.filename}
            </button>
          </li>
        ))}
      </ul>
      {previewFileId && ReactDOM.createPortal(
        <div
          className="importModalBackdrop"
          tabIndex={-1}
          onMouseDown={e => {
            if (e.target === e.currentTarget) setPreviewFileId(null);
          }}
        >
          <div className="importModal" style={{ maxWidth: 800, width: '95vw' }}>
            <Suspense fallback={<div style={{ background: 'var(--color-bg)', padding: 32, borderRadius: 12 }}>Loading preview…</div>}>
              <FilePreview fileId={previewFileId} onClose={() => setPreviewFileId(null)} />
            </Suspense>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
}