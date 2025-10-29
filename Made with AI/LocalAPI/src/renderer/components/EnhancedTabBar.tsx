/**
 * EnhancedTabBar - Advanced Tab Management UI
 * 
 * Features:
 * - Tab overflow with scrolling
 * - Tab groups with visual indicators
 * - Drag-and-drop reordering
 * - Context menu
 * - Sticky tabs
 * - Tab search
 * - Color coding by type
 * - Back/forward navigation
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  IconButton,
  Menu,
  MenuItem,
  TextField,
  InputAdornment,
  Chip,
  Tooltip,
  Typography,
  Divider,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import SearchIcon from '@mui/icons-material/Search';
import KeyboardArrowLeftIcon from '@mui/icons-material/KeyboardArrowLeft';
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import PushPinIcon from '@mui/icons-material/PushPin';
import AddIcon from '@mui/icons-material/Add';
import FolderIcon from '@mui/icons-material/Folder';
import CloseAllIcon from '@mui/icons-material/ClearAll';
import EditIcon from '@mui/icons-material/Edit';

interface Tab {
  id: string;
  title: string;
  type: string;
  icon?: string;
  color?: string;
  sticky?: boolean;
  groupId?: string;
  modified?: boolean;
  closable?: boolean;
}

interface TabGroup {
  id: string;
  name: string;
  color?: string;
  collapsed?: boolean;
}

interface EnhancedTabBarProps {
  onTabSelect?: (tabId: string) => void;
  onTabClose?: (tabId: string) => void;
  onNewTab?: () => void;
}

export const EnhancedTabBar: React.FC<EnhancedTabBarProps> = ({
  onTabSelect,
  onTabClose,
  onNewTab,
}) => {
  const [tabs, setTabs] = useState<Tab[]>([]);
  const [groups, setGroups] = useState<TabGroup[]>([]);
  const [activeTabId, setActiveTabId] = useState<string | null>(null);
  const [canGoBack, setCanGoBack] = useState(false);
  const [canGoForward, setCanGoForward] = useState(false);
  const [contextMenu, setContextMenu] = useState<{
    mouseX: number;
    mouseY: number;
    tabId: string;
  } | null>(null);
  const [overflowMenuAnchor, setOverflowMenuAnchor] = useState<null | HTMLElement>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Tab[]>([]);
  const [scrollPosition, setScrollPosition] = useState(0);
  const [showLeftScroll, setShowLeftScroll] = useState(false);
  const [showRightScroll, setShowRightScroll] = useState(false);
  const tabsContainerRef = useRef<HTMLDivElement>(null);
  const [draggedTabId, setDraggedTabId] = useState<string | null>(null);
  const [dropTargetIndex, setDropTargetIndex] = useState<number | null>(null);
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const [renameTabId, setRenameTabId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState('');

  // Load tabs and groups
  useEffect(() => {
    loadTabs();
    loadGroups();
    loadHistory();
    
    // Listen for tabs-updated event to reload tabs
    const handleTabsUpdated = () => {
      loadTabs();
      loadGroups();
    };
    
    window.addEventListener('tabs-updated', handleTabsUpdated);
    
    return () => {
      window.removeEventListener('tabs-updated', handleTabsUpdated);
    };
  }, []);

  // Check scroll state
  useEffect(() => {
    checkScrollButtons();
  }, [tabs, scrollPosition]);

  const loadTabs = async () => {
    try {
      const allTabs = await window.electronAPI.tabs.getAll();
      setTabs(allTabs || []);
      
      const active = await window.electronAPI.tabs.getActive();
      if (active) {
        setActiveTabId(active.id);
      }
    } catch (error) {
      console.error('Error loading tabs:', error);
    }
  };

  const loadGroups = async () => {
    try {
      const allGroups = await window.electronAPI.tabs.getAllGroups();
      setGroups(allGroups || []);
    } catch (error) {
      console.error('Error loading groups:', error);
    }
  };

  const loadHistory = async () => {
    try {
      const backResult = await window.electronAPI.tabs.goBack();
      setCanGoBack(backResult !== null);
      
      // Go back to restore state
      if (backResult) {
        await window.electronAPI.tabs.goForward();
      }

      const forwardResult = await window.electronAPI.tabs.goForward();
      setCanGoForward(forwardResult !== null);
      
      // Go forward to restore state
      if (forwardResult) {
        await window.electronAPI.tabs.goBack();
      }
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const handleTabSelect = async (tabId: string) => {
    try {
      await window.electronAPI.tabs.setActive(tabId);
      setActiveTabId(tabId);
      await loadHistory();
      onTabSelect?.(tabId);
    } catch (error) {
      console.error('Error selecting tab:', error);
    }
  };

  const handleTabClose = async (tabId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const success = await window.electronAPI.tabs.close(tabId);
      if (success) {
        await loadTabs();
        onTabClose?.(tabId);
      }
    } catch (error) {
      console.error('Error closing tab:', error);
    }
  };

  const handleContextMenu = (e: React.MouseEvent, tabId: string) => {
    e.preventDefault();
    setContextMenu({
      mouseX: e.clientX - 2,
      mouseY: e.clientY - 4,
      tabId,
    });
  };

  const handleContextMenuClose = () => {
    setContextMenu(null);
  };

  const handlePinTab = () => {
    // TODO: Implement pin functionality
    handleContextMenuClose();
  };
  
  const handleRenameTab = () => {
    if (!contextMenu) return;
    
    const tab = tabs.find(t => t.id === contextMenu.tabId);
    if (tab) {
      setRenameTabId(tab.id);
      setRenameValue(tab.title);
      setRenameDialogOpen(true);
    }
    handleContextMenuClose();
  };
  
  const handleRenameConfirm = async () => {
    if (!renameTabId || !renameValue.trim()) return;
    
    try {
      await window.electronAPI.tabs.update(renameTabId, { title: renameValue.trim() });
      await loadTabs();
      window.dispatchEvent(new Event('tabs-updated'));
    } catch (error) {
      console.error('Error renaming tab:', error);
    }
    
    setRenameDialogOpen(false);
    setRenameTabId(null);
    setRenameValue('');
  };

  const handleCloseOthers = async () => {
    if (!contextMenu) return;
    
    try {
      const allTabs = await window.electronAPI.tabs.getAll();
      for (const tab of allTabs) {
        if (tab.id !== contextMenu.tabId && tab.closable !== false) {
          await window.electronAPI.tabs.close(tab.id);
        }
      }
      await loadTabs();
    } catch (error) {
      console.error('Error closing other tabs:', error);
    }
    
    handleContextMenuClose();
  };

  const handleCloseAll = async () => {
    try {
      const allTabs = await window.electronAPI.tabs.getAll();
      for (const tab of allTabs) {
        if (tab.closable !== false) {
          await window.electronAPI.tabs.close(tab.id);
        }
      }
      await loadTabs();
    } catch (error) {
      console.error('Error closing all tabs:', error);
    }
    
    handleContextMenuClose();
    setOverflowMenuAnchor(null);
  };

  const handleGoBack = async () => {
    try {
      const tab = await window.electronAPI.tabs.goBack();
      if (tab) {
        setActiveTabId(tab.id);
        await loadTabs();
        await loadHistory();
        onTabSelect?.(tab.id);
      }
    } catch (error) {
      console.error('Error going back:', error);
    }
  };

  const handleGoForward = async () => {
    try {
      const tab = await window.electronAPI.tabs.goForward();
      if (tab) {
        setActiveTabId(tab.id);
        await loadTabs();
        await loadHistory();
        onTabSelect?.(tab.id);
      }
    } catch (error) {
      console.error('Error going forward:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const results = await window.electronAPI.tabs.search(searchQuery);
      setSearchResults(results.map((r: any) => r.tab));
    } catch (error) {
      console.error('Error searching tabs:', error);
    }
  };

  useEffect(() => {
    handleSearch();
  }, [searchQuery]);

  const scrollTabs = (direction: 'left' | 'right') => {
    if (tabsContainerRef.current) {
      const scrollAmount = 200;
      const newPosition = direction === 'left' 
        ? scrollPosition - scrollAmount 
        : scrollPosition + scrollAmount;
      
      tabsContainerRef.current.scrollLeft = newPosition;
      setScrollPosition(newPosition);
    }
  };

  const checkScrollButtons = () => {
    if (tabsContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = tabsContainerRef.current;
      setShowLeftScroll(scrollLeft > 0);
      setShowRightScroll(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  const handleDragStart = (e: React.DragEvent, tabId: string) => {
    setDraggedTabId(tabId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    setDropTargetIndex(index);
  };

  const handleDrop = async (e: React.DragEvent, targetIndex: number) => {
    e.preventDefault();
    if (draggedTabId) {
      try {
        await window.electronAPI.tabs.reorder(draggedTabId, targetIndex);
        await loadTabs();
      } catch (error) {
        console.error('Error reordering tab:', error);
      }
    }
    setDraggedTabId(null);
    setDropTargetIndex(null);
  };

  const handleDragEnd = () => {
    setDraggedTabId(null);
    setDropTargetIndex(null);
  };

  const getTabColor = (type: string): string => {
    const colors: Record<string, string> = {
      request: '#2196F3',
      graphql: '#E10098',
      websocket: '#FFA726',
      grpc: '#00BCD4',
      collection: '#4CAF50',
      environment: '#9C27B0',
      other: '#757575',
    };
    return colors[type] || colors.other;
  };

  const getTabIcon = (type: string): string => {
    const icons: Record<string, string> = {
      request: '📡',
      graphql: '⚡',
      websocket: '🔌',
      grpc: '⚙️',
      collection: '📁',
      environment: '🌍',
      other: '📄',
    };
    return icons[type] || icons.other;
  };

  const renderTab = (tab: Tab, index: number) => {
    const isActive = tab.id === activeTabId;
    const isDragging = tab.id === draggedTabId;
    const isDropTarget = index === dropTargetIndex;

    return (
      <Box
        key={tab.id}
        draggable
        onDragStart={(e) => handleDragStart(e, tab.id)}
        onDragOver={(e) => handleDragOver(e, index)}
        onDrop={(e) => handleDrop(e, index)}
        onDragEnd={handleDragEnd}
        onContextMenu={(e) => handleContextMenu(e, tab.id)}
        onClick={() => handleTabSelect(tab.id)}
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          px: 2,
          py: 1,
          minWidth: 120,
          maxWidth: 200,
          cursor: 'pointer',
          backgroundColor: isActive ? 'action.selected' : 'background.paper',
          borderBottom: isActive ? '2px solid' : '2px solid transparent',
          borderColor: tab.color || getTabColor(tab.type),
          opacity: isDragging ? 0.5 : 1,
          borderLeft: isDropTarget ? '3px solid' : 'none',
          borderLeftColor: 'primary.main',
          transition: 'all 0.2s ease',
          '&:hover': {
            backgroundColor: isActive ? 'action.selected' : 'action.hover',
          },
        }}
      >
        {tab.sticky && (
          <PushPinIcon sx={{ fontSize: 14, color: 'primary.main' }} />
        )}
        <span style={{ fontSize: '1.1rem' }}>{getTabIcon(tab.type)}</span>
        <Typography
          variant="body2"
          sx={{
            flex: 1,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            fontWeight: isActive ? 600 : 400,
          }}
        >
          {tab.title}
          {tab.modified && ' •'}
        </Typography>
        {tab.closable !== false && (
          <IconButton
            size="small"
            onClick={(e) => handleTabClose(tab.id, e)}
            sx={{
              p: 0.5,
              opacity: isActive ? 1 : 0.5,
              '&:hover': { opacity: 1 },
            }}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        )}
      </Box>
    );
  };

  const renderGroupHeader = (group: TabGroup) => {
    return (
      <Box
        key={`group-${group.id}`}
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          px: 2,
          py: 0.5,
          backgroundColor: 'action.hover',
          borderLeft: '3px solid',
          borderColor: group.color || 'primary.main',
        }}
      >
        <FolderIcon sx={{ fontSize: 16 }} />
        <Typography variant="caption" fontWeight="bold">
          {group.name}
        </Typography>
      </Box>
    );
  };

  const renderTabsWithGroups = () => {
    const ungroupedTabs = tabs.filter(t => !t.groupId);
    const groupedTabs = tabs.filter(t => t.groupId);

    const elements: React.ReactNode[] = [];

    // Render ungrouped tabs first
    ungroupedTabs.forEach((tab, index) => {
      elements.push(renderTab(tab, index));
    });

    // Render grouped tabs
    groups.forEach(group => {
      const groupTabs = groupedTabs.filter(t => t.groupId === group.id);
      if (groupTabs.length > 0 && !group.collapsed) {
        elements.push(renderGroupHeader(group));
        groupTabs.forEach((tab, index) => {
          elements.push(renderTab(tab, ungroupedTabs.length + index));
        });
      }
    });

    return elements;
  };

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', backgroundColor: 'background.paper' }}>
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        {/* Navigation buttons */}
        <Box sx={{ display: 'flex', gap: 0.5, px: 1 }}>
          <Tooltip title="Back">
            <span>
              <IconButton size="small" disabled={!canGoBack} onClick={handleGoBack}>
                <ArrowBackIcon fontSize="small" />
              </IconButton>
            </span>
          </Tooltip>
          <Tooltip title="Forward">
            <span>
              <IconButton size="small" disabled={!canGoForward} onClick={handleGoForward}>
                <ArrowForwardIcon fontSize="small" />
              </IconButton>
            </span>
          </Tooltip>
          <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
        </Box>

        {/* Scroll left button */}
        {showLeftScroll && (
          <IconButton size="small" onClick={() => scrollTabs('left')} sx={{ flexShrink: 0 }}>
            <KeyboardArrowLeftIcon />
          </IconButton>
        )}

        {/* Tabs container */}
        <Box
          ref={tabsContainerRef}
          onScroll={(e) => {
            setScrollPosition((e.target as HTMLDivElement).scrollLeft);
            checkScrollButtons();
          }}
          sx={{
            flex: 1,
            display: 'flex',
            overflowX: 'auto',
            overflowY: 'hidden',
            scrollBehavior: 'smooth',
            '&::-webkit-scrollbar': {
              display: 'none',
            },
          }}
        >
          {renderTabsWithGroups()}
        </Box>

        {/* Scroll right button */}
        {showRightScroll && (
          <IconButton size="small" onClick={() => scrollTabs('right')} sx={{ flexShrink: 0 }}>
            <KeyboardArrowRightIcon />
          </IconButton>
        )}

        {/* Tab actions */}
        <Box sx={{ display: 'flex', gap: 0.5, px: 1, flexShrink: 0 }}>
          <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
          <Tooltip title="Search tabs">
            <IconButton size="small" onClick={() => setSearchOpen(!searchOpen)}>
              <SearchIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="More">
            <IconButton 
              size="small" 
              onClick={(e) => setOverflowMenuAnchor(e.currentTarget)}
            >
              <MoreHorizIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="New tab">
            <IconButton size="small" onClick={onNewTab}>
              <AddIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Search panel */}
      {searchOpen && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Search tabs..."
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
          {searchResults.length > 0 && (
            <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {searchResults.map(tab => (
                <Chip
                  key={tab.id}
                  label={tab.title}
                  size="small"
                  onClick={() => {
                    handleTabSelect(tab.id);
                    setSearchOpen(false);
                    setSearchQuery('');
                  }}
                  onDelete={tab.closable !== false ? () => window.electronAPI.tabs.close(tab.id).then(loadTabs) : undefined}
                />
              ))}
            </Box>
          )}
        </Box>
      )}

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
        <MenuItem onClick={handleRenameTab}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Rename Tab</ListItemText>
        </MenuItem>
        <MenuItem onClick={handlePinTab}>
          <ListItemIcon>
            <PushPinIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Pin Tab</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleCloseOthers}>
          <ListItemIcon>
            <CloseIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Close Others</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleCloseAll}>
          <ListItemIcon>
            <CloseAllIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Close All</ListItemText>
        </MenuItem>
      </Menu>

      {/* Overflow menu */}
      <Menu
        anchorEl={overflowMenuAnchor}
        open={Boolean(overflowMenuAnchor)}
        onClose={() => setOverflowMenuAnchor(null)}
      >
        <MenuItem onClick={handleCloseAll}>
          <ListItemText>Close All Tabs</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => { loadTabs(); setOverflowMenuAnchor(null); }}>
          <ListItemText>Refresh Tabs</ListItemText>
        </MenuItem>
      </Menu>
      
      {/* Rename Dialog */}
      <Dialog open={renameDialogOpen} onClose={() => setRenameDialogOpen(false)}>
        <DialogTitle>Rename Tab</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Tab Name"
            type="text"
            fullWidth
            value={renameValue}
            onChange={(e) => setRenameValue(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleRenameConfirm();
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRenameDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleRenameConfirm} variant="contained">Rename</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
