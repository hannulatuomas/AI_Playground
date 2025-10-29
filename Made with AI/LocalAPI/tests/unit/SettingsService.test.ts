/**
 * SettingsService Comprehensive Unit Tests
 * 
 * Tests all settings functionality:
 * - Network settings
 * - Editor settings
 * - Keyboard shortcuts
 * - Language/locale
 * - Cache settings
 * - Auto-save
 * - Privacy
 * - Plugin management
 * - Backup/restore
 * - Import/export
 * - Reset to defaults
 * - Validation
 */

import { SettingsService } from '../../src/main/services/SettingsService';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

// Mock electron
jest.mock('electron', () => ({
  app: {
    getPath: () => path.join(os.tmpdir(), 'localapi-test'),
  },
}));

describe('SettingsService', () => {
  let service: SettingsService;
  let tempDir: string;
  let settingsPath: string;

  beforeEach(() => {
    tempDir = path.join(os.tmpdir(), 'localapi-test-' + Date.now());
    settingsPath = path.join(tempDir, 'settings.json');
    
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }

    service = new SettingsService(settingsPath);
  });

  afterEach(() => {
    service.stopAutoSave();
    if (fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });

  describe('Initialization', () => {
    it('should create service with default settings', () => {
      const settings = service.getAllSettings();
      
      expect(settings).toBeDefined();
      expect(settings.network).toBeDefined();
      expect(settings.editor).toBeDefined();
      expect(settings.shortcuts).toBeDefined();
      expect(settings.language).toBeDefined();
      expect(settings.cache).toBeDefined();
      expect(settings.autoSave).toBeDefined();
      expect(settings.privacy).toBeDefined();
      expect(settings.plugins).toBeDefined();
      expect(settings.backup).toBeDefined();
    });

    it('should have correct default values', () => {
      const settings = service.getAllSettings();
      
      expect(settings.network.timeout).toBe(30000);
      expect(settings.editor.theme).toBe('dark');
      expect(settings.editor.fontSize).toBe(14);
      expect(settings.language.locale).toBe('en-US');
      expect(settings.cache.enabled).toBe(true);
      expect(settings.autoSave.enabled).toBe(true);
      expect(settings.privacy.telemetry).toBe(false);
      expect(settings.plugins.enabled).toBe(true);
      expect(settings.backup.enabled).toBe(true);
    });

    it('should load existing settings file', () => {
      const customSettings = {
        network: { timeout: 60000 },
        editor: { theme: 'light' },
      };
      
      fs.writeFileSync(settingsPath, JSON.stringify(customSettings));
      
      const newService = new SettingsService(settingsPath);
      const settings = newService.getAllSettings();
      
      expect(settings.network.timeout).toBe(60000);
      expect(settings.editor.theme).toBe('light');
      
      newService.stopAutoSave();
    });
  });

  describe('Network Settings', () => {
    it('should get network settings', () => {
      const network = service.getNetworkSettings();
      
      expect(network.timeout).toBe(30000);
      expect(network.ssl.rejectUnauthorized).toBe(true);
      expect(network.maxRedirects).toBe(5);
      expect(network.followRedirects).toBe(true);
    });

    it('should update network settings', () => {
      service.updateNetworkSettings({
        timeout: 60000,
        maxRedirects: 10,
      });
      
      const network = service.getNetworkSettings();
      expect(network.timeout).toBe(60000);
      expect(network.maxRedirects).toBe(10);
    });

    it('should support proxy configuration', () => {
      service.updateNetworkSettings({
        proxy: {
          enabled: true,
          host: 'proxy.example.com',
          port: 8080,
        },
      });
      
      const network = service.getNetworkSettings();
      expect(network.proxy?.enabled).toBe(true);
      expect(network.proxy?.host).toBe('proxy.example.com');
      expect(network.proxy?.port).toBe(8080);
    });

    it('should support SSL configuration', () => {
      service.updateNetworkSettings({
        ssl: {
          rejectUnauthorized: false,
          certificatePath: '/path/to/cert.pem',
        },
      });
      
      const network = service.getNetworkSettings();
      expect(network.ssl.rejectUnauthorized).toBe(false);
      expect(network.ssl.certificatePath).toBe('/path/to/cert.pem');
    });
  });

  describe('Editor Settings', () => {
    it('should get editor settings', () => {
      const editor = service.getEditorSettings();
      
      expect(editor.theme).toBe('dark');
      expect(editor.fontSize).toBe(14);
      expect(editor.tabSize).toBe(2);
      expect(editor.insertSpaces).toBe(true);
      expect(editor.lineNumbers).toBe(true);
      expect(editor.minimap).toBe(true);
    });

    it('should update editor settings', () => {
      service.updateEditorSettings({
        theme: 'light',
        fontSize: 16,
        tabSize: 4,
      });
      
      const editor = service.getEditorSettings();
      expect(editor.theme).toBe('light');
      expect(editor.fontSize).toBe(16);
      expect(editor.tabSize).toBe(4);
    });

    it('should support font family customization', () => {
      service.updateEditorSettings({
        fontFamily: 'Fira Code, monospace',
      });
      
      const editor = service.getEditorSettings();
      expect(editor.fontFamily).toBe('Fira Code, monospace');
    });

    it('should support word wrap settings', () => {
      service.updateEditorSettings({
        wordWrap: 'on',
      });
      
      const editor = service.getEditorSettings();
      expect(editor.wordWrap).toBe('on');
    });
  });

  describe('Keyboard Shortcuts', () => {
    it('should get default shortcuts', () => {
      const shortcuts = service.getShortcuts();
      
      expect(shortcuts).toBeInstanceOf(Array);
      expect(shortcuts.length).toBeGreaterThan(0);
      expect(shortcuts[0]).toHaveProperty('action');
      expect(shortcuts[0]).toHaveProperty('key');
    });

    it('should update shortcuts', () => {
      const newShortcuts = [
        { action: 'test', key: 'T', ctrl: true },
      ];
      
      service.updateShortcuts(newShortcuts);
      const shortcuts = service.getShortcuts();
      
      expect(shortcuts).toEqual(newShortcuts);
    });

    it('should have common shortcuts defined', () => {
      const shortcuts = service.getShortcuts();
      const actions = shortcuts.map(s => s.action);
      
      expect(actions).toContain('save');
      expect(actions).toContain('open');
      expect(actions).toContain('send-request');
      expect(actions).toContain('settings');
    });
  });

  describe('Language Settings', () => {
    it('should get language settings', () => {
      const language = service.getLanguageSettings();
      
      expect(language.locale).toBe('en-US');
      expect(language.dateFormat).toBe('YYYY-MM-DD');
      expect(language.timeFormat).toBe('HH:mm:ss');
    });

    it('should update language settings', () => {
      service.updateLanguageSettings({
        locale: 'fi-FI',
        dateFormat: 'DD.MM.YYYY',
      });
      
      const language = service.getLanguageSettings();
      expect(language.locale).toBe('fi-FI');
      expect(language.dateFormat).toBe('DD.MM.YYYY');
    });
  });

  describe('Cache Settings', () => {
    it('should get cache settings', () => {
      const cache = service.getCacheSettings();
      
      expect(cache.enabled).toBe(true);
      expect(cache.maxSize).toBe(100 * 1024 * 1024);
      expect(cache.ttl).toBe(3600000);
    });

    it('should update cache settings', () => {
      service.updateCacheSettings({
        enabled: false,
        maxSize: 50 * 1024 * 1024,
        ttl: 1800000,
      });
      
      const cache = service.getCacheSettings();
      expect(cache.enabled).toBe(false);
      expect(cache.maxSize).toBe(50 * 1024 * 1024);
      expect(cache.ttl).toBe(1800000);
    });
  });

  describe('Auto-Save Settings', () => {
    it('should get auto-save settings', () => {
      const autoSave = service.getAutoSaveSettings();
      
      expect(autoSave.enabled).toBe(true);
      expect(autoSave.interval).toBe(60000);
      expect(autoSave.saveOnFocus).toBe(true);
      expect(autoSave.saveOnWindowChange).toBe(true);
    });

    it('should update auto-save settings', () => {
      service.updateAutoSaveSettings({
        enabled: false,
        interval: 120000,
      });
      
      const autoSave = service.getAutoSaveSettings();
      expect(autoSave.enabled).toBe(false);
      expect(autoSave.interval).toBe(120000);
    });
  });

  describe('Privacy Settings', () => {
    it('should get privacy settings', () => {
      const privacy = service.getPrivacySettings();
      
      expect(privacy.telemetry).toBe(false);
      expect(privacy.crashReports).toBe(true);
      expect(privacy.analytics).toBe(false);
      expect(privacy.shareUsageData).toBe(false);
    });

    it('should update privacy settings', () => {
      service.updatePrivacySettings({
        telemetry: true,
        analytics: true,
      });
      
      const privacy = service.getPrivacySettings();
      expect(privacy.telemetry).toBe(true);
      expect(privacy.analytics).toBe(true);
    });
  });

  describe('Plugin Settings', () => {
    it('should get plugin settings', () => {
      const plugins = service.getPluginSettings();
      
      expect(plugins.enabled).toBe(true);
      expect(plugins.autoUpdate).toBe(false);
      expect(plugins.allowedSources).toBeInstanceOf(Array);
      expect(plugins.trustedPlugins).toBeInstanceOf(Array);
    });

    it('should update plugin settings', () => {
      service.updatePluginSettings({
        enabled: false,
        autoUpdate: true,
        trustedPlugins: ['plugin1', 'plugin2'],
      });
      
      const plugins = service.getPluginSettings();
      expect(plugins.enabled).toBe(false);
      expect(plugins.autoUpdate).toBe(true);
      expect(plugins.trustedPlugins).toEqual(['plugin1', 'plugin2']);
    });
  });

  describe('Backup Settings', () => {
    it('should get backup settings', () => {
      const backup = service.getBackupSettings();
      
      expect(backup.enabled).toBe(true);
      expect(backup.interval).toBe(86400000);
      expect(backup.maxBackups).toBe(10);
      expect(backup.includeData).toBe(true);
      expect(backup.includeSettings).toBe(true);
    });

    it('should update backup settings', () => {
      service.updateBackupSettings({
        enabled: false,
        maxBackups: 5,
      });
      
      const backup = service.getBackupSettings();
      expect(backup.enabled).toBe(false);
      expect(backup.maxBackups).toBe(5);
    });
  });

  describe('Save and Load', () => {
    it('should save settings to file', () => {
      service.updateNetworkSettings({ timeout: 45000 });
      service.saveSettings();
      
      expect(fs.existsSync(settingsPath)).toBe(true);
      
      const data = JSON.parse(fs.readFileSync(settingsPath, 'utf-8'));
      expect(data.network.timeout).toBe(45000);
    });

    it('should persist settings across instances', () => {
      service.updateEditorSettings({ theme: 'light' });
      service.saveSettings();
      
      const newService = new SettingsService(settingsPath);
      const editor = newService.getEditorSettings();
      
      expect(editor.theme).toBe('light');
      
      newService.stopAutoSave();
    });
  });

  describe('Import and Export', () => {
    it('should export settings to file', () => {
      const exportPath = path.join(tempDir, 'exported-settings.json');
      service.exportSettings(exportPath);
      
      expect(fs.existsSync(exportPath)).toBe(true);
      
      const data = JSON.parse(fs.readFileSync(exportPath, 'utf-8'));
      expect(data.network).toBeDefined();
      expect(data.editor).toBeDefined();
    });

    it('should import settings from file', () => {
      const importPath = path.join(tempDir, 'import-settings.json');
      const importData = {
        network: { timeout: 90000 },
        editor: { theme: 'auto' },
      };
      
      fs.writeFileSync(importPath, JSON.stringify(importData));
      service.importSettings(importPath);
      
      const network = service.getNetworkSettings();
      const editor = service.getEditorSettings();
      
      expect(network.timeout).toBe(90000);
      expect(editor.theme).toBe('auto');
    });
  });

  describe('Backup and Restore', () => {
    it('should create backup', () => {
      const backupFile = service.createBackup();
      
      expect(backupFile).toBeTruthy();
      expect(fs.existsSync(backupFile)).toBe(true);
    });

    it('should list backups', () => {
      service.createBackup();
      service.createBackup();
      
      const backups = service.listBackups();
      expect(backups.length).toBeGreaterThanOrEqual(2);
      expect(backups[0]).toHaveProperty('file');
      expect(backups[0]).toHaveProperty('timestamp');
      expect(backups[0]).toHaveProperty('size');
    });

    it('should restore from backup', () => {
      service.updateNetworkSettings({ timeout: 99000 });
      service.saveSettings();
      
      const backupFile = service.createBackup();
      
      service.updateNetworkSettings({ timeout: 15000 });
      service.saveSettings();
      
      service.restoreBackup(backupFile);
      
      const network = service.getNetworkSettings();
      expect(network.timeout).toBe(99000);
    });

    it('should clean old backups when max is exceeded', () => {
      service.updateBackupSettings({ maxBackups: 3 });
      
      // Create more than max backups
      for (let i = 0; i < 5; i++) {
        service.createBackup();
      }
      
      const backups = service.listBackups();
      expect(backups.length).toBeLessThanOrEqual(3);
    });
  });

  describe('Reset to Defaults', () => {
    it('should reset all settings to defaults', () => {
      service.updateNetworkSettings({ timeout: 99000 });
      service.updateEditorSettings({ theme: 'light' });
      service.updateLanguageSettings({ locale: 'fi-FI' });
      
      service.resetToDefaults();
      
      const settings = service.getAllSettings();
      expect(settings.network.timeout).toBe(30000);
      expect(settings.editor.theme).toBe('dark');
      expect(settings.language.locale).toBe('en-US');
    });
  });

  describe('Validation', () => {
    it('should validate correct settings', () => {
      const result = service.validateSettings({
        network: { timeout: 5000 } as any,
        editor: { fontSize: 14, tabSize: 2 } as any,
      });
      
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject invalid network timeout', () => {
      const result = service.validateSettings({
        network: { timeout: 500 } as any,
      });
      
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Network timeout must be at least 1000ms');
    });

    it('should reject invalid font size', () => {
      const result = service.validateSettings({
        editor: { fontSize: 5 } as any,
      });
      
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Font size must be between 8 and 72');
    });

    it('should reject invalid tab size', () => {
      const result = service.validateSettings({
        editor: { tabSize: 10 } as any,
      });
      
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Tab size must be between 1 and 8');
    });

    it('should reject negative cache size', () => {
      const result = service.validateSettings({
        cache: { maxSize: -100 } as any,
      });
      
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Cache max size cannot be negative');
    });

    it('should reject negative maxRedirects', () => {
      const result = service.validateSettings({
        network: { maxRedirects: -1 } as any,
      });
      
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Max redirects cannot be negative');
    });
  });

  describe('Auto-Save Functionality', () => {
    it('should auto-save be enabled by default', () => {
      const autoSave = service.getAutoSaveSettings();
      expect(autoSave.enabled).toBe(true);
    });

    it('should stop auto-save', () => {
      service.stopAutoSave();
      // No error should be thrown
      expect(true).toBe(true);
    });
  });
});
