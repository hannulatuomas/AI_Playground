import { Router } from 'express';
import { getDbConnection } from './dbConnectionUtil';

const router = Router();

// In-memory storage for connections (replace with DB or secure store in prod)
import fs from 'fs';


import crypto from 'crypto';
import { DBConnection } from './types';
import { connections } from './connectionsStore';

// Test and add a new connection
router.post('/test', async (req, res) => {
  const params = req.body;
  try {
    // Use the utility for all supported types
    const type = params.type;
    if (type === 'sqlite') {
      if (!params.file) return res.json({ success: false, error: 'No file specified' });
      if (!fs.existsSync(params.file)) return res.json({ success: false, error: 'File not found' });
      return res.json({ success: true });
    }
    // All DBs except SQLite
    let dbConn: unknown;
    try {
      dbConn = await getDbConnection(params);
      // For drivers that require connect/close
      if (type === 'postgres') {
        const { Client: PGClient } = require('pg');
        const client = dbConn as InstanceType<typeof PGClient>;
        await client.connect();
        if (params.searchPath) await client.query(`SET search_path TO ${params.searchPath}`);
        await client.end();
      } else if (type === 'mysql') {
        const mysql = require('mysql2/promise');
        const conn = dbConn as InstanceType<typeof mysql.Connection>;
        await conn.connect?.();
        await conn.end();
      } else if (type === 'sqlserver') {
        const mssql = require('mssql');
        const pool = dbConn as InstanceType<typeof mssql.ConnectionPool>;
        await pool.close();
      } else if (type === 'oracle') {
        const oracledb = require('oracledb');
        const conn = dbConn as InstanceType<typeof oracledb.Connection>;
        await conn.close();
      } else if (type === 'mongodb') {
        const { MongoClient } = require('mongodb');
        const client = dbConn as InstanceType<typeof MongoClient>;
        await client.connect();
        await client.close();
      } else if (type === 'neo4j') {
        const neo4j = require('neo4j-driver');
        const driver = dbConn as InstanceType<typeof neo4j.Driver>;
        await driver.verifyConnectivity();
        await driver.close();
      } else {
        return res.json({ success: false, error: 'Unsupported connection type' });
      }
      return res.json({ success: true });
    } catch (err: any) {
      return res.json({ success: false, error: err.message });
    }
  } catch (err: any) {
    res.json({ success: false, error: err.message });
  }
});

// Add a new connection
router.post('/', async (req, res) => {
  const params = req.body;
  let testResult = { success: false, error: '' };
  try {
    const type = params.type;
    if (type === 'sqlite') {
      if (!params.file) {
        testResult.error = 'No file specified';
      } else if (!fs.existsSync(params.file)) {
        testResult.error = 'File not found';
      } else {
        testResult.success = true;
      }
    } else {
      let dbConn: unknown;
      try {
        dbConn = await getDbConnection(params);
        if (type === 'postgres') {
          const { Client: PGClient } = require('pg');
          const client = dbConn as InstanceType<typeof PGClient>;
          await client.connect();
          if (params.searchPath) await client.query(`SET search_path TO ${params.searchPath}`);
          await client.end();
        } else if (type === 'mysql') {
          const mysql = require('mysql2/promise');
          const conn = dbConn as InstanceType<typeof mysql.Connection>;
          await conn.connect?.();
          await conn.end();
        } else if (type === 'sqlserver') {
          const mssql = require('mssql');
          const pool = dbConn as InstanceType<typeof mssql.ConnectionPool>;
          await pool.close();
        } else if (type === 'oracle') {
          const oracledb = require('oracledb');
          const conn = dbConn as InstanceType<typeof oracledb.Connection>;
          await conn.close();
        } else if (type === 'mongodb') {
          const { MongoClient } = require('mongodb');
          const client = dbConn as InstanceType<typeof MongoClient>;
          await client.connect();
          await client.close();
        } else if (type === 'neo4j') {
          const neo4j = require('neo4j-driver');
          const driver = dbConn as InstanceType<typeof neo4j.Driver>;
          await driver.verifyConnectivity();
          await driver.close();
        } else {
          testResult.error = 'Unsupported database type';
        }
        if (!testResult.error) testResult.success = true;
      } catch (err: any) {
        testResult.error = err.message;
      }
    }
  } catch (err: any) {
    testResult.error = err.message;
  }
  if (testResult.success) {
    const crypto = await import('crypto');
    const uid = crypto.randomBytes(12).toString('hex');
    connections.push({
      uid,
      ...params
    });
    res.json({ success: true });
  } else {
    res.status(400).json({ success: false, error: testResult.error });
  }
});

// List connections
router.get('/', (req, res) => {
  res.json(connections.map((c) => ({ ...c, password: undefined })));
});

export default router;
