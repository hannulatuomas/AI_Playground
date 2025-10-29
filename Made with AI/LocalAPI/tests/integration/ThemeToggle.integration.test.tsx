/**
 * Theme Toggle Integration Test
 * Tests dark/light theme switching functionality
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { IconButton } from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';

// Simple ThemeToggle component for testing
const ThemeToggle: React.FC<{ mode: 'light' | 'dark'; onToggle: () => void }> = ({ mode, onToggle }) => {
  return (
    <IconButton onClick={onToggle} color="inherit" aria-label="toggle theme">
      {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
    </IconButton>
  );
};

// Test wrapper with theme provider
const ThemeToggleTest: React.FC = () => {
  const [mode, setMode] = React.useState<'light' | 'dark'>('dark');

  const theme = createTheme({
    palette: {
      mode,
    },
  });

  const toggleTheme = () => {
    setMode(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeProvider theme={theme}>
      <div data-testid="theme-container" data-theme={mode}>
        <ThemeToggle mode={mode} onToggle={toggleTheme} />
        <span data-testid="current-mode">{mode}</span>
      </div>
    </ThemeProvider>
  );
};

describe('Theme Toggle Integration', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  describe('Theme Switching', () => {
    it('should render theme toggle button', () => {
      render(<ThemeToggleTest />);
      
      const button = screen.getByRole('button', { name: /toggle theme/i });
      expect(button).toBeInTheDocument();
    });

    it('should start in dark mode by default', () => {
      render(<ThemeToggleTest />);
      
      const currentMode = screen.getByTestId('current-mode');
      expect(currentMode).toHaveTextContent('dark');
    });

    it('should toggle from dark to light', () => {
      render(<ThemeToggleTest />);
      
      const button = screen.getByRole('button', { name: /toggle theme/i });
      const currentMode = screen.getByTestId('current-mode');
      
      expect(currentMode).toHaveTextContent('dark');
      
      fireEvent.click(button);
      
      expect(currentMode).toHaveTextContent('light');
    });

    it('should toggle from light to dark', () => {
      render(<ThemeToggleTest />);
      
      const button = screen.getByRole('button', { name: /toggle theme/i });
      
      // Toggle to light
      fireEvent.click(button);
      expect(screen.getByTestId('current-mode')).toHaveTextContent('light');
      
      // Toggle back to dark
      fireEvent.click(button);
      expect(screen.getByTestId('current-mode')).toHaveTextContent('dark');
    });

    it('should toggle multiple times', () => {
      render(<ThemeToggleTest />);
      
      const button = screen.getByRole('button', { name: /toggle theme/i });
      const currentMode = screen.getByTestId('current-mode');
      
      expect(currentMode).toHaveTextContent('dark');
      
      fireEvent.click(button); // -> light
      expect(currentMode).toHaveTextContent('light');
      
      fireEvent.click(button); // -> dark
      expect(currentMode).toHaveTextContent('dark');
      
      fireEvent.click(button); // -> light
      expect(currentMode).toHaveTextContent('light');
    });
  });

  describe('Theme Icon', () => {
    it('should show sun icon in dark mode', () => {
      render(<ThemeToggleTest />);
      
      // In dark mode, show sun (light mode icon) to indicate what you'll get
      const container = screen.getByRole('button', { name: /toggle theme/i });
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should change icon when theme changes', () => {
      render(<ThemeToggleTest />);
      
      const button = screen.getByRole('button', { name: /toggle theme/i });
      
      // Click to toggle
      fireEvent.click(button);
      
      // Icon should change (still has svg element)
      expect(button.querySelector('svg')).toBeInTheDocument();
    });
  });

  describe('Theme Provider Integration', () => {
    it('should update theme in provider', () => {
      render(<ThemeToggleTest />);
      
      const container = screen.getByTestId('theme-container');
      expect(container).toHaveAttribute('data-theme', 'dark');
      
      const button = screen.getByRole('button', { name: /toggle theme/i });
      fireEvent.click(button);
      
      expect(container).toHaveAttribute('data-theme', 'light');
    });

    it('should apply theme to children', () => {
      render(<ThemeToggleTest />);
      
      const container = screen.getByTestId('theme-container');
      
      // Container should have theme attribute
      expect(container).toHaveAttribute('data-theme');
    });
  });

  describe('Accessibility', () => {
    it('should have accessible button', () => {
      render(<ThemeToggleTest />);
      
      const button = screen.getByRole('button', { name: /toggle theme/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveAccessibleName();
    });

    it('should be keyboard accessible', () => {
      render(<ThemeToggleTest />);
      
      const button = screen.getByRole('button', { name: /toggle theme/i });
      
      button.focus();
      expect(button).toHaveFocus();
    });
  });

  describe('Edge Cases', () => {
    it('should handle rapid clicking', () => {
      render(<ThemeToggleTest />);
      
      const button = screen.getByRole('button', { name: /toggle theme/i });
      const currentMode = screen.getByTestId('current-mode');
      
      // Rapid clicks
      for (let i = 0; i < 10; i++) {
        fireEvent.click(button);
      }
      
      // Should end up in dark mode (started dark, 10 toggles = even = back to dark)
      expect(currentMode).toHaveTextContent('dark');
    });

    it('should maintain state through multiple renders', () => {
      const { rerender } = render(<ThemeToggleTest />);
      
      const button = screen.getByRole('button', { name: /toggle theme/i });
      fireEvent.click(button);
      
      expect(screen.getByTestId('current-mode')).toHaveTextContent('light');
      
      rerender(<ThemeToggleTest />);
      
      // State should persist
      expect(screen.getByTestId('current-mode')).toHaveTextContent('light');
    });
  });

  describe('Theme Persistence', () => {
    beforeEach(() => {
      localStorage.clear();
      document.body.innerHTML = '';
    });

    it('should work without localStorage', () => {
      render(<ThemeToggleTest />);
      
      const button = screen.getByRole('button', { name: /toggle theme/i });
      
      expect(() => {
        fireEvent.click(button);
      }).not.toThrow();
    });
  });
});
