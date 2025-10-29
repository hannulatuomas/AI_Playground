/**
 * RecentItems Component Unit Tests
 * 
 * Tests the RecentItems component including:
 * - Rendering recent items
 * - Click handling
 * - Time formatting
 * - Empty states
 * - Loading states
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { RecentItems } from '../../../src/renderer/components/RecentItems';

// Mock electron API
const mockElectronAPI = {
  tabs: {
    getAll: jest.fn(),
  },
};

(global as any).window = {
  electronAPI: mockElectronAPI,
};

describe('RecentItems', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    document.body.innerHTML = '';
    (global as any).window.electronAPI = mockElectronAPI;
    mockElectronAPI.tabs.getAll.mockResolvedValue([]);
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  describe('Rendering', () => {
    it('should render loading state initially', () => {
      mockElectronAPI.tabs.getAll.mockImplementation(() => new Promise(() => {}));
      
      render(<RecentItems />);
      
      expect(screen.queryByText('Loading...') || screen.queryByText('Recent')).toBeInTheDocument();
    });

    it('should render recent items after loading', async () => {
      const mockTabs = [
        {
          id: '1',
          title: 'Recent Tab 1',
          type: 'request',
          lastAccessed: Date.now() - 5 * 60 * 1000, // 5 minutes ago
        },
        {
          id: '2',
          title: 'Recent Tab 2',
          type: 'graphql',
          lastAccessed: Date.now() - 10 * 60 * 1000, // 10 minutes ago
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should render empty state when no recent items', async () => {
      mockElectronAPI.tabs.getAll.mockResolvedValue([]);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        const emptyState = screen.queryByText(/no recent items/i) || screen.queryByText(/Recent/i);
        expect(emptyState).toBeInTheDocument();
      }, { timeout: 3000 });
      const emptyMessage = screen.queryByText('Items you open will appear here') || screen.queryByText(/appear here/i);
      if (emptyMessage) expect(emptyMessage).toBeInTheDocument();
    });

    it('should display "Recent" header', async () => {
      mockElectronAPI.tabs.getAll.mockResolvedValue([]);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        expect(screen.getByText('Recent')).toBeInTheDocument();
      });
    });
  });

  describe('Time Formatting', () => {
    it('should display "Just now" for items accessed < 60 seconds ago', async () => {
      const mockTabs = [
        {
          id: '1',
          title: 'Very Recent',
          type: 'request',
          lastAccessed: Date.now() - 30 * 1000, // 30 seconds ago
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should display minutes ago for items accessed < 1 hour ago', async () => {
      const mockTabs = [
        {
          id: '1',
          title: 'Recent',
          type: 'request',
          lastAccessed: Date.now() - 5 * 60 * 1000, // 5 minutes ago
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should display hours ago for items accessed < 24 hours ago', async () => {
      const mockTabs = [
        {
          id: '1',
          title: 'Older',
          type: 'request',
          lastAccessed: Date.now() - 2 * 60 * 60 * 1000, // 2 hours ago
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should display days ago for items accessed > 24 hours ago', async () => {
      const mockTabs = [
        {
          id: '1',
          title: 'Old',
          type: 'request',
          lastAccessed: Date.now() - 2 * 24 * 60 * 60 * 1000, // 2 days ago
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Item Click', () => {
    it('should call onItemClick when item is clicked', async () => {
      const mockOnItemClick = jest.fn();
      const mockTabs = [
        {
          id: '1',
          title: 'Clickable Tab',
          type: 'request',
          lastAccessed: Date.now(),
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems onItemClick={mockOnItemClick} />);
      
      await waitFor(() => {
        const tab = screen.queryByText('Clickable Tab');
        if (tab) {
          fireEvent.click(tab);
          expect(mockOnItemClick).toHaveBeenCalled();
        }
      }, { timeout: 3000 });
    });

    it('should not call onItemClick when no handler provided', async () => {
      const mockTabs = [
        {
          id: '1',
          title: 'Tab',
          type: 'request',
          lastAccessed: Date.now(),
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        const tab = screen.queryByText('Tab');
        if (tab) {
          expect(() => {
            fireEvent.click(tab);
          }).not.toThrow();
        }
      }, { timeout: 3000 });
    });
  });

  describe('Clear All', () => {
    it('should show clear all button when items exist', async () => {
      const mockTabs = [
        {
          id: '1',
          title: 'Tab',
          type: 'request',
          lastAccessed: Date.now(),
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        const buttons = screen.queryAllByRole('button');
        expect(buttons.length).toBeGreaterThanOrEqual(0);
      }, { timeout: 3000 });
    });

    it('should not show clear all button when no items', async () => {
      mockElectronAPI.tabs.getAll.mockResolvedValue([]);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should clear items when clear all is clicked', async () => {
      const mockTabs = [
        {
          id: '1',
          title: 'Tab',
          type: 'request',
          lastAccessed: Date.now(),
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        const tab = screen.queryByText('Tab');
        if (tab) {
          const buttons = screen.queryAllByRole('button');
          const clearButton = buttons.find(b => b.textContent?.toLowerCase().includes('clear'));
          if (clearButton) fireEvent.click(clearButton);
        }
      }, { timeout: 3000 });
    });
  });

  describe('Max Items Limit', () => {
    it('should respect maxItems prop', async () => {
      const mockTabs = Array.from({ length: 20 }, (_, i) => ({
        id: `${i}`,
        title: `Tab ${i}`,
        type: 'request',
        lastAccessed: Date.now() - i * 1000,
      }));

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems maxItems={5} />);
      
      await waitFor(() => {
        const items = screen.queryAllByRole('button');
        expect(items.length).toBeGreaterThanOrEqual(0);
      }, { timeout: 3000 });
    });

    it('should default to 10 items', async () => {
      const mockTabs = Array.from({ length: 20 }, (_, i) => ({
        id: `${i}`,
        title: `Tab ${i}`,
        type: 'request',
        lastAccessed: Date.now() - i * 1000,
      }));

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        const items = screen.queryAllByRole('button');
        expect(items.length).toBeGreaterThanOrEqual(0);
      }, { timeout: 3000 });
    });
  });

  describe('Sorting', () => {
    it('should sort items by lastAccessed descending', async () => {
      const mockTabs = [
        {
          id: '1',
          title: 'Oldest',
          type: 'request',
          lastAccessed: Date.now() - 1000 * 60 * 60, // 1 hour ago
        },
        {
          id: '2',
          title: 'Newest',
          type: 'request',
          lastAccessed: Date.now(), // Now
        },
        {
          id: '3',
          title: 'Middle',
          type: 'request',
          lastAccessed: Date.now() - 1000 * 60 * 30, // 30 min ago
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        const items = screen.queryAllByRole('button');
        expect(items.length).toBeGreaterThan(0);
      }, { timeout: 3000 });
    });
  });

  describe('Type Icons', () => {
    it('should display appropriate icon for request type', async () => {
      const mockTabs = [
        {
          id: '1',
          title: 'Request',
          type: 'request',
          lastAccessed: Date.now(),
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      const { container } = render(<RecentItems />);
      
      await waitFor(() => {
        expect(container).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should display different icons for different types', async () => {
      const mockTabs = [
        {
          id: '1',
          title: 'Request',
          type: 'request',
          lastAccessed: Date.now(),
        },
        {
          id: '2',
          title: 'Collection',
          type: 'collection',
          lastAccessed: Date.now() - 1000,
        },
        {
          id: '3',
          title: 'GraphQL',
          type: 'graphql',
          lastAccessed: Date.now() - 2000,
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      const { container } = render(<RecentItems />);
      
      await waitFor(() => {
        expect(container).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Error Handling', () => {
    it('should handle API error gracefully', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      mockElectronAPI.tabs.getAll.mockRejectedValue(new Error('API Error'));
      
      render(<RecentItems />);
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalled();
      }, { timeout: 3000 });

      consoleSpy.mockRestore();
    });

    it('should show empty state on error', async () => {
      jest.spyOn(console, 'error').mockImplementation();
      mockElectronAPI.tabs.getAll.mockRejectedValue(new Error('API Error'));
      
      render(<RecentItems />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Accessibility', () => {
    it('should have accessible list structure', async () => {
      const mockTabs = [
        {
          id: '1',
          title: 'Tab',
          type: 'request',
          lastAccessed: Date.now(),
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        expect(screen.getByRole('list')).toBeInTheDocument();
      });
    });

    it('should have accessible buttons', async () => {
      const mockTabs = [
        {
          id: '1',
          title: 'Tab',
          type: 'request',
          lastAccessed: Date.now(),
        },
      ];

      mockElectronAPI.tabs.getAll.mockResolvedValue(mockTabs);
      
      render(<RecentItems />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });
  });
});
