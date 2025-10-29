import { Router } from 'express';
import { getDbConnection } from './dbConnectionUtil';
import fs from 'fs';
import path from 'path';
import csvParse from 'csv-parse/sync';

// Import connections from the connections module
import { connections } from './connectionsStore';
import { DbTableSchema, DbColumnSchema, FileSchema, FileColumnSchema, SchemaApiResponse } from './schemaTypes';
import { inferType, mergeTypes } from './utils/typeInference';

const router = Router();

import { DBConnection } from './types';
import { debug } from 'console';

function getPgConfig(conn: DBConnection): any {
  // Convert ssl to boolean or object if needed
  let ssl: boolean | object | undefined = undefined;
  if (typeof conn.ssl === 'string') {
    ssl = conn.ssl === 'true';
  } else if (typeof conn.ssl === 'boolean' || typeof conn.ssl === 'object') {
    ssl = conn.ssl;
  }
  // Remove string from ssl for pg compatibility
  const { ssl: _ssl, ...rest } = conn;
  return { ...rest, ssl };
}


/**
 * Schema API endpoint
 * 
 * Returns the schema of a database or a CSV file.
 * 
 * @param {string} uid - The unique identifier of the database connection.
 * @param {string} fileName - The name of the CSV file.
 * 
 * @returns {object} - The schema of the database or CSV file.
 */
// Endpoint: Get all table names for a database connection
router.post('/tables', async (req, res) => {
  // Accept only 'uid' as the canonical connection identifier
  const uid = req.body.uid;
  let conn: DBConnection | null = null;
  if (uid) {
    conn = connections.find((c: DBConnection) => c.uid === uid) || null;
  }
  // Fallback: If no conn found, use request body fields directly
  // Always prefer explicit params if provided
  const type = conn?.type || req.body.type;
  const host = conn?.host || req.body.host;
  const port = conn?.port || req.body.port;
  const user = conn?.user || req.body.user;
  const password = conn?.password || req.body.password;
  const database = conn?.database || req.body.database;
  const file = conn?.file || req.body.file;
  const mongoUri = conn?.mongoUri || req.body.mongoUri;
  const neo4jUri = conn?.neo4jUri || req.body.neo4jUri;
  const resolvedNeo4jUser = conn?.neo4jUser || req.body.neo4jUser || req.body.user;
  const resolvedNeo4jPassword = conn?.neo4jPassword || req.body.neo4jPassword || req.body.password;
  if (!type) return res.json({ success: false, error: 'Missing connection type', tables: [] });
  try {
    switch (type as string) {
      case 'postgres': {
        const client = await getDbConnection({ type, host, port, user, password, database });
        await client.connect();
        const tablesRes = await client.query(`SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'`);
        await client.end();
        return res.json({ success: true, tables: tablesRes.rows.map((row: any) => row.table_name) });
      }
      case 'sqlite': {
        if (!file) return res.json({ success: false, error: 'Missing SQLite file', tables: [] });
        const db = await getDbConnection({ type, file });
        db.all(`SELECT name FROM sqlite_master WHERE type='table'`, (err: Error | null, rows: { name: string }[]) => {
          if (err) return res.json({ success: false, error: err.message, tables: [] });
          db.close();
          return res.json({ success: true, tables: rows.map((row) => row.name) });
        });
        return;
      }
      case 'mysql': {
        const connection = await getDbConnection({ type, host, port, user, password, database });
        const [tablesRes] = await connection.query(`SHOW TABLES`);
        await connection.end();
        return res.json({ success: true, tables: tablesRes.map((row: any) => String(Object.values(row)[0])) });
      }
      case 'sqlserver': {
        const pool = await getDbConnection({ type, host, port, user, password, database });
        const tablesRes = await pool.request().query(`SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'`);
        await pool.close();
        return res.json({ success: true, tables: tablesRes.recordset.map((row: any) => row.TABLE_NAME) });
      }
      case 'oracle': {
        const connection = await getDbConnection({ type, host, port, user, password, database });
        const tablesRes = await connection.execute(`SELECT table_name FROM user_tables`);
        await connection.close();
        return res.json({ success: true, tables: tablesRes.rows.map((row: any) => row[0]) });
      }
      case 'mongodb': {
        const client = await getDbConnection({ type, host, port, user, password, database, mongoUri });
        await client.connect();
        const db = client.db(database);
        const collections = await db.listCollections().toArray();
        await client.close();
        return res.json({ success: true, tables: collections.map((col: any) => col.name) });
      }
      case 'neo4j': {
        if (!neo4jUri && !(host && port)) return res.json({ success: false, error: 'Missing Neo4j URI/host/port or credentials', tables: [] });
        if (!resolvedNeo4jUser || !resolvedNeo4jPassword) return res.json({ success: false, error: 'Missing Neo4j credentials', tables: [] });
        const driver = await getDbConnection({ type, host, port, neo4jUri, neo4jUser: resolvedNeo4jUser, neo4jPassword: resolvedNeo4jPassword });
        const session = driver.session();
        // List node labels as "tables"
        const labelRes = await session.run('CALL db.labels()');
        await session.close();
        await driver.close();
        return res.json({ success: true, tables: labelRes.records.map((rec: any) => rec.get(0)) });
      }
      default:
        return res.json({ success: false, error: 'Unsupported DB type', tables: [] });
    }
  } catch (err: any) {
    return res.json({ success: false, error: err.message, tables: [] });
  }
});

