# Test Mocks

This directory contains comprehensive mocks for external dependencies used in tests.

## better-sqlite3.mock.ts

A comprehensive mock implementation of the better-sqlite3 database library. This mock provides an in-memory database simulation that supports all the database operations used by `DatabaseService`.

### Features

- **In-memory storage**: All data is stored in JavaScript Maps, no file system access
- **SQL parsing**: Parses common SQL operations (INSERT, UPDATE, DELETE, SELECT)
- **Statement mocking**: Fully mocked `prepare()`, `run()`, `get()`, and `all()` methods
- **WHERE clause support**: Handles simple equality and compound conditions
- **ORDER BY and LIMIT**: Supports sorting and limiting results
- **INSERT OR REPLACE**: Handles upsert operations

### Usage

The mock is automatically configured in `tests/setup.ts` and will be used for all tests. You don't need to manually mock better-sqlite3 in individual test files.

#### Using the Mock in Tests

Use the `createTestDatabase()` utility from `tests/utils/database-test-utils.ts`:

```typescript
import { createTestDatabase } from '../utils/database-test-utils';

describe('MyTest', () => {
  let db: DatabaseService;
  let mockDb: MockDatabase;

  beforeEach(() => {
    const testDb = createTestDatabase();
    db = testDb.db;
    mockDb = testDb.mockDb;
  });

  afterEach(() => {
    db.close();
  });

  test('should do something', () => {
    // Your test code here
    // The database is already initialized with tables
  });
});
```

#### Advanced Usage

For debugging or advanced scenarios, you can access the underlying mock database:

```typescript
import { getTableData, debugPrintDatabase } from '../utils/database-test-utils';

test('should verify table contents', () => {
  // Get raw table data
  const rows = getTableData(mockDb, 'collections');
  expect(rows).toHaveLength(1);

  // Print entire database for debugging
  debugPrintDatabase(mockDb);
});
```

### Supported SQL Operations

#### CREATE TABLE
```sql
CREATE TABLE IF NOT EXISTS table_name (...)
```

#### INSERT
```sql
INSERT INTO table_name (col1, col2) VALUES (?, ?)
INSERT OR REPLACE INTO table_name (col1, col2) VALUES (?, ?)
```

#### UPDATE
```sql
UPDATE table_name SET col1 = ?, col2 = ? WHERE id = ?
```

#### DELETE
```sql
DELETE FROM table_name WHERE id = ?
```

#### SELECT
```sql
SELECT * FROM table_name
SELECT * FROM table_name WHERE col = ?
SELECT * FROM table_name WHERE col1 = ? AND col2 = ?
SELECT * FROM table_name WHERE col IS NULL
SELECT * FROM table_name ORDER BY col ASC|DESC
SELECT * FROM table_name LIMIT 10
```

### Limitations

This is a simplified mock and doesn't support:
- Complex JOIN operations
- Subqueries
- Transactions (all operations are immediate)
- Advanced WHERE clauses (OR, IN, LIKE, etc.)
- Aggregate functions (COUNT, SUM, etc.)

These limitations are acceptable for unit and integration testing of DatabaseService, as the service doesn't use these advanced features.

## Adding New Mocks

When adding new mocks to this directory:

1. Create a new `.mock.ts` file
2. Export factory functions for creating mock instances
3. Document the mock's features and limitations in this README
4. If the mock should be global, add it to `tests/setup.ts`
