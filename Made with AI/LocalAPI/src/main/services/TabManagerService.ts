/**
 * TabManagerService - Comprehensive Tab Management
 * 
 * Features:
 * - Tab state management
 * - Tab history (back/forward navigation)
 * - Tab groups/workspaces
 * - Tab search/filter
 * - Drag-and-drop reordering
 * - Sticky tabs
 * - Tab color coding
 * - Close all/close others
 * - Tab overflow handling
 */

export interface Tab {
  id: string;
  title: string;
  type: 'request' | 'graphql' | 'websocket' | 'grpc' | 'collection' | 'environment' | 'other';
  content: any;
  icon?: string;
  color?: string;
  sticky?: boolean;
  groupId?: string;
  order: number;
  createdAt: number;
  lastAccessedAt: number;
  modified?: boolean;
  closable?: boolean;
}

export interface TabGroup {
  id: string;
  name: string;
  color?: string;
  tabs: string[]; // tab IDs
  collapsed?: boolean;
  order: number;
}

export interface TabHistory {
  past: string[]; // tab IDs
  present: string | null;
  future: string[];
}

export interface TabSearchResult {
  tab: Tab;
  score: number;
  matches: string[];
}

export class TabManagerService {
  private tabs: Map<string, Tab>;
  private groups: Map<string, TabGroup>;
  private history: TabHistory;
  private activeTabId: string | null;
  private maxHistorySize: number;
  private tabOrder: string[];

  constructor() {
    this.tabs = new Map();
    this.groups = new Map();
    this.history = {
      past: [],
      present: null,
      future: [],
    };
    this.activeTabId = null;
    this.maxHistorySize = 50;
    this.tabOrder = [];
  }

  /**
   * Create a new tab
   */
  createTab(tab: Omit<Tab, 'order' | 'createdAt' | 'lastAccessedAt'> & { id?: string }): Tab {
    // Use provided ID or generate a new one
    const id = tab.id || this.generateTabId();
    
    // Check if tab with this ID already exists
    if (this.tabs.has(id)) {
      console.warn(`Tab with ID ${id} already exists, returning existing tab`);
      return this.tabs.get(id)!;
    }
    
    const newTab: Tab = {
      ...tab,
      id,
      order: this.tabOrder.length,
      createdAt: Date.now(),
      lastAccessedAt: Date.now(),
      closable: tab.closable !== false,
    };

    this.tabs.set(id, newTab);
    this.tabOrder.push(id);

    // Add to group if specified
    if (tab.groupId && this.groups.has(tab.groupId)) {
      const group = this.groups.get(tab.groupId)!;
      group.tabs.push(id);
    }

    return newTab;
  }

  /**
   * Get tab by ID
   */
  getTab(id: string): Tab | undefined {
    return this.tabs.get(id);
  }

  /**
   * Get all tabs
   */
  getAllTabs(): Tab[] {
    return this.tabOrder
      .map(id => this.tabs.get(id))
      .filter((tab): tab is Tab => tab !== undefined);
  }

  /**
   * Get tabs by group
   */
  getTabsByGroup(groupId: string): Tab[] {
    const group = this.groups.get(groupId);
    if (!group) return [];

    return group.tabs
      .map(id => this.tabs.get(id))
      .filter((tab): tab is Tab => tab !== undefined);
  }

  /**
   * Update tab
   */
  updateTab(id: string, updates: Partial<Tab>): boolean {
    const tab = this.tabs.get(id);
    if (!tab) return false;

    const updatedTab = { ...tab, ...updates };
    this.tabs.set(id, updatedTab);
    return true;
  }

  /**
   * Close tab
   */
  closeTab(id: string): boolean {
    const tab = this.tabs.get(id);
    if (!tab || tab.sticky || tab.closable === false) return false;

    // Remove from group
    if (tab.groupId) {
      const group = this.groups.get(tab.groupId);
      if (group) {
        group.tabs = group.tabs.filter(tabId => tabId !== id);
      }
    }

    // Remove from order
    this.tabOrder = this.tabOrder.filter(tabId => tabId !== id);

    // Update orders
    this.reorderTabs();

    // Remove from tabs
    this.tabs.delete(id);

    // If active tab was closed, activate another
    if (this.activeTabId === id) {
      const nextTab = this.getNextTab(id);
      if (nextTab) {
        this.setActiveTab(nextTab.id);
      } else {
        this.activeTabId = null;
      }
    }

    return true;
  }

  /**
   * Close all tabs except specified
   */
  closeOthers(keepId: string): number {
    let closed = 0;
    const allTabs = this.getAllTabs();

    for (const tab of allTabs) {
      if (tab.id !== keepId && !tab.sticky && tab.closable !== false) {
        if (this.closeTab(tab.id)) {
          closed++;
        }
      }
    }

    return closed;
  }