// Endpoint: Get all columns for a table in a database connection
router.post('/columns', async (req, res) => {
  // Accept only 'uid' as the canonical connection identifier
  const uid = req.body.uid;
  let conn: DBConnection | null = null;
  if (uid) {
    conn = connections.find((c: DBConnection) => c.uid === uid) || null;
  }
  const type = conn?.type || req.body.type;
  const host = conn?.host || req.body.host;
  const port = conn?.port || req.body.port;
  const user = conn?.user || req.body.user;
  const password = conn?.password || req.body.password;
  const database = conn?.database || req.body.database;
  const file = conn?.file || req.body.file;
  const mongoUri = conn?.mongoUri || req.body.mongoUri;
  const neo4jUri = conn?.neo4jUri || req.body.neo4jUri;
  const resolvedNeo4jUser = conn?.neo4jUser || req.body.neo4jUser || user;
  const resolvedNeo4jPassword = conn?.neo4jPassword || req.body.neo4jPassword || password;
  const table = req.body.table;
  if (!type || !table) return res.json({ success: false, error: 'Missing connection type or table', columns: [] });
  try {
    switch (type as string) {
      case 'postgres': {
        const client = await getDbConnection({ type, host, port, user, password, database });
        await client.connect();
        const colsRes = await client.query(`SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name=$1`, [table]);
        await client.end();
        return res.json({ success: true, columns: colsRes.rows.map((r: any) => ({ name: r.column_name, type: r.data_type, nullable: r.is_nullable === 'YES' })) });
      }
      case 'sqlite': {
        if (!file) return res.json({ success: false, error: 'Missing SQLite file', columns: [] });
        const db = await getDbConnection({ type, file });
        db.all(`PRAGMA table_info(${table})`, (err: Error | null, cols: { name: string; type: string; notnull: number }[]) => {
          if (err) return res.json({ success: false, error: err.message, columns: [] });
          db.close();
          return res.json({ success: true, columns: cols.map((c) => ({ name: c.name, type: c.type, nullable: c.notnull === 0 })) });
        });
        return;
      }
      case 'mysql': {
        const connection = await getDbConnection({ type, host, port, user, password, database });
        const [colsRes] = await connection.query(`SHOW COLUMNS FROM ${table}`);
        await connection.end();
        return res.json({ success: true, columns: colsRes.map((c: any) => ({ name: c.Field, type: String(c.Type), nullable: c.Null === 'YES' })) });
      }
      case 'sqlserver': {
        const pool = await getDbConnection({ type, host, port, user, password, database });
        const colsRes = await pool.request().query(`SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '${table}'`);
        await pool.close();
        return res.json({ success: true, columns: colsRes.recordset.map((c: any) => ({ name: c.COLUMN_NAME, type: c.DATA_TYPE, nullable: c.IS_NULLABLE === 'YES' })) });
      }
      case 'oracle': {
        const connection = await getDbConnection({ type, host, port, user, password, database });
        const colsRes = await connection.execute(`SELECT column_name, data_type, nullable FROM user_tab_columns WHERE table_name = :table`, [table]);
        await connection.close();
        return res.json({ success: true, columns: colsRes.rows.map((c: any) => ({ name: c[0], type: c[1], nullable: c[2] === 'Y' })) });
      }
      case 'mongodb': {
        const dbConn = await getDbConnection({ type, host, port, user, password, database, mongoUri });
        await dbConn.connect();
        const db = dbConn.db(database);
        const samples = await db.collection(table).find({}).limit(20).toArray();
        await dbConn.close();
        if (!samples.length) return res.json({ success: true, columns: [] });
        const fieldStats: Record<string, { types: Set<string>, count: number }> = {};
        samples.forEach((doc: Record<string, unknown>) => {
          Object.keys(doc).forEach((key: string) => {
            if (!fieldStats[key]) fieldStats[key] = { types: new Set<string>(), count: 0 };
            fieldStats[key].types.add(inferType(doc[key]));
            fieldStats[key].count++;
          });
        });
        const columns = Object.entries(fieldStats).map(([name, stat]) => ({
          name,
          type: mergeTypes(Array.from(stat.types)),
          nullable: stat.count < samples.length
        }));
        return res.json({ success: true, columns });
      }
      case 'neo4j': {
        const dbConn = await getDbConnection({ type, host, port, user: resolvedNeo4jUser, password: resolvedNeo4jPassword, neo4jUri });
        const session = dbConn.session();
        const propRes = await session.run(`MATCH (n:${table}) RETURN n LIMIT 20`);
        const fieldStats: Record<string, { types: Set<string>, count: number }> = {};
        propRes.records.forEach((rec: any) => {
          const props: Record<string, unknown> = rec.get('n').properties;
          Object.keys(props).forEach((key: string) => {
            if (!fieldStats[key]) fieldStats[key] = { types: new Set<string>(), count: 0 };
            fieldStats[key].types.add(inferType(props[key]));
            fieldStats[key].count++;
          });
        });
        await session.close();
        await dbConn.close();
        const columns = Object.entries(fieldStats).map(([name, stat]) => ({
          name,
          type: mergeTypes(Array.from(stat.types)),
          nullable: stat.count < propRes.records.length
        }));
        return res.json({ success: true, columns });
      }

      default:
        return res.json({ success: false, error: 'Unsupported DB type', columns: [] });
    }
  } catch (err: any) {
    return res.json({ success: false, error: err.message, columns: [] });
  }
});

