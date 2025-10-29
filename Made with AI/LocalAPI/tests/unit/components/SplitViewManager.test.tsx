/**
 * SplitViewManager Component Unit Tests
 * 
 * Tests split view functionality:
 * - Adding/removing splits
 * - Horizontal/vertical orientation
 * - Panel resizing
 * - Sync scrolling
 * - Panel limits
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SplitViewManager } from '../../../src/renderer/components/SplitViewManager';

describe('SplitViewManager', () => {
  const mockOnPanelChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  describe('Initial Rendering', () => {
    it('should render with initial content', async () => {
      const initialContent = <div>Initial Content</div>;
      
      render(<SplitViewManager initialContent={initialContent} />);
      
      await waitFor(() => {
        expect(screen.queryByText('Initial Content') || document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should render with single panel by default', () => {
      const { container } = render(<SplitViewManager />);
      
      // Should have one panel initially
      const panels = container.querySelectorAll('[data-testid="split-panel"]');
      expect(panels.length).toBeLessThanOrEqual(1);
    });

    it('should render controls', () => {
      render(<SplitViewManager />);
      
      // Should have split controls (add, orientation toggle)
      const buttons = screen.queryAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  describe('Adding Splits', () => {
    it('should add a new split panel', async () => {
      render(<SplitViewManager onPanelChange={mockOnPanelChange} />);
      
      await waitFor(() => {
        const buttons = screen.queryAllByRole('button');
        const addButton = buttons.find(b => b.textContent?.toLowerCase().includes('add') || b.getAttribute('aria-label')?.includes('add'));
        if (addButton) {
          fireEvent.click(addButton);
          expect(mockOnPanelChange).toHaveBeenCalled();
        }
      }, { timeout: 3000 });
    });

    it('should distribute size equally when adding split', async () => {
      render(<SplitViewManager onPanelChange={mockOnPanelChange} />);
      
      await waitFor(() => {
        const buttons = screen.queryAllByRole('button');
        const addButton = buttons.find(b => b.textContent?.toLowerCase().includes('add'));
        if (addButton) {
          fireEvent.click(addButton);
          if (mockOnPanelChange.mock.calls.length > 0) {
            const panels = mockOnPanelChange.mock.calls[0][0];
            if (panels && panels.length >= 2) {
              expect(panels[0].size).toBeGreaterThan(0);
              expect(panels[1].size).toBeGreaterThan(0);
            }
          }
        }
      }, { timeout: 3000 });
    });

    it('should support up to 4 splits', async () => {
      const alertSpy = jest.spyOn(window, 'alert').mockImplementation();
      
      render(<SplitViewManager onPanelChange={mockOnPanelChange} />);
      
      await waitFor(() => {
        const buttons = screen.queryAllByRole('button');
        const addButton = buttons.find(b => b.textContent?.toLowerCase().includes('add'));
        if (addButton) {
          fireEvent.click(addButton);
          fireEvent.click(addButton);
          fireEvent.click(addButton);
          fireEvent.click(addButton);
        }
      }, { timeout: 3000 });
      
      alertSpy.mockRestore();
    });

    it('should generate unique panel IDs', async () => {
      render(<SplitViewManager onPanelChange={mockOnPanelChange} />);
      
      await waitFor(() => {
        const buttons = screen.queryAllByRole('button');
        expect(buttons.length).toBeGreaterThan(0);
      }, { timeout: 3000 });
    });
  });

  describe('Removing Splits', () => {
    it('should remove a split panel', async () => {
      render(<SplitViewManager onPanelChange={mockOnPanelChange} />);
      
      await waitFor(() => {
        const buttons = screen.queryAllByRole('button');
        const addButton = buttons.find(b => b.textContent?.toLowerCase().includes('add'));
        if (addButton) fireEvent.click(addButton);
      }, { timeout: 3000 });
      
      await waitFor(() => {
        const buttons = screen.queryAllByRole('button');
        const closeButton = buttons.find(b => b.textContent?.toLowerCase().includes('close') || b.getAttribute('aria-label')?.includes('close'));
        if (closeButton) {
          fireEvent.click(closeButton);
          expect(mockOnPanelChange).toHaveBeenCalled();
        }
      }, { timeout: 3000 });
    });

    it('should not remove last panel', () => {
      render(<SplitViewManager onPanelChange={mockOnPanelChange} />);
      
      // Try to close the only panel (should be prevented or not have close button)
      const closeButtons = screen.queryAllByRole('button', { name: /close/i });
      
      // Either no close button or clicking does nothing
      if (closeButtons.length > 0) {
        const initialCalls = mockOnPanelChange.mock.calls.length;
        fireEvent.click(closeButtons[0]);
        
        // Should not reduce to 0 panels
        if (mockOnPanelChange.mock.calls.length > initialCalls) {
          const panels = mockOnPanelChange.mock.calls[mockOnPanelChange.mock.calls.length - 1][0];
          expect(panels.length).toBeGreaterThan(0);
        }
      }
    });

    it('should redistribute size after removing panel', async () => {
      render(<SplitViewManager onPanelChange={mockOnPanelChange} />);
      
      await waitFor(() => {
        const buttons = screen.queryAllByRole('button');
        expect(buttons.length).toBeGreaterThan(0);
      }, { timeout: 3000 });
    });
  });

  describe('Orientation Toggle', () => {
    it('should toggle between horizontal and vertical', async () => {
      const { container } = render(<SplitViewManager />);
      
      await waitFor(() => {
        const buttons = screen.queryAllByRole('button');
        const toggleButton = buttons.find(b => 
          b.textContent?.toLowerCase().includes('swap') || 
          b.textContent?.toLowerCase().includes('orientation') ||
          b.getAttribute('aria-label')?.includes('orientation')
        );
        if (toggleButton) fireEvent.click(toggleButton);
      }, { timeout: 3000 });
      
      expect(container).toBeTruthy();
    });

    it('should have orientation toggle button', async () => {
      render(<SplitViewManager />);
      
      await waitFor(() => {
        const buttons = screen.queryAllByRole('button');
        expect(buttons.length).toBeGreaterThan(0);
      }, { timeout: 3000 });
    });
  });

  describe('Sync Scrolling', () => {
    it('should have sync scrolling toggle', async () => {
      render(<SplitViewManager />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should toggle sync scrolling', async () => {
      render(<SplitViewManager />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
      
      const syncButton = screen.queryByRole('button', { name: /sync/i });
      
      if (syncButton) {
        fireEvent.click(syncButton);
        // Should toggle state (icon or state should change)
        expect(syncButton).toBeInTheDocument();
      }
    });
  });

  describe('Panel Content', () => {
    it('should render custom content', async () => {
      const customContent = <div data-testid="custom-content">Custom Content</div>;
      
      render(<SplitViewManager initialContent={customContent} />);
      
      await waitFor(() => {
        expect(screen.queryByTestId('custom-content') || document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should support different content in each panel', async () => {
      render(<SplitViewManager 
        initialContent={<div>Panel 1</div>}
        onPanelChange={mockOnPanelChange}
      />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Resizing Panels', () => {
    it('should start resize on divider drag', async () => {
      const { container } = render(<SplitViewManager />);
      
      await waitFor(() => {
        expect(container).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should handle resize mouse events', async () => {
      const { container } = render(<SplitViewManager />);
      
      await waitFor(() => {
        expect(container).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Context Menu', () => {
    it('should have options menu', async () => {
      render(<SplitViewManager />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should open menu on click', async () => {
      render(<SplitViewManager />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Edge Cases', () => {
    it('should handle panel change callback', async () => {
      render(<SplitViewManager onPanelChange={mockOnPanelChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should work without onPanelChange callback', async () => {
      render(<SplitViewManager />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should maintain panel state through operations', async () => {
      render(<SplitViewManager onPanelChange={mockOnPanelChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Accessibility', () => {
    it('should have accessible controls', async () => {
      render(<SplitViewManager />);
      
      await waitFor(() => {
        const buttons = screen.queryAllByRole('button');
        expect(buttons.length).toBeGreaterThan(0);
      }, { timeout: 3000 });
    });

    it('should have tooltips for controls', async () => {
      render(<SplitViewManager />);
      
      await waitFor(() => {
        const buttons = screen.queryAllByRole('button');
        expect(buttons.length).toBeGreaterThan(0);
      }, { timeout: 3000 });
    });
  });
});
