// SQLite Database Service for LocalAPI
import * as path from 'path';
import * as fs from 'fs';
import { app } from 'electron';
import type {
  Collection,
  Request,
  Environment,
  Variable,
  Settings,
} from '../../types/models';

// Try to import better-sqlite3, fallback to sql.js
let Database: any;
let usingSqlJs = false;

try {
  Database = require('better-sqlite3');
  console.log('Using better-sqlite3');
} catch (err) {
  console.log('better-sqlite3 not available, using sql.js as fallback');
  Database = require('sql.js');
  usingSqlJs = true;
}

export interface IDatabaseDriver {
  prepare(sql: string): any;
  exec(sql: string): void;
  pragma(pragma: string): void;
  close(): void;
}

export class DatabaseService {
  private db: IDatabaseDriver | null = null;
  private dbPath: string;
  private dbInstance?: IDatabaseDriver;

  constructor(dbPath?: string, dbInstance?: IDatabaseDriver) {
    // If a database instance is provided (for testing), use it directly
    if (dbInstance) {
      this.db = dbInstance;
      this.dbInstance = dbInstance;
      this.dbPath = dbPath || ':memory:';
      return;
    }

    const userDataPath = app.getPath('userData');
    const dataDir = path.join(userDataPath, 'data');
    
    // Ensure data directory exists
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }

