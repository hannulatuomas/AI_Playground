import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { IAsset } from '../types/Asset';
import { AssetService } from '../services/AssetService';

interface UseAssetResult {
  asset: IAsset | undefined;
  isLoading: boolean;
  error: Error | null;
  saveAsset: (asset: IAsset) => Promise<void>;
  deleteAsset: () => Promise<void>;
}

export const useAsset = (containerId: string, assetId?: string): UseAssetResult => {
  const [asset, setAsset] = useState<IAsset | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const loadAsset = async () => {
      if (assetId) {
        try {
          setIsLoading(true);
          setError(null);
          const assetService = AssetService.getInstance();
          const data = await assetService.getAsset(containerId, assetId);
          setAsset(data);
        } catch (err) {
          const error = err instanceof Error ? err : new Error('Failed to load asset');
          setError(error);
          toast.error('Failed to load asset');
        } finally {
          setIsLoading(false);
        }
      }
    };

    loadAsset();
  }, [containerId, assetId]);

  const saveAsset = async (assetData: IAsset) => {
    try {
      setIsLoading(true);
      setError(null);
      const assetService = AssetService.getInstance();
      const updatedAsset = assetId
        ? await assetService.updateAsset(containerId, assetId, assetData)
        : await assetService.createAsset(containerId, assetData);
      setAsset(updatedAsset);
      toast.success('Asset saved successfully');
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to save asset');
      setError(error);
      toast.error('Failed to save asset');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const deleteAsset = async () => {
    if (!assetId) return;

    try {
      setIsLoading(true);
      setError(null);
      const assetService = AssetService.getInstance();
      await assetService.deleteAsset(containerId, assetId);
      toast.success('Asset deleted successfully');
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to delete asset');
      setError(error);
      toast.error('Failed to delete asset');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return { asset, isLoading, error, saveAsset, deleteAsset };
}; 