  /**
   * Close all tabs to the right
   */
  closeToRight(fromId: string): number {
    let closed = 0;
    const fromIndex = this.tabOrder.indexOf(fromId);
    if (fromIndex === -1) return 0;

    const tabsToClose = this.tabOrder.slice(fromIndex + 1);
    for (const id of tabsToClose) {
      const tab = this.tabs.get(id);
      if (tab && !tab.sticky && tab.closable !== false) {
        if (this.closeTab(id)) {
          closed++;
        }
      }
    }

    return closed;
  }

  /**
   * Close all non-sticky tabs
   */
  closeAll(): number {
    let closed = 0;
    const allTabs = [...this.tabs.values()];

    for (const tab of allTabs) {
      if (!tab.sticky && tab.closable !== false) {
        if (this.closeTab(tab.id)) {
          closed++;
        }
      }
    }

    return closed;
  }

  /**
   * Set active tab
   */
  setActiveTab(id: string): boolean {
    if (!this.tabs.has(id)) return false;

    // Update history
    if (this.history.present) {
      this.history.past.push(this.history.present);
      if (this.history.past.length > this.maxHistorySize) {
        this.history.past.shift();
      }
    }

    this.history.present = id;
    this.history.future = [];

    this.activeTabId = id;

    // Update last accessed time
    const tab = this.tabs.get(id)!;
    tab.lastAccessedAt = Date.now();

    return true;
  }

  /**
   * Get active tab
   */
  getActiveTab(): Tab | null {
    return this.activeTabId ? this.tabs.get(this.activeTabId) || null : null;
  }

  /**
   * Navigate back in history
   */
  goBack(): Tab | null {
    if (this.history.past.length === 0) return null;

    const previousId = this.history.past.pop()!;
    if (this.history.present) {
      this.history.future.unshift(this.history.present);
    }

    this.history.present = previousId;
    this.activeTabId = previousId;

    return this.tabs.get(previousId) || null;
  }

  /**
   * Navigate forward in history
   */
  goForward(): Tab | null {
    if (this.history.future.length === 0) return null;

    const nextId = this.history.future.shift()!;
    if (this.history.present) {
      this.history.past.push(this.history.present);
    }

    this.history.present = nextId;
    this.activeTabId = nextId;

    return this.tabs.get(nextId) || null;
  }

  /**
   * Check if can go back
   */
  canGoBack(): boolean {
    return this.history.past.length > 0;
  }

  /**
   * Check if can go forward
   */
  canGoForward(): boolean {
    return this.history.future.length > 0;
  }

  /**
   * Search tabs
   */
  searchTabs(query: string): TabSearchResult[] {
    if (!query.trim()) return [];

    const results: TabSearchResult[] = [];
    const lowerQuery = query.toLowerCase();

    for (const tab of this.tabs.values()) {
      const matches: string[] = [];
      let score = 0;

      // Check title
      if (tab.title.toLowerCase().includes(lowerQuery)) {
        matches.push('title');
        score += 10;
      }

      // Check type
      if (tab.type.toLowerCase().includes(lowerQuery)) {
        matches.push('type');
        score += 5;
      }

      // Check group
      if (tab.groupId) {
        const group = this.groups.get(tab.groupId);
        if (group && group.name.toLowerCase().includes(lowerQuery)) {
          matches.push('group');
          score += 3;
        }
      }

      if (matches.length > 0) {
        results.push({ tab, score, matches });
      }
    }

    return results.sort((a, b) => b.score - a.score);
  }

  /**
   * Reorder tab
   */
  reorderTab(tabId: string, newIndex: number): boolean {
    const currentIndex = this.tabOrder.indexOf(tabId);
    if (currentIndex === -1) return false;

    this.tabOrder.splice(currentIndex, 1);
    this.tabOrder.splice(newIndex, 0, tabId);

    this.reorderTabs();
    return true;
  }

  /**
   * Create tab group
   */
  createGroup(name: string, color?: string): TabGroup {
    const id = this.generateGroupId();
    const group: TabGroup = {
      id,
      name,
      color,
      tabs: [],
      collapsed: false,
      order: this.groups.size,
    };

    this.groups.set(id, group);
    return group;
  }

  /**
   * Get group by ID
   */
  getGroup(id: string): TabGroup | undefined {
    return this.groups.get(id);
  }

  /**
   * Get all groups
   */
  getAllGroups(): TabGroup[] {
    return Array.from(this.groups.values()).sort((a, b) => a.order - b.order);
  }

