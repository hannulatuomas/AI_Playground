// Main React App component
import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Button from '@mui/material/Button';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Tooltip from '@mui/material/Tooltip';
import MenuIcon from '@mui/icons-material/Menu';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import SettingsIcon from '@mui/icons-material/Settings';
import SecurityIcon from '@mui/icons-material/Security';
import BugReportIcon from '@mui/icons-material/BugReport';
import StorageIcon from '@mui/icons-material/Storage';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ScheduleIcon from '@mui/icons-material/Schedule';
import CachedIcon from '@mui/icons-material/Cached';
import GitHubIcon from '@mui/icons-material/GitHub';
import ExtensionIcon from '@mui/icons-material/Extension';
import AssessmentIcon from '@mui/icons-material/Assessment';
import ImportExportIcon from '@mui/icons-material/ImportExport';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import PublishIcon from '@mui/icons-material/Publish';
import CallSplitIcon from '@mui/icons-material/CallSplit';
import DashboardCustomizeIcon from '@mui/icons-material/DashboardCustomize';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import Sidebar from './components/Sidebar';
import RequestPanel from './components/RequestPanel';
import ResponsePanel from './components/ResponsePanel';
import MockServerManager from './components/MockServerManager';
import BatchRunner from './components/BatchRunner';
import MonitoringDashboard from './components/MonitoringDashboard';
import SecurityReport from './components/SecurityReport';
import VulnerabilityScanner from './components/VulnerabilityScanner';
import SecurityRunner from './components/SecurityRunner';
import ZAPProxy from './components/ZAPProxy';
import OWASPScanner from './components/OWASPScanner';
import FuzzingTester from './components/FuzzingTester';
import GraphQLExplorer from './components/GraphQLExplorer';
import WSDLExplorer from './components/WSDLExplorer';
import ProtoExplorer from './components/ProtoExplorer';
import WebSocketClient from './components/WebSocketClient';
import SSEViewer from './components/SSEViewer';
import MQTTClient from './components/MQTTClient';
import AMQPClient from './components/AMQPClient';
import SwaggerViewer from './components/SwaggerViewer';
import AsyncSchemaViewer from './components/AsyncSchemaViewer';
import CacheSettings from './components/CacheSettings';
import GitPanel from './components/GitPanel';
import PluginManager from './components/PluginManager';
import ReportManager from './components/ReportManager';
import { ImportDialog } from './components/ImportDialog';
import { ExportDialog } from './components/ExportDialog';
import { WorkspaceManager } from './components/WorkspaceManager';
import { WorkspaceTemplates } from './components/WorkspaceTemplates';
import VariableExtractorDialog from './components/VariableExtractorDialog';
import VariablePreviewPanel from './components/VariablePreviewPanel';
import ExtractionRulesManager from './components/ExtractionRulesManager';
import DebugConsole from './components/DebugConsole';
import APISpecGenerator from './components/APISpecGenerator';
import { APIPublisher } from './components/APIPublisher';
import { SettingsDialog } from './components/SettingsDialog';
import { CommandPalette } from './components/CommandPalette';
import { GlobalSearch } from './components/GlobalSearch';
import { EnhancedTabBar } from './components/EnhancedTabBar';
import { FavoritesPanel } from './components/FavoritesPanel';
import { RecentItems } from './components/RecentItems';
import { SplitViewManager } from './components/SplitViewManager';
import { CustomizableLayout } from './components/CustomizableLayout';
import { CollapsibleSection } from './components/CollapsibleSection';
import { BreadcrumbNavigation, type BreadcrumbItem } from './components/BreadcrumbNavigation';
import { NavigationSidebar, type NavigationView } from './components/NavigationSidebar';
import { useResponsive } from './hooks/useResponsive';
import { KeyboardShortcutManager } from './services/KeyboardShortcutManager';
import Drawer from '@mui/material/Drawer';
import './styles/responsive.css';

// Initialize global keyboard shortcut manager
const shortcutManager = new KeyboardShortcutManager();

const MIN_SIDEBAR_SIZE = 15;
const MIN_PANEL_SIZE = 20;

