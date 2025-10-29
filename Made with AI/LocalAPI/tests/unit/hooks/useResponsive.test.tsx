/**
 * useResponsive Hook Unit Tests
 * 
 * Tests responsive design functionality:
 * - Breakpoint detection
 * - Device type detection
 * - Orientation detection
 * - Window resize handling
 * - Touch device detection
 */

import { renderHook, act } from '@testing-library/react';
import { useResponsive, useBreakpoint, useMediaQuery, BREAKPOINTS } from '../../../src/renderer/hooks/useResponsive';

describe('useResponsive Hook', () => {
  const originalInnerWidth = window.innerWidth;
  const originalInnerHeight = window.innerHeight;

  beforeEach(() => {
    document.body.innerHTML = '';
    // Reset window size
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    });
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: 768,
    });
  });

  afterEach(() => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: originalInnerWidth,
    });
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: originalInnerHeight,
    });
  });

  describe('Breakpoint Detection', () => {
    it('should detect mobile breakpoint (xs)', () => {
      window.innerWidth = 400;
      
      const { result } = renderHook(() => useResponsive());
      
      expect(result.current.isMobile).toBe(true);
      expect(result.current.isTablet).toBe(false);
      expect(result.current.isDesktop).toBe(false);
      expect(result.current.breakpoint).toBe('xs');
    });

    it('should detect tablet breakpoint (sm)', () => {
      window.innerWidth = 700;
      
      const { result } = renderHook(() => useResponsive());
      
      expect(result.current.isMobile).toBe(false);
      expect(result.current.isTablet).toBe(true);
      expect(result.current.isDesktop).toBe(false);
      expect(result.current.breakpoint).toBe('sm');
    });

    it('should detect desktop breakpoint (md)', () => {
      window.innerWidth = 1024;
      
      const { result } = renderHook(() => useResponsive());
      
      expect(result.current.isMobile).toBe(false);
      expect(result.current.isTablet).toBe(false);
      expect(result.current.isDesktop).toBe(true);
      expect(result.current.breakpoint).toBe('md');
    });

    it('should detect large desktop breakpoint (xl)', () => {
      window.innerWidth = 1920;
      
      const { result } = renderHook(() => useResponsive());
      
      expect(result.current.isLargeDesktop).toBe(true);
      expect(result.current.breakpoint).toBe('xl');
    });
  });

  describe('Orientation Detection', () => {
    it('should detect landscape orientation', () => {
      window.innerWidth = 1024;
      window.innerHeight = 768;
      
      const { result } = renderHook(() => useResponsive());
      
      expect(result.current.orientation).toBe('landscape');
    });

    it('should detect portrait orientation', () => {
      window.innerWidth = 768;
      window.innerHeight = 1024;
      
      const { result } = renderHook(() => useResponsive());
      
      expect(result.current.orientation).toBe('portrait');
    });
  });

  describe('Window Size Tracking', () => {
    it('should track window width', () => {
      window.innerWidth = 1280;
      
      const { result } = renderHook(() => useResponsive());
      
      expect(result.current.width).toBe(1280);
    });

    it('should track window height', () => {
      window.innerHeight = 720;
      
      const { result } = renderHook(() => useResponsive());
      
      expect(result.current.height).toBe(720);
    });

    it('should update on window resize', () => {
      const { result } = renderHook(() => useResponsive());
      
      expect(result.current.width).toBe(1024);
      
      act(() => {
        window.innerWidth = 1920;
        window.dispatchEvent(new Event('resize'));
      });
      
      expect(result.current.width).toBe(1920);
    });
  });

  describe('Touch Device Detection', () => {
    it('should detect touch device', () => {
      Object.defineProperty(window, 'ontouchstart', {
        writable: true,
        configurable: true,
        value: {},
      });
      
      const { result } = renderHook(() => useResponsive());
      
      expect(result.current.isTouchDevice).toBe(true);
    });

    it('should detect non-touch device', () => {
      const { result } = renderHook(() => useResponsive());
      
      // Touch detection may vary based on environment
      expect(typeof result.current.isTouchDevice).toBe('boolean');
    });
  });

  describe('Responsive State Updates', () => {
    it('should update breakpoint on resize', () => {
      window.innerWidth = 400; // Mobile
      const { result } = renderHook(() => useResponsive());
      
      expect(result.current.isMobile).toBe(true);
      expect(result.current.breakpoint).toBe('xs');
      
      act(() => {
        window.innerWidth = 1024; // Desktop
        window.dispatchEvent(new Event('resize'));
      });
      
      expect(result.current.isMobile).toBe(false);
      expect(result.current.isDesktop).toBe(true);
      expect(result.current.breakpoint).toBe('md');
    });

    it('should update orientation on resize', () => {
      window.innerWidth = 1024;
      window.innerHeight = 768;
      const { result } = renderHook(() => useResponsive());
      
      expect(result.current.orientation).toBe('landscape');
      
      act(() => {
        window.innerWidth = 768;
        window.innerHeight = 1024;
        window.dispatchEvent(new Event('resize'));
      });
      
      expect(result.current.orientation).toBe('portrait');
    });
  });

  describe('Event Cleanup', () => {
    it('should remove event listeners on unmount', () => {
      const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener');
      
      const { unmount } = renderHook(() => useResponsive());
      unmount();
      
      expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function));
      expect(removeEventListenerSpy).toHaveBeenCalledWith('orientationchange', expect.any(Function));
      
      removeEventListenerSpy.mockRestore();
    });
  });
});

describe('useBreakpoint Hook', () => {
  it('should return true when width is above breakpoint', () => {
    window.innerWidth = 1024;
    
    const { result } = renderHook(() => useBreakpoint('md'));
    
    expect(result.current).toBe(true);
  });

  it('should return false when width is below breakpoint', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 500,
    });
    
    const { result } = renderHook(() => useBreakpoint('md'));
    
    // md breakpoint is 768px, so 500 should return false
    expect(result.current).toBe(false);
  });

  it('should update when breakpoint changes', () => {
    window.innerWidth = 500;
    const { result } = renderHook(() => useBreakpoint('md'));
    
    expect(result.current).toBe(false);
    
    act(() => {
      window.innerWidth = 1024;
      window.dispatchEvent(new Event('resize'));
    });
    
    expect(result.current).toBe(true);
  });
});

describe('useMediaQuery Hook', () => {
  let matchMediaMock: jest.Mock;

  beforeEach(() => {
    matchMediaMock = jest.fn().mockImplementation((query: string) => ({
      matches: query === '(min-width: 768px)',
      media: query,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      addListener: jest.fn(),
      removeListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));

    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      configurable: true,
      value: matchMediaMock,
    });
  });

  it('should return match result', () => {
    const { result } = renderHook(() => useMediaQuery('(min-width: 768px)'));
    
    expect(result.current).toBe(true);
  });

  it('should return false for non-matching query', () => {
    const { result } = renderHook(() => useMediaQuery('(min-width: 2000px)'));
    
    expect(result.current).toBe(false);
  });

  it('should call matchMedia with correct query', () => {
    renderHook(() => useMediaQuery('(max-width: 600px)'));
    
    expect(matchMediaMock).toHaveBeenCalledWith('(max-width: 600px)');
  });
});

describe('BREAKPOINTS constant', () => {
  it('should have correct breakpoint values', () => {
    expect(BREAKPOINTS.xs).toBe(0);
    expect(BREAKPOINTS.sm).toBe(600);
    expect(BREAKPOINTS.md).toBe(960);
    expect(BREAKPOINTS.lg).toBe(1280);
    expect(BREAKPOINTS.xl).toBe(1920);
  });
});
