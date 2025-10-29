import React, { useState, useEffect } from 'react';
import { IAsset } from '../../types/Asset';
import { IAssetTypeConfig } from '../../types/FieldConfig';
import { AssetService } from '../../services/AssetService';
import { AssetTypeService } from '../../services/AssetTypeService';

interface AssetTableProps {
  containerId: string;
  onEditAsset?: (asset: IAsset) => void;
  onDeleteAsset?: (assetId: string) => void;
}

export const AssetTable: React.FC<AssetTableProps> = ({ containerId, onEditAsset, onDeleteAsset }) => {
  const [assets, setAssets] = useState<IAsset[]>([]);
  const [assetTypes, setAssetTypes] = useState<IAssetTypeConfig[]>([]);
  const [selectedType, setSelectedType] = useState<string>('');
  const [selectedSubType, setSelectedSubType] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAssets();
    loadAssetTypes();
  }, [containerId]);

  const loadAssets = async () => {
    try {
      setLoading(true);
      const loadedAssets = await AssetService.getAssets(containerId);
      setAssets(loadedAssets);
      setError(null);
    } catch (err) {
      setError('Failed to load assets. Please try again later.');
      console.error('Error loading assets:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadAssetTypes = async () => {
    try {
      const loadedTypes = await AssetTypeService.getAssetTypes(containerId);
      setAssetTypes(loadedTypes);
    } catch (err) {
      console.error('Error loading asset types:', err);
    }
  };

  const handleDelete = async (assetId: string) => {
    if (window.confirm('Are you sure you want to delete this asset?')) {
      try {
        await AssetService.deleteAsset(containerId, assetId);
        setAssets(assets.filter(asset => asset.id !== assetId));
        if (onDeleteAsset) {
          onDeleteAsset(assetId);
        }
      } catch (err) {
        setError('Failed to delete asset. Please try again later.');
        console.error('Error deleting asset:', err);
      }
    }
  };

  const filteredAssets = assets.filter(asset => {
    const matchesType = !selectedType || asset.assetTypeId === selectedType;
    const matchesSubType = !selectedSubType || asset.assetSubTypeId === selectedSubType;
    const matchesSearch = !searchTerm || 
      asset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      Object.values(asset.values).some(value => 
        value?.toString().toLowerCase().includes(searchTerm.toLowerCase())
      );
    return matchesType && matchesSubType && matchesSearch;
  });

  const currentType = assetTypes.find(t => t.id === selectedType);

  return (
    <div className="mt-4">
      <div className="flex flex-col md:flex-row gap-4 mb-4">
        <div className="flex-1">
          <label htmlFor="search" className="block text-sm font-medium text-gray-700">
            Search
          </label>
          <input
            type="text"
            id="search"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="Search assets..."
          />
        </div>
        <div className="flex-1">
          <label htmlFor="assetType" className="block text-sm font-medium text-gray-700">
            Asset Type
          </label>
          <select
            id="assetType"
            value={selectedType}
            onChange={(e) => {
              setSelectedType(e.target.value);
              setSelectedSubType('');
            }}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option value="">All Types</option>
            {assetTypes.map(type => (
              <option key={type.id} value={type.id}>
                {type.label}
              </option>
            ))}
          </select>
        </div>
        {currentType?.subtypes?.length && (
          <div className="flex-1">
            <label htmlFor="subType" className="block text-sm font-medium text-gray-700">
              Subtype
            </label>
            <select
              id="subType"
              value={selectedSubType}
              onChange={(e) => setSelectedSubType(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option value="">All Subtypes</option>
              {currentType.subtypes.map(subtype => (
                <option key={subtype.id} value={subtype.id}>
                  {subtype.label}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4 mb-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">{error}</h3>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-4">Loading assets...</div>
      ) : filteredAssets.length === 0 ? (
        <div className="text-center py-4">No assets found</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Subtype
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Properties
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredAssets.map(asset => {
                const assetType = assetTypes.find(t => t.id === asset.assetTypeId);
                const subtype = assetType?.subtypes?.find(s => s.id === asset.assetSubTypeId);
                return (
                  <tr key={asset.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {asset.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {assetType?.label || 'Unknown'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {subtype?.label || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      <div className="space-y-1">
                        {Object.entries(asset.values).map(([key, value]) => (
                          <div key={key}>
                            <span className="font-medium">{key}:</span> {value?.toString() || '-'}
                          </div>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {onEditAsset && (
                        <button
                          onClick={() => onEditAsset(asset)}
                          className="text-indigo-600 hover:text-indigo-900 mr-4"
                        >
                          Edit
                        </button>
                      )}
                      {onDeleteAsset && (
                        <button
                          onClick={() => handleDelete(asset.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}; 