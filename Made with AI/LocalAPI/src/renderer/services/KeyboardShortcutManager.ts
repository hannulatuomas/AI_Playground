/**
 * KeyboardShortcutManager - Runtime Keyboard Shortcut Handling
 * 
 * Features:
 * - Global keyboard event listening
 * - Shortcut execution dispatcher
 * - Conflict detection
 * - Context-aware shortcuts (global vs. local)
 * - Enable/disable shortcuts dynamically
 * - Shortcut registration system
 */

export interface KeyboardShortcut {
  id: string;
  action: string;
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  meta?: boolean;
  context?: 'global' | 'editor' | 'dialog' | string;
  description?: string;
  enabled?: boolean;
}

export type ShortcutHandler = (event: KeyboardEvent) => void | Promise<void>;

export class KeyboardShortcutManager {
  private shortcuts: Map<string, KeyboardShortcut>;
  private handlers: Map<string, ShortcutHandler>;
  private activeContext: string = 'global';
  private listener: ((event: KeyboardEvent) => void) | null = null;
  private enabled: boolean = true;

  constructor() {
    this.shortcuts = new Map();
    this.handlers = new Map();
    this.registerDefaultShortcuts();
  }

  /**
   * Initialize and start listening for keyboard events
   */
  initialize(): void {
    if (this.listener) return;

    this.listener = (event: KeyboardEvent) => {
      if (!this.enabled) return;
      this.handleKeyboardEvent(event);
    };

    window.addEventListener('keydown', this.listener);
  }

  /**
   * Stop listening for keyboard events
   */
  destroy(): void {
    if (this.listener) {
      window.removeEventListener('keydown', this.listener);
      this.listener = null;
    }
  }

  /**
   * Register a keyboard shortcut
   */
  registerShortcut(shortcut: KeyboardShortcut): void {
    // Check for conflicts
    const existing = this.findConflictingShortcut(shortcut);
    if (existing) {
      console.warn(`Shortcut conflict detected: ${shortcut.id} conflicts with ${existing.id}`);
    }

    this.shortcuts.set(shortcut.id, shortcut);
  }

  /**
   * Unregister a keyboard shortcut
   */
  unregisterShortcut(id: string): boolean {
    return this.shortcuts.delete(id);
  }

  /**
   * Register a handler for a shortcut action
   */
  registerHandler(action: string, handler: ShortcutHandler): void {
    this.handlers.set(action, handler);
  }

  /**
   * Unregister a handler
   */
  unregisterHandler(action: string): boolean {
    return this.handlers.delete(action);
  }

  /**
   * Get all registered shortcuts
   */
  getAllShortcuts(): KeyboardShortcut[] {
    return Array.from(this.shortcuts.values());
  }

  /**
   * Get shortcuts by context
   */
  getShortcutsByContext(context: string): KeyboardShortcut[] {
    return this.getAllShortcuts().filter(s => s.context === context || s.context === 'global');
  }

  /**
   * Set active context
   */
  setActiveContext(context: string): void {
    this.activeContext = context;
  }

  /**
   * Get active context
   */
  getActiveContext(): string {
    return this.activeContext;
  }

  /**
   * Enable/disable all shortcuts
   */
  setEnabled(enabled: boolean): void {
    this.enabled = enabled;
  }

  /**
   * Check if shortcuts are enabled
   */
  isEnabled(): boolean {
    return this.enabled;
  }

  /**
   * Enable/disable a specific shortcut
   */
  setShortcutEnabled(id: string, enabled: boolean): boolean {
    const shortcut = this.shortcuts.get(id);
    if (!shortcut) return false;

    shortcut.enabled = enabled;
    return true;
  }

