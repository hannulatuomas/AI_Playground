/**
 * LayoutService - Customizable Panel Layout Management
 * 
 * Features:
 * - Save/restore panel layouts
 * - Drag-and-drop panel positioning
 * - Panel visibility management
 * - Layout presets (IDE-style, Browser-style, Custom)
 * - Multi-workspace support
 */

import * as fs from 'fs';
import * as path from 'path';
import { app } from 'electron';

export interface PanelConfig {
  id: string;
  type: 'sidebar' | 'main' | 'console' | 'properties' | 'tabs' | 'custom';
  visible: boolean;
  position: {
    area: 'left' | 'center' | 'right' | 'top' | 'bottom';
    order: number;
  };
  size: {
    width?: number;  // Percentage or pixels
    height?: number; // Percentage or pixels
    minWidth?: number;
    minHeight?: number;
    maxWidth?: number;
    maxHeight?: number;
  };
  docked: boolean;
  floating?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  content?: any;
}

export interface LayoutConfig {
  id: string;
  name: string;
  description?: string;
  panels: PanelConfig[];
  createdAt: number;
  lastModified: number;
  isDefault?: boolean;
}

export class LayoutService {
  private layouts: Map<string, LayoutConfig>;
  private activeLayoutId: string | null;
  private layoutsPath: string;

  constructor(dataPath?: string) {
    const userDataPath = app?.getPath('userData') || process.cwd();
    this.layoutsPath = dataPath || path.join(userDataPath, 'layouts.json');
    this.layouts = new Map();
    this.activeLayoutId = null;
    this.loadLayouts();
  }

  /**
   * Create a new layout
   */
  createLayout(name: string, panels: PanelConfig[], description?: string): LayoutConfig {
    const id = this.generateLayoutId();
    const layout: LayoutConfig = {
      id,
      name,
      description,
      panels,
      createdAt: Date.now(),
      lastModified: Date.now(),
    };

    this.layouts.set(id, layout);
    this.saveLayouts();
    return layout;
  }

  /**
   * Get layout by ID
   */
  getLayout(id: string): LayoutConfig | undefined {
    return this.layouts.get(id);
  }

  /**
   * Get all layouts
   */
  getAllLayouts(): LayoutConfig[] {
    return Array.from(this.layouts.values()).sort((a, b) => b.lastModified - a.lastModified);
  }

  /**
   * Update layout
   */
  updateLayout(id: string, updates: Partial<LayoutConfig>): boolean {
    const layout = this.layouts.get(id);
    if (!layout) return false;

    const updated: LayoutConfig = {
      ...layout,
      ...updates,
      lastModified: Date.now(),
    };

    this.layouts.set(id, updated);
    this.saveLayouts();
    return true;
  }

  /**
   * Delete layout
   */
  deleteLayout(id: string): boolean {
    if (!this.layouts.has(id)) return false;

    this.layouts.delete(id);
    
    if (this.activeLayoutId === id) {
      this.activeLayoutId = null;
    }

    this.saveLayouts();
    return true;
  }

  /**
   * Set active layout
   */
  setActiveLayout(id: string): boolean {
    if (!this.layouts.has(id)) return false;

    this.activeLayoutId = id;
    this.saveLayouts();
    return true;
  }

  /**
   * Get active layout
   */
  getActiveLayout(): LayoutConfig | null {
    return this.activeLayoutId ? this.layouts.get(this.activeLayoutId) || null : null;
  }

  /**
   * Update panel in layout
   */
  updatePanel(layoutId: string, panelId: string, updates: Partial<PanelConfig>): boolean {
    const layout = this.layouts.get(layoutId);
    if (!layout) return false;

    const panelIndex = layout.panels.findIndex(p => p.id === panelId);
    if (panelIndex === -1) return false;

    layout.panels[panelIndex] = {
      ...layout.panels[panelIndex],
      ...updates,
    };

    layout.lastModified = Date.now();
    this.saveLayouts();
    return true;
  }

  /**
   * Add panel to layout
   */
  addPanel(layoutId: string, panel: PanelConfig): boolean {
    const layout = this.layouts.get(layoutId);
    if (!layout) return false;

    layout.panels.push(panel);
    layout.lastModified = Date.now();
    this.saveLayouts();
    return true;
  }

  /**
   * Remove panel from layout
   */
  removePanel(layoutId: string, panelId: string): boolean {
    const layout = this.layouts.get(layoutId);
    if (!layout) return false;

    layout.panels = layout.panels.filter(p => p.id !== panelId);
    layout.lastModified = Date.now();
    this.saveLayouts();
    return true;
  }

  /**
   * Reorder panels in layout
   */
  reorderPanels(layoutId: string, panelIds: string[]): boolean {
    const layout = this.layouts.get(layoutId);
    if (!layout) return false;

    const panelMap = new Map(layout.panels.map(p => [p.id, p]));
    const reordered: PanelConfig[] = [];

    panelIds.forEach((id, index) => {
      const panel = panelMap.get(id);
      if (panel) {
        panel.position.order = index;
        reordered.push(panel);
      }
    });

    layout.panels = reordered;
    layout.lastModified = Date.now();
    this.saveLayouts();
    return true;
  }

  /**
   * Toggle panel visibility
   */
  togglePanelVisibility(layoutId: string, panelId: string): boolean {
    const layout = this.layouts.get(layoutId);
    if (!layout) return false;

    const panel = layout.panels.find(p => p.id === panelId);
    if (!panel) return false;

    panel.visible = !panel.visible;
    layout.lastModified = Date.now();
    this.saveLayouts();
    return true;
  }

