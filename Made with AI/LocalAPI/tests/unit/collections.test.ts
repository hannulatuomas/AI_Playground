// Unit tests for Collections functionality
import { DatabaseService } from '../../src/main/services/DatabaseService';
import type { Collection } from '../../src/types/models';
import { createTestDatabase } from '../utils/database-test-utils';
import { MockDatabase } from '../mocks/better-sqlite3.mock';

describe('Collections', () => {
  let db: DatabaseService;
  let mockDb: MockDatabase;

  beforeEach(() => {
    // Use mock database for tests
    const testDb = createTestDatabase();
    db = testDb.db;
    mockDb = testDb.mockDb;
  });

  afterEach(() => {
    db.close();
  });

  describe('Create Collection', () => {
    test('should create a collection with valid data', () => {
      const collection = db.createCollection({
        id: 'col-test-1',
        name: 'Test Collection',
        description: 'A test collection',
        requests: [],
        folders: [],
      });

      expect(collection).toBeDefined();
      expect(collection.id).toBeDefined();
      expect(collection.name).toBe('Test Collection');
      expect(collection.description).toBe('A test collection');
      expect(collection.createdAt).toBeInstanceOf(Date);
      expect(collection.updatedAt).toBeInstanceOf(Date);
    });

    test('should create a collection without description', () => {
      const collection = db.createCollection({
        id: 'col-simple-1',
        name: 'Simple Collection',
        requests: [],
        folders: [],
      });

      expect(collection).toBeDefined();
      expect(collection.name).toBe('Simple Collection');
      expect(collection.description).toBeUndefined();
    });

    test('should generate unique IDs for collections', () => {
      const collection1 = db.createCollection({ id: 'col-1', name: 'Collection 1', requests: [], folders: [] });
      const collection2 = db.createCollection({ id: 'col-2', name: 'Collection 2', requests: [], folders: [] });

      expect(collection1.id).not.toBe(collection2.id);
    });

    test('should handle special characters in name', () => {
      const collection = db.createCollection({
        id: 'col-special-1',
        name: 'Test & Collection "Special" <Chars>',
        requests: [],
        folders: [],
      });

      expect(collection.name).toBe('Test & Collection "Special" <Chars>');
    });
  });

  describe('Get Collection', () => {
    test('should retrieve a collection by ID', () => {
      const created = db.createCollection({
        id: 'col-read-1',
        name: 'Test Collection',
        description: 'Test description',
        requests: [],
        folders: [],
      });

      const retrieved = db.getCollectionById(created.id);

      expect(retrieved).toBeDefined();
      expect(retrieved?.id).toBe(created.id);
      expect(retrieved?.name).toBe('Test Collection');
      expect(retrieved?.description).toBe('Test description');
    });

    test('should return null for non-existent collection', () => {
      const collection = db.getCollectionById('non-existent-id');
      expect(collection).toBeNull();
    });

    test('should retrieve collection without requests', () => {
      const collection = db.createCollection({
        id: 'col-test-req',
        name: 'Test Collection',
        requests: [],
        folders: [],
      });
      
      db.createRequest({
        id: 'req-1',
        name: 'Test Request',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com/test',
        collectionId: collection.id,
        headers: [],
        queryParams: [],
        body: { type: 'none', content: '' },
        auth: { type: 'none' },
        assertions: [],
      });

      const retrieved = db.getCollectionById(collection.id);

      expect(retrieved).toBeDefined();
      expect(retrieved?.requests).toBeDefined();
      // Requests are loaded separately, so length should be 0
      expect(retrieved?.requests?.length).toBe(0);
    });
  });

  describe('Get All Collections', () => {
    test('should return empty array when no collections exist', () => {
      const collections = db.getAllCollections();
      expect(collections).toEqual([]);
    });

    test('should return all collections', () => {
      db.createCollection({ id: 'col-all-1', name: 'Collection 1', requests: [], folders: [] });
      db.createCollection({ id: 'col-all-2', name: 'Collection 2', requests: [], folders: [] });
      db.createCollection({ id: 'col-all-3', name: 'Collection 3', requests: [], folders: [] });

      const collections = db.getAllCollections();

      expect(collections).toHaveLength(3);
      expect(collections[0].name).toBe('Collection 1');
      expect(collections[1].name).toBe('Collection 2');
      expect(collections[2].name).toBe('Collection 3');
    });

    test('should return all collections without requests', () => {
      const col1 = db.createCollection({ id: 'col-all-req-1', name: 'Collection 1', requests: [], folders: [] });
      const col2 = db.createCollection({ id: 'col-all-req-2', name: 'Collection 2', requests: [], folders: [] });

      db.createRequest({
        id: 'req-all-1',
        protocol: 'REST',
        name: 'Request 1',
        method: 'GET',
        url: 'https://api.example.com',
        collectionId: col1.id,
        headers: [],
        queryParams: [],
        body: { type: 'none', content: '' },
        auth: { type: 'none' },
        assertions: [],
      });

      db.createRequest({
        id: 'req-all-2',
        protocol: 'REST',
        name: 'Request 2',
        method: 'POST',
        url: 'https://api.example.com',
        collectionId: col2.id,
        headers: [],
        queryParams: [],
        body: { type: 'none', content: '' },
        auth: { type: 'none' },
        assertions: [],
      });

      const collections = db.getAllCollections();

      expect(collections).toHaveLength(2);
      // Requests are loaded separately
      expect(collections[0].requests).toHaveLength(0);
      expect(collections[1].requests).toHaveLength(0);
    });
  });

  describe('Update Collection', () => {
    test('should update collection name', () => {
      const collection = db.createCollection({ id: 'col-upd-name-1', name: 'Original Name', requests: [], folders: [] });

      db.updateCollection(collection.id, { name: 'Updated Name' });

      const updated = db.getCollectionById(collection.id);
      expect(updated?.name).toBe('Updated Name');
    });

    test('should update collection description', () => {
      const collection = db.createCollection({
        id: 'col-upd-desc-1',
        name: 'Test Collection',
        description: 'Original description',
        requests: [],
        folders: [],
      });

      db.updateCollection(collection.id, { description: 'Updated description' });

      const updated = db.getCollectionById(collection.id);
      expect(updated?.description).toBe('Updated description');
    });

    test('should update both name and description', () => {
      const collection = db.createCollection({
        id: 'col-upd-both-1',
        name: 'Original Name',
        description: 'Original description',
        requests: [],
        folders: [],
      });

      db.updateCollection(collection.id, {
        name: 'New Name',
        description: 'New description',
      });

      const updated = db.getCollectionById(collection.id);
      expect(updated?.name).toBe('New Name');
      expect(updated?.description).toBe('New description');
    });

    test('should update updatedAt timestamp', (done) => {
      const collection = db.createCollection({ id: 'col-upd-time-1', name: 'Test Collection', requests: [], folders: [] });
      const originalUpdatedAt = collection.updatedAt;

      // Wait a bit to ensure timestamp difference
      setTimeout(() => {
        db.updateCollection(collection.id, { name: 'Updated Name' });

        const updated = db.getCollectionById(collection.id);
        expect(updated?.updatedAt.getTime()).toBeGreaterThan(originalUpdatedAt.getTime());
        done();
      }, 10);
    });
  });

  describe('Delete Collection', () => {
    test('should delete a collection', () => {
      const collection = db.createCollection({ id: 'col-del-1', name: 'Test Collection', requests: [], folders: [] });

      db.deleteCollection(collection.id);

      const retrieved = db.getCollectionById(collection.id);
      expect(retrieved).toBeNull();
    });

    test('should delete collection and its requests', () => {
      const collection = db.createCollection({ id: 'col-del-req-1', name: 'Test Collection', requests: [], folders: [] });
      
      const request = db.createRequest({
        id: 'req-del-1',
        protocol: 'REST',
        name: 'Test Request',
        method: 'GET',
        url: 'https://api.example.com',
        collectionId: collection.id,
        headers: [],
        queryParams: [],
        body: { type: 'none', content: '' },
        auth: { type: 'none' },
        assertions: [],
      });

      db.deleteCollection(collection.id);

      const retrievedCollection = db.getCollectionById(collection.id);
      const retrievedRequest = db.getRequestById(request.id);

      expect(retrievedCollection).toBeNull();
      expect(retrievedRequest).toBeNull();
    });

    test('should not affect other collections', () => {
      const collection1 = db.createCollection({ id: 'col-del-2', name: 'Collection 1', requests: [], folders: [] });
      const collection2 = db.createCollection({ id: 'col-del-3', name: 'Collection 2', requests: [], folders: [] });

      db.deleteCollection(collection1.id);

      const retrieved = db.getCollectionById(collection2.id);
      expect(retrieved).toBeDefined();
      expect(retrieved?.name).toBe('Collection 2');
    });
  });

  describe('Collection with Requests', () => {
    test('should create requests for collection', () => {
      const collection = db.createCollection({ id: 'col-req-count-1', name: 'Test Collection', requests: [], folders: [] });

      const req1 = db.createRequest({
        id: 'req-req-count-1',
        protocol: 'REST',
        name: 'Request 1',
        method: 'GET',
        url: 'https://api.example.com/1',
        collectionId: collection.id,
        headers: [],
        queryParams: [],
        body: { type: 'none', content: '' },
        auth: { type: 'none' },
        assertions: [],
      });

      const req2 = db.createRequest({
        id: 'req-req-count-2',
        protocol: 'REST',
        name: 'Request 2',
        method: 'POST',
        url: 'https://api.example.com/2',
        collectionId: collection.id,
        headers: [],
        queryParams: [],
        body: { type: 'none', content: '' },
        auth: { type: 'none' },
        assertions: [],
      });

      // Verify requests were created
      expect(req1.collectionId).toBe(collection.id);
      expect(req2.collectionId).toBe(collection.id);
    });

    test('should handle empty collection', () => {
      const collection = db.createCollection({ id: 'col-empty-1', name: 'Empty Collection', requests: [], folders: [] });
      const retrieved = db.getCollectionById(collection.id);

      expect(retrieved?.requests).toBeDefined();
      expect(retrieved?.requests).toHaveLength(0);
    });
  });

  describe('Edge Cases', () => {
    test('should handle long collection names', () => {
      const longName = 'A'.repeat(1000);
      const collection = db.createCollection({ id: 'col-long-1', name: longName, requests: [], folders: [] });

      expect(collection.name).toBe(longName);
    });

    test('should handle long descriptions', () => {
      const longDescription = 'B'.repeat(5000);
      const collection = db.createCollection({
        id: 'col-long-desc-1',
        name: 'Test',
        description: longDescription,
        requests: [],
        folders: [],
      });

      expect(collection.description).toBe(longDescription);
    });

    test('should handle unicode characters', () => {
      const collection = db.createCollection({
        id: 'col-unicode-1',
        name: '测试集合 🚀 émojis',
        description: 'Ñoño descripción 中文',
        requests: [],
        folders: [],
      });

      expect(collection.name).toBe('测试集合 🚀 émojis');
      expect(collection.description).toBe('Ñoño descripción 中文');
    });

    test('should handle rapid creation', () => {
      const collections: Collection[] = [];
      for (let i = 0; i < 100; i++) {
        collections.push(db.createCollection({ id: `col-rapid-${i}`, name: `Collection ${i}`, requests: [], folders: [] }));
      }

      const allCollections = db.getAllCollections();
      expect(allCollections).toHaveLength(100);
    });
  });
});
