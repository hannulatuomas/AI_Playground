/**
 * SettingsService - Comprehensive Application Settings Management
 * 
 * Manages all application settings including:
 * - Network settings (proxy, timeout, SSL)
 * - Editor settings (theme, font, indentation)
 * - Keyboard shortcuts
 * - Language/locale
 * - Cache settings
 * - Auto-save
 * - Privacy settings
 * - Plugin management
 * - Backup/restore
 */

import * as fs from 'fs';
import * as path from 'path';
import { app } from 'electron';

export interface NetworkSettings {
  proxy?: {
    enabled: boolean;
    host: string;
    port: number;
    username?: string;
    password?: string;
  };
  timeout: number;
  ssl: {
    rejectUnauthorized: boolean;
    certificatePath?: string;
  };
  maxRedirects: number;
  followRedirects: boolean;
}

export interface EditorSettings {
  theme: 'light' | 'dark' | 'auto';
  fontSize: number;
  fontFamily: string;
  lineHeight: number;
  tabSize: number;
  insertSpaces: boolean;
  wordWrap: 'on' | 'off' | 'wordWrapColumn';
  lineNumbers: boolean;
  minimap: boolean;
}

export interface KeyboardShortcut {
  action: string;
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  meta?: boolean;
}

export interface LanguageSettings {
  locale: string;
  dateFormat: string;
  timeFormat: string;
  numberFormat: string;
}

export interface CacheSettings {
  enabled: boolean;
  maxSize: number;
  ttl: number;
  location: string;
}

export interface AutoSaveSettings {
  enabled: boolean;
  interval: number;
  saveOnFocus: boolean;
  saveOnWindowChange: boolean;
}

export interface PrivacySettings {
  telemetry: boolean;
  crashReports: boolean;
  analytics: boolean;
  shareUsageData: boolean;
}

export interface PluginSettings {
  enabled: boolean;
  autoUpdate: boolean;
  allowedSources: string[];
  trustedPlugins: string[];
}

export interface BackupSettings {
  enabled: boolean;
  interval: number;
  maxBackups: number;
  location: string;
  includeData: boolean;
  includeSettings: boolean;
}

export interface ApplicationSettings {
  network: NetworkSettings;
  editor: EditorSettings;
  shortcuts: KeyboardShortcut[];
  language: LanguageSettings;
  cache: CacheSettings;
  autoSave: AutoSaveSettings;
  privacy: PrivacySettings;
  plugins: PluginSettings;
  backup: BackupSettings;
  version: string;
}

export class SettingsService {
  private settings: ApplicationSettings;
  private settingsPath: string;
  private backupPath: string;
  private autoSaveInterval?: NodeJS.Timeout;

  constructor(configPath?: string) {
    const userDataPath = app?.getPath('userData') || process.cwd();
    this.settingsPath = configPath || path.join(userDataPath, 'settings.json');
    this.backupPath = path.join(userDataPath, 'backups');
    this.settings = this.getDefaultSettings();
    this.loadSettings();
    this.startAutoSave();
  }

  /**
   * Get default settings
   */
  private getDefaultSettings(): ApplicationSettings {
    return {
      network: {
        timeout: 30000,
        ssl: {
          rejectUnauthorized: true,
        },
        maxRedirects: 5,
        followRedirects: true,
      },
      editor: {
        theme: 'dark',
        fontSize: 14,
        fontFamily: 'Consolas, Monaco, "Courier New", monospace',
        lineHeight: 1.5,
        tabSize: 2,
        insertSpaces: true,
        wordWrap: 'off',
        lineNumbers: true,
        minimap: true,
      },
      shortcuts: this.getDefaultShortcuts(),
      language: {
        locale: 'en-US',
        dateFormat: 'YYYY-MM-DD',
        timeFormat: 'HH:mm:ss',
        numberFormat: 'en-US',
      },
      cache: {
        enabled: true,
        maxSize: 100 * 1024 * 1024, // 100MB
        ttl: 3600000, // 1 hour
        location: path.join(app?.getPath('userData') || process.cwd(), 'cache'),
      },
      autoSave: {
        enabled: true,
        interval: 60000, // 1 minute
        saveOnFocus: true,
        saveOnWindowChange: true,
      },
      privacy: {
        telemetry: false,
        crashReports: true,
        analytics: false,
        shareUsageData: false,
      },
      plugins: {
        enabled: true,
        autoUpdate: false,
        allowedSources: [],
        trustedPlugins: [],
      },
      backup: {
        enabled: true,
        interval: 86400000, // 24 hours
        maxBackups: 10,
        location: this.backupPath,
        includeData: true,
        includeSettings: true,
      },
      version: '1.0.0',
    };
  }

