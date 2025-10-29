/**
 * BreadcrumbNavigation - Path Navigation Component
 * 
 * Features:
 * - Show current path (Workspace > Collection > Folder > Request)
 * - Click to navigate
 * - Copy path functionality
 * - Responsive collapse for long paths
 * - Icon for each level
 */

import React from 'react';
import {
  Box,
  Breadcrumbs,
  Link,
  Typography,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import FolderIcon from '@mui/icons-material/Folder';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import PublicIcon from '@mui/icons-material/Public';

export interface BreadcrumbItem {
  id: string;
  label: string;
  type: 'workspace' | 'collection' | 'folder' | 'request' | 'environment' | 'other';
  path?: string;
}

interface BreadcrumbNavigationProps {
  items: BreadcrumbItem[];
  onNavigate?: (item: BreadcrumbItem) => void;
  maxItems?: number;
  showHome?: boolean;
}

export const BreadcrumbNavigation: React.FC<BreadcrumbNavigationProps> = ({
  items,
  onNavigate,
  maxItems = 5,
  showHome = true,
}) => {
  const handleCopyPath = () => {
    const path = items.map(item => item.label).join(' > ');
    navigator.clipboard.writeText(path);
  };

  const getIcon = (type: BreadcrumbItem['type'], isLast: boolean) => {
    const iconProps = { fontSize: 'small' as const, sx: { mr: 0.5 } };
    
    switch (type) {
      case 'workspace':
        return <HomeIcon {...iconProps} />;
      case 'collection':
        return isLast ? <FolderOpenIcon {...iconProps} /> : <FolderIcon {...iconProps} />;
      case 'folder':
        return isLast ? <FolderOpenIcon {...iconProps} /> : <FolderIcon {...iconProps} />;
      case 'request':
        return <InsertDriveFileIcon {...iconProps} />;
      case 'environment':
        return <PublicIcon {...iconProps} />;
      default:
        return <FolderIcon {...iconProps} />;
    }
  };

  const getColor = (type: BreadcrumbItem['type']) => {
    const colors: Record<BreadcrumbItem['type'], string> = {
      workspace: '#2196F3',
      collection: '#4CAF50',
      folder: '#FFC107',
      request: '#FF5722',
      environment: '#9C27B0',
      other: '#757575',
    };
    return colors[type];
  };

  // Collapse breadcrumbs if too many
  const shouldCollapse = items.length > maxItems;
  const displayItems = shouldCollapse
    ? [
        items[0], // First item (usually workspace)
        { id: 'ellipsis', label: '...', type: 'other' as const },
        ...items.slice(-(maxItems - 2)), // Last few items
      ]
    : items;

  if (items.length === 0) {
    return null;
  }

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        px: 2,
        py: 1,
        backgroundColor: 'background.paper',
        borderBottom: 1,
        borderColor: 'divider',
      }}
    >
      {showHome && (
        <Tooltip title="Go to root">
          <IconButton
            size="small"
            onClick={() => onNavigate?.({ id: 'root', label: 'Root', type: 'workspace' })}
          >
            <HomeIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      )}

      <Breadcrumbs
        separator={<NavigateNextIcon fontSize="small" />}
        maxItems={maxItems}
        sx={{ flex: 1 }}
      >
        {displayItems.map((item, index) => {
          const isLast = index === displayItems.length - 1;
          const isEllipsis = item.id === 'ellipsis';

          if (isEllipsis) {
            return (
              <Typography
                key="ellipsis"
                color="text.secondary"
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  fontSize: '0.875rem',
                }}
              >
                ...
              </Typography>
            );
          }

          return isLast ? (
            <Typography
              key={item.id}
              color="text.primary"
              sx={{
                display: 'flex',
                alignItems: 'center',
                fontSize: '0.875rem',
                fontWeight: 600,
              }}
            >
              {getIcon(item.type, true)}
              {item.label}
            </Typography>
          ) : (
            <Link
              key={item.id}
              underline="hover"
              color="inherit"
              href="#"
              onClick={(e) => {
                e.preventDefault();
                onNavigate?.(item);
              }}
              sx={{
                display: 'flex',
                alignItems: 'center',
                fontSize: '0.875rem',
                cursor: 'pointer',
                '&:hover': {
                  color: getColor(item.type),
                },
              }}
            >
              {getIcon(item.type, false)}
              {item.label}
            </Link>
          );
        })}
      </Breadcrumbs>

      {/* Type badge */}
      {items.length > 0 && (
        <Chip
          label={items[items.length - 1].type}
          size="small"
          sx={{
            height: 20,
            fontSize: '0.7rem',
            backgroundColor: getColor(items[items.length - 1].type),
            color: 'white',
          }}
        />
      )}

      {/* Copy path button */}
      <Tooltip title="Copy path">
        <IconButton size="small" onClick={handleCopyPath}>
          <ContentCopyIcon fontSize="small" />
        </IconButton>
      </Tooltip>
    </Box>
  );
};