  /**
   * Update group
   */
  updateGroup(id: string, updates: Partial<TabGroup>): boolean {
    const group = this.groups.get(id);
    if (!group) return false;

    const updatedGroup = { ...group, ...updates };
    this.groups.set(id, updatedGroup);
    return true;
  }

  /**
   * Delete group (tabs remain but ungroup)
   */
  deleteGroup(id: string): boolean {
    const group = this.groups.get(id);
    if (!group) return false;

    // Remove group from all tabs
    for (const tabId of group.tabs) {
      const tab = this.tabs.get(tabId);
      if (tab) {
        tab.groupId = undefined;
      }
    }

    this.groups.delete(id);
    return true;
  }

  /**
   * Add tab to group
   */
  addTabToGroup(tabId: string, groupId: string): boolean {
    const tab = this.tabs.get(tabId);
    const group = this.groups.get(groupId);

    if (!tab || !group) return false;

    // Remove from old group
    if (tab.groupId) {
      const oldGroup = this.groups.get(tab.groupId);
      if (oldGroup) {
        oldGroup.tabs = oldGroup.tabs.filter(id => id !== tabId);
      }
    }

    // Add to new group
    tab.groupId = groupId;
    if (!group.tabs.includes(tabId)) {
      group.tabs.push(tabId);
    }

    return true;
  }

  /**
   * Remove tab from group
   */
  removeTabFromGroup(tabId: string): boolean {
    const tab = this.tabs.get(tabId);
    if (!tab || !tab.groupId) return false;

    const group = this.groups.get(tab.groupId);
    if (group) {
      group.tabs = group.tabs.filter(id => id !== tabId);
    }

    tab.groupId = undefined;
    return true;
  }

  /**
   * Get sticky tabs
   */
  getStickyTabs(): Tab[] {
    return this.getAllTabs().filter(tab => tab.sticky);
  }

  /**
   * Get recently accessed tabs
   */
  getRecentTabs(limit: number = 10): Tab[] {
    return this.getAllTabs()
      .sort((a, b) => b.lastAccessedAt - a.lastAccessedAt)
      .slice(0, limit);
  }

  /**
   * Get tabs by type
   */
  getTabsByType(type: Tab['type']): Tab[] {
    return this.getAllTabs().filter(tab => tab.type === type);
  }

  /**
   * Get modified tabs
   */
  getModifiedTabs(): Tab[] {
    return this.getAllTabs().filter(tab => tab.modified);
  }

  /**
   * Get tab count
   */
  getTabCount(): number {
    return this.tabs.size;
  }

  /**
   * Get color for tab type
   */
  getColorForType(type: Tab['type']): string {
    const colors: Record<Tab['type'], string> = {
      request: '#2196F3',
      graphql: '#E10098',
      websocket: '#FFA726',
      grpc: '#00BCD4',
      collection: '#4CAF50',
      environment: '#9C27B0',
      other: '#757575',
    };

    return colors[type] || colors.other;
  }

  /**
   * Export tabs state
   */
  exportState(): { tabs: Tab[]; groups: TabGroup[]; history: TabHistory; activeTabId: string | null } {
    return {
      tabs: this.getAllTabs(),
      groups: this.getAllGroups(),
      history: this.history,
      activeTabId: this.activeTabId,
    };
  }

  /**
   * Import tabs state
   */
  importState(state: { tabs: Tab[]; groups: TabGroup[]; history: TabHistory; activeTabId: string | null }): void {
    this.tabs.clear();
    this.groups.clear();
    this.tabOrder = [];

    // Import groups
    for (const group of state.groups) {
      this.groups.set(group.id, group);
    }

    // Import tabs
    for (const tab of state.tabs) {
      this.tabs.set(tab.id, tab);
      this.tabOrder.push(tab.id);
    }

    this.history = state.history;
    this.activeTabId = state.activeTabId;
  }

  /**
   * Private helper: Generate tab ID
   */
  private generateTabId(): string {
    return `tab-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Private helper: Generate group ID
   */
  private generateGroupId(): string {
    return `group-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Private helper: Get next tab to activate
   */
  private getNextTab(closedId: string): Tab | null {
    const index = this.tabOrder.indexOf(closedId);
    if (index === -1) return null;

    // Try next tab
    if (index < this.tabOrder.length - 1) {
      return this.tabs.get(this.tabOrder[index + 1]) || null;
    }

    // Try previous tab
    if (index > 0) {
      return this.tabs.get(this.tabOrder[index - 1]) || null;
    }

    return null;
  }

  /**
   * Private helper: Reorder tabs based on tabOrder array
   */
  private reorderTabs(): void {
    this.tabOrder.forEach((id, index) => {
      const tab = this.tabs.get(id);
      if (tab) {
        tab.order = index;
      }
    });
  }
}
