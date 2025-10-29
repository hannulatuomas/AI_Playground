import React, { useState, useEffect } from 'react';
import { IAsset } from '../../types/Asset';
import { IAssetType } from '../../types/AssetType';
import { IAssetTypeConfig, IFieldConfig, FieldType } from '../../types/FieldConfig';
import { AssetService } from '../../services/AssetService';
import { AssetTypeService } from '../../services/AssetTypeService';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { validateField } from '../../utils/fieldValidation';
import { toast } from 'react-toastify';

interface AssetFormProps {
  containerId: string;
  asset?: IAsset;
  onSave: (asset: IAsset) => void;
  onCancel: () => void;
}

const AssetForm: React.FC<AssetFormProps> = ({ containerId, asset, onSave, onCancel }) => {
  const [assetTypes, setAssetTypes] = useState<IAssetType[]>([]);
  const [selectedAssetType, setSelectedAssetType] = useState<string>('');
  const [selectedSubType, setSelectedSubType] = useState<string>('');
  const [formData, setFormData] = useState<Partial<IAsset>>({
    name: '',
    fields: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadAssetTypes();
    if (asset) {
      setFormData(asset);
      setSelectedAssetType(asset.id);
      setSelectedSubType(asset.id);
    }
  }, [asset, containerId]);

  const loadAssetTypes = async () => {
    try {
      setIsLoading(true);
      const assetTypeService = AssetTypeService.getInstance();
      const types = await assetTypeService.getAssetTypes(containerId);
      setAssetTypes(types);
    } catch (error) {
      console.error('Failed to load asset types:', error);
      setErrors({ load: 'Failed to load asset types' });
      toast.error('Failed to load asset types');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFieldChange = (field: IFieldConfig, value: any) => {
    setFormData((prev: Partial<IAsset>) => ({
      ...prev,
      fields: prev.fields?.map(f => f.id === field.id ? { ...f, defaultValue: value } : f) || []
    }));
    setErrors((prev: Record<string, string>) => ({
      ...prev,
      [field.name]: ''
    }));
  };

  const handleFieldError = (field: IFieldConfig, error: string | null) => {
    setErrors((prev: Record<string, string>) => ({
      ...prev,
      [field.name]: error || ''
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setErrors({});

    if (!selectedAssetType) {
      setErrors({ assetTypeId: 'Please select an asset type' });
      return;
    }

    const currentType = assetTypes.find(t => t.id === selectedAssetType);
    if (!currentType) {
      setErrors({ assetTypeId: 'Invalid asset type selected' });
      return;
    }

    const currentSubType = currentType.subtypes.find(s => s.id === selectedSubType);
    const fields = currentSubType?.fields || currentType.fields;

    // Validate all fields
    let hasErrors = false;
    fields.forEach(field => {
      const value = formData.fields?.find(f => f.id === field.id)?.defaultValue;
      const error = validateField(field, value);
      if (error) {
        handleFieldError(field, error);
        hasErrors = true;
      }
    });

    if (hasErrors) {
      return;
    }

    try {
      setIsLoading(true);
      const assetService = AssetService.getInstance();
      const data = {
        name: formData.name || '',
        fields: formData.fields || [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      } as Omit<IAsset, 'id'>;

      const currentType = assetTypes.find(t => t.id === selectedAssetType);
      if (!currentType) {
        throw new Error('Invalid asset type selected');
      }

      const assetTypeConfig: IAssetTypeConfig = {
        id: currentType.id,
        name: currentType.name,
        label: currentType.label || currentType.name,
        fields: currentType.fields,
        subtypes: currentType.subtypes.map(subType => ({
          id: subType.id,
          name: subType.name,
          label: subType.label || subType.name,
          parentTypeId: subType.parentTypeId,
          fields: subType.fields,
          hiddenFields: subType.hiddenFields,
          overriddenFields: subType.overriddenFields,
          createdAt: subType.createdAt,
          updatedAt: subType.updatedAt
        })),
        createdAt: currentType.createdAt,
        updatedAt: currentType.updatedAt
      };

      if (asset?.id) {
        const updatedAsset = await assetService.updateAsset(containerId, asset.id, data, assetTypeConfig);
        onSave(updatedAsset);
        toast.success('Asset updated successfully');
      } else {
        const newAsset = await assetService.createAsset(containerId, data, assetTypeConfig);
        onSave(newAsset);
        toast.success('Asset created successfully');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const renderFieldInput = (field: IFieldConfig) => {
    const value = formData.fields?.find(f => f.id === field.id)?.defaultValue;
    const error = errors[field.name];
    const inputClassName = `w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
      error ? 'border-red-300' : 'border-gray-300'
    }`;

    switch (field.type) {
      case FieldType.Text:
        return (
          <div>
            <input
              type="text"
              value={value || ''}
              onChange={(e) => handleFieldChange(field, e.target.value)}
              className={inputClassName}
              disabled={isLoading}
            />
            {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
          </div>
        );

      case FieldType.Number:
        return (
          <div>
            <input
              type="number"
              value={value || ''}
              onChange={(e) => handleFieldChange(field, Number(e.target.value))}
              className={inputClassName}
              disabled={isLoading}
              min={field.min}
              max={field.max}
              step={field.step || 'any'}
            />
            {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
          </div>
        );

      case FieldType.Date:
        return (
          <div>
            <input
              type="date"
              value={value ? new Date(value).toISOString().split('T')[0] : ''}
              onChange={(e) => handleFieldChange(field, new Date(e.target.value))}
              className={inputClassName}
              disabled={isLoading}
              min={field.minDate ? new Date(field.minDate).toISOString().split('T')[0] : undefined}
              max={field.maxDate ? new Date(field.maxDate).toISOString().split('T')[0] : undefined}
            />
            {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
          </div>
        );

      case FieldType.Boolean:
        return (
          <div>
            <label className="inline-flex items-center">
              <input
                type="checkbox"
                checked={Boolean(value)}
                onChange={(e) => handleFieldChange(field, e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                disabled={isLoading}
              />
              <span className="ml-2 text-sm text-gray-700">Enabled</span>
            </label>
            {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
          </div>
        );

      case FieldType.Select:
        return (
          <div>
            <select
              value={value || ''}
              onChange={(e) => handleFieldChange(field, e.target.value)}
              className={inputClassName}
              disabled={isLoading}
            >
              <option value="">Select an option</option>
              {field.options?.map((option: string) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
          </div>
        );

      case FieldType.MultiSelect:
        return (
          <div>
            <select
              multiple
              value={value || []}
              onChange={(e) => {
                const values = Array.from(e.target.selectedOptions, option => option.value);
                handleFieldChange(field, values);
              }}
              className={`${inputClassName} h-auto min-h-[100px]`}
              disabled={isLoading}
            >
              {field.options?.map((option: string) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
          </div>
        );

      default:
        return null;
    }
  };

  const currentType = assetTypes.find(t => t.id === selectedAssetType);
  const currentSubType = currentType?.subtypes.find(s => s.id === selectedSubType);
  const fields = currentSubType?.fields || currentType?.fields || [];

  if (isLoading && !asset) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            {asset ? 'Edit Asset' : 'Create New Asset'}
          </h2>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <div className="space-y-6">
            <div>
              <label htmlFor="assetType" className="block text-sm font-medium text-gray-700 mb-1">
                Asset Type
              </label>
              <select
                id="assetType"
                value={selectedAssetType}
                onChange={(e) => {
                  setSelectedAssetType(e.target.value);
                  setSelectedSubType('');
                  setFormData(prev => ({ ...prev, fields: [] }));
                }}
                className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                  errors.assetTypeId ? 'border-red-300' : 'border-gray-300'
                }`}
                disabled={isLoading}
              >
                <option value="">Select an asset type</option>
                {assetTypes.map(type => (
                  <option key={type.id} value={type.id}>
                    {type.label}
                  </option>
                ))}
              </select>
              {errors.assetTypeId && <p className="mt-1 text-sm text-red-600">{errors.assetTypeId}</p>}
            </div>

            {currentType && currentType.subtypes.length > 0 && (
              <div>
                <label htmlFor="subType" className="block text-sm font-medium text-gray-700 mb-1">
                  Asset Subtype
                </label>
                <select
                  id="subType"
                  value={selectedSubType}
                  onChange={(e) => {
                    setSelectedSubType(e.target.value);
                    setFormData(prev => ({ ...prev, fields: [] }));
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  disabled={isLoading}
                >
                  <option value="">Select a subtype</option>
                  {currentType.subtypes.map(subType => (
                    <option key={subType.id} value={subType.id}>
                      {subType.label}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {currentType && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900">Fields</h3>
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  {fields.map(field => (
                    <div key={field.id}>
                      <label htmlFor={field.name} className="block text-sm font-medium text-gray-700 mb-1">
                        {field.label}
                      </label>
                      {renderFieldInput(field)}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={onCancel}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : 'Save Asset'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default AssetForm; 