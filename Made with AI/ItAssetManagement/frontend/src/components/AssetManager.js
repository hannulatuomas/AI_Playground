import React, { useState, useEffect } from 'react';
import { useAuth } from '../App';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  ArrowLeft, 
  Plus, 
  Package,
  Edit3,
  Trash2,
  Search,
  Filter,
  Settings,
  Layers,
  Database,
  Tag,
  Link as LinkIcon,
  Building2,
  Grid3X3,
  List,
  X,
  Table,
  Trello,
  ChevronDown,
  ChevronRight,
  // Asset Icons
  Box, Monitor, Code, Router, Cloud, Shield, User, Cable, Plug, Bug, Smartphone,
  Laptop, Server, HardDrive, Cpu, MemoryStick, Printer, Camera, Headphones,
  Keyboard, Mouse, Speaker, Gamepad2, Globe, Lock, Key, Terminal, FileText,
  Folder, Archive, Download, Upload, Network, Users, Mail, Phone, MapPin,
  Building, Home, Briefcase, Calculator, Clock, Calendar, Star, Flag, Zap,
  Wrench, Cog, Activity, BarChart3, TrendingUp, Package2, Circle, Square,
  Triangle, Diamond, Tablet, Wifi
} from 'lucide-react';
import ConfirmDialog from './ConfirmDialog';
import Toast from './Toast';
import TemplateDialog from './TemplateDialog';
import FieldManager from './FieldManager';
import IconPicker from './IconPicker';
import TemplateManager from './TemplateManager';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  rectSortingStrategy,
} from '@dnd-kit/sortable';
import {
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AssetManager = () => {
  const { orgId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [organization, setOrganization] = useState(null);
  const [allOrganizations, setAllOrganizations] = useState([]);
  const [assetGroups, setAssetGroups] = useState([]);
  const [assetTypes, setAssetTypes] = useState([]);
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showCreateGroupForm, setShowCreateGroupForm] = useState(false);
  const [showCreateTypeForm, setShowCreateTypeForm] = useState(false);
  const [showCreateAssetForm, setShowCreateAssetForm] = useState(false);
  const [selectedGroupId, setSelectedGroupId] = useState('');
  const [selectedTypeId, setSelectedTypeId] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState('');

  const [groupFormData, setGroupFormData] = useState({
    name: '',
    description: '',
    icon: '',
    custom_fields: []
  });

  const [typeFormData, setTypeFormData] = useState({
    name: '',
    description: '',
    icon: '',
    asset_group_id: '',
    custom_fields: []
  });

  const [assetFormData, setAssetFormData] = useState({
    name: '',
    description: '',
    icon: '',
    asset_type_id: '',
    custom_fields: [],
    custom_data: {},
    tags: [],
    relationships: [],
    custom_field_values: {}
  });

  const [detailedAssets, setDetailedAssets] = useState([]);
  const [customAssetOrder, setCustomAssetOrder] = useState(null); // Store drag order separately 
  const [assetViewMode, setAssetViewMode] = useState('cards'); // 'cards', 'list', 'table', 'board'
  const [assetFilter, setAssetFilter] = useState('all'); // 'all', specific group/type
  const [assetSort, setAssetSort] = useState('name'); // 'name', 'created_at', 'type'
  
  // Edit functionality state
  const [editingGroup, setEditingGroup] = useState(null);
  const [editingType, setEditingType] = useState(null);
  const [editingAsset, setEditingAsset] = useState(null);
  const [showEditAssetModal, setShowEditAssetModal] = useState(false);
  const [editGroupData, setEditGroupData] = useState({ name: '', description: '', icon: '', custom_fields: [] });
  const [editTypeData, setEditTypeData] = useState({ name: '', description: '', icon: '', asset_group_id: '', custom_fields: [] });
  const [editAssetData, setEditAssetData] = useState({ name: '', description: '', icon: '', asset_type_id: '', custom_fields: [], custom_data: {}, tags: [], relationships: [] });
  
  // Dialog and notification state
  const [confirmDialog, setConfirmDialog] = useState({ isOpen: false, type: '', data: null });
  const [toast, setToast] = useState({ isOpen: false, message: '', type: 'success' });
  const [templateDialog, setTemplateDialog] = useState({ isOpen: false, template: null, type: 'group' });
  const [expandedAsset, setExpandedAsset] = useState(null);
  const [templatesExpanded, setTemplatesExpanded] = useState(false);
  const [templateManagerOpen, setTemplateManagerOpen] = useState(false);

  const [defaultTemplates, setDefaultTemplates] = useState({
    assetGroups: [],
    assetTypes: {}
  });

  // Icon inheritance helper function
  const getAssetIcon = (asset) => {
    // 1. Use Asset's own icon if defined
    if (asset.icon) return asset.icon;
    
    // 2. Use Asset Type's icon if Asset has none but Type has one
    const assetType = assetTypes.find(type => type.id === asset.asset_type_id);
    if (assetType?.icon) return assetType.icon;
    
    // 3. Use Asset Group's icon if Type has none but Group has one
    const assetGroup = assetGroups.find(group => group.id === asset.asset_group_id);
    if (assetGroup?.icon) return assetGroup.icon;
    
    // 4. Default fallback icon
    return 'Box';
  };

  // Icon component mapping
  const getIconComponent = (iconName) => {
    const iconMap = {
      Box, Monitor, Code, Router, Cloud, Shield, User, Cable, Plug, Bug, Smartphone,
      Laptop, Server, HardDrive, Cpu, MemoryStick, Printer, Camera, Headphones,
      Keyboard, Mouse, Speaker, Gamepad2, Globe, Lock, Key, Terminal, FileText,
      Folder, Archive, Download, Upload, Network, Users, Mail, Phone, MapPin,
      Building, Home, Briefcase, Calculator, Clock, Calendar, Star, Flag, Zap,
      Wrench, Cog, Activity, BarChart3, TrendingUp, Package2, Circle, Square,
      Triangle, Diamond, Tablet, Wifi, Building2, Package
    };
    return iconMap[iconName] || Box;
  };

  useEffect(() => {
    fetchAllData();
    fetchDefaultTemplates();
  }, [orgId]);

  const fetchAllData = async () => {
    try {
      // Fetch all organizations for dropdown
      const allOrgsResponse = await axios.get(`${API}/organizations`);
      setAllOrganizations(allOrgsResponse.data);
      
      // Fetch current organization
      const orgResponse = await axios.get(`${API}/organizations/${orgId}`);
      setOrganization(orgResponse.data);

      // Fetch asset groups
      const groupsResponse = await axios.get(`${API}/organizations/${orgId}/asset-groups`);
      setAssetGroups(groupsResponse.data);

      // Fetch all asset types for this org
      const allTypes = [];
      for (const group of groupsResponse.data) {
        try {
          const typesResponse = await axios.get(`${API}/asset-groups/${group.id}/asset-types`);
          allTypes.push(...typesResponse.data);
        } catch (error) {
          console.error(`Error fetching types for group ${group.id}:`, error);
        }
      }
      setAssetTypes(allTypes);

      // Fetch assets
      const assetsResponse = await axios.get(`${API}/organizations/${orgId}/assets`);
      setAssets(assetsResponse.data);

      // Fetch detailed assets for better view
      const detailedResponse = await axios.get(`${API}/organizations/${orgId}/assets/detailed`);
      setDetailedAssets(detailedResponse.data);

    } catch (error) {
      console.error('Error fetching data:', error);
      setToast({
        isOpen: true,
        message: 'Failed to load organization data: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchDefaultTemplates = async () => {
    try {
      const [groupsRes, typesRes, assetsRes] = await Promise.all([
        axios.get(`${API}/templates/default-asset-groups`),
        axios.get(`${API}/templates/default-asset-types`),
        axios.get(`${API}/templates/default-assets`)
      ]);
      setDefaultTemplates({
        assetGroups: groupsRes.data,
        assetTypes: typesRes.data,
        assets: assetsRes.data
      });
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const createAssetGroup = async (e) => {
    e.preventDefault();
    if (!groupFormData.name.trim()) return;

    try {
      const response = await axios.post(`${API}/asset-groups`, {
        ...groupFormData,
        organization_id: orgId
      });
      setAssetGroups([...assetGroups, response.data]);
      setGroupFormData({ name: '', description: '', icon: '', custom_fields: [] });
      setShowCreateGroupForm(false);
    } catch (error) {
      console.error('Error creating asset group:', error);
      setError(error.response?.data?.detail || 'Failed to create asset group');
    }
  };

  const createAssetType = async (e) => {
    e.preventDefault();
    if (!typeFormData.name.trim() || !typeFormData.asset_group_id) return;

    try {
      const response = await axios.post(`${API}/asset-types`, typeFormData);
      setAssetTypes([...assetTypes, response.data]);
      setTypeFormData({ name: '', description: '', icon: '', asset_group_id: '', custom_fields: [] });
      setShowCreateTypeForm(false);
    } catch (error) {
      console.error('Error creating asset type:', error);
      setError(error.response?.data?.detail || 'Failed to create asset type');
    }
  };

  const createAsset = async (e) => {
    e.preventDefault();
    if (!assetFormData.name.trim() || !assetFormData.asset_type_id) return;

    try {
      // Combine custom_data with custom_field_values
      const assetData = {
        ...assetFormData,
        custom_data: {
          ...assetFormData.custom_data,
          ...assetFormData.custom_field_values
        }
      };
      
      const response = await axios.post(`${API}/assets`, assetData);
      setAssets([...assets, response.data]);
      
      // Refresh detailed assets
      const detailedResponse = await axios.get(`${API}/organizations/${orgId}/assets/detailed`);
      const newAssets = detailedResponse.data;
      
      // If we have a custom order, integrate the new asset into it
      if (customAssetOrder) {
        const updatedOrder = [...customAssetOrder, newAssets.find(asset => !customAssetOrder.find(existing => existing.id === asset.id))].filter(Boolean);
        setCustomAssetOrder(updatedOrder);
      }
      setDetailedAssets(newAssets);
      
      setAssetFormData({ name: '', description: '', icon: '', asset_type_id: '', custom_fields: [], custom_data: {}, tags: [], relationships: [], custom_field_values: {} });
      setShowCreateAssetForm(false);
      
      setToast({
        isOpen: true,
        message: `Asset "${response.data.name}" created successfully!`,
        type: 'success'
      });
      
    } catch (error) {
      console.error('Error creating asset:', error);
      setToast({
        isOpen: true,
        message: 'Failed to create asset: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    }
  };

  const handleTemplateClick = (template, type) => {
    setTemplateDialog({
      isOpen: true,
      template,
      type
    });
  };

  const createFromTemplate = async (templateData, templateType) => {
    try {
      let response;
      let successMessage;
      
      if (templateType === 'group') {
        // Create Asset Group from template
        response = await axios.post(`${API}/asset-groups`, {
          name: templateData.name,
          description: templateData.description,
          icon: templateData.icon,
          organization_id: orgId,
          custom_fields: templateData.customFields || []
        });
        setAssetGroups([...assetGroups, response.data]);
        successMessage = `Created "${templateData.name}" asset group successfully!`;
        
      } else if (templateType === 'type') {
        // Create Asset Type from template
        // Pre-fill the form data instead of creating directly
        setTypeFormData({
          name: templateData.name,
          description: templateData.description,
          icon: templateData.icon || '',
          asset_group_id: '', // User needs to select
          custom_fields: templateData.customFields || []
        });
        setToast({
          isOpen: true,
          message: `Template "${templateData.name}" loaded! Please select an Asset Group.`,
          type: 'success'
        });
        return;
        
      } else if (templateType === 'asset') {
        // Create Asset from template - need to auto-create parent entities if needed
        // For now, pre-fill the form
        setAssetFormData({
          name: templateData.name,
          description: templateData.description,
          icon: templateData.icon || '',
          asset_type_id: '', // User needs to select or create
          custom_fields: templateData.customFields || [],
          custom_data: {},
          tags: [],
          relationships: [],
          custom_field_values: {}
        });
        setToast({
          isOpen: true,
          message: `Template "${templateData.name}" loaded! Please select Asset Type or create: ${templateData.asset_group_name} → ${templateData.asset_type_name}`,
          type: 'success'
        });
        return;
      }
      
      if (successMessage) {
        setToast({
          isOpen: true,
          message: successMessage,
          type: 'success'
        });
      }
      
    } catch (error) {
      console.error('Error creating from template:', error);
      setToast({
        isOpen: true,
        message: 'Failed to create from template: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    }
  };

  const handleDeleteGroup = (groupId, groupName) => {
    setConfirmDialog({
      isOpen: true,
      type: 'deleteGroup',
      data: { groupId, groupName }
    });
  };

  const deleteAssetGroup = async (groupId, groupName) => {
    try {
      await axios.delete(`${API}/asset-groups/${groupId}`);
      
      // Update state to remove deleted group
      setAssetGroups(prevGroups => prevGroups.filter(g => g.id !== groupId));
      // Also remove associated types and assets
      setAssetTypes(prevTypes => prevTypes.filter(t => t.asset_group_id !== groupId));
      setAssets(prevAssets => prevAssets.filter(a => a.asset_group_id !== groupId));
      
      setToast({
        isOpen: true,
        message: `Asset group "${groupName}" deleted successfully!`,
        type: 'success'
      });
      
    } catch (error) {
      console.error('Error deleting asset group:', error);
      setToast({
        isOpen: true,
        message: 'Failed to delete asset group: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    }
  };

  const handleDeleteType = (typeId, typeName) => {
    setConfirmDialog({
      isOpen: true,
      type: 'deleteType',
      data: { typeId, typeName }
    });
  };

  const deleteAssetType = async (typeId, typeName) => {
    try {
      await axios.delete(`${API}/asset-types/${typeId}`);
      
      // Update state to remove deleted type
      setAssetTypes(prevTypes => prevTypes.filter(t => t.id !== typeId));
      // Also remove associated assets
      setAssets(prevAssets => prevAssets.filter(a => a.asset_type_id !== typeId));
      
      setToast({
        isOpen: true,
        message: `Asset type "${typeName}" deleted successfully!`,
        type: 'success'
      });
      
    } catch (error) {
      console.error('Error deleting asset type:', error);
      setToast({
        isOpen: true,
        message: 'Failed to delete asset type: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    }
  };

  const handleDeleteAsset = (assetId, assetName) => {
    setConfirmDialog({
      isOpen: true,
      type: 'deleteAsset',
      data: { assetId, assetName }
    });
  };

  const deleteAsset = async (assetId, assetName) => {
    try {
      await axios.delete(`${API}/assets/${assetId}`);
      
      // Update state to remove deleted asset
      setAssets(prevAssets => prevAssets.filter(a => a.id !== assetId));
      
      // Refresh detailed assets if they exist
      if (detailedAssets.length > 0) {
        setDetailedAssets(prevDetailed => prevDetailed.filter(a => a.id !== assetId));
      }
      
      setToast({
        isOpen: true,
        message: `Asset "${assetName}" deleted successfully!`,
        type: 'success'
      });
      
    } catch (error) {
      console.error('Error deleting asset:', error);
      setToast({
        isOpen: true,
        message: 'Failed to delete asset: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    }
  };

  // Edit functionality
  const startEditGroup = (group) => {
    setEditingGroup(group.id);
    setEditGroupData({
      name: group.name,
      description: group.description || '',
      icon: group.icon || '',
      custom_fields: group.custom_fields || []
    });
  };

  const cancelEditGroup = () => {
    setEditingGroup(null);
    setEditGroupData({ name: '', description: '', icon: '', custom_fields: [] });
  };

  const saveEditGroup = async () => {
    try {
      const response = await axios.put(`${API}/asset-groups/${editingGroup}`, {
        ...editGroupData,
        organization_id: orgId
      });
      
      // Update the group in state
      setAssetGroups(prevGroups => 
        prevGroups.map(g => g.id === editingGroup ? response.data : g)
      );
      
      setEditingGroup(null);
      setEditGroupData({ name: '', description: '', icon: '', custom_fields: [] });
      setToast({
        isOpen: true,
        message: 'Asset group updated successfully!',
        type: 'success'
      });
      
    } catch (error) {
      console.error('Error updating asset group:', error);
      setToast({
        isOpen: true,
        message: 'Failed to update asset group: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    }
  };

  const startEditType = (type) => {
    setEditingType(type.id);
    setEditTypeData({
      name: type.name,
      description: type.description || '',
      icon: type.icon || '',
      asset_group_id: type.asset_group_id,
      custom_fields: type.custom_fields || []
    });
  };

  const cancelEditType = () => {
    setEditingType(null);
    setEditTypeData({ name: '', description: '', icon: '', asset_group_id: '', custom_fields: [] });
  };

  const saveEditType = async () => {
    try {
      const response = await axios.put(`${API}/asset-types/${editingType}`, editTypeData);
      
      // Update the type in state
      setAssetTypes(prevTypes => 
        prevTypes.map(t => t.id === editingType ? response.data : t)
      );
      
      setEditingType(null);
      setEditTypeData({ name: '', description: '', icon: '', asset_group_id: '', custom_fields: [] });
      setToast({
        isOpen: true,
        message: 'Asset type updated successfully!',
        type: 'success'
      });
      
    } catch (error) {
      console.error('Error updating asset type:', error);
      setToast({
        isOpen: true,
        message: 'Failed to update asset type: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    }
  };

  const startEditAsset = (asset) => {
    setEditingAsset(asset.id);
    setEditAssetData({
      name: asset.name,
      description: asset.description || '',
      icon: asset.icon || '',
      asset_type_id: asset.asset_type_id,
      custom_fields: asset.custom_fields || [],
      custom_data: asset.custom_data || {},
      tags: asset.tags || [],
      relationships: asset.relationships || []
    });
    setShowEditAssetModal(true);
  };

  const cancelEditAsset = () => {
    setEditingAsset(null);
    setEditAssetData({ name: '', description: '', icon: '', asset_type_id: '', custom_fields: [], custom_data: {}, tags: [], relationships: [] });
    setShowEditAssetModal(false);
  };

  // Sensors for drag and drop
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Fixed drag handler - uses same array as SortableContext
  const handleDragEnd = (event) => {
    const { active, over } = event;
    
    if (active.id !== over?.id) {
      // Use displayAssets - exactly what the UI shows
      const currentArray = displayAssets;
      const oldIndex = currentArray.findIndex((asset) => asset.id === active.id);
      const newIndex = currentArray.findIndex((asset) => asset.id === over.id);
      
      if (oldIndex !== -1 && newIndex !== -1) {
        const reorderedAssets = arrayMove([...currentArray], oldIndex, newIndex);
        setCustomAssetOrder(reorderedAssets);
        
        const movedAsset = currentArray[oldIndex];
        setToast({
          isOpen: true,
          message: `Moved "${movedAsset.name}" to position ${newIndex + 1}`,
          type: 'success'
        });
      }
    }
  };

  // Sorting functionality for table view
  const handleSort = (field) => {
    const isCurrentField = assetSort === field;
    const newSortDirection = isCurrentField && assetSort.includes('_desc') ? field : `${field}_desc`;
    setAssetSort(newSortDirection);
  };

  // Reset custom drag order to original database order
  const resetAssetOrder = () => {
    setCustomAssetOrder(null);
    setToast({
      isOpen: true,
      message: 'Asset order reset to default',
      type: 'info'
    });
  };

  // Enhanced filtering and display logic with custom drag order support
  const displayAssets = customAssetOrder ? customAssetOrder : detailedAssets;

  // Sortable Card Component
  const SortableAssetCard = ({ asset, viewMode }) => {
    const {
      attributes,
      listeners,
      setNodeRef,
      transform,
      transition,
      isDragging,
    } = useSortable({ id: asset.id });

    const style = {
      transform: CSS.Transform.toString(transform),
      transition,
      opacity: isDragging ? 0.8 : 1,
      zIndex: isDragging ? 999 : 1,
    };

    if (viewMode === 'cards') {
      return (
        <div
          ref={setNodeRef}
          style={style}
          className={`relative bg-white rounded-xl shadow-sm border border-slate-200 p-8 hover:shadow-lg hover:border-slate-300 transition-all duration-200 group cursor-pointer ${
            isDragging ? 'shadow-2xl rotate-1 ring-2 ring-emerald-200' : ''
          }`}
          data-testid={`asset-card-${asset.id}`}
          onClick={() => expandedAsset === asset.id ? setExpandedAsset(null) : setExpandedAsset(asset.id)}
        >
          {/* Drag Handle */}
          <div 
            {...attributes}
            {...listeners}
            className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity z-10 cursor-grab active:cursor-grabbing"
            onClick={(e) => e.stopPropagation()}
            title="Drag to reorder"
          >
            <div className="p-2 text-slate-500 hover:text-emerald-600 bg-white hover:bg-emerald-50 rounded-lg shadow-md border border-slate-200 hover:border-emerald-200 transition-all">
              <Grid3X3 className="w-4 h-4" />
            </div>
          </div>

          {/* Card Content */}
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
              <Tag className="w-6 h-6 text-purple-600" />
            </div>
            <div className="flex items-center space-x-1">
              <button 
                onClick={(e) => { e.stopPropagation(); startEditAsset(asset); }}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
                title="Edit Asset"
                data-testid={`edit-asset-${asset.id}`}
              >
                <Edit3 className="w-4 h-4" />
              </button>
              <button 
                onClick={(e) => { e.stopPropagation(); handleDeleteAsset(asset.id, asset.name); }}
                className="p-1.5 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                title="Delete Asset"
                data-testid={`delete-asset-${asset.id}`}
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="space-y-3">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                {(() => {
                  const IconComponent = getIconComponent(getAssetIcon(asset));
                  return <IconComponent className="w-8 h-8 text-emerald-600 flex-shrink-0" />;
                })()}
                <div className="flex-1">
                  <h3 className="font-semibold text-slate-900 text-lg">{asset.name}</h3>
                </div>
              </div>
              <p className="text-sm text-slate-600 line-clamp-2">{asset.description || 'No description'}</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-500">Type:</span>
                <span className="text-slate-900 font-medium">{asset.asset_type_name}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-500">Group:</span>
                <span className="text-slate-900 font-medium">{asset.asset_group_name}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-500">Created:</span>
                <span className="text-slate-900 font-medium">{new Date(asset.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            {/* Custom Fields Display */}
            {asset.custom_data && Object.keys(asset.custom_data).length > 0 && (
              <div>
                <label className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2 block">Inherited Fields</label>
                <div className="grid grid-cols-1 gap-2">
                  {Object.entries(asset.custom_data).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-slate-600">{key.replace(/_/g, ' ')}:</span>
                      <span className="text-slate-900 font-medium">
                        {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value?.toString() || 'N/A'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Asset-Specific Fields Display */}
            {asset.custom_fields && asset.custom_fields.length > 0 && (
              <div>
                <label className="text-xs font-medium text-emerald-600 uppercase tracking-wide mb-2 block">Asset-Specific Fields</label>
                <div className="grid grid-cols-1 gap-2">
                  {asset.custom_fields.map((field) => {
                    const value = asset.custom_data?.[field.name];
                    return (
                      <div key={field.id || field.name} className="flex justify-between text-sm">
                        <span className="text-emerald-700">{field.label}:</span>
                        <span className="text-sm font-medium text-emerald-900">
                          {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value?.toString() || field.default_value || 'N/A'}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {expandedAsset === asset.id && (
              <div className="pt-4 border-t border-slate-200 space-y-4">
                {/* Relationships */}
                {asset.relationships && asset.relationships.length > 0 && (
                  <div>
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2 block">Dependencies</label>
                    <div className="flex flex-wrap gap-2">
                      {asset.relationships.map((relId, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded font-mono">
                          {relId}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* All Tags */}
                {asset.tags && asset.tags.length > 0 && (
                  <div>
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2 block">All Tags</label>
                    <div className="flex flex-wrap gap-2">
                      {asset.tags.map((tag, index) => (
                        <span key={index} className="px-2 py-1 bg-slate-100 text-slate-700 text-xs rounded">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      );
    }

    // For list view
    if (viewMode === 'list') {
      return (
        <div 
          ref={setNodeRef}
          style={style}
          className={`p-8 hover:bg-slate-50 transition-all duration-200 border-b border-slate-200 group ${
            isDragging ? 'bg-emerald-50 shadow-lg' : ''
          }`}
          data-testid={`asset-row-${asset.id}`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* Drag Handle */}
              <div 
                {...attributes}
                {...listeners}
                className="opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing"
                title="Drag to reorder"
              >
                <div className="p-1 text-slate-400 hover:text-emerald-600 rounded transition-colors">
                  <Grid3X3 className="w-4 h-4" />
                </div>
              </div>
              
              <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                {(() => {
                  const IconComponent = getIconComponent(getAssetIcon(asset));
                  return <IconComponent className="w-5 h-5 text-emerald-600" />;
                })()}
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-slate-900">{asset.name}</h4>
                <div className="flex items-center space-x-4 mt-1 text-xs text-slate-500">
                  <span>{asset.asset_type_name}</span>
                  <span>•</span>
                  <span>{asset.asset_group_name}</span>
                  <span>•</span>
                  <span>{new Date(asset.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button 
                onClick={() => startEditAsset(asset)}
                className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
                title="Edit Asset"
                data-testid={`edit-asset-${asset.id}`}
              >
                <Edit3 className="w-4 h-4" />
              </button>
              <button 
                onClick={() => handleDeleteAsset(asset.id, asset.name)}
                className="p-2 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                title="Delete Asset"
                data-testid={`delete-asset-${asset.id}`}
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="mt-4">
            <p className="text-sm text-slate-600 line-clamp-2">{asset.description || 'No description'}</p>
            
            {/* Custom Fields Display in List View */}
            {asset.custom_data && Object.keys(asset.custom_data).length > 0 && (
              <div className="mt-2 pt-2 border-t border-slate-100">
                <div className="flex flex-wrap gap-2">
                  {Object.entries(asset.custom_data).slice(0, 4).map(([key, value]) => (
                    <span key={key} className="inline-flex items-center px-2 py-1 bg-slate-50 text-slate-700 text-xs rounded">
                      <span className="text-slate-500 mr-1">{key.replace(/_/g, ' ')}:</span>
                      <span className="font-medium">
                        {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value?.toString() || 'N/A'}
                      </span>
                    </span>
                  ))}
                  {Object.keys(asset.custom_data).length > 4 && (
                    <span className="inline-flex items-center px-2 py-1 bg-slate-100 text-slate-500 text-xs rounded">
                      +{Object.keys(asset.custom_data).length - 4} more
                    </span>
                  )}
                </div>
              </div>
            )}
            
            {/* Asset-Specific Fields in List View */}
            {asset.custom_fields && asset.custom_fields.length > 0 && (
              <div className="mt-2 pt-2 border-t border-emerald-100">
                <div className="flex flex-wrap gap-2">
                  <span className="text-xs font-medium text-emerald-600 uppercase tracking-wide mr-2">Asset Fields:</span>
                  {asset.custom_fields.slice(0, 3).map((field) => {
                    const value = asset.custom_data?.[field.name];
                    return (
                      <span key={field.id || field.name} className="inline-flex items-center px-2 py-1 bg-emerald-50 text-emerald-700 text-xs rounded">
                        <span className="text-emerald-500 mr-1">{field.label}:</span>
                        <span className="font-medium">
                          {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value?.toString() || field.default_value || 'N/A'}
                        </span>
                      </span>
                    );
                  })}
                  {asset.custom_fields.length > 3 && (
                    <span className="inline-flex items-center px-2 py-1 bg-emerald-100 text-emerald-600 text-xs rounded">
                      +{asset.custom_fields.length - 3} more asset fields
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      );
    }

    // Board view (simplified for now)
    return (
      <div 
        ref={setNodeRef}
        style={style}
        className={`bg-white rounded-lg p-4 shadow-sm border border-slate-200 hover:shadow-md transition-all cursor-pointer group ${
          isDragging ? 'shadow-lg rotate-1 ring-2 ring-emerald-200' : ''
        }`}
        onClick={() => expandedAsset === asset.id ? setExpandedAsset(null) : setExpandedAsset(asset.id)}
      >
        {/* Drag Handle */}
        <div 
          {...attributes}
          {...listeners}
          className="opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing float-right"
          onClick={(e) => e.stopPropagation()}
          title="Drag to reorder"
        >
          <div className="p-1 text-slate-400 hover:text-emerald-600 rounded transition-colors">
            <Grid3X3 className="w-3 h-3" />
          </div>
        </div>

        <div className="flex items-center space-x-3 mb-2">
          {(() => {
            const IconComponent = getIconComponent(getAssetIcon(asset));
            return <IconComponent className="w-4 h-4 text-emerald-600 flex-shrink-0" />;
          })()}
          <h4 className="font-medium text-slate-900 text-sm truncate">{asset.name}</h4>
        </div>
        
        <p className="text-xs text-slate-600 mb-2 line-clamp-2">{asset.description || 'No description'}</p>
        
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>{asset.asset_type_name}</span>
          <div className="flex space-x-1">
            <button onClick={(e) => { e.stopPropagation(); startEditAsset(asset); }} className="text-emerald-600 hover:text-emerald-900">
              <Edit3 className="w-3 h-3" />
            </button>
            <button onClick={(e) => { e.stopPropagation(); handleDeleteAsset(asset.id, asset.name); }} className="text-red-600 hover:text-red-900">
              <Trash2 className="w-3 h-3" />
            </button>
          </div>
        </div>
        
        {/* Custom Fields */}
        {asset.custom_data && Object.keys(asset.custom_data).length > 0 && (
          <div className="mt-2 pt-2 border-t border-slate-100">
            <div className="flex flex-wrap gap-1">
              {Object.entries(asset.custom_data).slice(0, 2).map(([key, value]) => (
                <span key={key} className="inline-flex items-center px-1.5 py-0.5 bg-slate-50 text-slate-700 text-xs rounded">
                  {typeof value === 'boolean' ? (value ? '✓' : '✗') : value?.toString()?.substring(0, 10) || 'N/A'}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {/* Asset-Specific Fields */}
        {asset.custom_fields && asset.custom_fields.length > 0 && (
          <div className="mt-2 pt-2 border-t border-emerald-100">
            <div className="flex flex-wrap gap-1">
              <span className="text-xs font-medium text-emerald-600 mr-1">Asset:</span>
              {asset.custom_fields.slice(0, 2).map((field) => {
                const value = asset.custom_data?.[field.name];
                return (
                  <span key={field.id || field.name} className="inline-flex items-center px-1.5 py-0.5 bg-emerald-50 text-emerald-700 text-xs rounded">
                    {typeof value === 'boolean' ? (value ? '✓' : '✗') : value?.toString()?.substring(0, 8) || 'N/A'}
                  </span>
                );
              })}
              {asset.custom_fields.length > 2 && (
                <span className="text-xs text-emerald-600">+{asset.custom_fields.length - 2}</span>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  const saveEditAsset = async () => {
    try {
      const response = await axios.put(`${API}/assets/${editingAsset}`, editAssetData);
      
      // Update the asset in state
      setAssets(prevAssets => 
        prevAssets.map(a => a.id === editingAsset ? response.data : a)
      );
      
      // Refresh detailed assets
      const detailedResponse = await axios.get(`${API}/organizations/${orgId}/assets/detailed`);
      const newAssets = detailedResponse.data;
      
      // If we have a custom order, integrate the new asset into it
      if (customAssetOrder) {
        const updatedOrder = [...customAssetOrder, newAssets.find(asset => !customAssetOrder.find(existing => existing.id === asset.id))].filter(Boolean);
        setCustomAssetOrder(updatedOrder);
      }
      setDetailedAssets(newAssets);
      
      setEditingAsset(null);
      setEditAssetData({ name: '', description: '', icon: '', asset_type_id: '', custom_fields: [], custom_data: {}, tags: [], relationships: [] });
      setShowEditAssetModal(false);
      setToast({
        isOpen: true,
        message: 'Asset updated successfully!',
        type: 'success'
      });
      
    } catch (error) {
      console.error('Error updating asset:', error);
      setToast({
        isOpen: true,
        message: 'Failed to update asset: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    }
  };

  // Confirmation dialog handler
  const handleConfirmAction = () => {
    const { type, data } = confirmDialog;
    
    switch (type) {
      case 'deleteGroup':
        deleteAssetGroup(data.groupId, data.groupName);
        break;
      case 'deleteType':
        deleteAssetType(data.typeId, data.typeName);
        break;
      case 'deleteAsset':
        deleteAsset(data.assetId, data.assetName);
        break;
      default:
        break;
    }
  };

  const getAssetsByType = (typeId) => {
    return assets.filter(asset => asset.asset_type_id === typeId);
  };

  const getTypesByGroup = (groupId) => {
    return assetTypes.filter(type => type.asset_group_id === groupId);
  };

  const filteredAssets = assets.filter(asset =>
    asset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    asset.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  if (!organization) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Organization Not Found</h2>
          <p className="text-slate-600 mb-4">The organization you're looking for doesn't exist or you don't have access to it.</p>
          <Link to="/" className="btn-primary">
            Back to Dashboard
          </Link>
        </div>
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
                <span>Dashboard</span>
              </Link>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
                    <Building2 className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold text-slate-900">{organization.name}</h1>
                    <p className="text-sm text-slate-600">Asset Management</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-3 sm:space-y-0 sm:space-x-6">
              {/* Organization Dropdown - moved here for proper spacing */}
              {allOrganizations.length > 1 && (
                <div className="relative flex-shrink-0">
                  <select
                    value={orgId}
                    onChange={(e) => navigate(`/organizations/${e.target.value}/assets`)}
                    className="appearance-none bg-white border border-slate-300 rounded-lg pl-10 pr-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 w-full sm:min-w-[200px]"
                    data-testid="org-dropdown"
                  >
                    {allOrganizations.map(org => (
                      <option key={org.id} value={org.id}>
                        {org.name}
                      </option>
                    ))}
                  </select>
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                    <Building2 className="w-4 h-4 text-slate-400" />
                  </div>
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                    <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              )}
              
              <div className="relative flex-1 min-w-0">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search assets..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  data-testid="asset-search"
                />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-slate-200">
        <div className="container">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: Database },
              { id: 'groups', label: 'Asset Groups', icon: Layers },
              { id: 'types', label: 'Asset Types', icon: Package },
              { id: 'assets', label: 'Assets', icon: Tag }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-emerald-500 text-emerald-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
                data-testid={`tab-${tab.id}`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      <main className="container py-8">
        {/* Removed old error display - using Toast component now */}

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Asset Groups</p>
                    <p className="text-3xl font-bold text-slate-900" data-testid="groups-count">
                      {assetGroups.length}
                    </p>
                  </div>
                  <Layers className="w-8 h-8 text-emerald-600" />
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Asset Types</p>
                    <p className="text-3xl font-bold text-slate-900" data-testid="types-count">
                      {assetTypes.length}
                    </p>
                  </div>
                  <Package className="w-8 h-8 text-blue-600" />
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Total Assets</p>
                    <p className="text-3xl font-bold text-slate-900" data-testid="assets-count">
                      {assets.length}
                    </p>
                  </div>
                  <Tag className="w-8 h-8 text-purple-600" />
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">With Relations</p>
                    <p className="text-3xl font-bold text-slate-900">
                      {assets.filter(asset => asset.relationships.length > 0).length}
                    </p>
                  </div>
                  <LinkIcon className="w-8 h-8 text-orange-600" />
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => {
                    setActiveTab('groups');
                    setShowCreateGroupForm(true);
                  }}
                  className="flex items-center space-x-3 p-4 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition-colors group text-left"
                  data-testid="quick-create-group"
                >
                  <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
                    <Plus className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-slate-900 group-hover:text-emerald-700">Add Asset Group</p>
                    <p className="text-sm text-slate-600">Create a new category</p>
                  </div>
                </button>

                <button
                  onClick={() => {
                    setActiveTab('types');
                    setShowCreateTypeForm(true);
                  }}
                  className="flex items-center space-x-3 p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors group text-left"
                  data-testid="quick-create-type"
                >
                  <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                    <Plus className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-slate-900 group-hover:text-blue-700">Add Asset Type</p>
                    <p className="text-sm text-slate-600">Define asset specifications</p>
                  </div>
                </button>

                <button
                  onClick={() => {
                    setActiveTab('assets');
                    setShowCreateAssetForm(true);
                  }}
                  className="flex items-center space-x-3 p-4 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors group text-left"
                  data-testid="quick-create-asset"
                >
                  <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
                    <Plus className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-slate-900 group-hover:text-purple-700">Add Asset</p>
                    <p className="text-sm text-slate-600">Register new asset</p>
                  </div>
                </button>
              </div>
            </div>

            {/* Hierarchy View */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Asset Hierarchy</h3>
              {assetGroups.length === 0 ? (
                <div className="text-center py-8">
                  <Layers className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <p className="text-slate-600">No asset groups created yet. Start by creating your first asset group.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {assetGroups.map((group) => {
                    const groupTypes = getTypesByGroup(group.id);
                    return (
                      <div key={group.id} className="border border-slate-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <Layers className="w-5 h-5 text-emerald-600" />
                            <h4 className="font-semibold text-slate-900">{group.name}</h4>
                            <span className="text-sm text-slate-500">
                              ({groupTypes.length} types, {groupTypes.reduce((acc, type) => acc + getAssetsByType(type.id).length, 0)} assets)
                            </span>
                          </div>
                        </div>
                        
                        {groupTypes.length > 0 ? (
                          <div className="ml-8 space-y-2">
                            {groupTypes.map((type) => {
                              const typeAssets = getAssetsByType(type.id);
                              return (
                                <div key={type.id} className="flex items-center space-x-3 text-sm">
                                  <Package className="w-4 h-4 text-blue-600" />
                                  <span className="font-medium">{type.name}</span>
                                  <span className="text-slate-500">({typeAssets.length} assets)</span>
                                </div>
                              );
                            })}
                          </div>
                        ) : (
                          <p className="ml-8 text-sm text-slate-500">No asset types defined</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Asset Groups Tab */}
        {activeTab === 'groups' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-slate-900">Asset Groups</h2>
                <p className="text-slate-600">Organize your assets into logical categories</p>
              </div>
              <button
                onClick={() => setShowCreateGroupForm(true)}
                className="btn-primary flex items-center space-x-2"
                data-testid="create-group-button"
              >
                <Plus className="w-4 h-4" />
                <span>New Group</span>
              </button>
            </div>

            {/* Create Group Form */}
            {showCreateGroupForm && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Create Asset Group</h3>
                
                {/* Templates */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-3">
                    <button
                      onClick={() => setTemplatesExpanded(!templatesExpanded)}
                      className="flex items-center space-x-2 text-sm font-medium text-slate-700 hover:text-slate-900 transition-colors"
                    >
                      {templatesExpanded ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronRight className="w-4 h-4" />
                      )}
                      <span>Quick Start Templates ({defaultTemplates.assetGroups.length} available)</span>
                    </button>
                    <button
                      onClick={() => setTemplateManagerOpen(true)}
                      className="text-sm text-emerald-600 hover:text-emerald-700 font-medium transition-colors"
                    >
                      Manage Templates
                    </button>
                  </div>
                  
                  {templatesExpanded && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {defaultTemplates.assetGroups.map((template, index) => (
                        <button
                          key={index}
                          onClick={() => handleTemplateClick(template, 'group')}
                          className="p-4 text-left bg-slate-50 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors group"
                          data-testid={`template-group-${index}`}
                        >
                          <div className="flex items-center space-x-2 mb-2">
                            {/* Template icon preview */}
                            {(() => {
                              const IconComponent = getIconComponent(template.icon || 'Package');
                              return <IconComponent className="w-4 h-4 text-emerald-600" />;
                            })()}
                            <p className="font-medium text-sm text-slate-900 group-hover:text-slate-800">{template.name}</p>
                          </div>
                          <p className="text-xs text-slate-600 line-clamp-2">{template.description}</p>
                          {template.custom_fields && (
                            <p className="text-xs text-emerald-600 mt-2">{template.custom_fields.length} fields included</p>
                          )}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                <form onSubmit={createAssetGroup} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">Name *</label>
                      <input
                        type="text"
                        value={groupFormData.name}
                        onChange={(e) => setGroupFormData({...groupFormData, name: e.target.value})}
                        className="form-input"
                        placeholder="e.g., Hardware, Software"
                        required
                        data-testid="group-name-input"
                      />
                    </div>
                    <div>
                      <label className="form-label">Description</label>
                      <input
                        type="text"
                        value={groupFormData.description}
                        onChange={(e) => setGroupFormData({...groupFormData, description: e.target.value})}
                        className="form-input"
                        placeholder="Brief description"
                        data-testid="group-description-input"
                      />
                    </div>
                    
                    <div>
                      <IconPicker
                        selectedIcon={groupFormData.icon}
                        onSelect={(icon) => setGroupFormData({...groupFormData, icon})}
                        title="Group Icon"
                      />
                    </div>
                  </div>
                  
                  {/* Custom Fields Management */}
                  <FieldManager
                    fields={groupFormData.custom_fields}
                    onChange={(fields) => setGroupFormData({...groupFormData, custom_fields: fields})}
                    title="Asset Group Fields"
                  />
                  
                  <div className="flex space-x-3">
                    <button type="submit" className="btn-primary" data-testid="create-group-submit">
                      Create Group
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setShowCreateGroupForm(false);
                        setGroupFormData({ name: '', description: '', icon: '', custom_fields: [] });
                      }}
                      className="btn-secondary"
                      data-testid="cancel-group-create"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Groups List */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {assetGroups.map((group) => {
                const groupTypes = getTypesByGroup(group.id);
                const totalAssets = groupTypes.reduce((acc, type) => acc + getAssetsByType(type.id).length, 0);
                const isEditing = editingGroup === group.id;
                
                return (
                  <div key={group.id} className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow" data-testid={`group-card-${group.id}`}>
                    {isEditing ? (
                      // Edit Form
                      <div className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="form-label">Group Name</label>
                            <input
                              type="text"
                              value={editGroupData.name}
                              onChange={(e) => setEditGroupData({...editGroupData, name: e.target.value})}
                              className="form-input"
                              data-testid={`edit-group-name-${group.id}`}
                            />
                          </div>
                          <div>
                            <label className="form-label">Description</label>
                            <textarea
                              value={editGroupData.description}
                              onChange={(e) => setEditGroupData({...editGroupData, description: e.target.value})}
                              className="form-input"
                              rows="2"
                              data-testid={`edit-group-description-${group.id}`}
                            />
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <IconPicker
                              selectedIcon={editGroupData.icon}
                              onSelect={(icon) => setEditGroupData({...editGroupData, icon})}
                              title="Group Icon"
                            />
                          </div>
                        </div>
                        
                        {/* Custom Fields Management */}
                        <FieldManager
                          fields={editGroupData.custom_fields}
                          onChange={(fields) => setEditGroupData({...editGroupData, custom_fields: fields})}
                          title="Asset Group Fields"
                        />
                        
                        <div className="flex space-x-2">
                          <button 
                            onClick={saveEditGroup}
                            className="btn-primary text-sm"
                            data-testid={`save-group-${group.id}`}
                          >
                            Save Changes
                          </button>
                          <button 
                            onClick={cancelEditGroup}
                            className="btn-secondary text-sm"
                            data-testid={`cancel-group-${group.id}`}
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      // Display Mode
                      <>
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center space-x-3 flex-1">
                            <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                              <Layers className="w-5 h-5 text-emerald-600" />
                            </div>
                            <div className="flex-1">
                              <h3 className="font-semibold text-slate-900">{group.name}</h3>
                              <p className="text-sm text-slate-600">{group.description || 'No description'}</p>
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-1">
                            <button 
                              onClick={() => startEditGroup(group)}
                              className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
                              title="Edit Group"
                              data-testid={`edit-group-${group.id}`}
                            >
                              <Edit3 className="w-4 h-4" />
                            </button>
                            <button 
                              onClick={() => handleDeleteGroup(group.id, group.name)}
                              className="p-2 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                              title="Delete Group"
                              data-testid={`delete-group-${group.id}`}
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        
                        <div className="space-y-2 text-sm text-slate-600">
                          <div className="flex justify-between">
                            <span>Asset Types:</span>
                            <span className="font-medium">{groupTypes.length}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Total Assets:</span>
                            <span className="font-medium">{totalAssets}</span>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                );
              })}
            </div>

            {assetGroups.length === 0 && !showCreateGroupForm && (
              <div className="text-center py-12">
                <Layers className="w-20 h-20 text-slate-300 mx-auto mb-4" />
                <h3 className="text-xl font-medium text-slate-900 mb-2">No Asset Groups</h3>
                <p className="text-slate-600 mb-6">Create your first asset group to start organizing your assets.</p>
                <button
                  onClick={() => setShowCreateGroupForm(true)}
                  className="btn-primary"
                  data-testid="create-first-group"
                >
                  Create Asset Group
                </button>
              </div>
            )}
          </div>
        )}

        {/* Asset Types Tab */}
        {activeTab === 'types' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-slate-900">Asset Types</h2>
                <p className="text-slate-600">Define specific types of assets within your groups</p>
              </div>
              <button
                onClick={() => setShowCreateTypeForm(true)}
                className="btn-primary flex items-center space-x-2"
                disabled={assetGroups.length === 0}
                data-testid="create-type-button"
              >
                <Plus className="w-4 h-4" />
                <span>New Type</span>
              </button>
            </div>

            {assetGroups.length === 0 ? (
              <div className="text-center py-12">
                <Package className="w-20 h-20 text-slate-300 mx-auto mb-4" />
                <h3 className="text-xl font-medium text-slate-900 mb-2">No Asset Groups</h3>
                <p className="text-slate-600 mb-6">Create asset groups first before defining asset types.</p>
                <button
                  onClick={() => setActiveTab('groups')}
                  className="btn-primary"
                  data-testid="go-to-groups"
                >
                  Create Asset Groups
                </button>
              </div>
            ) : (
              <>
                {/* Create Type Form */}
                {showCreateTypeForm && (
                  <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <h3 className="text-lg font-semibold text-slate-900 mb-4">Create Asset Type</h3>
                    
                    {/* Asset Type Templates */}
                    <div className="mb-6">
                      <div className="flex items-center justify-between mb-3">
                        <button
                          type="button"
                          onClick={() => setTemplatesExpanded(!templatesExpanded)}
                          className="flex items-center space-x-2 text-sm font-medium text-slate-700 hover:text-slate-900 transition-colors"
                        >
                          {templatesExpanded ? (
                            <ChevronDown className="w-4 h-4" />
                          ) : (
                            <ChevronRight className="w-4 h-4" />
                          )}
                          <span>Quick Start Templates ({defaultTemplates.assetTypes?.length || 0} available)</span>
                        </button>
                      </div>
                      
                      {templatesExpanded && (
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                          {(defaultTemplates.assetTypes || []).map((template, index) => (
                            <button
                              key={index}
                              type="button"
                              onClick={() => handleTemplateClick(template, 'type')}
                              className="p-3 text-left bg-slate-50 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors group"
                              data-testid={`template-type-${index}`}
                            >
                              <div className="flex items-center space-x-2 mb-2">
                                {(() => {
                                  const IconComponent = getIconComponent(template.icon || 'Package');
                                  return <IconComponent className="w-4 h-4 text-blue-600" />;
                                })()}
                                <p className="font-medium text-sm text-slate-900 group-hover:text-slate-800">{template.name}</p>
                              </div>
                              <p className="text-xs text-slate-600 line-clamp-2">{template.description}</p>
                              {template.custom_fields && (
                                <p className="text-xs text-blue-600 mt-2">{template.custom_fields.length} fields included</p>
                              )}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <form onSubmit={createAssetType} className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label className="form-label">Asset Group *</label>
                          <select
                            value={typeFormData.asset_group_id}
                            onChange={(e) => setTypeFormData({...typeFormData, asset_group_id: e.target.value})}
                            className="form-input"
                            required
                            data-testid="type-group-select"
                          >
                            <option value="">Select a group</option>
                            {assetGroups.map((group) => (
                              <option key={group.id} value={group.id}>{group.name}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="form-label">Name *</label>
                          <input
                            type="text"
                            value={typeFormData.name}
                            onChange={(e) => setTypeFormData({...typeFormData, name: e.target.value})}
                            className="form-input"
                            placeholder="e.g., Laptops, Servers"
                            required
                            data-testid="type-name-input"
                          />
                        </div>
                        <div>
                          <label className="form-label">Description</label>
                          <input
                            type="text"
                            value={typeFormData.description}
                            onChange={(e) => setTypeFormData({...typeFormData, description: e.target.value})}
                            className="form-input"
                            placeholder="Brief description"
                            data-testid="type-description-input"
                          />
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <IconPicker
                            selectedIcon={typeFormData.icon}
                            onSelect={(icon) => setTypeFormData({...typeFormData, icon})}
                            title="Type Icon"
                          />
                        </div>
                      </div>
                      
                      {/* Custom Fields Management for Asset Types */}
                      <FieldManager
                        fields={typeFormData.custom_fields}
                        onChange={(fields) => setTypeFormData({...typeFormData, custom_fields: fields})}
                        title="Asset Type Specific Fields"
                      />
                      
                      <div className="flex space-x-3">
                        <button type="submit" className="btn-primary" data-testid="create-type-submit">
                          Create Type
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setShowCreateTypeForm(false);
                            setTypeFormData({ name: '', description: '', icon: '', asset_group_id: '', custom_fields: [] });
                          }}
                          className="btn-secondary"
                          data-testid="cancel-type-create"
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {/* Types by Group */}
                <div className="space-y-6">
                  {assetGroups.map((group) => {
                    const groupTypes = getTypesByGroup(group.id);
                    
                    return (
                      <div key={group.id} className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                        <div className="flex items-center space-x-3 mb-4">
                          <Layers className="w-5 h-5 text-emerald-600" />
                          <h3 className="text-lg font-semibold text-slate-900">{group.name}</h3>
                          <span className="text-sm text-slate-500">({groupTypes.length} types)</span>
                        </div>
                        
                        {groupTypes.length > 0 ? (
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {groupTypes.map((type) => {
                              const typeAssets = getAssetsByType(type.id);
                              const isEditingType = editingType === type.id;
                              
                              return (
                                <div key={type.id} className="p-4 bg-slate-50 rounded-lg border border-slate-200 hover:bg-slate-100 transition-colors" data-testid={`type-card-${type.id}`}>
                                  {isEditingType ? (
                                    // Edit Form for Type
                                    <div className="space-y-4 p-4 bg-white rounded-lg shadow-sm">
                                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                          <label className="block text-sm font-medium text-slate-700 mb-1">Type Name</label>
                                          <input
                                            type="text"
                                            value={editTypeData.name}
                                            onChange={(e) => setEditTypeData({...editTypeData, name: e.target.value})}
                                            className="form-input text-sm"
                                            data-testid={`edit-type-name-${type.id}`}
                                          />
                                        </div>
                                        <div>
                                          <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
                                          <textarea
                                            value={editTypeData.description}
                                            onChange={(e) => setEditTypeData({...editTypeData, description: e.target.value})}
                                            className="form-input text-sm"
                                            rows="2"
                                            data-testid={`edit-type-description-${type.id}`}
                                          />
                                        </div>
                                      </div>
                                      
                                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <div>
                                          <IconPicker
                                            selectedIcon={editTypeData.icon}
                                            onSelect={(icon) => setEditTypeData({...editTypeData, icon})}
                                            title="Type Icon"
                                          />
                                        </div>
                                      </div>
                                      
                                      {/* Custom Fields Management for Asset Types */}
                                      <FieldManager
                                        fields={editTypeData.custom_fields}
                                        onChange={(fields) => setEditTypeData({...editTypeData, custom_fields: fields})}
                                        title="Asset Type Specific Fields"
                                      />
                                      
                                      <div className="flex space-x-2">
                                        <button 
                                          onClick={saveEditType}
                                          className="btn-primary text-sm"
                                          data-testid={`save-type-${type.id}`}
                                        >
                                          Save Changes
                                        </button>
                                        <button 
                                          onClick={cancelEditType}
                                          className="btn-secondary text-sm"
                                          data-testid={`cancel-type-${type.id}`}
                                        >
                                          Cancel
                                        </button>
                                      </div>
                                    </div>
                                  ) : (
                                    // Display Mode for Type
                                    <>
                                      <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center space-x-3">
                                          <Package className="w-4 h-4 text-blue-600" />
                                          <h4 className="font-medium text-slate-900">{type.name}</h4>
                                        </div>
                                        <div className="flex items-center space-x-1">
                                          <button 
                                            onClick={() => startEditType(type)}
                                            className="p-1 text-slate-400 hover:text-slate-600 rounded hover:bg-slate-200 transition-colors"
                                            title="Edit Type"
                                            data-testid={`edit-type-${type.id}`}
                                          >
                                            <Edit3 className="w-3 h-3" />
                                          </button>
                                          <button 
                                            onClick={() => handleDeleteType(type.id, type.name)}
                                            className="p-1 text-slate-400 hover:text-red-600 rounded hover:bg-red-100 transition-colors"
                                            title="Delete Type"
                                            data-testid={`delete-type-${type.id}`}
                                          >
                                            <Trash2 className="w-3 h-3" />
                                          </button>
                                        </div>
                                      </div>
                                      <p className="text-sm text-slate-600 mb-2">{type.description || 'No description'}</p>
                                      <p className="text-xs text-slate-500">{typeAssets.length} assets</p>
                                    </>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        ) : (
                          <p className="text-slate-600">No asset types defined for this group.</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </>
            )}
          </div>
        )}

        {/* Assets Tab */}
        {activeTab === 'assets' && (
          <div className="space-y-6">
            {/* Header with Controls */}
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div className="space-y-2">
                <h2 className="text-2xl font-bold text-slate-900">Assets</h2>
                <p className="text-lg text-slate-600 leading-relaxed">
                  Manage individual assets and their properties with custom fields and relationships
                </p>
              </div>
              <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                {/* View Mode Toggle */}
                <div className="flex items-center bg-slate-100 rounded-lg p-1">
                  <button
                    onClick={() => setAssetViewMode('cards')}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1 ${
                      assetViewMode === 'cards' 
                        ? 'bg-white text-slate-900 shadow-sm' 
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                    data-testid="view-mode-cards"
                    title="Card View"
                  >
                    <Grid3X3 className="w-4 h-4" />
                    <span className="hidden sm:block">Cards</span>
                  </button>
                  <button
                    onClick={() => setAssetViewMode('list')}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1 ${
                      assetViewMode === 'list' 
                        ? 'bg-white text-slate-900 shadow-sm' 
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                    data-testid="view-mode-list"
                    title="List View"
                  >
                    <List className="w-4 h-4" />
                    <span className="hidden sm:block">List</span>
                  </button>
                  <button
                    onClick={() => setAssetViewMode('table')}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1 ${
                      assetViewMode === 'table' 
                        ? 'bg-white text-slate-900 shadow-sm' 
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                    data-testid="view-mode-table"
                    title="Table View"
                  >
                    <Table className="w-4 h-4" />
                    <span className="hidden sm:block">Table</span>
                  </button>
                  <button
                    onClick={() => setAssetViewMode('board')}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1 ${
                      assetViewMode === 'board' 
                        ? 'bg-white text-slate-900 shadow-sm' 
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                    data-testid="view-mode-board"
                    title="Board View"
                  >
                    <Trello className="w-4 h-4" />
                    <span className="hidden sm:block">Board</span>
                  </button>
                </div>

                {/* Sort and Filter */}
                <div className="flex items-center gap-3">
                  <select
                    value={assetFilter}
                    onChange={(e) => setAssetFilter(e.target.value)}
                    className="px-3 py-2 border border-slate-300 rounded-lg text-sm min-w-[140px]"
                    data-testid="asset-filter"
                  >
                    <option value="all">All Assets</option>
                    {assetGroups.map((group) => (
                      <option key={group.id} value={`group_${group.id}`}>
                        {group.name} Group
                      </option>
                    ))}
                    {assetTypes.map((type) => (
                      <option key={type.id} value={`type_${type.id}`}>
                        {type.name} Type
                      </option>
                    ))}
                  </select>

                  <select
                    value={assetSort}
                    onChange={(e) => setAssetSort(e.target.value)}
                    className="px-3 py-2 border border-slate-300 rounded-lg text-sm min-w-[140px]"
                    data-testid="asset-sort"
                  >
                    <option value="name">Name (A-Z)</option>
                    <option value="name_desc">Name (Z-A)</option>
                    <option value="created_at">Created (Oldest)</option>
                    <option value="created_at_desc">Created (Newest)</option>
                    <option value="type">Type (A-Z)</option>
                    <option value="type_desc">Type (Z-A)</option>
                    <option value="group">Group (A-Z)</option>
                    <option value="group_desc">Group (Z-A)</option>
                  </select>
                  
                  {/* Reset Order Button - Only show when custom order exists */}
                  {customAssetOrder && (
                    <button
                      onClick={resetAssetOrder}
                      className="px-3 py-2 border border-orange-300 text-orange-700 bg-orange-50 hover:bg-orange-100 rounded-lg text-sm flex items-center space-x-1 transition-colors"
                      title="Reset to default order"
                      data-testid="reset-order-button"
                    >
                      <X className="w-4 h-4" />
                      <span className="hidden sm:block">Reset Order</span>
                    </button>
                  )}
                </div>

                <button
                  onClick={() => setShowCreateAssetForm(true)}
                  className="btn-primary flex items-center justify-center space-x-2 px-4 py-2"
                  disabled={assetTypes.length === 0}
                  data-testid="create-asset-button"
                >
                  <Plus className="w-4 h-4" />
                  <span>New Asset</span>
                </button>
              </div>
            </div>

            {assetTypes.length === 0 ? (
              <div className="text-center py-12">
                <Tag className="w-20 h-20 text-slate-300 mx-auto mb-4" />
                <h3 className="text-xl font-medium text-slate-900 mb-2">No Asset Types</h3>
                <p className="text-slate-600 mb-6">Create asset types first before adding individual assets.</p>
                <button
                  onClick={() => setActiveTab('types')}
                  className="btn-primary"
                  data-testid="go-to-types"
                >
                  Create Asset Types
                </button>
              </div>
            ) : (
              <>
                {/* Create Asset Form */}
                {showCreateAssetForm && (
                  <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <h3 className="text-lg font-semibold text-slate-900 mb-4">Create New Asset</h3>
                    
                    {/* Asset Templates */}
                    <div className="mb-6">
                      <div className="flex items-center justify-between mb-3">
                        <button
                          type="button"
                          onClick={() => setTemplatesExpanded(!templatesExpanded)}
                          className="flex items-center space-x-2 text-sm font-medium text-slate-700 hover:text-slate-900 transition-colors"
                        >
                          {templatesExpanded ? (
                            <ChevronDown className="w-4 h-4" />
                          ) : (
                            <ChevronRight className="w-4 h-4" />
                          )}
                          <span>Quick Start Templates</span>
                        </button>
                      </div>
                      
                      {templatesExpanded && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {defaultTemplates.assets?.map((template, index) => (
                            <button
                              key={index}
                              type="button"
                              onClick={() => handleTemplateClick(template, 'asset')}
                              className="p-3 text-left bg-slate-50 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors group"
                              data-testid={`template-asset-${index}`}
                            >
                              <div className="flex items-center space-x-2 mb-2">
                                {(() => {
                                  const IconComponent = getIconComponent(template.icon || 'Package');
                                  return <IconComponent className="w-4 h-4 text-purple-600" />;
                                })()}
                                <p className="font-medium text-sm text-slate-900 group-hover:text-slate-800">{template.name}</p>
                              </div>
                              <p className="text-xs text-slate-600 line-clamp-2">{template.description}</p>
                              <p className="text-xs text-purple-600 mt-1">Requires: {template.asset_group_name} → {template.asset_type_name}</p>
                            </button>
                          )) || (
                            <p className="text-sm text-slate-500">Asset templates will be available after adding Asset Groups and Types</p>
                          )}
                        </div>
                      )}
                    </div>
                    
                    <form onSubmit={createAsset} className="space-y-6">
                      {/* Basic Information */}
                      <div>
                        <h4 className="font-medium text-slate-900 mb-4">Basic Information</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="form-label">Asset Type *</label>
                            <select
                              value={assetFormData.asset_type_id}
                              onChange={(e) => setAssetFormData({...assetFormData, asset_type_id: e.target.value})}
                              className="form-input"
                              required
                              data-testid="asset-type-select"
                            >
                              <option value="">Select asset type</option>
                              {assetTypes.map((type) => {
                                const group = assetGroups.find(g => g.id === type.asset_group_id);
                                return (
                                  <option key={type.id} value={type.id}>
                                    {group?.name} → {type.name}
                                  </option>
                                );
                              })}
                            </select>
                          </div>
                          <div>
                            <label className="form-label">Asset Name *</label>
                            <input
                              type="text"
                              value={assetFormData.name}
                              onChange={(e) => setAssetFormData({...assetFormData, name: e.target.value})}
                              className="form-input"
                              placeholder="e.g., John's MacBook Pro"
                              required
                              data-testid="asset-name-input"
                            />
                          </div>
                        </div>
                        
                        <div className="mt-4">
                          <label className="form-label">Description</label>
                          <textarea
                            value={assetFormData.description}
                            onChange={(e) => setAssetFormData({...assetFormData, description: e.target.value})}
                            className="form-input"
                            rows="3"
                            placeholder="Detailed description of the asset"
                            data-testid="asset-description-input"
                          />
                        </div>
                        
                        <div className="mt-4">
                          <IconPicker
                            selectedIcon={assetFormData.icon}
                            onSelect={(icon) => setAssetFormData({...assetFormData, icon})}
                            title="Asset Icon"
                          />
                        </div>
                      </div>

                      {/* Custom Field Values */}
                      {assetFormData.asset_type_id && (() => {
                        const selectedType = assetTypes.find(t => t.id === assetFormData.asset_type_id);
                        const selectedGroup = assetGroups.find(g => g.id === selectedType?.asset_group_id);
                        
                        // Create a proper inheritance chain: Group fields first, then Type-specific fields
                        const groupFields = (selectedGroup?.custom_fields || []).map(f => ({...f, source: 'Group'}));
                        const typeSpecificFields = (selectedType?.custom_fields || []).filter(tf => 
                          !groupFields.some(gf => gf.name === tf.name)
                        ).map(f => ({...f, source: 'Type'}));
                        
                        const allFields = [...groupFields, ...typeSpecificFields];

                        return (
                          <div>
                            <h4 className="font-medium text-slate-900 mb-4">Custom Fields</h4>
                            {allFields.length > 0 ? (
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {allFields.map((field) => (
                                  <div key={field.id || field.name} className="space-y-1">
                                    <label className="form-label">
                                      {field.label}
                                      {field.required && <span className="text-red-500 ml-1">*</span>}
                                      <span className="ml-2 text-xs text-slate-500">
                                        (from {field.source})
                                      </span>
                                    </label>
                                    
                                    {field.type === 'text' && (
                                      <input
                                        type="text"
                                        value={assetFormData.custom_field_values[field.name] || field.default_value || ''}
                                        onChange={(e) => setAssetFormData({
                                          ...assetFormData,
                                          custom_field_values: {
                                            ...assetFormData.custom_field_values,
                                            [field.name]: e.target.value
                                          }
                                        })}
                                        className="form-input"
                                        placeholder={field.default_value || `Enter ${field.label.toLowerCase()}`}
                                        required={field.required}
                                      />
                                    )}
                                    
                                    {field.type === 'number' && (
                                      <input
                                        type="number"
                                        value={assetFormData.custom_field_values[field.name] || field.default_value || ''}
                                        onChange={(e) => setAssetFormData({
                                          ...assetFormData,
                                          custom_field_values: {
                                            ...assetFormData.custom_field_values,
                                            [field.name]: e.target.value
                                          }
                                        })}
                                        className="form-input"
                                        placeholder={field.default_value || `Enter ${field.label.toLowerCase()}`}
                                        required={field.required}
                                      />
                                    )}
                                    
                                    {field.type === 'date' && (
                                      <input
                                        type="date"
                                        value={assetFormData.custom_field_values[field.name] || field.default_value || ''}
                                        onChange={(e) => setAssetFormData({
                                          ...assetFormData,
                                          custom_field_values: {
                                            ...assetFormData.custom_field_values,
                                            [field.name]: e.target.value
                                          }
                                        })}
                                        className="form-input"
                                        required={field.required}
                                      />
                                    )}
                                    
                                    {field.type === 'boolean' && (
                                      <select
                                        value={assetFormData.custom_field_values[field.name] || field.default_value || ''}
                                        onChange={(e) => setAssetFormData({
                                          ...assetFormData,
                                          custom_field_values: {
                                            ...assetFormData.custom_field_values,
                                            [field.name]: e.target.value === 'true'
                                          }
                                        })}
                                        className="form-input"
                                        required={field.required}
                                      >
                                        <option value="">Select...</option>
                                        <option value="true">Yes</option>
                                        <option value="false">No</option>
                                      </select>
                                    )}
                                    
                                    {field.type === 'dataset' && (
                                      <select
                                        value={assetFormData.custom_field_values[field.name] || field.default_value || ''}
                                        onChange={(e) => setAssetFormData({
                                          ...assetFormData,
                                          custom_field_values: {
                                            ...assetFormData.custom_field_values,
                                            [field.name]: e.target.value
                                          }
                                        })}
                                        className="form-input"
                                        required={field.required}
                                      >
                                        <option value="">Select...</option>
                                        {(field.dataset_values || []).map((value, index) => (
                                          <option key={index} value={value}>{value}</option>
                                        ))}
                                      </select>
                                    )}
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div className="text-center py-6 bg-slate-50 rounded-lg border-2 border-dashed border-slate-200">
                                <p className="text-slate-600 text-sm">
                                  No custom fields defined for this asset type.
                                </p>
                                <p className="text-slate-500 text-xs mt-1">
                                  Add custom fields to the Asset Group or Asset Type to see them here.
                                </p>
                              </div>
                            )}
                            </div>
                          );
                      })()}
                      
                      {/* Asset-Specific Custom Fields */}
                      <FieldManager
                        fields={assetFormData.custom_fields}
                        onChange={(fields) => setAssetFormData({...assetFormData, custom_fields: fields})}
                        title="Asset-Specific Custom Fields"
                      />
                      
                      {/* Asset-Specific Field Values */}
                      {assetFormData.custom_fields.length > 0 && (
                        <div>
                          <h4 className="font-medium text-slate-900 mb-4">Asset-Specific Field Values</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {assetFormData.custom_fields.map((field) => (
                              <div key={field.id || field.name} className="space-y-1">
                                <label className="form-label">
                                  {field.label}
                                  {field.required && <span className="text-red-500 ml-1">*</span>}
                                  <span className="ml-2 text-xs text-slate-500">(Asset-specific)</span>
                                </label>
                                
                                {field.type === 'text' && (
                                  <input
                                    type="text"
                                    value={assetFormData.custom_field_values[field.name] || field.default_value || ''}
                                    onChange={(e) => setAssetFormData({
                                      ...assetFormData,
                                      custom_field_values: {
                                        ...assetFormData.custom_field_values,
                                        [field.name]: e.target.value
                                      }
                                    })}
                                    className="form-input"
                                    required={field.required}
                                  />
                                )}
                                
                                {field.type === 'number' && (
                                  <input
                                    type="number"
                                    value={assetFormData.custom_field_values[field.name] || field.default_value || ''}
                                    onChange={(e) => setAssetFormData({
                                      ...assetFormData,
                                      custom_field_values: {
                                        ...assetFormData.custom_field_values,
                                        [field.name]: e.target.value
                                      }
                                    })}
                                    className="form-input"
                                    required={field.required}
                                  />
                                )}
                                
                                {field.type === 'boolean' && (
                                  <select
                                    value={assetFormData.custom_field_values[field.name] !== undefined ? assetFormData.custom_field_values[field.name] : field.default_value || ''}
                                    onChange={(e) => setAssetFormData({
                                      ...assetFormData,
                                      custom_field_values: {
                                        ...assetFormData.custom_field_values,
                                        [field.name]: e.target.value === 'true'
                                      }
                                    })}
                                    className="form-input"
                                    required={field.required}
                                  >
                                    <option value="">Select...</option>
                                    <option value="true">Yes</option>
                                    <option value="false">No</option>
                                  </select>
                                )}
                                
                                {field.type === 'dataset' && (
                                  <select
                                    value={assetFormData.custom_field_values[field.name] || field.default_value || ''}
                                    onChange={(e) => setAssetFormData({
                                      ...assetFormData,
                                      custom_field_values: {
                                        ...assetFormData.custom_field_values,
                                        [field.name]: e.target.value
                                      }
                                    })}
                                    className="form-input"
                                    required={field.required}
                                  >
                                    <option value="">Select...</option>
                                    {(field.dataset_values || []).map((value, index) => (
                                      <option key={index} value={value}>{value}</option>
                                    ))}
                                  </select>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      <div className="flex space-x-3 pt-4 border-t">
                        <button type="submit" className="btn-primary" data-testid="create-asset-submit">
                          Create Asset
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setShowCreateAssetForm(false);
                            setAssetFormData({ name: '', description: '', icon: '', asset_type_id: '', custom_fields: [], custom_data: {}, tags: [], relationships: [], custom_field_values: {} });
                          }}
                          className="btn-secondary"
                          data-testid="cancel-asset-create"
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {/* Assets Display */}
                {(() => {
                  // Use the global displayAssets that respects custom drag order
                  let filteredAssets = displayAssets.length > 0 ? displayAssets : assets.map(asset => {
                    const assetType = assetTypes.find(t => t.id === asset.asset_type_id);
                    const assetGroup = assetGroups.find(g => g.id === asset.asset_group_id);
                    return {
                      ...asset,
                      asset_type_name: assetType?.name || 'Unknown',
                      asset_group_name: assetGroup?.name || 'Unknown'
                    };
                  });

                  if (assetFilter !== 'all') {
                    if (assetFilter.startsWith('group_')) {
                      const groupId = assetFilter.replace('group_', '');
                      filteredAssets = filteredAssets.filter(asset => asset.asset_group_id === groupId);
                    } else if (assetFilter.startsWith('type_')) {
                      const typeId = assetFilter.replace('type_', '');
                      filteredAssets = filteredAssets.filter(asset => asset.asset_type_id === typeId);
                    }
                  }

                  // Sort assets - but NOT if we have custom drag order
                  if (!customAssetOrder) {
                    filteredAssets.sort((a, b) => {
                      switch (assetSort) {
                        case 'created_at':
                          return new Date(b.created_at) - new Date(a.created_at);
                        case 'type':
                          return (a.asset_type_name || '').localeCompare(b.asset_type_name || '');
                        default:
                          return (a.name || '').localeCompare(b.name || '');
                      }
                    });
                  }

                  if (filteredAssets.length === 0) {
                    return (
                      <div className="text-center py-12">
                        <Tag className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                        <p className="text-slate-600">
                          {searchTerm ? 'No assets match your search.' : 
                           assetFilter !== 'all' ? 'No assets in this filter.' : 
                           'No assets created yet.'}
                        </p>
                      </div>
                    );
                  }

                  // Card View with Drag & Drop
                  if (assetViewMode === 'cards') {
                    return (
                      <DndContext 
                        sensors={sensors}
                        collisionDetection={closestCenter}
                        onDragEnd={handleDragEnd}
                      >
                        <SortableContext 
                          items={filteredAssets.map(asset => asset.id)}
                          strategy={rectSortingStrategy}
                        >
                          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
                            {filteredAssets.map((asset) => (
                              <SortableAssetCard key={asset.id} asset={asset} viewMode="cards" />
                            ))}
                          </div>
                        </SortableContext>
                      </DndContext>
                    );
                  }

                  // List View with Drag & Drop
                  if (assetViewMode === 'list') {
                    return (
                      <DndContext 
                        sensors={sensors}
                        collisionDetection={closestCenter}
                        onDragEnd={handleDragEnd}
                      >
                        <SortableContext 
                          items={filteredAssets.map(asset => asset.id)}
                          strategy={verticalListSortingStrategy}
                        >
                          <div className="bg-white rounded-xl shadow-sm border border-slate-200">
                            <div className="p-6 border-b border-slate-200">
                              <h3 className="text-lg font-semibold text-slate-900">All Assets ({filteredAssets.length})</h3>
                            </div>
                            
                            <div className="divide-y divide-slate-200">
                              {filteredAssets.map((asset) => (
                                <SortableAssetCard key={asset.id} asset={asset} viewMode="list" />
                              ))}
                            </div>
                          </div>
                        </SortableContext>
                      </DndContext>
                    );
                  }
                  // List view now uses SortableAssetCard component above

                  // Table View
                  if (assetViewMode === 'table') {
                    return (
                      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                        <div className="overflow-x-auto">
                          <table className="w-full">
                            <thead className="bg-slate-50 border-b border-slate-200">
                              <tr>
                                <th className="px-6 py-4 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                                  <button 
                                    onClick={() => handleSort('name')}
                                    className="flex items-center space-x-1 hover:text-slate-700 transition-colors"
                                  >
                                    <span>Asset</span>
                                    {assetSort === 'name' && <ChevronDown className="w-3 h-3" />}
                                    {assetSort === 'name_desc' && <ChevronDown className="w-3 h-3 rotate-180" />}
                                  </button>
                                </th>
                                <th className="px-6 py-4 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                                  <button 
                                    onClick={() => handleSort('type')}
                                    className="flex items-center space-x-1 hover:text-slate-700 transition-colors"
                                  >
                                    <span>Type</span>
                                    {assetSort === 'type' && <ChevronDown className="w-3 h-3" />}
                                    {assetSort === 'type_desc' && <ChevronDown className="w-3 h-3 rotate-180" />}
                                  </button>
                                </th>
                                <th className="px-6 py-4 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                                  <button 
                                    onClick={() => handleSort('group')}
                                    className="flex items-center space-x-1 hover:text-slate-700 transition-colors"
                                  >
                                    <span>Group</span>
                                    {assetSort === 'group' && <ChevronDown className="w-3 h-3" />}
                                    {assetSort === 'group_desc' && <ChevronDown className="w-3 h-3 rotate-180" />}
                                  </button>
                                </th>
                                <th className="px-6 py-4 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                                  <button 
                                    onClick={() => handleSort('created_at')}
                                    className="flex items-center space-x-1 hover:text-slate-700 transition-colors"
                                  >
                                    <span>Created</span>
                                    {assetSort === 'created_at' && <ChevronDown className="w-3 h-3" />}
                                    {assetSort === 'created_at_desc' && <ChevronDown className="w-3 h-3 rotate-180" />}
                                  </button>
                                </th>
                                <th className="px-6 py-4 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Custom Fields</th>
                                <th className="px-6 py-4 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Actions</th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-slate-200">
                              {filteredAssets.map((asset) => (
                                <tr key={asset.id} className="hover:bg-slate-50" data-testid={`asset-table-row-${asset.id}`}>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex items-center space-x-3">
                                      <div className="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center">
                                        {(() => {
                                          const IconComponent = getIconComponent(getAssetIcon(asset));
                                          return <IconComponent className="w-4 h-4 text-emerald-600" />;
                                        })()}
                                      </div>
                                      <div>
                                        <div className="font-medium text-slate-900">{asset.name}</div>
                                        <div className="text-sm text-slate-500 truncate max-w-xs">{asset.description || 'No description'}</div>
                                      </div>
                                    </div>
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{asset.asset_type_name}</td>
                                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{asset.asset_group_name}</td>
                                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{new Date(asset.created_at).toLocaleDateString()}</td>
                                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                                    <div className="flex flex-col gap-1 max-w-xs">
                                      {/* Inherited Custom Fields */}
                                      {asset.custom_data && Object.keys(asset.custom_data).length > 0 ? (
                                        <div className="flex flex-wrap gap-1">
                                          {Object.entries(asset.custom_data).slice(0, 2).map(([key, value]) => (
                                            <span key={key} className="inline-flex items-center px-2 py-1 bg-slate-100 text-slate-700 text-xs rounded">
                                              {key}: {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value?.toString() || 'N/A'}
                                            </span>
                                          ))}
                                          {Object.keys(asset.custom_data).length > 2 && (
                                            <span className="text-xs text-slate-400">+{Object.keys(asset.custom_data).length - 2}</span>
                                          )}
                                        </div>
                                      ) : null}
                                      
                                      {/* Asset-Specific Fields */}
                                      {asset.custom_fields && asset.custom_fields.length > 0 && (
                                        <div className="flex flex-wrap gap-1">
                                          {asset.custom_fields.slice(0, 2).map((field) => {
                                            const value = asset.custom_data?.[field.name];
                                            return (
                                              <span key={field.id || field.name} className="inline-flex items-center px-2 py-1 bg-emerald-100 text-emerald-700 text-xs rounded">
                                                {field.label}: {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value?.toString() || field.default_value || 'N/A'}
                                              </span>
                                            );
                                          })}
                                          {asset.custom_fields.length > 2 && (
                                            <span className="text-xs text-emerald-600">+{asset.custom_fields.length - 2} asset fields</span>
                                          )}
                                        </div>
                                      )}
                                      
                                      {/* No Fields Message */}
                                      {(!asset.custom_data || Object.keys(asset.custom_data).length === 0) && 
                                       (!asset.custom_fields || asset.custom_fields.length === 0) && (
                                        <span className="text-xs text-slate-400">No custom fields</span>
                                      )}
                                    </div>
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <div className="flex items-center justify-end space-x-2">
                                      <button 
                                        onClick={() => startEditAsset(asset)}
                                        className="text-emerald-600 hover:text-emerald-900"
                                        title="Edit Asset"
                                      >
                                        <Edit3 className="w-4 h-4" />
                                      </button>
                                      <button 
                                        onClick={() => handleDeleteAsset(asset.id, asset.name)}
                                        className="text-red-600 hover:text-red-900"
                                        title="Delete Asset"
                                      >
                                        <Trash2 className="w-4 h-4" />
                                      </button>
                                    </div>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    );
                  }

                  // Board View with Drag & Drop (Kanban-style by Asset Group)
                  if (assetViewMode === 'board') {
                    const assetsByGroup = assetGroups.reduce((acc, group) => {
                      acc[group.id] = {
                        group: group,
                        assets: filteredAssets.filter(asset => asset.asset_group_id === group.id)
                      };
                      return acc;
                    }, {});

                    return (
                      <DndContext 
                        sensors={sensors}
                        collisionDetection={closestCenter}
                        onDragEnd={handleDragEnd}
                      >
                        <div className="flex space-x-6 overflow-x-auto pb-6">
                          {Object.values(assetsByGroup).map(({ group, assets }) => (
                            <div key={group.id} className="flex-shrink-0 w-80 bg-slate-100 rounded-xl p-4">
                              <div className="flex items-center space-x-3 mb-4">
                                {(() => {
                                  const IconComponent = getIconComponent(group.icon || 'Package');
                                  return <IconComponent className="w-5 h-5 text-slate-600" />;
                                })()}
                                <h3 className="font-semibold text-slate-900">{group.name}</h3>
                                <span className="bg-slate-200 text-slate-600 text-xs px-2 py-1 rounded">{assets.length}</span>
                              </div>
                              
                              <SortableContext 
                                items={assets.map(asset => asset.id)}
                                strategy={rectSortingStrategy}
                              >
                                <div className="space-y-3 max-h-96 overflow-y-auto">
                                  {assets.map((asset) => (
                                    <SortableAssetCard key={asset.id} asset={asset} viewMode="board" />
                                  ))}
                                  
                                  {assets.length === 0 && (
                                    <div className="text-center py-8 text-slate-500">
                                      <Package className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                      <p className="text-xs">No assets in this group</p>
                                    </div>
                                  )}
                                </div>
                              </SortableContext>
                            </div>
                          ))}
                        </div>
                      </DndContext>
                    );
                  }

                  // Default fallback to cards view
                  return null;
                })()}
              </>
            )}
          </div>
        )}
      </main>

      {/* Confirmation Dialog */}
      <ConfirmDialog
        isOpen={confirmDialog.isOpen}
        onClose={() => setConfirmDialog({ isOpen: false, type: '', data: null })}
        onConfirm={handleConfirmAction}
        title={
          confirmDialog.type === 'deleteGroup' ? 'Delete Asset Group' :
          confirmDialog.type === 'deleteType' ? 'Delete Asset Type' :
          confirmDialog.type === 'deleteAsset' ? 'Delete Asset' : 'Confirm Action'
        }
        message={
          confirmDialog.type === 'deleteGroup' ? 
            `Are you sure you want to delete "${confirmDialog.data?.groupName}"? This will also delete all associated asset types and assets. This action cannot be undone.` :
          confirmDialog.type === 'deleteType' ? 
            `Are you sure you want to delete "${confirmDialog.data?.typeName}"? This will also delete all associated assets. This action cannot be undone.` :
          confirmDialog.type === 'deleteAsset' ? 
            `Are you sure you want to delete "${confirmDialog.data?.assetName}"? This action cannot be undone.` : 
            'Please confirm this action.'
        }
        confirmText="Delete"
        type="danger"
      />

      {/* Template Dialog */}
      <TemplateDialog
        isOpen={templateDialog.isOpen}
        onClose={() => setTemplateDialog({ isOpen: false, template: null, type: 'group' })}
        onConfirm={createFromTemplate}
        template={templateDialog.template}
        type={templateDialog.type}
      />

      {/* Toast Notifications */}
      <Toast
        isOpen={toast.isOpen}
        onClose={() => setToast({ isOpen: false, message: '', type: 'success' })}
        message={toast.message}
        type={toast.type}
      />

      {/* Template Manager */}
      <TemplateManager
        isOpen={templateManagerOpen}
        onClose={() => setTemplateManagerOpen(false)}
        onTemplateCreated={() => {
          // Refresh templates after creation
          fetchDefaultTemplates();
          setToast({ isOpen: true, message: 'Custom template created successfully!', type: 'success' });
        }}
      />

      {/* Asset Edit Modal */}
      {showEditAssetModal && editingAsset && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-slate-900">Edit Asset</h3>
                <button
                  onClick={cancelEditAsset}
                  className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-slate-500" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="form-label">Asset Name *</label>
                  <input
                    type="text"
                    value={editAssetData.name}
                    onChange={(e) => setEditAssetData({...editAssetData, name: e.target.value})}
                    className="form-input"
                    data-testid="edit-asset-name-modal"
                  />
                </div>

                <div>
                  <label className="form-label">Asset Type *</label>
                  <select
                    value={editAssetData.asset_type_id}
                    onChange={(e) => setEditAssetData({...editAssetData, asset_type_id: e.target.value})}
                    className="form-input"
                    data-testid="edit-asset-type-modal"
                  >
                    <option value="">Select asset type</option>
                    {assetTypes.map((type) => {
                      const group = assetGroups.find(g => g.id === type.asset_group_id);
                      return (
                        <option key={type.id} value={type.id}>
                          {group?.name} → {type.name}
                        </option>
                      );
                    })}
                  </select>
                </div>

                <div>
                  <label className="form-label">Description</label>
                  <textarea
                    value={editAssetData.description}
                    onChange={(e) => setEditAssetData({...editAssetData, description: e.target.value})}
                    className="form-input"
                    rows="3"
                    data-testid="edit-asset-description-modal"
                  />
                </div>

                <IconPicker
                  selectedIcon={editAssetData.icon}
                  onSelect={(icon) => setEditAssetData({...editAssetData, icon})}
                  title="Asset Icon"
                />

                {/* Custom Fields Section */}
                {editAssetData.asset_type_id && (() => {
                  const selectedType = assetTypes.find(t => t.id === editAssetData.asset_type_id);
                  const selectedGroup = assetGroups.find(g => g.id === selectedType?.asset_group_id);
                  
                  // Create a proper inheritance chain: Group fields first, then Type-specific fields
                  const groupFields = (selectedGroup?.custom_fields || []).map(f => ({...f, source: 'Group'}));
                  const typeSpecificFields = (selectedType?.custom_fields || []).filter(tf => 
                    !groupFields.some(gf => gf.name === tf.name)
                  ).map(f => ({...f, source: 'Type'}));
                  
                  const allFields = [...groupFields, ...typeSpecificFields];

                  if (allFields.length > 0) {
                    return (
                      <div>
                        <h5 className="font-medium text-slate-900 mb-3">Custom Fields</h5>
                        <div className="space-y-4">
                          {allFields.map((field) => (
                            <div key={field.id || field.name} className="space-y-1">
                              <label className="form-label">
                                {field.label}
                                {field.required && <span className="text-red-500 ml-1">*</span>}
                                <span className="ml-2 text-sm text-slate-500">
                                  (from {field.source})
                                </span>
                              </label>
                              
                              {field.type === 'text' && (
                                <input
                                  type="text"
                                  value={editAssetData.custom_data[field.name] || field.default_value || ''}
                                  onChange={(e) => setEditAssetData({
                                    ...editAssetData,
                                    custom_data: {
                                      ...editAssetData.custom_data,
                                      [field.name]: e.target.value
                                    }
                                  })}
                                  className="form-input"
                                  required={field.required}
                                />
                              )}
                              
                              {field.type === 'number' && (
                                <input
                                  type="number"
                                  value={editAssetData.custom_data[field.name] || field.default_value || ''}
                                  onChange={(e) => setEditAssetData({
                                    ...editAssetData,
                                    custom_data: {
                                      ...editAssetData.custom_data,
                                      [field.name]: e.target.value
                                    }
                                  })}
                                  className="form-input"
                                  required={field.required}
                                />
                              )}
                              
                              {field.type === 'boolean' && (
                                <select
                                  value={editAssetData.custom_data[field.name] !== undefined ? editAssetData.custom_data[field.name] : field.default_value || ''}
                                  onChange={(e) => setEditAssetData({
                                    ...editAssetData,
                                    custom_data: {
                                      ...editAssetData.custom_data,
                                      [field.name]: e.target.value === 'true'
                                    }
                                  })}
                                  className="form-input"
                                  required={field.required}
                                >
                                  <option value="">Select...</option>
                                  <option value="true">Yes</option>
                                  <option value="false">No</option>
                                </select>
                              )}
                              
                              {field.type === 'dataset' && (
                                <select
                                  value={editAssetData.custom_data[field.name] || field.default_value || ''}
                                  onChange={(e) => setEditAssetData({
                                    ...editAssetData,
                                    custom_data: {
                                      ...editAssetData.custom_data,
                                      [field.name]: e.target.value
                                    }
                                  })}
                                  className="form-input"
                                  required={field.required}
                                >
                                  <option value="">Select...</option>
                                  {field.dataset_values && field.dataset_values.map((option, idx) => (
                                    <option key={idx} value={option}>{option}</option>
                                  ))}
                                </select>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  }
                  return null;
                })()}
                
                {/* Asset-Specific Custom Fields */}
                <FieldManager
                  fields={editAssetData.custom_fields}
                  onChange={(fields) => setEditAssetData({...editAssetData, custom_fields: fields})}
                  title="Asset-Specific Custom Fields"
                />
                
                <div className="flex justify-end space-x-3 pt-4 border-t border-slate-200">
                  <button 
                    onClick={cancelEditAsset}
                    className="btn-secondary"
                    data-testid="cancel-asset-modal"
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={saveEditAsset}
                    className="btn-primary"
                    data-testid="save-asset-modal"
                  >
                    Save Changes
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AssetManager;