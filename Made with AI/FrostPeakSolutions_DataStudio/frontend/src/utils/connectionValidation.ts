/**
 * Centralized validation and parsing logic for database connections.
 * Strictly typed, reusable, and ready for future testing and extension.
 *
 * Supported DB types: postgres, mysql, sqlite, sqlserver, oracle, mongodb, neo4j
 *
 * Usage:
 *   - Use validateField for field-level validation in forms
 *   - Use validateForm for form-level validation before submit
 *   - Use parseConnStr to parse connection strings into structured fields
 */

/**
 * Supported database types for connection forms.
 */
export type DBType = 'postgres' | 'mysql' | 'sqlite' | 'sqlserver' | 'oracle' | 'mongodb' | 'neo4j';

/**
 * Connection form structure for all supported DB types.
 * Extend as needed for new DBs or advanced options.
 */
export interface ConnectionForm {
  uid?: string;
  type: DBType;
  displayName: string;
  host?: string;
  server?: string;
  port?: number | string;
  user?: string;
  password?: string;
  database?: string;
  file?: string;
  mongoUri?: string;
  neo4jUri?: string;
  neo4jUser?: string;
  neo4jPassword?: string;
  ssl?: string;
  schema?: string;
  connectTimeout?: string | number;
  applicationName?: string;
  options?: string;
  searchPath?: string;
  charset?: string;
  encrypt?: string;
  trustServerCertificate?: string;
  replicaSet?: string;
  neo4jDatabase?: string;
  [key: string]: any;
}

/**
 * Validates a single field in a connection form.
 * @param name - Field name
 * @param value - Field value
 * @param type - Database type
 * @returns Error message if invalid, otherwise empty string
 */
