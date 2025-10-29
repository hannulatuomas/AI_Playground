/**
 * NavigationSidebar - Main Feature Navigation
 * 
 * Postman-inspired sidebar navigation for accessing features.
 * Replaces the overwhelming 31-tab system with organized sections.
 */

import React, { useState } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  Divider,
  Typography,
  TextField,
  InputAdornment,
  IconButton,
  Tooltip,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import FolderIcon from '@mui/icons-material/Folder';
import HttpIcon from '@mui/icons-material/Http';
import SecurityIcon from '@mui/icons-material/Security';
import BuildIcon from '@mui/icons-material/Build';
import DescriptionIcon from '@mui/icons-material/Description';
import SettingsIcon from '@mui/icons-material/Settings';
import MonitorHeartIcon from '@mui/icons-material/MonitorHeart';
import BugReportIcon from '@mui/icons-material/BugReport';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import SearchIcon from '@mui/icons-material/Search';
import GraphqlIcon from '@mui/icons-material/GraphicEq';
import WebIcon from '@mui/icons-material/Web';
import CodeIcon from '@mui/icons-material/Code';
import StorageIcon from '@mui/icons-material/Storage';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CachedIcon from '@mui/icons-material/Cached';
import GitHubIcon from '@mui/icons-material/GitHub';
import VariableIcon from '@mui/icons-material/DataObject';
import ExtractIcon from '@mui/icons-material/FilterAlt';
import WorkspacesIcon from '@mui/icons-material/Workspaces';
import TemplateIcon from '@mui/icons-material/ContentCopy';
import SwaggerIcon from '@mui/icons-material/Api';
import PublishIcon from '@mui/icons-material/Publish';
import TerminalIcon from '@mui/icons-material/Terminal';

export type NavigationView = 
  | 'home'
  | 'collections'
  | 'request'
  | 'graphql'
  | 'wsdl'
  | 'grpc'
  | 'websocket'
  | 'sse'
  | 'mqtt'
  | 'amqp'
  | 'securityrunner'
  | 'owasp'
  | 'fuzzing'
  | 'zap'
  | 'vulnerability'
  | 'variables'
  | 'mock'
  | 'batch'
  | 'cache'
  | 'git'
  | 'extraction-rules'
  | 'workspaces'
  | 'templates'
  | 'swagger'
  | 'asyncapi'
  | 'apispec'
  | 'publisher'
  | 'settings'
  | 'monitor'
  | 'console';

interface NavigationItem {
  id: NavigationView;
  label: string;
  icon: React.ReactNode;
  badge?: number;
}

interface NavigationSection {
  id: string;
  label: string;
  icon: React.ReactNode;
  items: NavigationItem[];
  defaultExpanded?: boolean;
}

interface NavigationSidebarProps {
  activeView: NavigationView;
  onNavigate: (view: NavigationView) => void;
  onCollectionsClick?: () => void;
}

