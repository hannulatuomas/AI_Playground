import React, { useState, useEffect } from 'react';
import { Plus, Edit3, Trash2, Save, X, Copy } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../App';
import IconPicker from './IconPicker';
import FieldManager from './FieldManager';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TemplateManager = ({ isOpen, onClose, onTemplateCreated }) => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('browse'); // 'browse', 'create', 'edit'
  const [customTemplates, setCustomTemplates] = useState([]);
  const [defaultTemplates, setDefaultTemplates] = useState({
    asset_groups: [],
    asset_types: [],
    assets: []
  });
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    icon: '',
    template_type: 'asset_group',
    custom_fields: [],
    organization_id: null,
    is_public: false
  });

  useEffect(() => {
    if (isOpen) {
      fetchTemplates();
    }
  }, [isOpen]);

  const fetchTemplates = async () => {
    try {
      // Fetch custom templates
      const customResponse = await axios.get(`${API}/templates/custom`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setCustomTemplates(customResponse.data || []);

      // Fetch default templates
      const [groupsRes, typesRes, assetsRes] = await Promise.all([
        axios.get(`${API}/templates/default-asset-groups`),
        axios.get(`${API}/templates/default-asset-types`),
        axios.get(`${API}/templates/default-assets`)
      ]);

      setDefaultTemplates({
        asset_groups: groupsRes.data || [],
        asset_types: typesRes.data || [],
        assets: assetsRes.data || []
      });
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const handleCreateTemplate = async () => {
    try {
      const response = await axios.post(`${API}/templates/custom`, formData, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });

      setCustomTemplates([...customTemplates, response.data]);
      resetForm();
      setActiveTab('browse');
      
      if (onTemplateCreated) {
        onTemplateCreated(response.data);
      }
    } catch (error) {
      console.error('Error creating template:', error);
      alert('Error creating template: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleUpdateTemplate = async () => {
    try {
      const response = await axios.put(`${API}/templates/custom/${editingTemplate.id}`, formData, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });

      setCustomTemplates(customTemplates.map(t => t.id === editingTemplate.id ? response.data : t));
      setEditingTemplate(null);
      resetForm();
      setActiveTab('browse');
    } catch (error) {
      console.error('Error updating template:', error);
      alert('Error updating template: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDeleteTemplate = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this template?')) return;

    try {
      await axios.delete(`${API}/templates/custom/${templateId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });

      setCustomTemplates(customTemplates.filter(t => t.id !== templateId));
    } catch (error) {
      console.error('Error deleting template:', error);
      alert('Error deleting template: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleCloneTemplate = (template, isDefault = false) => {
    const templateData = {
      name: `${template.name} (Copy)`,
      description: template.description,
      icon: template.icon || '',
      template_type: isDefault ? 'asset_group' : template.template_type,
      custom_fields: template.custom_fields || [],
      organization_id: null,
      is_public: false
    };

    setFormData(templateData);
    setActiveTab('create');
  };

  const handleEditTemplate = (template) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      description: template.description,
      icon: template.icon || '',
      template_type: template.template_type,
      custom_fields: template.custom_fields || [],
      organization_id: template.organization_id,
      is_public: template.is_public
    });
    setActiveTab('edit');
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      icon: '',
      template_type: 'asset_group',
      custom_fields: [],
      organization_id: null,
      is_public: false
    });
    setEditingTemplate(null);
  };

  const handleClose = () => {
    resetForm();
    setActiveTab('browse');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity bg-slate-500 bg-opacity-75" onClick={handleClose} />

        <div className="inline-block w-full max-w-6xl px-6 py-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-xl">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-slate-900">Template Manager</h2>
            <button onClick={handleClose} className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Tab Navigation */}
          <div className="flex space-x-1 mb-6 bg-slate-100 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('browse')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'browse' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Browse Templates
            </button>
            <button
              onClick={() => { setActiveTab('create'); resetForm(); }}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'create' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Create Template
            </button>
            {editingTemplate && (
              <button
                onClick={() => setActiveTab('edit')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'edit' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Edit Template
              </button>
            )}
          </div>

          {/* Browse Templates Tab */}
          {activeTab === 'browse' && (
            <div className="space-y-8">
              {/* Custom Templates */}
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Your Custom Templates</h3>
                {customTemplates.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {customTemplates.map((template) => (
                      <div key={template.id} className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-slate-900">{template.name}</h4>
                          <div className="flex space-x-1">
                            <button
                              onClick={() => handleEditTemplate(template)}
                              className="p-1.5 text-slate-400 hover:text-slate-600 rounded"
                              title="Edit"
                            >
                              <Edit3 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleCloneTemplate(template)}
                              className="p-1.5 text-slate-400 hover:text-slate-600 rounded"
                              title="Clone"
                            >
                              <Copy className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteTemplate(template.id)}
                              className="p-1.5 text-slate-400 hover:text-red-600 rounded"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <p className="text-sm text-slate-600 mb-2">{template.description}</p>
                        <div className="flex items-center justify-between text-xs">
                          <span className="px-2 py-1 bg-slate-200 text-slate-700 rounded">{template.template_type}</span>
                          <span className="text-slate-500">{template.custom_fields?.length || 0} fields</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    <p>No custom templates yet.</p>
                    <button
                      onClick={() => { setActiveTab('create'); resetForm(); }}
                      className="mt-2 text-emerald-600 hover:text-emerald-700 font-medium"
                    >
                      Create your first template
                    </button>
                  </div>
                )}
              </div>

              {/* Default Templates */}
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Default Templates (Clone to Customize)</h3>
                
                {/* Asset Group Templates */}
                <div className="mb-6">
                  <h4 className="font-medium text-slate-700 mb-3">Asset Group Templates</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-3">
                    {defaultTemplates.asset_groups.map((template, index) => (
                      <div key={index} className="bg-white rounded-lg p-3 border border-slate-200">
                        <div className="flex items-center justify-between mb-2">
                          <h5 className="font-medium text-sm text-slate-900">{template.name}</h5>
                          <button
                            onClick={() => handleCloneTemplate(template, true)}
                            className="p-1 text-slate-400 hover:text-slate-600 rounded"
                            title="Clone to customize"
                          >
                            <Copy className="w-3 h-3" />
                          </button>
                        </div>
                        <p className="text-xs text-slate-600">{template.description}</p>
                        <p className="text-xs text-emerald-600 mt-1">{template.custom_fields?.length || 0} fields</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Asset Type Templates */}
                <div className="mb-6">
                  <h4 className="font-medium text-slate-700 mb-3">Asset Type Templates</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-3">
                    {defaultTemplates.asset_types.map((template, index) => (
                      <div key={index} className="bg-white rounded-lg p-3 border border-slate-200">
                        <div className="flex items-center justify-between mb-2">
                          <h5 className="font-medium text-sm text-slate-900">{template.name}</h5>
                          <button
                            onClick={() => handleCloneTemplate({...template, template_type: 'asset_type'}, false)}
                            className="p-1 text-slate-400 hover:text-slate-600 rounded"
                            title="Clone to customize"
                          >
                            <Copy className="w-3 h-3" />
                          </button>
                        </div>
                        <p className="text-xs text-slate-600">{template.description}</p>
                        <p className="text-xs text-blue-600 mt-1">Requires: {template.asset_group_name}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Asset Templates */}
                <div>
                  <h4 className="font-medium text-slate-700 mb-3">Asset Templates</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-3">
                    {defaultTemplates.assets.map((template, index) => (
                      <div key={index} className="bg-white rounded-lg p-3 border border-slate-200">
                        <div className="flex items-center justify-between mb-2">
                          <h5 className="font-medium text-sm text-slate-900">{template.name}</h5>
                          <button
                            onClick={() => handleCloneTemplate({...template, template_type: 'asset'}, false)}
                            className="p-1 text-slate-400 hover:text-slate-600 rounded"
                            title="Clone to customize"
                          >
                            <Copy className="w-3 h-3" />
                          </button>
                        </div>
                        <p className="text-xs text-slate-600">{template.description}</p>
                        <p className="text-xs text-purple-600 mt-1">Requires: {template.asset_group_name} → {template.asset_type_name}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Create/Edit Template Tab */}
          {(activeTab === 'create' || activeTab === 'edit') && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="form-label">Template Name *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="form-input"
                    placeholder="Enter template name"
                  />
                </div>

                <div>
                  <label className="form-label">Template Type *</label>
                  <select
                    value={formData.template_type}
                    onChange={(e) => setFormData({...formData, template_type: e.target.value})}
                    className="form-input"
                  >
                    <option value="asset_group">Asset Group Template</option>
                    <option value="asset_type">Asset Type Template</option>
                    <option value="asset">Asset Template</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="form-label">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="form-input"
                  rows="3"
                  placeholder="Describe what this template is for"
                />
              </div>

              <IconPicker
                selectedIcon={formData.icon}
                onSelect={(icon) => setFormData({...formData, icon})}
                title="Template Icon"
              />

              <div className="flex items-center space-x-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_public}
                    onChange={(e) => setFormData({...formData, is_public: e.target.checked})}
                    className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                  />
                  <span className="ml-2 text-sm text-slate-700">Make this template public (other users can use it)</span>
                </label>
              </div>

              <FieldManager
                fields={formData.custom_fields}
                onChange={(fields) => setFormData({...formData, custom_fields: fields})}
                title="Template Custom Fields"
              />

              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button
                  onClick={() => { resetForm(); setActiveTab('browse'); }}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={activeTab === 'edit' ? handleUpdateTemplate : handleCreateTemplate}
                  className="btn-primary flex items-center space-x-2"
                >
                  <Save className="w-4 h-4" />
                  <span>{activeTab === 'edit' ? 'Update Template' : 'Create Template'}</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TemplateManager;