  /**
   * Get default keyboard shortcuts
   */
  private getDefaultShortcuts(): KeyboardShortcut[] {
    return [
      { action: 'new-request', key: 'N', ctrl: true },
      { action: 'save', key: 'S', ctrl: true },
      { action: 'open', key: 'O', ctrl: true },
      { action: 'close-tab', key: 'W', ctrl: true },
      { action: 'send-request', key: 'Enter', ctrl: true },
      { action: 'find', key: 'F', ctrl: true },
      { action: 'replace', key: 'H', ctrl: true },
      { action: 'settings', key: ',', ctrl: true },
      { action: 'toggle-sidebar', key: 'B', ctrl: true },
      { action: 'focus-url', key: 'L', ctrl: true },
      { action: 'new-tab', key: 'T', ctrl: true },
      { action: 'next-tab', key: 'Tab', ctrl: true },
      { action: 'prev-tab', key: 'Tab', ctrl: true, shift: true },
      { action: 'copy', key: 'C', ctrl: true },
      { action: 'paste', key: 'V', ctrl: true },
      { action: 'cut', key: 'X', ctrl: true },
      { action: 'undo', key: 'Z', ctrl: true },
      { action: 'redo', key: 'Y', ctrl: true },
      { action: 'select-all', key: 'A', ctrl: true },
      { action: 'zoom-in', key: '+', ctrl: true },
      { action: 'zoom-out', key: '-', ctrl: true },
      { action: 'zoom-reset', key: '0', ctrl: true },
      { action: 'quit', key: 'Q', ctrl: true },
    ];
  }

