/**
 * FavoritesPanel - Favorites/Bookmarks Management UI
 * 
 * Features:
 * - Favorites list with folders
 * - Drag-and-drop organization
 * - Quick access
 * - Search favorites
 * - Tag filtering
 * - Add/remove favorites
 * - Folder management
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Typography,
  TextField,
  InputAdornment,
  Collapse,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Chip,
  Tooltip,
  Divider,
} from '@mui/material';
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import FolderIcon from '@mui/icons-material/Folder';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import SearchIcon from '@mui/icons-material/Search';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import AddIcon from '@mui/icons-material/Add';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import LabelIcon from '@mui/icons-material/Label';

interface Favorite {
  id: string;
  type: string;
  entityId: string;
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  tags: string[];
  folder?: string;
  order: number;
  createdAt: number;
  lastAccessedAt: number;
}

interface FavoriteFolder {
  id: string;
  name: string;
  color?: string;
  order: number;
  collapsed?: boolean;
}

interface FavoritesPanelProps {
  onFavoriteClick?: (favorite: Favorite) => void;
}

export const FavoritesPanel: React.FC<FavoritesPanelProps> = ({ onFavoriteClick }) => {
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [folders, setFolders] = useState<FavoriteFolder[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredFavorites, setFilteredFavorites] = useState<Favorite[]>([]);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [allTags, setAllTags] = useState<string[]>([]);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [contextMenu, setContextMenu] = useState<{
    mouseX: number;
    mouseY: number;
    favoriteId?: string;
    folderId?: string;
  } | null>(null);
  const [newFolderDialogOpen, setNewFolderDialogOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [newFolderColor, setNewFolderColor] = useState('#4CAF50');

  useEffect(() => {
    loadFavorites();
    loadFolders();
  }, []);

  useEffect(() => {
    filterFavorites();
  }, [favorites, searchQuery, selectedTag]);

  const loadFavorites = async () => {
    try {
      const allFavorites = await window.electronAPI.favorites.getAll();
      setFavorites(allFavorites || []);
      
      // Extract all unique tags
      const tags = new Set<string>();
      allFavorites?.forEach((fav: Favorite) => {
        fav.tags?.forEach((tag: string) => tags.add(tag));
      });
      setAllTags(Array.from(tags).sort());
    } catch (error) {
      console.error('Error loading favorites:', error);
    }
  };

  const loadFolders = async () => {
    try {
      const allFolders = await window.electronAPI.favorites.getAllFolders();
      setFolders(allFolders || []);
      
      // Expand all folders by default
      const expanded = new Set(allFolders?.map((f: FavoriteFolder) => f.id) || []);
      setExpandedFolders(expanded);
    } catch (error) {
      console.error('Error loading folders:', error);
    }
  };

  const filterFavorites = () => {
    let filtered = [...favorites];

    // Filter by search query
    if (searchQuery.trim()) {
      const lowerQuery = searchQuery.toLowerCase();
      filtered = filtered.filter(fav =>
        fav.name.toLowerCase().includes(lowerQuery) ||
        fav.description?.toLowerCase().includes(lowerQuery) ||
        fav.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
      );
    }

    // Filter by tag
    if (selectedTag) {
      filtered = filtered.filter(fav => fav.tags.includes(selectedTag));
    }

    setFilteredFavorites(filtered);
  };

  const handleFavoriteClick = async (favorite: Favorite) => {
    try {
      // Update last accessed time
      await window.electronAPI.favorites.add({
        ...favorite,
        lastAccessedAt: Date.now(),
      });
      onFavoriteClick?.(favorite);
    } catch (error) {
      console.error('Error accessing favorite:', error);
    }
  };

  const handleRemoveFavorite = async (favoriteId: string) => {
    try {
      await window.electronAPI.favorites.remove(favoriteId);
      await loadFavorites();
    } catch (error) {
      console.error('Error removing favorite:', error);
    }
    handleContextMenuClose();
  };

  const handleContextMenu = (e: React.MouseEvent, favoriteId?: string, folderId?: string) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenu({
      mouseX: e.clientX - 2,
      mouseY: e.clientY - 4,
      favoriteId,
      folderId,
    });
  };

  const handleContextMenuClose = () => {
    setContextMenu(null);
  };

  const toggleFolder = (folderId: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderId)) {
      newExpanded.delete(folderId);
    } else {
      newExpanded.add(folderId);
    }
    setExpandedFolders(newExpanded);
  };

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) return;

    try {
      await window.electronAPI.favorites.createFolder(newFolderName, newFolderColor);
      await loadFolders();
      setNewFolderDialogOpen(false);
      setNewFolderName('');
      setNewFolderColor('#4CAF50');
    } catch (error) {
      console.error('Error creating folder:', error);
    }
  };

  const getTypeIcon = (type: string): string => {
    const icons: Record<string, string> = {
      request: '📡',
      collection: '📁',
      environment: '🌍',
      variable: '🔤',
      folder: '📂',
      other: '⭐',
    };
    return icons[type] || icons.other;
  };

  const getFavoritesByFolder = (folderId?: string) => {
    return filteredFavorites.filter(fav => fav.folder === folderId);
  };

  const renderFavorite = (favorite: Favorite, inFolder: boolean = false) => {
    return (
      <ListItem
        key={favorite.id}
        disablePadding
        sx={{ pl: inFolder ? 4 : 0 }}
        onContextMenu={(e) => handleContextMenu(e, favorite.id)}
      >
        <ListItemButton onClick={() => handleFavoriteClick(favorite)}>
          <ListItemIcon sx={{ minWidth: 40 }}>
            <span style={{ fontSize: '1.2rem' }}>{getTypeIcon(favorite.type)}</span>
          </ListItemIcon>
          <ListItemText
            primary={favorite.name}
            secondary={
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                {favorite.tags.map(tag => (
                  <Chip
                    key={tag}
                    label={tag}
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedTag(tag);
                    }}
                    sx={{ height: 18, fontSize: '0.7rem' }}
                  />
                ))}
              </Box>
            }
          />
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              handleRemoveFavorite(favorite.id);
            }}
          >
            <StarIcon sx={{ color: 'warning.main' }} fontSize="small" />
          </IconButton>
        </ListItemButton>
      </ListItem>
    );
  };

  const renderFolder = (folder: FavoriteFolder) => {
    const isExpanded = expandedFolders.has(folder.id);
    const folderFavorites = getFavoritesByFolder(folder.id);

    return (
      <Box key={folder.id}>
        <ListItem
          disablePadding
          onContextMenu={(e) => handleContextMenu(e, undefined, folder.id)}
        >
          <ListItemButton onClick={() => toggleFolder(folder.id)}>
            <ListItemIcon sx={{ minWidth: 40 }}>
              {isExpanded ? (
                <FolderOpenIcon sx={{ color: folder.color }} />
              ) : (
                <FolderIcon sx={{ color: folder.color }} />
              )}
            </ListItemIcon>
            <ListItemText primary={folder.name} />
            <Typography variant="caption" color="textSecondary" sx={{ mr: 1 }}>
              {folderFavorites.length}
            </Typography>
            {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </ListItemButton>
        </ListItem>
        <Collapse in={isExpanded} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {folderFavorites.map(fav => renderFavorite(fav, true))}
          </List>
        </Collapse>
      </Box>
    );
  };

  const ungroupedFavorites = getFavoritesByFolder(undefined);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            <StarIcon sx={{ color: 'warning.main', verticalAlign: 'middle', mr: 1 }} />
            Favorites
          </Typography>
          <Tooltip title="New Folder">
            <IconButton size="small" onClick={() => setNewFolderDialogOpen(true)}>
              <AddIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Search */}
        <TextField
          fullWidth
          size="small"
          placeholder="Search favorites..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
        />

        {/* Tags filter */}
        {allTags.length > 0 && (
          <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            <Chip
              label="All"
              size="small"
              color={selectedTag === null ? 'primary' : 'default'}
              onClick={() => setSelectedTag(null)}
            />
            {allTags.map(tag => (
              <Chip
                key={tag}
                label={tag}
                size="small"
                icon={<LabelIcon />}
                color={selectedTag === tag ? 'primary' : 'default'}
                onClick={() => setSelectedTag(tag === selectedTag ? null : tag)}
              />
            ))}
          </Box>
        )}
      </Box>

      {/* Favorites list */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {filteredFavorites.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <StarBorderIcon sx={{ fontSize: 48, color: 'text.secondary', opacity: 0.5 }} />
            <Typography color="textSecondary" sx={{ mt: 1 }}>
              {searchQuery || selectedTag ? 'No favorites match your filter' : 'No favorites yet'}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              {!searchQuery && !selectedTag && 'Click the star icon on any item to add it to favorites'}
            </Typography>
          </Box>
        ) : (
          <List>
            {/* Folders */}
            {folders.map(folder => renderFolder(folder))}

            {/* Divider between folders and ungrouped */}
            {folders.length > 0 && ungroupedFavorites.length > 0 && <Divider sx={{ my: 1 }} />}

            {/* Ungrouped favorites */}
            {ungroupedFavorites.map(fav => renderFavorite(fav))}
          </List>
        )}
      </Box>

      {/* Context menu */}
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
        {contextMenu?.favoriteId && (
          <MenuItem onClick={() => handleRemoveFavorite(contextMenu.favoriteId!)}>
            <ListItemIcon>
              <DeleteIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Remove from Favorites</ListItemText>
          </MenuItem>
        )}
        {contextMenu?.folderId && (
          <>
            <MenuItem onClick={handleContextMenuClose}>
              <ListItemIcon>
                <EditIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Rename Folder</ListItemText>
            </MenuItem>
            <MenuItem onClick={handleContextMenuClose}>
              <ListItemIcon>
                <DeleteIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Delete Folder</ListItemText>
            </MenuItem>
          </>
        )}
      </Menu>

      {/* New folder dialog */}
      <Dialog open={newFolderDialogOpen} onClose={() => setNewFolderDialogOpen(false)}>
        <DialogTitle>Create New Folder</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Folder Name"
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
            sx={{ mt: 1 }}
          />
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption" gutterBottom>
              Folder Color
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              {['#4CAF50', '#2196F3', '#FFC107', '#FF5722', '#9C27B0', '#607D8B'].map(color => (
                <Box
                  key={color}
                  onClick={() => setNewFolderColor(color)}
                  sx={{
                    width: 32,
                    height: 32,
                    backgroundColor: color,
                    borderRadius: 1,
                    cursor: 'pointer',
                    border: newFolderColor === color ? '3px solid' : '1px solid',
                    borderColor: newFolderColor === color ? 'primary.main' : 'divider',
                  }}
                />
              ))}
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewFolderDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateFolder} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
