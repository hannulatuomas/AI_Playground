// Centralized DB connection/config utility for all supported types
// Returns connection/config objects for each DB type for use in query/schema modules

import { Client as PGClient } from 'pg';
import sqlite3 from 'sqlite3';
const mysql = require('mysql2/promise');
const mssql = require('mssql');
const oracledb = require('oracledb');

import { DBConnection } from './types';

export type DBConnectionParams = {
  type: string;
  host?: string;
  port?: number;
  user?: string;
  password?: string;
  database?: string;
  file?: string;
  ssl?: boolean | string;
  applicationName?: string;
  connectTimeout?: number;
  options?: string | object;
  searchPath?: string;
  charset?: string;
  encrypt?: boolean | string;
  trustServerCertificate?: boolean | string;
  mongoUri?: string;
  replicaSet?: string;
  neo4jUri?: string;
  neo4jUser?: string;
  neo4jPassword?: string;
  neo4jDatabase?: string;
};

// Utility to get DB config/connection for each type
export async function getDbConnection(params: DBConnectionParams): Promise<any> {
  const {
    type, host, port, user, password, database, file, ssl, applicationName, connectTimeout, options, searchPath, charset, encrypt, trustServerCertificate,
    mongoUri, replicaSet, neo4jUri, neo4jUser, neo4jPassword, neo4jDatabase
  } = params;

  switch (type) {
    case 'postgres': {
      const pgConfig: any = { host, port, user, password, database };
      if (ssl === 'true') pgConfig.ssl = true;
      if (applicationName) pgConfig.application_name = applicationName;
      if (connectTimeout) pgConfig.connectionTimeoutMillis = Number(connectTimeout);
      if (options) {
        try { Object.assign(pgConfig, typeof options === 'string' ? JSON.parse(options) : options); } catch {}
      }
      return new PGClient(pgConfig);
    }
    case 'sqlite': {
      if (!file) throw new Error('No SQLite file specified');
      return new sqlite3.Database(file);
    }
    case 'mysql': {
      const mysqlConfig: any = { host, port, user, password, database };
      if (charset) mysqlConfig.charset = charset;
      if (ssl === 'true') mysqlConfig.ssl = true;
      if (connectTimeout) mysqlConfig.connectTimeout = Number(connectTimeout);
      if (options) {
        try { Object.assign(mysqlConfig, typeof options === 'string' ? JSON.parse(options) : options); } catch {}
      }
      return mysql.createConnection(mysqlConfig);
    }
    case 'sqlserver': {
      const mssqlConfig: any = {
        user, password, server: host, port, database,
        options: {
          trustServerCertificate: trustServerCertificate === 'false' ? false : true,
          encrypt: encrypt === 'true',
          enableArithAbort: true
        }
      };
      if (ssl === 'true') mssqlConfig.options.encrypt = true;
      if (connectTimeout) mssqlConfig.connectionTimeout = Number(connectTimeout);
      if (applicationName) mssqlConfig.options.appName = applicationName;
      if (options) {
        try { Object.assign(mssqlConfig.options, typeof options === 'string' ? JSON.parse(options) : options); } catch {}
      }
      return mssql.connect(mssqlConfig);
    }
    case 'oracle': {
      const oracleConfig: any = { user, password, connectString: `${host}:${port}/${database}` };
      if (connectTimeout) oracleConfig.connectTimeout = Number(connectTimeout);
      if (options) {
        try { Object.assign(oracleConfig, typeof options === 'string' ? JSON.parse(options) : options); } catch {}
      }
      return oracledb.getConnection(oracleConfig);
    }
    case 'mongodb': {
      let uri = mongoUri;
      if (!uri && host && port) {
        uri = `mongodb://${user && password ? `${encodeURIComponent(user)}:${encodeURIComponent(password)}@` : ''}${host}:${port}${database ? '/' + database : ''}`;
      }
      let mongoOptions: any = { serverSelectionTimeoutMS: 3000 };
      if (replicaSet) mongoOptions.replicaSet = replicaSet;
      if (ssl === 'true') mongoOptions.ssl = true;
      if (connectTimeout) mongoOptions.connectTimeoutMS = Number(connectTimeout);
      if (options) {
        try { Object.assign(mongoOptions, typeof options === 'string' ? JSON.parse(options) : options); } catch {}
      }
      if (!uri) throw new Error('Missing MongoDB connection URI or host/port');
      const { MongoClient } = require('mongodb');
      return new MongoClient(uri, mongoOptions);
    }
    case 'neo4j': {
      let uri = neo4jUri;
      if (!uri && host && port) {
        uri = `bolt://${host}:${port}`;
      }
      if (!uri || !neo4jUser || !neo4jPassword) throw new Error('Missing Neo4j URI/host/port or credentials');
      const neo4j = require('neo4j-driver');
      return neo4j.driver(uri, neo4j.auth.basic(neo4jUser, neo4jPassword));
    }
    default:
      throw new Error('Unsupported database type');
  }
}
