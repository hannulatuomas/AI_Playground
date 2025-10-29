import React, { createContext, useContext, useEffect, useState } from 'react';

interface User {
  id: string;
  email: string;
  emailVerified?: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  googleLogin: () => void;
  resendVerification: (email: string) => Promise<string | null>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Timestamp for last successful fetch of /api/auth/me
  const [lastFetched, setLastFetched] = useState<number>(0);

  // Cache duration in milliseconds (default: 60 seconds)
  const CACHE_DURATION = 60 * 1000;

  // On mount, hydrate user session if not already loaded (one-time check)
  React.useEffect(() => {
    if (!user && !loading) {
      refreshUser();
    }
    // eslint-disable-next-line
  }, []);
  // Protected routes/components should call refreshUser as needed.

  /**
   * Client-side caching for /api/auth/me
   * Only re-fetches if cache is stale or if forced
   * @param force If true, always fetch from server
   */
  const refreshUser = async (force = false) => {
    if (!force && user && Date.now() - lastFetched < CACHE_DURATION) {
      // Use cached user
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('/api/auth/me', { credentials: 'include' });
      if (res.ok) {
        setUser(await res.json());
        setLastFetched(Date.now());
        setError(null);
      } else {
        setUser(null);
        setLastFetched(Date.now());
        setError(null);
      }
    } catch {
      setUser(null);
      setLastFetched(Date.now());
      setError('Network error while checking auth');
    }
    setLoading(false);
  };

  // Utility to force cache invalidation
  const invalidateUserCache = () => setLastFetched(0);

  const resetError = () => setError(null);

  const login = async (email: string, password: string) => {
    resetError();
    setLoading(true);
    invalidateUserCache();
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });
      if (res.ok) {
        const userData = await res.json();
        if (!userData.emailVerified) {
          setError('Please verify your email before logging in.');
          setUser(null);
        } else {
          setUser(userData);
          setError(null);
        }
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data.message || 'Invalid credentials');
        setUser(null);
      }
    } catch (err) {
      setError('Network error during login');
      setUser(null);
    }
    setLoading(false);
  };

  const register = async (email: string, password: string): Promise<boolean> => {
    resetError();
    setLoading(true);
    invalidateUserCache();
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });
      if (res.ok) {
        setError(null);
        setLoading(false);
        return true;
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data.message || 'Registration failed');
        setUser(null);
        setLoading(false);
        return false;
      }
    } catch (err) {
      setError('Network error during registration');
      setUser(null);
      setLoading(false);
      return false;
    }
  };


  const resendVerification = async (email: string) => {
    try {
      const res = await fetch('/api/auth/resend-verification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (res.ok) return data.message || null;
      return data.message || 'Failed to resend verification email';
    } catch {
      return 'Network error while resending verification email';
    }
  };

  const logout = async () => {
    setLoading(true);
    invalidateUserCache();
    try {
      await fetch('/api/auth/logout', { credentials: 'include' });
      setUser(null);
      setError(null);
    } catch {
      setError('Network error during logout');
    }
    setLoading(false);
  };

  const googleLogin = () => {
    window.location.href = '/api/auth/google';
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, login, register, logout, googleLogin, resendVerification, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuthContext must be used within AuthProvider');
  return ctx;
}