export function validateField(name: string, value: string | number | undefined, type: DBType): string {
  if (["displayName", "host", "server", "user", "password", "database", "file", "port", "neo4jUser", "neo4jPassword"].includes(name)) {
    if (!value || (typeof value === 'string' && value.trim() === '')) {
      if (name === 'displayName') return 'Required for easy identification.';
      if (name === 'host' || name === 'server') return 'Host/server is required.';
      if (name === 'user' || name === 'neo4jUser') return 'User is required.';
      if (name === 'password' || name === 'neo4jPassword') return 'Password is required.';
      if (name === 'database') return 'Database is required.';
      if (name === 'file') return 'File path is required.';
      if (name === 'port') return 'Port is required.';
    }
  }
  if (name === 'port' && value && (isNaN(Number(value)) || Number(value) <= 0)) {
    return 'Port must be a positive number.';
  }
  if (type === 'mongodb' && name === 'mongoUri' && value && typeof value === 'string') {
    if (!/^mongodb:\/\//.test(value)) return 'MongoDB URI must start with mongodb://';
  }
  if (type === 'neo4j' && name === 'neo4jUri' && value && typeof value === 'string') {
    if (!/^neo4j:\/\//.test(value)) return 'Neo4j URI must start with neo4j://';
  }
  return '';
}

/**
 * Validates a full connection form before submit.
 * @param form - ConnectionForm object
 * @param useConnStr - Whether using connection string mode
 * @param connStr - The connection string (if used)
 * @returns Map of field errors (fieldName -> errorMessage)
 */
export function validateForm(form: ConnectionForm, useConnStr: boolean, connStr: string): Record<string, string> {
  const errors: Record<string, string> = {};
  if (useConnStr) {
    if (!connStr || connStr.trim() === '') errors['connStr'] = 'Connection string is required.';
    else {
      if (form.type === 'mongodb' && !/^mongodb:\/\//.test(connStr)) errors['connStr'] = 'MongoDB URI must start with mongodb://';
      if (form.type === 'neo4j' && !/^neo4j:\/\//.test(connStr)) errors['connStr'] = 'Neo4j URI must start with neo4j://';
    }
    const displayNameError = validateField('displayName', form.displayName, form.type);
    if (displayNameError) errors['displayName'] = displayNameError;
    return errors;
  }
  ['displayName'].forEach(field => {
    const err = validateField(field, (form as any)[field], form.type);
    if (err) errors[field] = err;
  });
  switch (form.type) {
    case 'postgres':
    case 'mysql':
    case 'oracle':
      ['host', 'port', 'user', 'password', 'database'].forEach(field => {
        const err = validateField(field, (form as any)[field], form.type);
        if (err) errors[field] = err;
      });
      break;
    case 'sqlserver':
      ['server', 'port', 'user', 'password', 'database'].forEach(field => {
        const err = validateField(field, (form as any)[field], form.type);
        if (err) errors[field] = err;
      });
      break;
    case 'sqlite':
      ['file'].forEach(field => {
        const err = validateField(field, (form as any)[field], form.type);
        if (err) errors[field] = err;
      });
      break;
    case 'mongodb':
      ['host', 'port', 'user', 'password', 'database'].forEach(field => {
        const err = validateField(field, (form as any)[field], form.type);
        if (err) errors[field] = err;
      });
      break;
    case 'neo4j':
      ['host', 'port', 'neo4jUser', 'neo4jPassword'].forEach(field => {
        const err = validateField(field, (form as any)[field], form.type);
        if (err) errors[field] = err;
      });
      break;
  }
  return errors;
}

/**
 * Parses key-value pairs from a connection string (case-insensitive, supports synonyms).
 * Used for SQL Server, PostgreSQL, MySQL, Oracle key-value style strings.
 * @param s - Input string
 * @param synonyms - Optional mapping of synonyms to canonical field names
 * @returns Parsed object
 */
function parseKeyValue(s: string, synonyms: Record<string, string> = {}): Record<string, any> {
  const out: Record<string, any> = {};
  s.split(';').forEach(pair => {
    const [k, v] = pair.split('=').map(x => x.trim());
    if (!k || !v) return;
    let key = k.toLowerCase();
    if (synonyms[key]) key = synonyms[key];
    out[key] = v;
  });
  return out;
}

/**
 * Parses a connection string and returns a partial ConnectionForm.
 * Handles all supported DB types, including MongoDB and Neo4j URIs.
 * @param type - DB type
 * @param str - Connection string
 * @returns Partial ConnectionForm with parsed fields
 */
export function parseConnStr(type: string, str: string): Partial<ConnectionForm> {
  try {
    // --- SQL Server ---
    if (type === 'sqlserver') {
      // ADO.NET/ODBC
      if (/Data Source=/i.test(str) || /Server=/i.test(str)) {
        const synonyms = {
          'data source': 'host', 'server': 'host',
          'address': 'host', 'addr': 'host', 'network address': 'host',
          'initial catalog': 'database', 'database': 'database',
          'user id': 'user', 'uid': 'user', 'user': 'user',
          'password': 'password', 'pwd': 'password',
          'port': 'port'
        };
        const fields = parseKeyValue(str, synonyms);
        if (fields.host && /[:,]/.test(fields.host)) {
          const [host, port] = fields.host.split(/[:,]/);
          fields.host = host;
          if (port) fields.port = Number(port);
        }
        if (fields.port) fields.port = Number(fields.port);
        return { type: type as DBType, ...fields };
      }
      // URI
      const m = str.match(/^(sqlserver):\/\/(.*?)(:(.*?))?@(.*?)(:(\d+))?\/(.+)$/);
      if (m) {
        const [, proto, user, , password, host, , port, database] = m;
        return { type: proto as any, user, password, host, port: port ? Number(port) : undefined, database };
      }
    }
    // --- PostgreSQL, MySQL, Oracle: key-value ---
    if (["postgres", "postgresql", "mysql", "oracle"].includes(type)) {
      if (/=/.test(str) && !str.startsWith("mongodb://") && !str.startsWith("bolt://") && !str.startsWith("neo4j://")) {
        const synonyms = {
          'host': 'host', 'server': 'host',
          'port': 'port',
          'user': 'user', 'uid': 'user',
          'password': 'password', 'pwd': 'password',
          'database': 'database', 'dbname': 'database', 'schema': 'schema',
          'sid': 'sid', 'service_name': 'serviceName'
        };
        const fields = parseKeyValue(str, synonyms);
        if (fields.port) fields.port = Number(fields.port);
        return { type: type as DBType, ...fields };
      }
    }
    // --- MongoDB: URI ---
    if (type === 'mongodb') {
      try {
        const url = new URL(str);
        const [user, password] = url.username ? [decodeURIComponent(url.username), decodeURIComponent(url.password)] : [undefined, undefined];
        return {
          type: 'mongodb' as DBType,
          mongoUri: str,
          user,
          password,
          host: url.hostname,
          port: url.port ? Number(url.port) : undefined,
          database: url.pathname ? url.pathname.replace(/^\//, '') : undefined
        };
      } catch {}
    }
    // --- Neo4j: URI ---
    if (type === 'neo4j') {
      try {
        const url = new URL(str);
        const [user, password] = url.username ? [decodeURIComponent(url.username), decodeURIComponent(url.password)] : [undefined, undefined];
        return {
          type: 'neo4j' as DBType,
          neo4jUri: str,
          neo4jUser: user,
          neo4jPassword: password,
          host: url.hostname,
          port: url.port ? Number(url.port) : undefined,
        };
      } catch {}
    }
    // --- SQLite ---
    if (type === 'sqlite') {
      return { type: type as DBType, file: str.replace(/^sqlite:/, '').replace(/^\/\/+/, '') };
    }
    // --- Fallback: URI for Postgres/MySQL/Oracle ---
    if (!str.startsWith("mongodb://") && !str.startsWith("neo4j://") && !str.startsWith("bolt://")) {
      const m = str.match(/^(\w+):\/\/(.*?)(:(.*?))?@(.*?)(:(\d+))?\/(.+?)(\?(.*))?$/);
      if (m) {
        const [, proto, user, , password, host, , port, database] = m;
        const protoLower = proto.toLowerCase();
        const formTypeLower = type.toLowerCase();
        const typeMap: Record<string, DBType> = {
          'postgresql': 'postgres',
          'pg': 'postgres',
        };
        const mappedProto = typeMap[protoLower] || protoLower as DBType;
        if (mappedProto === formTypeLower) {
          return {
            type: type as DBType,
            user,
            password,
            host,
            port: port ? Number(port) : undefined,
            database
          };
        }
      }
    }
    return {};
  } catch {
    return {};
  }
}
