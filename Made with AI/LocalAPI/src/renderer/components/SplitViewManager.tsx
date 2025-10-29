/**
 * SplitViewManager - Side-by-Side Tab Comparison
 * 
 * Features:
 * - Horizontal/vertical split
 * - Drag to resize splits
 * - Drag tabs between splits
 * - Close splits
 * - Multiple splits (2-4 panels)
 * - Sync scrolling option
 */

import React, { useState, useRef } from 'react';
import {
  Box,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Divider as MuiDivider,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import SwapVertIcon from '@mui/icons-material/SwapVert';
import AddIcon from '@mui/icons-material/Add';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import SyncIcon from '@mui/icons-material/Sync';
import SyncDisabledIcon from '@mui/icons-material/SyncDisabled';

interface SplitPanel {
  id: string;
  content: React.ReactNode;
  title?: string;
  size: number; // Percentage (0-100)
}

interface SplitViewManagerProps {
  initialContent?: React.ReactNode;
  onPanelChange?: (panels: SplitPanel[]) => void;
}

export const SplitViewManager: React.FC<SplitViewManagerProps> = ({
  initialContent,
  onPanelChange,
}) => {
  const [panels, setPanels] = useState<SplitPanel[]>([
    { id: 'panel-1', content: initialContent, size: 100 },
  ]);
  const [orientation, setOrientation] = useState<'horizontal' | 'vertical'>('horizontal');
  const [syncScrolling, setSyncScrolling] = useState(false);
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [resizing, setResizing] = useState<{ panelIndex: number; startPos: number; startSize: number } | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const generatePanelId = () => `panel-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  const addSplit = () => {
    if (panels.length >= 4) {
      alert('Maximum 4 splits supported');
      return;
    }

    const newSize = 100 / (panels.length + 1);
    const updatedPanels = panels.map(p => ({ ...p, size: newSize }));
    updatedPanels.push({ id: generatePanelId(), content: null, size: newSize });

    setPanels(updatedPanels);
    onPanelChange?.(updatedPanels);
  };

  const removeSplit = (panelId: string) => {
    if (panels.length === 1) return;

    const updatedPanels = panels.filter(p => p.id !== panelId);
    const newSize = 100 / updatedPanels.length;
    updatedPanels.forEach(p => (p.size = newSize));

    setPanels(updatedPanels);
    onPanelChange?.(updatedPanels);
  };

  const toggleOrientation = () => {
    setOrientation(prev => (prev === 'horizontal' ? 'vertical' : 'horizontal'));
  };

  const handleResizeStart = (panelIndex: number, event: React.MouseEvent) => {
    event.preventDefault();
    const startPos = orientation === 'horizontal' ? event.clientX : event.clientY;
    setResizing({ panelIndex, startPos, startSize: panels[panelIndex].size });
  };

  const handleResizeMove = (event: MouseEvent) => {
    if (!resizing || !containerRef.current) return;

    const containerRect = containerRef.current.getBoundingClientRect();
    const containerSize = orientation === 'horizontal' ? containerRect.width : containerRect.height;
    const currentPos = orientation === 'horizontal' ? event.clientX : event.clientY;
    const containerStart = orientation === 'horizontal' ? containerRect.left : containerRect.top;

    const delta = ((currentPos - resizing.startPos) / containerSize) * 100;
    const newSize = Math.max(10, Math.min(90, resizing.startSize + delta));

    const updatedPanels = [...panels];
    const nextPanelIndex = resizing.panelIndex + 1;

    if (nextPanelIndex < panels.length) {
      const sizeDiff = newSize - updatedPanels[resizing.panelIndex].size;
      updatedPanels[resizing.panelIndex].size = newSize;
      updatedPanels[nextPanelIndex].size = Math.max(10, updatedPanels[nextPanelIndex].size - sizeDiff);

      setPanels(updatedPanels);
    }
  };

  const handleResizeEnd = () => {
    if (resizing) {
      onPanelChange?.(panels);
      setResizing(null);
    }
  };

  React.useEffect(() => {
    if (resizing) {
      window.addEventListener('mousemove', handleResizeMove);
      window.addEventListener('mouseup', handleResizeEnd);
      return () => {
        window.removeEventListener('mousemove', handleResizeMove);
        window.removeEventListener('mouseup', handleResizeEnd);
      };
    }
  }, [resizing, panels]);

  const handleScroll = (event: React.UIEvent<HTMLDivElement>, panelId: string) => {
    if (!syncScrolling) return;

    const scrollTop = event.currentTarget.scrollTop;
    const scrollLeft = event.currentTarget.scrollLeft;

    // Sync scroll to all other panels
    panels.forEach(panel => {
      if (panel.id !== panelId) {
        const element = document.getElementById(`split-panel-${panel.id}`);
        if (element) {
          element.scrollTop = scrollTop;
          element.scrollLeft = scrollLeft;
        }
      }
    });
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
        <Tooltip title={`Switch to ${orientation === 'horizontal' ? 'vertical' : 'horizontal'} split`}>
          <IconButton size="small" onClick={toggleOrientation}>
            {orientation === 'horizontal' ? <SwapVertIcon /> : <SwapHorizIcon />}
          </IconButton>
        </Tooltip>

        <Tooltip title="Add split">
          <span>
            <IconButton size="small" onClick={addSplit} disabled={panels.length >= 4}>
              <AddIcon />
            </IconButton>
          </span>
        </Tooltip>

        <Tooltip title={syncScrolling ? 'Disable sync scrolling' : 'Enable sync scrolling'}>
          <IconButton size="small" onClick={() => setSyncScrolling(!syncScrolling)}>
            {syncScrolling ? <SyncIcon color="primary" /> : <SyncDisabledIcon />}
          </IconButton>
        </Tooltip>

        <Box sx={{ flex: 1 }} />

        <IconButton size="small" onClick={(e) => setMenuAnchor(e.currentTarget)}>
          <MoreVertIcon />
        </IconButton>
      </Box>

      {/* Split Panels */}
      <Box
        ref={containerRef}
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: orientation === 'horizontal' ? 'row' : 'column',
          overflow: 'hidden',
        }}
      >
        {panels.map((panel, index) => (
          <React.Fragment key={panel.id}>
            {/* Panel */}
            <Box
              sx={{
                [orientation === 'horizontal' ? 'width' : 'height']: `${panel.size}%`,
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
                position: 'relative',
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
                }}
              >
                <Box sx={{ flex: 1, fontSize: '0.875rem', fontWeight: 600, px: 1 }}>
                  {panel.title || `Panel ${index + 1}`}
                </Box>
                {panels.length > 1 && (
                  <Tooltip title="Close split">
                    <IconButton size="small" onClick={() => removeSplit(panel.id)}>
                      <CloseIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
              </Box>

              {/* Panel Content */}
              <Box
                id={`split-panel-${panel.id}`}
                onScroll={(e) => handleScroll(e, panel.id)}
                sx={{
                  flex: 1,
                  overflow: 'auto',
                  p: 2,
                }}
              >
                {panel.content || (
                  <Box
                    sx={{
                      height: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'text.secondary',
                    }}
                  >
                    No content
                  </Box>
                )}
              </Box>
            </Box>

            {/* Resize Handle */}
            {index < panels.length - 1 && (
              <Box
                onMouseDown={(e) => handleResizeStart(index, e)}
                sx={{
                  [orientation === 'horizontal' ? 'width' : 'height']: '4px',
                  backgroundColor: 'divider',
                  cursor: orientation === 'horizontal' ? 'ew-resize' : 'ns-resize',
                  position: 'relative',
                  zIndex: 1,
                  '&:hover': {
                    backgroundColor: 'primary.main',
                  },
                  '&:active': {
                    backgroundColor: 'primary.dark',
                  },
                }}
              />
            )}
          </React.Fragment>
        ))}
      </Box>

      {/* Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={() => setMenuAnchor(null)}
      >
        <MenuItem
          onClick={() => {
            toggleOrientation();
            setMenuAnchor(null);
          }}
        >
          {orientation === 'horizontal' ? 'Switch to Vertical' : 'Switch to Horizontal'}
        </MenuItem>
        <MenuItem
          onClick={() => {
            setSyncScrolling(!syncScrolling);
            setMenuAnchor(null);
          }}
        >
          {syncScrolling ? 'Disable' : 'Enable'} Sync Scrolling
        </MenuItem>
        <MuiDivider />
        <MenuItem
          onClick={() => {
            const equalSize = 100 / panels.length;
            setPanels(panels.map(p => ({ ...p, size: equalSize })));
            setMenuAnchor(null);
          }}
        >
          Reset Panel Sizes
        </MenuItem>
        <MenuItem
          onClick={() => {
            setPanels([{ id: generatePanelId(), content: initialContent, size: 100 }]);
            setMenuAnchor(null);
          }}
        >
          Close All Splits
        </MenuItem>
      </Menu>
    </Box>
  );
};