export const NavigationSidebar: React.FC<NavigationSidebarProps> = ({
  activeView,
  onNavigate,
  onCollectionsClick,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set([]) // Start with all sections collapsed
  );

  const sections: NavigationSection[] = [
    {
      id: 'apis',
      label: 'APIs & Protocols',
      icon: <HttpIcon />,
      defaultExpanded: true,
      items: [
        { id: 'request', label: 'REST/HTTP', icon: <HttpIcon fontSize="small" /> },
        { id: 'graphql', label: 'GraphQL', icon: <GraphqlIcon fontSize="small" /> },
        { id: 'wsdl', label: 'SOAP/WSDL', icon: <WebIcon fontSize="small" /> },
        { id: 'grpc', label: 'gRPC', icon: <CodeIcon fontSize="small" /> },
        { id: 'websocket', label: 'WebSocket', icon: <WebIcon fontSize="small" /> },
        { id: 'sse', label: 'Server-Sent Events', icon: <WebIcon fontSize="small" /> },
        { id: 'mqtt', label: 'MQTT', icon: <WebIcon fontSize="small" /> },
        { id: 'amqp', label: 'AMQP', icon: <WebIcon fontSize="small" /> },
      ],
    },
    {
      id: 'security',
      label: 'Security Testing',
      icon: <SecurityIcon />,
      defaultExpanded: false,
      items: [
        { id: 'securityrunner', label: 'Security Runner', icon: <SecurityIcon fontSize="small" /> },
        { id: 'owasp', label: 'OWASP Scanner', icon: <SecurityIcon fontSize="small" /> },
        { id: 'fuzzing', label: 'Fuzzing', icon: <BugReportIcon fontSize="small" /> },
        { id: 'zap', label: 'ZAP Proxy', icon: <SecurityIcon fontSize="small" /> },
        { id: 'vulnerability', label: 'Vulnerabilities', icon: <BugReportIcon fontSize="small" /> },
      ],
    },
    {
      id: 'tools',
      label: 'Tools & Automation',
      icon: <BuildIcon />,
      defaultExpanded: false,
      items: [
        { id: 'variables', label: 'Variables', icon: <VariableIcon fontSize="small" /> },
        { id: 'mock', label: 'Mock Servers', icon: <StorageIcon fontSize="small" /> },
        { id: 'batch', label: 'Batch Runner', icon: <PlayArrowIcon fontSize="small" /> },
        { id: 'cache', label: 'Cache', icon: <CachedIcon fontSize="small" /> },
        { id: 'git', label: 'Git Integration', icon: <GitHubIcon fontSize="small" /> },
        { id: 'extraction-rules', label: 'Extraction Rules', icon: <ExtractIcon fontSize="small" /> },
        { id: 'workspaces', label: 'Workspaces', icon: <WorkspacesIcon fontSize="small" /> },
        { id: 'templates', label: 'Templates', icon: <TemplateIcon fontSize="small" /> },
      ],
    },
    {
      id: 'docs',
      label: 'Documentation',
      icon: <DescriptionIcon />,
      defaultExpanded: false,
      items: [
        { id: 'swagger', label: 'Swagger/OpenAPI', icon: <SwaggerIcon fontSize="small" /> },
        { id: 'asyncapi', label: 'AsyncAPI', icon: <SwaggerIcon fontSize="small" /> },
        { id: 'apispec', label: 'API Spec Generator', icon: <CodeIcon fontSize="small" /> },
        { id: 'publisher', label: 'API Publisher', icon: <PublishIcon fontSize="small" /> },
      ],
    },
  ];

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(sectionId)) {
        next.delete(sectionId);
      } else {
        next.add(sectionId);
      }
      return next;
    });
  };

  const filteredSections = sections.map(section => ({
    ...section,
    items: section.items.filter(item =>
      item.label.toLowerCase().includes(searchQuery.toLowerCase())
    ),
  })).filter(section => section.items.length > 0);

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.paper',
        borderRight: 1,
        borderColor: 'divider',
      }}
    >
      {/* Search */}
      <Box sx={{ p: 2, pb: 1 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search features..."
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
      </Box>

      {/* Main Navigation Items */}
      <List sx={{ flexGrow: 1, overflow: 'auto', py: 0 }}>
        {/* Home */}
        <ListItem disablePadding>
          <ListItemButton
            selected={activeView === 'home'}
            onClick={() => onNavigate('home')}
          >
            <ListItemIcon>
              <HomeIcon />
            </ListItemIcon>
            <ListItemText primary="Home" />
          </ListItemButton>
        </ListItem>

        {/* Collections */}
        <ListItem disablePadding>
          <ListItemButton
            selected={activeView === 'collections'}
            onClick={onCollectionsClick}
          >
            <ListItemIcon>
              <FolderIcon />
            </ListItemIcon>
            <ListItemText primary="Collections" />
          </ListItemButton>
        </ListItem>

        <Divider sx={{ my: 1 }} />

        {/* Collapsible Sections */}
        {filteredSections.map((section) => (
          <React.Fragment key={section.id}>
            <ListItem disablePadding>
              <ListItemButton 
                onClick={() => toggleSection(section.id)}
                sx={{ py: 0.5 }}
              >
                <ListItemIcon sx={{ minWidth: 36 }}>{section.icon}</ListItemIcon>
                <ListItemText 
                  primary={section.label}
                  primaryTypographyProps={{ fontWeight: 600, fontSize: '0.85rem' }}
                />
                {expandedSections.has(section.id) ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />}
              </ListItemButton>
            </ListItem>
            <Collapse in={expandedSections.has(section.id)} timeout="auto" unmountOnExit>
              <List component="div" disablePadding>
                {section.items.map((item) => (
                  <ListItem key={item.id} disablePadding>
                    <ListItemButton
                      sx={{ pl: 4, py: 0.5 }}
                      selected={activeView === item.id}
                      onClick={() => onNavigate(item.id)}
                    >
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText 
                        primary={item.label}
                        primaryTypographyProps={{ fontSize: '0.8125rem' }}
                      />
                      {item.badge && (
                        <Box
                          sx={{
                            bgcolor: 'primary.main',
                            color: 'primary.contrastText',
                            borderRadius: '10px',
                            px: 1,
                            py: 0.25,
                            fontSize: '0.75rem',
                            fontWeight: 600,
                          }}
                        >
                          {item.badge}
                        </Box>
                      )}
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </Collapse>
          </React.Fragment>
        ))}

        <Divider sx={{ my: 1 }} />

        {/* Bottom Items */}
        <ListItem disablePadding>
          <ListItemButton
            selected={activeView === 'monitor'}
            onClick={() => onNavigate('monitor')}
          >
            <ListItemIcon>
              <MonitorHeartIcon />
            </ListItemIcon>
            <ListItemText primary="Monitoring" />
          </ListItemButton>
        </ListItem>

        <ListItem disablePadding>
          <ListItemButton
            selected={activeView === 'console'}
            onClick={() => onNavigate('console')}
          >
            <ListItemIcon>
              <TerminalIcon />
            </ListItemIcon>
            <ListItemText primary="Console" />
          </ListItemButton>
        </ListItem>

        <ListItem disablePadding>
          <ListItemButton
            selected={activeView === 'settings'}
            onClick={() => onNavigate('settings')}
          >
            <ListItemIcon>
              <SettingsIcon />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );
};
