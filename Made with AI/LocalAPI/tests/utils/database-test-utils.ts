/**
 * Database Testing Utilities
 * Provides helpers for setting up database mocks in tests
 */

import { DatabaseService, IDatabaseDriver } from '../../src/main/services/DatabaseService';
import { createMockDatabase, MockDatabase } from '../mocks/better-sqlite3.mock';

/**
 * Creates a DatabaseService instance with a mock database for testing
 * @returns Object containing the DatabaseService and the mock database
 */
export function createTestDatabase(): { db: DatabaseService; mockDb: MockDatabase } {
  const mockDb = createMockDatabase();
  const db = new DatabaseService(':memory:', mockDb as unknown as IDatabaseDriver);
  db.initialize();
  
  return { db, mockDb };
}

/**
 * Creates a DatabaseService instance with a mock database but doesn't initialize it
 * Useful for testing initialization logic
 * @returns Object containing the DatabaseService and the mock database
 */
export function createUninitializedTestDatabase(): { db: DatabaseService; mockDb: MockDatabase } {
  const mockDb = createMockDatabase();
  const db = new DatabaseService(':memory:', mockDb as unknown as IDatabaseDriver);
  
  return { db, mockDb };
}

/**
 * Clears all data from a mock database
 * @param mockDb The mock database to clear
 */
export function clearMockDatabase(mockDb: MockDatabase): void {
  mockDb._tables.clear();
}

/**
 * Gets the raw data from a table in the mock database
 * Useful for debugging tests
 * @param mockDb The mock database
 * @param tableName The name of the table
 * @returns Array of rows in the table
 */
export function getTableData(mockDb: MockDatabase, tableName: string): any[] {
  return mockDb._tables.get(tableName) || [];
}

/**
 * Prints the contents of all tables in the mock database
 * Useful for debugging tests
 * @param mockDb The mock database
 */
export function debugPrintDatabase(mockDb: MockDatabase): void {
  console.log('=== Mock Database Contents ===');
  mockDb._tables.forEach((rows, tableName) => {
    console.log(`\nTable: ${tableName} (${rows.length} rows)`);
    rows.forEach((row, index) => {
      console.log(`  Row ${index}:`, row);
    });
  });
  console.log('==============================\n');
}
