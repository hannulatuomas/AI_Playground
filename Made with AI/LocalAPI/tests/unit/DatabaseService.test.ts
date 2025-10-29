// Unit tests for DatabaseService
import { DatabaseService } from '../../src/main/services/DatabaseService';
import type { Collection, Request, Environment, Variable } from '../../src/types/models';
import { createTestDatabase } from '../utils/database-test-utils';
import { MockDatabase } from '../mocks/better-sqlite3.mock';

describe('DatabaseService', () => {
  let db: DatabaseService;
  let mockDb: MockDatabase;

  beforeEach(() => {
    // Use mock database for testing
    const testDb = createTestDatabase();
    db = testDb.db;
    mockDb = testDb.mockDb;
  });

  afterEach(() => {
    db.close();
  });

  describe('Collections', () => {
    test('should create a collection', () => {
      const collection: Omit<Collection, 'createdAt' | 'updatedAt'> = {
        id: 'col1',
        name: 'Test Collection',
        description: 'Test description',
        requests: [],
        folders: [],
        variables: [],
      };

      const created = db.createCollection(collection);
      expect(created.id).toBe('col1');
      expect(created.name).toBe('Test Collection');
      expect(created.createdAt).toBeInstanceOf(Date);
    });

    test('should get all collections', () => {
      db.createCollection({
        id: 'col1',
        name: 'Collection 1',
        requests: [],
        folders: [],
      });
      db.createCollection({
        id: 'col2',
        name: 'Collection 2',
        requests: [],
        folders: [],
      });

      const collections = db.getAllCollections();
      expect(collections).toHaveLength(2);
      expect(collections[0].name).toBe('Collection 1');
    });

    test('should get collection by id', () => {
      db.createCollection({
        id: 'col1',
        name: 'Test Collection',
        requests: [],
        folders: [],
      });

      const collection = db.getCollectionById('col1');
      expect(collection).not.toBeNull();
      expect(collection?.name).toBe('Test Collection');
    });

    test('should update a collection', () => {
      db.createCollection({
        id: 'col1',
        name: 'Original Name',
        requests: [],
        folders: [],
      });

      const updated = db.updateCollection('col1', { name: 'Updated Name' });
      expect(updated.name).toBe('Updated Name');
    });

    test('should delete a collection', () => {
      db.createCollection({
        id: 'col1',
        name: 'Test Collection',
        requests: [],
        folders: [],
      });

      db.deleteCollection('col1');
      const collection = db.getCollectionById('col1');
      expect(collection).toBeNull();
    });
  });

  describe('Requests', () => {
    test('should create a request', () => {
      const request: Omit<Request, 'createdAt' | 'updatedAt'> = {
        id: 'req1',
        name: 'Test Request',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com/users',
        headers: [],
        queryParams: [],
        assertions: [],
      };

      const created = db.createRequest(request);
      expect(created.id).toBe('req1');
      expect(created.method).toBe('GET');
    });

    test('should get all requests', () => {
      db.createRequest({
        id: 'req1',
        name: 'Request 1',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com',
        headers: [],
        queryParams: [],
        assertions: [],
      });

      const requests = db.getAllRequests();
      expect(requests).toHaveLength(1);
    });

    test('should get requests by collection', () => {
      db.createCollection({
        id: 'col1',
        name: 'Collection 1',
        requests: [],
        folders: [],
      });

      db.createRequest({
        id: 'req1',
        name: 'Request 1',
        collectionId: 'col1',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com',
        headers: [],
        queryParams: [],
        assertions: [],
      });

      const requests = db.getRequestsByCollection('col1');
      expect(requests).toHaveLength(1);
      expect(requests[0].collectionId).toBe('col1');
    });

    test('should update a request', () => {
      db.createRequest({
        id: 'req1',
        name: 'Original',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com',
        headers: [],
        queryParams: [],
        assertions: [],
      });

      const updated = db.updateRequest('req1', { name: 'Updated' });
      expect(updated.name).toBe('Updated');
    });

    test('should delete a request', () => {
      db.createRequest({
        id: 'req1',
        name: 'Test',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com',
        headers: [],
        queryParams: [],
        assertions: [],
      });

      db.deleteRequest('req1');
      const request = db.getRequestById('req1');
      expect(request).toBeNull();
    });
  });

  describe('Environments', () => {
    test('should create an environment', () => {
      const env: Omit<Environment, 'createdAt' | 'updatedAt'> = {
        id: 'env1',
        name: 'Development',
        variables: [],
        isActive: false,
      };

      const created = db.createEnvironment(env);
      expect(created.name).toBe('Development');
    });

    test('should get active environment', () => {
      db.createEnvironment({
        id: 'env1',
        name: 'Development',
        variables: [],
        isActive: true,
      });

      const active = db.getActiveEnvironment();
      expect(active).not.toBeNull();
      expect(active?.name).toBe('Development');
    });

    test('should update environment', () => {
      db.createEnvironment({
        id: 'env1',
        name: 'Development',
        variables: [],
        isActive: false,
      });

      const updated = db.updateEnvironment('env1', { isActive: true });
      expect(updated.isActive).toBe(true);
    });

    test('should deactivate other environments when activating one', () => {
      db.createEnvironment({
        id: 'env1',
        name: 'Development',
        variables: [],
        isActive: true,
      });

      db.createEnvironment({
        id: 'env2',
        name: 'Production',
        variables: [],
        isActive: false,
      });

      db.updateEnvironment('env2', { isActive: true });

      const env1 = db.getAllEnvironments().find(e => e.id === 'env1');
      const env2 = db.getAllEnvironments().find(e => e.id === 'env2');

      expect(env1?.isActive).toBe(false);
      expect(env2?.isActive).toBe(true);
    });
  });

  describe('Variables', () => {
    test('should set a variable', () => {
      const variable = db.setVariable({
        key: 'apiKey',
        value: 'test123',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      expect(variable.key).toBe('apiKey');
      expect(variable.value).toBe('test123');
    });

    test('should get variables by scope', () => {
      db.setVariable({
        key: 'var1',
        value: 'value1',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables).toHaveLength(1);
      expect(variables[0].key).toBe('var1');
    });

    test('should delete a variable', () => {
      db.setVariable({
        key: 'var1',
        value: 'value1',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      db.deleteVariable('global', 'var1');
      const variables = db.getVariablesByScope('global');
      expect(variables).toHaveLength(0);
    });
  });

  describe('Settings', () => {
    test('should set and get settings', () => {
      db.setSetting('theme', 'dark');
      db.setSetting('requestTimeout', 30000);

      const settings = db.getAllSettings();
      expect(settings.theme).toBe('dark');
      expect(settings.requestTimeout).toBe(30000);
    });

    test('should update existing setting', () => {
      db.setSetting('theme', 'dark');
      db.setSetting('theme', 'light');

      const settings = db.getAllSettings();
      expect(settings.theme).toBe('light');
    });
  });
});
