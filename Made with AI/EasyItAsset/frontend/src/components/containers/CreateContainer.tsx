import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ContainerService } from '../../services/ContainerService';
import { AssetTypeForm } from '../assetTypes/AssetTypeForm';
import { IAssetTypeConfig } from '../../types/FieldConfig';
import { validateContainer } from '../../utils/validation';
import { toast } from 'react-toastify';
import { IdUtils } from '../../utils/IdUtils';
import { useUser } from '../../contexts/UserContext';
import { Tooltip } from '../common/Tooltip';
import { IContainer } from '../../types/Container';
import { IAssetType } from '../../types/AssetType';

const CreateContainer: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useUser();
  const [containerName, setContainerName] = useState('');
  const [containerDescription, setContainerDescription] = useState('');
  const [assetTypes, setAssetTypes] = useState<IAssetTypeConfig[]>([]);
  const [showAssetTypeForm, setShowAssetTypeForm] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [container, setContainer] = useState<IContainer | null>(null);
  const [editingAssetType, setEditingAssetType] = useState<IAssetTypeConfig | null>(null);

  useEffect(() => {
    if (!user) {
      toast.error('User must be logged in to create a container');
      navigate('/login');
      return;
    }

    const now = new Date().toISOString();
    const containerId = IdUtils.generateContainerId(user.id);
    
    const newContainer: IContainer = {
      id: containerId,
      name: '',
      description: '',
      ownerId: user.id,
      assetTypeConfigs: [],
      assets: [],
      createdAt: now,
      updatedAt: now
    };

    setContainer(newContainer);
  }, [user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors([]);

    try {
      if (!user || !container) {
        throw new Error('User must be logged in to create a container');
      }

      const containerData = {
        ...container,
        name: containerName,
        description: containerDescription,
        assetTypeConfigs: assetTypes,
        updatedAt: new Date().toISOString()
      };

      const validationErrors = validateContainer(containerData);

      if (validationErrors.length > 0) {
        setErrors(validationErrors);
        validationErrors.forEach(error => toast.error(error));
        return;
      }

      const containerService = ContainerService.getInstance();
      const savedContainer = await containerService.createContainer(containerData);

      toast.success('Container created successfully!');
      navigate(`/containers/${savedContainer.id}`);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create container';
      setErrors([errorMessage]);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAssetTypeSubmit = (assetType: IAssetType) => {
    const now = new Date().toISOString();
    const assetTypeConfig: IAssetTypeConfig = {
      id: assetType.id,
      name: assetType.name,
      label: assetType.label || assetType.name,
      fields: assetType.fields.map(field => ({
        id: field.id,
        name: field.name,
        label: field.label || field.name,
        type: field.type,
        required: field.required || false,
        defaultValue: field.defaultValue,
        options: field.options,
        length: field.length,
        pattern: field.pattern,
        min: field.min,
        max: field.max,
        step: field.step,
        minDate: field.minDate,
        maxDate: field.maxDate,
        parentTypeId: field.parentTypeId,
        createdAt: field.createdAt || now,
        updatedAt: field.updatedAt || now
      })),
      subtypes: assetType.subtypes.map(subtype => ({
        id: subtype.id,
        name: subtype.name,
        label: subtype.label || subtype.name,
        parentTypeId: subtype.parentTypeId,
        fields: subtype.fields.map(field => ({
          id: field.id,
          name: field.name,
          label: field.label || field.name,
          type: field.type,
          required: field.required || false,
          defaultValue: field.defaultValue,
          options: field.options,
          length: field.length,
          pattern: field.pattern,
          min: field.min,
          max: field.max,
          step: field.step,
          minDate: field.minDate,
          maxDate: field.maxDate,
          parentTypeId: field.parentTypeId,
          createdAt: field.createdAt || now,
          updatedAt: field.updatedAt || now
        })),
        hiddenFields: subtype.hiddenFields || [],
        overriddenFields: subtype.overriddenFields || [],
        createdAt: subtype.createdAt || now,
        updatedAt: subtype.updatedAt || now
      })),
      createdAt: assetType.createdAt || now,
      updatedAt: assetType.updatedAt || now
    };

    if (editingAssetType) {
      setAssetTypes(prev => prev.map(at => at.id === assetTypeConfig.id ? assetTypeConfig : at));
    } else {
      setAssetTypes(prev => [...prev, assetTypeConfig]);
    }
    setEditingAssetType(null);
    setShowAssetTypeForm(false);
  };

  const handleEditAssetType = (assetType: IAssetTypeConfig) => {
    setEditingAssetType(assetType);
    setShowAssetTypeForm(true);
  };

  const handleRemoveAssetType = (assetTypeId: string) => {
    setAssetTypes(prev => prev.filter(at => at.id !== assetTypeId));
  };

  const canSave = containerName.trim() !== '' && assetTypes.length > 0;

  if (!container) {
    return <div>Loading...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Create New Container</h1>
      {errors.length > 0 && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <ul>
            {errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="containerName" className="block text-sm font-medium text-gray-700">
            Container Name
          </label>
          <input
            type="text"
            id="containerName"
            value={containerName}
            onChange={(e) => setContainerName(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
            required
            disabled={isLoading}
          />
        </div>
        <div>
          <label htmlFor="containerDescription" className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <textarea
            id="containerDescription"
            value={containerDescription}
            onChange={(e) => setContainerDescription(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
            rows={3}
            disabled={isLoading}
          />
        </div>
        
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-medium text-gray-900">Asset Types</h2>
            <button
              type="button"
              onClick={() => setShowAssetTypeForm(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              disabled={isLoading}
            >
              Add Asset Type
            </button>
          </div>

          {assetTypes.length > 0 ? (
            <ul className="space-y-2">
              {assetTypes.map((type) => (
                <li key={type.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span>{type.label || type.name}</span>
                  <div className="flex space-x-2">
                    <button
                      type="button"
                      onClick={() => handleEditAssetType(type)}
                      className="px-2 py-1 text-xs bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                      disabled={isLoading}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      onClick={() => handleRemoveAssetType(type.id)}
                      className="px-2 py-1 text-xs bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                      disabled={isLoading}
                    >
                      Remove
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-center text-sm text-gray-500 italic py-2 bg-white rounded-md border border-gray-200">
              No asset types added yet
            </p>
          )}
        </div>

        <div className="flex justify-end space-x-2">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            disabled={isLoading}
          >
            Cancel
          </button>
          <Tooltip
            content={!canSave ? "Container must have a name and at least one asset type" : ""}
            disabled={canSave}
          >
            <button
              type="submit"
              disabled={!canSave || isLoading}
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white ${
                canSave ? 'bg-green-600 hover:bg-green-700 focus:ring-green-500' : 'bg-gray-400 cursor-not-allowed'
              } focus:outline-none focus:ring-2 focus:ring-offset-2`}
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating...
                </>
              ) : (
                'Create Container'
              )}
            </button>
          </Tooltip>
        </div>
      </form>
      
      {showAssetTypeForm && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <AssetTypeForm
              containerId={container.id}
              assetType={editingAssetType || undefined}
              onSave={handleAssetTypeSubmit}
              onCancel={() => {
                setShowAssetTypeForm(false);
                setEditingAssetType(null);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default CreateContainer; 