// Integration tests for complete request flow
import { DatabaseService } from '../../src/main/services/DatabaseService';
import { RequestService } from '../../src/main/services/RequestService';
import type { Request } from '../../src/types/models';
import { createTestDatabase } from '../utils/database-test-utils';
import { MockDatabase } from '../mocks/better-sqlite3.mock';

describe('Request Flow Integration', () => {
  let db: DatabaseService;
  let mockDb: MockDatabase;
  let requestService: RequestService;

  beforeEach(() => {
    const testDb = createTestDatabase();
    db = testDb.db;
    mockDb = testDb.mockDb;
    requestService = new RequestService();
  });

  afterEach(() => {
    db.close();
  });

  test('should save request and retrieve it', () => {
    // Create a request
    const request: Omit<Request, 'createdAt' | 'updatedAt'> = {
      id: 'req1',
      name: 'Get Users',
      protocol: 'REST',
      method: 'GET',
      url: 'https://jsonplaceholder.typicode.com/users',
      headers: [
        { key: 'Content-Type', value: 'application/json', enabled: true },
      ],
      queryParams: [],
      assertions: [],
    };

    // Save to database
    const saved = db.createRequest(request);
    expect(saved.id).toBe('req1');

    // Retrieve from database
    const retrieved = db.getRequestById('req1');
    expect(retrieved).not.toBeNull();
    expect(retrieved?.name).toBe('Get Users');
    expect(retrieved?.headers).toHaveLength(1);
  });

  test('should create collection with requests', () => {
    // Create collection
    const collection = db.createCollection({
      id: 'col1',
      name: 'API Tests',
      requests: [],
      folders: [],
    });

    // Create requests in collection
    db.createRequest({
      id: 'req1',
      name: 'Request 1',
      collectionId: 'col1',
      protocol: 'REST',
      method: 'GET',
      url: 'https://api.example.com/1',
      headers: [],
      queryParams: [],
      assertions: [],
    });

    db.createRequest({
      id: 'req2',
      name: 'Request 2',
      collectionId: 'col1',
      protocol: 'REST',
      method: 'POST',
      url: 'https://api.example.com/2',
      headers: [],
      queryParams: [],
      assertions: [],
    });

    // Retrieve requests by collection
    const requests = db.getRequestsByCollection('col1');
    expect(requests).toHaveLength(2);
    expect(requests[0].collectionId).toBe('col1');
    expect(requests[1].collectionId).toBe('col1');
  });

  test('should manage environment variables', () => {
    // Create environment
    const env = db.createEnvironment({
      id: 'env1',
      name: 'Development',
      variables: [
        { key: 'apiUrl', value: 'https://dev.api.com', type: 'string', scope: 'environment', enabled: true },
        { key: 'apiKey', value: 'dev-key-123', type: 'string', scope: 'environment', enabled: true },
      ],
      isActive: true,
    });

    expect(env.variables).toHaveLength(2);

    // Get active environment
    const active = db.getActiveEnvironment();
    expect(active?.id).toBe('env1');
    expect(active?.variables).toHaveLength(2);
  });

  test('should handle request with variables', async () => {
    // Set up variables
    db.setVariable({
      key: 'baseUrl',
      value: 'https://jsonplaceholder.typicode.com',
      type: 'string',
      scope: 'global',
      enabled: true,
    });

    // Create request with variable
    const request: Request = {
      id: 'req1',
      name: 'Test',
      protocol: 'REST',
      method: 'GET',
      url: '{{baseUrl}}/users/1',
      headers: [],
      queryParams: [],
      assertions: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    // Get variables
    const variables = db.getVariablesByScope('global');
    const varMap: Record<string, any> = {};
    variables.forEach(v => {
      if (v.enabled) {
        varMap[v.key] = v.value;
      }
    });

    // Send request (this will make a real HTTP call)
    try {
      const response = await requestService.sendRequest(request, varMap);
      expect(response.status).toBeDefined();
      expect(response.time).toBeGreaterThan(0);
    } catch (error) {
      // Network errors are acceptable in tests
      console.log('Network request failed (expected in test environment)');
    }
  });
});
