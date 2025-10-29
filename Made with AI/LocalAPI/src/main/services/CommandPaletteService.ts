/**
 * CommandPaletteService - Quick Actions Command Palette
 * 
 * Provides Ctrl+P quick actions functionality
 * Similar to VS Code Command Palette
 */

export interface Command {
  id: string;
  label: string;
  category: 'File' | 'Edit' | 'View' | 'Go' | 'Help' | 'Window' | 'Tools';
  description?: string;
  shortcut?: string;
  icon?: string;
  action: () => void | Promise<void>;
  enabled?: boolean;
  keywords?: string[];
}

export interface CommandMatch {
  command: Command;
  score: number;
  highlightedLabel: string;
}

export class CommandPaletteService {
  private commands: Map<string, Command>;
  private recentCommands: string[]; // command IDs
  private maxRecentCommands: number;

  constructor() {
    this.commands = new Map();
    this.recentCommands = [];
    this.maxRecentCommands = 10;
    this.registerDefaultCommands();
  }

  /**
   * Register a command
   */
  registerCommand(command: Command): void {
    this.commands.set(command.id, command);
  }

  /**
   * Unregister a command
   */
  unregisterCommand(id: string): boolean {
    return this.commands.delete(id);
  }

  /**
   * Get command by ID
   */
  getCommand(id: string): Command | undefined {
    return this.commands.get(id);
  }

  /**
   * Get all commands
   */
  getAllCommands(): Command[] {
    return Array.from(this.commands.values()).filter(cmd => cmd.enabled !== false);
  }

  /**
   * Search commands with fuzzy matching
   */
  searchCommands(query: string): CommandMatch[] {
    if (!query.trim()) {
      return this.getRecentCommandMatches();
    }

    const matches: CommandMatch[] = [];
    const lowerQuery = query.toLowerCase();

    for (const command of this.commands.values()) {
      if (command.enabled === false) continue;

      const score = this.calculateMatchScore(command, lowerQuery);
      if (score > 0) {
        matches.push({
          command,
          score,
          highlightedLabel: this.highlightMatch(command.label, lowerQuery),
        });
      }
    }

    return matches.sort((a, b) => b.score - a.score);
  }

  /**
   * Execute command
   */
  async executeCommand(id: string): Promise<boolean> {
    const command = this.commands.get(id);
    if (!command || command.enabled === false) return false;

    try {
      await command.action();
      this.addToRecent(id);
      return true;
    } catch (error) {
      console.error(`Error executing command ${id}:`, error);
      return false;
    }
  }

  /**
   * Get recent commands
   */
  getRecentCommands(): Command[] {
    return this.recentCommands
      .map(id => this.commands.get(id))
      .filter((cmd): cmd is Command => cmd !== undefined && cmd.enabled !== false);
  }

  /**
   * Clear recent commands
   */
  clearRecentCommands(): void {
    this.recentCommands = [];
  }

