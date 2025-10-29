/**
 * TabManagerService Unit Tests
 * 
 * Tests all tab management functionality including:
 * - CRUD operations
 * - History management
 * - Group management
 * - Pin/sticky tabs
 * - Recent tabs
 */

import { TabManagerService, type Tab } from '../../../src/main/services/TabManagerService';

describe('TabManagerService', () => {
  let service: TabManagerService;

  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();
    
    // Create new service instance
    service = new TabManagerService();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Tab CRUD Operations', () => {
    it('should create a new tab', () => {
      const tab = service.createTab({
        title: 'Test Tab',
        type: 'request',
        content: {},
        sticky: false,
        closable: true,
      });

      expect(tab).toBeDefined();
      expect(tab.id).toBeDefined();
      expect(tab.title).toBe('Test Tab');
      expect(tab.type).toBe('request');
      expect(tab.createdAt).toBeDefined();
    });

    it('should get tab by ID', () => {
      const tab = service.createTab({ title: 'Test', type: 'request', content: {} });
      const retrieved = service.getTab(tab.id);

      expect(retrieved).toEqual(tab);
    });

    it('should return undefined for non-existent tab', () => {
      const retrieved = service.getTab('non-existent');
      expect(retrieved).toBeUndefined();
    });

    it('should get all tabs', () => {
      service.createTab({ title: 'Tab 1', type: 'request', content: {} });
      service.createTab({ title: 'Tab 2', type: 'graphql', content: {} });
      service.createTab({ title: 'Tab 3', type: 'other', content: {} });

      const tabs = service.getAllTabs();
      expect(tabs).toHaveLength(3);
    });

    it('should update tab', () => {
      const tab = service.createTab({ title: 'Original', type: 'request', content: {} });
      const updated = service.updateTab(tab.id, { title: 'Updated' });

      expect(updated).toBe(true);
      const retrieved = service.getTab(tab.id);
      expect(retrieved?.title).toBe('Updated');
    });

    it('should return false when updating non-existent tab', () => {
      const result = service.updateTab('non-existent', { title: 'Updated' });
      expect(result).toBe(false);
    });

    it('should close tab', () => {
      const tab = service.createTab({ title: 'Test', type: 'request', content: {}, closable: true });
      const result = service.closeTab(tab.id);

      expect(result).toBe(true);
      expect(service.getTab(tab.id)).toBeUndefined();
    });

    it('should not close sticky tab', () => {
      const tab = service.createTab({ 
        title: 'Sticky', 
        type: 'request',
        content: {},
        sticky: true,
        closable: false 
      });
      const result = service.closeTab(tab.id);

      expect(result).toBe(false);
      expect(service.getTab(tab.id)).not.toBeNull();
    });

    it('should close multiple tabs individually', () => {
      const tab1 = service.createTab({ title: 'Tab 1', type: 'request', content: {} });
      const tab2 = service.createTab({ title: 'Tab 2', type: 'request', content: {} });
      const tab3 = service.createTab({ title: 'Tab 3', type: 'request', content: {} });

      service.closeTab(tab1.id);
      service.closeTab(tab2.id);
      expect(service.getAllTabs()).toHaveLength(1);
    });
  });

  describe('Active Tab Management', () => {
    it('should set active tab', () => {
      const tab = service.createTab({ title: 'Test', type: 'request', content: {} });
      const result = service.setActiveTab(tab.id);

      expect(result).toBe(true);
      expect(service.getActiveTab()).toEqual(tab);
    });

    it('should return false when setting non-existent active tab', () => {
      const result = service.setActiveTab('non-existent');
      expect(result).toBe(false);
    });

    it('should update lastAccessedAt when setting active tab', () => {
      const tab = service.createTab({ title: 'Test', type: 'request', content: {} });
      const originalTime = tab.lastAccessedAt;

      // Wait a bit
      jest.advanceTimersByTime(100);

      service.setActiveTab(tab.id);
      const updated = service.getTab(tab.id);

      expect(updated?.lastAccessedAt).toBeGreaterThan(originalTime);
    });
  });

  describe('Tab History', () => {
    it('should track tab history', () => {
      const tab1 = service.createTab({ title: 'Tab 1', type: 'request', content: {} });
      const tab2 = service.createTab({ title: 'Tab 2', type: 'request', content: {} });
      const tab3 = service.createTab({ title: 'Tab 3', type: 'request', content: {} });

      service.setActiveTab(tab1.id);
      service.setActiveTab(tab2.id);
      service.setActiveTab(tab3.id);

      expect(service.canGoBack()).toBe(true);
      expect(service.canGoForward()).toBe(false);
    });

    it('should go back in history', () => {
      const tab1 = service.createTab({ title: 'Tab 1', type: 'request', content: {} });
      const tab2 = service.createTab({ title: 'Tab 2', type: 'request', content: {} });

      service.setActiveTab(tab1.id);
      service.setActiveTab(tab2.id);

      const result = service.goBack();
      expect(result).toBeTruthy();
      expect(result?.id).toBe(tab1.id);
      expect(service.getActiveTab()?.id).toBe(tab1.id);
    });

    it('should go forward in history', () => {
      const tab1 = service.createTab({ title: 'Tab 1', type: 'request', content: {} });
      const tab2 = service.createTab({ title: 'Tab 2', type: 'request', content: {} });

      service.setActiveTab(tab1.id);
      service.setActiveTab(tab2.id);
      service.goBack();

      const result = service.goForward();
      expect(result).toBeTruthy();
      expect(result?.id).toBe(tab2.id);
      expect(service.getActiveTab()?.id).toBe(tab2.id);
    });

    it('should not go back when at start of history', () => {
      const tab = service.createTab({ title: 'Tab', type: 'request', content: {} });
      service.setActiveTab(tab.id);

      expect(service.canGoBack()).toBe(false);
      expect(service.goBack()).toBeNull();
    });

    it('should not go forward when at end of history', () => {
      const tab = service.createTab({ title: 'Tab', type: 'request', content: {} });
      service.setActiveTab(tab.id);

      expect(service.canGoForward()).toBe(false);
      expect(service.goForward()).toBeNull();
    });
  });

  describe('Recent Tabs', () => {
    it('should get recent tabs sorted by lastAccessedAt', () => {
      const tab1 = service.createTab({ title: 'Tab 1', type: 'request', content: {} });
      const tab2 = service.createTab({ title: 'Tab 2', type: 'request', content: {} });
      const tab3 = service.createTab({ title: 'Tab 3', type: 'request', content: {} });

      // Access in specific order
      service.setActiveTab(tab1.id);
      jest.advanceTimersByTime(1000);
      service.setActiveTab(tab3.id);
      jest.advanceTimersByTime(1000);
      service.setActiveTab(tab2.id);

      const recent = service.getRecentTabs(3);
      
      expect(recent).toHaveLength(3);
      expect(recent[0].id).toBe(tab2.id); // Most recent
      expect(recent[1].id).toBe(tab3.id);
      expect(recent[2].id).toBe(tab1.id); // Least recent
    });

    it('should limit recent tabs to specified count', () => {
      for (let i = 0; i < 5; i++) {
        service.createTab({ title: `Tab ${i}`, type: 'request', content: {} });
      }

      const recent = service.getRecentTabs(3);
      expect(recent).toHaveLength(3);
    });
  });

  // Pin/Sticky Tabs - sticky property can be set at creation, no pin/unpin methods

  describe('Tab Groups', () => {
    it('should create group', () => {
      const group = service.createGroup('API Tests', '#FF5733');

      expect(group).toBeDefined();
      expect(group.id).toBeDefined();
      expect(group.name).toBe('API Tests');
      expect(group.color).toBe('#FF5733');
    });

    it('should get all groups', () => {
      service.createGroup('Group 1');
      service.createGroup('Group 2');

      const groups = service.getAllGroups();
      expect(groups).toHaveLength(2);
    });

    it('should add tab to group', () => {
      const tab = service.createTab({ title: 'Test', type: 'request', content: {} });
      const group = service.createGroup('Test Group');

      const result = service.addTabToGroup(tab.id, group.id);
      expect(result).toBe(true);

      const updated = service.getTab(tab.id);
      expect(updated?.groupId).toBe(group.id);
    });

    it('should remove tab from group', () => {
      const tab = service.createTab({ title: 'Test', type: 'request', content: {} });
      const group = service.createGroup('Test Group');

      service.addTabToGroup(tab.id, group.id);
      const result = service.removeTabFromGroup(tab.id);

      expect(result).toBe(true);
      const updated = service.getTab(tab.id);
      expect(updated?.groupId).toBeUndefined();
    });

    it('should get tabs by group', () => {
      const group = service.createGroup('Test Group');
      const tab1 = service.createTab({ title: 'Tab 1', type: 'request', content: {} });
      const tab2 = service.createTab({ title: 'Tab 2', type: 'request', content: {} });
      const tab3 = service.createTab({ title: 'Tab 3', type: 'request', content: {} });

      service.addTabToGroup(tab1.id, group.id);
      service.addTabToGroup(tab2.id, group.id);

      const groupTabs = service.getTabsByGroup(group.id);
      expect(groupTabs).toHaveLength(2);
    });

    it('should delete group and ungroup tabs', () => {
      const group = service.createGroup('Test Group');
      const tab = service.createTab({ title: 'Test', type: 'request', content: {} });
      service.addTabToGroup(tab.id, group.id);

      const result = service.deleteGroup(group.id);
      expect(result).toBe(true);

      const updated = service.getTab(tab.id);
      expect(updated?.groupId).toBeUndefined();
    });
  });

  // Persistence - TabManagerService uses in-memory storage, no file persistence

  describe('Edge Cases', () => {
    it('should handle closing last tab', () => {
      const tab = service.createTab({ title: 'Only Tab', type: 'request', content: {}, closable: true });
      service.closeTab(tab.id);

      expect(service.getAllTabs()).toHaveLength(0);
      expect(service.getActiveTab()).toBeNull();
    });

    it('should handle empty tab list', () => {
      expect(service.getAllTabs()).toHaveLength(0);
      expect(service.getActiveTab()).toBeNull();
      expect(service.getRecentTabs()).toHaveLength(0);
    });

    it('should handle invalid group operations', () => {
      const tab = service.createTab({ title: 'Test', type: 'request', content: {} });
      
      expect(service.addTabToGroup(tab.id, 'invalid-group')).toBe(false);
      expect(service.getTabsByGroup('invalid-group')).toHaveLength(0);
    });
  });
});
