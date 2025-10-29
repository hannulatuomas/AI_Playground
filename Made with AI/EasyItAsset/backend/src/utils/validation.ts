import { IContainer } from '../types/Container';
import { IAsset } from '../types/Asset';
import { IAssetTypeConfig } from '../types/FieldConfig';

export const validateContainer = (container: Partial<IContainer>): string[] => {
  const errors: string[] = [];
  if (!container.name) errors.push('Container name is required');
  if (!container.ownerId) errors.push('Owner ID is required');
  return errors;
};

export const validateAsset = (asset: Partial<IAsset>): string[] => {
  const errors: string[] = [];
  if (!asset.name) errors.push('Asset name is required');
  if (!asset.containerId) errors.push('Container ID is required');
  if (!asset.assetTypeId) errors.push('Asset type ID is required');
  return errors;
};

export const validateAssetType = (assetType: Partial<IAssetTypeConfig>): string[] => {
  const errors: string[] = [];
  if (!assetType.name) errors.push('Asset type name is required');
  if (!assetType.label) errors.push('Asset type label is required');
  if (!assetType.containerId) errors.push('Container ID is required');
  return errors;
}; 