export type DBType = 'postgres' | 'sqlite' | 'mongodb' | 'neo4j' | 'json';
export interface DBConnection {
  uid: string;
  type: DBType;
  // Common fields
  host?: string;
  port?: number;
  user?: string;
  password?: string;
  database?: string;
  file?: string;
  ssl?: boolean | string;
  schema?: string;
  connectTimeout?: number | string;
  applicationName?: string;
  options?: any;
  searchPath?: string;
  charset?: string;
  encrypt?: boolean | string;
  trustServerCertificate?: boolean | string;
  // MongoDB specific
  mongoUri?: string;
  replicaSet?: string;
  // Neo4j specific
  neo4jUri?: string;
  neo4jUser?: string;
  neo4jPassword?: string;
  neo4jDatabase?: string;
}
