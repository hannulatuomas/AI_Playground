import React, { useState } from 'react';
import FilePreview from './FilePreview';

import { useFileContext } from './FileContext';

export default function NotebookEditorFilePreview({ fileIds }: { fileIds: string[] }) {
  const { files: allFiles } = useFileContext();
  const [previewId, setPreviewId] = useState<string | null>(null);

  return (
    <>
      <div style={{ margin: '12px 0', display: 'flex', gap: 8 }}>
        {fileIds.map(fileId => {
          const file = allFiles.find(f => f.id === fileId);
          if (!file) return null;
          return (
            <button
              key={fileId}
              style={{ fontFamily: 'monospace', fontSize: 13, background: 'var(--color-primary-light)', border: '1px solid var(--color-border-accent)', borderRadius: 4, padding: '3px 10px' }}
              onClick={() => setPreviewId(fileId)}
            >
              Preview {file.type.toUpperCase()}: {file.filename}
            </button>
          );
        })}
      </div>
      {previewId && (
        <FilePreview fileId={previewId} onClose={() => setPreviewId(null)} />
      )}
    </>
  );
}

