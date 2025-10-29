import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ContainerService } from '../../services/ContainerService';
import { IContainer } from '../../types/Container';
import { IAssetTypeConfig } from '../../types/FieldConfig';
import { AssetList } from '../assets/AssetList';
import AssetTypeList from '../assetTypes/AssetTypeList';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { toast } from 'react-toastify';
import { Tooltip } from '../common/Tooltip';

const ContainerDetails: React.FC = () => {
  const { containerId } = useParams<{ containerId: string }>();
  const navigate = useNavigate();
  const [container, setContainer] = useState<IContainer | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchContainer = async () => {
      if (!containerId) return;
      
      try {
        setIsLoading(true);
        const containerService = ContainerService.getInstance();
        const data = await containerService.getContainer(containerId);
        setContainer(data);
        setError(null);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load container details';
        setError(errorMessage);
        toast.error(errorMessage);
        console.error('Error fetching container:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchContainer();
  }, [containerId]);

  const handleDeleteAssetType = async (typeId: string) => {
    if (!containerId) return;

    try {
      const containerService = ContainerService.getInstance();
      await containerService.deleteAssetTypeConfig(containerId, typeId);
      setContainer(prev => prev ? {
        ...prev,
        assetTypeConfigs: prev.assetTypeConfigs.filter(t => t.id !== typeId)
      } : null);
      toast.success('Asset type deleted successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete asset type';
      toast.error(errorMessage);
      console.error('Error deleting asset type:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (error || !container) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error || 'Container not found'}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{container.name}</h1>
          <p className="text-gray-600 mt-1">{container.description}</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-4">
          <Tooltip
            content={!containerId ? "Select a container first" : ""}
            disabled={!!containerId}
          >
            <button
              onClick={() => navigate(`/containers/${containerId}/assets/new`)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium shadow-md transition-colors duration-200"
              disabled={!containerId}
            >
              Add Asset
            </button>
          </Tooltip>
          <Tooltip
            content={!containerId ? "Select a container first" : ""}
            disabled={!!containerId}
          >
            <button
              onClick={() => navigate(`/containers/${containerId}/asset-types/new`)}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium shadow-md transition-colors duration-200"
              disabled={!containerId}
            >
              Add Asset Type
            </button>
          </Tooltip>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">Assets</h2>
          <AssetList containerId={containerId!} />
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">Asset Types</h2>
          <AssetTypeList
            assetTypes={container.assetTypeConfigs}
            onEdit={(type: IAssetTypeConfig) => navigate(`/containers/${containerId}/asset-types/${type.id}`)}
            onDelete={handleDeleteAssetType}
          />
        </div>
      </div>
    </div>
  );
};

export default ContainerDetails; 