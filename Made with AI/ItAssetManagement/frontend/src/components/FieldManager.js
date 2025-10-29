import React, { useState } from 'react';
import { Plus, Edit3, Trash2, X } from 'lucide-react';

const FieldManager = ({ fields = [], onChange, title = "Custom Fields" }) => {
  const [newField, setNewField] = useState({
    name: '',
    label: '',
    type: 'text',
    required: false,
    default_value: '',
    datasetValues: []
  });
  
  const [editingField, setEditingField] = useState(null);
  const [editFieldData, setEditFieldData] = useState({});
  const [datasetValue, setDatasetValue] = useState('');

  const fieldTypes = [
    { value: 'text', label: 'Text' },
    { value: 'number', label: 'Number' },
    { value: 'date', label: 'Date' },
    { value: 'boolean', label: 'Yes/No' },
    { value: 'dataset', label: 'Dropdown List' },
    { value: 'file', label: 'File Upload' },
    { value: 'rich_text', label: 'Rich Text' },
    { value: 'multi_select', label: 'Multi-Select' },
    { value: 'asset_reference', label: 'Asset Reference' },
    { value: 'ip_address', label: 'IP Address' },
    { value: 'mac_address', label: 'MAC Address' },
    { value: 'url', label: 'URL/Website' },
    { value: 'email', label: 'Email Address' },
    { value: 'phone', label: 'Phone Number' },
    { value: 'serial_number', label: 'Serial Number' },
    { value: 'version', label: 'Version Number' },
    { value: 'currency', label: 'Currency/Cost' },
    { value: 'file_size', label: 'File Size' },
    { value: 'duration', label: 'Duration/Time' },
    { value: 'password', label: 'Password/Secret' }
  ];

  // Helper function to convert field name to display label
  const convertNameToLabel = (name) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  const addField = () => {
    if (newField.name && newField.label) {
      const fieldToAdd = {
        ...newField,
        id: Date.now().toString(),
        dataset_values: newField.datasetValues
      };
      onChange([...fields, fieldToAdd]);
      setNewField({
        name: '',
        label: '',
        type: 'text',
        required: false,
        default_value: '',
        datasetValues: []
      });
    }
  };

  const handleFieldNameChange = (value) => {
    setNewField({
      ...newField,
      name: value,
      label: value ? convertNameToLabel(value) : ''
    });
  };

  const removeField = (fieldId) => {
    onChange(fields.filter(field => field.id !== fieldId));
  };

  const startEditField = (field) => {
    setEditingField(field.id);
    setEditFieldData({...field, datasetValues: field.dataset_values || [], default_value: field.default_value || field.defaultValue || ''});
  };

  const saveEditField = () => {
    const updatedFields = fields.map(field => 
      field.id === editingField ? {...editFieldData, dataset_values: editFieldData.datasetValues} : field
    );
    onChange(updatedFields);
    setEditingField(null);
    setEditFieldData({});
  };

  const cancelEditField = () => {
    setEditingField(null);
    setEditFieldData({});
  };

  const addDatasetValue = (isEdit = false) => {
    if (datasetValue.trim()) {
      if (isEdit) {
        setEditFieldData({
          ...editFieldData,
          datasetValues: [...(editFieldData.datasetValues || []), datasetValue.trim()]
        });
      } else {
        setNewField({
          ...newField,
          datasetValues: [...newField.datasetValues, datasetValue.trim()]
        });
      }
      setDatasetValue('');
    }
  };

  const removeDatasetValue = (index, isEdit = false) => {
    if (isEdit) {
      setEditFieldData({
        ...editFieldData,
        datasetValues: editFieldData.datasetValues.filter((_, i) => i !== index)
      });
    } else {
      setNewField({
        ...newField,
        datasetValues: newField.datasetValues.filter((_, i) => i !== index)
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-slate-900">{title}</h4>
        <span className="text-sm text-slate-500">{fields.length} fields defined</span>
      </div>
      
      {/* Existing Fields */}
      {fields.length > 0 && (
        <div className="space-y-3">
          {fields.map((field) => (
            <div key={field.id} className="border border-slate-200 rounded-lg p-4">
              {editingField === field.id ? (
                // Edit Form
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Field Name</label>
                      <input
                        type="text"
                        value={editFieldData.name || ''}
                        onChange={(e) => setEditFieldData({...editFieldData, name: e.target.value})}
                        className="form-input text-sm"
                        placeholder="e.g., serial_number"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Display Label</label>
                      <input
                        type="text"
                        value={editFieldData.label || ''}
                        onChange={(e) => setEditFieldData({...editFieldData, label: e.target.value})}
                        className="form-input text-sm"
                        placeholder="e.g., Serial Number"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Field Type</label>
                      <select
                        value={editFieldData.type || 'text'}
                        onChange={(e) => setEditFieldData({...editFieldData, type: e.target.value})}
                        className="form-input text-sm"
                      >
                        {fieldTypes.map(type => (
                          <option key={type.value} value={type.value}>{type.label}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Default Value</label>
                      <input
                        type="text"
                        value={editFieldData.default_value || ''}
                        onChange={(e) => setEditFieldData({...editFieldData, default_value: e.target.value})}
                        className="form-input text-sm"
                        placeholder="Optional default value"
                      />
                    </div>
                  </div>

                  {editFieldData.type === 'dataset' && (
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">Dropdown Options</label>
                      <div className="space-y-2">
                        {editFieldData.datasetValues && editFieldData.datasetValues.map((value, index) => (
                          <div key={index} className="flex items-center space-x-2">
                            <span className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded text-sm">
                              {value}
                            </span>
                            <button
                              onClick={() => removeDatasetValue(index, true)}
                              className="p-2 text-slate-400 hover:text-red-600"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                        <div className="flex items-center space-x-2">
                          <input
                            type="text"
                            value={datasetValue}
                            onChange={(e) => setDatasetValue(e.target.value)}
                            placeholder="Add option"
                            className="flex-1 form-input text-sm"
                            onKeyPress={(e) => e.key === 'Enter' && addDatasetValue(true)}
                          />
                          <button
                            onClick={() => addDatasetValue(true)}
                            className="btn-secondary text-sm"
                          >
                            Add
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center space-x-4">
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={editFieldData.required || false}
                        onChange={(e) => setEditFieldData({...editFieldData, required: e.target.checked})}
                        className="rounded"
                      />
                      <span className="text-sm text-slate-700">Required field</span>
                    </label>
                  </div>

                  <div className="flex space-x-3">
                    <button onClick={saveEditField} className="btn-primary text-sm">
                      Save Changes
                    </button>
                    <button onClick={cancelEditField} className="btn-secondary text-sm">
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                // Display Mode
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="font-medium text-slate-900">{field.label}</span>
                      <span className="px-2 py-1 bg-slate-100 text-slate-600 text-xs rounded">
                        {fieldTypes.find(t => t.value === field.type)?.label || field.type}
                      </span>
                      {field.required && (
                        <span className="px-2 py-1 bg-red-100 text-red-600 text-xs rounded">Required</span>
                      )}
                    </div>
                    <div className="text-sm text-slate-500 space-y-1">
                      <p>Field name: {field.name}</p>
                      {field.default_value && <p>Default: {field.default_value}</p>}
                      {field.dataset_values && field.dataset_values.length > 0 && (
                        <p>Options: {field.dataset_values.join(', ')}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => startEditField(field)}
                      className="p-2 text-slate-400 hover:text-slate-600 rounded hover:bg-slate-100"
                      title="Edit Field"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => removeField(field.id)}
                      className="p-2 text-slate-400 hover:text-red-600 rounded hover:bg-red-50"
                      title="Delete Field"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add New Field */}
      <div className="border border-slate-200 rounded-lg p-4 bg-slate-50">
        <h5 className="font-medium text-slate-800 mb-4">Add New Field</h5>
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Field Name</label>
              <input
                type="text"
                value={newField.name}
                onChange={(e) => handleFieldNameChange(e.target.value)}
                className="form-input text-sm"
                placeholder="e.g., serial_number"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Display Label</label>
              <input
                type="text"
                value={newField.label}
                onChange={(e) => setNewField({...newField, label: e.target.value})}
                className="form-input text-sm"
                placeholder="e.g., Serial Number"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Field Type</label>
              <select
                value={newField.type}
                onChange={(e) => setNewField({...newField, type: e.target.value})}
                className="form-input text-sm"
              >
                {fieldTypes.map(type => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Default Value</label>
              <input
                type="text"
                value={newField.default_value}
                onChange={(e) => setNewField({...newField, default_value: e.target.value})}
                className="form-input text-sm"
                placeholder="Optional default value"
              />
            </div>
          </div>

          {newField.type === 'dataset' && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Dropdown Options</label>
              <div className="space-y-2">
                {newField.datasetValues.map((value, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <span className="flex-1 px-3 py-2 bg-white border border-slate-200 rounded text-sm">
                      {value}
                    </span>
                    <button
                      onClick={() => removeDatasetValue(index)}
                      className="p-2 text-slate-400 hover:text-red-600"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={datasetValue}
                    onChange={(e) => setDatasetValue(e.target.value)}
                    placeholder="Add option"
                    className="flex-1 form-input text-sm"
                    onKeyPress={(e) => e.key === 'Enter' && addDatasetValue()}
                  />
                  <button
                    onClick={() => addDatasetValue()}
                    className="btn-secondary text-sm"
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={newField.required}
                onChange={(e) => setNewField({...newField, required: e.target.checked})}
                className="rounded"
              />
              <span className="text-sm text-slate-700">Required field</span>
            </label>
          </div>

          <div className="flex justify-start">
            <button
              onClick={addField}
              disabled={!newField.name || !newField.label}
              className="btn-primary text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Add Field</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FieldManager;