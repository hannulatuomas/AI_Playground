import { useState, useEffect } from 'react';
import { getApiUrl } from '../apiConfig';
import { DbColumnSchema } from '../schemaTypes';

export function useTableColumns(uid: string | null, table: string | null, enabled: boolean) {
  const [columns, setColumns] = useState<DbColumnSchema[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled || !uid || !table) {
      setColumns(null);
      setError(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    // Find the full connection object using ConnectionContext
    let connObj: any = null;
    try {
      // Dynamically import context to avoid React hook rules violation
      // (since this is a hook, we can't use useConnectionContext directly here)
      connObj = JSON.parse(localStorage.getItem('connections') || '[]').find((c: any) => c.uid === uid) || null;
    } catch {}
    if (!connObj) {
      setColumns([]);
      setError('Connection details not found for this UID. Please reselect or recreate the connection.');
      setLoading(false);
      return;
    }
    fetch(getApiUrl('schema/columns'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...connObj, table })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success && Array.isArray(data.columns)) {
          setColumns(data.columns);
        } else {
          setColumns([]);
          setError(data.error || 'Failed to fetch columns');
        }
        setLoading(false);
      })
      .catch(err => {
        setColumns([]);
        setError(err.message || 'Failed to fetch columns');
        setLoading(false);
      });
  }, [uid, table, enabled]);

  return { columns, loading, error };
}