const App: React.FC = () => {
  // Responsive hook - use early to determine initial state
  const { isMobile, isTablet, width } = useResponsive();
  
  // Calculate responsive sidebar size
  const DEFAULT_SIDEBAR_SIZE = isMobile ? 0 : (isTablet ? 25 : 20);
  
  const [mode, setMode] = useState<'light' | 'dark'>('dark');
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile); // Closed on mobile by default
  const [currentResponse, setCurrentResponse] = useState<any>(null);
  const [currentRequest, setCurrentRequest] = useState<any>(null);
  const [mainView, setMainView] = useState<'home' | 'request' | 'graphql' | 'wsdl' | 'grpc' | 'websocket' | 'sse' | 'mqtt' | 'amqp' | 'swagger' | 'asyncapi' | 'mock' | 'batch' | 'monitor' | 'securityrunner' | 'owasp' | 'fuzzing' | 'zap' | 'security' | 'vulnerability' | 'cache' | 'git' | 'plugins' | 'reports' | 'workspaces' | 'templates' | 'variables' | 'extraction-rules' | 'console' | 'apispec' | 'publisher'>('request');
  const [currentTabId, setCurrentTabId] = useState<string>('request');
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [globalSearchOpen, setGlobalSearchOpen] = useState(false);
  const [selectedCollections, setSelectedCollections] = useState<string[]>([]);
  const [selectedRequests, setSelectedRequests] = useState<string[]>([]);
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([]);
  const [splitViewEnabled, setSplitViewEnabled] = useState(false);
  const [customLayoutEnabled, setCustomLayoutEnabled] = useState(false);
  const [collectionsOpen, setCollectionsOpen] = useState(false);
  
  // Store tab content - maps tab ID to its view and data
  const [tabContents, setTabContents] = useState<Map<string, {
    view: string;
    request: any;
    response: any;
  }>>(new Map());

  // Initialize KeyboardShortcutManager
  React.useEffect(() => {
    // Initialize the manager
    shortcutManager.initialize();
    
    // Register handlers
    shortcutManager.registerHandler('command-palette', () => setCommandPaletteOpen(true));
    shortcutManager.registerHandler('global-search', () => setGlobalSearchOpen(true));
    shortcutManager.registerHandler('toggle-sidebar', () => setSidebarOpen(prev => !prev));
    shortcutManager.registerHandler('settings', () => setSettingsDialogOpen(true));
    shortcutManager.registerHandler('new-tab', () => handleNewTab());
    shortcutManager.registerHandler('close-tab', () => {
      if (currentTabId) handleTabClose(currentTabId);
    });
    
    // Tab navigation
    shortcutManager.registerHandler('go-back', async () => {
      try {
        await window.electronAPI.tabs.goBack();
        const active = await window.electronAPI.tabs.getActive();
        if (active) handleTabSelect(active.id);
      } catch (error) {
        console.error('Error going back:', error);
      }
    });
    
    shortcutManager.registerHandler('go-forward', async () => {
      try {
        await window.electronAPI.tabs.goForward();
        const active = await window.electronAPI.tabs.getActive();
        if (active) handleTabSelect(active.id);
      } catch (error) {
        console.error('Error going forward:', error);
      }
    });
    
    // Cleanup
    return () => {
      shortcutManager.destroy();
    };
  }, [currentTabId]);

  // Initialize tabs on mount
  const [tabsInitialized, setTabsInitialized] = React.useState(false);
  
  React.useEffect(() => {
    if (!tabsInitialized) {
      initializeTabs();
    }
  }, [tabsInitialized]);

  const initializeTabs = async () => {
    try {
      // Check if tabs API exists
      if (!window.electronAPI?.tabs) {
        console.warn('Tabs API not available - tabs will not be managed');
        return;
      }
      
      // Prevent duplicate initialization
      if (tabsInitialized) {
        console.log('Tabs already initialized, skipping');
        return;
      }

      // NOTE: We no longer create feature tabs here
      // Features are accessed via NavigationSidebar
      // Tabs are only for open documents (requests, etc.)
      
      const existingTabs = await window.electronAPI.tabs.getAll();
      setTabsInitialized(true);
      
      // Force EnhancedTabBar to reload
      setTimeout(() => {
        window.dispatchEvent(new Event('tabs-updated'));
      }, 100);
    } catch (error) {
      console.error('Error initializing tabs:', error);
      setTabsInitialized(true); // Mark as initialized even on error
    }
  };

  const handleTabSelect = async (tabId: string) => {
    try {
      // Save current tab's content before switching (for ALL tabs, not just document tabs)
      if (currentTabId) {
        setTabContents(prev => {
          const next = new Map(prev);
          next.set(currentTabId, {
            view: mainView,
            request: currentRequest,
            response: currentResponse,
          });
          return next;
        });
      }
      
      // Set active tab in TabManagerService
      if (window.electronAPI?.tabs) {
        await window.electronAPI.tabs.setActive(tabId);
      }
      
      setCurrentTabId(tabId);
      
      // Load tab's saved content
      const savedContent = tabContents.get(tabId);
      if (savedContent) {
        // Restore the saved view and data
        setMainView(savedContent.view as any);
        setCurrentRequest(savedContent.request);
        setCurrentResponse(savedContent.response);
      } else {
        // New tab - default to request view with empty content
        setMainView('request');
        setCurrentRequest(null);
        setCurrentResponse(null);
      }
      
      // Update breadcrumbs (don't show root since we have "LocalAPI" in toolbar)
      const items: BreadcrumbItem[] = [];
      
      if (tabId !== 'request') {
        items.push({
          id: tabId,
          label: tabId.charAt(0).toUpperCase() + tabId.slice(1),
          type: 'other',
        });
      }
      
      setBreadcrumbs(items);
    } catch (error) {
      console.error('Error selecting tab:', error);
    }
  };

  const handleTabClose = async (tabId: string) => {
    try {
      await window.electronAPI.tabs.close(tabId);
      
      // Trigger tab bar refresh
      window.dispatchEvent(new Event('tabs-updated'));
      
      // Get updated tab list
      const tabs = await window.electronAPI.tabs.getAll();
      
      // If closing current tab, switch to first available
      if (tabId === currentTabId) {
        if (tabs.length > 0) {
          await handleTabSelect(tabs[0].id);
        } else {
          // No tabs left, go to home view
          setMainView('home');
          setCurrentTabId('');
        }
      }
    } catch (error) {
      console.error('Error closing tab:', error);
    }
  };

  const handleNewTab = async () => {
    try {
      const newTab = await window.electronAPI.tabs.create({
        id: `tab-${Date.now()}`,
        title: 'New Tab',
        type: 'request',
        closable: true,
      });
      
      // Trigger tab bar refresh
      window.dispatchEvent(new Event('tabs-updated'));
      
      // Wait a bit for the tab bar to update, then select the new tab
      setTimeout(() => {
        handleTabSelect(newTab.id);
      }, 50);
    } catch (error) {
      console.error('Error creating tab:', error);
    }
  };

  // Breadcrumbs are updated in handleTabSelect, no need for separate useEffect

  // Apply CSS variables for theme
  React.useEffect(() => {
    const root = document.documentElement;
    if (mode === 'dark') {
      root.style.setProperty('--color-primary', '#2196f3');
      root.style.setProperty('--color-background', '#1e1e1e');
      root.style.setProperty('--color-surface', '#252526');
      root.style.setProperty('--color-text', '#ffffff');
      root.style.setProperty('--color-text-secondary', '#b0b0b0');
      root.style.setProperty('--color-border', '#3e3e3e');
      root.style.setProperty('--color-hover', '#2a2a2a');
    } else {
      root.style.setProperty('--color-primary', '#1976d2');
      root.style.setProperty('--color-background', '#ffffff');
      root.style.setProperty('--color-surface', '#f5f5f5');
      root.style.setProperty('--color-text', '#000000');
      root.style.setProperty('--color-text-secondary', '#666666');
      root.style.setProperty('--color-border', '#e0e0e0');
      root.style.setProperty('--color-hover', '#f0f0f0');
    }
  }, [mode]);

  const theme = createTheme({
    palette: {
      mode,
      primary: {
        main: mode === 'dark' ? '#2196f3' : '#1976d2',
      },
      background: {
        default: mode === 'dark' ? '#1e1e1e' : '#ffffff',
        paper: mode === 'dark' ? '#252526' : '#f5f5f5',
      },
    },
  });

  const toggleTheme = () => {
    setMode(prev => prev === 'light' ? 'dark' : 'light');
  };

  const toggleSidebar = () => {
    setSidebarOpen(prev => !prev);
  };

  const handleResponse = (response: any) => {
    setCurrentResponse(response);
  };

  const handleRequestSelect = (request: any) => {
    setCurrentRequest(request);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
        {/* Top Menu Bar */}
        <AppBar
          position="static"
          elevation={0}
          sx={{
            backgroundColor: theme.palette.background.paper,
            color: theme.palette.text.primary,
            borderBottom: 1,
            borderColor: 'divider',
          }}
        >
          <Toolbar variant="dense" sx={{ minHeight: 48 }}>
            <Tooltip title="Toggle Sidebar">
              <IconButton
                edge="start"
                color="inherit"
                onClick={toggleSidebar}
                sx={{ mr: 1 }}
              >
                <MenuIcon />
              </IconButton>
            </Tooltip>
            <Typography
              variant="h6"
              component="div"
              sx={{ mr: 3, color: theme.palette.primary.main, fontWeight: 700, fontSize: '1.1rem' }}
            >
              LocalAPI
            </Typography>
            
            {/* EnhancedTabBar - Full tab management system */}
            <Box sx={{ flexGrow: 1 }}>
              <EnhancedTabBar
                onTabSelect={handleTabSelect}
                onTabClose={handleTabClose}
                onNewTab={handleNewTab}
              />
            </Box>
            
            <Tooltip title="Import">
              <IconButton color="inherit" onClick={() => setImportDialogOpen(true)} sx={{ ml: 1 }}>
                <FileUploadIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Export">
              <IconButton color="inherit" onClick={() => setExportDialogOpen(true)}>
                <FileDownloadIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Toggle Theme">
              <IconButton color="inherit" onClick={toggleTheme} sx={{ ml: 1 }}>
                {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
              </IconButton>
            </Tooltip>
            <Tooltip title={splitViewEnabled ? "Disable Split View" : "Enable Split View"}>
              <IconButton 
                color="inherit" 
                onClick={() => setSplitViewEnabled(prev => !prev)}
                sx={{ 
                  ml: 1,
                  backgroundColor: splitViewEnabled ? 'primary.main' : 'transparent',
                  '&:hover': {
                    backgroundColor: splitViewEnabled ? 'primary.dark' : 'action.hover',
                  }
                }}
              >
                <CallSplitIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title={customLayoutEnabled ? "Disable Custom Layout" : "Enable Custom Layout"}>
              <IconButton 
                color="inherit" 
                onClick={() => setCustomLayoutEnabled(prev => !prev)}
                sx={{ 
                  ml: 1,
                  backgroundColor: customLayoutEnabled ? 'primary.main' : 'transparent',
                  '&:hover': {
                    backgroundColor: customLayoutEnabled ? 'primary.dark' : 'action.hover',
                  }
                }}
              >
                <DashboardCustomizeIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Settings">
              <IconButton color="inherit" onClick={() => setSettingsDialogOpen(true)}>
                <SettingsIcon />
              </IconButton>
            </Tooltip>
          </Toolbar>
        </AppBar>

        {/* Breadcrumb Navigation */}
        <BreadcrumbNavigation 
          items={breadcrumbs}
          onNavigate={(item) => {
            if (item.id === 'root') {
              setMainView('request');
            }
          }}
        />

        {/* Main Content with Resizable Panels */}
        <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
          {customLayoutEnabled ? (
            <CustomizableLayout
              onLayoutChange={(layout) => {
                console.log('Layout changed:', layout);
              }}
            >
              {/* Main content rendered inside customizable layout */}
            </CustomizableLayout>
          ) : (
          <PanelGroup direction="horizontal">
            {/* Sidebar Panel */}
            {sidebarOpen && (
              <>
                <Panel
                  defaultSize={DEFAULT_SIDEBAR_SIZE}
                  minSize={MIN_SIDEBAR_SIZE}
                  maxSize={40}
                  style={{
                    overflow: 'hidden',
                    borderRight: `1px solid ${theme.palette.divider}`,
                  }}
                >
                  {/* Navigation Sidebar - Postman-style feature navigation */}
                  <NavigationSidebar
                    activeView={mainView as NavigationView}
                    onNavigate={(view) => {
                      setMainView(view as any);
                      // Update breadcrumbs
                      if (view !== 'request' && view !== 'home') {
                        setBreadcrumbs([{
                          id: view,
                          label: view.charAt(0).toUpperCase() + view.slice(1).replace(/-/g, ' '),
                          type: 'other',
                        }]);
                      } else {
                        setBreadcrumbs([]);
                      }
                    }}
                    onCollectionsClick={() => {
                      setCollectionsOpen(!collectionsOpen);
                    }}
                  />
                </Panel>
                <PanelResizeHandle
                  style={{
                    width: '4px',
                    backgroundColor: theme.palette.divider,
                    cursor: 'col-resize',
                    transition: 'background-color 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    (e.target as HTMLElement).style.backgroundColor = theme.palette.primary.main;
                  }}
                  onMouseLeave={(e) => {
                    (e.target as HTMLElement).style.backgroundColor = theme.palette.divider;
                  }}
                />
              </>
            )}

            {/* Main Content Panel */}
            <Panel minSize={30}>
              {splitViewEnabled ? (
                <SplitViewManager 
                  initialContent={
                    mainView === 'request' ? (
                      <PanelGroup direction="vertical">
                        {/* Request Panel */}
                        <Panel defaultSize={50} minSize={MIN_PANEL_SIZE}>
                          <Box sx={{ height: '100%', overflow: 'auto' }}>
                            <RequestPanel onResponse={handleResponse} initialRequest={currentRequest} />
                          </Box>
                        </Panel>
                        
                        <PanelResizeHandle
                          style={{
                            height: '4px',
                            backgroundColor: theme.palette.divider,
                            cursor: 'row-resize',
                            transition: 'background-color 0.2s',
                          }}
                          onMouseEnter={(e) => {
                            (e.target as HTMLElement).style.backgroundColor = theme.palette.primary.main;
                          }}
                          onMouseLeave={(e) => {
                            (e.target as HTMLElement).style.backgroundColor = theme.palette.divider;
                          }}
                        />
                        
                        {/* Response Panel */}
                        <Panel defaultSize={50} minSize={MIN_PANEL_SIZE}>
                          <Box sx={{ height: '100%', overflow: 'auto', backgroundColor: theme.palette.background.paper }}>
                            <ResponsePanel response={currentResponse} />
                          </Box>
                        </Panel>
                      </PanelGroup>
                    ) : null
                  }
                  onPanelChange={(panels) => {
                    console.log('Split view panels changed:', panels);
                  }}
                />
              ) : (
                <>
                  {mainView === 'home' && (
                    <Box sx={{ 
                      height: '100%', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      flexDirection: 'column',
                      gap: 3,
                      p: 4
                    }}>
                      <Typography variant="h3" sx={{ fontWeight: 700, color: 'primary.main' }}>
                        Welcome to LocalAPI
                      </Typography>
                      <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600, textAlign: 'center' }}>
                        Your fully local, offline-capable API development tool. Get started by creating a new request or exploring the features in the sidebar.
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                        <Button 
                          variant="contained" 
                          size="large"
                          onClick={() => setMainView('request')}
                        >
                          New Request
                        </Button>
                        <Button 
                          variant="outlined" 
                          size="large"
                          onClick={() => setCollectionsOpen(true)}
                        >
                          Browse Collections
                        </Button>
                      </Box>
                    </Box>
                  )}
                  
                  {mainView === 'request' && (
                    <PanelGroup direction="vertical">
                      {/* Request Panel */}
                      <Panel defaultSize={50} minSize={MIN_PANEL_SIZE}>
                        <Box sx={{ height: '100%', overflow: 'auto' }}>
                          <RequestPanel onResponse={handleResponse} initialRequest={currentRequest} />
                        </Box>
                      </Panel>
                      
                      <PanelResizeHandle
                        style={{
                          height: '4px',
                          backgroundColor: theme.palette.divider,
                          cursor: 'row-resize',
                          transition: 'background-color 0.2s',
                        }}
                        onMouseEnter={(e) => {
                          (e.target as HTMLElement).style.backgroundColor = theme.palette.primary.main;
                        }}
                        onMouseLeave={(e) => {
                          (e.target as HTMLElement).style.backgroundColor = theme.palette.divider;
                        }}
                      />
                      
                      {/* Response Panel */}
                      <Panel defaultSize={50} minSize={MIN_PANEL_SIZE}>
                        <Box sx={{ height: '100%', overflow: 'auto', backgroundColor: theme.palette.background.paper }}>
                          <ResponsePanel response={currentResponse} />
                        </Box>
                      </Panel>
                    </PanelGroup>
                  )}
                  
                      
                  {mainView === 'graphql' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <GraphQLExplorer endpoint="https://api.example.com/graphql" />
                    </Box>
                  )}
                  
                  {mainView === 'wsdl' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <WSDLExplorer />
                    </Box>
                  )}
                  
                  {mainView === 'grpc' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <ProtoExplorer />
                    </Box>
                  )}
                  
                  {mainView === 'websocket' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <WebSocketClient />
                    </Box>
                  )}
              
                  {mainView === 'sse' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <SSEViewer />
                    </Box>
                  )}
                  
                  {mainView === 'mqtt' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <MQTTClient />
                    </Box>
                  )}
                  
                  {mainView === 'amqp' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <AMQPClient />
                    </Box>
                  )}
                  
                  {mainView === 'swagger' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <SwaggerViewer />
                    </Box>
                  )}
              
                  {mainView === 'asyncapi' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <AsyncSchemaViewer />
                    </Box>
                  )}
                  
                  {mainView === 'mock' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <MockServerManager />
                    </Box>
                  )}
                  
                  {mainView === 'batch' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <BatchRunner />
                    </Box>
                  )}
                  
                  {mainView === 'monitor' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <MonitoringDashboard />
                    </Box>
                  )}
                  
                  {mainView === 'securityrunner' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <SecurityRunner />
                    </Box>
                  )}
                  
                  {mainView === 'owasp' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <OWASPScanner />
                    </Box>
                  )}
                  
                  {mainView === 'fuzzing' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <FuzzingTester />
                    </Box>
                  )}
                  
                  {mainView === 'zap' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <ZAPProxy />
                    </Box>
                  )}
                  
                  {mainView === 'security' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <SecurityReport report={null} />
                    </Box>
                  )}
                  
                  {mainView === 'vulnerability' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <VulnerabilityScanner />
                    </Box>
                  )}
              
                  {mainView === 'cache' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <CacheSettings />
                    </Box>
                  )}
                  
                  {mainView === 'git' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <GitPanel />
                    </Box>
                  )}
                  
                  {mainView === 'plugins' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <PluginManager />
                    </Box>
                  )}
                  
                  {mainView === 'reports' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <ReportManager />
                    </Box>
                  )}
              
                  {mainView === 'workspaces' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <WorkspaceManager />
                    </Box>
                  )}
                  
                  {mainView === 'templates' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <WorkspaceTemplates />
                    </Box>
                  )}
                  
                  {mainView === 'variables' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <VariablePreviewPanel />
                    </Box>
                  )}
                  
                  {mainView === 'extraction-rules' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <ExtractionRulesManager />
                    </Box>
                  )}
              
                  {mainView === 'console' && (
                    <Box sx={{ height: '100%', overflow: 'hidden' }}>
                      <DebugConsole />
                    </Box>
                  )}
                  
                  {mainView === 'apispec' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <APISpecGenerator />
                    </Box>
                  )}
                  
                  {mainView === 'publisher' && (
                    <Box sx={{ height: '100%', overflow: 'auto' }}>
                      <APIPublisher />
                    </Box>
                  )}
                </>
              )}
            </Panel>
          </PanelGroup>
          )}
        </Box>
        
        {/* Import Dialog */}
        <ImportDialog 
          open={importDialogOpen} 
          onClose={() => setImportDialogOpen(false)} 
        />
        
        {/* Export Dialog */}
        <ExportDialog 
          open={exportDialogOpen} 
          onClose={() => setExportDialogOpen(false)}
          selectedCollections={selectedCollections}
          selectedRequests={selectedRequests}
        />
        
        {/* Settings Dialog */}
        <SettingsDialog 
          open={settingsDialogOpen} 
          onClose={() => setSettingsDialogOpen(false)}
        />
        
        {/* Command Palette */}
        <CommandPalette 
          open={commandPaletteOpen} 
          onClose={() => setCommandPaletteOpen(false)}
        />
        
        {/* Global Search */}
        <GlobalSearch 
          open={globalSearchOpen} 
          onClose={() => setGlobalSearchOpen(false)}
          onResultSelect={(result) => {
            console.log('Selected:', result);
            // Navigate to selected item
          }}
        />
        
        {/* Collections Drawer */}
        <Drawer
          anchor="left"
          open={collectionsOpen}
          onClose={() => setCollectionsOpen(false)}
          sx={{
            '& .MuiDrawer-paper': {
              width: 320,
              boxSizing: 'border-box',
              mt: '64px', // Below toolbar
              height: 'calc(100% - 64px)',
            },
          }}
        >
          <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Collections
            </Typography>
            <Sidebar onRequestSelect={(request) => {
              handleRequestSelect(request);
              setCollectionsOpen(false); // Close drawer after selection
            }} />
          </Box>
        </Drawer>
      </Box>
    </ThemeProvider>
  );
};

export default App;
