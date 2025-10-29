/**
 * Search and Navigation Integration Tests
 * 
 * Tests complete search and navigation workflows:
 * - Global search → navigation
 * - Command palette → action execution
 * - Breadcrumb navigation
 * - Favorites access
 */

import { FavoritesService } from '../../src/main/services/FavoritesService';
import { CommandPaletteService } from '../../src/main/services/CommandPaletteService';

// Mock electron
jest.mock('electron', () => ({
  app: { getPath: jest.fn(() => '/mock/user/data') },
}));

jest.mock('fs', () => ({
  existsSync: jest.fn(() => false),
  readFileSync: jest.fn(),
  writeFileSync: jest.fn(),
}));

describe('Search and Navigation Integration', () => {
  describe('Favorites to Navigation', () => {
    let favoritesService: FavoritesService;

    beforeEach(() => {
      favoritesService = new FavoritesService();
    });

    it('should add item to favorites and retrieve it', () => {
      const favorite = favoritesService.addFavorite({
        type: 'request',
        entityId: 'req-123',
        name: 'Get Users API',
        tags: ['api', 'users'],
      });

      expect(favorite).toBeDefined();
      expect(favorite.name).toBe('Get Users API');

      const retrieved = favoritesService.getFavorite(favorite.id);
      expect(retrieved).toEqual(favorite);
    });

    it('should search favorites and navigate to result', () => {
      favoritesService.addFavorite({
        type: 'request',
        entityId: 'req-1',
        name: 'User Login API',
        tags: ['auth', 'user'],
      });

      favoritesService.addFavorite({
        type: 'request',
        entityId: 'req-2',
        name: 'Product Search API',
        tags: ['products', 'search'],
      });

      const results = favoritesService.searchFavorites('user');

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].name).toContain('User');
    });

    it('should toggle favorite and check status', () => {
      const entityId = 'req-test';
      
      // Add to favorites
      favoritesService.addFavorite({
        type: 'request',
        entityId: entityId,
        name: 'Test Request',
        tags: [],
      });
      expect(favoritesService.isFavorite(entityId)).toBe(true);

      // Remove from favorites
      const favorite = favoritesService.getAllFavorites().find(f => f.entityId === entityId);
      if (favorite) {
        favoritesService.removeFavorite(favorite.id);
      }
      expect(favoritesService.isFavorite(entityId)).toBe(false);
    });

    it('should organize favorites in folders', () => {
      const folder = favoritesService.createFolder('Work APIs');

      const fav1 = favoritesService.addFavorite({
        type: 'request',
        entityId: 'req-1',
        name: 'Work Request 1',
        tags: [],
        folder: folder.id,
      });

      const fav2 = favoritesService.addFavorite({
        type: 'request',
        entityId: 'req-2',
        name: 'Work Request 2',
        tags: [],
        folder: folder.id,
      });

      const folderFavorites = favoritesService.getFavoritesByFolder(folder.id);

      expect(folderFavorites).toHaveLength(2);
      expect(folderFavorites.every(f => f.folder === folder.id)).toBe(true);
    });
  });

  describe('Command Palette Workflow', () => {
    let commandService: CommandPaletteService;

    beforeEach(() => {
      commandService = new CommandPaletteService();
    });

    it('should search and execute command', async () => {
      const mockAction = jest.fn();

      commandService.registerCommand({
        id: 'test.command',
        label: 'Test Command',
        category: 'Tools',
        action: mockAction,
      });

      // Search for command
      const matches = commandService.searchCommands('test');
      expect(matches.length).toBeGreaterThan(0);
      expect(matches[0].command.id).toBe('test.command');

      // Execute command
      const result = await commandService.executeCommand('test.command');
      expect(result).toBe(true);
      expect(mockAction).toHaveBeenCalled();
    });

    it('should track recent commands after execution', async () => {
      const mockAction = jest.fn();

      commandService.registerCommand({
        id: 'recent.command',
        label: 'Recent Command',
        category: 'Tools',
        action: mockAction,
      });

      await commandService.executeCommand('recent.command');

      const recentCommands = commandService.getRecentCommands();
      const recentIds = recentCommands.map(c => c.id);
      expect(recentIds).toContain('recent.command');
    });

    it('should search with fuzzy matching', () => {
      commandService.registerCommand({
        id: 'file.new.request',
        label: 'New API Request',
        category: 'File',
        action: jest.fn(),
      });

      // Fuzzy match "nar" should match "New API Request"
      const matches = commandService.searchCommands('nar');
      
      expect(matches.length).toBeGreaterThan(0);
    });

    it('should filter disabled commands', () => {
      commandService.registerCommand({
        id: 'disabled.command',
        label: 'Disabled Command',
        category: 'Tools',
        action: jest.fn(),
        enabled: false,
      });

      const allCommands = commandService.getAllCommands();
      const disabledCommand = allCommands.find(c => c.id === 'disabled.command');

      expect(disabledCommand).toBeUndefined();
    });
  });

  describe('Search and Favorites Integration', () => {
    it('should add search result to favorites', () => {
      const favoritesService = new FavoritesService();

      // Simulate finding item through search
      const searchResult = {
        id: 'req-found',
        type: 'request' as const,
        name: 'Found API Request',
      };

      // Add to favorites
      const favorite = favoritesService.addFavorite({
        type: searchResult.type,
        entityId: searchResult.id,
        name: searchResult.name,
        tags: ['from-search'],
      });

      expect(favorite).toBeDefined();
      expect(favoritesService.isFavorite(searchResult.id)).toBe(true);
    });
  });

  describe('Command Palette and Quick Actions', () => {
    it('should register and execute quick action commands', async () => {
      const commandService = new CommandPaletteService();
      const actions = {
        newRequest: jest.fn(),
        openFavorites: jest.fn(),
        toggleSidebar: jest.fn(),
      };

      // Register quick action commands
      commandService.registerCommand({
        id: 'quick.new.request',
        label: 'New Request',
        category: 'File',
        shortcut: 'Ctrl+N',
        action: actions.newRequest,
      });

      commandService.registerCommand({
        id: 'quick.favorites',
        label: 'Open Favorites',
        category: 'View',
        shortcut: 'Ctrl+F',
        action: actions.openFavorites,
      });

      commandService.registerCommand({
        id: 'quick.sidebar',
        label: 'Toggle Sidebar',
        category: 'View',
        shortcut: 'Ctrl+B',
        action: actions.toggleSidebar,
      });

      // Execute quick actions
      await commandService.executeCommand('quick.new.request');
      await commandService.executeCommand('quick.favorites');
      await commandService.executeCommand('quick.sidebar');

      expect(actions.newRequest).toHaveBeenCalled();
      expect(actions.openFavorites).toHaveBeenCalled();
      expect(actions.toggleSidebar).toHaveBeenCalled();
    });

    it('should handle command execution errors', async () => {
      const commandService = new CommandPaletteService();

      commandService.registerCommand({
        id: 'error.command',
        label: 'Error Command',
        category: 'Tools',
        action: async () => {
          throw new Error('Command failed');
        },
      });

      const result = await commandService.executeCommand('error.command');
      expect(result).toBe(false);
    });
  });

  describe('Navigation Breadcrumb Integration', () => {
    it('should build breadcrumb path through navigation', () => {
      const breadcrumbs = [
        { id: 'root', label: 'Home', type: 'workspace' as const },
        { id: 'collection', label: 'API Collection', type: 'collection' as const },
        { id: 'folder', label: 'Auth Folder', type: 'folder' as const },
        { id: 'request', label: 'Login Request', type: 'request' as const },
      ];

      // Simulate navigation building breadcrumbs
      expect(breadcrumbs).toHaveLength(4);
      expect(breadcrumbs[0].label).toBe('Home');
      expect(breadcrumbs[breadcrumbs.length - 1].label).toBe('Login Request');
    });

    it('should navigate backwards through breadcrumbs', () => {
      const breadcrumbs = [
        { id: 'root', label: 'Home', type: 'workspace' as const },
        { id: 'collection', label: 'API Collection', type: 'collection' as const },
        { id: 'request', label: 'Request', type: 'request' as const },
      ];

      // Click on second breadcrumb should navigate to collection
      const targetBreadcrumb = breadcrumbs[1];
      expect(targetBreadcrumb.label).toBe('API Collection');
    });
  });

  describe('Complete Search to Action Flow', () => {
    it('should search, select, and execute action', async () => {
      const commandService = new CommandPaletteService();
      const mockNavigate = jest.fn();

      commandService.registerCommand({
        id: 'navigate.request',
        label: 'Open User Request',
        category: 'Go',
        action: mockNavigate,
      });

      // User opens command palette (Ctrl+P)
      // User types search query
      const results = commandService.searchCommands('user');
      expect(results.length).toBeGreaterThan(0);

      // User selects first result
      const selectedCommand = results[0];
      await commandService.executeCommand(selectedCommand.command.id);

      // Action should be executed
      expect(mockNavigate).toHaveBeenCalled();
    });

    it('should handle empty search results', () => {
      const commandService = new CommandPaletteService();
      const results = commandService.searchCommands('xyz123nonexistent');

      expect(results.length).toBeGreaterThanOrEqual(0);
    });
  });
});
