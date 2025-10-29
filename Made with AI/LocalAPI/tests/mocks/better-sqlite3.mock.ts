/**
 * Comprehensive mock for better-sqlite3
 * Provides in-memory database simulation for testing
 */

export interface MockStatement {
  run: (...params: any[]) => { changes: number; lastInsertRowid: number };
  get: (...params: any[]) => any;
  all: (...params: any[]) => any[];
}

export interface MockDatabase {
  prepare: jest.Mock<MockStatement>;
  exec: jest.Mock;
  pragma: jest.Mock;
  close: jest.Mock;
  _tables: Map<string, any[]>;
}

/**
 * Creates a mock better-sqlite3 database instance
 */
export function createMockDatabase(): MockDatabase {
  const tables = new Map<string, any[]>();

  // Helper function to execute SQL INSERT
  const executeInsert = (sql: string, params: any[]): void => {
    const tableMatch = sql.match(/INSERT\s+(?:OR\s+REPLACE\s+)?INTO\s+(\w+)/i);
    if (!tableMatch) return;

    const tableName = tableMatch[1];
    
    if (!tables.has(tableName)) {
      tables.set(tableName, []);
    }

    // Extract column names
    const columnsMatch = sql.match(/\(([^)]+)\)\s*VALUES/i);
    if (!columnsMatch) return;

    const columns = columnsMatch[1].split(',').map(c => c.trim());
    
    // Create row object
    const row: any = {};
    columns.forEach((col, index) => {
      row[col] = params[index];
    });

    const table = tables.get(tableName)!;
    
    // Handle INSERT OR REPLACE
    if (sql.match(/INSERT\s+OR\s+REPLACE/i)) {
      // Find and remove existing row with same primary key (id)
      // For settings table, also check 'key' column as it's the primary key there
      const existingIndex = table.findIndex(r => {
        if (tableName === 'settings') {
          return r.key === row.key;
        }
        return r.id === row.id;
      });
      if (existingIndex !== -1) {
        table.splice(existingIndex, 1);
      }
    }

    table.push(row);
  };

  // Helper function to execute SQL UPDATE
  const executeUpdate = (sql: string, params: any[]): void => {
    const tableMatch = sql.match(/UPDATE\s+(\w+)/i);
    if (!tableMatch) return;

    const tableName = tableMatch[1];
    if (!tables.has(tableName)) return;

    // Handle UPDATE with no WHERE clause (e.g., "UPDATE environments SET is_active = 0")
    const whereMatch = sql.match(/WHERE\s+(\w+)\s*=\s*\?/i);
    
    const table = tables.get(tableName)!;
    
    if (!whereMatch) {
      // No WHERE clause - update all rows
      const setMatch = sql.match(/SET\s+(.+?)(?:\s*$)/i);
      if (!setMatch) return;
      
      const setPairs = setMatch[1].split(',').map(p => p.trim());
      
      table.forEach(row => {
        setPairs.forEach((pair, index) => {
          const [col, value] = pair.split('=').map(s => s.trim());
          // If value is a literal number, parse it
          if (value && !value.includes('?')) {
            row[col] = isNaN(Number(value)) ? value : Number(value);
          } else if (params.length > index) {
            row[col] = params[index];
          }
        });
      });
      return;
    }

    const whereColumn = whereMatch[1];
    const whereValue = params[params.length - 1];

    // Extract SET columns (use[\s\S] instead of . to match newlines)
    const setMatch = sql.match(/SET\s+([\s\S]+?)\s+WHERE/i);
    if (!setMatch) return;

    const setPairs = setMatch[1].split(',').map(p => p.trim());
    const columns = setPairs.map(p => p.split('=')[0].trim());

    const row = table.find(r => r[whereColumn] === whereValue);
    
    if (row) {
      columns.forEach((col, index) => {
        row[col] = params[index];
      });
    }
  };

  // Helper function to execute SQL DELETE
  const executeDelete = (sql: string, params: any[]): void => {
    const tableMatch = sql.match(/DELETE\s+FROM\s+(\w+)/i);
    if (!tableMatch) return;

    const tableName = tableMatch[1];
    if (!tables.has(tableName)) return;

    const whereMatch = sql.match(/WHERE\s+(\w+)\s*=\s*\?/i);
    if (!whereMatch) return;

    const whereColumn = whereMatch[1];
    const whereValue = params[0];

    const table = tables.get(tableName)!;
    const index = table.findIndex(r => r[whereColumn] === whereValue);
    
    if (index !== -1) {
      // Handle cascade deletes for collections
      if (tableName === 'collections') {
        const collectionId = table[index].id;
        // Delete all requests in this collection
        if (tables.has('requests')) {
          const requestsTable = tables.get('requests')!;
          const requestsToDelete = requestsTable.filter(r => r.collection_id === collectionId);
          requestsToDelete.forEach(req => {
            const reqIndex = requestsTable.indexOf(req);
            if (reqIndex !== -1) {
              requestsTable.splice(reqIndex, 1);
            }
          });
        }
      }
      
      table.splice(index, 1);
    }
  };

  // Helper function to execute SQL SELECT
  const executeSelect = (sql: string, params: any[]): any[] => {
    const tableMatch = sql.match(/FROM\s+(\w+)/i);
    if (!tableMatch) return [];

    const tableName = tableMatch[1];
    if (!tables.has(tableName)) return [];

    let results = [...tables.get(tableName)!];

    // Handle WHERE clause
    const whereMatch = sql.match(/WHERE\s+(.+?)(?:\s+ORDER\s+BY|\s+LIMIT|$)/i);
    if (whereMatch) {
      const whereClause = whereMatch[1].trim();
      
      // Handle column = ? AND column2 IS NULL
      const eqAndNullMatch = whereClause.match(/^(\w+)\s*=\s*\?\s+AND\s+(\w+)\s+IS\s+NULL$/i);
      if (eqAndNullMatch && params.length >= 1) {
        const column1 = eqAndNullMatch[1];
        const column2 = eqAndNullMatch[2];
        results = results.filter(r => 
          r[column1] === params[0] && 
          (r[column2] === null || r[column2] === undefined)
        );
      }
      // Handle two parameters: column = ? AND column2 = ?
      else if (whereClause.match(/^(\w+)\s*=\s*\?\s+AND\s+(\w+)\s*=\s*\?$/i)) {
        const doubleEqMatch = whereClause.match(/^(\w+)\s*=\s*\?\s+AND\s+(\w+)\s*=\s*\?$/i);
        if (doubleEqMatch && params.length >= 2) {
          const column1 = doubleEqMatch[1];
          const column2 = doubleEqMatch[2];
          results = results.filter(r => r[column1] === params[0] && r[column2] === params[1]);
        }
      }
      // Handle simple equality: column = ?
      else if (whereClause.match(/^(\w+)\s*=\s*\?$/)) {
        const simpleEqMatch = whereClause.match(/^(\w+)\s*=\s*\?$/);
        if (simpleEqMatch && params.length > 0) {
          const column = simpleEqMatch[1];
          results = results.filter(r => r[column] === params[0]);
        }
      }
      // Handle integer equality: column = 1
      else if (whereClause.match(/^(\w+)\s*=\s*(\d+)$/)) {
        const intEqMatch = whereClause.match(/^(\w+)\s*=\s*(\d+)$/);
        if (intEqMatch) {
          const column = intEqMatch[1];
          const value = parseInt(intEqMatch[2]);
          results = results.filter(r => r[column] === value);
        }
      }
      // Handle IS NULL: column IS NULL
      else if (whereClause.match(/^(\w+)\s+IS\s+NULL$/i)) {
        const isNullMatch = whereClause.match(/^(\w+)\s+IS\s+NULL$/i);
        if (isNullMatch) {
          const column = isNullMatch[1];
          results = results.filter(r => r[column] === null || r[column] === undefined);
        }
      }
    }

    // Handle ORDER BY
    const orderMatch = sql.match(/ORDER\s+BY\s+(\w+)(?:\s+(ASC|DESC))?/i);
    if (orderMatch) {
      const column = orderMatch[1];
      const direction = orderMatch[2]?.toUpperCase() || 'ASC';
      results.sort((a, b) => {
        const aVal = a[column];
        const bVal = b[column];
        if (aVal < bVal) return direction === 'ASC' ? -1 : 1;
        if (aVal > bVal) return direction === 'ASC' ? 1 : -1;
        return 0;
      });
    }

    // Handle LIMIT
    const limitMatch = sql.match(/LIMIT\s+(\d+)/i);
    if (limitMatch) {
      const limit = parseInt(limitMatch[1]);
      results = results.slice(0, limit);
    }

    return results;
  };

  // Create statement mock factory
  const createStatement = (sql: string): MockStatement => {
    return {
      run: (...params: any[]) => {
        const trimmedSql = sql.trim();
        if (trimmedSql.match(/^INSERT/i)) {
          executeInsert(trimmedSql, params);
        } else if (trimmedSql.match(/^UPDATE/i)) {
          executeUpdate(trimmedSql, params);
        } else if (trimmedSql.match(/^DELETE/i)) {
          executeDelete(trimmedSql, params);
        }
        return { changes: 1, lastInsertRowid: 1 };
      },
      
      get: (...params: any[]) => {
        const results = executeSelect(sql.trim(), params);
        const result = results[0] || undefined;
        return result;
      },
      
      all: (...params: any[]) => {
        return executeSelect(sql.trim(), params);
      },
    };
  };

  // Create database mock
  const db: MockDatabase = {
    prepare: ((sql: string) => createStatement(sql)) as any,
    
    exec: jest.fn((sql: string) => {
      // Handle CREATE TABLE
      if (sql.match(/CREATE TABLE/i)) {
        const tableMatch = sql.match(/CREATE TABLE(?:\s+IF NOT EXISTS)?\s+(\w+)/i);
        if (tableMatch) {
          const tableName = tableMatch[1];
          if (!tables.has(tableName)) {
            tables.set(tableName, []);
          }
        }
      }
      // Handle CREATE INDEX (no-op for mock)
      // Handle multi-statement exec
      const statements = sql.split(';').filter(s => s.trim());
      statements.forEach(stmt => {
        if (stmt.match(/CREATE TABLE/i)) {
          const tableMatch = stmt.match(/CREATE TABLE(?:\s+IF NOT EXISTS)?\s+(\w+)/i);
          if (tableMatch) {
            const tableName = tableMatch[1];
            if (!tables.has(tableName)) {
              tables.set(tableName, []);
            }
          }
        }
      });
    }),
    
    pragma: jest.fn(() => {}),
    
    close: jest.fn(() => {
      tables.clear();
    }),
    
    _tables: tables,
  };

  return db;
}

/**
 * Mock better-sqlite3 constructor
 */
export class MockBetterSqlite3 {
  static instances: MockDatabase[] = [];
  
  constructor(path: string, options?: any) {
    const db = createMockDatabase();
    MockBetterSqlite3.instances.push(db);
    return db as any;
  }
  
  static clearInstances(): void {
    MockBetterSqlite3.instances = [];
  }
}

/**
 * Factory function to create mock better-sqlite3 module
 */
export function createBetterSqlite3Mock() {
  return MockBetterSqlite3;
}
