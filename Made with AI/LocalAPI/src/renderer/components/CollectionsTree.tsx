import React, { useState, useEffect } from 'react';
import {
  Box,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Typography,
  Tooltip,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  Folder as FolderIcon,
  FolderOpen as FolderOpenIcon,
  Description as RequestIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ContentCopy as DuplicateIcon,
} from '@mui/icons-material';
import type { Collection, Request } from '../../types/models';

interface CollectionsTreeProps {
  onRequestSelect?: (request: Request) => void;
}

interface TreeNode {
  id: string;
  name: string;
  type: 'collection' | 'request';
  children?: TreeNode[];
  data?: Collection | Request;
}

const CollectionsTree: React.FC<CollectionsTreeProps> = ({ onRequestSelect }) => {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  
  // Context menu state
  const [contextMenu, setContextMenu] = useState<{
    mouseX: number;
    mouseY: number;
    nodeId: string;
    nodeType: 'collection' | 'request';
  } | null>(null);

  // Dialog states
  const [collectionDialog, setCollectionDialog] = useState<{
    open: boolean;
    mode: 'create' | 'edit';
    collection?: Collection;
  }>({ open: false, mode: 'create' });

  const [requestDialog, setRequestDialog] = useState<{
    open: boolean;
    mode: 'create' | 'edit';
    collectionId?: string;
    request?: Request;
  }>({ open: false, mode: 'create' });

  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean;
    type: 'collection' | 'request';
    id: string;
    name: string;
  } | null>(null);

  // Form states
  const [collectionForm, setCollectionForm] = useState({ name: '', description: '' });
  const [requestForm, setRequestForm] = useState({ name: '', method: 'GET', url: '' });

  // Load collections on mount
  useEffect(() => {
    loadCollections();
  }, []);

  const loadCollections = async () => {
    try {
      const cols = await window.api.database.getAllCollections();
      setCollections(cols);
    } catch (error) {
      console.error('Failed to load collections:', error);
    }
  };

  const handleNodeToggle = (nodeId: string) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(nodeId)) {
        newSet.delete(nodeId);
      } else {
        newSet.add(nodeId);
      }
      return newSet;
    });
  };

  const handleNodeSelect = async (nodeId: string, nodeType: 'collection' | 'request') => {
    setSelectedNode(nodeId);
    
    if (nodeType === 'request' && onRequestSelect) {
      try {
        const request = await window.api.database.getRequest(nodeId);
        if (request) {
          onRequestSelect(request);
        }
      } catch (error) {
        console.error('Failed to load request:', error);
      }
    }
  };

  const handleContextMenu = (
    event: React.MouseEvent,
    nodeId: string,
    nodeType: 'collection' | 'request'
  ) => {
    event.preventDefault();
    event.stopPropagation();
    setContextMenu({
      mouseX: event.clientX - 2,
      mouseY: event.clientY - 4,
      nodeId,
      nodeType,
    });
  };

  const handleContextMenuClose = () => {
    setContextMenu(null);
  };

  // Collection CRUD
  const handleCreateCollection = () => {
    setCollectionForm({ name: '', description: '' });
    setCollectionDialog({ open: true, mode: 'create' });
    handleContextMenuClose();
  };

  const handleEditCollection = async (collectionId: string) => {
    try {
      const collection = await window.api.database.getCollection(collectionId);
      if (collection) {
        setCollectionForm({ name: collection.name, description: collection.description || '' });
        setCollectionDialog({ open: true, mode: 'edit', collection });
      }
    } catch (error) {
      console.error('Failed to load collection:', error);
    }
    handleContextMenuClose();
  };

  const handleDeleteCollection = (collectionId: string, name: string) => {
    setDeleteDialog({ open: true, type: 'collection', id: collectionId, name });
    handleContextMenuClose();
  };

  const handleSaveCollection = async () => {
    try {
      if (collectionDialog.mode === 'create') {
        await window.api.database.createCollection({
          name: collectionForm.name,
          description: collectionForm.description,
        });
      } else if (collectionDialog.collection) {
        await window.api.database.updateCollection(collectionDialog.collection.id, {
          name: collectionForm.name,
          description: collectionForm.description,
        });
      }
      await loadCollections();
      setCollectionDialog({ open: false, mode: 'create' });
    } catch (error) {
      console.error('Failed to save collection:', error);
    }
  };

  // Request CRUD
  const handleCreateRequest = (collectionId: string) => {
    setRequestForm({ name: '', method: 'GET', url: '' });
    setRequestDialog({ open: true, mode: 'create', collectionId });
    handleContextMenuClose();
  };

  const handleEditRequest = async (requestId: string) => {
    try {
      const request = await window.api.database.getRequest(requestId);
      if (request) {
        setRequestForm({ name: request.name, method: request.method, url: request.url });
        setRequestDialog({ open: true, mode: 'edit', request });
      }
    } catch (error) {
      console.error('Failed to load request:', error);
    }
    handleContextMenuClose();
  };

  const handleDeleteRequest = (requestId: string, name: string) => {
    setDeleteDialog({ open: true, type: 'request', id: requestId, name });
    handleContextMenuClose();
  };

  const handleDuplicateRequest = async (requestId: string) => {
    try {
      const request = await window.api.database.getRequest(requestId);
      if (request) {
        await window.api.database.createRequest({
          ...request,
          id: undefined,
          name: `${request.name} (Copy)`,
        });
        await loadCollections();
      }
    } catch (error) {
      console.error('Failed to duplicate request:', error);
    }
    handleContextMenuClose();
  };

  const handleSaveRequest = async () => {
    try {
      if (requestDialog.mode === 'create' && requestDialog.collectionId) {
        await window.api.database.createRequest({
          name: requestForm.name,
          method: requestForm.method as any,
          url: requestForm.url,
          collectionId: requestDialog.collectionId,
          headers: [],
          queryParams: [],
          body: { type: 'none', content: '' },
          auth: { type: 'none' },
        });
      } else if (requestDialog.request) {
        await window.api.database.updateRequest(requestDialog.request.id, {
          name: requestForm.name,
          method: requestForm.method as any,
          url: requestForm.url,
        });
      }
      await loadCollections();
      setRequestDialog({ open: false, mode: 'create' });
    } catch (error) {
      console.error('Failed to save request:', error);
    }
  };

  const handleConfirmDelete = async () => {
    if (!deleteDialog) return;

    try {
      if (deleteDialog.type === 'collection') {
        await window.api.database.deleteCollection(deleteDialog.id);
      } else {
        await window.api.database.deleteRequest(deleteDialog.id);
      }
      await loadCollections();
      setDeleteDialog(null);
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  const renderTreeNode = (collection: Collection) => {
    const isExpanded = expandedNodes.has(collection.id);
    const isSelected = selectedNode === collection.id;

    return (
      <Box key={collection.id}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            padding: '6px 8px',
            cursor: 'pointer',
            backgroundColor: isSelected ? 'action.selected' : 'transparent',
            '&:hover': {
              backgroundColor: 'action.hover',
            },
            borderRadius: 1,
          }}
          onClick={() => handleNodeSelect(collection.id, 'collection')}
          onContextMenu={(e) => handleContextMenu(e, collection.id, 'collection')}
        >
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              handleNodeToggle(collection.id);
            }}
            sx={{ mr: 0.5 }}
          >
            {isExpanded ? <FolderOpenIcon fontSize="small" /> : <FolderIcon fontSize="small" />}
          </IconButton>
          <Typography variant="body2" sx={{ flexGrow: 1 }}>
            {collection.name}
          </Typography>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              handleCreateRequest(collection.id);
            }}
          >
            <AddIcon fontSize="small" />
          </IconButton>
        </Box>

        {isExpanded && collection.requests && (
          <Box sx={{ ml: 3 }}>
            {collection.requests.map((request) => {
              const isRequestSelected = selectedNode === request.id;
              return (
                <Box
                  key={request.id}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '6px 8px',
                    cursor: 'pointer',
                    backgroundColor: isRequestSelected ? 'action.selected' : 'transparent',
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                    borderRadius: 1,
                  }}
                  onClick={() => handleNodeSelect(request.id, 'request')}
                  onContextMenu={(e) => handleContextMenu(e, request.id, 'request')}
                >
                  <RequestIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 600,
                      mr: 1,
                      color: `method-${request.method.toLowerCase()}`,
                    }}
                  >
                    {request.method}
                  </Typography>
                  <Typography variant="body2" sx={{ flexGrow: 1 }}>
                    {request.name}
                  </Typography>
                </Box>
              );
            })}
          </Box>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">Collections</Typography>
          <Tooltip title="New Collection">
            <IconButton size="small" onClick={handleCreateCollection}>
              <AddIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Tree */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 1 }}>
        {collections.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              No collections yet
            </Typography>
            <Button
              startIcon={<AddIcon />}
              onClick={handleCreateCollection}
              sx={{ mt: 2 }}
            >
              Create Collection
            </Button>
          </Box>
        ) : (
          collections.map(renderTreeNode)
        )}
      </Box>

      {/* Context Menu */}
      <Menu
        open={contextMenu !== null}
        onClose={handleContextMenuClose}
        anchorReference="anchorPosition"
        anchorPosition={
          contextMenu !== null
            ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
            : undefined
        }
      >
        {contextMenu && contextMenu.nodeType === 'collection' ? (
          [
            <MenuItem key="add" onClick={() => handleCreateRequest(contextMenu.nodeId)}>
              <ListItemIcon><AddIcon fontSize="small" /></ListItemIcon>
              <ListItemText>Add Request</ListItemText>
            </MenuItem>,
            <MenuItem key="edit" onClick={() => handleEditCollection(contextMenu.nodeId)}>
              <ListItemIcon><EditIcon fontSize="small" /></ListItemIcon>
              <ListItemText>Edit Collection</ListItemText>
            </MenuItem>,
            <MenuItem key="delete" onClick={() => {
              const col = collections.find(c => c.id === contextMenu.nodeId);
              if (col) handleDeleteCollection(contextMenu.nodeId, col.name);
            }}>
              <ListItemIcon><DeleteIcon fontSize="small" /></ListItemIcon>
              <ListItemText>Delete Collection</ListItemText>
            </MenuItem>,
          ]
        ) : contextMenu ? (
          [
            <MenuItem key="edit" onClick={() => handleEditRequest(contextMenu.nodeId)}>
              <ListItemIcon><EditIcon fontSize="small" /></ListItemIcon>
              <ListItemText>Edit Request</ListItemText>
            </MenuItem>,
            <MenuItem key="duplicate" onClick={() => handleDuplicateRequest(contextMenu.nodeId)}>
              <ListItemIcon><DuplicateIcon fontSize="small" /></ListItemIcon>
              <ListItemText>Duplicate Request</ListItemText>
            </MenuItem>,
            <MenuItem key="delete" onClick={() => {
              collections.forEach(col => {
                const req = col.requests?.find(r => r.id === contextMenu.nodeId);
                if (req) handleDeleteRequest(contextMenu.nodeId, req.name);
              });
            }}>
              <ListItemIcon><DeleteIcon fontSize="small" /></ListItemIcon>
              <ListItemText>Delete Request</ListItemText>
            </MenuItem>,
          ]
        ) : null}
      </Menu>

      {/* Collection Dialog */}
      <Dialog
        open={collectionDialog.open}
        onClose={() => setCollectionDialog({ open: false, mode: 'create' })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {collectionDialog.mode === 'create' ? 'Create Collection' : 'Edit Collection'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={collectionForm.name}
            onChange={(e) => setCollectionForm({ ...collectionForm, name: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={collectionForm.description}
            onChange={(e) => setCollectionForm({ ...collectionForm, description: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCollectionDialog({ open: false, mode: 'create' })}>
            Cancel
          </Button>
          <Button onClick={handleSaveCollection} variant="contained">
            {collectionDialog.mode === 'create' ? 'Create' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Request Dialog */}
      <Dialog
        open={requestDialog.open}
        onClose={() => setRequestDialog({ open: false, mode: 'create' })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {requestDialog.mode === 'create' ? 'Create Request' : 'Edit Request'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={requestForm.name}
            onChange={(e) => setRequestForm({ ...requestForm, name: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Method"
            select
            fullWidth
            value={requestForm.method}
            onChange={(e) => setRequestForm({ ...requestForm, method: e.target.value })}
            SelectProps={{ native: true }}
          >
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="PATCH">PATCH</option>
            <option value="DELETE">DELETE</option>
            <option value="HEAD">HEAD</option>
            <option value="OPTIONS">OPTIONS</option>
          </TextField>
          <TextField
            margin="dense"
            label="URL"
            fullWidth
            value={requestForm.url}
            onChange={(e) => setRequestForm({ ...requestForm, url: e.target.value })}
            placeholder="https://api.example.com/endpoint"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRequestDialog({ open: false, mode: 'create' })}>
            Cancel
          </Button>
          <Button onClick={handleSaveRequest} variant="contained">
            {requestDialog.mode === 'create' ? 'Create' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog !== null}
        onClose={() => setDeleteDialog(null)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete {deleteDialog?.type} "{deleteDialog?.name}"?
            {deleteDialog?.type === 'collection' && (
              <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                This will also delete all requests in this collection.
              </Typography>
            )}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(null)}>Cancel</Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CollectionsTree;