// File schema endpoint for CSV/XML only
router.post('/', async (req, res) => {
  const { fileName } = req.body;
  if (!fileName) return res.json({ type: 'file', success: false, error: 'No file specified', files: [] });
  try {
    const uploadsDir = path.join(__dirname, '../uploads');
  } catch (err: any) {
    return res.json({ type: 'file', success: false, error: err.message, files: [] });
  }
});

// Endpoint: Get all properties for a relationship in a Neo4j connection
router.post('/relationships', async (req, res) => {
  const { uid, relationship } = req.body;
  if (!uid || !relationship) return res.json({ success: false, error: 'Missing uid or relationship', properties: [] });
  const conn = connections.find((c: DBConnection) => c.uid === uid);
  if (!conn) return res.json({ success: false, error: 'Invalid connection UID', properties: [] });
  if (conn.type !== 'neo4j') return res.json({ success: false, error: 'Not a Neo4j connection type', properties: [] });
  try {
    const neo4j = require('neo4j-driver');
    let uri = conn.neo4jUri;
    const neo4jUser = conn.neo4jUser || conn.user;
    const neo4jPassword = conn.neo4jPassword || conn.password;
    if (!uri && conn.host && conn.port) uri = `bolt://${conn.host}:${conn.port}`;
    if (!uri || !neo4jUser || !neo4jPassword) {
      return res.json({ success: false, error: 'Missing Neo4j URI/host/port or credentials', properties: [] });
    }
    const driver = neo4j.driver(uri, neo4j.auth.basic(neo4jUser, neo4jPassword));
    const session = driver.session();
    // Scan up to 20 relationships of the given type
    const relRes = await session.run(`MATCH ()-[r:${relationship}]->() RETURN r LIMIT 20`);
    const fieldStats: Record<string, { types: Set<string>, count: number }> = {};
    relRes.records.forEach((rec: any) => {
      const props: Record<string, unknown> = rec.get('r').properties;
      Object.keys(props).forEach((key: string) => {
        if (!fieldStats[key]) fieldStats[key] = { types: new Set<string>(), count: 0 };
        fieldStats[key].types.add(inferType(props[key]));
        fieldStats[key].count++;
      });
    });
    await session.close();
    await driver.close();
    const properties = Object.entries(fieldStats).map(([name, stat]) => ({
      name,
      type: mergeTypes(Array.from(stat.types)),
      nullable: stat.count < relRes.records.length
    }));
    return res.json({ success: true, properties });
  } catch (err: any) {
    return res.json({ success: false, error: err.message, properties: [] });
  }
});

export default router;
