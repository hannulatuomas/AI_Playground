import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getApiUrl } from '../apiConfig';
import { generateFileId } from '../utils/fileUtils';

export type FileItem = {
  id: string;
  filename: string;
  type: 'csv' | 'xml';
};

interface FileContextType {
  files: FileItem[];
  refreshFiles: () => Promise<void>;
  loading: boolean;
  error: string | null;
  schemaStatus: Record<string, 'unconfirmed' | 'confirmed' | 'editing'>;
  setSchemaStatus: (fileId: string, status: 'unconfirmed' | 'confirmed' | 'editing') => void;
}

const FileContext = createContext<FileContextType | undefined>(undefined);

export const useFileContext = () => {
  const ctx = useContext(FileContext);
  if (!ctx) throw new Error('useFileContext must be used within a FileProvider');
  return ctx;
};

export const FileProvider = ({ children }: { children: ReactNode }) => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [schemaStatus, setSchemaStatusState] = useState<Record<string, 'unconfirmed' | 'confirmed' | 'editing'>>({});

  const setSchemaStatus = (fileId: string, status: 'unconfirmed' | 'confirmed' | 'editing') => {
    setSchemaStatusState(prev => ({ ...prev, [fileId]: status }));
  };

  const refreshFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(getApiUrl('files'));
      if (!res.ok) throw new Error('Failed to fetch files');
      const data = await res.json();
      if (data.success && Array.isArray(data.files)) {
        setFiles(
          data.files
            .filter((f: string) => /\.(csv|xml)$/i.test(f))
            .map((f: string) => {
              const type = f.toLowerCase().endsWith('.csv') ? 'csv' : 'xml';
              return {
                id: generateFileId(f, type),
                filename: f,
                type,
              };
            })
        );
      } else {
        setFiles([]);
      }
    } catch (e: any) {
      console.error('Failed to refresh files:', e);
      setError(e.message || 'Unknown error');
      setFiles([]);
    }
    setLoading(false);
  };

  useEffect(() => {
    refreshFiles();
  }, []);

  // Initialize schemaStatus for new files as 'unconfirmed' if not already set
  useEffect(() => {
    setSchemaStatusState(prev => {
      const updated = { ...prev };
      files.forEach(file => {
        if (!(file.id in updated)) {
          updated[file.id] = 'unconfirmed';
        }
      });
      return updated;
    });
  }, [files]);

  return (
    <FileContext.Provider value={{ files, refreshFiles, loading, error, schemaStatus, setSchemaStatus }}>
      {children}
    </FileContext.Provider>
  );
};
