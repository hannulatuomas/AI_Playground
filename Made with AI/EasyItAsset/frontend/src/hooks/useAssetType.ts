import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { IAssetType } from '../types/AssetType';
import { ContainerService } from '../services/ContainerService';

interface UseAssetTypeResult {
  assetType: IAssetType | undefined;
  isLoading: boolean;
  error: Error | null;
  saveAssetType: (assetType: IAssetType) => Promise<void>;
}

export const useAssetType = (containerId: string, assetTypeId?: string): UseAssetTypeResult => {
  const [assetType, setAssetType] = useState<IAssetType | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const loadAssetType = async () => {
      if (containerId && assetTypeId) {
        try {
          setIsLoading(true);
          setError(null);
          const containerService = ContainerService.getInstance();
          const container = await containerService.getContainer(containerId);
          const assetTypeConfig = container.assetTypeConfigs.find(at => at.id === assetTypeId);
          if (assetTypeConfig) {
            setAssetType({
              id: assetTypeConfig.id,
              name: assetTypeConfig.name,
              label: assetTypeConfig.label || assetTypeConfig.name,
              fields: assetTypeConfig.fields,
              subtypes: assetTypeConfig.subtypes.map(subtype => ({
                id: subtype.id,
                name: subtype.name,
                label: subtype.label || subtype.name,
                parentTypeId: subtype.parentTypeId,
                fields: subtype.fields,
                hiddenFields: subtype.hiddenFields || [],
                overriddenFields: subtype.overriddenFields || [],
                createdAt: subtype.createdAt,
                updatedAt: subtype.updatedAt
              })),
              createdAt: assetTypeConfig.createdAt,
              updatedAt: assetTypeConfig.updatedAt
            });
          }
        } catch (err) {
          const error = err instanceof Error ? err : new Error('Failed to load asset type');
          setError(error);
          toast.error('Failed to load asset type');
        } finally {
          setIsLoading(false);
        }
      }
    };

    loadAssetType();
  }, [containerId, assetTypeId]);

  const saveAssetType = async (assetType: IAssetType) => {
    try {
      setIsLoading(true);
      setError(null);
      const containerService = ContainerService.getInstance();
      const container = await containerService.getContainer(containerId);
      const updatedConfigs = container.assetTypeConfigs.map(at => 
        at.id === assetType.id ? {
          id: assetType.id,
          name: assetType.name,
          label: assetType.label || assetType.name,
          fields: assetType.fields,
          subtypes: assetType.subtypes.map(subtype => ({
            id: subtype.id,
            name: subtype.name,
            label: subtype.label || subtype.name,
            parentTypeId: subtype.parentTypeId,
            fields: subtype.fields,
            hiddenFields: subtype.hiddenFields || [],
            overriddenFields: subtype.overriddenFields || [],
            createdAt: subtype.createdAt,
            updatedAt: subtype.updatedAt
          })),
          createdAt: assetType.createdAt,
          updatedAt: assetType.updatedAt
        } : at
      );
      await containerService.updateContainer(containerId, {
        ...container,
        assetTypeConfigs: updatedConfigs
      });
      toast.success('Asset type saved successfully');
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to save asset type');
      setError(error);
      toast.error('Failed to save asset type');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return { assetType, isLoading, error, saveAssetType };
}; 