  /**
   * Create default layouts
   */
  createDefaultLayouts(): void {
    // IDE-style layout
    const ideLayout = this.createLayout(
      'IDE Style',
      [
        {
          id: 'sidebar-left',
          type: 'sidebar',
          visible: true,
          position: { area: 'left', order: 0 },
          size: { width: 20, minWidth: 200 },
          docked: true,
        },
        {
          id: 'main-editor',
          type: 'main',
          visible: true,
          position: { area: 'center', order: 0 },
          size: { width: 60 },
          docked: true,
        },
        {
          id: 'properties-right',
          type: 'properties',
          visible: true,
          position: { area: 'right', order: 0 },
          size: { width: 20, minWidth: 200 },
          docked: true,
        },
        {
          id: 'console-bottom',
          type: 'console',
          visible: true,
          position: { area: 'bottom', order: 0 },
          size: { height: 30, minHeight: 150 },
          docked: true,
        },
      ],
      'Classic IDE layout with sidebar, editor, properties, and console'
    );
    ideLayout.isDefault = true;

    // Browser-style layout
    const browserLayout = this.createLayout(
      'Browser Style',
      [
        {
          id: 'tabs-top',
          type: 'tabs',
          visible: true,
          position: { area: 'top', order: 0 },
          size: { height: 40 },
          docked: true,
        },
        {
          id: 'sidebar-left',
          type: 'sidebar',
          visible: true,
          position: { area: 'left', order: 0 },
          size: { width: 15, minWidth: 200 },
          docked: true,
        },
        {
          id: 'main-content',
          type: 'main',
          visible: true,
          position: { area: 'center', order: 0 },
          size: { width: 85 },
          docked: true,
        },
      ],
      'Browser-style layout with top tabs and sidebar'
    );

    // Minimal layout
    const minimalLayout = this.createLayout(
      'Minimal',
      [
        {
          id: 'main-only',
          type: 'main',
          visible: true,
          position: { area: 'center', order: 0 },
          size: { width: 100 },
          docked: true,
        },
      ],
      'Minimal layout with only the main content area'
    );

    // Focus layout
    const focusLayout = this.createLayout(
      'Focus Mode',
      [
        {
          id: 'tabs-compact',
          type: 'tabs',
          visible: true,
          position: { area: 'top', order: 0 },
          size: { height: 35 },
          docked: true,
        },
        {
          id: 'main-fullwidth',
          type: 'main',
          visible: true,
          position: { area: 'center', order: 0 },
          size: { width: 100 },
          docked: true,
        },
      ],
      'Distraction-free focus mode with tabs and main content'
    );
  }

  /**
   * Export layout to file
   */
  exportLayout(layoutId: string, filePath: string): void {
    const layout = this.layouts.get(layoutId);
    if (!layout) {
      throw new Error('Layout not found');
    }

    fs.writeFileSync(filePath, JSON.stringify(layout, null, 2));
  }

  /**
   * Import layout from file
   */
  importLayout(filePath: string): LayoutConfig {
    const data = fs.readFileSync(filePath, 'utf-8');
    const layout = JSON.parse(data) as LayoutConfig;

    // Generate new ID to avoid conflicts
    layout.id = this.generateLayoutId();
    layout.lastModified = Date.now();

    this.layouts.set(layout.id, layout);
    this.saveLayouts();

    return layout;
  }

  /**
   * Duplicate layout
   */
  duplicateLayout(layoutId: string, newName: string): LayoutConfig | null {
    const layout = this.layouts.get(layoutId);
    if (!layout) return null;

    const duplicate: LayoutConfig = {
      ...layout,
      id: this.generateLayoutId(),
      name: newName,
      createdAt: Date.now(),
      lastModified: Date.now(),
      isDefault: false,
    };

    this.layouts.set(duplicate.id, duplicate);
    this.saveLayouts();

    return duplicate;
  }

  /**
   * Reset layout to default
   */
  resetToDefault(layoutId: string): boolean {
    const layout = this.layouts.get(layoutId);
    if (!layout || !layout.isDefault) return false;

    // Would need to store original default state
    // For now, just recreate defaults
    this.createDefaultLayouts();
    return true;
  }

  /**
   * Save layouts to file
   */
  private saveLayouts(): void {
    try {
      const dir = path.dirname(this.layoutsPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      const data = {
        activeLayoutId: this.activeLayoutId,
        layouts: this.getAllLayouts(),
      };

      fs.writeFileSync(this.layoutsPath, JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('Error saving layouts:', error);
    }
  }

  /**
   * Load layouts from file
   */
  private loadLayouts(): void {
    try {
      if (fs.existsSync(this.layoutsPath)) {
        const data = JSON.parse(fs.readFileSync(this.layoutsPath, 'utf-8'));

        if (data.layouts) {
          data.layouts.forEach((layout: LayoutConfig) => {
            this.layouts.set(layout.id, layout);
          });
        }

        if (data.activeLayoutId) {
          this.activeLayoutId = data.activeLayoutId;
        }
      } else {
        // Create default layouts on first run
        this.createDefaultLayouts();
      }
    } catch (error) {
      console.error('Error loading layouts:', error);
      // Create defaults on error
      this.createDefaultLayouts();
    }
  }

  /**
   * Generate unique layout ID
   */
  private generateLayoutId(): string {
    return `layout-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}
