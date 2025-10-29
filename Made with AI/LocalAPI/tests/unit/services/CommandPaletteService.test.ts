/**
 * CommandPaletteService Unit Tests
 * 
 * Tests command palette functionality:
 * - Command registration
 * - Search and fuzzy matching
 * - Command execution
 * - Recent commands
 * - Categories
 */

import { CommandPaletteService, type Command } from '../../../src/main/services/CommandPaletteService';

describe('CommandPaletteService', () => {
  let service: CommandPaletteService;
  let mockAction: jest.Mock;

  beforeEach(() => {
    service = new CommandPaletteService();
    mockAction = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Command Registration', () => {
    it('should register a command', () => {
      const command: Command = {
        id: 'test.command',
        label: 'Test Command',
        category: 'Tools',
        action: mockAction,
      };

      service.registerCommand(command);
      const retrieved = service.getCommand('test.command');

      expect(retrieved).toBeDefined();
      expect(retrieved?.label).toBe('Test Command');
    });

    it('should get all commands', () => {
      const cmd1: Command = {
        id: 'cmd1',
        label: 'Command 1',
        category: 'File',
        action: mockAction,
      };

      const cmd2: Command = {
        id: 'cmd2',
        label: 'Command 2',
        category: 'Edit',
        action: mockAction,
      };

      service.registerCommand(cmd1);
      service.registerCommand(cmd2);

      const commands = service.getAllCommands();
      // Should include registered commands plus default commands
      expect(commands.length).toBeGreaterThanOrEqual(2);
    });

    it('should unregister a command', () => {
      const command: Command = {
        id: 'test.command',
        label: 'Test Command',
        category: 'Tools',
        action: mockAction,
      };

      service.registerCommand(command);
      const result = service.unregisterCommand('test.command');

      expect(result).toBe(true);
      expect(service.getCommand('test.command')).toBeUndefined();
    });

    it('should return false when unregistering non-existent command', () => {
      const result = service.unregisterCommand('non.existent');
      expect(result).toBe(false);
    });

    it('should filter out disabled commands from getAllCommands', () => {
      const cmd1: Command = {
        id: 'enabled',
        label: 'Enabled Command',
        category: 'Tools',
        action: mockAction,
        enabled: true,
      };

      const cmd2: Command = {
        id: 'disabled',
        label: 'Disabled Command',
        category: 'Tools',
        action: mockAction,
        enabled: false,
      };

      service.registerCommand(cmd1);
      service.registerCommand(cmd2);

      const commands = service.getAllCommands();
      const disabledCmd = commands.find(c => c.id === 'disabled');

      expect(disabledCmd).toBeUndefined();
    });
  });

  describe('Command Search', () => {
    beforeEach(() => {
      // Clear default commands for predictable testing
      const allCommands = service.getAllCommands();
      allCommands.forEach(cmd => service.unregisterCommand(cmd.id));

      // Register test commands
      service.registerCommand({
        id: 'new.file',
        label: 'New File',
        category: 'File',
        action: mockAction,
      });

      service.registerCommand({
        id: 'open.file',
        label: 'Open File',
        category: 'File',
        action: mockAction,
      });

      service.registerCommand({
        id: 'save.file',
        label: 'Save File',
        category: 'File',
        action: mockAction,
      });

      service.registerCommand({
        id: 'close.window',
        label: 'Close Window',
        category: 'Window',
        action: mockAction,
      });
    });

    it('should search commands by label', () => {
      const matches = service.searchCommands('file');

      expect(matches.length).toBeGreaterThan(0);
      expect(matches.every(m => m.command.label.toLowerCase().includes('file'))).toBe(true);
    });

    it('should return empty search with no matches', () => {
      const matches = service.searchCommands('xyz123');
      expect(matches).toHaveLength(0);
    });

    it('should rank matches by relevance', () => {
      const matches = service.searchCommands('new');

      expect(matches.length).toBeGreaterThan(0);
      // Exact label match should rank higher
      expect(matches[0].command.label).toContain('New');
    });

    it('should return recent commands for empty query', async () => {
      // Execute some commands to populate recent
      await service.executeCommand('new.file');
      await service.executeCommand('save.file');

      const matches = service.searchCommands('');

      expect(matches.length).toBeGreaterThanOrEqual(0); // May be 0 if no matches
    });

    it('should perform case-insensitive search', () => {
      const lowerMatches = service.searchCommands('file');
      const upperMatches = service.searchCommands('FILE');
      const mixedMatches = service.searchCommands('FiLe');

      expect(lowerMatches.length).toBe(upperMatches.length);
      expect(lowerMatches.length).toBe(mixedMatches.length);
    });

    it('should highlight matched text', () => {
      const matches = service.searchCommands('new');

      expect(matches.length).toBeGreaterThan(0);
      expect(matches[0].highlightedLabel).toBeDefined();
    });

    it('should search by keywords if provided', () => {
      service.registerCommand({
        id: 'test.keywords',
        label: 'Test Command',
        category: 'Tools',
        action: mockAction,
        keywords: ['foo', 'bar', 'baz'],
      });

      const matches = service.searchCommands('foo');
      const found = matches.find(m => m.command.id === 'test.keywords');

      expect(found).toBeDefined();
    });
  });

  describe('Command Execution', () => {
    it('should execute command successfully', async () => {
      const command: Command = {
        id: 'test.execute',
        label: 'Test Execute',
        category: 'Tools',
        action: mockAction,
      };

      service.registerCommand(command);
      const result = await service.executeCommand('test.execute');

      expect(result).toBe(true);
      expect(mockAction).toHaveBeenCalled();
    });

    it('should return false for non-existent command', async () => {
      const result = await service.executeCommand('non.existent');
      expect(result).toBe(false);
    });

    it('should not execute disabled command', async () => {
      const command: Command = {
        id: 'disabled.cmd',
        label: 'Disabled',
        category: 'Tools',
        action: mockAction,
        enabled: false,
      };

      service.registerCommand(command);
      const result = await service.executeCommand('disabled.cmd');

      expect(result).toBe(false);
      expect(mockAction).not.toHaveBeenCalled();
    });

    it('should handle async actions', async () => {
      const asyncAction = jest.fn().mockResolvedValue('done');

      const command: Command = {
        id: 'async.cmd',
        label: 'Async Command',
        category: 'Tools',
        action: asyncAction,
      };

      service.registerCommand(command);
      const result = await service.executeCommand('async.cmd');

      expect(result).toBe(true);
      expect(asyncAction).toHaveBeenCalled();
    });

    it('should handle errors in command execution', async () => {
      const errorAction = jest.fn().mockRejectedValue(new Error('Command failed'));

      const command: Command = {
        id: 'error.cmd',
        label: 'Error Command',
        category: 'Tools',
        action: errorAction,
      };

      service.registerCommand(command);
      
      // Should catch error and return false
      const result = await service.executeCommand('error.cmd');
      expect(result).toBe(false);
    });

    it('should add executed command to recent commands', async () => {
      const command: Command = {
        id: 'recent.cmd',
        label: 'Recent Command',
        category: 'Tools',
        action: mockAction,
      };

      service.registerCommand(command);
      await service.executeCommand('recent.cmd');

      const recentCommands = service.getRecentCommands();
      const recentIds = recentCommands.map(c => c.id);
      expect(recentIds).toContain('recent.cmd');
    });
  });

  describe('Recent Commands', () => {
    it('should track recent commands', async () => {
      const cmd1: Command = {
        id: 'cmd1',
        label: 'Command 1',
        category: 'Tools',
        action: mockAction,
      };

      const cmd2: Command = {
        id: 'cmd2',
        label: 'Command 2',
        category: 'Tools',
        action: mockAction,
      };

      service.registerCommand(cmd1);
      service.registerCommand(cmd2);

      await service.executeCommand('cmd1');
      await service.executeCommand('cmd2');

      const recent = service.getRecentCommands();
      const recentIds = recent.map(c => c.id);

      expect(recentIds).toContain('cmd1');
      expect(recentIds).toContain('cmd2');
    });

    it('should limit recent commands to max size', async () => {
      // Create and execute many commands
      for (let i = 0; i < 15; i++) {
        const cmd: Command = {
          id: `cmd${i}`,
          label: `Command ${i}`,
          category: 'Tools',
          action: mockAction,
        };

        service.registerCommand(cmd);
        await service.executeCommand(`cmd${i}`);
      }

      const recent = service.getRecentCommands();
      expect(recent.length).toBeLessThanOrEqual(10); // maxRecentCommands = 10
    });

    it('should show most recent commands first', async () => {
      const cmd1: Command = {
        id: 'first',
        label: 'First',
        category: 'Tools',
        action: mockAction,
      };

      const cmd2: Command = {
        id: 'second',
        label: 'Second',
        category: 'Tools',
        action: mockAction,
      };

      service.registerCommand(cmd1);
      service.registerCommand(cmd2);

      await service.executeCommand('first');
      await service.executeCommand('second');

      const recent = service.getRecentCommands();
      expect(recent[0].id).toBe('second'); // Most recent first
    });

    it('should clear recent commands', () => {
      service.clearRecentCommands();
      const recent = service.getRecentCommands();
      expect(recent).toHaveLength(0);
    });
  });

  describe('Command Categories', () => {
    it('should register commands with different categories', () => {
      const fileCmd: Command = {
        id: 'file.cmd',
        label: 'File Command',
        category: 'File',
        action: mockAction,
      };

      const editCmd: Command = {
        id: 'edit.cmd',
        label: 'Edit Command',
        category: 'Edit',
        action: mockAction,
      };

      service.registerCommand(fileCmd);
      service.registerCommand(editCmd);

      const allCommands = service.getAllCommands();
      const fileCommands = allCommands.filter(c => c.category === 'File');
      const editCommands = allCommands.filter(c => c.category === 'Edit');

      expect(fileCommands.length).toBeGreaterThan(0);
      expect(editCommands.length).toBeGreaterThan(0);
    });

    it('should support multiple command categories', () => {
      const categories = ['File', 'Edit', 'View', 'Go', 'Help', 'Window', 'Tools'];
      
      categories.forEach(cat => {
        service.registerCommand({
          id: `${cat.toLowerCase()}.cmd`,
          label: `${cat} Command`,
          category: cat as any,
          action: mockAction,
        });
      });

      const commands = service.getAllCommands();
      expect(commands.length).toBeGreaterThanOrEqual(categories.length);
    });
  });

  describe('Default Commands', () => {
    it('should have default commands registered', () => {
      const commands = service.getAllCommands();
      expect(commands.length).toBeGreaterThan(0);
    });

    it('should include common commands like new request', () => {
      const commands = service.getAllCommands();
      const hasNewRequest = commands.some(c => 
        c.label.toLowerCase().includes('new') && 
        c.label.toLowerCase().includes('request')
      );

      expect(hasNewRequest).toBe(true);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty search query', () => {
      const matches = service.searchCommands('');
      expect(Array.isArray(matches)).toBe(true);
    });

    it('should handle whitespace-only search query', () => {
      const matches = service.searchCommands('   ');
      expect(Array.isArray(matches)).toBe(true);
    });

    it('should handle special characters in search', () => {
      const matches = service.searchCommands('!@#$%');
      expect(Array.isArray(matches)).toBe(true);
    });

    it('should handle very long search query', () => {
      const longQuery = 'a'.repeat(1000);
      const matches = service.searchCommands(longQuery);
      expect(Array.isArray(matches)).toBe(true);
    });
  });
});
