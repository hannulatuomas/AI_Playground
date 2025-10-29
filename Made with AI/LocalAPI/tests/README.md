# LocalAPI v0.9.0 Test Suite

**12 test files | 323+ test cases | 3,700+ lines**

---

## Structure

```
tests/
├── unit/
│   ├── services/        (5 files, 160+ tests)
│   │   ├── TabManagerService.test.ts
│   │   ├── KeyboardShortcutManager.test.ts
│   │   ├── CommandPaletteService.test.ts
│   │   ├── FavoritesService.test.ts
│   │   └── LayoutService.test.ts
│   └── components/      (4 files, 88+ tests)
│       ├── RecentItems.test.tsx
│       ├── CollapsibleSection.test.tsx
│       ├── BreadcrumbNavigation.test.tsx
│       └── EnhancedTabBar.test.tsx
├── integration/         (3 files, 75+ tests)
│   ├── KeyboardShortcuts.integration.test.tsx
│   ├── TabManagement.integration.test.tsx
│   └── SearchAndNavigation.integration.test.tsx
└── v0.9.0/
    ├── TEST_SUITE_INDEX.md
    └── FEATURE_TEST_COVERAGE.md
```

## Test Structure

```
tests/
├── unit/           # Unit tests for individual components
│   ├── DatabaseService.test.ts
│   ├── RequestService.test.ts
│   ├── collections.test.ts
│   └── variables.test.ts
├── integration/    # Integration tests for workflows
│   └── request-flow.test.ts
└── e2e/           # End-to-end tests (future)
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- collections.test.ts

# Run tests matching pattern
npm test -- --testNamePattern="Create Collection"
```

## Test Files

### Unit Tests

#### DatabaseService.test.ts
- Database initialization
- CRUD operations
- Settings management
- Error handling

#### RequestService.test.ts
- HTTP request sending
- Variable resolution
- Authentication
- Request body handling

#### collections.test.ts 
- Create collections
- Get collections (by ID and all)
- Update collections
- Delete collections
- Collections with requests
- Edge cases (unicode, long names, etc.)

#### variables.test.ts 
- Create variables (global, environment, collection)
- Get variables by scope
- Update variables
- Delete variables
- Variable types (string, number, boolean, secret)
- Variable scoping
- Edge cases (empty values, unicode, special chars)

### Integration Tests

#### request-flow.test.ts
- Complete request/response flow
- Database integration
- Environment variables
- Error scenarios

## Test Coverage

### Collections Tests
- Create operations (5 tests)
- Read operations (3 tests)
- Update operations (4 tests)
- Delete operations (3 tests)
- Request relationships (2 tests)
- Edge cases (4 tests)
- **Total: 21 tests**

### Variables Tests
- Create operations (7 tests)
- Read operations (5 tests)
- Update operations (4 tests)
- Delete operations (3 tests)
- Scoping (4 tests)
- Type handling (4 tests)
- Edge cases (6 tests)
- **Total: 33 tests**

## Writing Tests

### Unit Test Example
```typescript
describe('DatabaseService', () => {
  let db: DatabaseService;

  beforeEach(() => {
    db = new DatabaseService(':memory:');
    db.initialize();
  });

  afterEach(() => {
    db.close();
  });

  test('should create a collection', () => {
    const collection = db.createCollection({
      id: 'col1',
      name: 'Test',
      requests: [],
      folders: [],
    });
    
    expect(collection.id).toBe('col1');
  });
});
```

### Integration Test Example
```typescript
describe('Request Flow', () => {
  test('should save and retrieve request', () => {
    const db = new DatabaseService(':memory:');
    db.initialize();
    
    const request = db.createRequest({...});
    const retrieved = db.getRequestById(request.id);
    
    expect(retrieved).toEqual(request);
    
    db.close();
  });
});
```

## Test Coverage Goals

- **v0.1.0**: Basic smoke tests
- **v0.2.0**: 70%+ coverage
- **v1.0.0**: 90%+ coverage

## Current Coverage

Run `npm run test:coverage` to see current coverage report.

## Mocking

For tests that require external dependencies:

```typescript
jest.mock('axios');
jest.mock('better-sqlite3');
```

## Test Database

Tests use in-memory SQLite database (`:memory:`) to avoid file system operations.

## Continuous Integration

Tests run automatically on:
- Pre-commit hooks (future)
- Pull requests (future)
- CI/CD pipeline (future)

## Troubleshooting

### Tests Fail to Run
- Ensure dependencies installed: `npm install`
- Check Node.js version: `node --version` (18+)

### Database Tests Fail
- better-sqlite3 may need native compilation
- Use `:memory:` database for tests

### Network Tests Fail
- Some tests make real HTTP requests
- Network errors are acceptable in test environment
- Consider mocking axios for offline tests

## Best Practices

1. **Isolation** - Each test should be independent
2. **Cleanup** - Always clean up resources (close DB, etc.)
3. **Descriptive** - Test names should describe what they test
4. **Fast** - Keep tests fast (use mocks for slow operations)
5. **Reliable** - Tests should not be flaky

## Future Enhancements

- [ ] E2E tests with Spectron/Playwright
- [ ] Visual regression tests
- [ ] Performance benchmarks
- [ ] Load testing
- [ ] Security testing
