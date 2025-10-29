import React, { useState, useEffect } from 'react';
import { useAuth } from '../App';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { 
  Building2, 
  Plus, 
  ArrowLeft, 
  Edit3, 
  Trash2,
  Users,
  Package,
  Settings,
  Database
} from 'lucide-react';
import ConfirmDialog from './ConfirmDialog';
import Toast from './Toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const OrganizationManager = () => {
  const { user } = useAuth();
  const [organizations, setOrganizations] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  
  // Edit functionality
  const [editingOrg, setEditingOrg] = useState(null);
  const [editOrgData, setEditOrgData] = useState({ name: '', description: '' });
  
  // Dialog and notification state
  const [confirmDialog, setConfirmDialog] = useState({ isOpen: false, type: '', data: null });
  const [toast, setToast] = useState({ isOpen: false, message: '', type: 'success' });

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    try {
      const response = await axios.get(`${API}/organizations`);
      setOrganizations(response.data);
    } catch (error) {
      console.error('Error fetching organizations:', error);
      setToast({
        isOpen: true,
        message: 'Failed to fetch organizations: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrganization = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    setCreating(true);
    setError('');

    try {
      const response = await axios.post(`${API}/organizations`, formData);
      setOrganizations([...organizations, response.data]);
      setFormData({ name: '', description: '' });
      setShowCreateForm(false);
    } catch (error) {
      console.error('Error creating organization:', error);
      setError(error.response?.data?.detail || 'Failed to create organization');
    } finally {
      setCreating(false);
    }
  };

  // Edit functionality
  const startEditOrganization = (org) => {
    setEditingOrg(org.id);
    setEditOrgData({
      name: org.name,
      description: org.description || ''
    });
  };

  const cancelEditOrganization = () => {
    setEditingOrg(null);
    setEditOrgData({ name: '', description: '' });
  };

  const saveEditOrganization = async () => {
    try {
      const response = await axios.put(`${API}/organizations/${editingOrg}`, editOrgData);
      
      // Update the organization in state
      setOrganizations(prevOrgs => 
        prevOrgs.map(org => org.id === editingOrg ? response.data : org)
      );
      
      setEditingOrg(null);
      setEditOrgData({ name: '', description: '' });
      setToast({
        isOpen: true,
        message: 'Organization updated successfully!',
        type: 'success'
      });
      
    } catch (error) {
      console.error('Error updating organization:', error);
      setToast({
        isOpen: true,
        message: 'Failed to update organization: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    }
  };

  // Delete functionality
  const handleDeleteOrganization = (orgId, orgName) => {
    setConfirmDialog({
      isOpen: true,
      type: 'deleteOrg',
      data: { orgId, orgName }
    });
  };

  const deleteOrganization = async (orgId, orgName) => {
    try {
      await axios.delete(`${API}/organizations/${orgId}`);
      
      // Remove organization from state
      setOrganizations(prevOrgs => prevOrgs.filter(org => org.id !== orgId));
      
      setToast({
        isOpen: true,
        message: `Organization "${orgName}" deleted successfully!`,
        type: 'success'
      });
      
    } catch (error) {
      console.error('Error deleting organization:', error);
      setToast({
        isOpen: true,
        message: 'Failed to delete organization: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    }
  };

  const handleConfirmAction = () => {
    const { type, data } = confirmDialog;
    
    if (type === 'deleteOrg') {
      deleteOrganization(data.orgId, data.orgName);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="container py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link 
                to="/"
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-900 transition-colors"
                data-testid="back-to-dashboard"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back to Dashboard</span>
              </Link>
              
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-slate-900">Organizations</h1>
                  <p className="text-sm text-slate-600">Manage your organizations and settings</p>
                </div>
              </div>
            </div>
            
            <button
              onClick={() => setShowCreateForm(true)}
              className="btn-primary flex items-center space-x-2"
              data-testid="create-org-button"
            >
              <Plus className="w-4 h-4" />
              <span>New Organization</span>
            </button>
          </div>
        </div>
      </header>

      <main className="container py-8">
        {/* Create Organization Form */}
        {showCreateForm && (
          <div className="mb-8 bg-white rounded-xl shadow-sm border border-slate-200 p-6 slide-up">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Create New Organization</h3>
            
            <form onSubmit={handleCreateOrganization} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="form-label" htmlFor="name">
                    Organization Name *
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter organization name"
                    required
                    data-testid="org-name-input"
                  />
                </div>
                
                <div>
                  <label className="form-label" htmlFor="description">
                    Description
                  </label>
                  <input
                    type="text"
                    id="description"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Brief description (optional)"
                    data-testid="org-description-input"
                  />
                </div>
              </div>
              
              {error && (
                <div className="form-error" data-testid="create-error">
                  {error}
                </div>
              )}
              
              <div className="flex items-center space-x-3">
                <button
                  type="submit"
                  disabled={creating || !formData.name.trim()}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  data-testid="create-submit-button"
                >
                  {creating ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Creating...</span>
                    </div>
                  ) : (
                    'Create Organization'
                  )}
                </button>
                
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateForm(false);
                    setFormData({ name: '', description: '' });
                    setError('');
                  }}
                  className="btn-secondary"
                  data-testid="cancel-create-button"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Organizations List */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200">
          <div className="p-6 border-b border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-slate-900">Your Organizations</h2>
                <p className="text-slate-600">Manage organizations and their asset structures</p>
              </div>
              <div className="text-sm text-slate-500">
                {organizations.length} {organizations.length === 1 ? 'organization' : 'organizations'}
              </div>
            </div>
          </div>
          
          {organizations.length === 0 ? (
            <div className="text-center py-16">
              <Building2 className="w-20 h-20 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-slate-900 mb-2">No Organizations Yet</h3>
              <p className="text-slate-600 mb-6 max-w-md mx-auto">
                Organizations help you structure and manage your IT assets. 
                Create your first organization to get started.
              </p>
              <button
                onClick={() => setShowCreateForm(true)}
                className="btn-primary flex items-center space-x-2 mx-auto"
                data-testid="create-first-org-empty"
              >
                <Plus className="w-4 h-4" />
                <span>Create Your First Organization</span>
              </button>
            </div>
          ) : (
            <div className="divide-y divide-slate-200">
              {organizations.map((org) => {
                const isEditing = editingOrg === org.id;
                
                return (
                  <div 
                    key={org.id}
                    className="p-6 hover:bg-slate-50 transition-colors"
                    data-testid={`org-row-${org.id}`}
                  >
                    {isEditing ? (
                      // Edit Form
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="form-label">Organization Name</label>
                            <input
                              type="text"
                              value={editOrgData.name}
                              onChange={(e) => setEditOrgData({...editOrgData, name: e.target.value})}
                              className="form-input"
                              data-testid={`edit-org-name-${org.id}`}
                            />
                          </div>
                          <div>
                            <label className="form-label">Description</label>
                            <input
                              type="text"
                              value={editOrgData.description}
                              onChange={(e) => setEditOrgData({...editOrgData, description: e.target.value})}
                              className="form-input"
                              data-testid={`edit-org-description-${org.id}`}
                            />
                          </div>
                        </div>
                        <div className="flex space-x-3">
                          <button 
                            onClick={saveEditOrganization}
                            className="btn-primary"
                            data-testid={`save-org-${org.id}`}
                          >
                            Save Changes
                          </button>
                          <button 
                            onClick={cancelEditOrganization}
                            className="btn-secondary"
                            data-testid={`cancel-org-${org.id}`}
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      // Display Mode
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
                            <Building2 className="w-6 h-6 text-emerald-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-slate-900">{org.name}</h3>
                            <p className="text-slate-600">
                              {org.description || 'No description provided'}
                            </p>
                            <div className="flex items-center space-x-4 mt-2 text-sm text-slate-500">
                              <span>Created {new Date(org.created_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-3">
                          <Link
                            to={`/organizations/${org.id}/assets`}
                            className="btn-outline flex items-center space-x-2"
                            data-testid={`manage-assets-${org.id}`}
                          >
                            <Package className="w-4 h-4" />
                            <span>Manage Assets</span>
                          </Link>
                          
                          <button 
                            onClick={() => startEditOrganization(org)}
                            className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
                            title="Edit Organization"
                            data-testid={`edit-org-${org.id}`}
                          >
                            <Edit3 className="w-4 h-4" />
                          </button>
                          
                          <button 
                            onClick={() => handleDeleteOrganization(org.id, org.name)}
                            className="p-2 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                            title="Delete Organization"
                            data-testid={`delete-org-${org.id}`}
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Usage Instructions */}
        {organizations.length > 0 && (
          <div className="mt-8 bg-emerald-50 border border-emerald-200 rounded-xl p-6">
            <div className="flex items-start space-x-3">
              <Database className="w-6 h-6 text-emerald-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold text-emerald-900 mb-2">Next Steps</h3>
                <div className="text-emerald-800 space-y-2">
                  <p>• <strong>Asset Groups:</strong> Create categories like "Hardware", "Software", "Identity & Access"</p>
                  <p>• <strong>Asset Types:</strong> Define specific types within groups like "Laptops", "Servers", "Games"</p>
                  <p>• <strong>Custom Fields:</strong> Configure data fields that match your organization's needs</p>
                  <p>• <strong>Assets:</strong> Add individual assets with custom data and relationships</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Confirmation Dialog */}
      <ConfirmDialog
        isOpen={confirmDialog.isOpen}
        onClose={() => setConfirmDialog({ isOpen: false, type: '', data: null })}
        onConfirm={handleConfirmAction}
        title="Delete Organization"
        message={
          confirmDialog.type === 'deleteOrg' ? 
            `Are you sure you want to delete "${confirmDialog.data?.orgName}"? This will also delete all associated asset groups, types, and assets. This action cannot be undone.` :
            'Please confirm this action.'
        }
        confirmText="Delete"
        type="danger"
      />

      {/* Toast Notifications */}
      <Toast
        isOpen={toast.isOpen}
        onClose={() => setToast({ isOpen: false, message: '', type: 'success' })}
        message={toast.message}
        type={toast.type}
      />
    </div>
  );
};

export default OrganizationManager;
