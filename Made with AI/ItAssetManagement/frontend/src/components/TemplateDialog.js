import React, { useState } from 'react';
import { Layers, X, Plus, Box } from 'lucide-react';

const TemplateDialog = ({ isOpen, onClose, onConfirm, template, type = "group" }) => {
  const [formData, setFormData] = useState({
    name: template?.name || '',
    description: template?.description || '',
    icon: template?.icon || '',
    customFields: template?.custom_fields || []
  });
  
  // Auto-fill data when template changes
  React.useEffect(() => {
    if (template) {
      console.log('Template data received:', template);
      console.log('Template custom_fields:', template.custom_fields);
      setFormData(prev => ({
        ...prev,
        name: template.name || '',
        description: template.description || '',
        icon: template.icon || '',
        customFields: template.custom_fields || []
      }));
    }
  }, [template]);
  
  const [newField, setNewField] = useState({
    name: '',
    label: '',
    type: 'text',
    required: false,
    default_value: ''
  });

  // Helper function to convert field name to display label
  const convertNameToLabel = (name) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  const handleFieldNameChange = (value) => {
    setNewField({
      ...newField,
      name: value,
      label: value ? convertNameToLabel(value) : ''
    });
  };

  const addCustomField = () => {
    if (newField.name && newField.label) {
      setFormData({
        ...formData,
        customFields: [...formData.customFields, { ...newField, id: Date.now() }]
      });
      setNewField({
        name: '',
        label: '',
        type: 'text',
        required: false,
        default_value: ''
      });
    }
  };

  const removeCustomField = (id) => {
    setFormData({
      ...formData,
      customFields: formData.customFields.filter(field => field.id !== id)
    });
  };

  const handleConfirm = () => {
    onConfirm(formData, type);
    onClose();
    // Reset form
    setFormData({
      name: template?.name || '',
      description: template?.description || '',
      icon: template?.icon || '',
      customFields: template?.custom_fields || []
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50" 
        onClick={onClose}
      />
      
      {/* Dialog */}
      <div className="relative bg-white rounded-xl shadow-xl p-6 max-w-2xl w-full mx-4 z-10 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
              <Layers className="w-5 h-5 text-emerald-600" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900">
              Create {type === 'group' ? 'Asset Group' : 'Asset Type'} from Template
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        
        <div className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h4 className="font-medium text-slate-900">Basic Information</h4>
            {/* Template Icon Display */}
            {template && formData.icon && (
              <div className="flex items-center space-x-3 p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
                <Box className="w-6 h-6 text-emerald-600" />
                <div>
                  <p className="font-medium text-emerald-900">Template Icon: {formData.icon}</p>
                  <p className="text-sm text-emerald-600">This icon will be used for your {type}</p>
                </div>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="form-label">Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="form-input"
                  placeholder={`e.g., ${template?.name || 'Hardware'}`}
                  data-testid="template-name-input"
                />
              </div>
              <div>
                <label className="form-label">Description</label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="form-input"
                  placeholder={template?.description || 'Brief description'}
                  data-testid="template-description-input"
                />
              </div>
            </div>
          </div>

          {/* Custom Fields */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-slate-900">Custom Fields</h4>
              <span className="text-sm text-slate-500">Define fields for this {type}</span>
            </div>
            
            {/* Template Fields (Pre-defined) */}
            {formData.customFields.length > 0 && (
              <div className="space-y-2">
                <h5 className="font-medium text-emerald-700 text-sm flex items-center">
                  <Layers className="w-4 h-4 mr-2" />
                  Template Fields (Included with this template)
                </h5>
                {formData.customFields.map((field) => (
                  <div key={field.id} className="flex items-center justify-between p-3 bg-emerald-50 border border-emerald-200 rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <span className="font-medium text-emerald-900">{field.label}</span>
                        <span className="px-2 py-1 bg-emerald-200 text-emerald-700 text-xs rounded font-semibold">{field.type}</span>
                        {field.required && (
                          <span className="px-2 py-1 bg-red-100 text-red-600 text-xs rounded">Required</span>
                        )}
                        {field.default_value && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-600 text-xs rounded">Default: {field.default_value}</span>
                        )}
                      </div>
                      <p className="text-sm text-emerald-600">Field name: {field.name}</p>
                      {field.dataset_values && (
                        <p className="text-xs text-emerald-500 mt-1">Options: {field.dataset_values.join(', ')}</p>
                      )}
                    </div>
                    <button
                      onClick={() => removeCustomField(field.id)}
                      className="p-1 text-emerald-400 hover:text-red-600 rounded"
                      title="Remove this template field"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
            
            {/* Show message if no template fields */}
            {formData.customFields.length === 0 && template && (
              <div className="text-center py-4 bg-slate-50 rounded-lg border-2 border-dashed border-slate-200">
                <p className="text-slate-600 text-sm">
                  This template doesn't include any pre-defined fields.
                </p>
                <p className="text-slate-500 text-xs mt-1">
                  You can add your own custom fields below.
                </p>
              </div>
            )}

            {/* Add New Field */}
            <div className="border border-slate-200 rounded-lg p-4 space-y-3">
              <h5 className="font-medium text-slate-800">Add Custom Field</h5>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                <input
                  type="text"
                  placeholder="Field name (e.g., serial_number)"
                  value={newField.name}
                  onChange={(e) => handleFieldNameChange(e.target.value)}
                  className="form-input text-sm"
                />
                <input
                  type="text"
                  placeholder="Display label (e.g., Serial Number)"
                  value={newField.label}
                  onChange={(e) => setNewField({...newField, label: e.target.value})}
                  className="form-input text-sm"
                />
                <select
                  value={newField.type}
                  onChange={(e) => setNewField({...newField, type: e.target.value})}
                  className="form-input text-sm"
                >
                  <option value="text">Text</option>
                  <option value="number">Number</option>
                  <option value="date">Date</option>
                  <option value="boolean">Yes/No</option>
                  <option value="dataset">Dropdown List</option>
                  <option value="file">File Upload</option>
                  <option value="rich_text">Rich Text</option>
                  <option value="multi_select">Multi-Select</option>
                  <option value="asset_reference">Asset Reference</option>
                </select>
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="required"
                    checked={newField.required}
                    onChange={(e) => setNewField({...newField, required: e.target.checked})}
                    className="rounded"
                  />
                  <label htmlFor="required" className="text-sm text-slate-600">Required</label>
                </div>
              </div>
              <button
                onClick={addCustomField}
                disabled={!newField.name || !newField.label}
                className="btn-secondary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Plus className="w-4 h-4 mr-1" />
                Add Field
              </button>
            </div>
          </div>
        </div>
        
        <div className="flex space-x-3 justify-end mt-6 pt-6 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
            data-testid="template-cancel"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={!formData.name}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            data-testid="template-confirm"
          >
            Create {type === 'group' ? 'Asset Group' : 'Asset Type'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default TemplateDialog;