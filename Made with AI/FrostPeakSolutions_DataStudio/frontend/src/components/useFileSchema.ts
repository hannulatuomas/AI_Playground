import { useCallback } from 'react';
import { useFileContext } from './FileContext';
import { FileColumnSchema } from '../schemaTypes';

const LOCALSTORAGE_KEY = 'file_schema_overrides';

export function useFileSchema(fileId: string) {
  const { schemaStatus, setSchemaStatus } = useFileContext();

  // Load schema override from localStorage
  const loadSchemaOverride = useCallback((): FileColumnSchema[] | null => {
    const raw = localStorage.getItem(LOCALSTORAGE_KEY);
    if (!raw) return null;
    try {
      const obj = JSON.parse(raw);
      return obj[fileId] || null;
    } catch {
      return null;
    }
  }, [fileId]);

  // Save schema override to localStorage
  const saveSchemaOverride = useCallback((schema: FileColumnSchema[]) => {
    let obj: Record<string, FileColumnSchema[]> = {};
    const raw = localStorage.getItem(LOCALSTORAGE_KEY);
    if (raw) {
      try { obj = JSON.parse(raw); } catch { obj = {}; }
    }
    obj[fileId] = schema;
    localStorage.setItem(LOCALSTORAGE_KEY, JSON.stringify(obj));
    setSchemaStatus(fileId, 'confirmed');
  }, [fileId, setSchemaStatus]);

  // Set schema status
  const setStatus = useCallback((status: 'unconfirmed' | 'confirmed' | 'editing') => {
    setSchemaStatus(fileId, status);
  }, [fileId, setSchemaStatus]);

  // Get current schema status
  const status = schemaStatus[fileId] || 'unconfirmed';

  return {
    loadSchemaOverride,
    saveSchemaOverride,
    setStatus,
    status,
  };
}
