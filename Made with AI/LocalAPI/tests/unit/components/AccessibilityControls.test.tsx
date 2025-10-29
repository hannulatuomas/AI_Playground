/**
 * AccessibilityControls Component Unit Tests - FIXED
 * Matches actual component API: onSettingsChange prop
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AccessibilityControls } from '../../../src/renderer/components/AccessibilityControls';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('AccessibilityControls', () => {
  const mockOnSettingsChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.clear();
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  describe('Rendering', () => {
    it('should render accessibility controls', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      expect(screen.getByText(/Accessibility Settings/i)).toBeInTheDocument();
    });

    it('should render font size controls', () => {
      const { container } = render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      expect(container.textContent).toContain('Font Size');
      expect(screen.getByRole('slider')).toBeInTheDocument();
    });

    it('should render high contrast toggle', () => {
      const { container } = render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      expect(container.textContent).toContain('High Contrast Mode');
    });

    it('should render reduced motion toggle', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      expect(screen.getByText(/Reduce Motion/i)).toBeInTheDocument();
    });
  });

  describe('Font Size Controls', () => {
    it('should change font size with slider', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      const slider = screen.getByRole('slider');
      fireEvent.change(slider, { target: { value: '18' } });
      
      // Should show preview mode
      expect(screen.queryByText(/Preview mode active/i)).toBeInTheDocument();
    });

    it('should have font size presets', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      // Should have preset buttons
      const buttons = screen.getAllByRole('button');
      const buttonTexts = buttons.map(b => b.textContent);
      expect(buttonTexts.some(t => t?.includes('Small'))).toBe(true);
      expect(buttonTexts.some(t => t?.includes('Medium'))).toBe(true);
      expect(buttonTexts.some(t => t?.includes('Large'))).toBe(true);
    });

    it('should click font size preset', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      const buttons = screen.getAllByRole('button');
      const largeButton = buttons.find(b => b.textContent?.includes('Large') && !b.textContent?.includes('X'));
      if (largeButton) fireEvent.click(largeButton);
      
      // Should activate preview mode
      expect(screen.getByText(/Preview mode active/i)).toBeInTheDocument();
    });

    it('should show preview text', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      expect(screen.getByText(/The quick brown fox/i)).toBeInTheDocument();
    });
  });

  describe('High Contrast Mode', () => {
    it('should toggle high contrast', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      const switches = screen.getAllByRole('checkbox');
      const highContrastSwitch = switches[0]; // First switch is high contrast
      
      fireEvent.click(highContrastSwitch);
      
      expect(screen.getByText(/Preview mode active/i)).toBeInTheDocument();
    });

    it('should show warning when high contrast enabled', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      const switches = screen.getAllByRole('checkbox');
      fireEvent.click(switches[0]);
      
      expect(screen.getByText(/strong colors that may override your theme/i)).toBeInTheDocument();
    });
  });

  describe('Reduced Motion', () => {
    it('should toggle reduced motion', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      const switches = screen.getAllByRole('checkbox');
      const reducedMotionSwitch = switches[1]; // Second switch is reduced motion
      
      fireEvent.click(reducedMotionSwitch);
      
      expect(screen.getByText(/Preview mode active/i)).toBeInTheDocument();
    });
  });

  describe('Save and Reset', () => {
    it('should have save changes button', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      expect(screen.getByRole('button', { name: /Save Changes/i })).toBeInTheDocument();
    });

    it('should have reset button', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      expect(screen.getByRole('button', { name: /Reset to Defaults/i })).toBeInTheDocument();
    });

    it('should save settings and call callback', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      // Make a change
      const slider = screen.getByRole('slider');
      fireEvent.change(slider, { target: { value: '18' } });
      
      // Save
      const saveButton = screen.getByRole('button', { name: /Save Changes/i });
      fireEvent.click(saveButton);
      
      expect(mockOnSettingsChange).toHaveBeenCalledWith(expect.objectContaining({
        fontSize: expect.any(Number),
        highContrast: expect.any(Boolean),
        reducedMotion: expect.any(Boolean),
      }));
    });

    it('should reset to defaults', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      // Make a change
      const slider = screen.getByRole('slider');
      fireEvent.change(slider, { target: { value: '20' } });
      
      // Reset
      const resetButton = screen.getByRole('button', { name: /Reset to Defaults/i });
      fireEvent.click(resetButton);
      
      // Preview mode should be gone
      expect(screen.queryByText(/Preview mode active/i)).not.toBeInTheDocument();
    });
  });

  describe('Keyboard Shortcuts Reference', () => {
    it('should show keyboard shortcuts', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      expect(screen.getByText(/Keyboard Shortcuts for Accessibility/i)).toBeInTheDocument();
      expect(screen.getByText(/Ctrl \+ Plus/i)).toBeInTheDocument();
    });
  });

  describe('Persistence', () => {
    it('should save settings to localStorage', () => {
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      // Make changes
      const slider = screen.getByRole('slider');
      fireEvent.change(slider, { target: { value: '18' } });
      
      // Save
      const saveButton = screen.getByRole('button', { name: /Save Changes/i });
      fireEvent.click(saveButton);
      
      // Check localStorage
      const saved = localStorageMock.getItem('accessibility-settings');
      expect(saved).toBeTruthy();
      expect(JSON.parse(saved!).fontSize).toBe(18);
    });

    it('should load saved settings', () => {
      // Pre-populate localStorage
      localStorageMock.setItem('accessibility-settings', JSON.stringify({
        fontSize: 20,
        highContrast: true,
        reducedMotion: false,
      }));
      
      render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      
      // Should show the saved font size
      expect(screen.getByText(/20px/i)).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should work without callback', () => {
      expect(() => {
        render(<AccessibilityControls />);
      }).not.toThrow();
    });

    it('should handle invalid localStorage data', () => {
      localStorageMock.setItem('accessibility-settings', 'invalid json');
      
      expect(() => {
        render(<AccessibilityControls onSettingsChange={mockOnSettingsChange} />);
      }).not.toThrow();
    });
  });
});
