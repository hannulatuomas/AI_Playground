/**
 * RecentItems - Quick Access to Recent Tabs/Requests
 * 
 * Features:
 * - Shows recently accessed tabs
 * - Click to open
 * - Shows type icon
 * - Shows last accessed time
 * - Clear recent items
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import ClearAllIcon from '@mui/icons-material/ClearAll';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import FolderIcon from '@mui/icons-material/Folder';
import CodeIcon from '@mui/icons-material/Code';
import StorageIcon from '@mui/icons-material/Storage';

interface RecentItem {
  id: string;
  title: string;
  type: string;
  lastAccessed: number;
  icon?: string;
}

interface RecentItemsProps {
  onItemClick?: (item: RecentItem) => void;
  maxItems?: number;
}

export const RecentItems: React.FC<RecentItemsProps> = ({ 
  onItemClick,
  maxItems = 10 
}) => {
  const [recentItems, setRecentItems] = useState<RecentItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadRecentItems();
  }, []);

  const loadRecentItems = async () => {
    setLoading(true);
    try {
      const tabs = await window.electronAPI.tabs.getAll();
      
      // Sort by lastAccessed and take top N
      const sorted = tabs
        .filter((tab: any) => tab.lastAccessed)
        .sort((a: any, b: any) => b.lastAccessed - a.lastAccessed)
        .slice(0, maxItems);
      
      setRecentItems(sorted);
    } catch (error) {
      console.error('Error loading recent items:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClearAll = async () => {
    try {
      // Would clear recent items tracking
      setRecentItems([]);
    } catch (error) {
      console.error('Error clearing recent items:', error);
    }
  };

  const getIcon = (type: string) => {
    const iconProps = { fontSize: 'small' as const };
    switch (type) {
      case 'request':
        return <InsertDriveFileIcon {...iconProps} />;
      case 'collection':
        return <FolderIcon {...iconProps} />;
      case 'graphql':
      case 'wsdl':
      case 'grpc':
        return <CodeIcon {...iconProps} />;
      case 'mock':
        return <StorageIcon {...iconProps} />;
      default:
        return <InsertDriveFileIcon {...iconProps} />;
    }
  };

  const getTimeAgo = (timestamp: number): string => {
    const seconds = Math.floor((Date.now() - timestamp) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  if (loading) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="caption" color="textSecondary">
          Loading...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 1, 
        p: 1.5,
        borderBottom: 1,
        borderColor: 'divider'
      }}>
        <AccessTimeIcon fontSize="small" />
        <Typography variant="subtitle2" sx={{ flex: 1, fontWeight: 600 }}>
          Recent
        </Typography>
        {recentItems.length > 0 && (
          <Tooltip title="Clear all">
            <IconButton size="small" onClick={handleClearAll}>
              <ClearAllIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        )}
      </Box>

      {/* List */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {recentItems.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <AccessTimeIcon sx={{ fontSize: 48, color: 'text.secondary', opacity: 0.3, mb: 1 }} />
            <Typography variant="body2" color="textSecondary">
              No recent items
            </Typography>
            <Typography variant="caption" color="textSecondary">
              Items you open will appear here
            </Typography>
          </Box>
        ) : (
          <List dense>
            {recentItems.map((item, index) => (
              <React.Fragment key={item.id}>
                {index > 0 && <Divider />}
                <ListItem disablePadding>
                  <ListItemButton 
                    onClick={() => onItemClick?.(item)}
                    sx={{ py: 1 }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      {getIcon(item.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={item.title}
                      secondary={getTimeAgo(item.lastAccessed)}
                      primaryTypographyProps={{
                        variant: 'body2',
                        noWrap: true,
                      }}
                      secondaryTypographyProps={{
                        variant: 'caption',
                      }}
                    />
                  </ListItemButton>
                </ListItem>
              </React.Fragment>
            ))}
          </List>
        )}
      </Box>
    </Box>
  );
};