  /**
   * Load settings from file
   */
  private loadSettings(): void {
    try {
      if (fs.existsSync(this.settingsPath)) {
        const data = fs.readFileSync(this.settingsPath, 'utf-8');
        const loadedSettings = JSON.parse(data);
        this.settings = this.mergeSettings(this.settings, loadedSettings);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  }

  /**
   * Merge loaded settings with defaults
   */
  private mergeSettings(defaults: ApplicationSettings, loaded: Partial<ApplicationSettings>): ApplicationSettings {
    return {
      network: { ...defaults.network, ...loaded.network },
      editor: { ...defaults.editor, ...loaded.editor },
      shortcuts: loaded.shortcuts || defaults.shortcuts,
      language: { ...defaults.language, ...loaded.language },
      cache: { ...defaults.cache, ...loaded.cache },
      autoSave: { ...defaults.autoSave, ...loaded.autoSave },
      privacy: { ...defaults.privacy, ...loaded.privacy },
      plugins: { ...defaults.plugins, ...loaded.plugins },
      backup: { ...defaults.backup, ...loaded.backup },
      version: loaded.version || defaults.version,
    };
  }

  /**
   * Save settings to file
   */
  saveSettings(): void {
    try {
      const dir = path.dirname(this.settingsPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(this.settingsPath, JSON.stringify(this.settings, null, 2));
    } catch (error) {
      console.error('Error saving settings:', error);
      throw error;
    }
  }

  /**
   * Get all settings
   */
  getAllSettings(): ApplicationSettings {
    return JSON.parse(JSON.stringify(this.settings));
  }

  /**
   * Get network settings
   */
  getNetworkSettings(): NetworkSettings {
    return JSON.parse(JSON.stringify(this.settings.network));
  }

  /**
   * Update network settings
   */
  updateNetworkSettings(settings: Partial<NetworkSettings>): void {
    this.settings.network = { ...this.settings.network, ...settings };
    this.saveSettings();
  }

  /**
   * Get editor settings
   */
  getEditorSettings(): EditorSettings {
    return JSON.parse(JSON.stringify(this.settings.editor));
  }

  /**
   * Update editor settings
   */
  updateEditorSettings(settings: Partial<EditorSettings>): void {
    this.settings.editor = { ...this.settings.editor, ...settings };
    this.saveSettings();
  }

  /**
   * Get keyboard shortcuts
   */
  getShortcuts(): KeyboardShortcut[] {
    return JSON.parse(JSON.stringify(this.settings.shortcuts));
  }

  /**
   * Update keyboard shortcuts
   */
  updateShortcuts(shortcuts: KeyboardShortcut[]): void {
    this.settings.shortcuts = shortcuts;
    this.saveSettings();
  }

  /**
   * Get language settings
   */
  getLanguageSettings(): LanguageSettings {
    return JSON.parse(JSON.stringify(this.settings.language));
  }

  /**
   * Update language settings
   */
  updateLanguageSettings(settings: Partial<LanguageSettings>): void {
    this.settings.language = { ...this.settings.language, ...settings };
    this.saveSettings();
  }

  /**
   * Get cache settings
   */
  getCacheSettings(): CacheSettings {
    return JSON.parse(JSON.stringify(this.settings.cache));
  }

  /**
   * Update cache settings
   */
  updateCacheSettings(settings: Partial<CacheSettings>): void {
    this.settings.cache = { ...this.settings.cache, ...settings };
    this.saveSettings();
  }

  /**
   * Get auto-save settings
   */
  getAutoSaveSettings(): AutoSaveSettings {
    return JSON.parse(JSON.stringify(this.settings.autoSave));
  }

  /**
   * Update auto-save settings
   */
  updateAutoSaveSettings(settings: Partial<AutoSaveSettings>): void {
    this.settings.autoSave = { ...this.settings.autoSave, ...settings };
    this.saveSettings();
    this.restartAutoSave();
  }

  /**
   * Get privacy settings
   */
  getPrivacySettings(): PrivacySettings {
    return JSON.parse(JSON.stringify(this.settings.privacy));
  }

  /**
   * Update privacy settings
   */
  updatePrivacySettings(settings: Partial<PrivacySettings>): void {
    this.settings.privacy = { ...this.settings.privacy, ...settings };
    this.saveSettings();
  }

  /**
   * Get plugin settings
   */
  getPluginSettings(): PluginSettings {
    return JSON.parse(JSON.stringify(this.settings.plugins));
  }

  /**
   * Update plugin settings
   */
  updatePluginSettings(settings: Partial<PluginSettings>): void {
    this.settings.plugins = { ...this.settings.plugins, ...settings };
    this.saveSettings();
  }

  /**
   * Get backup settings
   */
  getBackupSettings(): BackupSettings {
    return JSON.parse(JSON.stringify(this.settings.backup));
  }

  /**
   * Update backup settings
   */
  updateBackupSettings(settings: Partial<BackupSettings>): void {
    this.settings.backup = { ...this.settings.backup, ...settings };
    this.saveSettings();
  }

  /**
   * Export settings to file
   */
  exportSettings(filePath: string): void {
    try {
      fs.writeFileSync(filePath, JSON.stringify(this.settings, null, 2));
    } catch (error) {
      console.error('Error exporting settings:', error);
      throw error;
    }
  }

  /**
   * Import settings from file
   */
  importSettings(filePath: string): void {
    try {
      const data = fs.readFileSync(filePath, 'utf-8');
      const importedSettings = JSON.parse(data);
      this.settings = this.mergeSettings(this.getDefaultSettings(), importedSettings);
      this.saveSettings();
      this.restartAutoSave();
    } catch (error) {
      console.error('Error importing settings:', error);
      throw error;
    }
  }

  /**
   * Create backup
   */
  createBackup(): string {
    try {
      if (!fs.existsSync(this.backupPath)) {
        fs.mkdirSync(this.backupPath, { recursive: true });
      }

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const backupFile = path.join(this.backupPath, `backup-${timestamp}.json`);

      const backupData = {
        timestamp: new Date().toISOString(),
        settings: this.settings.backup.includeSettings ? this.settings : null,
        version: this.settings.version,
      };

      fs.writeFileSync(backupFile, JSON.stringify(backupData, null, 2));

      // Clean old backups
      this.cleanOldBackups();

      return backupFile;
    } catch (error) {
      console.error('Error creating backup:', error);
      throw error;
    }
  }

  /**
   * Restore from backup
   */
  restoreBackup(backupFile: string): void {
    try {
      const data = fs.readFileSync(backupFile, 'utf-8');
      const backupData = JSON.parse(data);

      if (backupData.settings) {
        this.settings = this.mergeSettings(this.getDefaultSettings(), backupData.settings);
        this.saveSettings();
        this.restartAutoSave();
      }
    } catch (error) {
      console.error('Error restoring backup:', error);
      throw error;
    }
  }

  /**
   * Get list of backups
   */
  listBackups(): Array<{ file: string; timestamp: string; size: number }> {
    try {
      if (!fs.existsSync(this.backupPath)) {
        return [];
      }

      const files = fs.readdirSync(this.backupPath);
      return files
        .filter(file => file.startsWith('backup-') && file.endsWith('.json'))
        .map(file => {
          const filePath = path.join(this.backupPath, file);
          const stats = fs.statSync(filePath);
          return {
            file: filePath,
            timestamp: stats.mtime.toISOString(),
            size: stats.size,
          };
        })
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    } catch (error) {
      console.error('Error listing backups:', error);
      return [];
    }
  }

  /**
   * Clean old backups
   */
  private cleanOldBackups(): void {
    try {
      const backups = this.listBackups();
      if (backups.length > this.settings.backup.maxBackups) {
        const toDelete = backups.slice(this.settings.backup.maxBackups);
        toDelete.forEach(backup => {
          try {
            fs.unlinkSync(backup.file);
          } catch (error) {
            console.error('Error deleting old backup:', error);
          }
        });
      }
    } catch (error) {
      console.error('Error cleaning old backups:', error);
    }
  }

  /**
   * Reset to default settings
   */
  resetToDefaults(): void {
    this.settings = this.getDefaultSettings();
    this.saveSettings();
    this.restartAutoSave();
  }

  /**
   * Start auto-save
   */
  private startAutoSave(): void {
    if (this.settings.autoSave.enabled && this.settings.autoSave.interval > 0) {
      this.autoSaveInterval = setInterval(() => {
        this.saveSettings();
      }, this.settings.autoSave.interval);
    }
  }

  /**
   * Restart auto-save
   */
  private restartAutoSave(): void {
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
      this.autoSaveInterval = undefined;
    }
    this.startAutoSave();
  }

  /**
   * Stop auto-save
   */
  stopAutoSave(): void {
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
      this.autoSaveInterval = undefined;
    }
  }

  /**
   * Validate settings
   */
  validateSettings(settings: Partial<ApplicationSettings>): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (settings.network) {
      if (settings.network.timeout && settings.network.timeout < 1000) {
        errors.push('Network timeout must be at least 1000ms');
      }
      if (settings.network.maxRedirects && settings.network.maxRedirects < 0) {
        errors.push('Max redirects cannot be negative');
      }
    }

    if (settings.editor) {
      if (settings.editor.fontSize && (settings.editor.fontSize < 8 || settings.editor.fontSize > 72)) {
        errors.push('Font size must be between 8 and 72');
      }
      if (settings.editor.tabSize && (settings.editor.tabSize < 1 || settings.editor.tabSize > 8)) {
        errors.push('Tab size must be between 1 and 8');
      }
    }

    if (settings.cache) {
      if (settings.cache.maxSize && settings.cache.maxSize < 0) {
        errors.push('Cache max size cannot be negative');
      }
      if (settings.cache.ttl && settings.cache.ttl < 0) {
        errors.push('Cache TTL cannot be negative');
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}