  /**
   * Register default commands
   */
  private registerDefaultCommands(): void {
    // File commands
    this.registerCommand({
      id: 'file.newRequest',
      label: 'New Request',
      category: 'File',
      shortcut: 'Ctrl+N',
      icon: 'add',
      action: async () => {
        // Will be connected to actual implementation
        console.log('New Request');
      },
      keywords: ['create', 'add'],
    });

    this.registerCommand({
      id: 'file.newCollection',
      label: 'New Collection',
      category: 'File',
      icon: 'folder',
      action: async () => {
        console.log('New Collection');
      },
      keywords: ['create', 'folder'],
    });

    this.registerCommand({
      id: 'file.save',
      label: 'Save',
      category: 'File',
      shortcut: 'Ctrl+S',
      icon: 'save',
      action: async () => {
        console.log('Save');
      },
    });

    this.registerCommand({
      id: 'file.importCollection',
      label: 'Import Collection',
      category: 'File',
      icon: 'upload',
      action: async () => {
        console.log('Import');
      },
      keywords: ['load', 'open'],
    });

    this.registerCommand({
      id: 'file.exportCollection',
      label: 'Export Collection',
      category: 'File',
      icon: 'download',
      action: async () => {
        console.log('Export');
      },
      keywords: ['save', 'download'],
    });

    // Edit commands
    this.registerCommand({
      id: 'edit.find',
      label: 'Find',
      category: 'Edit',
      shortcut: 'Ctrl+F',
      icon: 'search',
      action: async () => {
        console.log('Find');
      },
    });

    this.registerCommand({
      id: 'edit.replace',
      label: 'Replace',
      category: 'Edit',
      shortcut: 'Ctrl+H',
      icon: 'find_replace',
      action: async () => {
        console.log('Replace');
      },
    });

    // View commands
    this.registerCommand({
      id: 'view.toggleSidebar',
      label: 'Toggle Sidebar',
      category: 'View',
      shortcut: 'Ctrl+B',
      icon: 'menu',
      action: async () => {
        console.log('Toggle Sidebar');
      },
    });

    this.registerCommand({
      id: 'view.toggleConsole',
      label: 'Toggle Debug Console',
      category: 'View',
      icon: 'terminal',
      action: async () => {
        console.log('Toggle Console');
      },
      keywords: ['debug', 'logs'],
    });

    this.registerCommand({
      id: 'view.toggleFullscreen',
      label: 'Toggle Fullscreen',
      category: 'View',
      shortcut: 'F11',
      icon: 'fullscreen',
      action: async () => {
        console.log('Toggle Fullscreen');
      },
    });

    // Go commands
    this.registerCommand({
      id: 'go.back',
      label: 'Go Back',
      category: 'Go',
      shortcut: 'Alt+Left',
      icon: 'arrow_back',
      action: async () => {
        console.log('Go Back');
      },
    });

    this.registerCommand({
      id: 'go.forward',
      label: 'Go Forward',
      category: 'Go',
      shortcut: 'Alt+Right',
      icon: 'arrow_forward',
      action: async () => {
        console.log('Go Forward');
      },
    });

    this.registerCommand({
      id: 'go.goToCollection',
      label: 'Go to Collection',
      category: 'Go',
      shortcut: 'Ctrl+Shift+O',
      icon: 'folder_open',
      action: async () => {
        console.log('Go to Collection');
      },
      keywords: ['open', 'navigate'],
    });

    // Window commands
    this.registerCommand({
      id: 'window.newTab',
      label: 'New Tab',
      category: 'Window',
      shortcut: 'Ctrl+T',
      icon: 'tab',
      action: async () => {
        console.log('New Tab');
      },
    });

    this.registerCommand({
      id: 'window.closeTab',
      label: 'Close Tab',
      category: 'Window',
      shortcut: 'Ctrl+W',
      icon: 'close',
      action: async () => {
        console.log('Close Tab');
      },
    });

    this.registerCommand({
      id: 'window.closeOthers',
      label: 'Close Other Tabs',
      category: 'Window',
      action: async () => {
        console.log('Close Others');
      },
    });

    this.registerCommand({
      id: 'window.closeAll',
      label: 'Close All Tabs',
      category: 'Window',
      action: async () => {
        console.log('Close All');
      },
    });

    this.registerCommand({
      id: 'window.nextTab',
      label: 'Next Tab',
      category: 'Window',
      shortcut: 'Ctrl+Tab',
      icon: 'arrow_forward',
      action: async () => {
        console.log('Next Tab');
      },
    });

    this.registerCommand({
      id: 'window.previousTab',
      label: 'Previous Tab',
      category: 'Window',
      shortcut: 'Ctrl+Shift+Tab',
      icon: 'arrow_back',
      action: async () => {
        console.log('Previous Tab');
      },
    });

    // Tools commands
    this.registerCommand({
      id: 'tools.settings',
      label: 'Open Settings',
      category: 'Tools',
      shortcut: 'Ctrl+,',
      icon: 'settings',
      action: async () => {
        console.log('Settings');
      },
      keywords: ['preferences', 'config'],
    });

    this.registerCommand({
      id: 'tools.shortcuts',
      label: 'Keyboard Shortcuts',
      category: 'Tools',
      icon: 'keyboard',
      action: async () => {
        console.log('Shortcuts');
      },
      keywords: ['hotkeys', 'keys'],
    });

    this.registerCommand({
      id: 'tools.clearCache',
      label: 'Clear Cache',
      category: 'Tools',
      icon: 'delete',
      action: async () => {
        console.log('Clear Cache');
      },
      keywords: ['clean', 'remove'],
    });

    // Help commands
    this.registerCommand({
      id: 'help.documentation',
      label: 'View Documentation',
      category: 'Help',
      icon: 'help',
      action: async () => {
        console.log('Documentation');
      },
      keywords: ['docs', 'manual', 'guide'],
    });

    this.registerCommand({
      id: 'help.about',
      label: 'About LocalAPI',
      category: 'Help',
      icon: 'info',
      action: async () => {
        console.log('About');
      },
      keywords: ['version', 'info'],
    });
  }

  /**
   * Calculate match score for fuzzy search
   */
  private calculateMatchScore(command: Command, query: string): number {
    let score = 0;
    const lowerLabel = command.label.toLowerCase();
    const lowerCategory = command.category.toLowerCase();

    // Exact match
    if (lowerLabel === query) {
      score += 100;
    }

    // Starts with
    if (lowerLabel.startsWith(query)) {
      score += 50;
    }

    // Contains
    if (lowerLabel.includes(query)) {
      score += 25;
    }

    // Category match
    if (lowerCategory.includes(query)) {
      score += 10;
    }

    // Description match
    if (command.description?.toLowerCase().includes(query)) {
      score += 5;
    }

    // Keywords match
    if (command.keywords) {
      for (const keyword of command.keywords) {
        if (keyword.toLowerCase().includes(query)) {
          score += 15;
        }
      }
    }

    // Fuzzy match (consecutive characters)
    let queryIndex = 0;
    for (const char of lowerLabel) {
      if (char === query[queryIndex]) {
        queryIndex++;
        score += 2;
      }
      if (queryIndex === query.length) break;
    }

    return score;
  }

  /**
   * Highlight matching characters
   */
  private highlightMatch(label: string, query: string): string {
    if (!query) return label;

    const lowerLabel = label.toLowerCase();
    const lowerQuery = query.toLowerCase();

    let result = '';
    let queryIndex = 0;

    for (let i = 0; i < label.length; i++) {
      const char = label[i];
      const lowerChar = lowerLabel[i];

      if (queryIndex < query.length && lowerChar === lowerQuery[queryIndex]) {
        result += `<mark>${char}</mark>`;
        queryIndex++;
      } else {
        result += char;
      }
    }

    return result;
  }

  /**
   * Add command to recent
   */
  private addToRecent(id: string): void {
    // Remove if already exists
    this.recentCommands = this.recentCommands.filter(cmdId => cmdId !== id);

    // Add to beginning
    this.recentCommands.unshift(id);

    // Limit size
    if (this.recentCommands.length > this.maxRecentCommands) {
      this.recentCommands.pop();
    }
  }

  /**
   * Get recent command matches
   */
  private getRecentCommandMatches(): CommandMatch[] {
    return this.getRecentCommands().map(command => ({
      command,
      score: 0,
      highlightedLabel: command.label,
    }));
  }
}
