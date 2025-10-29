import React, { createContext, useContext, useState, useEffect } from 'react';
import { IUserContext, IUser } from '../types/User';
import { UserService } from '../services/UserService';

const UserContext = createContext<IUserContext | null>(null);

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<IUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const userService = UserService.getInstance();

  useEffect(() => {
    const initializeUser = async () => {
      try {
        // Check if user is already logged in
        const currentUser = userService.getCurrentUser();
        if (currentUser) {
          setUser(currentUser);
        } else {
          // Auto-login with debug user if no user is logged in
          const debugUser = await userService.login('debug-user', 'debug-password');
          setUser(debugUser);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to initialize user');
        console.error('Failed to initialize user:', err);
      } finally {
        setIsLoading(false);
      }
    };

    initializeUser();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const loggedInUser = await userService.login(username, password);
      setUser(loggedInUser);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to login');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    userService.logout();
    setUser(null);
  };

  const value = {
    user,
    isLoading,
    error,
    login,
    logout,
    isAuthenticated: userService.isAuthenticated()
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}; 