  /**
   * Handle keyboard event
   */
  private handleKeyboardEvent(event: KeyboardEvent): void {
    // Don't handle if user is typing in input/textarea
    const target = event.target as HTMLElement;
    if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)) {
      // Exception: Allow certain shortcuts even in inputs (like Ctrl+A, Ctrl+C, etc.)
      if (!this.isAllowedInInput(event)) {
        return;
      }
    }

    // Find matching shortcut
    const matchingShortcut = this.findMatchingShortcut(event);
    if (!matchingShortcut) return;

    // Check if shortcut is enabled
    if (matchingShortcut.enabled === false) return;

    // Check context
    if (matchingShortcut.context && matchingShortcut.context !== 'global') {
      if (matchingShortcut.context !== this.activeContext) {
        return;
      }
    }

    // Get handler
    const handler = this.handlers.get(matchingShortcut.action);
    if (!handler) {
      console.warn(`No handler registered for action: ${matchingShortcut.action}`);
      return;
    }

    // Prevent default and execute
    event.preventDefault();
    event.stopPropagation();

    try {
      handler(event);
    } catch (error) {
      console.error(`Error executing shortcut ${matchingShortcut.id}:`, error);
    }
  }

  /**
   * Find shortcut matching the keyboard event
   */
  private findMatchingShortcut(event: KeyboardEvent): KeyboardShortcut | null {
    for (const shortcut of this.shortcuts.values()) {
      if (this.matchesEvent(shortcut, event)) {
        return shortcut;
      }
    }
    return null;
  }

  /**
   * Check if shortcut matches the event
   */
  private matchesEvent(shortcut: KeyboardShortcut, event: KeyboardEvent): boolean {
    // Normalize key
    const eventKey = event.key.toLowerCase();
    const shortcutKey = shortcut.key.toLowerCase();

    // Check key
    if (eventKey !== shortcutKey) return false;

    // Check modifiers
    if (!!shortcut.ctrl !== (event.ctrlKey || event.metaKey)) return false;
    if (!!shortcut.shift !== event.shiftKey) return false;
    if (!!shortcut.alt !== event.altKey) return false;
    if (!!shortcut.meta !== event.metaKey) return false;

    return true;
  }

  /**
   * Find conflicting shortcut
   */
  private findConflictingShortcut(newShortcut: KeyboardShortcut): KeyboardShortcut | null {
    for (const existing of this.shortcuts.values()) {
      if (existing.id === newShortcut.id) continue;

      // Check if they have the same key combination
      if (
        existing.key.toLowerCase() === newShortcut.key.toLowerCase() &&
        !!existing.ctrl === !!newShortcut.ctrl &&
        !!existing.shift === !!newShortcut.shift &&
        !!existing.alt === !!newShortcut.alt &&
        !!existing.meta === !!newShortcut.meta
      ) {
        // Check context overlap
        const existingContext = existing.context || 'global';
        const newContext = newShortcut.context || 'global';

        if (existingContext === 'global' || newContext === 'global' || existingContext === newContext) {
          return existing;
        }
      }
    }
    return null;
  }

  /**
   * Check if shortcut is allowed in input fields
   */
  private isAllowedInInput(event: KeyboardEvent): boolean {
    const key = event.key.toLowerCase();

    // Allow common edit shortcuts
    if (event.ctrlKey || event.metaKey) {
      const allowedKeys = ['a', 'c', 'v', 'x', 'z', 'y'];
      if (allowedKeys.includes(key)) return false; // Let browser handle these
    }

    // Allow shortcuts with Ctrl/Cmd + Shift
    if ((event.ctrlKey || event.metaKey) && event.shiftKey) {
      return true;
    }

    return false;
  }

  /**
   * Register default shortcuts
   */
  private registerDefaultShortcuts(): void {
    const defaults: KeyboardShortcut[] = [
      // File operations
      { id: 'new-request', action: 'new-request', key: 'n', ctrl: true, description: 'New Request' },
      { id: 'save', action: 'save', key: 's', ctrl: true, description: 'Save' },
      { id: 'open', action: 'open', key: 'o', ctrl: true, description: 'Open' },

      // Navigation
      { id: 'command-palette', action: 'command-palette', key: 'p', ctrl: true, description: 'Command Palette' },
      { id: 'global-search', action: 'global-search', key: 'k', ctrl: true, description: 'Global Search' },
      { id: 'go-back', action: 'go-back', key: 'arrowleft', alt: true, description: 'Go Back' },
      { id: 'go-forward', action: 'go-forward', key: 'arrowright', alt: true, description: 'Go Forward' },

      // Tab operations
      { id: 'new-tab', action: 'new-tab', key: 't', ctrl: true, description: 'New Tab' },
      { id: 'close-tab', action: 'close-tab', key: 'w', ctrl: true, description: 'Close Tab' },
      { id: 'next-tab', action: 'next-tab', key: 'tab', ctrl: true, description: 'Next Tab' },
      { id: 'prev-tab', action: 'prev-tab', key: 'tab', ctrl: true, shift: true, description: 'Previous Tab' },

      // Request operations
      { id: 'send-request', action: 'send-request', key: 'enter', ctrl: true, description: 'Send Request', context: 'editor' },

      // View operations
      { id: 'toggle-sidebar', action: 'toggle-sidebar', key: 'b', ctrl: true, description: 'Toggle Sidebar' },
      { id: 'toggle-console', action: 'toggle-console', key: 'j', ctrl: true, description: 'Toggle Console' },
      { id: 'toggle-fullscreen', action: 'toggle-fullscreen', key: 'f11', description: 'Toggle Fullscreen' },

      // Edit operations
      { id: 'find', action: 'find', key: 'f', ctrl: true, description: 'Find' },
      { id: 'replace', action: 'replace', key: 'h', ctrl: true, description: 'Replace' },

      // Settings
      { id: 'settings', action: 'settings', key: ',', ctrl: true, description: 'Settings' },

      // Zoom
      { id: 'zoom-in', action: 'zoom-in', key: '+', ctrl: true, description: 'Zoom In' },
      { id: 'zoom-out', action: 'zoom-out', key: '-', ctrl: true, description: 'Zoom Out' },
      { id: 'zoom-reset', action: 'zoom-reset', key: '0', ctrl: true, description: 'Reset Zoom' },

      // Accessibility
      { id: 'high-contrast', action: 'high-contrast', key: 'c', alt: true, shift: true, description: 'Toggle High Contrast' },

      // Misc
      { id: 'quit', action: 'quit', key: 'q', ctrl: true, description: 'Quit' },
    ];

    defaults.forEach(shortcut => this.registerShortcut(shortcut));
  }

  /**
   * Get shortcut string representation
   */
  getShortcutString(shortcut: KeyboardShortcut): string {
    const parts: string[] = [];

    if (shortcut.ctrl) parts.push('Ctrl');
    if (shortcut.alt) parts.push('Alt');
    if (shortcut.shift) parts.push('Shift');
    if (shortcut.meta) parts.push('Cmd');

    parts.push(shortcut.key.charAt(0).toUpperCase() + shortcut.key.slice(1));

    return parts.join('+');
  }

  /**
   * Export shortcuts configuration
   */
  exportShortcuts(): KeyboardShortcut[] {
    return this.getAllShortcuts();
  }

  /**
   * Import shortcuts configuration
   */
  importShortcuts(shortcuts: KeyboardShortcut[]): void {
    this.shortcuts.clear();
    shortcuts.forEach(shortcut => this.registerShortcut(shortcut));
  }

  /**
   * Reset to default shortcuts
   */
  resetToDefaults(): void {
    this.shortcuts.clear();
    this.registerDefaultShortcuts();
  }
}
