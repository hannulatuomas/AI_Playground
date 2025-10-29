import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { AssetSubType, IAssetSubType } from '../../types/AssetSubType';
import { IFieldConfig, FieldType } from '../../types/FieldConfig';
import { FieldForm } from './FieldForm';
import { useUser } from '../../contexts/UserContext';
import { Tooltip } from '../common/Tooltip';

interface SubTypeFormProps {
  containerId: string;
  assetTypeId: string;
  subType: IAssetSubType;
  onSave: (subType: IAssetSubType) => void;
  onCancel: () => void;
}

export const SubTypeForm: React.FC<SubTypeFormProps> = ({ containerId, assetTypeId, subType, onSave, onCancel }) => {
  const { user } = useUser();
  const [name, setName] = useState(subType.name);
  const [label, setLabel] = useState(subType.label || '');
  const [fields, setFields] = useState<IFieldConfig[]>(subType.fields);
  const [hiddenFields, setHiddenFields] = useState<string[]>(subType.hiddenFields);
  const [overriddenFields, setOverriddenFields] = useState<string[]>(subType.overriddenFields);
  const [isEditingField, setIsEditingField] = useState(false);
  const [editingField, setEditingField] = useState<IFieldConfig | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (subType) {
      setName(subType.name);
      setLabel(subType.label || '');
      setFields(subType.fields);
      setHiddenFields(subType.hiddenFields);
      setOverriddenFields(subType.overriddenFields);
    }
  }, [subType]);

  const formatLabel = (name: string): string => {
    if (!name) return '';
    return name.charAt(0).toUpperCase() + name.slice(1).replace(/([A-Z])/g, ' $1');
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newName = e.target.value;
    setName(newName);
    setLabel(formatLabel(newName));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) {
      return;
    }

    setIsLoading(true);
    try {
      const updatedSubType: IAssetSubType = {
        ...subType,
        name: name.trim(),
        label: (label || '').trim() || formatLabel(name),
        fields: fields.map(field => ({
          ...field,
          parentTypeId: assetTypeId,
          updatedAt: new Date().toISOString()
        })),
        hiddenFields: hiddenFields,
        overriddenFields: overriddenFields,
        parentTypeId: assetTypeId,
        createdAt: subType?.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      await onSave(updatedSubType);
      toast.success(`Subtype "${updatedSubType.label || updatedSubType.name}" ${subType ? 'updated' : 'added'} successfully`);
    } catch (error) {
      console.error('Error saving subtype:', error);
      toast.error('Failed to save subtype');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!isLoading) {
      onCancel();
    }
  };

  const handleAddField = () => {
    setEditingField(null);
    setIsEditingField(true);
  };

  const handleEditField = (field: IFieldConfig) => {
    setEditingField(field);
    setIsEditingField(true);
  };

  const handleDeleteField = (fieldId: string) => {
    setFields(prevFields => prevFields.filter(f => f.id !== fieldId));
  };

  const handleFieldSubmit = (field: IFieldConfig) => {
    if (editingField) {
      setFields(prev => prev.map(f => f.id === field.id ? field : f));
    } else {
      setFields(prev => [...prev, { ...field, id: Date.now().toString() }]);
    }
    setIsEditingField(false);
    setEditingField(null);
  };

  const handleFieldCancel = () => {
    setIsEditingField(false);
    setEditingField(null);
  };

  const canSave = () => {
    return name.trim() !== '' && fields.length > 0;
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label htmlFor="subtypeName" className="block text-sm font-medium text-gray-700">Name</label>
          <input
            type="text"
            id="subtypeName"
            name="name"
            value={name}
            onChange={handleNameChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="subtypeLabel" className="block text-sm font-medium text-gray-700">Label</label>
          <input
            type="text"
            id="subtypeLabel"
            name="label"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">Fields</h3>
          <Tooltip content={isEditingField ? "Cannot add fields while editing" : ""} disabled={!isEditingField}>
            <button
              type="button"
              onClick={handleAddField}
              disabled={isEditingField}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              Add Field
            </button>
          </Tooltip>
        </div>

        {isEditingField ? (
          <div className="space-y-4">
            <FieldForm
              field={editingField || undefined}
              onSubmit={handleFieldSubmit}
              onCancel={handleFieldCancel}
            />
            {fields.length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Existing Fields</h4>
                <ul className="space-y-1">
                  {fields
                    .filter(field => field.id !== editingField?.id)
                    .map(field => (
                      <li key={field.id} className="flex justify-between items-center p-2 bg-white rounded-md border border-gray-200">
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
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            {fields.length > 0 ? (
              <ul className="space-y-1">
                {fields.map(field => (
                  <li key={field.id} className="flex justify-between items-center p-2 bg-white rounded-md border border-gray-200">
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
        )}
      </div>

      <div className="flex justify-end space-x-2">
        <Tooltip content={isLoading ? "Cannot cancel while saving" : ""} disabled={!isLoading}>
          <button
            type="button"
            onClick={handleCancel}
            disabled={isLoading}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50"
          >
            Cancel
          </button>
        </Tooltip>
        <Tooltip content={!canSave() ? "Name and at least one field are required" : ""} disabled={canSave()}>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canSave() || isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {isLoading ? 'Saving...' : (subType ? 'Update Subtype' : 'Add Subtype')}
          </button>
        </Tooltip>
      </div>
    </div>
  );
}; 