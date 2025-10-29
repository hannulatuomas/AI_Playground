/**
 * Tab Management Integration Tests
 * 
 * Tests the complete tab management workflow:
 * - Creating tabs
 * - Switching tabs
 * - Closing tabs
 * - Tab history
 * - Recent items integration
 */

import { TabManagerService } from '../../src/main/services/TabManagerService';

describe('Tab Management Integration', () => {
  let tabService: TabManagerService;

  beforeEach(() => {
    tabService = new TabManagerService();
  });

  describe('Complete Tab Lifecycle', () => {
    it('should create and manage multiple tabs', () => {
      const tab1 = tabService.createTab({
        title: 'First Tab',
        type: 'request',
        content: { url: 'https://api.example.com/users' },
      });

      const tab2 = tabService.createTab({
        title: 'Second Tab',
        type: 'graphql',
        content: { query: 'query { users { id name } }' },
      });

      expect(tabService.getAllTabs()).toHaveLength(2);
      expect(tab1.id).toBeDefined();
      expect(tab2.id).toBeDefined();
    });

    it('should switch between tabs', () => {
      const tab1 = tabService.createTab({
        title: 'Tab 1',
        type: 'request',
        content: {},
      });

      const tab2 = tabService.createTab({
        title: 'Tab 2',
        type: 'request',
        content: {},
      });

      tabService.setActiveTab(tab1.id);
      expect(tabService.getActiveTab()?.id).toBe(tab1.id);

      tabService.setActiveTab(tab2.id);
      expect(tabService.getActiveTab()?.id).toBe(tab2.id);
    });

    it('should track tab navigation history', () => {
      const tab1 = tabService.createTab({ title: 'Tab 1', type: 'request', content: {} });
      const tab2 = tabService.createTab({ title: 'Tab 2', type: 'request', content: {} });
      const tab3 = tabService.createTab({ title: 'Tab 3', type: 'request', content: {} });

      // Navigate through tabs
      tabService.setActiveTab(tab1.id);
      tabService.setActiveTab(tab2.id);
      tabService.setActiveTab(tab3.id);

      // Should be able to go back
      expect(tabService.canGoBack()).toBe(true);
      tabService.goBack();
      expect(tabService.getActiveTab()?.id).toBe(tab2.id);

      // And forward
      expect(tabService.canGoForward()).toBe(true);
      tabService.goForward();
      expect(tabService.getActiveTab()?.id).toBe(tab3.id);
    });

    it('should maintain recent tabs order', () => {
      const tab1 = tabService.createTab({ title: 'Old Tab', type: 'request', content: {} });
      const tab2 = tabService.createTab({ title: 'New Tab', type: 'request', content: {} });

      tabService.setActiveTab(tab1.id);
      jest.advanceTimersByTime(1000);
      tabService.setActiveTab(tab2.id);

      const recent = tabService.getRecentTabs(2);
      expect(recent[0].id).toBe(tab2.id); // Most recent first
      expect(recent[1].id).toBe(tab1.id);
    });
  });

  describe('Tab Groups Workflow', () => {
    it('should create groups and organize tabs', () => {
      const apiGroup = tabService.createGroup('API Tests', '#FF5733');
      const authGroup = tabService.createGroup('Auth', '#3357FF');

      const tab1 = tabService.createTab({ title: 'Login', type: 'request', content: {} });
      const tab2 = tabService.createTab({ title: 'Get Profile', type: 'request', content: {} });
      const tab3 = tabService.createTab({ title: 'Register', type: 'request', content: {} });

      tabService.addTabToGroup(tab1.id, authGroup.id);
      tabService.addTabToGroup(tab3.id, authGroup.id);
      tabService.addTabToGroup(tab2.id, apiGroup.id);

      const authTabs = tabService.getTabsByGroup(authGroup.id);
      const apiTabs = tabService.getTabsByGroup(apiGroup.id);

      expect(authTabs).toHaveLength(2);
      expect(apiTabs).toHaveLength(1);
    });

    it('should handle group deletion', () => {
      const group = tabService.createGroup('Test Group');
      const tab = tabService.createTab({ title: 'Tab', type: 'request', content: {} });

      tabService.addTabToGroup(tab.id, group.id);
      tabService.deleteGroup(group.id);

      const updatedTab = tabService.getTab(tab.id);
      expect(updatedTab?.groupId).toBeUndefined();
    });
  });

  describe('Tab Closing Scenarios', () => {
    it('should close closable tabs', () => {
      const tab = tabService.createTab({
        title: 'Closable Tab',
        type: 'request',
        content: {},
        closable: true,
      });

      const result = tabService.closeTab(tab.id);
      expect(result).toBe(true);
      expect(tabService.getTab(tab.id)).toBeUndefined();
    });

    it('should prevent closing pinned tabs', () => {
      const tab = tabService.createTab({
        title: 'Pinned Tab',
        type: 'request',
        content: {},
        sticky: true,
        closable: false,
      });

      const result = tabService.closeTab(tab.id);
      expect(result).toBe(false);
      expect(tabService.getTab(tab.id)).not.toBeNull();
    });

    it('should close multiple tabs and adjust active tab', () => {
      const tab1 = tabService.createTab({ title: 'Tab 1', type: 'request', content: {} });
      const tab2 = tabService.createTab({ title: 'Tab 2', type: 'request', content: {} });
      const tab3 = tabService.createTab({ title: 'Tab 3', type: 'request', content: {} });

      tabService.setActiveTab(tab2.id);
      tabService.closeTab(tab2.id);

      // Active tab should change when current is closed
      const activeTab = tabService.getActiveTab();
      expect(activeTab?.id).not.toBe(tab2.id);
    });
  });

  describe('Tab State Persistence', () => {
    it('should maintain tab order', () => {
      const tab1 = tabService.createTab({ title: 'First', type: 'request', content: {} });
      const tab2 = tabService.createTab({ title: 'Second', type: 'request', content: {} });
      const tab3 = tabService.createTab({ title: 'Third', type: 'request', content: {} });

      const tabs = tabService.getAllTabs();
      expect(tabs[0].id).toBe(tab1.id);
      expect(tabs[1].id).toBe(tab2.id);
      expect(tabs[2].id).toBe(tab3.id);
    });

    it('should track last accessed time', () => {
      const tab = tabService.createTab({ title: 'Tab', type: 'request', content: {} });
      const originalTime = tab.lastAccessedAt;

      jest.advanceTimersByTime(100);
      tabService.setActiveTab(tab.id);

      const updated = tabService.getTab(tab.id);
      expect(updated?.lastAccessedAt).toBeGreaterThan(originalTime);
    });
  });

  describe('Edge Cases', () => {
    it('should handle closing last tab', () => {
      const tab = tabService.createTab({ title: 'Only Tab', type: 'request', content: {} });
      tabService.closeTab(tab.id);

      expect(tabService.getAllTabs()).toHaveLength(0);
      expect(tabService.getActiveTab()).toBeNull();
    });

    it('should handle switching to non-existent tab', () => {
      const result = tabService.setActiveTab('non-existent-id');
      expect(result).toBe(false);
    });

    it('should handle invalid group operations', () => {
      const tab = tabService.createTab({ title: 'Tab', type: 'request', content: {} });
      const result = tabService.addTabToGroup(tab.id, 'invalid-group-id');
      
      expect(result).toBe(false);
    });
  });

  describe('Complex Workflows', () => {
    it('should handle rapid tab switching', () => {
      const tabs = Array.from({ length: 10 }, (_, i) =>
        tabService.createTab({ title: `Tab ${i}`, type: 'request', content: {} })
      );

      // Rapidly switch between tabs
      tabs.forEach(tab => tabService.setActiveTab(tab.id));

      const activeTab = tabService.getActiveTab();
      expect(activeTab?.id).toBe(tabs[tabs.length - 1].id);
    });

    it('should maintain history through complex navigation', () => {
      const tab1 = tabService.createTab({ title: 'Tab 1', type: 'request', content: {} });
      const tab2 = tabService.createTab({ title: 'Tab 2', type: 'request', content: {} });
      const tab3 = tabService.createTab({ title: 'Tab 3', type: 'request', content: {} });

      // Complex navigation pattern
      tabService.setActiveTab(tab1.id);
      tabService.setActiveTab(tab2.id);
      tabService.setActiveTab(tab3.id);
      tabService.goBack(); // to tab2
      tabService.goBack(); // to tab1
      tabService.goForward(); // to tab2

      expect(tabService.getActiveTab()?.id).toBe(tab2.id);
      expect(tabService.canGoBack()).toBe(true);
      expect(tabService.canGoForward()).toBe(true);
    });

    it('should handle tab modifications during navigation', () => {
      const tab1 = tabService.createTab({ title: 'Original', type: 'request', content: {} });
      
      tabService.setActiveTab(tab1.id);
      tabService.updateTab(tab1.id, { title: 'Modified' });

      const updated = tabService.getTab(tab1.id);
      expect(updated?.title).toBe('Modified');
      expect(tabService.getActiveTab()?.title).toBe('Modified');
    });
  });
});
