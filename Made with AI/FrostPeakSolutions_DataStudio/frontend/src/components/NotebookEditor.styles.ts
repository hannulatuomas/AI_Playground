// Centralized styles for NotebookEditor (extracted from inline styles)

export const ungroupedDroppableStyle = (isDraggingOver: boolean): React.CSSProperties => ({
  minHeight: 32,
  marginBottom: 16,
  background: isDraggingOver ? 'var(--color-primary-light)' : undefined,
  borderRadius: 6,
});

export const addGroupButtonRow: React.CSSProperties = {
  display: 'flex',
  gap: 12,
  marginTop: 16,
};
