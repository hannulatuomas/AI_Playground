import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { AssetType, IAssetType } from '../../types/AssetType';
import { AssetSubType, IAssetSubType } from '../../types/AssetSubType';
import { IFieldConfig, FieldType } from '../../types/FieldConfig';
import { FieldForm } from './FieldForm';
import { SubTypeForm } from './SubTypeForm';
import { useUser } from '../../contexts/UserContext';
import { IdUtils } from '../../utils/IdUtils';
import { Tooltip } from '../common/Tooltip';

interface AssetTypeFormProps {
  containerId: string;
  assetType?: IAssetType;
  onSave: (assetType: IAssetType) => void;
  onCancel: () => void;
}

export const AssetTypeForm: React.FC<AssetTypeFormProps> = ({ containerId, assetType, onSave, onCancel }) => {
  const navigate = useNavigate();
  const { user } = useUser();
  const [name, setName] = useState(assetType?.name || '');
  const [label, setLabel] = useState(assetType?.label || '');
  const [fields, setFields] = useState<IFieldConfig[]>(assetType?.fields || []);
  const [subtypes, setSubtypes] = useState<IAssetSubType[]>(assetType?.subtypes || []);
  const [isLoading, setIsLoading] = useState(false);
  const [showFieldForm, setShowFieldForm] = useState(false);
  const [showSubtypeForm, setShowSubtypeForm] = useState(false);
  const [editingField, setEditingField] = useState<IFieldConfig | null>(null);
  const [editingSubtype, setEditingSubtype] = useState<IAssetSubType | null>(null);
  const [currentAssetTypeId] = useState(() => {
    if (assetType?.id) {
      return assetType.id;
    } else {
      return IdUtils.generateAssetTypeId(containerId);
    }
  });

  useEffect(() => {
    if (assetType) {
      setName(assetType.name);
      setLabel(assetType.label || '');
      setFields(assetType.fields || []);
      setSubtypes(assetType.subtypes || []);
    }
  }, [assetType]);

  const formatLabel = (name: string): string => {
    if (!name) return '';
    return name.charAt(0).toUpperCase() + name.slice(1);
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newName = e.target.value;
    setName(newName);
    setLabel(formatLabel(newName));
  };

  const handleCancel = () => {
    if (assetType) {
      navigate(`/containers/${containerId}`);
    } else {
      onCancel();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      toast.error('Name is required');
      return;
    }

    if (isLoading) {
      return;
    }

    setIsLoading(true);
    try {
      const updatedAssetType: IAssetType = {
        id: currentAssetTypeId,
        name: name.trim(),
        label: label.trim() || name.charAt(0).toUpperCase() + name.slice(1),
        fields: fields,
        subtypes: subtypes,
        createdAt: assetType?.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      await onSave(updatedAssetType);
      toast.success(assetType ? 'Asset type updated successfully' : 'Asset type created successfully');
    } catch (error) {
      console.error('Error saving asset type:', error);
      toast.error('Failed to save asset type');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddField = () => {
    setEditingField(null);
    setShowFieldForm(true);
  };

  const handleEditField = (field: IFieldConfig) => {
    setEditingField(field);
    setShowFieldForm(true);
  };

  const handleDeleteField = (fieldId: string) => {
    setFields(prev => prev.filter(f => f.id !== fieldId));
  };

  const handleFieldSubmit = (field: IFieldConfig) => {
    if (editingField) {
      setFields(prev => prev.map(f => f.id === field.id ? field : f));
    } else {
      setFields(prev => [...prev, field]);
    }
    setShowFieldForm(false);
    setEditingField(null);
  };

  const handleFieldCancel = () => {
    setShowFieldForm(false);
    setEditingField(null);
  };

  const handleAddSubType = () => {
    const newSubType = new AssetSubType({
      id: Date.now().toString(),
      name: '',
      label: '',
      fields: [],
      hiddenFields: [],
      overriddenFields: [],
      parentTypeId: assetType?.id || '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    });
    setEditingSubtype(newSubType);
  };

  const handleSubTypeSubmit = (subType: IAssetSubType) => {
    setSubtypes(prev => {
      const existingIndex = prev.findIndex(s => s.id === subType.id);
      if (existingIndex >= 0) {
        const updated = [...prev];
        updated[existingIndex] = {
          ...subType,
          parentTypeId: assetType?.id || '',
          updatedAt: new Date().toISOString()
        };
        return updated;
      }
      return [...prev, {
        ...subType,
        parentTypeId: assetType?.id || '',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }];
    });
    setEditingSubtype(null);
  };

  const handleSubTypeCancel = () => {
    setEditingSubtype(null);
  };

  const handleDeleteSubtype = (subtypeId: string) => {
    setSubtypes(prev => prev.filter(s => s.id !== subtypeId));
  };

  const canSave = () => {
    return name.trim() !== '' && fields.length > 0;
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) {
      return;
    }

    setIsLoading(true);
    try {
      const updatedAssetType: IAssetType = {
        id: currentAssetTypeId,
        name: name.trim(),
        label: label.trim() || name.charAt(0).toUpperCase() + name.slice(1),
        fields: fields,
        subtypes: subtypes.map(subtype => ({
          ...subtype,
          parentTypeId: currentAssetTypeId,
          updatedAt: new Date().toISOString()
        })),
        createdAt: assetType?.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      await onSave(updatedAssetType);
      toast.success(assetType ? 'Asset type updated successfully' : 'Asset type created successfully');
      
      if (assetType) {
        navigate(`/containers/${containerId}`);
      }
    } catch (error) {
      console.error('Error saving asset type:', error);
      toast.error('Failed to save asset type');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl h-[90vh] flex flex-col">
        <div className="bg-white rounded-lg shadow-md flex-1 flex flex-col overflow-hidden">
          <form onSubmit={handleFormSubmit} className="flex-1 flex flex-col overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-bold mb-4">Asset Type Details</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">Name</label>
                  <input
                    type="text"
                    id="name"
                    value={name}
                    onChange={handleNameChange}
                    required
                    disabled={isLoading}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="label" className="block text-sm font-medium text-gray-700">Label</label>
                  <input
                    type="text"
                    id="label"
                    value={label}
                    onChange={(e) => setLabel(e.target.value)}
                    disabled={isLoading}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>

            <div className="border-t border-gray-200 px-6 py-4">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium text-gray-900">Fields</h3>
                  <Tooltip content={isLoading ? "Saving..." : ""} disabled={!isLoading}>
                    <button
                      type="button"
                      onClick={handleAddField}
                      disabled={isLoading}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                    >
                      Add Field
                    </button>
                  </Tooltip>
                </div>

                {showFieldForm && (
                  <div className="bg-white p-4 rounded-md border border-gray-200">
                    <FieldForm
                      field={editingField || undefined}
                      onSubmit={handleFieldSubmit}
                      onCancel={handleFieldCancel}
                      disabled={isLoading}
                    />
                  </div>
                )}

                {fields.length > 0 ? (
                  <ul className="space-y-1">
                    {fields.map((field, index) => (
                      <li key={`field-${field.id || index}`} className="flex justify-between items-center p-2 bg-white rounded-md border border-gray-200">
                        <div className="space-y-0.5">
                          <strong className="block text-sm text-gray-900">{field.label || field.name}</strong>
                          <span className="text-xs text-gray-500">({field.type})</span>
                        </div>
                        <div className="flex space-x-1">
                          <button
                            type="button"
                            onClick={() => handleEditField(field)}
                            className="px-2 py-1 text-xs bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            onClick={() => handleDeleteField(field.id)}
                            className="px-2 py-1 text-xs bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                          >
                            Delete
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-center text-sm text-gray-500 italic py-2 bg-white rounded-md border border-gray-200">
                    No fields added yet
                  </p>
                )}
              </div>
            </div>

            <div className="border-t border-gray-200 px-6 py-4">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium text-gray-900">Subtypes</h3>
                  <Tooltip content={isLoading ? "Saving..." : ""} disabled={!isLoading}>
                    <button
                      type="button"
                      onClick={handleAddSubType}
                      disabled={isLoading}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                    >
                      Add Subtype
                    </button>
                  </Tooltip>
                </div>

                {editingSubtype ? (
                  <div className="space-y-4">
                    <div className="bg-white p-4 rounded-md border border-gray-200">
                      <SubTypeForm
                        containerId={containerId}
                        assetTypeId={assetType?.id || ''}
                        subType={editingSubtype}
                        onSave={handleSubTypeSubmit}
                        onCancel={handleSubTypeCancel}
                      />
                    </div>
                    {subtypes.length > 0 && (
                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Existing Subtypes</h4>
                        <ul className="space-y-1">
                          {subtypes
                            .filter(subtype => subtype.id !== editingSubtype.id)
                            .map(subtype => (
                              <li key={subtype.id} className="flex justify-between items-center p-2 bg-white rounded-md border border-gray-200">
                                <div className="space-y-0.5">
                                  <strong className="block text-sm text-gray-900">{subtype.label || subtype.name}</strong>
                                  <span className="text-xs text-gray-500">{subtype.fields.length} fields</span>
                                </div>
                                <div className="flex space-x-1">
                                  <button
                                    type="button"
                                    onClick={() => setEditingSubtype(subtype)}
                                    className="px-2 py-1 text-xs bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                                    disabled={isLoading}
                                  >
                                    Edit
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => handleDeleteSubtype(subtype.id)}
                                    className="px-2 py-1 text-xs bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                                    disabled={isLoading}
                                  >
                                    Delete
                                  </button>
                                </div>
                              </li>
                            ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-2">
                    {subtypes.length > 0 ? (
                      <ul className="space-y-1">
                        {subtypes.map(subtype => (
                          <li key={subtype.id} className="flex justify-between items-center p-2 bg-white rounded-md border border-gray-200">
                            <div className="space-y-0.5">
                              <strong className="block text-sm text-gray-900">{subtype.label || subtype.name}</strong>
                              <span className="text-xs text-gray-500">{subtype.fields.length} fields</span>
                            </div>
                            <div className="flex space-x-1">
                              <button
                                type="button"
                                onClick={() => setEditingSubtype(subtype)}
                                className="px-2 py-1 text-xs bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                                disabled={isLoading}
                              >
                                Edit
                              </button>
                              <button
                                type="button"
                                onClick={() => handleDeleteSubtype(subtype.id)}
                                className="px-2 py-1 text-xs bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                                disabled={isLoading}
                              >
                                Delete
                              </button>
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-center text-sm text-gray-500 italic py-2 bg-white rounded-md border border-gray-200">
                        No subtypes added yet
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="border-t border-gray-200 px-6 py-4 mt-auto">
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={handleCancel}
                  disabled={isLoading}
                  className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  Cancel
                </button>
                <Tooltip content={!canSave() ? "Name and at least one field are required" : ""} disabled={canSave()}>
                  <button
                    type="submit"
                    disabled={!canSave() || isLoading}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
                  >
                    {isLoading ? 'Saving...' : (assetType ? 'Update Asset Type' : 'Create Asset Type')}
                  </button>
                </Tooltip>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}; 