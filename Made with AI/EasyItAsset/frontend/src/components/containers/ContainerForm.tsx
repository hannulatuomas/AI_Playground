import React, { useState, useEffect } from 'react';
import { ContainerService } from '../../services/ContainerService';
import { AssetTypeService } from '../../services/AssetTypeService';
import { IContainer } from '../../types/Container';
import { IAssetTypeConfig } from '../../types/FieldConfig';
import { IAssetType } from '../../types/AssetType';
import { useUser } from '../../contexts/UserContext';
import { toast } from 'react-toastify';
import { LoadingSpinner } from '../common/LoadingSpinner';

interface ContainerFormProps {
  container?: IContainer;
  assetTypeData?: Partial<IAssetTypeConfig>;
  onSave: () => void;
  onCancel: () => void;
}

export const ContainerForm: React.FC<ContainerFormProps> = ({
  container,
  assetTypeData,
  onSave,
  onCancel
}) => {
  const [name, setName] = useState(container?.name || '');
  const [description, setDescription] = useState(container?.description || '');
  const [ownerId, setOwnerId] = useState(container?.ownerId || '');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [editingAssetType, setEditingAssetType] = useState<IAssetTypeConfig | undefined>(undefined);
  const [showAssetTypeForm, setShowAssetTypeForm] = useState(false);
  const [currentAssetTypeId, setCurrentAssetTypeId] = useState<string | undefined>(undefined);
  const [assetTypes, setAssetTypes] = useState<IAssetTypeConfig[]>([]);
  const { user } = useUser();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const containerService = ContainerService.getInstance();
      const assetTypeService = AssetTypeService.getInstance();

      // If this is a new container, create it first
      let containerId = container?.id;
      if (!containerId) {
        const newContainer = await containerService.createContainer({
          name,
          description,
          ownerId,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          assetTypeConfigs: [],
          assets: []
        });
        containerId = newContainer.id;
      } else {
        // Update existing container
        await containerService.updateContainer(containerId, {
          name,
          description,
          ownerId,
          updatedAt: new Date().toISOString(),
          assets: container?.assets || []
        });
      }

      // If we have asset type data, create it
      if (assetTypeData) {
        try {
          await assetTypeService.saveAssetType(containerId, assetTypeData as IAssetType);
          toast.success('Container and asset type created successfully');
        } catch (assetTypeError) {
          console.error('Error creating asset type:', assetTypeError);
          toast.error('Container created, but failed to create asset type');
        }
      } else {
        toast.success('Container saved successfully');
      }

      onSave();
    } catch (error) {
      console.error('Error saving container:', error);
      setError(error instanceof Error ? error.message : 'Failed to save container');
      toast.error('Failed to save container');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAssetTypeSave = (assetType: IAssetType) => {
    const assetTypeConfig: IAssetTypeConfig = {
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
    };

    if (editingAssetType) {
      setAssetTypes(assetTypes.map(at => at.id === assetTypeConfig.id ? assetTypeConfig : at));
    } else {
      setAssetTypes([...assetTypes, assetTypeConfig]);
    }
    setEditingAssetType(undefined);
    setShowAssetTypeForm(false);
  };

  const handleAssetTypeCancel = () => {
    // If we were editing an existing asset type, just close the form
    // If we were creating a new one, remove it from the list
    if (!editingAssetType) {
      setAssetTypes(assetTypes.filter(at => at.id !== currentAssetTypeId));
    }
    setEditingAssetType(undefined);
    setShowAssetTypeForm(false);
  };

  const handleAddAssetType = () => {
    const newId = `u-${user?.id}-c-${container?.id}-at-${Date.now()}`;
    setCurrentAssetTypeId(newId);
    setEditingAssetType(undefined);
    setShowAssetTypeForm(true);
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
          Name
        </label>
        <input
          type="text"
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          required
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          rows={3}
          required
        />
      </div>

      <div>
        <label htmlFor="ownerId" className="block text-sm font-medium text-gray-700">
          Owner ID
        </label>
        <input
          type="text"
          id="ownerId"
          value={ownerId}
          onChange={(e) => setOwnerId(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          required
        />
      </div>

      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Save
        </button>
      </div>
    </form>
  );
}; 