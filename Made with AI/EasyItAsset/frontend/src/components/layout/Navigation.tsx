import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ContainerService } from '../../services/ContainerService';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { toast } from 'react-toastify';

export const Navigation: React.FC = () => {
  const [hasContainers, setHasContainers] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const userId = localStorage.getItem('userId');

  useEffect(() => {
    const checkContainers = async () => {
      if (!userId) {
        setLoading(false);
        return;
      }

      try {
        const containerService = ContainerService.getInstance();
        const containers = await containerService.getContainersByOwner(userId);
        setHasContainers(containers.length > 0);
        setError(null);
      } catch (error) {
        console.error('Error checking containers:', error);
        setError('Failed to load containers');
        toast.error('Failed to load containers');
      } finally {
        setLoading(false);
      }
    };

    checkContainers();
  }, [userId]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('refreshToken');
    navigate('/login');
    toast.success('Logged out successfully');
  };

  if (loading) {
    return (
      <nav className="bg-gray-800 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <LoadingSpinner size="small" color="white" />
        </div>
      </nav>
    );
  }

  const getNavLinkClass = (path: string) => {
    const isActive = location.pathname === path || 
                    (path !== '/' && location.pathname.startsWith(path));
    return `px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
      isActive 
        ? 'bg-gray-900 text-white shadow-md' 
        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
    }`;
  };

  return (
    <nav className="bg-gray-800 text-white p-4 shadow-lg">
      <div className="container mx-auto">
        {error && (
          <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        )}
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-6">
            <Link to="/" className={getNavLinkClass('/')}>
              Home
            </Link>
            {hasContainers ? (
              <>
                <Link to="/containers" className={getNavLinkClass('/containers')}>
                  Containers
                </Link>
                <Link to="/assets" className={getNavLinkClass('/assets')}>
                  Assets
                </Link>
              </>
            ) : (
              <Link 
                to="/containers/new" 
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 shadow-md"
              >
                Create Container
              </Link>
            )}
          </div>
          <div className="flex items-center space-x-4">
            <Link to="/settings" className={getNavLinkClass('/settings')}>
              Settings
            </Link>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 shadow-md"
            >
              Logout
            </button>
            {userId && (
              <span className="text-gray-400 text-sm bg-gray-700 px-3 py-1 rounded-full">
                {userId}
              </span>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}; 