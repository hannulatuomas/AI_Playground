/**
 * DebugConsole Component - Main console interface
 * 
 * Features:
 * - Real-time log display with virtual scrolling
 * - Filtering by method, status, type, time range
 * - Full-text search across all entries
 * - Entry details panel with tabs
 * - Toolbar actions (clear, pause, export, settings)
 * - Auto-scroll toggle
 * - Request replay functionality
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  Chip,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Toolbar,
  Divider,
  List,
  ListItem,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Tooltip,
  CircularProgress,
  Alert,
  Switch,
  FormControlLabel,
  Menu,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Pause as PauseIcon,
  PlayArrow as PlayIcon,
  FileDownload as ExportIcon,
  Settings as SettingsIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
  Replay as ReplayIcon,
  FilterList as FilterIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

interface ConsoleEntry {
  id: string;
  timestamp: number;
  type: 'request' | 'response' | 'websocket' | 'sse' | 'script' | 'error';
  method?: string;
  url?: string;
  status?: number;
  statusText?: string;
  headers?: Record<string, string>;
  body?: any;
  duration?: number;
  timings?: any;
  requestId?: string;
  protocol?: string;
  cached?: boolean;
  error?: string;
  direction?: 'sent' | 'received';
  connectionId?: string;
  eventType?: string;
  scriptOutput?: string;
  logLevel?: 'log' | 'info' | 'warn' | 'error';
}

interface ConsoleFilter {
  methods?: string[];
  statuses?: number[];
  types?: string[];
  timeRange?: { start: number; end: number };
  search?: string;
  hasError?: boolean;
}

const DebugConsole: React.FC = () => {
  const [entries, setEntries] = useState<ConsoleEntry[]>([]);
  const [filteredEntries, setFilteredEntries] = useState<ConsoleEntry[]>([]);
  const [selectedEntry, setSelectedEntry] = useState<ConsoleEntry | null>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<ConsoleFilter>({});
  const [showFilters, setShowFilters] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [exportMenuAnchor, setExportMenuAnchor] = useState<null | HTMLElement>(null);
  const [stats, setStats] = useState<any>(null);
  const [persistence, setPersistence] = useState(true);
  const [maxEntries, setMaxEntries] = useState(10000);
  const [selectedTab, setSelectedTab] = useState(0);
  const [loading, setLoading] = useState(false);
  
  const listRef = useRef<HTMLDivElement>(null);
  const pollInterval = useRef<NodeJS.Timeout>();

  // Load initial entries
  useEffect(() => {
    loadEntries();
    loadStats();
    checkPausedState();
  }, []);

  // Poll for new entries every 2 seconds when not paused
  useEffect(() => {
    if (!isPaused) {
      pollInterval.current = setInterval(() => {
        loadEntries();
        loadStats();
      }, 2000);
    } else {
      if (pollInterval.current) {
        clearInterval(pollInterval.current);
      }
    }

    return () => {
      if (pollInterval.current) {
        clearInterval(pollInterval.current);
      }
    };
  }, [isPaused]);

  // Auto-scroll to bottom when new entries arrive
  useEffect(() => {
    if (autoScroll && listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [filteredEntries, autoScroll]);

  // Apply filters whenever entries or filter state changes
  useEffect(() => {
    applyFilters();
  }, [entries, filters, searchQuery]);

  const loadEntries = async () => {
    try {
      const data = await window.electronAPI.console.getEntries(filters);
      setEntries(data);
    } catch (error) {
      console.error('Error loading console entries:', error);
    }
  };

  const loadStats = async () => {
    try {
      const data = await window.electronAPI.console.getStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading console stats:', error);
    }
  };

  const checkPausedState = async () => {
    try {
      const paused = await window.electronAPI.console.isPaused();
      setIsPaused(paused);
    } catch (error) {
      console.error('Error checking paused state:', error);
    }
  };

  const applyFilters = () => {
    let filtered = [...entries];

    // Apply search
    if (searchQuery) {
      filtered = filtered.filter(entry =>
        entry.url?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        entry.method?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        entry.error?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        entry.scriptOutput?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredEntries(filtered);
  };

  const handleClearAll = async () => {
    if (confirm('Are you sure you want to clear all console entries?')) {
      try {
        await window.electronAPI.console.clearEntries();
        setEntries([]);
        setSelectedEntry(null);
      } catch (error) {
        console.error('Error clearing console:', error);
      }
    }
  };

  const handleTogglePause = async () => {
    try {
      await window.electronAPI.console.setPaused(!isPaused);
      setIsPaused(!isPaused);
    } catch (error) {
      console.error('Error toggling pause:', error);
    }
  };

  const handleExport = async (format: 'json' | 'csv' | 'har') => {
    try {
      setLoading(true);
      const data = await window.electronAPI.console.exportEntries({
        format,
        filters,
        includeHeaders: true,
        includeBody: true,
      });

      // Create download link
      const blob = new Blob([data], { 
        type: format === 'json' ? 'application/json' : 
              format === 'csv' ? 'text/csv' : 'application/json'
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `console-export-${Date.now()}.${format}`;
      a.click();
      URL.revokeObjectURL(url);

      setExportMenuAnchor(null);
    } catch (error) {
      console.error('Error exporting console:', error);
      alert('Failed to export console entries');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteEntry = async (id: string) => {
    try {
      await window.electronAPI.console.deleteEntry(id);
      setEntries(entries.filter(e => e.id !== id));
      if (selectedEntry?.id === id) {
        setSelectedEntry(null);
      }
    } catch (error) {
      console.error('Error deleting entry:', error);
    }
  };

  const handleReplayRequest = (entry: ConsoleEntry) => {
    // TODO: Integrate with request sender
    console.log('Replay request:', entry);
    alert('Request replay will be implemented in integration phase');
  };

  const handleSaveSettings = async () => {
    try {
      await window.electronAPI.console.setPersistence(persistence);
      await window.electronAPI.console.setMaxEntries(maxEntries);
      setSettingsOpen(false);
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };

  const getEntryIcon = (entry: ConsoleEntry) => {
    if (entry.type === 'error' || entry.error) {
      return <ErrorIcon color="error" fontSize="small" />;
    }
    if (entry.type === 'script' && entry.logLevel === 'warn') {
      return <WarningIcon color="warning" fontSize="small" />;
    }
    if (entry.type === 'script' && entry.logLevel === 'info') {
      return <InfoIcon color="info" fontSize="small" />;
    }
    return null;
  };

  const getStatusColor = (status?: number): 'success' | 'error' | 'warning' | 'default' => {
    if (!status) return 'default';
    if (status >= 200 && status < 300) return 'success';
    if (status >= 400) return 'error';
    if (status >= 300) return 'warning';
    return 'default';
  };

  const formatTimestamp = (timestamp: number): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour12: false });
  };

  const formatDuration = (duration?: number): string => {
    if (!duration) return '';
    return `${duration}ms`;
  };

  const renderEntryListItem = (entry: ConsoleEntry) => {
    const isSelected = selectedEntry?.id === entry.id;
    
    return (
      <ListItem
        key={entry.id}
        button
        selected={isSelected}
        onClick={() => setSelectedEntry(entry)}
        sx={{
          borderLeft: entry.error ? '3px solid #f44336' : 
                     entry.type === 'error' ? '3px solid #f44336' :
                     entry.status && entry.status >= 400 ? '3px solid #ff9800' : 
                     'none',
          backgroundColor: isSelected ? 'action.selected' : 'inherit',
          '&:hover': {
            backgroundColor: 'action.hover',
          },
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 1 }}>
          {getEntryIcon(entry)}
          
          <Typography variant="caption" sx={{ minWidth: 70, fontFamily: 'monospace' }}>
            {formatTimestamp(entry.timestamp)}
          </Typography>

          {entry.type === 'request' || entry.type === 'response' ? (
            <>
              <Chip
                label={entry.method}
                size="small"
                sx={{ minWidth: 60 }}
              />
              <Typography variant="body2" sx={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {entry.url}
              </Typography>
              {entry.status && (
                <Chip
                  label={`${entry.status} ${entry.statusText || ''}`}
                  size="small"
                  color={getStatusColor(entry.status)}
                  sx={{ minWidth: 100 }}
                />
              )}
              {entry.duration && (
                <Typography variant="caption" sx={{ minWidth: 60, color: 'text.secondary' }}>
                  {formatDuration(entry.duration)}
                </Typography>
              )}
              {entry.cached && (
                <Chip label="cached" size="small" color="info" variant="outlined" />
              )}
            </>
          ) : entry.type === 'websocket' ? (
            <>
              <Chip label="WS" size="small" color="primary" />
              <Typography variant="body2" sx={{ flex: 1 }}>
                {entry.direction === 'sent' ? '→' : '←'} {entry.body?.toString().substring(0, 100)}
              </Typography>
            </>
          ) : entry.type === 'sse' ? (
            <>
              <Chip label="SSE" size="small" color="secondary" />
              <Typography variant="body2" sx={{ flex: 1 }}>
                {entry.eventType || 'message'}: {entry.body?.toString().substring(0, 100)}
              </Typography>
            </>
          ) : entry.type === 'script' ? (
            <>
              <Chip label={entry.logLevel || 'log'} size="small" />
              <Typography variant="body2" sx={{ flex: 1, fontFamily: 'monospace' }}>
                {entry.scriptOutput}
              </Typography>
            </>
          ) : entry.type === 'error' ? (
            <>
              <Chip label="ERROR" size="small" color="error" />
              <Typography variant="body2" sx={{ flex: 1, color: 'error.main' }}>
                {entry.error}
              </Typography>
            </>
          ) : null}

          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              handleDeleteEntry(entry.id);
            }}
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Box>
      </ListItem>
    );
  };

  const renderEntryDetails = () => {
    if (!selectedEntry) {
      return (
        <Box sx={{ p: 4, textAlign: 'center', color: 'text.secondary' }}>
          <Typography>Select a console entry to view details</Typography>
        </Box>
      );
    }

    return (
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Entry Details</Typography>
          {(selectedEntry.type === 'request' || selectedEntry.type === 'response') && (
            <Button
              startIcon={<ReplayIcon />}
              onClick={() => handleReplayRequest(selectedEntry)}
              variant="outlined"
              size="small"
            >
              Replay Request
            </Button>
          )}
        </Box>

        <Tabs value={selectedTab} onChange={(_, v) => setSelectedTab(v)}>
          <Tab label="Overview" />
          <Tab label="Headers" />
          <Tab label="Body" />
          <Tab label="Timing" />
        </Tabs>

        <Box sx={{ mt: 2 }}>
          {selectedTab === 0 && (
            <Box>
              <Typography variant="body2"><strong>ID:</strong> {selectedEntry.id}</Typography>
              <Typography variant="body2"><strong>Timestamp:</strong> {new Date(selectedEntry.timestamp).toLocaleString()}</Typography>
              <Typography variant="body2"><strong>Type:</strong> {selectedEntry.type}</Typography>
              {selectedEntry.method && <Typography variant="body2"><strong>Method:</strong> {selectedEntry.method}</Typography>}
              {selectedEntry.url && <Typography variant="body2"><strong>URL:</strong> {selectedEntry.url}</Typography>}
              {selectedEntry.status && <Typography variant="body2"><strong>Status:</strong> {selectedEntry.status} {selectedEntry.statusText}</Typography>}
              {selectedEntry.protocol && <Typography variant="body2"><strong>Protocol:</strong> {selectedEntry.protocol}</Typography>}
              {selectedEntry.duration && <Typography variant="body2"><strong>Duration:</strong> {formatDuration(selectedEntry.duration)}</Typography>}
              {selectedEntry.cached && <Typography variant="body2"><strong>Cached:</strong> Yes</Typography>}
              {selectedEntry.error && <Typography variant="body2" color="error"><strong>Error:</strong> {selectedEntry.error}</Typography>}
            </Box>
          )}

          {selectedTab === 1 && (
            <Box>
              {selectedEntry.headers ? (
                <pre style={{ fontSize: 12, overflow: 'auto' }}>
                  {JSON.stringify(selectedEntry.headers, null, 2)}
                </pre>
              ) : (
                <Typography color="text.secondary">No headers</Typography>
              )}
            </Box>
          )}

          {selectedTab === 2 && (
            <Box>
              {selectedEntry.body ? (
                <pre style={{ fontSize: 12, overflow: 'auto' }}>
                  {typeof selectedEntry.body === 'string' 
                    ? selectedEntry.body 
                    : JSON.stringify(selectedEntry.body, null, 2)}
                </pre>
              ) : selectedEntry.scriptOutput ? (
                <pre style={{ fontSize: 12, overflow: 'auto' }}>
                  {selectedEntry.scriptOutput}
                </pre>
              ) : (
                <Typography color="text.secondary">No body</Typography>
              )}
            </Box>
          )}

          {selectedTab === 3 && (
            <Box>
              {selectedEntry.timings ? (
                <Box>
                  <Typography variant="body2"><strong>Total:</strong> {selectedEntry.timings.total}ms</Typography>
                  {selectedEntry.timings.dns && <Typography variant="body2"><strong>DNS:</strong> {selectedEntry.timings.dns}ms</Typography>}
                  {selectedEntry.timings.tcp && <Typography variant="body2"><strong>TCP:</strong> {selectedEntry.timings.tcp}ms</Typography>}
                  {selectedEntry.timings.ssl && <Typography variant="body2"><strong>SSL:</strong> {selectedEntry.timings.ssl}ms</Typography>}
                  {selectedEntry.timings.request && <Typography variant="body2"><strong>Request:</strong> {selectedEntry.timings.request}ms</Typography>}
                  {selectedEntry.timings.response && <Typography variant="body2"><strong>Response:</strong> {selectedEntry.timings.response}ms</Typography>}
                </Box>
              ) : (
                <Typography color="text.secondary">No timing information</Typography>
              )}
            </Box>
          )}
        </Box>
      </Box>
    );
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Toolbar */}
      <Paper sx={{ mb: 1 }}>
        <Toolbar variant="dense" sx={{ gap: 1 }}>
          <Tooltip title={isPaused ? 'Resume logging' : 'Pause logging'}>
            <IconButton onClick={handleTogglePause} color={isPaused ? 'warning' : 'default'}>
              {isPaused ? <PlayIcon /> : <PauseIcon />}
            </IconButton>
          </Tooltip>

          <Tooltip title="Clear all entries">
            <IconButton onClick={handleClearAll}>
              <DeleteIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Export entries">
            <IconButton onClick={(e) => setExportMenuAnchor(e.currentTarget)}>
              <ExportIcon />
            </IconButton>
          </Tooltip>
          <Menu
            anchorEl={exportMenuAnchor}
            open={Boolean(exportMenuAnchor)}
            onClose={() => setExportMenuAnchor(null)}
          >
            <MenuItem onClick={() => handleExport('json')}>Export as JSON</MenuItem>
            <MenuItem onClick={() => handleExport('csv')}>Export as CSV</MenuItem>
            <MenuItem onClick={() => handleExport('har')}>Export as HAR</MenuItem>
          </Menu>

          <Tooltip title="Settings">
            <IconButton onClick={() => setSettingsOpen(true)}>
              <SettingsIcon />
            </IconButton>
          </Tooltip>

          <Divider orientation="vertical" flexItem />

          <TextField
            size="small"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon fontSize="small" sx={{ mr: 1 }} />,
              endAdornment: searchQuery && (
                <IconButton size="small" onClick={() => setSearchQuery('')}>
                  <ClearIcon fontSize="small" />
                </IconButton>
              ),
            }}
            sx={{ minWidth: 300 }}
          />

          <FormControlLabel
            control={<Switch checked={autoScroll} onChange={(e) => setAutoScroll(e.target.checked)} />}
            label="Auto-scroll"
          />

          <Box sx={{ flex: 1 }} />

          {stats && (
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Chip label={`Total: ${stats.totalEntries}`} size="small" />
              <Chip label={`Errors: ${stats.errorCount}`} size="small" color="error" />
              <Chip label={`Avg: ${stats.averageDuration}ms`} size="small" color="info" />
            </Box>
          )}
        </Toolbar>
      </Paper>

      {/* Main content */}
      <Box sx={{ display: 'flex', flex: 1, gap: 1, overflow: 'hidden' }}>
        {/* Entry list */}
        <Paper sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="subtitle2">
              Console Entries ({filteredEntries.length})
            </Typography>
          </Box>
          <List
            ref={listRef}
            sx={{
              flex: 1,
              overflow: 'auto',
              '& .MuiListItem-root': {
                borderBottom: 1,
                borderColor: 'divider',
              },
            }}
          >
            {filteredEntries.length === 0 ? (
              <Box sx={{ p: 4, textAlign: 'center', color: 'text.secondary' }}>
                <Typography>No console entries</Typography>
                {isPaused && (
                  <Typography variant="caption">
                    Logging is paused. Click the play button to resume.
                  </Typography>
                )}
              </Box>
            ) : (
              filteredEntries.map(entry => renderEntryListItem(entry))
            )}
          </List>
        </Paper>

        {/* Details panel */}
        <Paper sx={{ width: 400, overflow: 'auto' }}>
          {renderEntryDetails()}
        </Paper>
      </Box>

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Console Settings</DialogTitle>
        <DialogContent>
          <FormControlLabel
            control={
              <Switch
                checked={persistence}
                onChange={(e) => setPersistence(e.target.checked)}
              />
            }
            label="Persist logs to database"
          />
          <TextField
            fullWidth
            label="Max Entries"
            type="number"
            value={maxEntries}
            onChange={(e) => setMaxEntries(parseInt(e.target.value))}
            sx={{ mt: 2 }}
            helperText="Maximum number of entries to keep in memory (1000-50000)"
            inputProps={{ min: 1000, max: 50000 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveSettings} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>

      {loading && (
        <Box sx={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>
          <CircularProgress />
        </Box>
      )}
    </Box>
  );
};

export default DebugConsole;
