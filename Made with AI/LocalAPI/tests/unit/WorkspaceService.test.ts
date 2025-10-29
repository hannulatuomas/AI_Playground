// WorkspaceService Unit Tests
import { WorkspaceService } from '../../src/main/services/WorkspaceService';
import * as path from 'path';

// Create mock functions
const mockWriteFile = jest.fn();
const mockReadFile = jest.fn();
const mockUnlink = jest.fn();
const mockReaddir = jest.fn();
const mockCopyFile = jest.fn();
const mockExistsSync = jest.fn();
const mockMkdirSync = jest.fn();

// Mock fs module
jest.mock('fs', () => ({
  existsSync: jest.fn().mockReturnValue(true),
  mkdirSync: jest.fn(),
  promises: {
    writeFile: jest.fn().mockResolvedValue(undefined),
    readFile: jest.fn().mockResolvedValue('{}'),
    unlink: jest.fn().mockResolvedValue(undefined),
    readdir: jest.fn().mockResolvedValue([]),
    copyFile: jest.fn().mockResolvedValue(undefined),
  },
}));

// Get the mocked fs module
const fs = require('fs');

// Mock electron app
jest.mock('electron', () => ({
  app: {
    getPath: jest.fn(() => '/mock/userdata'),
  },
}));

describe('WorkspaceService', () => {
  let service: WorkspaceService;
  const mockUserDataPath = '/mock/userdata';
  const mockWorkspacesDir = path.join(mockUserDataPath, 'workspaces');
  const mockTemplatesDir = path.join(mockUserDataPath, 'templates');
  const mockSnapshotsDir = path.join(mockUserDataPath, 'snapshots');

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Reset mock implementations
    fs.existsSync.mockReturnValue(true);
    fs.mkdirSync.mockImplementation(() => {});
    fs.promises.writeFile.mockResolvedValue(undefined);
    fs.promises.readFile.mockResolvedValue('{}');
    fs.promises.unlink.mockResolvedValue(undefined);
    fs.promises.readdir.mockResolvedValue([]);
    fs.promises.copyFile.mockResolvedValue(undefined);

    service = new WorkspaceService();
  });

  afterEach(() => {
    service.cleanup();
  });

  describe('Workspace Creation', () => {
    it('should create a new workspace', () => {
      const workspace = service.createWorkspace('Test Workspace', 'Test description');

      expect(workspace).toBeDefined();
      expect(workspace.name).toBe('Test Workspace');
      expect(workspace.description).toBe('Test description');
      expect(workspace.collections).toEqual([]);
      expect(workspace.environments).toEqual([]);
      expect(workspace.globalVariables).toEqual([]);
      expect(workspace.settings).toBeDefined();
      expect(workspace.createdAt).toBeInstanceOf(Date);
      expect(workspace.updatedAt).toBeInstanceOf(Date);
    });

    it('should create workspace with default settings', () => {
      const workspace = service.createWorkspace('Test');

      expect(workspace.settings.theme).toBe('light');
      expect(workspace.settings.autoSave).toBe(true);
      expect(workspace.settings.autoSaveInterval).toBe(300);
      expect(workspace.settings.requestTimeout).toBe(30000);
    });

    it('should set workspace as current', () => {
      const workspace = service.createWorkspace('Test');
      const current = service.getCurrentWorkspace();

      expect(current).toEqual(workspace);
    });
  });

  describe('Workspace Save/Load', () => {
    it('should save workspace to file', async () => {
      const workspace = service.createWorkspace('Test');
      const filePath = await service.saveWorkspace(workspace);

      expect(fs.promises.writeFile).toHaveBeenCalled();
      expect(filePath).toContain(workspace.id);
      expect(filePath).toContain('.json');
    });

    it('should update updatedAt when saving', async () => {
      const workspace = service.createWorkspace('Test');
      const originalUpdatedAt = workspace.updatedAt;

      // Wait a bit to ensure timestamp changes
      await new Promise(resolve => setTimeout(resolve, 10));
      
      await service.saveWorkspace(workspace);

      expect(workspace.updatedAt.getTime()).toBeGreaterThan(originalUpdatedAt.getTime());
    });

    it('should load workspace from file', async () => {
      const mockWorkspace = {
        id: 'test-123',
        name: 'Test Workspace',
        description: 'Test',
        collections: [],
        environments: [],
        globalVariables: [],
        settings: {
          theme: 'dark',
          requestTimeout: 30000,
          followRedirects: true,
          validateSSL: true,
          proxyEnabled: false,
          maxResponseSize: 10485760,
          autoSave: true,
          autoSaveInterval: 300,
          editorFontSize: 14,
          editorTheme: 'vs-dark',
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      fs.promises.readFile.mockResolvedValue(JSON.stringify(mockWorkspace));

      const workspace = await service.loadWorkspace('test-123');

      expect(workspace.id).toBe('test-123');
      expect(workspace.name).toBe('Test Workspace');
      expect(workspace.createdAt).toBeInstanceOf(Date);
      expect(workspace.updatedAt).toBeInstanceOf(Date);
      expect(workspace.lastOpenedAt).toBeInstanceOf(Date);
    });

    it('should throw error when loading non-existent workspace', async () => {
      fs.existsSync.mockReturnValue(false);

      await expect(service.loadWorkspace('non-existent')).rejects.toThrow('Workspace not found');
    });

    it('should set workspace as current when loaded', async () => {
      const mockWorkspace = {
        id: 'test-123',
        name: 'Test',
        collections: [],
        environments: [],
        globalVariables: [],
        settings: {
          theme: 'light',
          requestTimeout: 30000,
          followRedirects: true,
          validateSSL: true,
          proxyEnabled: false,
          maxResponseSize: 10485760,
          autoSave: true,
          editorFontSize: 14,
          editorTheme: 'vs-dark',
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      fs.promises.readFile.mockResolvedValue(JSON.stringify(mockWorkspace));

      await service.loadWorkspace('test-123');
      const current = service.getCurrentWorkspace();

      expect(current?.id).toBe('test-123');
    });
  });

  describe('Workspace Update', () => {
    it('should update workspace properties', () => {
      service.createWorkspace('Test');
      
      service.updateWorkspace({ name: 'Updated Name' });
      const current = service.getCurrentWorkspace();

      expect(current?.name).toBe('Updated Name');
    });

    it('should throw error when no current workspace', () => {
      expect(() => service.updateWorkspace({ name: 'Test' })).toThrow('No current workspace');
    });

    it('should mark workspace as dirty after update', () => {
      service.createWorkspace('Test');
      service.updateWorkspace({ name: 'Updated' });

      expect(service.isDirtyWorkspace()).toBe(true);
    });
  });

  describe('Workspace Delete', () => {
    it('should delete workspace file', async () => {
      await service.deleteWorkspace('test-123');

      expect(fs.promises.unlink).toHaveBeenCalled();
    });

    it('should clear current workspace if deleting current', async () => {
      const workspace = service.createWorkspace('Test');
      await service.deleteWorkspace(workspace.id);

      expect(service.getCurrentWorkspace()).toBeNull();
    });

    it('should delete associated snapshots', async () => {
      fs.promises.readdir.mockResolvedValue(['snapshot1.json', 'snapshot2.json']);
      fs.promises.readFile.mockResolvedValue(JSON.stringify({
        id: 'snap-1',
        workspaceId: 'test-123',
        name: 'Snapshot',
        workspace: {},
        createdAt: new Date().toISOString(),
      }));

      await service.deleteWorkspace('test-123');

      // Should delete workspace + snapshots
      expect(fs.promises.unlink).toHaveBeenCalled();
    });
  });

  describe('Workspace Listing', () => {
    it('should list all workspaces', async () => {
      const mockWorkspace = {
        id: 'test-123',
        name: 'Test',
        collections: [],
        environments: [],
        globalVariables: [],
        settings: {},
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      fs.promises.readdir.mockResolvedValue(['test-123.json']);
      fs.promises.readFile.mockResolvedValue(JSON.stringify(mockWorkspace));

      const workspaces = await service.listWorkspaces();

      expect(workspaces).toHaveLength(1);
      expect(workspaces[0].id).toBe('test-123');
      expect(workspaces[0].name).toBe('Test');
    });

    it('should sort workspaces by lastOpenedAt descending', async () => {
      const ws1 = {
        id: 'ws-1',
        name: 'First',
        collections: [],
        environments: [],
        globalVariables: [],
        settings: {},
        createdAt: new Date('2024-01-01').toISOString(),
        updatedAt: new Date('2024-01-01').toISOString(),
        lastOpenedAt: new Date('2024-01-01').toISOString(),
      };

      const ws2 = {
        id: 'ws-2',
        name: 'Second',
        collections: [],
        environments: [],
        globalVariables: [],
        settings: {},
        createdAt: new Date('2024-01-02').toISOString(),
        updatedAt: new Date('2024-01-02').toISOString(),
        lastOpenedAt: new Date('2024-01-02').toISOString(),
      };

      fs.promises.readdir.mockResolvedValue(['ws-1.json', 'ws-2.json']);
      fs.promises.readFile
        .mockResolvedValueOnce(JSON.stringify(ws1))
        .mockResolvedValueOnce(JSON.stringify(ws2));

      const workspaces = await service.listWorkspaces();

      expect(workspaces[0].id).toBe('ws-2'); // Most recent first
      expect(workspaces[1].id).toBe('ws-1');
    });

    it('should get recent workspaces (max 10)', async () => {
      const mockFiles = Array.from({ length: 15 }, (_, i) => `ws-${i}.json`);
      fs.promises.readdir.mockResolvedValue(mockFiles);
      fs.promises.readFile.mockImplementation((path: string) => {
        const id = path.match(/ws-(\d+)/)![1];
        return Promise.resolve(JSON.stringify({
          id: `ws-${id}`,
          name: `Workspace ${id}`,
          collections: [],
          environments: [],
          globalVariables: [],
          settings: {},
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          lastOpenedAt: new Date().toISOString(),
        }));
      });

      const recent = await service.getRecentWorkspaces();

      expect(recent.length).toBeLessThanOrEqual(10);
    });
  });

  describe('Workspace Export/Import', () => {
    it('should export workspace to file', async () => {
      const workspace = service.createWorkspace('Test');
      await service.saveWorkspace(workspace);

      await service.exportWorkspace(workspace.id, '/export/path.json');

      expect(fs.promises.copyFile).toHaveBeenCalled();
    });

    it('should import workspace from file', async () => {
      const mockWorkspace = {
        id: 'old-id',
        name: 'Imported',
        collections: [],
        environments: [],
        globalVariables: [],
        settings: {},
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      fs.promises.readFile.mockResolvedValue(JSON.stringify(mockWorkspace));

      const workspace = await service.importWorkspace('/import/path.json');

      expect(workspace.name).toBe('Imported');
      expect(workspace.id).not.toBe('old-id'); // Should generate new ID
      expect(fs.promises.writeFile).toHaveBeenCalled();
    });
  });

  describe('Snapshots', () => {
    it('should create snapshot of current workspace', async () => {
      service.createWorkspace('Test');

      const snapshot = await service.createSnapshot('Before changes', 'Test snapshot');

      expect(snapshot.name).toBe('Before changes');
      expect(snapshot.description).toBe('Test snapshot');
      expect(snapshot.workspace).toBeDefined();
      expect(fs.promises.writeFile).toHaveBeenCalled();
    });

    it('should throw error when creating snapshot without current workspace', async () => {
      await expect(service.createSnapshot('Test')).rejects.toThrow('No current workspace');
    });

    it('should restore workspace from snapshot', async () => {
      const mockSnapshot = {
        id: 'snap-123',
        workspaceId: 'ws-123',
        name: 'Snapshot',
        workspace: {
          id: 'ws-123',
          name: 'Restored',
          collections: [],
          environments: [],
          globalVariables: [],
          settings: {},
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        createdAt: new Date().toISOString(),
      };

      fs.promises.readFile.mockResolvedValue(JSON.stringify(mockSnapshot));

      const workspace = await service.restoreSnapshot('snap-123');

      expect(workspace.name).toBe('Restored');
      expect(fs.promises.writeFile).toHaveBeenCalled();
    });

    it('should list snapshots for workspace', async () => {
      const mockSnapshot = {
        id: 'snap-1',
        workspaceId: 'ws-123',
        name: 'Snapshot',
        workspace: {},
        createdAt: new Date().toISOString(),
      };

      fs.promises.readdir.mockResolvedValue(['snap-1.json', 'snap-2.json']);
      fs.promises.readFile.mockResolvedValue(JSON.stringify(mockSnapshot));

      const snapshots = await service.listSnapshots('ws-123');

      expect(snapshots.length).toBeGreaterThan(0);
      expect(snapshots[0].workspaceId).toBe('ws-123');
    });

    it('should delete snapshot', async () => {
      await service.deleteSnapshot('snap-123');

      expect(fs.promises.unlink).toHaveBeenCalled();
    });
  });

  describe('Templates', () => {
    it('should save workspace as template', async () => {
      service.createWorkspace('Test');

      const template = await service.saveAsTemplate('My Template', 'Description', ['tag1', 'tag2']);

      expect(template.name).toBe('My Template');
      expect(template.description).toBe('Description');
      expect(template.tags).toEqual(['tag1', 'tag2']);
      expect(template.workspace).toBeDefined();
      expect(fs.promises.writeFile).toHaveBeenCalled();
    });

    it('should load workspace from template', async () => {
      const mockTemplate = {
        id: 'tpl-123',
        name: 'Template',
        workspace: {
          name: 'Template Workspace',
          collections: [],
          environments: [],
          globalVariables: [],
          settings: {},
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      fs.promises.readFile.mockResolvedValue(JSON.stringify(mockTemplate));

      const workspace = await service.loadFromTemplate('tpl-123', 'New Workspace');

      expect(workspace.name).toBe('New Workspace');
      expect(workspace.id).toBeDefined();
      expect(fs.promises.writeFile).toHaveBeenCalled();
    });

    it('should list all templates', async () => {
      const mockTemplate = {
        id: 'tpl-1',
        name: 'Template',
        workspace: {},
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      fs.promises.readdir.mockResolvedValue(['tpl-1.json']);
      fs.promises.readFile.mockResolvedValue(JSON.stringify(mockTemplate));

      const templates = await service.listTemplates();

      expect(templates).toHaveLength(1);
      expect(templates[0].id).toBe('tpl-1');
    });

    it('should delete template', async () => {
      await service.deleteTemplate('tpl-123');

      expect(fs.promises.unlink).toHaveBeenCalled();
    });
  });

  describe('Auto-save', () => {
    it('should start auto-save timer', () => {
      service.createWorkspace('Test');
      service.startAutoSave(1); // 1 second for testing

      // Timer should be set
      expect((service as any).autoSaveTimer).toBeDefined();
    });

    it('should stop auto-save timer', () => {
      service.createWorkspace('Test');
      service.startAutoSave(1);
      service.stopAutoSave();

      expect((service as any).autoSaveTimer).toBeNull();
    });

    it('should mark workspace as dirty', () => {
      service.createWorkspace('Test');
      service.markDirty();

      expect(service.isDirtyWorkspace()).toBe(true);
    });

    it('should clear dirty flag after save', async () => {
      service.createWorkspace('Test');
      service.markDirty();
      await service.saveWorkspace();

      expect(service.isDirtyWorkspace()).toBe(false);
    });
  });

  describe('Backup/Restore', () => {
    it('should backup workspace to specific location', async () => {
      const workspace = service.createWorkspace('Test');
      await service.saveWorkspace(workspace);

      await service.backupWorkspace(workspace.id, '/backup/path.json');

      expect(fs.promises.copyFile).toHaveBeenCalled();
    });

    it('should restore workspace from backup', async () => {
      const mockWorkspace = {
        id: 'old-id',
        name: 'Backup',
        collections: [],
        environments: [],
        globalVariables: [],
        settings: {},
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      fs.promises.readFile.mockResolvedValue(JSON.stringify(mockWorkspace));

      const workspace = await service.restoreFromBackup('/backup/path.json');

      expect(workspace.name).toBe('Backup');
      expect(workspace.id).not.toBe('old-id');
    });
  });

  describe('Cleanup', () => {
    it('should stop auto-save on cleanup', () => {
      service.createWorkspace('Test');
      service.startAutoSave(1);
      service.cleanup();

      expect((service as any).autoSaveTimer).toBeNull();
    });
  });
});
