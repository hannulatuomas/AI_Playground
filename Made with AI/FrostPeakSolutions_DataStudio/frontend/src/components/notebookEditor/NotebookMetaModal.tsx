import React from 'react';

interface NotebookMetaModalProps {
  meta: { title: string; description: string };
  onChange: (meta: { title: string; description: string }) => void;
  onSave: () => void;
  onCancel: () => void;
}

const NotebookMetaModal: React.FC<NotebookMetaModalProps> = ({ meta, onChange, onSave, onCancel }) => (
  <div className="importModalBackdrop">
    <div className="importModal">
      <h3>Edit Notebook Info</h3>
      <div style={{ marginBottom: 10 }}>
        <label>Title:<br />
          <input
            value={meta.title}
            onChange={e => onChange({ ...meta, title: e.target.value })}
            style={{ width: '100%' }}
          />
        </label>
      </div>
      <div style={{ marginBottom: 10 }}>
        <label>Description:<br />
          <textarea
            value={meta.description}
            onChange={e => onChange({ ...meta, description: e.target.value })}
            style={{ width: '100%' }}
            rows={3}
          />
        </label>
      </div>
      <button
        className="modalPrimaryButton"
        style={{ marginRight: 8 }}
        onClick={onSave}
      >Save</button>
      <button
        className="modalSecondaryButton"
        onClick={onCancel}
      >Cancel</button>
    </div>
  </div>
);

export default NotebookMetaModal;
