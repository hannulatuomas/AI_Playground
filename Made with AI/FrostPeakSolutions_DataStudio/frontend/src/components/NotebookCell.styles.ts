// Centralized styles for NotebookCell (extracted from inline styles)

export const cellContent: React.CSSProperties = {
  padding: '14px 18px 14px 18px',
  boxSizing: 'border-box',
};

export const fileSelectorRow: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  marginBottom: 12,
};

export const fileSelector: React.CSSProperties = {
  marginRight: 12,
  padding: '2px 10px',
  borderRadius: 5,
  border: '1px solid var(--color-border-light)',
  background: 'var(--color-primary-light)',
  color: 'var(--color-primary)',
  fontWeight: 600,
  fontSize: 14,
  cursor: 'pointer',
  height: 28,
};

export const fileSchemaStatus: React.CSSProperties = {
  marginLeft: 8,
};

export const fileSchemaPreview: React.CSSProperties = {
  margin: '8px 0 0 0',
};
