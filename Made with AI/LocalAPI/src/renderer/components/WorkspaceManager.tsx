// Workspace Manager Component
// Manages workspaces: create, load, delete, recent workspaces

import React, { useState, useEffect } from 'react';

interface Workspace {
  id: string;
  name: string;
  description?: string;
  createdAt: Date;
  updatedAt: Date;
  lastOpenedAt?: Date;
}

interface WorkspaceMetadata {
  id: string;
  name: string;
  description?: string;
  path: string;
  lastOpenedAt: Date;
  createdAt: Date;
  updatedAt: Date;
}

export const WorkspaceManager: React.FC = () => {
  const [workspaces, setWorkspaces] = useState<WorkspaceMetadata[]>([]);
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newWorkspaceName, setNewWorkspaceName] = useState('');
  const [newWorkspaceDesc, setNewWorkspaceDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWorkspaces();
    loadCurrentWorkspace();
  }, []);

  const loadWorkspaces = async () => {
    try {
      const list = await window.electronAPI.workspace.list();
      setWorkspaces(list);
    } catch (err) {
      console.error('Failed to load workspaces:', err);
      setError('Failed to load workspaces');
    }
  };

  const loadCurrentWorkspace = async () => {
    try {
      const current = await window.electronAPI.workspace.getCurrent();
      setCurrentWorkspace(current);
    } catch (err) {
      console.error('Failed to load current workspace:', err);
    }
  };

  const handleCreateWorkspace = async () => {
    if (!newWorkspaceName.trim()) {
      setError('Workspace name is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const workspace = await window.electronAPI.workspace.create(
        newWorkspaceName,
        newWorkspaceDesc || undefined
      );
      await window.electronAPI.workspace.save(workspace);
      setCurrentWorkspace(workspace);
      setShowCreateDialog(false);
      setNewWorkspaceName('');
      setNewWorkspaceDesc('');
      await loadWorkspaces();
    } catch (err: any) {
      console.error('Failed to create workspace:', err);
      setError(err.message || 'Failed to create workspace');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadWorkspace = async (workspaceId: string) => {
    setLoading(true);
    setError(null);

    try {
      const workspace = await window.electronAPI.workspace.load(workspaceId);
      setCurrentWorkspace(workspace);
      await loadWorkspaces();
    } catch (err: any) {
      console.error('Failed to load workspace:', err);
      setError(err.message || 'Failed to load workspace');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteWorkspace = async (workspaceId: string) => {
    if (!confirm('Are you sure you want to delete this workspace?')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await window.electronAPI.workspace.delete(workspaceId);
      if (currentWorkspace?.id === workspaceId) {
        setCurrentWorkspace(null);
      }
      await loadWorkspaces();
    } catch (err: any) {
      console.error('Failed to delete workspace:', err);
      setError(err.message || 'Failed to delete workspace');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveWorkspace = async () => {
    if (!currentWorkspace) return;

    setLoading(true);
    setError(null);

    try {
      await window.electronAPI.workspace.save();
      await loadWorkspaces();
    } catch (err: any) {
      console.error('Failed to save workspace:', err);
      setError(err.message || 'Failed to save workspace');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (date: Date | string) => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString();
  };

  return (
    <div className="workspace-manager">
      <div className="workspace-header">
        <h2>Workspace Manager</h2>
        <div className="workspace-actions">
          <button onClick={() => setShowCreateDialog(true)} disabled={loading}>
            New Workspace
          </button>
          {currentWorkspace && (
            <button onClick={handleSaveWorkspace} disabled={loading}>
              Save Current
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {currentWorkspace && (
        <div className="current-workspace">
          <h3>Current Workspace</h3>
          <div className="workspace-info">
            <strong>{currentWorkspace.name}</strong>
            {currentWorkspace.description && <p>{currentWorkspace.description}</p>}
            <small>Last updated: {formatDate(currentWorkspace.updatedAt)}</small>
          </div>
        </div>
      )}

      <div className="workspaces-list">
        <h3>All Workspaces ({workspaces.length})</h3>
        {workspaces.length === 0 ? (
          <p className="empty-state">No workspaces found. Create one to get started.</p>
        ) : (
          <div className="workspace-grid">
            {workspaces.map((ws) => (
              <div
                key={ws.id}
                className={`workspace-card ${currentWorkspace?.id === ws.id ? 'active' : ''}`}
              >
                <div className="workspace-card-header">
                  <h4>{ws.name}</h4>
                  <div className="workspace-card-actions">
                    {currentWorkspace?.id !== ws.id && (
                      <button
                        onClick={() => handleLoadWorkspace(ws.id)}
                        disabled={loading}
                        title="Load workspace"
                      >
                        Load
                      </button>
                    )}
                    <button
                      onClick={() => handleDeleteWorkspace(ws.id)}
                      disabled={loading}
                      className="danger"
                      title="Delete workspace"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                {ws.description && <p className="workspace-description">{ws.description}</p>}
                <div className="workspace-meta">
                  <small>Created: {formatDate(ws.createdAt)}</small>
                  <small>Last opened: {formatDate(ws.lastOpenedAt)}</small>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showCreateDialog && (
        <div className="modal-overlay" onClick={() => setShowCreateDialog(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Workspace</h3>
              <button onClick={() => setShowCreateDialog(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label htmlFor="workspace-name">Name *</label>
                <input
                  id="workspace-name"
                  type="text"
                  value={newWorkspaceName}
                  onChange={(e) => setNewWorkspaceName(e.target.value)}
                  placeholder="My Workspace"
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label htmlFor="workspace-desc">Description</label>
                <textarea
                  id="workspace-desc"
                  value={newWorkspaceDesc}
                  onChange={(e) => setNewWorkspaceDesc(e.target.value)}
                  placeholder="Optional description"
                  rows={3}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button onClick={() => setShowCreateDialog(false)} disabled={loading}>
                Cancel
              </button>
              <button
                onClick={handleCreateWorkspace}
                disabled={loading || !newWorkspaceName.trim()}
                className="primary"
              >
                {loading ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .workspace-manager {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .workspace-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .workspace-actions {
          display: flex;
          gap: 10px;
        }

        .error-message {
          background: #fee;
          border: 1px solid #fcc;
          padding: 10px;
          border-radius: 4px;
          margin-bottom: 20px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .current-workspace {
          background: #f0f8ff;
          border: 2px solid #4a90e2;
          padding: 15px;
          border-radius: 8px;
          margin-bottom: 20px;
        }

        .workspace-info {
          margin-top: 10px;
        }

        .workspaces-list h3 {
          margin-bottom: 15px;
        }

        .empty-state {
          text-align: center;
          color: #666;
          padding: 40px;
        }

        .workspace-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 15px;
        }

        .workspace-card {
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 15px;
          background: white;
          transition: all 0.2s;
        }

        .workspace-card:hover {
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .workspace-card.active {
          border-color: #4a90e2;
          background: #f0f8ff;
        }

        .workspace-card-header {
          display: flex;
          justify-content: space-between;
          align-items: start;
          margin-bottom: 10px;
        }

        .workspace-card-header h4 {
          margin: 0;
          flex: 1;
        }

        .workspace-card-actions {
          display: flex;
          gap: 5px;
        }

        .workspace-description {
          color: #666;
          font-size: 0.9em;
          margin: 10px 0;
        }

        .workspace-meta {
          display: flex;
          flex-direction: column;
          gap: 5px;
          margin-top: 10px;
          padding-top: 10px;
          border-top: 1px solid #eee;
        }

        .workspace-meta small {
          color: #999;
          font-size: 0.85em;
        }

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal-content {
          background: white;
          border-radius: 8px;
          width: 90%;
          max-width: 500px;
          max-height: 90vh;
          overflow: auto;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          border-bottom: 1px solid #eee;
        }

        .modal-header h3 {
          margin: 0;
        }

        .modal-body {
          padding: 20px;
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
          padding: 20px;
          border-top: 1px solid #eee;
        }

        .form-group {
          margin-bottom: 15px;
        }

        .form-group label {
          display: block;
          margin-bottom: 5px;
          font-weight: 500;
        }

        .form-group input,
        .form-group textarea {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-family: inherit;
        }

        button {
          padding: 8px 16px;
          border: 1px solid #ddd;
          border-radius: 4px;
          background: white;
          cursor: pointer;
          font-size: 14px;
        }

        button:hover:not(:disabled) {
          background: #f5f5f5;
        }

        button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        button.primary {
          background: #4a90e2;
          color: white;
          border-color: #4a90e2;
        }

        button.primary:hover:not(:disabled) {
          background: #357abd;
        }

        button.danger {
          color: #d32f2f;
        }

        button.danger:hover:not(:disabled) {
          background: #ffebee;
        }
      `}</style>
    </div>
  );
};
