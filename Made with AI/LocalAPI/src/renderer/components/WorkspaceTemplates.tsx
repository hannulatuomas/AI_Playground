// Workspace Templates Component
// Manage workspace templates and snapshots

import React, { useState, useEffect } from 'react';

interface WorkspaceTemplate {
  id: string;
  name: string;
  description?: string;
  tags?: string[];
  createdAt: Date;
  updatedAt: Date;
}

interface WorkspaceSnapshot {
  id: string;
  workspaceId: string;
  name: string;
  description?: string;
  createdAt: Date;
}

export const WorkspaceTemplates: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'templates' | 'snapshots'>('templates');
  const [templates, setTemplates] = useState<WorkspaceTemplate[]>([]);
  const [snapshots, setSnapshots] = useState<WorkspaceSnapshot[]>([]);
  const [showCreateTemplate, setShowCreateTemplate] = useState(false);
  const [showCreateSnapshot, setShowCreateSnapshot] = useState(false);
  const [showLoadTemplate, setShowLoadTemplate] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [templateName, setTemplateName] = useState('');
  const [templateDesc, setTemplateDesc] = useState('');
  const [templateTags, setTemplateTags] = useState('');
  const [snapshotName, setSnapshotName] = useState('');
  const [snapshotDesc, setSnapshotDesc] = useState('');
  const [workspaceName, setWorkspaceName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTemplates();
    loadSnapshots();
  }, []);

  const loadTemplates = async () => {
    try {
      const list = await window.electronAPI.workspace.listTemplates();
      setTemplates(list);
    } catch (err) {
      console.error('Failed to load templates:', err);
    }
  };

  const loadSnapshots = async () => {
    try {
      const current = await window.electronAPI.workspace.getCurrent();
      if (current) {
        const list = await window.electronAPI.workspace.listSnapshots(current.id);
        setSnapshots(list);
      }
    } catch (err) {
      console.error('Failed to load snapshots:', err);
    }
  };

  const handleSaveAsTemplate = async () => {
    if (!templateName.trim()) {
      setError('Template name is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const tags = templateTags.split(',').map(t => t.trim()).filter(Boolean);
      await window.electronAPI.workspace.saveAsTemplate(
        templateName,
        templateDesc || undefined,
        tags.length > 0 ? tags : undefined
      );
      setShowCreateTemplate(false);
      setTemplateName('');
      setTemplateDesc('');
      setTemplateTags('');
      await loadTemplates();
    } catch (err: any) {
      console.error('Failed to save template:', err);
      setError(err.message || 'Failed to save template');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadFromTemplate = async () => {
    if (!selectedTemplate || !workspaceName.trim()) {
      setError('Please select a template and enter a workspace name');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await window.electronAPI.workspace.loadFromTemplate(selectedTemplate, workspaceName);
      setShowLoadTemplate(false);
      setSelectedTemplate(null);
      setWorkspaceName('');
    } catch (err: any) {
      console.error('Failed to load from template:', err);
      setError(err.message || 'Failed to load from template');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTemplate = async (templateId: string) => {
    if (!confirm('Are you sure you want to delete this template?')) {
      return;
    }

    setLoading(true);
    try {
      await window.electronAPI.workspace.deleteTemplate(templateId);
      await loadTemplates();
    } catch (err: any) {
      console.error('Failed to delete template:', err);
      setError(err.message || 'Failed to delete template');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSnapshot = async () => {
    if (!snapshotName.trim()) {
      setError('Snapshot name is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await window.electronAPI.workspace.createSnapshot(
        snapshotName,
        snapshotDesc || undefined
      );
      setShowCreateSnapshot(false);
      setSnapshotName('');
      setSnapshotDesc('');
      await loadSnapshots();
    } catch (err: any) {
      console.error('Failed to create snapshot:', err);
      setError(err.message || 'Failed to create snapshot');
    } finally {
      setLoading(false);
    }
  };

  const handleRestoreSnapshot = async (snapshotId: string) => {
    if (!confirm('Are you sure you want to restore this snapshot? Current changes will be lost.')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await window.electronAPI.workspace.restoreSnapshot(snapshotId);
      await loadSnapshots();
    } catch (err: any) {
      console.error('Failed to restore snapshot:', err);
      setError(err.message || 'Failed to restore snapshot');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSnapshot = async (snapshotId: string) => {
    if (!confirm('Are you sure you want to delete this snapshot?')) {
      return;
    }

    setLoading(true);
    try {
      await window.electronAPI.workspace.deleteSnapshot(snapshotId);
      await loadSnapshots();
    } catch (err: any) {
      console.error('Failed to delete snapshot:', err);
      setError(err.message || 'Failed to delete snapshot');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (date: Date | string) => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString();
  };

  return (
    <div className="workspace-templates">
      <div className="templates-header">
        <h2>Workspace Templates & Snapshots</h2>
        <div className="tab-buttons">
          <button
            className={activeTab === 'templates' ? 'active' : ''}
            onClick={() => setActiveTab('templates')}
          >
            Templates ({templates.length})
          </button>
          <button
            className={activeTab === 'snapshots' ? 'active' : ''}
            onClick={() => setActiveTab('snapshots')}
          >
            Snapshots ({snapshots.length})
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {activeTab === 'templates' && (
        <div className="templates-content">
          <div className="content-actions">
            <button onClick={() => setShowCreateTemplate(true)} disabled={loading}>
              Save Current as Template
            </button>
            <button onClick={() => setShowLoadTemplate(true)} disabled={loading || templates.length === 0}>
              Load from Template
            </button>
          </div>

          {templates.length === 0 ? (
            <p className="empty-state">No templates found. Save your current workspace as a template.</p>
          ) : (
            <div className="items-grid">
              {templates.map((template) => (
                <div key={template.id} className="item-card">
                  <div className="item-header">
                    <h4>{template.name}</h4>
                    <button
                      onClick={() => handleDeleteTemplate(template.id)}
                      disabled={loading}
                      className="danger"
                      title="Delete template"
                    >
                      Delete
                    </button>
                  </div>
                  {template.description && <p className="item-description">{template.description}</p>}
                  {template.tags && template.tags.length > 0 && (
                    <div className="tags">
                      {template.tags.map((tag, i) => (
                        <span key={i} className="tag">{tag}</span>
                      ))}
                    </div>
                  )}
                  <div className="item-meta">
                    <small>Created: {formatDate(template.createdAt)}</small>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'snapshots' && (
        <div className="snapshots-content">
          <div className="content-actions">
            <button onClick={() => setShowCreateSnapshot(true)} disabled={loading}>
              Create Snapshot
            </button>
          </div>

          {snapshots.length === 0 ? (
            <p className="empty-state">No snapshots found. Create a snapshot to save the current state.</p>
          ) : (
            <div className="items-grid">
              {snapshots.map((snapshot) => (
                <div key={snapshot.id} className="item-card">
                  <div className="item-header">
                    <h4>{snapshot.name}</h4>
                    <div className="item-actions">
                      <button
                        onClick={() => handleRestoreSnapshot(snapshot.id)}
                        disabled={loading}
                        title="Restore snapshot"
                      >
                        Restore
                      </button>
                      <button
                        onClick={() => handleDeleteSnapshot(snapshot.id)}
                        disabled={loading}
                        className="danger"
                        title="Delete snapshot"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                  {snapshot.description && <p className="item-description">{snapshot.description}</p>}
                  <div className="item-meta">
                    <small>Created: {formatDate(snapshot.createdAt)}</small>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Create Template Dialog */}
      {showCreateTemplate && (
        <div className="modal-overlay" onClick={() => setShowCreateTemplate(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Save as Template</h3>
              <button onClick={() => setShowCreateTemplate(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={templateName}
                  onChange={(e) => setTemplateName(e.target.value)}
                  placeholder="My Template"
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={templateDesc}
                  onChange={(e) => setTemplateDesc(e.target.value)}
                  placeholder="Optional description"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>Tags (comma-separated)</label>
                <input
                  type="text"
                  value={templateTags}
                  onChange={(e) => setTemplateTags(e.target.value)}
                  placeholder="api, testing, development"
                />
              </div>
            </div>
            <div className="modal-footer">
              <button onClick={() => setShowCreateTemplate(false)} disabled={loading}>
                Cancel
              </button>
              <button
                onClick={handleSaveAsTemplate}
                disabled={loading || !templateName.trim()}
                className="primary"
              >
                {loading ? 'Saving...' : 'Save Template'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Load Template Dialog */}
      {showLoadTemplate && (
        <div className="modal-overlay" onClick={() => setShowLoadTemplate(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Load from Template</h3>
              <button onClick={() => setShowLoadTemplate(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Select Template *</label>
                <select
                  value={selectedTemplate || ''}
                  onChange={(e) => setSelectedTemplate(e.target.value)}
                >
                  <option value="">-- Select a template --</option>
                  {templates.map((t) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>New Workspace Name *</label>
                <input
                  type="text"
                  value={workspaceName}
                  onChange={(e) => setWorkspaceName(e.target.value)}
                  placeholder="My New Workspace"
                />
              </div>
            </div>
            <div className="modal-footer">
              <button onClick={() => setShowLoadTemplate(false)} disabled={loading}>
                Cancel
              </button>
              <button
                onClick={handleLoadFromTemplate}
                disabled={loading || !selectedTemplate || !workspaceName.trim()}
                className="primary"
              >
                {loading ? 'Loading...' : 'Load Template'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Snapshot Dialog */}
      {showCreateSnapshot && (
        <div className="modal-overlay" onClick={() => setShowCreateSnapshot(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create Snapshot</h3>
              <button onClick={() => setShowCreateSnapshot(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={snapshotName}
                  onChange={(e) => setSnapshotName(e.target.value)}
                  placeholder="Before major changes"
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={snapshotDesc}
                  onChange={(e) => setSnapshotDesc(e.target.value)}
                  placeholder="Optional description"
                  rows={3}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button onClick={() => setShowCreateSnapshot(false)} disabled={loading}>
                Cancel
              </button>
              <button
                onClick={handleCreateSnapshot}
                disabled={loading || !snapshotName.trim()}
                className="primary"
              >
                {loading ? 'Creating...' : 'Create Snapshot'}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .workspace-templates {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .templates-header {
          margin-bottom: 20px;
        }

        .tab-buttons {
          display: flex;
          gap: 10px;
          margin-top: 15px;
        }

        .tab-buttons button {
          padding: 10px 20px;
          border: 1px solid #ddd;
          background: white;
          cursor: pointer;
          border-radius: 4px 4px 0 0;
        }

        .tab-buttons button.active {
          background: #4a90e2;
          color: white;
          border-color: #4a90e2;
        }

        .content-actions {
          display: flex;
          gap: 10px;
          margin-bottom: 20px;
        }

        .empty-state {
          text-align: center;
          color: #666;
          padding: 40px;
        }

        .items-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 15px;
        }

        .item-card {
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 15px;
          background: white;
        }

        .item-header {
          display: flex;
          justify-content: space-between;
          align-items: start;
          margin-bottom: 10px;
        }

        .item-header h4 {
          margin: 0;
          flex: 1;
        }

        .item-actions {
          display: flex;
          gap: 5px;
        }

        .item-description {
          color: #666;
          font-size: 0.9em;
          margin: 10px 0;
        }

        .tags {
          display: flex;
          flex-wrap: wrap;
          gap: 5px;
          margin: 10px 0;
        }

        .tag {
          background: #e3f2fd;
          color: #1976d2;
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 0.85em;
        }

        .item-meta {
          margin-top: 10px;
          padding-top: 10px;
          border-top: 1px solid #eee;
        }

        .item-meta small {
          color: #999;
          font-size: 0.85em;
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
        .form-group textarea,
        .form-group select {
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
