import React, { createContext, useContext, useEffect, useState } from 'react';
import { getApiUrl } from '../apiConfig';

export type DBType = 'postgres' | 'sqlite' | 'mysql' | 'sqlserver' | 'oracle' | 'mongodb' | 'neo4j';
export interface DBConnection {
  /**
   * Unique identifier for the connection (persistent, not array index)
   */
  uid: string;
  /**
   * User-friendly name for the connection (shown in sidebar, etc.)
   */
  displayName?: string;
  type: DBType;
  host?: string;
  port?: number;
  user?: string;
  password?: string;
  database?: string;
  file?: string;
  // MongoDB specific
  mongoUri?: string;
  // Neo4j specific
  neo4jUri?: string;
  neo4jUser?: string;
  neo4jPassword?: string;
}

interface ConnectionContextType {
  connections: DBConnection[];
  addConnection: (conn: DBConnection) => void;
  removeConnection: (idx: number) => void;
  selected: number | null;
  setSelected: (idx: number | null) => void;
}

const ConnectionContext = createContext<ConnectionContextType | undefined>(undefined);



export function ConnectionProvider({ children }: { children: React.ReactNode }) {
  const [connections, setConnections] = useState<DBConnection[]>([]);
  const [selected, setSelected] = useState<number | null>(null);

  // --- UID generator ---
  function generateUID() {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
    return 'conn_' + Math.random().toString(36).substr(2, 9) + Date.now();
  }

  // --- Load from localStorage on mount ---
  useEffect(() => {
    const stored = localStorage.getItem('connections');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) setConnections(parsed);
      } catch {}
    }
  }, []);

  // --- Save to localStorage whenever connections change ---
  useEffect(() => {
    localStorage.setItem('connections', JSON.stringify(connections));
  }, [connections]);

  const addConnection = (conn: DBConnection) => {
    // Ensure UID exists
    const withUid = { ...conn, uid: conn.uid || generateUID() };
    setConnections(cs => {
      const updated = [...cs, withUid];
      localStorage.setItem('connections', JSON.stringify(updated));
      return updated;
    });
  };

  const removeConnection = (idx: number) => {
    setConnections(cs => {
      const updated = cs.filter((_, i) => i !== idx);
      localStorage.setItem('connections', JSON.stringify(updated));
      return updated;
    });
    setSelected(sel => (sel === idx ? null : sel && sel > idx ? sel - 1 : sel));
  };

  return (
    <ConnectionContext.Provider value={{ connections, addConnection, removeConnection, selected, setSelected }}>
      {children}
    </ConnectionContext.Provider>
  );
}

export function useConnectionContext() {
  const ctx = useContext(ConnectionContext);
  if (!ctx) throw new Error('useConnectionContext must be used within ConnectionProvider');
  return ctx;
}
