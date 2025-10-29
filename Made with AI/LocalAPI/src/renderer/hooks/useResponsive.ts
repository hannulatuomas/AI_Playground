/**
 * useResponsive Hook - Responsive Design Support
 * 
 * Features:
 * - Breakpoint detection
 * - Mobile/tablet/desktop detection
 * - Orientation detection
 * - Window size tracking
 * - Touch device detection
 */

import { useState, useEffect } from 'react';

export interface ResponsiveState {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isLargeDesktop: boolean;
  width: number;
  height: number;
  orientation: 'portrait' | 'landscape';
  isTouchDevice: boolean;
  breakpoint: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
}

export const BREAKPOINTS = {
  xs: 0,    // Extra small devices (phones)
  sm: 600,  // Small devices (tablets)
  md: 960,  // Medium devices (small laptops)
  lg: 1280, // Large devices (desktops)
  xl: 1920, // Extra large devices (large desktops)
};

export function useResponsive(): ResponsiveState {
  const [state, setState] = useState<ResponsiveState>(() => getResponsiveState());

  useEffect(() => {
    const handleResize = () => {
      setState(getResponsiveState());
    };

    const handleOrientationChange = () => {
      setState(getResponsiveState());
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleOrientationChange);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleOrientationChange);
    };
  }, []);

  return state;
}

function getResponsiveState(): ResponsiveState {
  const width = window.innerWidth;
  const height = window.innerHeight;

  const isMobile = width < BREAKPOINTS.sm;
  const isTablet = width >= BREAKPOINTS.sm && width < BREAKPOINTS.md;
  const isDesktop = width >= BREAKPOINTS.md && width < BREAKPOINTS.xl;
  const isLargeDesktop = width >= BREAKPOINTS.xl;

  const orientation: 'portrait' | 'landscape' = width > height ? 'landscape' : 'portrait';

  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

  let breakpoint: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  if (width < BREAKPOINTS.sm) breakpoint = 'xs';
  else if (width < BREAKPOINTS.md) breakpoint = 'sm';
  else if (width < BREAKPOINTS.lg) breakpoint = 'md';
  else if (width < BREAKPOINTS.xl) breakpoint = 'lg';
  else breakpoint = 'xl';

  return {
    isMobile,
    isTablet,
    isDesktop,
    isLargeDesktop,
    width,
    height,
    orientation,
    isTouchDevice,
    breakpoint,
  };
}

/**
 * Hook for checking specific breakpoint
 */
export function useBreakpoint(breakpoint: keyof typeof BREAKPOINTS): boolean {
  const { width } = useResponsive();
  return width >= BREAKPOINTS[breakpoint];
}

/**
 * Hook for media query
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.matchMedia(query).matches;
    }
    return false;
  });

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    
    const handleChange = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } 
    // Legacy browsers
    else if (mediaQuery.addListener) {
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }

    return undefined;
  }, [query]);

  return matches;
}
