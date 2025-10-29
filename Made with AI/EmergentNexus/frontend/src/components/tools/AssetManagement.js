import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { 
  Table as TableIcon, 
  Plus, 
  Edit,
  Trash,
  Link as LinkIcon,
  Search,
  Filter,
  Download,
  Upload
} from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

const assetTypes = [
  'Document',
  'Image',
  'Video',
  'Audio',
  'Spreadsheet',
  'Code',
  'Design',
  'Other'
];

const statusOptions = [
  'Active',
  'Archived',
  'In Review',
  'Deprecated',
  'Draft'
];

export default function AssetManagement() {
  const [assets, setAssets] = useState([]);
  const [filteredAssets, setFilteredAssets] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [isAssetModalOpen, setIsAssetModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [sortField, setSortField] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [assetForm, setAssetForm] = useState({
    name: '',
    description: '',
    type: 'Document',
    status: 'Active',
    url: '',
    fileSize: '',
    version: '1.0',
    category: '',
    tags: [],
    metadata: {}
  });
  
  const { nodes, api, actions } = useWorkspace();
  
  useEffect(() => {
    const assetItems = nodes.filter(node => node.node_type === 'asset-item');
    setAssets(assetItems);
  }, [nodes]);

  useEffect(() => {
    let filtered = assets;
    
    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(asset =>
        asset.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (asset.content.description && asset.content.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
        asset.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }
    
    // Apply type filter
    if (filterType) {
      filtered = filtered.filter(asset => asset.content.type === filterType);
    }
    
    // Apply status filter
    if (filterStatus) {
      filtered = filtered.filter(asset => asset.content.status === filterStatus);
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
      let aVal, bVal;
      
      switch (sortField) {
        case 'name':
          aVal = a.title.toLowerCase();
          bVal = b.title.toLowerCase();
          break;
        case 'type':
          aVal = a.content.type;
          bVal = b.content.type;
          break;
        case 'status':
          aVal = a.content.status;
          bVal = b.content.status;
          break;
        case 'created_at':
        default:
          aVal = new Date(a.created_at);
          bVal = new Date(b.created_at);
          break;
      }
      
      if (sortOrder === 'desc') {
        return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
      } else {
        return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      }
    });
    
    setFilteredAssets(filtered);
  }, [assets, searchQuery, filterType, filterStatus, sortField, sortOrder]);

  const openNewAssetModal = () => {
    setSelectedAsset(null);
    setAssetForm({
      name: '',
      description: '',
      type: 'Document',
      status: 'Active',
      url: '',
      fileSize: '',
      version: '1.0',
      category: '',
      tags: [],
      metadata: {}
    });
    setIsAssetModalOpen(true);
  };

  const openEditAssetModal = (asset) => {
    setSelectedAsset(asset);
    setAssetForm({
      name: asset.title,
      description: asset.content.description || '',
      type: asset.content.type || 'Document',
      status: asset.content.status || 'Active',
      url: asset.content.url || '',
      fileSize: asset.content.fileSize || '',
      version: asset.content.version || '1.0',
      category: asset.content.category || '',
      tags: asset.tags || [],
      metadata: asset.content.metadata || {}
    });
    setIsAssetModalOpen(true);
  };

  const saveAsset = async () => {
    if (!assetForm.name.trim()) return;
    
    const assetData = {
      node_type: 'asset-item',
      title: assetForm.name.trim(),
      content: {
        description: assetForm.description,
        type: assetForm.type,
        status: assetForm.status,
        url: assetForm.url,
        fileSize: assetForm.fileSize,
        version: assetForm.version,
        category: assetForm.category,
        metadata: assetForm.metadata
      },
      tags: assetForm.tags
    };

    try {
      if (selectedAsset) {
        await api.updateNode(selectedAsset.id, assetData);
      } else {
        await api.createNode(assetData);
      }
      setIsAssetModalOpen(false);
    } catch (error) {
      console.error('Failed to save asset:', error);
    }
  };

  const deleteAsset = async (assetId) => {
    try {
      await api.deleteNode(assetId);
    } catch (error) {
      console.error('Failed to delete asset:', error);
    }
  };

  const addTag = (tag) => {
    if (tag.trim() && !assetForm.tags.includes(tag.trim())) {
      setAssetForm({
        ...assetForm,
        tags: [...assetForm.tags, tag.trim()]
      });
    }
  };

  const removeTag = (tagToRemove) => {
    setAssetForm({
      ...assetForm,
      tags: assetForm.tags.filter(tag => tag !== tagToRemove)
    });
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'Active': 'bg-green-100 text-green-800',
      'Archived': 'bg-gray-100 text-gray-800',
      'In Review': 'bg-yellow-100 text-yellow-800',
      'Deprecated': 'bg-red-100 text-red-800',
      'Draft': 'bg-blue-100 text-blue-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getTypeColor = (type) => {
    const colors = {
      'Document': 'text-blue-400',
      'Image': 'text-green-400',
      'Video': 'text-purple-400',
      'Audio': 'text-yellow-400',
      'Spreadsheet': 'text-emerald-400',
      'Code': 'text-red-400',
      'Design': 'text-pink-400',
      'Other': 'text-slate-400'
    };
    return colors[type] || 'text-slate-400';
  };

  const exportAssets = () => {
    const csvContent = [
      'Name,Type,Status,Category,Description,URL,File Size,Version,Tags,Created',
      ...filteredAssets.map(asset => [
        asset.title,
        asset.content.type,
        asset.content.status,
        asset.content.category,
        asset.content.description,
        asset.content.url,
        asset.content.fileSize,
        asset.content.version,
        asset.tags.join('; '),
        new Date(asset.created_at).toLocaleDateString()
      ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'assets.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="h-full bg-slate-900 p-6 flex flex-col" data-testid="asset-management">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <TableIcon className="h-6 w-6 text-orange-400" />
            Asset Management
          </h1>
          
          <div className="text-sm text-slate-400">
            {filteredAssets.length} of {assets.length} assets
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={exportAssets}
            className="text-slate-400 hover:text-white"
            data-testid="export-assets-btn"
          >
            <Download className="h-4 w-4 mr-1" />
            Export
          </Button>
          
          <Button
            size="sm"
            onClick={openNewAssetModal}
            className="bg-orange-600 hover:bg-orange-700"
            data-testid="add-asset-btn"
          >
            <Plus className="h-4 w-4 mr-1" />
            Add Asset
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 mb-6 p-4 bg-slate-800 rounded-lg border border-slate-700">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Search assets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-slate-700 border-slate-600 text-white"
              data-testid="asset-search-input"
            />
          </div>
        </div>
        
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="bg-slate-700 border border-slate-600 text-white rounded px-3 py-2"
          data-testid="type-filter-select"
        >
          <option value="">All Types</option>
          {assetTypes.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
        
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="bg-slate-700 border border-slate-600 text-white rounded px-3 py-2"
          data-testid="status-filter-select"
        >
          <option value="">All Status</option>
          {statusOptions.map(status => (
            <option key={status} value={status}>{status}</option>
          ))}
        </select>
        
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            setSearchQuery('');
            setFilterType('');
            setFilterStatus('');
          }}
          className="text-slate-400 hover:text-white"
          data-testid="clear-filters-btn"
        >
          Clear
        </Button>
      </div>

      {/* Assets Table */}
      <div className="flex-1 bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <div className="overflow-auto h-full">
          <table className="w-full">
            <thead className="bg-slate-700 sticky top-0">
              <tr>
                <th 
                  className="text-left p-4 font-medium text-slate-300 cursor-pointer hover:text-white"
                  onClick={() => handleSort('name')}
                  data-testid="sort-name-header"
                >
                  Name {sortField === 'name' && (sortOrder === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  className="text-left p-4 font-medium text-slate-300 cursor-pointer hover:text-white"
                  onClick={() => handleSort('type')}
                  data-testid="sort-type-header"
                >
                  Type {sortField === 'type' && (sortOrder === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  className="text-left p-4 font-medium text-slate-300 cursor-pointer hover:text-white"
                  onClick={() => handleSort('status')}
                  data-testid="sort-status-header"
                >
                  Status {sortField === 'status' && (sortOrder === 'asc' ? '↑' : '↓')}
                </th>
                <th className="text-left p-4 font-medium text-slate-300">Description</th>
                <th className="text-left p-4 font-medium text-slate-300">Tags</th>
                <th 
                  className="text-left p-4 font-medium text-slate-300 cursor-pointer hover:text-white"
                  onClick={() => handleSort('created_at')}
                  data-testid="sort-date-header"
                >
                  Created {sortField === 'created_at' && (sortOrder === 'asc' ? '↑' : '↓')}
                </th>
                <th className="text-left p-4 font-medium text-slate-300">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAssets.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center p-12 text-slate-400">
                    <TableIcon className="h-12 w-12 mx-auto mb-4 text-slate-500" />
                    <div className="text-lg font-medium mb-2">
                      {assets.length === 0 ? 'No Assets' : 'No Assets Found'}
                    </div>
                    <div className="text-sm">
                      {assets.length === 0 
                        ? 'Add your first asset to get started'
                        : 'Try adjusting your filters'
                      }
                    </div>
                  </td>
                </tr>
              ) : (
                filteredAssets.map((asset) => (
                  <tr 
                    key={asset.id} 
                    className="border-t border-slate-600 hover:bg-slate-700 cursor-pointer"
                    onClick={() => openEditAssetModal(asset)}
                    data-testid={`asset-row-${asset.id}`}
                  >
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${getTypeColor(asset.content.type).replace('text-', 'bg-')}`} />
                        <div>
                          <div className="font-medium text-white">{asset.title}</div>
                          {asset.content.category && (
                            <div className="text-xs text-slate-400">{asset.content.category}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className={`${getTypeColor(asset.content.type)} font-medium`}>
                        {asset.content.type}
                      </span>
                    </td>
                    <td className="p-4">
                      <Badge variant="secondary" className={getStatusColor(asset.content.status)}>
                        {asset.content.status}
                      </Badge>
                    </td>
                    <td className="p-4 max-w-xs">
                      <div className="text-slate-300 text-sm truncate">
                        {asset.content.description || '-'}
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex flex-wrap gap-1">
                        {asset.tags.slice(0, 3).map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {asset.tags.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{asset.tags.length - 3}
                          </Badge>
                        )}
                      </div>
                    </td>
                    <td className="p-4 text-slate-400 text-sm">
                      {new Date(asset.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-1">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            openEditAssetModal(asset);
                          }}
                          className="h-8 w-8 p-0 text-slate-400 hover:text-white"
                          data-testid={`edit-asset-${asset.id}`}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            actions.setSelectedNode(asset);
                          }}
                          className="h-8 w-8 p-0 text-blue-400 hover:text-blue-300"
                          data-testid={`link-asset-${asset.id}`}
                        >
                          <LinkIcon className="h-4 w-4" />
                        </Button>
                        
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteAsset(asset.id);
                          }}
                          className="h-8 w-8 p-0 text-red-400 hover:text-red-300"
                          data-testid={`delete-asset-${asset.id}`}
                        >
                          <Trash className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Asset Modal */}
      <Dialog open={isAssetModalOpen} onOpenChange={setIsAssetModalOpen}>
        <DialogContent className="max-w-2xl bg-slate-800 border-slate-700 max-h-[90vh] overflow-y-auto" data-testid="asset-modal">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <TableIcon className="h-5 w-5 text-orange-400" />
              {selectedAsset ? 'Edit Asset' : 'Add New Asset'}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            {/* Name */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Asset Name *
              </label>
              <Input
                placeholder="Enter asset name..."
                value={assetForm.name}
                onChange={(e) => setAssetForm({ ...assetForm, name: e.target.value })}
                className="bg-slate-700 border-slate-600 text-white"
                data-testid="asset-name-input"
              />
            </div>

            {/* Type and Status */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Type
                </label>
                <select
                  value={assetForm.type}
                  onChange={(e) => setAssetForm({ ...assetForm, type: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2"
                  data-testid="asset-type-select"
                >
                  {assetTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Status
                </label>
                <select
                  value={assetForm.status}
                  onChange={(e) => setAssetForm({ ...assetForm, status: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2"
                  data-testid="asset-status-select"
                >
                  {statusOptions.map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Description
              </label>
              <textarea
                placeholder="Describe this asset..."
                value={assetForm.description}
                onChange={(e) => setAssetForm({ ...assetForm, description: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2 resize-none"
                rows={3}
                data-testid="asset-description-input"
              />
            </div>

            {/* URL and File Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  URL/Location
                </label>
                <Input
                  placeholder="https://... or /path/to/file"
                  value={assetForm.url}
                  onChange={(e) => setAssetForm({ ...assetForm, url: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="asset-url-input"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  File Size
                </label>
                <Input
                  placeholder="e.g., 2.5MB"
                  value={assetForm.fileSize}
                  onChange={(e) => setAssetForm({ ...assetForm, fileSize: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="asset-size-input"
                />
              </div>
            </div>

            {/* Version and Category */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Version
                </label>
                <Input
                  placeholder="1.0"
                  value={assetForm.version}
                  onChange={(e) => setAssetForm({ ...assetForm, version: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="asset-version-input"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Category
                </label>
                <Input
                  placeholder="e.g., Marketing, Design, Development"
                  value={assetForm.category}
                  onChange={(e) => setAssetForm({ ...assetForm, category: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="asset-category-input"
                />
              </div>
            </div>

            {/* Tags */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Tags
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {assetForm.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                    {tag}
                    <button
                      onClick={() => removeTag(tag)}
                      className="ml-1 text-slate-400 hover:text-red-400"
                    >
                      ×
                    </button>
                  </Badge>
                ))}
              </div>
              <Input
                placeholder="Add tags (press Enter)..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    addTag(e.target.value);
                    e.target.value = '';
                  }
                }}
                className="bg-slate-700 border-slate-600 text-white"
                data-testid="asset-tags-input"
              />
            </div>

            {/* Actions */}
            <div className="flex justify-between pt-4">
              <div>
                {selectedAsset && (
                  <Button
                    variant="outline"
                    onClick={() => deleteAsset(selectedAsset.id)}
                    className="text-red-400 border-red-400 hover:bg-red-400 hover:text-white"
                    data-testid="delete-asset-modal-btn"
                  >
                    <Trash className="h-4 w-4 mr-1" />
                    Delete
                  </Button>
                )}
              </div>
              
              <div className="flex gap-3">
                <Button 
                  variant="outline" 
                  onClick={() => setIsAssetModalOpen(false)}
                  data-testid="cancel-asset-btn"
                >
                  Cancel
                </Button>
                <Button
                  onClick={saveAsset}
                  disabled={!assetForm.name.trim()}
                  className="bg-orange-600 hover:bg-orange-700"
                  data-testid="save-asset-btn"
                >
                  {selectedAsset ? 'Update' : 'Create'} Asset
                </Button>
              </div>
            </div>

            {/* Link Action */}
            {selectedAsset && (
              <div className="pt-2 border-t border-slate-700">
                <Button
                  variant="outline"
                  onClick={() => {
                    actions.setSelectedNode(selectedAsset);
                    setIsAssetModalOpen(false);
                  }}
                  className="w-full text-blue-400 border-blue-400 hover:bg-blue-400 hover:text-white"
                  data-testid="link-asset-modal-btn"
                >
                  <LinkIcon className="h-4 w-4 mr-1" />
                  Link to Other Nodes
                </Button>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}