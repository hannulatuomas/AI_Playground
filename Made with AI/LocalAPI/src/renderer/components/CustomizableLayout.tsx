/**
 * CustomizableLayout - Drag-and-Drop Panel Layout System
 * 
 * Features:
 * - Drag panels to reposition
 * - Resize panels
 * - Show/hide panels
 * - Save layout configurations
 * - Layout presets
 * - Floating panels support
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  TextField,
  Tooltip,
  Divider,
  Chip,
} from '@mui/material';
import DashboardCustomizeIcon from '@mui/icons-material/DashboardCustomize';
import SaveIcon from '@mui/icons-material/Save';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import AddIcon from '@mui/icons-material/Add';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';

interface PanelConfig {
  id: string;
  type: string;
  visible: boolean;
  position: {
    area: 'left' | 'center' | 'right' | 'top' | 'bottom';
    order: number;
  };
  size: {
    width?: number;
    height?: number;
    minWidth?: number;
    minHeight?: number;
  };
  docked: boolean;
  content?: React.ReactNode;
}

interface LayoutConfig {
  id: string;
  name: string;
  description?: string;
  panels: PanelConfig[];
}

interface CustomizableLayoutProps {
  children?: React.ReactNode;
  onLayoutChange?: (layout: LayoutConfig) => void;
}

export const CustomizableLayout: React.FC<CustomizableLayoutProps> = ({ children, onLayoutChange }) => {
  const [panels, setPanels] = useState<PanelConfig[]>([]);
  const [layouts, setLayouts] = useState<LayoutConfig[]>([]);
  const [currentLayoutId, setCurrentLayoutId] = useState<string | null>(null);
  const [layoutMenuAnchor, setLayoutMenuAnchor] = useState<null | HTMLElement>(null);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [layoutsDialogOpen, setLayoutsDialogOpen] = useState(false);
  const [panelMenuAnchor, setPanelMenuAnchor] = useState<null | HTMLElement>(null);
  const [newLayoutName, setNewLayoutName] = useState('');
  const [draggedPanel, setDraggedPanel] = useState<string | null>(null);
  const [resizingPanel, setResizingPanel] = useState<{
    panelId: string;
    startX: number;
    startY: number;
    startWidth: number;
    startHeight: number;
  } | null>(null);

  useEffect(() => {
    loadLayouts();
  }, []);

  const loadLayouts = async () => {
    try {
      // Would call: const layouts = await window.electronAPI.layouts.getAll();
      // For now, create demo layouts
      const demoLayouts: LayoutConfig[] = [
        {
          id: 'ide-style',
          name: 'IDE Style',
          description: 'Classic IDE layout',
          panels: [
            {
              id: 'sidebar',
              type: 'sidebar',
              visible: true,
              position: { area: 'left', order: 0 },
              size: { width: 20, minWidth: 200 },
              docked: true,
            },
            {
              id: 'main',
              type: 'main',
              visible: true,
              position: { area: 'center', order: 0 },
              size: { width: 60 },
              docked: true,
            },
            {
              id: 'properties',
              type: 'properties',
              visible: true,
              position: { area: 'right', order: 0 },
              size: { width: 20, minWidth: 200 },
              docked: true,
            },
          ],
        },
      ];
      setLayouts(demoLayouts);
      
      if (demoLayouts.length > 0) {
        applyLayout(demoLayouts[0]);
      }
    } catch (error) {
      console.error('Error loading layouts:', error);
    }
  };

  const applyLayout = (layout: LayoutConfig) => {
    setPanels(layout.panels);
    setCurrentLayoutId(layout.id);
    onLayoutChange?.(layout);
  };

  const handleSaveLayout = async () => {
    if (!newLayoutName.trim()) return;

    const newLayout: LayoutConfig = {
      id: `layout-${Date.now()}`,
      name: newLayoutName,
      panels: panels,
    };

    try {
      // Would call: await window.electronAPI.layouts.create(newLayout);
      setLayouts(prev => [...prev, newLayout]);
      setSaveDialogOpen(false);
      setNewLayoutName('');
    } catch (error) {
      console.error('Error saving layout:', error);
    }
  };

  const togglePanelVisibility = (panelId: string) => {
    setPanels(prev =>
      prev.map(p => (p.id === panelId ? { ...p, visible: !p.visible } : p))
    );
  };

  const handleDragStart = (e: React.DragEvent, panelId: string) => {
    setDraggedPanel(panelId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, targetArea: PanelConfig['position']['area']) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e: React.DragEvent, targetArea: PanelConfig['position']['area']) => {
    e.preventDefault();
    
    if (!draggedPanel) return;

    setPanels(prev =>
      prev.map(p =>
        p.id === draggedPanel
          ? { ...p, position: { ...p.position, area: targetArea } }
          : p
      )
    );

    setDraggedPanel(null);
  };

  const handleResizeStart = (e: React.MouseEvent, panelId: string, currentWidth: number, currentHeight: number) => {
    e.preventDefault();
    setResizingPanel({
      panelId,
      startX: e.clientX,
      startY: e.clientY,
      startWidth: currentWidth,
      startHeight: currentHeight,
    });
  };

  const handleResizeMove = (e: MouseEvent) => {
    if (!resizingPanel) return;

    const deltaX = e.clientX - resizingPanel.startX;
    const deltaY = e.clientY - resizingPanel.startY;

    setPanels(prev =>
      prev.map(p => {
        if (p.id === resizingPanel.panelId) {
          const newWidth = Math.max(p.size.minWidth || 100, resizingPanel.startWidth + deltaX);
          const newHeight = Math.max(p.size.minHeight || 100, resizingPanel.startHeight + deltaY);

          return {
            ...p,
            size: {
              ...p.size,
              width: newWidth,
              height: newHeight,
            },
          };
        }
        return p;
      })
    );
  };

  const handleResizeEnd = () => {
    setResizingPanel(null);
  };

  useEffect(() => {
    if (resizingPanel) {
      window.addEventListener('mousemove', handleResizeMove);
      window.addEventListener('mouseup', handleResizeEnd);
      return () => {
        window.removeEventListener('mousemove', handleResizeMove);
        window.removeEventListener('mouseup', handleResizeEnd);
      };
    }
  }, [resizingPanel]);

  const renderPanel = (panel: PanelConfig) => {
    if (!panel.visible) return null;

    return (
      <Box
        key={panel.id}
        draggable
        onDragStart={(e) => handleDragStart(e, panel.id)}
        sx={{
          width: panel.size.width ? `${panel.size.width}%` : 'auto',
          height: panel.size.height ? `${panel.size.height}px` : 'auto',
          minWidth: panel.size.minWidth,
          minHeight: panel.size.minHeight,
          border: 1,
          borderColor: 'divider',
          backgroundColor: 'background.paper',
          position: 'relative',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* Panel Header */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            p: 0.5,
            backgroundColor: 'action.hover',
            borderBottom: 1,
            borderColor: 'divider',
            cursor: 'move',
          }}
        >
          <DragIndicatorIcon fontSize="small" />
          <Box sx={{ flex: 1, fontSize: '0.875rem', fontWeight: 600 }}>
            {panel.type.charAt(0).toUpperCase() + panel.type.slice(1)}
          </Box>
          <IconButton size="small" onClick={() => togglePanelVisibility(panel.id)}>
            <VisibilityOffIcon fontSize="small" />
          </IconButton>
        </Box>

        {/* Panel Content */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {panel.content || `${panel.type} panel content`}
        </Box>

        {/* Resize Handle */}
        <Box
          onMouseDown={(e) => handleResizeStart(e, panel.id, panel.size.width || 0, panel.size.height || 0)}
          sx={{
            position: 'absolute',
            right: 0,
            bottom: 0,
            width: 10,
            height: 10,
            cursor: 'nwse-resize',
            backgroundColor: 'primary.main',
            opacity: 0.3,
            '&:hover': {
              opacity: 1,
            },
          }}
        />
      </Box>
    );
  };

  const getPanelsByArea = (area: PanelConfig['position']['area']) => {
    return panels
      .filter(p => p.position.area === area)
      .sort((a, b) => a.position.order - b.position.order);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Toolbar */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          p: 1,
          backgroundColor: 'background.paper',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Tooltip title="Customize Layout">
          <IconButton size="small" onClick={(e) => setLayoutMenuAnchor(e.currentTarget)}>
            <DashboardCustomizeIcon />
          </IconButton>
        </Tooltip>

        {currentLayoutId && (
          <Chip
            label={layouts.find(l => l.id === currentLayoutId)?.name || 'Custom'}
            size="small"
            variant="outlined"
          />
        )}

        <Box sx={{ flex: 1 }} />

        <Tooltip title="Save Layout">
          <IconButton size="small" onClick={() => setSaveDialogOpen(true)}>
            <SaveIcon />
          </IconButton>
        </Tooltip>

        <Tooltip title="Load Layout">
          <IconButton size="small" onClick={() => setLayoutsDialogOpen(true)}>
            <FolderOpenIcon />
          </IconButton>
        </Tooltip>

        <Tooltip title="Panel Visibility">
          <IconButton size="small" onClick={(e) => setPanelMenuAnchor(e.currentTarget)}>
            <VisibilityIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Layout Areas */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Top Area */}
        {getPanelsByArea('top').length > 0 && (
          <Box
            onDragOver={(e) => handleDragOver(e, 'top')}
            onDrop={(e) => handleDrop(e, 'top')}
            sx={{ display: 'flex', gap: 1, p: 1, borderBottom: 1, borderColor: 'divider' }}
          >
            {getPanelsByArea('top').map(renderPanel)}
          </Box>
        )}

        {/* Middle Area */}
        <Box sx={{ flex: 1, display: 'flex', gap: 1, p: 1, overflow: 'hidden' }}>
          {/* Left Area */}
          {getPanelsByArea('left').length > 0 && (
            <Box
              onDragOver={(e) => handleDragOver(e, 'left')}
              onDrop={(e) => handleDrop(e, 'left')}
              sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}
            >
              {getPanelsByArea('left').map(renderPanel)}
            </Box>
          )}

          {/* Center Area */}
          <Box
            onDragOver={(e) => handleDragOver(e, 'center')}
            onDrop={(e) => handleDrop(e, 'center')}
            sx={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 1, overflow: 'hidden' }}
          >
            {getPanelsByArea('center').map(renderPanel)}
            {children}
          </Box>

          {/* Right Area */}
          {getPanelsByArea('right').length > 0 && (
            <Box
              onDragOver={(e) => handleDragOver(e, 'right')}
              onDrop={(e) => handleDrop(e, 'right')}
              sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}
            >
              {getPanelsByArea('right').map(renderPanel)}
            </Box>
          )}
        </Box>

        {/* Bottom Area */}
        {getPanelsByArea('bottom').length > 0 && (
          <Box
            onDragOver={(e) => handleDragOver(e, 'bottom')}
            onDrop={(e) => handleDrop(e, 'bottom')}
            sx={{ display: 'flex', gap: 1, p: 1, borderTop: 1, borderColor: 'divider' }}
          >
            {getPanelsByArea('bottom').map(renderPanel)}
          </Box>
        )}
      </Box>

      {/* Layout Menu */}
      <Menu
        anchorEl={layoutMenuAnchor}
        open={Boolean(layoutMenuAnchor)}
        onClose={() => setLayoutMenuAnchor(null)}
      >
        <MenuItem onClick={() => setLayoutsDialogOpen(true)}>Load Layout</MenuItem>
        <MenuItem onClick={() => setSaveDialogOpen(true)}>Save Layout</MenuItem>
        <Divider />
        <MenuItem onClick={() => setPanelMenuAnchor(layoutMenuAnchor)}>Panel Visibility</MenuItem>
      </Menu>

      {/* Panel Visibility Menu */}
      <Menu
        anchorEl={panelMenuAnchor}
        open={Boolean(panelMenuAnchor)}
        onClose={() => setPanelMenuAnchor(null)}
      >
        {panels.map(panel => (
          <MenuItem key={panel.id} onClick={() => togglePanelVisibility(panel.id)}>
            {panel.visible ? <VisibilityIcon fontSize="small" sx={{ mr: 1 }} /> : <VisibilityOffIcon fontSize="small" sx={{ mr: 1 }} />}
            {panel.type}
          </MenuItem>
        ))}
      </Menu>

      {/* Save Layout Dialog */}
      <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)}>
        <DialogTitle>Save Layout</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Layout Name"
            value={newLayoutName}
            onChange={(e) => setNewLayoutName(e.target.value)}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveLayout} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Layouts Dialog */}
      <Dialog open={layoutsDialogOpen} onClose={() => setLayoutsDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Load Layout</DialogTitle>
        <DialogContent>
          <List>
            {layouts.map(layout => (
              <ListItem key={layout.id} disablePadding>
                <ListItemButton
                  onClick={() => {
                    applyLayout(layout);
                    setLayoutsDialogOpen(false);
                  }}
                  selected={layout.id === currentLayoutId}
                >
                  <ListItemText
                    primary={layout.name}
                    secondary={layout.description}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLayoutsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
