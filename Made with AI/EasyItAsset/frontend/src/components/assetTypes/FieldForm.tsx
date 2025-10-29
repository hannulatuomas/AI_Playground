import React, { useState, useEffect } from 'react';
import { IFieldConfig, FieldType } from '../../types/FieldConfig';
import { toast } from 'react-toastify';
import { formatLabel } from '../../utils/formatLabel';
import { Tooltip } from '../common/Tooltip';

interface FieldFormProps {
  field?: IFieldConfig;
  onSubmit: (field: IFieldConfig) => void;
  onCancel: () => void;
  disabled?: boolean;
}

export const FieldForm: React.FC<FieldFormProps> = ({
  field,
  onSubmit,
  onCancel,
  disabled = false
}) => {
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  const [formData, setFormData] = useState<IFieldConfig>(field || {
    id: '',
    name: '',
    type: FieldType.Text,
    label: '',
    required: false,
    parentTypeId: '',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  });
  const [isEditing, setIsEditing] = useState(true);

  useEffect(() => {
    // Reset form when field changes
    if (field) {
      setFormData({
        ...formData,
        name: field.name,
        label: field.label || '',
        type: field.type,
        options: field.options || [],
        defaultValue: field.defaultValue || '',
        parentTypeId: field.parentTypeId,
        required: field.required || false,
        pattern: field.pattern,
        min: field.min,
        max: field.max,
        step: field.step,
        minDate: field.minDate,
        maxDate: field.maxDate,
        length: field.length,
        description: field.description,
        updatedAt: new Date().toISOString()
      });
    }
  }, [field]);

  useEffect(() => {
    if (formData.name) {
      setFormData(prev => ({ ...prev, label: formatLabel(formData.name) }));
    } else {
      setFormData(prev => ({ ...prev, label: '' }));
    }
  }, [formData.name]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (disabled) {
      return;
    }

    const errors = validateForm();
    if (errors.length > 0) {
      errors.forEach(error => toast.error(error));
      return;
    }

    const updatedField: IFieldConfig = {
      ...formData,
      name: formData.name.trim(),
      label: (formData.label || '').trim() || formData.name.charAt(0).toUpperCase() + formData.name.slice(1).replace(/([A-Z])/g, ' $1'),
      type: formData.type,
      defaultValue: formData.defaultValue ? processDefaultValue(formData.defaultValue, formData.type) : undefined,
      options: formData.type === FieldType.Select || formData.type === FieldType.MultiSelect ? formData.options : undefined,
      updatedAt: new Date().toISOString()
    };

    onSubmit(updatedField);
    toast.success(`Field "${updatedField.label || updatedField.name}" ${field ? 'updated' : 'added'} successfully`);
  };

  const handleCancel = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!disabled) {
      onCancel();
    }
  };

  const processDefaultValue = (value: string, fieldType: FieldType): any => {
    switch (fieldType) {
      case FieldType.Number:
        return value ? Number(value) : undefined;
      case FieldType.Boolean:
        return value === 'true';
      case FieldType.Date:
        return value ? new Date(value) : undefined;
      case FieldType.MultiSelect:
        return value ? value.split(',').map(v => v.trim()) : [];
      case FieldType.Select:
        return value || undefined;
      default:
        return value || undefined;
    }
  };

  const validateForm = (): string[] => {
    const errors: string[] = [];
    
    if (!formData.name?.trim()) {
      errors.push('Name is required');
    } else if (!/^[a-zA-Z0-9_]+$/.test(formData.name)) {
      errors.push('Name can only contain letters, numbers, and underscores');
    }
    
    if (!formData.label?.trim()) {
      errors.push('Label is required');
    }
    
    if (formData.type === FieldType.Number) {
      if (formData.min !== undefined && formData.max !== undefined && formData.min > formData.max) {
        errors.push('Minimum value cannot be greater than maximum value');
      }
      if (formData.defaultValue && isNaN(Number(formData.defaultValue))) {
        errors.push('Default value must be a number');
      }
      if (formData.defaultValue && formData.min !== undefined && Number(formData.defaultValue) < formData.min) {
        errors.push(`Default value must be greater than or equal to ${formData.min}`);
      }
      if (formData.defaultValue && formData.max !== undefined && Number(formData.defaultValue) > formData.max) {
        errors.push(`Default value must be less than or equal to ${formData.max}`);
      }
    }
    
    if (formData.type === FieldType.Text) {
      if (formData.pattern) {
        try {
          new RegExp(formData.pattern);
        } catch (e) {
          errors.push('Invalid regular expression pattern');
        }
      }
      if (formData.length !== undefined && formData.defaultValue && formData.defaultValue.length > formData.length) {
        errors.push(`Default value must be at most ${formData.length} characters long`);
      }
    }
    
    if (formData.type === FieldType.Date) {
      if (formData.defaultValue && isNaN(Date.parse(formData.defaultValue))) {
        errors.push('Invalid date format');
      }
      if (formData.defaultValue && formData.minDate && new Date(formData.defaultValue) < new Date(formData.minDate)) {
        errors.push(`Default value must be after ${formData.minDate}`);
      }
      if (formData.defaultValue && formData.maxDate && new Date(formData.defaultValue) > new Date(formData.maxDate)) {
        errors.push(`Default value must be before ${formData.maxDate}`);
      }
    }
    
    if (formData.type === FieldType.Boolean) {
      if (formData.defaultValue && formData.defaultValue !== 'true' && formData.defaultValue !== 'false') {
        errors.push('Default value must be true or false');
      }
    }

    if (formData.type === FieldType.Select || formData.type === FieldType.MultiSelect) {
      const options = formData.options || [];
      if (options.length === 0) {
        errors.push('At least one option is required for select fields');
      } else if (new Set(options).size !== options.length) {
        errors.push('Duplicate options are not allowed');
      }
      if (formData.defaultValue) {
        const defaultValues = Array.isArray(formData.defaultValue) ? formData.defaultValue : [formData.defaultValue];
        const invalidValues = defaultValues.filter(value => !options.includes(value));
        if (invalidValues.length > 0) {
          errors.push(`Default value(s) ${invalidValues.join(', ')} not found in options`);
        }
      }
    }
    
    return errors;
  };

  const renderAdvancedOptions = () => {
    const type = formData.type;

    switch (type) {
      case FieldType.Text:
        return (
          <div className="mt-4 space-y-4">
            <div className="space-y-2">
              <label htmlFor="fieldDefaultValue" className="block text-sm font-medium text-gray-700">Default Value</label>
              <input
                type="text"
                id="fieldDefaultValue"
                name="defaultValue"
                value={formData.defaultValue}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="fieldLength" className="block text-sm font-medium text-gray-700">Max Length</label>
                <input
                  type="number"
                  id="fieldLength"
                  name="length"
                  value={formData.length}
                  onChange={handleChange}
                  min="1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="fieldPattern" className="block text-sm font-medium text-gray-700">Pattern (Regex)</label>
                <input
                  type="text"
                  id="fieldPattern"
                  name="pattern"
                  value={formData.pattern}
                  onChange={handleChange}
                  placeholder="e.g. ^[A-Za-z]+$"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        );

      case FieldType.Number:
        return (
          <div className="mt-4 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="fieldDefaultValue" className="block text-sm font-medium text-gray-700">Default Value</label>
                <input
                  type="number"
                  id="fieldDefaultValue"
                  name="defaultValue"
                  value={formData.defaultValue}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="fieldStep" className="block text-sm font-medium text-gray-700">Step</label>
                <input
                  type="number"
                  id="fieldStep"
                  name="step"
                  value={formData.step}
                  onChange={handleChange}
                  min="0.01"
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="fieldMin" className="block text-sm font-medium text-gray-700">Min Value</label>
                <input
                  type="number"
                  id="fieldMin"
                  name="min"
                  value={formData.min}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="fieldMax" className="block text-sm font-medium text-gray-700">Max Value</label>
                <input
                  type="number"
                  id="fieldMax"
                  name="max"
                  value={formData.max}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        );

      case FieldType.Date:
        return (
          <div className="mt-4 space-y-4">
            <div className="space-y-2">
              <label htmlFor="fieldDefaultValue" className="block text-sm font-medium text-gray-700">Default Value</label>
              <input
                type="date"
                id="fieldDefaultValue"
                name="defaultValue"
                value={formData.defaultValue}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="fieldMinDate" className="block text-sm font-medium text-gray-700">Min Date</label>
                <input
                  type="date"
                  id="fieldMinDate"
                  name="minDate"
                  value={formData.minDate}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="fieldMaxDate" className="block text-sm font-medium text-gray-700">Max Date</label>
                <input
                  type="date"
                  id="fieldMaxDate"
                  name="maxDate"
                  value={formData.maxDate}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        );

      case FieldType.Select:
      case FieldType.MultiSelect:
        return (
          <div className="mt-4 space-y-4">
            <div className="space-y-2">
              <label htmlFor="fieldOptions" className="block text-sm font-medium text-gray-700">Options (one per line)</label>
              <textarea
                id="fieldOptions"
                name="options"
                value={formData.options?.join('\n')}
                onChange={(e) => {
                  const options = e.target.value.split('\n').filter(option => option.trim() !== '');
                  setFormData(prev => ({ ...prev, options }));
                }}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Option 1&#10;Option 2&#10;Option 3"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="fieldDefaultValue" className="block text-sm font-medium text-gray-700">Default Value</label>
              <input
                type="text"
                id="fieldDefaultValue"
                name="defaultValue"
                value={formData.defaultValue}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        );

      default:
        return (
          <div className="mt-4 space-y-4">
            <div className="space-y-2">
              <label htmlFor="fieldDefaultValue" className="block text-sm font-medium text-gray-700">Default Value</label>
              <input
                type="text"
                id="fieldDefaultValue"
                name="defaultValue"
                value={formData.defaultValue}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        );
    }
  };

  const canSave = () => {
    return formData.name.trim() !== '';
  };

  if (!isEditing) {
    return (
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">{formData.label}</h3>
          <p className="text-sm text-gray-500">{formData.name}</p>
        </div>
        <div className="flex space-x-2">
          <button
            type="button"
            onClick={() => setIsEditing(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            disabled={disabled}
          >
            Edit
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="inline-flex items-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            disabled={disabled}
          >
            Remove
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label htmlFor="fieldName" className="block text-sm font-medium text-gray-700">Name</label>
          <input
            type="text"
            id="fieldName"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="fieldLabel" className="block text-sm font-medium text-gray-700">Label</label>
          <input
            type="text"
            id="fieldLabel"
            name="label"
            value={formData.label}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label htmlFor="fieldType" className="block text-sm font-medium text-gray-700">Type</label>
          <select
            id="fieldType"
            name="type"
            value={formData.type}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            {Object.values(FieldType).map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Required</label>
          <div className="flex items-center h-10">
            <input
              type="checkbox"
              id="fieldRequired"
              name="required"
              checked={formData.required}
              onChange={handleChange}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="fieldRequired" className="ml-2 block text-sm text-gray-900">
              This field is required
            </label>
          </div>
        </div>
      </div>

      <div className="border-t border-gray-200 pt-4">
        <button
          type="button"
          onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
          className="flex items-center text-sm text-blue-600 hover:text-blue-800"
        >
          <span>Advanced Options</span>
          <svg
            className={`ml-2 h-4 w-4 transform transition-transform ${showAdvancedOptions ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {showAdvancedOptions && renderAdvancedOptions()}
      </div>

      <div className="flex justify-end space-x-2">
        <Tooltip content={disabled ? "Cannot edit while saving" : ""} disabled={!disabled}>
          <button
            type="button"
            onClick={handleCancel}
            disabled={disabled}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50"
          >
            Cancel
          </button>
        </Tooltip>
        <Tooltip content={!canSave() ? "Name and label are required" : ""} disabled={canSave()}>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canSave() || disabled}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {field ? 'Update Field' : 'Add Field'}
          </button>
        </Tooltip>
      </div>
    </div>
  );
}; 