import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ContainerService } from '../../services/ContainerService';
import { IContainer } from '../../types/Container';
import { useUser } from '../../contexts/UserContext';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { toast } from 'react-toastify';

const ContainerList: React.FC = () => {
  const [containers, setContainers] = useState<IContainer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useUser();
  const containerService = ContainerService.getInstance();

  useEffect(() => {
    const fetchContainers = async () => {
      if (!user) {
        setLoading(false);
        return;
      }

      try {
        const data = await containerService.getContainersByOwner(user.id);
        setContainers(data);
        setError(null);
      } catch (err) {
        setError('Failed to load containers');
        console.error('Error fetching containers:', err);
        toast.error('Failed to load containers');
      } finally {
        setLoading(false);
      }
    };

    fetchContainers();
  }, [user, containerService]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">My Containers</h1>
        <Link
          to="/containers/new"
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium shadow-md hover:shadow-lg transition-all"
        >
          Create New Container
        </Link>
      </div>

      {containers.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">No Containers Yet</h2>
          <p className="text-gray-600 mb-6">Create your first container to start managing your assets.</p>
          <Link
            to="/containers/new"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium shadow-md hover:shadow-lg transition-all"
          >
            Create Your First Container
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {containers.map((container) => (
            <div
              key={container.id}
              className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow"
            >
              <h2 className="text-xl font-semibold mb-2">{container.name}</h2>
              <p className="text-gray-600 mb-4">{container.description}</p>
              <Link
                to={`/containers/${container.id}`}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                View Details
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ContainerList; 