    this.dbPath = dbPath || path.join(dataDir, 'localapi.db');
  }

  /**
   * Get the database instance (for use by other services like ConsoleService)
   */
  getDatabase(): IDatabaseDriver | null {
    return this.db;
  }

  /**
   * Initialize database connection and create tables
   */
  initialize(): void {
    try {
      // Skip initialization if database instance was provided in constructor
      if (this.dbInstance) {
        this.createTables();
        console.log('Database initialized successfully (using injected instance)');
        return;
      }

      this.db = new Database(this.dbPath);
      if (this.db) {
        this.db.pragma('journal_mode = WAL');
      }
      this.createTables();
      console.log('Database initialized successfully');
    } catch (error) {
      console.error('Failed to initialize database:', error);
      throw error;
    }
  }

  /**
   * Create database tables
   */
  private createTables(): void {
    if (!this.db) throw new Error('Database not initialized');

    // Collections table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS collections (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        parent_id TEXT,
        variables TEXT,
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL,
        FOREIGN KEY (parent_id) REFERENCES collections(id) ON DELETE CASCADE
      )
    `);

    // Requests table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS requests (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        collection_id TEXT,
        protocol TEXT NOT NULL,
        method TEXT NOT NULL,
        url TEXT NOT NULL,
        headers TEXT,
        query_params TEXT,
        body TEXT,
        auth TEXT,
        pre_request_script TEXT,
        test_script TEXT,
        assertions TEXT,
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL,
        FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
      )
    `);

    // Environments table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS environments (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        variables TEXT NOT NULL,
        is_active INTEGER DEFAULT 0,
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL
      )
    `);

    // Variables table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS variables (
        id TEXT PRIMARY KEY,
        key TEXT NOT NULL,
        value TEXT,
        type TEXT NOT NULL,
        scope TEXT NOT NULL,
        scope_id TEXT,
        enabled INTEGER DEFAULT 1,
        description TEXT,
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL
      )
    `);

    // Settings table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at INTEGER NOT NULL
      )
    `);

    // Create indexes
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_requests_collection ON requests(collection_id);
      CREATE INDEX IF NOT EXISTS idx_collections_parent ON collections(parent_id);
      CREATE INDEX IF NOT EXISTS idx_variables_scope ON variables(scope, scope_id);
      CREATE INDEX IF NOT EXISTS idx_environments_active ON environments(is_active);
    `);
  }

  /**
   * Close database connection
   */
  close(): void {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }

  // ==================== Collections ====================

  /**
   * Get all collections
   */
  getAllCollections(): Collection[] {
    if (!this.db) throw new Error('Database not initialized');

    const stmt = this.db.prepare('SELECT * FROM collections ORDER BY name');
    const rows = stmt.all() as any[];

    return rows.map(row => this.deserializeCollection(row));
  }

  /**
   * Get collection by ID
   */
  getCollectionById(id: string): Collection | null {
    if (!this.db) throw new Error('Database not initialized');

    const stmt = this.db.prepare('SELECT * FROM collections WHERE id = ?');
    const row = stmt.get(id) as any;

    return row ? this.deserializeCollection(row) : null;
  }

  /**
   * Create new collection
   */
  createCollection(collection: Omit<Collection, 'createdAt' | 'updatedAt'>): Collection {
    if (!this.db) throw new Error('Database not initialized');

    const now = Date.now();
    const stmt = this.db.prepare(`
      INSERT INTO collections (id, name, description, parent_id, variables, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      collection.id,
      collection.name,
      collection.description || null,
      collection.parentId || null,
      JSON.stringify(collection.variables || []),
      now,
      now
    );

    return {
      ...collection,
      createdAt: new Date(now),
      updatedAt: new Date(now),
    };
  }

  /**
   * Update collection
   */
  updateCollection(id: string, updates: Partial<Collection>): Collection {
    if (!this.db) throw new Error('Database not initialized');

    const existing = this.getCollectionById(id);
    if (!existing) throw new Error(`Collection ${id} not found`);

    const now = Date.now();
    const stmt = this.db.prepare(`
      UPDATE collections
      SET name = ?, description = ?, parent_id = ?, variables = ?, updated_at = ?
      WHERE id = ?
    `);

    stmt.run(
      updates.name ?? existing.name,
      updates.description ?? existing.description ?? null,
      updates.parentId ?? existing.parentId ?? null,
      JSON.stringify(updates.variables ?? existing.variables ?? []),
      now,
      id
    );

    return this.getCollectionById(id)!;
  }

  /**
   * Delete collection
   */
  deleteCollection(id: string): void {
    if (!this.db) throw new Error('Database not initialized');

    const stmt = this.db.prepare('DELETE FROM collections WHERE id = ?');
    stmt.run(id);
  }

  // ==================== Requests ====================

  /**
   * Get all requests
   */
  getAllRequests(): Request[] {
    if (!this.db) throw new Error('Database not initialized');

    const stmt = this.db.prepare('SELECT * FROM requests ORDER BY name');
    const rows = stmt.all() as any[];

    return rows.map(row => this.deserializeRequest(row));
  }

  /**
   * Get requests by collection ID
   */
  getRequestsByCollection(collectionId: string): Request[] {
    if (!this.db) throw new Error('Database not initialized');

    const stmt = this.db.prepare('SELECT * FROM requests WHERE collection_id = ? ORDER BY name');
    const rows = stmt.all(collectionId) as any[];

    return rows.map(row => this.deserializeRequest(row));
  }

  /**
   * Get request by ID
   */
  getRequestById(id: string): Request | null {
    if (!this.db) throw new Error('Database not initialized');

    const stmt = this.db.prepare('SELECT * FROM requests WHERE id = ?');
    const row = stmt.get(id) as any;

    return row ? this.deserializeRequest(row) : null;
  }

  /**
   * Create new request
   */
  createRequest(request: Omit<Request, 'createdAt' | 'updatedAt'>): Request {
    if (!this.db) throw new Error('Database not initialized');

    const now = Date.now();
    const stmt = this.db.prepare(`
      INSERT INTO requests (
        id, name, description, collection_id, protocol, method, url,
        headers, query_params, body, auth, pre_request_script, test_script,
        assertions, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      request.id,
      request.name,
      request.description || null,
      request.collectionId || null,
      request.protocol,
      request.method,
      request.url,
      JSON.stringify(request.headers),
      JSON.stringify(request.queryParams),
      JSON.stringify(request.body || null),
      JSON.stringify(request.auth || null),
      request.preRequestScript || null,
      request.testScript || null,
      JSON.stringify(request.assertions || []),
      now,
      now
    );

    return {
      ...request,
      createdAt: new Date(now),
      updatedAt: new Date(now),
    };
  }

  /**
   * Update request
   */
  updateRequest(id: string, updates: Partial<Request>): Request {
    if (!this.db) throw new Error('Database not initialized');

    const existing = this.getRequestById(id);
    if (!existing) throw new Error(`Request ${id} not found`);

    const now = Date.now();
    const stmt = this.db.prepare(`
      UPDATE requests
      SET name = ?, description = ?, collection_id = ?, protocol = ?, method = ?,
          url = ?, headers = ?, query_params = ?, body = ?, auth = ?,
          pre_request_script = ?, test_script = ?, assertions = ?, updated_at = ?
      WHERE id = ?
    `);

    stmt.run(
      updates.name ?? existing.name,
      updates.description ?? existing.description ?? null,
      updates.collectionId ?? existing.collectionId ?? null,
      updates.protocol ?? existing.protocol,
      updates.method ?? existing.method,
      updates.url ?? existing.url,
      JSON.stringify(updates.headers ?? existing.headers),
      JSON.stringify(updates.queryParams ?? existing.queryParams),
      JSON.stringify(updates.body ?? existing.body ?? null),
      JSON.stringify(updates.auth ?? existing.auth ?? null),
      updates.preRequestScript ?? existing.preRequestScript ?? null,
      updates.testScript ?? existing.testScript ?? null,
      JSON.stringify(updates.assertions ?? existing.assertions ?? []),
      now,
      id
    );

    return this.getRequestById(id)!;
  }

  /**
   * Delete request
   */
  deleteRequest(id: string): void {
    if (!this.db) throw new Error('Database not initialized');

    const stmt = this.db.prepare('DELETE FROM requests WHERE id = ?');
    stmt.run(id);
  }

  // ==================== Environments ====================

  /**
   * Get all environments
   */
  getAllEnvironments(): Environment[] {
    if (!this.db) throw new Error('Database not initialized');

    const stmt = this.db.prepare('SELECT * FROM environments ORDER BY name');
    const rows = stmt.all() as any[];

    return rows.map(row => this.deserializeEnvironment(row));
  }

  /**
   * Get active environment
   */
  getActiveEnvironment(): Environment | null {
    if (!this.db) throw new Error('Database not initialized');

    const stmt = this.db.prepare('SELECT * FROM environments WHERE is_active = 1 LIMIT 1');
    const row = stmt.get() as any;

    return row ? this.deserializeEnvironment(row) : null;
  }

  /**
   * Create environment
   */
  createEnvironment(environment: Omit<Environment, 'createdAt' | 'updatedAt'>): Environment {
    if (!this.db) throw new Error('Database not initialized');

    const now = Date.now();
    const stmt = this.db.prepare(`
      INSERT INTO environments (id, name, variables, is_active, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      environment.id,
      environment.name,
      JSON.stringify(environment.variables),
      environment.isActive ? 1 : 0,
      now,
      now
    );

    return {
      ...environment,
      createdAt: new Date(now),
      updatedAt: new Date(now),
    };
  }

  /**
   * Update environment
   */
  updateEnvironment(id: string, updates: Partial<Environment>): Environment {
    if (!this.db) throw new Error('Database not initialized');

    const existing = this.getAllEnvironments().find(e => e.id === id);
    if (!existing) throw new Error(`Environment ${id} not found`);

    const now = Date.now();

    // If setting this environment as active, deactivate others
    if (updates.isActive) {
      this.db.prepare('UPDATE environments SET is_active = 0').run();
    }

    const stmt = this.db.prepare(`
      UPDATE environments
      SET name = ?, variables = ?, is_active = ?, updated_at = ?
      WHERE id = ?
    `);

    stmt.run(
      updates.name ?? existing.name,
      JSON.stringify(updates.variables ?? existing.variables),
      updates.isActive !== undefined ? (updates.isActive ? 1 : 0) : (existing.isActive ? 1 : 0),
      now,
      id
    );

    return this.getAllEnvironments().find(e => e.id === id)!;
  }

  /**
   * Delete environment
   */
  deleteEnvironment(id: string): void {
    if (!this.db) throw new Error('Database not initialized');

    const stmt = this.db.prepare('DELETE FROM environments WHERE id = ?');
    stmt.run(id);
  }

  // ==================== Variables ====================

  /**
   * Get variables by scope
   */
  getVariablesByScope(scope: string, scopeId?: string): Variable[] {
    if (!this.db) throw new Error('Database not initialized');

    let stmt;
    let rows;

    if (scopeId) {
      stmt = this.db.prepare('SELECT * FROM variables WHERE scope = ? AND scope_id = ?');
      rows = stmt.all(scope, scopeId) as any[];
    } else {
      stmt = this.db.prepare('SELECT * FROM variables WHERE scope = ? AND scope_id IS NULL');
      rows = stmt.all(scope) as any[];
    }

    return rows.map(row => this.deserializeVariable(row));
  }

  /**
   * Set variable
   */
  setVariable(variable: Omit<Variable, 'key'> & { key: string; scopeId?: string }): Variable {
    if (!this.db) throw new Error('Database not initialized');

    const now = Date.now();
    const id = `${variable.scope}_${variable.scopeId || 'global'}_${variable.key}`;

    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO variables (
        id, key, value, type, scope, scope_id, enabled, description, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      id,
      variable.key,
      JSON.stringify(variable.value),
      variable.type,
      variable.scope,
      (variable as any).scopeId || null,
      variable.enabled ? 1 : 0,
      variable.description || null,
      now,
      now
    );

    const result = this.db.prepare('SELECT * FROM variables WHERE id = ?').get(id) as any;
    return this.deserializeVariable(result);
  }

  /**
   * Delete variable
   */
  deleteVariable(scope: string, key: string, scopeId?: string): void {
    if (!this.db) throw new Error('Database not initialized');

    const id = `${scope}_${scopeId || 'global'}_${key}`;
    const stmt = this.db.prepare('DELETE FROM variables WHERE id = ?');
    stmt.run(id);
  }

  // ==================== Settings ====================

  /**
   * Get all settings
   */
  getAllSettings(): Settings {
    if (!this.db) throw new Error('Database not initialized');

    const stmt = this.db.prepare('SELECT * FROM settings');
    const rows = stmt.all() as any[];

    const settings: any = {};
    rows.forEach(row => {
      settings[row.key] = JSON.parse(row.value);
    });

    return settings as Settings;
  }

  /**
   * Set setting
   */
  setSetting(key: string, value: any): void {
    if (!this.db) throw new Error('Database not initialized');

    const now = Date.now();
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO settings (key, value, updated_at)
      VALUES (?, ?, ?)
    `);

    stmt.run(key, JSON.stringify(value), now);
  }

  // ==================== Helper Methods ====================

  private deserializeCollection(row: any): Collection {
    return {
      id: row.id,
      name: row.name,
      description: row.description,
      parentId: row.parent_id,
      requests: [], // Loaded separately
      folders: [], // Loaded separately
      variables: row.variables ? JSON.parse(row.variables) : [],
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at),
    };
  }

  private deserializeRequest(row: any): Request {
    return {
      id: row.id,
      name: row.name,
      description: row.description,
      collectionId: row.collection_id,
      protocol: row.protocol,
      method: row.method,
      url: row.url,
      headers: JSON.parse(row.headers),
      queryParams: JSON.parse(row.query_params),
      body: row.body ? JSON.parse(row.body) : undefined,
      auth: row.auth ? JSON.parse(row.auth) : undefined,
      preRequestScript: row.pre_request_script,
      testScript: row.test_script,
      assertions: row.assertions ? JSON.parse(row.assertions) : [],
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at),
    };
  }

  private deserializeEnvironment(row: any): Environment {
    return {
      id: row.id,
      name: row.name,
      variables: JSON.parse(row.variables),
      isActive: row.is_active === 1,
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at),
    };
  }

  private deserializeVariable(row: any): Variable {
    return {
      key: row.key,
      value: JSON.parse(row.value),
      type: row.type,
      scope: row.scope,
      enabled: row.enabled === 1,
      description: row.description,
    };
  }
}

// Singleton instance
let dbInstance: DatabaseService | null = null;

export function getDatabaseService(): DatabaseService {
  if (!dbInstance) {
    dbInstance = new DatabaseService();
    dbInstance.initialize();
  }
  return dbInstance;
}
