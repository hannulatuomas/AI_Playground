/**
 * FavoritesService Unit Tests - Favorites management
 */

import { FavoritesService, type Favorite } from '../../../src/main/services/FavoritesService';
import * as fs from 'fs';

jest.mock('fs');
jest.mock('electron', () => ({
  app: { getPath: jest.fn(() => '/mock/user/data') },
}));

const mockFs = fs as jest.Mocked<typeof fs>;

describe('FavoritesService', () => {
  let service: FavoritesService;

  beforeEach(() => {
    jest.clearAllMocks();
    mockFs.existsSync.mockReturnValue(false);
    mockFs.writeFileSync.mockImplementation(() => {});
    service = new FavoritesService();
  });

  describe('Add/Remove Favorites', () => {
    it('should add a favorite', () => {
      const fav = service.addFavorite({
        type: 'request',
        entityId: 'req-1',
        name: 'Test Request',
        tags: [],
      });

      expect(fav).toBeDefined();
      expect(fav.id).toBeDefined();
      expect(fav.name).toBe('Test Request');
    });

    it('should remove a favorite', () => {
      const fav = service.addFavorite({
        type: 'request',
        entityId: 'req-1',
        name: 'Test Request',
        tags: [],
      });

      const result = service.removeFavorite(fav.id);
      expect(result).toBe(true);
      expect(service.getFavorite(fav.id)).toBeUndefined();
    });

    it('should return false when removing non-existent favorite', () => {
      const result = service.removeFavorite('non-existent');
      expect(result).toBe(false);
    });
  });

  describe('Toggle Favorites', () => {
    it('should toggle favorite on', () => {
      const result = service.toggleFavorite({
        type: 'request',
        entityId: 'req-1',
        name: 'Test Request',
        tags: [],
      });
      expect(result.added).toBe(true);
      expect(service.isFavorite('req-1')).toBe(true);
    });

    it('should toggle favorite off', () => {
      service.toggleFavorite({
        type: 'request',
        entityId: 'req-1',
        name: 'Test Request',
        tags: [],
      });
      const result = service.toggleFavorite({
        type: 'request',
        entityId: 'req-1',
        name: 'Test Request',
        tags: [],
      });
      expect(result.added).toBe(false);
      expect(service.isFavorite('req-1')).toBe(false);
    });
  });

  describe('Search Favorites', () => {
    beforeEach(() => {
      service.addFavorite({
        type: 'request',
        entityId: 'req-1',
        name: 'User API Request',
        tags: ['api', 'user'],
      });

      service.addFavorite({
        type: 'collection',
        entityId: 'col-1',
        name: 'Auth Collection',
        tags: ['auth'],
      });
    });

    it('should search by name', () => {
      const results = service.searchFavorites('user');
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].name).toContain('User');
    });

    it('should search by tags', () => {
      const results = service.searchFavorites('api');
      expect(results.length).toBeGreaterThan(0);
    });

    it('should return all favorites for empty query', () => {
      const results = service.searchFavorites('');
      expect(results.length).toBe(2);
    });
  });

  describe('Folders', () => {
    it('should create folder', () => {
      const folder = service.createFolder('Work Projects');
      expect(folder).toBeDefined();
      expect(folder.name).toBe('Work Projects');
    });

    it('should get all folders', () => {
      service.createFolder('Folder 1');
      service.createFolder('Folder 2');
      const folders = service.getAllFolders();
      expect(folders.length).toBe(2);
    });

    it('should add favorite to folder', () => {
      const folder = service.createFolder('Work');
      const fav = service.addFavorite({
        type: 'request',
        entityId: 'req-1',
        name: 'Test',
        tags: [],
        folder: folder.id,
      });

      expect(fav.folder).toBe(folder.id);
    });
  });

  describe('Tags', () => {
    it('should get favorites by tag', () => {
      service.addFavorite({
        type: 'request',
        entityId: 'req-1',
        name: 'Test 1',
        tags: ['important'],
      });

      const results = service.getFavoritesByTag('important');
      expect(results.length).toBeGreaterThan(0);
    });

    it('should get all unique tags', () => {
      service.addFavorite({
        type: 'request',
        entityId: 'req-1',
        name: 'Test 1',
        tags: ['tag1', 'tag2'],
      });

      service.addFavorite({
        type: 'request',
        entityId: 'req-2',
        name: 'Test 2',
        tags: ['tag2', 'tag3'],
      });

      const tags = service.getAllTags();
      expect(tags).toContain('tag1');
      expect(tags).toContain('tag2');
      expect(tags).toContain('tag3');
    });
  });

  describe('Persistence', () => {
    it('should save favorites to file', () => {
      service.addFavorite({
        type: 'request',
        entityId: 'req-1',
        name: 'Test',
        tags: [],
      });

      expect(mockFs.writeFileSync).toHaveBeenCalled();
    });

    it('should load favorites from file', () => {
      const mockData = {
        favorites: [
          {
            id: '1',
            type: 'request',
            entityId: 'req-1',
            name: 'Test',
            tags: [],
            order: 0,
            createdAt: Date.now(),
            lastAccessedAt: Date.now(),
          },
        ],
        folders: [],
      };

      mockFs.existsSync.mockReturnValue(true);
      mockFs.readFileSync.mockReturnValue(JSON.stringify(mockData));

      const newService = new FavoritesService();
      const favs = newService.getAllFavorites();

      expect(favs.length).toBe(1);
    });
  });
});
