import { Router } from 'express';
import { getDbConnection } from './dbConnectionUtil';
import fs from 'fs';
import path from 'path';
import csvParse from 'csv-parse/sync';

const router = Router();

import { connections } from './connectionsStore';

router.post('/', async (req, res) => {
  const { uid, type, host, port, user, password, database, file, sql, params } = req.body;
  let conn: any = null;
  if (uid) {
    conn = connections.find((c: any) => c.uid === uid) || null;
  }
  // Prefer conn fields if available, fallback to request body fields
  const resolvedType = conn?.type || type;
  const resolvedHost = conn?.host || host;
  const resolvedPort = conn?.port || port;
  const resolvedUser = conn?.user || user;
  const resolvedPassword = conn?.password || password;
  const resolvedDatabase = conn?.database || database;
  const resolvedFile = conn?.file || file;
  const resolvedMongoUri = conn?.mongoUri || req.body.mongoUri;
  const resolvedNeo4jUri = conn?.neo4jUri || req.body.neo4jUri;
  const resolvedNeo4jUser = conn?.neo4jUser || req.body.neo4jUser || (conn ? conn.user : user);
  const resolvedNeo4jPassword = conn?.neo4jPassword || req.body.neo4jPassword || (conn ? conn.password : password);
  // Only error if neither uid nor connection details are present
  if (!resolvedType) {
    return res.json({ success: false, error: 'No database type specified (resolvedType missing)' });
  }

  // CSV file query support (streaming and paginated)
  if (resolvedType === 'csv' && resolvedFile && sql) {
    try {
      const filePath = path.join(__dirname, '../uploads', file);
      if (!fs.existsSync(filePath)) return res.json({ success: false, error: 'CSV file not found' });
      const limit = Math.max(1, parseInt(req.body.limit) || 100);
      const offset = Math.max(0, parseInt(req.body.offset) || 0);
      const schemaOverride = req.body.schemaOverride;
      const csvParser = require('csv-parser');
      const sqlite3 = require('sqlite3').verbose();
      const db = new sqlite3.Database(':memory:');
      let columns: string[] = [];
      let rowCount = 0;
      let inserted = 0;
      let tableCreated = false;
      let createTablePromise: Promise<void> | null = null;
      let insertPromises: Promise<void>[] = [];
      const tableName = 'csv';

      // If schemaOverride is present, validate and use it
      let schemaCols: { name: string; type: string }[] | null = null;
      if (schemaOverride && Array.isArray(schemaOverride) && schemaOverride.every((c: any) => typeof c.name === 'string' && typeof c.type === 'string')) {
        schemaCols = schemaOverride;
      }

      await new Promise<void>((resolve, reject) => {
        fs.createReadStream(filePath)
          .pipe(csvParser())
          .on('data', (row: any) => {
            rowCount++;
            if (!tableCreated) {
              if (schemaCols) {
                columns = schemaCols.map(c => c.name);
                const colDefs = schemaCols.map(c => `"${c.name.replace(/"/g, '""')}" TEXT`).join(', ');
                createTablePromise = new Promise((res, rej) => db.run(`CREATE TABLE ${tableName} (${colDefs})`, (err: Error | null) => err ? rej(err) : res()));
              } else {
                columns = Object.keys(row);
                const colDefs = columns.map(c => `"${c.replace(/"/g, '""')}" TEXT`).join(', ');
                createTablePromise = new Promise((res, rej) => db.run(`CREATE TABLE ${tableName} (${colDefs})`, (err: Error | null) => err ? rej(err) : res()));
              }
              tableCreated = true;
            }
            // Only insert rows within the requested page
            if (rowCount > offset && inserted < limit) {
              const placeholders = columns.map(() => '?').join(',');
              const insertSQL = `INSERT INTO ${tableName} VALUES (${placeholders})`;
              insertPromises.push(new Promise((res, rej) => {
                db.run(insertSQL, columns.map(c => row[c]), (err: Error | null) => err ? rej(err) : res());
              }));
              inserted++;
            }
          })
          .on('end', async () => {
            try {
              if (createTablePromise) await createTablePromise;
              await Promise.all(insertPromises);
              resolve();
            } catch (err) {
              reject(err);
            }
          })
          .on('error', (err: Error) => reject(err));
      });
      // Query the inserted window
      db.all(sql, params || [], (err: Error | null, rows: any[]) => {
        db.close();
        if (err) return res.json({ success: false, error: err.message });
        res.json({ success: true, rows, total: rowCount });
      });
      return;
    } catch (err: any) {
      return res.json({ success: false, error: err.message });
    }
  }

  // JSON file query support (streaming and paginated)
  if (resolvedType === 'json' && resolvedFile && sql) {
    try {
      const filePath = path.join(__dirname, '../uploads', file);
      if (!fs.existsSync(filePath)) return res.json({ success: false, error: 'JSON file not found' });
      const limit = Math.max(1, parseInt(req.body.limit) || 100);
      const offset = Math.max(0, parseInt(req.body.offset) || 0);
      const schemaOverride = req.body.schemaOverride;
      const sqlite3 = require('sqlite3').verbose();
      const db = new sqlite3.Database(':memory:');
      let columns: string[] = [];
      let rowCount = 0;
      let inserted = 0;
      let tableCreated = false;
      let createTablePromise: Promise<void> | null = null;
      let insertPromises: Promise<void>[] = [];
      const tableName = 'json';

      // Helper to flatten a JSON object (1-level deep)
      function flatten(obj: any, prefix = ''): any {
        const flat: any = {};
        for (const k in obj) {
          if (typeof obj[k] === 'object' && obj[k] !== null && !Array.isArray(obj[k])) {
            for (const subk in obj[k]) {
              flat[`${prefix}${k}.${subk}`] = obj[k][subk];
            }
          } else {
            flat[`${prefix}${k}`] = obj[k];
          }
        }
        return flat;
      }

      // Read and parse JSON file
      const raw = fs.readFileSync(filePath, 'utf8');
      let jsonArr: any[];
      try {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          jsonArr = parsed;
        } else if (typeof parsed === 'object' && parsed !== null) {
          jsonArr = [parsed];
        } else {
          return res.json({ success: false, error: 'JSON root must be object or array' });
        }
      } catch (err) {
        return res.json({ success: false, error: 'Invalid JSON: ' + (err as Error).message });
      }

      // Flatten all rows
      const flatRows = jsonArr.map(obj => flatten(obj));
      rowCount = flatRows.length;

      // If schemaOverride is present, validate and use it
      let schemaCols: { name: string; type: string }[] | null = null;
      if (schemaOverride && Array.isArray(schemaOverride) && schemaOverride.every((c: any) => typeof c.name === 'string' && typeof c.type === 'string')) {
        schemaCols = schemaOverride;
      }

      // Determine columns
      if (schemaCols) {
        columns = schemaCols.map(c => c.name);
      } else {
        // Union of all keys
        const colSet = new Set<string>();
        flatRows.forEach(row => Object.keys(row).forEach(k => colSet.add(k)));
        columns = Array.from(colSet);
      }
      const colDefs = columns.map(c => `"${c.replace(/"/g, '""')}" TEXT`).join(', ');
      await new Promise<void>((resolve, reject) => {
        db.run(`CREATE TABLE ${tableName} (${colDefs})`, (err: Error | null) => err ? reject(err) : resolve());
      });
      // Insert rows
      await new Promise<void>((resolve, reject) => {
        let insertedRows = 0;
        function insertNext(i: number) {
          if (i >= flatRows.length || insertedRows >= limit) return resolve();
          if (i < offset) return insertNext(i + 1);
          const row = flatRows[i];
          const placeholders = columns.map(() => '?').join(',');
          const insertSQL = `INSERT INTO ${tableName} VALUES (${placeholders})`;
          db.run(insertSQL, columns.map(c => row[c] !== undefined ? String(row[c]) : null), (err: Error | null) => {
            if (err) return reject(err);
            insertedRows++;
            insertNext(i + 1);
          });
        }
        insertNext(0);
      });
      // Query the inserted window
      db.all(sql, params || [], (err: Error | null, rows: any[]) => {
        db.close();
        if (err) return res.json({ success: false, error: err.message });
        res.json({ success: true, rows, total: rowCount });
      });
      return;
    } catch (err: any) {
      return res.json({ success: false, error: err.message });
    }
  }

  // Existing logic for PostgreSQL and SQLite DBs
  if (!resolvedType) {
    return res.json({ success: false, error: 'No database type specified (resolvedType missing)' });
  }
  try {
    // --- Unified DB connection logic using getDbConnection ---
    if (['postgres', 'sqlite', 'mysql', 'sqlserver', 'oracle', 'mongodb', 'neo4j'].includes(resolvedType)) {
      try {
        let dbConn: unknown;
        switch (resolvedType) {
          case 'postgres': {
            const { Client: PGClient } = require('pg');
            dbConn = await getDbConnection({ type: resolvedType, host: resolvedHost, port: resolvedPort, user: resolvedUser, password: resolvedPassword, database: resolvedDatabase });
            const client = dbConn as InstanceType<typeof PGClient>;
            await client.connect();
            const { rows } = await client.query(sql, params || []);
            await client.end();
            return res.json({ success: true, rows });
          }
          case 'sqlite': {
            if (!resolvedFile) return res.json({ success: false, error: 'Missing SQLite file' });
            const sqlite3 = require('sqlite3').verbose();
            dbConn = await getDbConnection({ type: resolvedType, file: resolvedFile });
            const db = dbConn as InstanceType<typeof sqlite3.Database>;
            db.all(sql, params || [], (err: Error | null, rows: any[]) => {
              db.close();
              if (err) return res.json({ success: false, error: err.message });
              res.json({ success: true, rows });
            });
            return;
          }
          case 'mysql': {
            const mysql = require('mysql2/promise');
            dbConn = await getDbConnection({ type: resolvedType, host: resolvedHost, port: resolvedPort, user: resolvedUser, password: resolvedPassword, database: resolvedDatabase });
            const conn = dbConn as InstanceType<typeof mysql.Connection>;
            const [rows] = await conn.execute(sql, params || []);
            await conn.end();
            return res.json({ success: true, rows });
          }
          case 'sqlserver': {
            const mssql = require('mssql');
            dbConn = await getDbConnection({ type: resolvedType, host: resolvedHost, port: resolvedPort, user: resolvedUser, password: resolvedPassword, database: resolvedDatabase });
            const pool = dbConn as InstanceType<typeof mssql.ConnectionPool>;
            let request = pool.request();
            if (Array.isArray(params)) {
              params.forEach((val, idx) => {
                request = request.input(`param${idx+1}`, val);
              });
            }
            const result = await request.query(sql);
            await pool.close();
            return res.json({ success: true, rows: result.recordset });
          }
          case 'oracle': {
            const oracledb = require('oracledb');
            dbConn = await getDbConnection({ type: resolvedType, host: resolvedHost, port: resolvedPort, user: resolvedUser, password: resolvedPassword, database: resolvedDatabase });
            const conn = dbConn as InstanceType<typeof oracledb.Connection>;
            const result = await conn.execute(sql, params || [], { outFormat: oracledb.OUT_FORMAT_OBJECT });
            await conn.close();
            return res.json({ success: true, rows: result.rows });
          }
          case 'mongodb': {
            const { MongoClient } = require('mongodb');
            dbConn = await getDbConnection({ type: resolvedType, host: resolvedHost, port: resolvedPort, user: resolvedUser, password: resolvedPassword, database: resolvedDatabase, mongoUri: resolvedMongoUri });
            const client = dbConn as InstanceType<typeof MongoClient>;
            await client.connect();
            const db = client.db(resolvedDatabase);
            const collection = db.collection(req.body.collection);
            let results;
            if (req.body.mongoQueryType === 'aggregate' && Array.isArray(req.body.pipeline)) {
              results = await collection.aggregate(req.body.pipeline).toArray();
            } else {
              results = await collection.find(req.body.query || {}, req.body.options || {}).toArray();
            }
            await client.close();
            return res.json({ success: true, rows: results });
          }
          case 'neo4j': {
            if ((!resolvedNeo4jUri && !(resolvedHost && resolvedPort)) || !resolvedNeo4jUser || !resolvedNeo4jPassword) {
              return res.json({ success: false, error: 'Missing Neo4j URI/host/port or credentials' });
            }
            const neo4j = require('neo4j-driver');
            dbConn = await getDbConnection({ type: resolvedType, host: resolvedHost, port: resolvedPort, neo4jUri: resolvedNeo4jUri, neo4jUser: resolvedNeo4jUser, neo4jPassword: resolvedNeo4jPassword });
            const driver = dbConn as InstanceType<typeof neo4j.Driver>;
            const session = driver.session();
            const cypher = req.body.cypher || sql;
            const cypherParams = req.body.params || {};
            const result = await session.run(cypher, cypherParams);
            await session.close();
            await driver.close();
            const rows = result.records.map((rec: any) => rec.toObject());
            return res.json({ success: true, rows });
          }
        }
      } catch (err: any) {
        return res.json({ success: false, error: err.message });
      }
    }
    res.json({ success: false, error: 'Unsupported connection type' });
  } catch (err: any) {
    res.json({ success: false, error: err.message });
  }
});

export default router;
