import React from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

export const Navbar = ({ user, onLogin, onLogout, onAddCommand }) => {
  return (
    <nav className="navbar-glass sticky top-0 z-40 w-full">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">LX</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 font-['Space_Grotesk']">Linux Toolbox</h1>
              <p className="text-xs text-gray-500">System Administration Made Easy</p>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <Button
                  onClick={onAddCommand}
                  className="btn-hover bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium"
                  data-testid="add-command-btn"
                >
                  + Add Command
                </Button>
                
                <div className="flex items-center space-x-3">
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">{user.username}</div>
                    <div className="text-xs text-gray-500">{user.email}</div>
                  </div>
                  
                  <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-bold">
                      {user.username.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  
                  <Button
                    onClick={onLogout}
                    variant="outline"
                    size="sm"
                    className="btn-hover"
                    data-testid="logout-btn"
                  >
                    Logout
                  </Button>
                </div>
              </>
            ) : (
              <Button
                onClick={onLogin}
                className="btn-hover bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium"
                data-testid="login-btn"
              >
                Sign In
              </Button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};