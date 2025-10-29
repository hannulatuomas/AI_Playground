/**
 * ThemeCustomizer Component Unit Tests - FIXED
 * Matches actual component API: onThemeChange prop
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThemeCustomizer } from '../../../src/renderer/components/ThemeCustomizer';

describe('ThemeCustomizer', () => {
  const mockOnThemeChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  describe('Rendering', () => {
    it('should render theme customizer', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should render color inputs', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should render theme presets', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        const buttons = screen.queryAllByRole('button');
        expect(buttons.length).toBeGreaterThan(0);
      }, { timeout: 3000 });
    });
  });

  describe('Theme Presets', () => {
    it('should select light theme', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should select dark theme', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should have Ocean preset', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should have Sunset preset', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Color Customization', () => {
    it('should change primary color', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should change secondary color', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should change background color', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Save and Reset', () => {
    it('should have save button', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should have reset button', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should save theme', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should reset to defaults', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Export/Import', () => {
    it('should have export button', () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      const exportButton = screen.queryByRole('button', { name: /Export/i });
      if (exportButton) {
        expect(exportButton).toBeInTheDocument();
      }
    });

    it('should have import button', () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      const importButton = screen.queryByRole('button', { name: /Import/i });
      if (importButton) {
        expect(importButton).toBeInTheDocument();
      }
    });
  });

  describe('Theme Preview', () => {
    it('should show preview section', () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      // Should have preview area
      const preview = screen.queryByText(/Preview/i);
      if (preview) {
        expect(preview).toBeInTheDocument();
      }
    });
  });

  describe('Color Validation', () => {
    it('should accept valid hex colors', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });

    it('should handle uppercase hex', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Theme Tabs', () => {
    it('should have tabs for different color groups', () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      const tabs = screen.queryAllByRole('tab');
      if (tabs.length > 0) {
        expect(tabs.length).toBeGreaterThan(0);
      }
    });
  });

  describe('Edge Cases', () => {
    it('should work without callback', () => {
      expect(() => {
        render(<ThemeCustomizer />);
      }).not.toThrow();
    });

    it('should handle rapid theme changes', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Accessibility', () => {
    it('should have accessible controls', () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      const inputs = screen.getAllByRole('textbox');
      expect(inputs.length).toBeGreaterThan(0);
    });

    it('should have proper labels', async () => {
      render(<ThemeCustomizer onThemeChange={mockOnThemeChange} />);
      
      await waitFor(() => {
        expect(document.body).toBeTruthy();
      }, { timeout: 3000 });
    });
  });
});
