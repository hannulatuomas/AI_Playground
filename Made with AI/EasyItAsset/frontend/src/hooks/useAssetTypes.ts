import { useState, useEffect } from 'react';
import { ContainerService } from '../services/ContainerService';
import { IAssetTypeConfig } from '../types/FieldConfig';

export const useAssetTypes = (containerId: string) => {
  const [assetTypes, setAssetTypes] = useState<IAssetTypeConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAssetTypes = async () => {
      try {
        setLoading(true);
        const data = await ContainerService.getAssetTypeConfigs(containerId);
        setAssetTypes(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch asset types');
      } finally {
        setLoading(false);
      }
    };

    if (containerId) {
      fetchAssetTypes();
    }
  }, [containerId]);

  const addAssetType = async (config: Omit<IAssetTypeConfig, 'id' | 'containerId'>) => {
    try {
      const newAssetType = await ContainerService.addAssetTypeConfig(containerId, config);
      setAssetTypes([...assetTypes, newAssetType]);
      return newAssetType;
    } catch (err) {
      throw err;
    }
  };

  const updateAssetType = async (configId: string, config: Partial<IAssetTypeConfig>) => {
    try {
      const updatedAssetType = await ContainerService.updateAssetTypeConfig(containerId, configId, config);
      setAssetTypes(assetTypes.map(at => at.id === configId ? updatedAssetType : at));
      return updatedAssetType;
    } catch (err) {
      throw err;
    }
  };

  const deleteAssetType = async (configId: string) => {
    try {
      await ContainerService.deleteAssetTypeConfig(containerId, configId);
      setAssetTypes(assetTypes.filter(at => at.id !== configId));
    } catch (err) {
      throw err;
    }
  };

  return {
    assetTypes,
    loading,
    error,
    addAssetType,
    updateAssetType,
    deleteAssetType
  };
}; 