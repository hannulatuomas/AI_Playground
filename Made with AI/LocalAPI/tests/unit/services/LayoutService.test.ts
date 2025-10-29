/**
 * LayoutService Unit Tests
 */

import { LayoutService, type LayoutConfig, type PanelConfig } from '../../../src/main/services/LayoutService';
import * as fs from 'fs';

jest.mock('fs');
jest.mock('electron', () => ({
  app: { getPath: jest.fn(() => '/mock/user/data') },
}));

const mockFs = fs as jest.Mocked<typeof fs>;

describe('LayoutService', () => {
  let service: LayoutService;

  beforeEach(() => {
    jest.clearAllMocks();
    mockFs.existsSync.mockReturnValue(false);
    mockFs.writeFileSync.mockImplementation(() => {});
    service = new LayoutService();
  });

  describe('Create Layout', () => {
    it('should create a new layout', () => {
      const panels: PanelConfig[] = [{
        id: 'panel-1',
        type: 'sidebar',
        visible: true,
        position: { area: 'left', order: 0 },
        size: { width: 250 },
        docked: true,
      }];

      const layout = service.createLayout('My Layout', panels);

      expect(layout).toBeDefined();
      expect(layout.name).toBe('My Layout');
      expect(layout.panels).toEqual(panels);
    });

    it('should create layout with description', () => {
      const panels: PanelConfig[] = [];
      const layout = service.createLayout('Test', panels, 'Test description');

      expect(layout.description).toBe('Test description');
    });
  });

  describe('Get Layout', () => {
    it('should get layout by ID', () => {
      const panels: PanelConfig[] = [];
      const created = service.createLayout('Test', panels);
      const retrieved = service.getLayout(created.id);

      expect(retrieved).toEqual(created);
    });

    it('should return undefined for non-existent layout', () => {
      const layout = service.getLayout('non-existent');
      expect(layout).toBeUndefined();
    });

    it('should get all layouts', () => {
      const initialCount = service.getAllLayouts().length; // Includes default layouts
      service.createLayout('Layout 1', []);
      service.createLayout('Layout 2', []);

      const layouts = service.getAllLayouts();
      expect(layouts.length).toBe(initialCount + 2);
    });
  });

  describe('Update Layout', () => {
    it('should update layout', () => {
      const layout = service.createLayout('Original', []);
      const updated = service.updateLayout(layout.id, { name: 'Updated' });

      expect(updated).toBe(true);
      const retrieved = service.getLayout(layout.id);
      expect(retrieved?.name).toBe('Updated');
    });

    it('should return false for non-existent layout', () => {
      const result = service.updateLayout('non-existent', { name: 'Test' });
      expect(result).toBe(false);
    });
  });

  describe('Delete Layout', () => {
    it('should delete layout', () => {
      const layout = service.createLayout('To Delete', []);
      const result = service.deleteLayout(layout.id);

      expect(result).toBe(true);
      expect(service.getLayout(layout.id)).toBeUndefined();
    });

    it('should return false for non-existent layout', () => {
      const result = service.deleteLayout('non-existent');
      expect(result).toBe(false);
    });
  });

  describe('Active Layout', () => {
    it('should set active layout', () => {
      const layout = service.createLayout('Active', []);
      const result = service.setActiveLayout(layout.id);

      expect(result).toBe(true);
      expect(service.getActiveLayout()?.id).toBe(layout.id);
    });

    it('should return false for non-existent layout', () => {
      const result = service.setActiveLayout('non-existent');
      expect(result).toBe(false);
    });
  });

  describe('Default Layouts', () => {
    it('should create default layouts', () => {
      const layouts = service.getAllLayouts();
      expect(layouts.length).toBeGreaterThan(0);
    });

    it('should have IDE style layout', () => {
      const layouts = service.getAllLayouts();
      const ideLayout = layouts.find(l => l.name.toLowerCase().includes('ide'));
      expect(ideLayout).toBeDefined();
    });
  });

  describe('Panel Management', () => {
    it('should add panel to layout', () => {
      const layout = service.createLayout('Test', []);
      const panel: PanelConfig = {
        id: 'new-panel',
        type: 'sidebar',
        visible: true,
        position: { area: 'left', order: 0 },
        size: {},
        docked: true,
      };

      const result = service.addPanel(layout.id, panel);
      expect(result).toBe(true);

      const updated = service.getLayout(layout.id);
      expect(updated?.panels).toContainEqual(panel);
    });

    it('should remove panel from layout', () => {
      const panel: PanelConfig = {
        id: 'panel-1',
        type: 'sidebar',
        visible: true,
        position: { area: 'left', order: 0 },
        size: {},
        docked: true,
      };

      const layout = service.createLayout('Test', [panel]);
      const result = service.removePanel(layout.id, 'panel-1');

      expect(result).toBe(true);
      const updated = service.getLayout(layout.id);
      expect(updated?.panels).toHaveLength(0);
    });

    it('should update panel', () => {
      const panel: PanelConfig = {
        id: 'panel-1',
        type: 'sidebar',
        visible: true,
        position: { area: 'left', order: 0 },
        size: {},
        docked: true,
      };

      const layout = service.createLayout('Test', [panel]);
      const result = service.updatePanel(layout.id, 'panel-1', { visible: false });

      expect(result).toBe(true);
      const updated = service.getLayout(layout.id);
      expect(updated?.panels[0].visible).toBe(false);
    });

    it('should toggle panel visibility', () => {
      const panel: PanelConfig = {
        id: 'panel-1',
        type: 'sidebar',
        visible: true,
        position: { area: 'left', order: 0 },
        size: {},
        docked: true,
      };

      const layout = service.createLayout('Test', [panel]);
      service.togglePanelVisibility(layout.id, 'panel-1');

      const updated = service.getLayout(layout.id);
      expect(updated?.panels[0].visible).toBe(false);
    });
  });

  describe('Layout Export/Import', () => {
    it('should get layout for export', () => {
      const layout = service.createLayout('Export Test', []);
      const retrieved = service.getLayout(layout.id);

      expect(retrieved).toBeDefined();
      expect(retrieved?.name).toBe('Export Test');
      
      // Can export to JSON
      const json = JSON.stringify(retrieved);
      expect(json).toContain('Export Test');
    });

    it('should create layout from imported data', () => {
      const importedPanels: PanelConfig[] = [{
        id: 'panel-1',
        type: 'sidebar',
        visible: true,
        position: { area: 'left', order: 0 },
        size: {},
        docked: true,
      }];

      const layout = service.createLayout('Imported Layout', importedPanels);
      
      expect(layout).toBeDefined();
      expect(layout.name).toBe('Imported Layout');
      expect(layout.panels).toEqual(importedPanels);
    });
  });

  describe('Duplicate Layout', () => {
    it('should duplicate layout', () => {
      const original = service.createLayout('Original', []);
      const duplicate = service.duplicateLayout(original.id, 'Copy');

      expect(duplicate).toBeDefined();
      expect(duplicate?.name).toBe('Copy');
      expect(duplicate?.id).not.toBe(original.id);
    });
  });

  describe('Persistence', () => {
    it('should save layouts to file', () => {
      service.createLayout('Test', []);
      expect(mockFs.writeFileSync).toHaveBeenCalled();
    });

    it('should load layouts from file', () => {
      const mockData = {
        layouts: [{
          id: '1',
          name: 'Test Layout',
          panels: [],
          createdAt: Date.now(),
          lastModified: Date.now(),
        }],
        activeLayoutId: '1',
      };

      mockFs.existsSync.mockReturnValue(true);
      mockFs.readFileSync.mockReturnValue(JSON.stringify(mockData));

      const newService = new LayoutService();
      const layouts = newService.getAllLayouts();

      expect(layouts.length).toBe(1);
    });
  });
});
