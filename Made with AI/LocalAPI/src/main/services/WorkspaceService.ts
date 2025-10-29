// Workspace Service for LocalAPI
// Handles workspace save/load, templates, snapshots, and auto-save

import * as fs from 'fs';
import * as path from 'path';
import { app } from 'electron';
import type {
  Workspace,
  WorkspaceSnapshot,
  WorkspaceTemplate,
  WorkspaceMetadata,
  Collection,
  Environment,
  Variable,
  Settings,
} from '../../types/models';

export class WorkspaceService {
  private workspacesDir: string;
  private templatesDir: string;
  private snapshotsDir: string;
  private currentWorkspace: Workspace | null = null;
  private autoSaveTimer: NodeJS.Timeout | null = null;
  private isDirty: boolean = false;

  constructor() {
    const userDataPath = app.getPath('userData');
    this.workspacesDir = path.join(userDataPath, 'workspaces');
    this.templatesDir = path.join(userDataPath, 'templates');
    this.snapshotsDir = path.join(userDataPath, 'snapshots');

    // Ensure directories exist
    this.ensureDirectories();
  }

  /**
   * Ensure all required directories exist
   */
  private ensureDirectories(): void {
    [this.workspacesDir, this.templatesDir, this.snapshotsDir].forEach((dir) => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  }

  /**
   * Create a new workspace
   */
  createWorkspace(name: string, description?: string): Workspace {
    const workspace: Workspace = {
      id: this.generateId(),
      name,
      description,
      collections: [],
      environments: [],
      globalVariables: [],
      settings: this.getDefaultSettings(),
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.currentWorkspace = workspace;
    this.markDirty();
    return workspace;
  }

  /**
   * Save workspace to file
   */
  async saveWorkspace(workspace?: Workspace): Promise<string> {
    const ws = workspace || this.currentWorkspace;
    if (!ws) {
      throw new Error('No workspace to save');
    }

    ws.updatedAt = new Date();
    const filePath = path.join(this.workspacesDir, `${ws.id}.json`);
    
    await fs.promises.writeFile(
      filePath,
      JSON.stringify(ws, null, 2),
      'utf-8'
    );

    this.isDirty = false;
    return filePath;
  }

  /**
   * Load workspace from file
   */
  async loadWorkspace(workspaceId: string): Promise<Workspace> {
    const filePath = path.join(this.workspacesDir, `${workspaceId}.json`);
    
    if (!fs.existsSync(filePath)) {
      throw new Error(`Workspace not found: ${workspaceId}`);
    }

    const data = await fs.promises.readFile(filePath, 'utf-8');
    const workspace = JSON.parse(data) as Workspace;
    
    // Convert date strings back to Date objects
    workspace.createdAt = new Date(workspace.createdAt);
    workspace.updatedAt = new Date(workspace.updatedAt);
    if (workspace.lastOpenedAt) {
      workspace.lastOpenedAt = new Date(workspace.lastOpenedAt);
    }

    workspace.lastOpenedAt = new Date();
    this.currentWorkspace = workspace;
    
    // Save the updated lastOpenedAt
    await this.saveWorkspace(workspace);
    
    // Start auto-save if enabled
    if (workspace.settings.autoSave) {
      this.startAutoSave(workspace.settings.autoSaveInterval);
    }

    return workspace;
  }

  /**
   * Get current workspace
   */
  getCurrentWorkspace(): Workspace | null {
    return this.currentWorkspace;
  }

  /**
   * Update current workspace
   */
  updateWorkspace(updates: Partial<Workspace>): void {
    if (!this.currentWorkspace) {
      throw new Error('No current workspace');
    }

    Object.assign(this.currentWorkspace, updates);
    this.markDirty();
  }

  /**
   * Delete workspace
   */
  async deleteWorkspace(workspaceId: string): Promise<void> {
    const filePath = path.join(this.workspacesDir, `${workspaceId}.json`);
    
    if (fs.existsSync(filePath)) {
      await fs.promises.unlink(filePath);
    }

    // Delete associated snapshots
    const snapshots = await this.listSnapshots(workspaceId);
    for (const snapshot of snapshots) {
      await this.deleteSnapshot(snapshot.id);
    }

    if (this.currentWorkspace?.id === workspaceId) {
      this.currentWorkspace = null;
      this.stopAutoSave();
    }
  }

  /**
   * List all workspaces
   */
  async listWorkspaces(): Promise<WorkspaceMetadata[]> {
    const files = await fs.promises.readdir(this.workspacesDir);
    const workspaces: WorkspaceMetadata[] = [];

    for (const file of files) {
      if (file.endsWith('.json')) {
        try {
          const filePath = path.join(this.workspacesDir, file);
          const data = await fs.promises.readFile(filePath, 'utf-8');
          const workspace = JSON.parse(data) as Workspace;

          workspaces.push({
            id: workspace.id,
            name: workspace.name,
            description: workspace.description,
            path: filePath,
            lastOpenedAt: workspace.lastOpenedAt || workspace.updatedAt,
            createdAt: workspace.createdAt,
            updatedAt: workspace.updatedAt,
          });
        } catch (error) {
          console.error(`Failed to read workspace ${file}:`, error);
        }
      }
    }

    // Sort by lastOpenedAt descending
    return workspaces.sort((a, b) => 
      new Date(b.lastOpenedAt).getTime() - new Date(a.lastOpenedAt).getTime()
    );
  }

  /**
   * Get recent workspaces (last 10)
   */
  async getRecentWorkspaces(): Promise<WorkspaceMetadata[]> {
    const all = await this.listWorkspaces();
    return all.slice(0, 10);
  }

  /**
   * Export workspace to file
   */
  async exportWorkspace(workspaceId: string, exportPath: string): Promise<void> {
    const filePath = path.join(this.workspacesDir, `${workspaceId}.json`);
    
    if (!fs.existsSync(filePath)) {
      throw new Error(`Workspace not found: ${workspaceId}`);
    }

    await fs.promises.copyFile(filePath, exportPath);
  }

  /**
   * Import workspace from file
   */
  async importWorkspace(importPath: string): Promise<Workspace> {
    if (!fs.existsSync(importPath)) {
      throw new Error(`File not found: ${importPath}`);
    }

    const data = await fs.promises.readFile(importPath, 'utf-8');
    const workspace = JSON.parse(data) as Workspace;

    // Generate new ID to avoid conflicts
    workspace.id = this.generateId();
    workspace.createdAt = new Date();
    workspace.updatedAt = new Date();
    workspace.lastOpenedAt = new Date();

    // Save the imported workspace
    await this.saveWorkspace(workspace);

    return workspace;
  }

  /**
   * Create snapshot of current workspace
   */
  async createSnapshot(name: string, description?: string): Promise<WorkspaceSnapshot> {
    if (!this.currentWorkspace) {
      throw new Error('No current workspace');
    }

    const snapshot: WorkspaceSnapshot = {
      id: this.generateId(),
      workspaceId: this.currentWorkspace.id,
      name,
      description,
      workspace: JSON.parse(JSON.stringify(this.currentWorkspace)), // Deep clone
      createdAt: new Date(),
    };

    const filePath = path.join(this.snapshotsDir, `${snapshot.id}.json`);
    await fs.promises.writeFile(
      filePath,
      JSON.stringify(snapshot, null, 2),
      'utf-8'
    );

    return snapshot;
  }

  /**
   * Restore workspace from snapshot
   */
  async restoreSnapshot(snapshotId: string): Promise<Workspace> {
    const filePath = path.join(this.snapshotsDir, `${snapshotId}.json`);
    
    if (!fs.existsSync(filePath)) {
      throw new Error(`Snapshot not found: ${snapshotId}`);
    }

    const data = await fs.promises.readFile(filePath, 'utf-8');
    const snapshot = JSON.parse(data) as WorkspaceSnapshot;

    // Restore the workspace
    const workspace = snapshot.workspace;
    workspace.updatedAt = new Date();
    
    this.currentWorkspace = workspace;
    await this.saveWorkspace(workspace);

    return workspace;
  }

  /**
   * List snapshots for a workspace
   */
  async listSnapshots(workspaceId: string): Promise<WorkspaceSnapshot[]> {
    const files = await fs.promises.readdir(this.snapshotsDir);
    const snapshots: WorkspaceSnapshot[] = [];

    for (const file of files) {
      if (file.endsWith('.json')) {
        try {
          const filePath = path.join(this.snapshotsDir, file);
          const data = await fs.promises.readFile(filePath, 'utf-8');
          const snapshot = JSON.parse(data) as WorkspaceSnapshot;

          if (snapshot.workspaceId === workspaceId) {
            snapshots.push(snapshot);
          }
        } catch (error) {
          console.error(`Failed to read snapshot ${file}:`, error);
        }
      }
    }

    // Sort by createdAt descending
    return snapshots.sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  }

  /**
   * Delete snapshot
   */
  async deleteSnapshot(snapshotId: string): Promise<void> {
    const filePath = path.join(this.snapshotsDir, `${snapshotId}.json`);
    
    if (fs.existsSync(filePath)) {
      await fs.promises.unlink(filePath);
    }
  }

  /**
   * Save workspace as template
   */
  async saveAsTemplate(name: string, description?: string, tags?: string[]): Promise<WorkspaceTemplate> {
    if (!this.currentWorkspace) {
      throw new Error('No current workspace');
    }

    const { id, createdAt, updatedAt, lastOpenedAt, ...workspaceData } = this.currentWorkspace;

    const template: WorkspaceTemplate = {
      id: this.generateId(),
      name,
      description,
      workspace: workspaceData,
      tags,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    const filePath = path.join(this.templatesDir, `${template.id}.json`);
    await fs.promises.writeFile(
      filePath,
      JSON.stringify(template, null, 2),
      'utf-8'
    );

    return template;
  }

  /**
   * Load workspace from template
   */
  async loadFromTemplate(templateId: string, workspaceName: string): Promise<Workspace> {
    const filePath = path.join(this.templatesDir, `${templateId}.json`);
    
    if (!fs.existsSync(filePath)) {
      throw new Error(`Template not found: ${templateId}`);
    }

    const data = await fs.promises.readFile(filePath, 'utf-8');
    const template = JSON.parse(data) as WorkspaceTemplate;

    // Create new workspace from template
    const workspace: Workspace = {
      ...template.workspace,
      id: this.generateId(),
      name: workspaceName,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.currentWorkspace = workspace;
    await this.saveWorkspace(workspace);

    return workspace;
  }

  /**
   * List all templates
   */
  async listTemplates(): Promise<WorkspaceTemplate[]> {
    const files = await fs.promises.readdir(this.templatesDir);
    const templates: WorkspaceTemplate[] = [];

    for (const file of files) {
      if (file.endsWith('.json')) {
        try {
          const filePath = path.join(this.templatesDir, file);
          const data = await fs.promises.readFile(filePath, 'utf-8');
          const template = JSON.parse(data) as WorkspaceTemplate;
          templates.push(template);
        } catch (error) {
          console.error(`Failed to read template ${file}:`, error);
        }
      }
    }

    return templates.sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  }

  /**
   * Delete template
   */
  async deleteTemplate(templateId: string): Promise<void> {
    const filePath = path.join(this.templatesDir, `${templateId}.json`);
    
    if (fs.existsSync(filePath)) {
      await fs.promises.unlink(filePath);
    }
  }

  /**
   * Start auto-save
   */
  startAutoSave(intervalSeconds: number = 300): void {
    this.stopAutoSave();

    this.autoSaveTimer = setInterval(async () => {
      if (this.isDirty && this.currentWorkspace) {
        try {
          await this.saveWorkspace();
          console.log('Auto-saved workspace:', this.currentWorkspace.name);
        } catch (error) {
          console.error('Auto-save failed:', error);
        }
      }
    }, intervalSeconds * 1000);
  }

  /**
   * Stop auto-save
   */
  stopAutoSave(): void {
    if (this.autoSaveTimer) {
      clearInterval(this.autoSaveTimer);
      this.autoSaveTimer = null;
    }
  }

  /**
   * Mark workspace as dirty (needs save)
   */
  markDirty(): void {
    this.isDirty = true;
  }

  /**
   * Check if workspace has unsaved changes
   */
  isDirtyWorkspace(): boolean {
    return this.isDirty;
  }

  /**
   * Backup workspace to a specific location
   */
  async backupWorkspace(workspaceId: string, backupPath: string): Promise<void> {
    const filePath = path.join(this.workspacesDir, `${workspaceId}.json`);
    
    if (!fs.existsSync(filePath)) {
      throw new Error(`Workspace not found: ${workspaceId}`);
    }

    // Ensure backup directory exists
    const backupDir = path.dirname(backupPath);
    if (!fs.existsSync(backupDir)) {
      fs.mkdirSync(backupDir, { recursive: true });
    }

    await fs.promises.copyFile(filePath, backupPath);
  }

  /**
   * Restore workspace from backup
   */
  async restoreFromBackup(backupPath: string): Promise<Workspace> {
    return this.importWorkspace(backupPath);
  }

  /**
   * Get default settings
   */
  private getDefaultSettings(): Settings {
    return {
      theme: 'light',
      requestTimeout: 30000,
      followRedirects: true,
      validateSSL: true,
      proxyEnabled: false,
      maxResponseSize: 10485760, // 10MB
      autoSave: true,
      autoSaveInterval: 300, // 5 minutes
      editorFontSize: 14,
      editorTheme: 'vs-dark',
    };
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Cleanup on service shutdown
   */
  cleanup(): void {
    this.stopAutoSave();
  }
}

// Singleton instance
let instance: WorkspaceService | null = null;

export function getWorkspaceService(): WorkspaceService {
  if (!instance) {
    instance = new WorkspaceService();
  }
  return instance;
}
