import { useEffect, useState } from 'react';
import { getApiUrl } from '../apiConfig';
import { DbTableSchema, SchemaApiResponse } from '../schemaTypes';

/**
 * Fetches schema for the given DB connection UID.
 * @param uid UID of the DB connection (or null)
 * @returns { tables: TableSchema[], loading: boolean, error: string|null }
 */
export function useSchema(uid: string | null) {
  const [tables, setTables] = useState<DbTableSchema[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    if (uid == null) {
      setTables([]);
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    // Step 1: Fetch tables
    fetch(getApiUrl('schema/tables'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uid })
    })
      .then(res => res.json())
      .then(async (data) => {
        if (!isMounted) return;
        if (data.success && Array.isArray(data.tables)) {
          // Step 2: For each table, fetch columns
          const tableNames: string[] = data.tables;
          const tablePromises = tableNames.map(table =>
            fetch(getApiUrl('schema/columns'), {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ uid, table })
            })
              .then(res => res.json())
              .then((colData) => {
                if (colData.success && Array.isArray(colData.columns)) {
                  return { table, columns: colData.columns } as DbTableSchema;
                } else {
                  return { table, columns: [] } as DbTableSchema;
                }
              })
              .catch(() => ({ table, columns: [] } as DbTableSchema))
          );
          const hydratedTables = await Promise.all(tablePromises);
          if (isMounted) setTables(hydratedTables);
        } else {
          setError(data.error || 'Failed to fetch tables');
          setTables([]);
        }
        setLoading(false);
      })
      .catch(err => {
        if (isMounted) {
          setError(err.message || 'Failed to fetch tables');
          setTables([]);
          setLoading(false);
        }
      });
    return () => { isMounted = false; };
  }, [uid]);

  return { tables, loading, error };
}

