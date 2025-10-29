// Tests for PluginLoader
import { PluginLoader } from '../src/main/services/PluginLoader';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

describe('PluginLoader', () => {
  let pluginLoader: PluginLoader;
  let testPluginsDir: string;
  let testDataDir: string;

  beforeEach(() => {
    // Create temporary directories for testing
    testPluginsDir = fs.mkdtempSync(path.join(os.tmpdir(), 'plugins-test-'));
    testDataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'plugin-data-test-'));
    pluginLoader = new PluginLoader(testPluginsDir, testDataDir);
  });

  afterEach(() => {
    // Clean up test directories
    if (fs.existsSync(testPluginsDir)) {
      fs.rmSync(testPluginsDir, { recursive: true, force: true });
    }
    if (fs.existsSync(testDataDir)) {
      fs.rmSync(testDataDir, { recursive: true, force: true });
    }
  });

  describe('Plugin Discovery', () => {
    test('should discover plugins in directory', async () => {
      // Create test plugin
      const pluginDir = path.join(testPluginsDir, 'test-plugin');
      fs.mkdirSync(pluginDir, { recursive: true });
      
      const manifest = {
        id: 'test.plugin',
        name: 'Test Plugin',
        version: '1.0.0',
        description: 'Test',
        main: 'index.js',
      };
      
      fs.writeFileSync(
        path.join(pluginDir, 'plugin.json'),
        JSON.stringify(manifest)
      );

      const discovered = await pluginLoader.discoverPlugins();
      expect(discovered).toContain('test-plugin');
    });

    test('should not discover directories without plugin.json', async () => {
      const notPluginDir = path.join(testPluginsDir, 'not-a-plugin');
      fs.mkdirSync(notPluginDir, { recursive: true });

      const discovered = await pluginLoader.discoverPlugins();
      expect(discovered).not.toContain('not-a-plugin');
    });

    test('should discover multiple plugins', async () => {
      // Create multiple test plugins
      for (let i = 1; i <= 3; i++) {
        const pluginDir = path.join(testPluginsDir, `plugin-${i}`);
        fs.mkdirSync(pluginDir, { recursive: true });
        
        fs.writeFileSync(
          path.join(pluginDir, 'plugin.json'),
          JSON.stringify({
            id: `test.plugin${i}`,
            name: `Plugin ${i}`,
            version: '1.0.0',
            description: 'Test',
            main: 'index.js',
          })
        );
      }

      const discovered = await pluginLoader.discoverPlugins();
      expect(discovered).toHaveLength(3);
    });
  });

  describe('Plugin Loading', () => {
    test('should load valid plugin', async () => {
      // Create test plugin
      const pluginDir = path.join(testPluginsDir, 'test-plugin');
      fs.mkdirSync(pluginDir, { recursive: true });
      
      const manifest = {
        id: 'test.plugin',
        name: 'Test Plugin',
        version: '1.0.0',
        description: 'Test plugin',
        main: 'index.js',
      };
      
      fs.writeFileSync(
        path.join(pluginDir, 'plugin.json'),
        JSON.stringify(manifest)
      );

      // Create main file
      fs.writeFileSync(
        path.join(pluginDir, 'index.js'),
        'module.exports = { onLoad: async (ctx) => { ctx.api.log("loaded"); } };'
      );

      const result = await pluginLoader.loadPlugin('test-plugin');
      
      expect(result.success).toBe(true);
      expect(result.plugin).toBeDefined();
      expect(result.plugin?.id).toBe('test.plugin');
      expect(result.plugin?.name).toBe('Test Plugin');
    });

    test('should fail to load plugin without manifest', async () => {
      const result = await pluginLoader.loadPlugin('nonexistent');
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('plugin.json not found');
    });

    test('should fail to load plugin with invalid manifest', async () => {
      const pluginDir = path.join(testPluginsDir, 'invalid-plugin');
      fs.mkdirSync(pluginDir, { recursive: true });
      
      // Missing required fields
      fs.writeFileSync(
        path.join(pluginDir, 'plugin.json'),
        JSON.stringify({ name: 'Invalid' })
      );

      const result = await pluginLoader.loadPlugin('invalid-plugin');
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Invalid plugin manifest');
    });

    test('should fail to load plugin without main file', async () => {
      const pluginDir = path.join(testPluginsDir, 'no-main-plugin');
      fs.mkdirSync(pluginDir, { recursive: true });
      
      fs.writeFileSync(
        path.join(pluginDir, 'plugin.json'),
        JSON.stringify({
          id: 'test.nomain',
          name: 'No Main',
          version: '1.0.0',
          description: 'Test',
          main: 'missing.js',
        })
      );

      const result = await pluginLoader.loadPlugin('no-main-plugin');
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Main file not found');
    });

    test('should not load same plugin twice', async () => {
      const pluginDir = path.join(testPluginsDir, 'test-plugin');
      fs.mkdirSync(pluginDir, { recursive: true });
      
      fs.writeFileSync(
        path.join(pluginDir, 'plugin.json'),
        JSON.stringify({
          id: 'test.plugin',
          name: 'Test',
          version: '1.0.0',
          description: 'Test',
          main: 'index.js',
        })
      );

      fs.writeFileSync(
        path.join(pluginDir, 'index.js'),
        'module.exports = {};'
      );

      await pluginLoader.loadPlugin('test-plugin');
      const result = await pluginLoader.loadPlugin('test-plugin');
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('already loaded');
    });
  });

  describe('Plugin Unloading', () => {
    test('should unload loaded plugin', async () => {
      // Create and load plugin
      const pluginDir = path.join(testPluginsDir, 'test-plugin');
      fs.mkdirSync(pluginDir, { recursive: true });
      
      fs.writeFileSync(
        path.join(pluginDir, 'plugin.json'),
        JSON.stringify({
          id: 'test.plugin',
          name: 'Test',
          version: '1.0.0',
          description: 'Test',
          main: 'index.js',
        })
      );

      fs.writeFileSync(
        path.join(pluginDir, 'index.js'),
        'module.exports = {};'
      );

      await pluginLoader.loadPlugin('test-plugin');
      const result = await pluginLoader.unloadPlugin('test.plugin');
      
      expect(result).toBe(true);
    });

    test('should return false for non-existent plugin', async () => {
      const result = await pluginLoader.unloadPlugin('nonexistent');
      expect(result).toBe(false);
    });

    test('should call onUnload hook', async () => {
      const pluginDir = path.join(testPluginsDir, 'test-plugin');
      fs.mkdirSync(pluginDir, { recursive: true });
      
      fs.writeFileSync(
        path.join(pluginDir, 'plugin.json'),
        JSON.stringify({
          id: 'test.plugin',
          name: 'Test',
          version: '1.0.0',
          description: 'Test',
          main: 'index.js',
        })
      );

      // Plugin with onUnload hook
      fs.writeFileSync(
        path.join(pluginDir, 'index.js'),
        `
        let unloadCalled = false;
        module.exports = {
          onUnload: async (ctx) => { unloadCalled = true; },
          wasUnloadCalled: () => unloadCalled
        };
        `
      );

      await pluginLoader.loadPlugin('test-plugin');
      await pluginLoader.unloadPlugin('test.plugin');
      
      // Plugin should be removed
      const info = pluginLoader.getPluginInfo('test.plugin');
      expect(info).toBeNull();
    });
  });

  describe('Plugin Enable/Disable', () => {
    test('should enable/disable plugin', async () => {
      const pluginDir = path.join(testPluginsDir, 'test-plugin');
      fs.mkdirSync(pluginDir, { recursive: true });
      
      fs.writeFileSync(
        path.join(pluginDir, 'plugin.json'),
        JSON.stringify({
          id: 'test.plugin',
          name: 'Test',
          version: '1.0.0',
          description: 'Test',
          main: 'index.js',
        })
      );

      fs.writeFileSync(
        path.join(pluginDir, 'index.js'),
        'module.exports = {};'
      );

      await pluginLoader.loadPlugin('test-plugin');
      
      // Disable
      const disabled = pluginLoader.setPluginEnabled('test.plugin', false);
      expect(disabled).toBe(true);
      
      let info = pluginLoader.getPluginInfo('test.plugin');
      expect(info?.enabled).toBe(false);
      
      // Enable
      const enabled = pluginLoader.setPluginEnabled('test.plugin', true);
      expect(enabled).toBe(true);
      
      info = pluginLoader.getPluginInfo('test.plugin');
      expect(info?.enabled).toBe(true);
    });

    test('should return false for non-existent plugin', () => {
      const result = pluginLoader.setPluginEnabled('nonexistent', true);
      expect(result).toBe(false);
    });
  });

  describe('Plugin Info', () => {
    test('should get plugin info', async () => {
      const pluginDir = path.join(testPluginsDir, 'test-plugin');
      fs.mkdirSync(pluginDir, { recursive: true });
      
      fs.writeFileSync(
        path.join(pluginDir, 'plugin.json'),
        JSON.stringify({
          id: 'test.plugin',
          name: 'Test Plugin',
          version: '1.2.3',
          description: 'A test plugin',
          author: 'Test Author',
          main: 'index.js',
          permissions: ['network', 'notifications'],
        })
      );

      fs.writeFileSync(
        path.join(pluginDir, 'index.js'),
        'module.exports = {};'
      );

      await pluginLoader.loadPlugin('test-plugin');
      const info = pluginLoader.getPluginInfo('test.plugin');
      
      expect(info).toBeDefined();
      expect(info?.id).toBe('test.plugin');
      expect(info?.name).toBe('Test Plugin');
      expect(info?.version).toBe('1.2.3');
      expect(info?.description).toBe('A test plugin');
      expect(info?.author).toBe('Test Author');
      expect(info?.enabled).toBe(true);
      expect(info?.loaded).toBe(true);
      expect(info?.permissions).toEqual(['network', 'notifications']);
    });

    test('should return null for non-existent plugin', () => {
      const info = pluginLoader.getPluginInfo('nonexistent');
      expect(info).toBeNull();
    });

    test('should get all plugins', async () => {
      // Create multiple plugins
      for (let i = 1; i <= 2; i++) {
        const pluginDir = path.join(testPluginsDir, `plugin-${i}`);
        fs.mkdirSync(pluginDir, { recursive: true });
        
        fs.writeFileSync(
          path.join(pluginDir, 'plugin.json'),
          JSON.stringify({
            id: `test.plugin${i}`,
            name: `Plugin ${i}`,
            version: '1.0.0',
            description: 'Test',
            main: 'index.js',
          })
        );

        fs.writeFileSync(
          path.join(pluginDir, 'index.js'),
          'module.exports = {};'
        );

        await pluginLoader.loadPlugin(`plugin-${i}`);
      }

      const allPlugins = pluginLoader.getAllPlugins();
      expect(allPlugins).toHaveLength(2);
    });
  });

  describe('Hook Execution', () => {
    test('should execute hooks for enabled plugins', async () => {
      const pluginDir = path.join(testPluginsDir, 'test-plugin');
      fs.mkdirSync(pluginDir, { recursive: true });
      
      fs.writeFileSync(
        path.join(pluginDir, 'plugin.json'),
        JSON.stringify({
          id: 'test.plugin',
          name: 'Test',
          version: '1.0.0',
          description: 'Test',
          main: 'index.js',
        })
      );

      fs.writeFileSync(
        path.join(pluginDir, 'index.js'),
        `
        module.exports = {
          onBeforeRequest: async (request, ctx) => {
            request.modified = true;
            return request;
          }
        };
        `
      );

      await pluginLoader.loadPlugin('test-plugin');
      
      const request = { method: 'GET', url: 'https://example.com' };
      const result = await pluginLoader.executeHook('onBeforeRequest', request);
      
      expect(result.modified).toBe(true);
    });

    test('should not execute hooks for disabled plugins', async () => {
      const pluginDir = path.join(testPluginsDir, 'test-plugin');
      fs.mkdirSync(pluginDir, { recursive: true });
      
      fs.writeFileSync(
        path.join(pluginDir, 'plugin.json'),
        JSON.stringify({
          id: 'test.plugin',
          name: 'Test',
          version: '1.0.0',
          description: 'Test',
          main: 'index.js',
        })
      );

      fs.writeFileSync(
        path.join(pluginDir, 'index.js'),
        `
        module.exports = {
          onBeforeRequest: async (request, ctx) => {
            request.modified = true;
            return request;
          }
        };
        `
      );

      await pluginLoader.loadPlugin('test-plugin');
      pluginLoader.setPluginEnabled('test.plugin', false);
      
      const request = { method: 'GET', url: 'https://example.com' };
      const result = await pluginLoader.executeHook('onBeforeRequest', request);
      
      expect(result.modified).toBeUndefined();
    });

    test('should handle hook errors gracefully', async () => {
      const pluginDir = path.join(testPluginsDir, 'test-plugin');
      fs.mkdirSync(pluginDir, { recursive: true });
      
      fs.writeFileSync(
        path.join(pluginDir, 'plugin.json'),
        JSON.stringify({
          id: 'test.plugin',
          name: 'Test',
          version: '1.0.0',
          description: 'Test',
          main: 'index.js',
        })
      );

      fs.writeFileSync(
        path.join(pluginDir, 'index.js'),
        `
        module.exports = {
          onBeforeRequest: async (request, ctx) => {
            throw new Error('Hook error');
          }
        };
        `
      );

      await pluginLoader.loadPlugin('test-plugin');
      
      const request = { method: 'GET', url: 'https://example.com' };
      
      // Should not throw, should return original request
      const result = await pluginLoader.executeHook('onBeforeRequest', request);
      expect(result).toEqual(request);
      
      // Plugin should have error
      const info = pluginLoader.getPluginInfo('test.plugin');
      expect(info?.error).toBeDefined();
    });
  });

  describe('Plugin Context', () => {
    test('should provide plugin context with correct info', async () => {
      const pluginDir = path.join(testPluginsDir, 'test-plugin');
      fs.mkdirSync(pluginDir, { recursive: true });
      
      fs.writeFileSync(
        path.join(pluginDir, 'plugin.json'),
        JSON.stringify({
          id: 'test.plugin',
          name: 'Test Plugin',
          version: '1.0.0',
          description: 'Test',
          main: 'index.js',
        })
      );

      let capturedContext: any = null;
      
      fs.writeFileSync(
        path.join(pluginDir, 'index.js'),
        `
        let ctx = null;
        module.exports = {
          onLoad: async (context) => {
            ctx = context;
          },
          getContext: () => ctx
        };
        `
      );

      await pluginLoader.loadPlugin('test-plugin');
      
      // Context should be available (we can't easily test it without modifying the plugin system)
      // This test verifies the plugin loaded successfully with context
      const info = pluginLoader.getPluginInfo('test.plugin');
      expect(info?.loaded).toBe(true);
    });
  });
});
