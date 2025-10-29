import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AssetService } from '../../services/AssetService';
import { IAsset } from '../../types/Asset';
import { LoadingSpinner } from '../common/LoadingSpinner';

interface AssetListProps {
  containerId: string;
}

export const AssetList: React.FC<AssetListProps> = ({ containerId }) => {
  const [assets, setAssets] = useState<IAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAssets();
  }, [containerId]);

  const fetchAssets = async () => {
    try {
      setLoading(true);
      const assetService = AssetService.getInstance();
      const loadedAssets = await assetService.getAssets(containerId);
      setAssets(loadedAssets);
      setError(null);
    } catch (err) {
      setError('Failed to load assets');
      console.error('Error loading assets:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Assets</h2>
        <Link
          to={`/containers/${containerId}/assets/new`}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Add Asset
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {assets.map(asset => (
          <div key={asset.id} className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold">{asset.name}</h3>
            <p className="text-gray-600">{asset.label || 'No description'}</p>
            <div className="mt-4 flex space-x-2">
              <Link
                to={`/containers/${containerId}/assets/${asset.id}`}
                className="text-blue-500 hover:text-blue-600"
              >
                View
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}; 