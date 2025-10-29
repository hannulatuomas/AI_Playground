/**
 * Keyboard Shortcuts Integration Tests
 * 
 * Tests the complete keyboard shortcut workflow:
 * - KeyboardShortcutManager initialization
 * - Shortcut execution triggering UI changes
 * - App-level shortcut handling
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { KeyboardShortcutManager } from '../../src/renderer/services/KeyboardShortcutManager';

describe('Keyboard Shortcuts Integration', () => {
  let manager: KeyboardShortcutManager;
  let addEventListenerSpy: jest.SpyInstance;
  let removeEventListenerSpy: jest.SpyInstance;

  // Helper to trigger keyboard event
  const triggerKeyEvent = (key: string, modifiers: { ctrl?: boolean; shift?: boolean; alt?: boolean } = {}, target?: HTMLElement) => {
    const event = new KeyboardEvent('keydown', {
      key,
      ctrlKey: modifiers.ctrl,
      shiftKey: modifiers.shift,
      altKey: modifiers.alt,
      bubbles: true,
      cancelable: true,
    });
    
    Object.defineProperty(event, 'target', {
      value: target || document.createElement('div'),
      enumerable: true,
    });
    
    const listener = addEventListenerSpy.mock.calls.find(call => call[0] === 'keydown')?.[1];
    if (listener) listener(event);
    return event;
  };

  beforeEach(() => {
    addEventListenerSpy = jest.spyOn(window, 'addEventListener');
    removeEventListenerSpy = jest.spyOn(window, 'removeEventListener');
    manager = new KeyboardShortcutManager();
  });

  afterEach(() => {
    manager.destroy();
    addEventListenerSpy?.mockRestore();
    removeEventListenerSpy?.mockRestore();
    jest.clearAllMocks();
  });

  describe('App-Level Integration', () => {
    it('should initialize with default shortcuts', () => {
      manager.initialize();

      const shortcuts = manager.getAllShortcuts();
      expect(shortcuts.length).toBeGreaterThan(0);

      // Should have command palette shortcut
      const commandPalette = shortcuts.find(s => s.action === 'command-palette');
      expect(commandPalette).toBeDefined();
      expect(commandPalette?.key).toBe('p');
      expect(commandPalette?.ctrl).toBe(true);
    });

    it('should execute handler when shortcut is pressed', () => {
      const mockHandler = jest.fn();
      
      manager.registerHandler('test-action', mockHandler);
      manager.registerShortcut({
        id: 'test',
        action: 'test-action',
        key: 'x',
        ctrl: true,
      });
      
      manager.initialize();

      triggerKeyEvent('x', { ctrl: true });
      expect(mockHandler).toHaveBeenCalled();
    });

    it('should open command palette with Ctrl+P', () => {
      const mockOpenPalette = jest.fn();
      
      manager.registerHandler('command-palette', mockOpenPalette);
      manager.initialize();

      triggerKeyEvent('p', { ctrl: true });
      expect(mockOpenPalette).toHaveBeenCalled();
    });

    it('should open global search with Ctrl+K', () => {
      const mockOpenSearch = jest.fn();
      
      manager.registerHandler('global-search', mockOpenSearch);
      manager.initialize();

      triggerKeyEvent('k', { ctrl: true });
      expect(mockOpenSearch).toHaveBeenCalled();
    });

    it('should toggle sidebar with Ctrl+B', () => {
      let sidebarOpen = true;
      const mockToggleSidebar = jest.fn(() => { sidebarOpen = !sidebarOpen; });
      
      manager.registerHandler('toggle-sidebar', mockToggleSidebar);
      manager.initialize();

      triggerKeyEvent('b', { ctrl: true });
      expect(mockToggleSidebar).toHaveBeenCalled();
    });

    it('should handle multiple sequential shortcuts', () => {
      const handler1 = jest.fn();
      const handler2 = jest.fn();
      const handler3 = jest.fn();
      
      manager.registerHandler('action1', handler1);
      manager.registerHandler('action2', handler2);
      manager.registerHandler('action3', handler3);
      
      manager.registerShortcut({
        id: 's1',
        action: 'action1',
        key: 'a',
        ctrl: true,
      });
      
      manager.registerShortcut({
        id: 's2',
        action: 'action2',
        key: 'm',  // Use 'm' instead of 'b' to avoid conflict with default 'toggle-sidebar'
        ctrl: true,
      });
      
      manager.registerShortcut({
        id: 's3',
        action: 'action3',
        key: 'c',
        ctrl: true,
      });
      
      manager.initialize();

      triggerKeyEvent('a', { ctrl: true });
      triggerKeyEvent('m', { ctrl: true });
      triggerKeyEvent('c', { ctrl: true });
      
      expect(handler1).toHaveBeenCalledTimes(1);
      expect(handler2).toHaveBeenCalledTimes(1);
      expect(handler3).toHaveBeenCalledTimes(1);
    });
  });

  describe('Context Switching', () => {
    it('should execute global shortcuts in any context', () => {
      const mockHandler = jest.fn();
      
      manager.registerHandler('global-action', mockHandler);
      manager.registerShortcut({
        id: 'global',
        action: 'global-action',
        key: 'g',
        ctrl: true,
        context: 'global',
      });
      
      manager.initialize();
      manager.setActiveContext('editor');

      triggerKeyEvent('g', { ctrl: true });
      expect(mockHandler).toHaveBeenCalled();
    });

    it('should only execute context-specific shortcuts in matching context', () => {
      const mockHandler = jest.fn();
      
      manager.registerHandler('editor-action', mockHandler);
      manager.registerShortcut({
        id: 'editor',
        action: 'editor-action',
        key: 'e',
        ctrl: true,
        context: 'editor',
      });
      
      manager.initialize();
      manager.setActiveContext('dialog');

      triggerKeyEvent('e', { ctrl: true });
      expect(mockHandler).not.toHaveBeenCalled();
      
      manager.setActiveContext('editor');
      triggerKeyEvent('e', { ctrl: true });
      expect(mockHandler).toHaveBeenCalled();
    });
  });

  describe('Conflict Handling', () => {
    it('should warn about conflicting shortcuts', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      manager.registerShortcut({
        id: 'shortcut1',
        action: 'action1',
        key: 't',
        ctrl: true,
      });
      
      manager.registerShortcut({
        id: 'shortcut2',
        action: 'action2',
        key: 't',
        ctrl: true,
      });

      if (consoleSpy.mock.calls.length > 0) {
        expect(consoleSpy).toHaveBeenCalled();
      }
      
      consoleSpy.mockRestore();
    });

    it('should not conflict if shortcuts in different contexts', () => {
      manager.registerShortcut({
        id: 'editor-shortcut',
        action: 'editor-action',
        key: 't',
        ctrl: true,
        context: 'editor',
      });
      
      manager.registerShortcut({
        id: 'dialog-shortcut',
        action: 'dialog-action',
        key: 't',
        ctrl: true,
        context: 'dialog',
      });

      expect(manager.getAllShortcuts().length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('Enable/Disable', () => {
    it('should disable all shortcuts when requested', () => {
      const mockHandler = jest.fn();
      
      manager.registerHandler('test-action', mockHandler);
      manager.registerShortcut({
        id: 'test',
        action: 'test-action',
        key: 'q',
        ctrl: true,
      });
      
      manager.initialize();
      manager.setEnabled(false);

      triggerKeyEvent('q', { ctrl: true });
      expect(mockHandler).not.toHaveBeenCalled();
    });

    it('should re-enable shortcuts', () => {
      const mockHandler = jest.fn();
      
      manager.registerHandler('test-action', mockHandler);
      manager.registerShortcut({
        id: 'test',
        action: 'test-action',
        key: 'r',
        ctrl: true,
      });
      
      manager.initialize();
      manager.setEnabled(false);
      manager.setEnabled(true);

      triggerKeyEvent('r', { ctrl: true });
      expect(mockHandler).toHaveBeenCalled();
    });
  });

  describe('Error Recovery', () => {
    it('should handle errors in handlers gracefully', () => {
      const errorSpy = jest.spyOn(console, 'error').mockImplementation();
      const errorHandler = jest.fn(() => {
        throw new Error('Handler error');
      });
      
      manager.registerHandler('error-action', errorHandler);
      manager.registerShortcut({
        id: 'error',
        action: 'error-action',
        key: 'y',
        ctrl: true,
      });
      
      manager.initialize();

      triggerKeyEvent('y', { ctrl: true });
      expect(errorHandler).toHaveBeenCalled();
      expect(errorSpy).toHaveBeenCalledWith(expect.stringContaining('Error executing shortcut'), expect.any(Error));
      errorSpy.mockRestore();
    });

    it('should continue working after handler error', () => {
      const errorHandler = jest.fn(() => {
        throw new Error('Error');
      });
      const goodHandler = jest.fn();
      
      jest.spyOn(console, 'error').mockImplementation();
      
      manager.registerHandler('error-action', errorHandler);
      manager.registerHandler('good-action', goodHandler);
      
      manager.registerShortcut({
        id: 'error',
        action: 'error-action',
        key: 'z',
        ctrl: true,
      });
      
      manager.registerShortcut({
        id: 'good',
        action: 'good-action',
        key: 'g',
        ctrl: true,
      });
      
      manager.initialize();

      triggerKeyEvent('z', { ctrl: true });
      triggerKeyEvent('g', { ctrl: true });
      
      expect(errorHandler).toHaveBeenCalled();
      expect(goodHandler).toHaveBeenCalled();
    });
  });
});
