import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  Alert,
  Tooltip,
  Card,
  CardContent,
  CardActions,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';

interface MockServer {
  id: string;
  name: string;
  port: number;
  status: 'running' | 'stopped' | 'error';
  routes: MockRoute[];
  logs: MockLog[];
  createdAt: Date;
}

interface MockRoute {
  method: string;
  path: string;
  response: {
    status: number;
    headers?: Record<string, string>;
    body: any;
  };
  delay?: number;
}

interface MockLog {
  id: string;
  timestamp: Date;
  method: string;
  path: string;
  response: {
    status: number;
    body: any;
  };
  duration: number;
}

const MockServerManager: React.FC = () => {
  const [servers, setServers] = useState<MockServer[]>([]);
  const [selectedServer, setSelectedServer] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newServerName, setNewServerName] = useState('');
  const [newServerPort, setNewServerPort] = useState(3000);
  const [selectedCollection, setSelectedCollection] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    loadServers();
  }, []);

  const loadServers = async () => {
    try {
      const result = await (window as any).electronAPI.mockServer.getAll();
      if (result.servers) {
        setServers(result.servers);
      }
    } catch (err) {
      setError('Failed to load servers: ' + (err as Error).message);
    }
  };

  const handleCreateServer = async () => {
    setError(null);
    try {
      const result = await (window as any).electronAPI.mockServer.create({
        name: newServerName,
        port: newServerPort,
        collectionId: selectedCollection,
      });

      if (result.error) {
        setError(result.error);
      } else {
        setCreateDialogOpen(false);
        setNewServerName('');
        setNewServerPort(3000);
        setSelectedCollection('');
        loadServers();
      }
    } catch (err: any) {
      setError(`Failed to create server: ${err.message}`);
    }
  };

  const handleStartServer = async (serverId: string) => {
    setError(null);
    try {
      const result = await (window as any).electronAPI.mockServer.start(serverId);

      if (result.error) {
        setError(result.error);
      } else {
        loadServers();
      }
    } catch (err: any) {
      setError(`Failed to start server: ${err.message}`);
    }
  };

  const handleStopServer = async (serverId: string) => {
    setError(null);
    try {
      const result = await (window as any).electronAPI.mockServer.stop(serverId);

      if (result.error) {
        setError(result.error);
      } else {
        loadServers();
      }
    } catch (err: any) {
      setError(`Failed to stop server: ${err.message}`);
    }
  };

  const handleDeleteServer = async (serverId: string) => {
    if (!confirm('Are you sure you want to delete this mock server?')) {
      return;
    }

    setError(null);
    try {
      await (window as any).electronAPI.mockServer.delete(serverId);
      loadServers();
      if (selectedServer === serverId) {
        setSelectedServer(null);
      }
    } catch (err: any) {
      setError(`Failed to delete server: ${err.message}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'success';
      case 'stopped':
        return 'default';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour12: false });
  };

  const server = servers.find(s => s.id === selectedServer);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Mock Servers</Typography>
          <Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setCreateDialogOpen(true)}
              sx={{ mr: 1 }}
            >
              New Server
            </Button>
            <IconButton onClick={loadServers}>
              <RefreshIcon />
            </IconButton>
          </Box>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ m: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Content */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Server List */}
        <Box sx={{ width: 300, borderRight: 1, borderColor: 'divider', overflow: 'auto' }}>
          {servers.length === 0 ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                No mock servers yet
              </Typography>
            </Box>
          ) : (
            <List>
              {servers.map((srv) => (
                <ListItem
                  key={srv.id}
                  button
                  selected={selectedServer === srv.id}
                  onClick={() => setSelectedServer(srv.id)}
                >
                  <ListItemText
                    primary={srv.name}
                    secondary={`Port: ${srv.port}`}
                  />
                  <Chip
                    label={srv.status}
                    color={getStatusColor(srv.status) as any}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Box>

        {/* Server Details */}
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          {!server ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                No Server Selected
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Select a server from the list or create a new one
              </Typography>
            </Box>
          ) : (
            <Box>
              {/* Server Header */}
              <Paper sx={{ m: 2, p: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="h6">{server.name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      http://localhost:{server.port}
                    </Typography>
                  </Box>
                  <Box>
                    {server.status === 'running' ? (
                      <Button
                        variant="outlined"
                        color="error"
                        startIcon={<StopIcon />}
                        onClick={() => handleStopServer(server.id)}
                        sx={{ mr: 1 }}
                      >
                        Stop
                      </Button>
                    ) : (
                      <Button
                        variant="contained"
                        color="success"
                        startIcon={<PlayIcon />}
                        onClick={() => handleStartServer(server.id)}
                        sx={{ mr: 1 }}
                      >
                        Start
                      </Button>
                    )}
                    <IconButton
                      color="error"
                      onClick={() => handleDeleteServer(server.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
              </Paper>

              {/* Tabs */}
              <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
                <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
                  <Tab label={`Routes (${server.routes.length})`} />
                  <Tab label={`Logs (${server.logs.length})`} />
                </Tabs>
              </Box>

              {/* Routes Tab */}
              {activeTab === 0 && (
                <Box sx={{ p: 2 }}>
                  {server.routes.length === 0 ? (
                    <Typography variant="body2" color="text.secondary">
                      No routes configured
                    </Typography>
                  ) : (
                    <TableContainer component={Paper}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Method</TableCell>
                            <TableCell>Path</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Delay</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {server.routes.map((route, index) => (
                            <TableRow key={index}>
                              <TableCell>
                                <Chip label={route.method} size="small" color="primary" />
                              </TableCell>
                              <TableCell>{route.path}</TableCell>
                              <TableCell>{route.response.status}</TableCell>
                              <TableCell>{route.delay || 0}ms</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  )}
                </Box>
              )}

              {/* Logs Tab */}
              {activeTab === 1 && (
                <Box sx={{ p: 2 }}>
                  {server.logs.length === 0 ? (
                    <Typography variant="body2" color="text.secondary">
                      No requests logged yet
                    </Typography>
                  ) : (
                    <TableContainer component={Paper}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Time</TableCell>
                            <TableCell>Method</TableCell>
                            <TableCell>Path</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Duration</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {server.logs.slice(-50).reverse().map((log) => (
                            <TableRow key={log.id}>
                              <TableCell>{formatTimestamp(log.timestamp)}</TableCell>
                              <TableCell>
                                <Chip label={log.method} size="small" />
                              </TableCell>
                              <TableCell>{log.path}</TableCell>
                              <TableCell>{log.response.status}</TableCell>
                              <TableCell>{log.duration}ms</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  )}
                </Box>
              )}
            </Box>
          )}
        </Box>
      </Box>

      {/* Create Server Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Mock Server</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Server Name"
            value={newServerName}
            onChange={(e) => setNewServerName(e.target.value)}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Port"
            type="number"
            value={newServerPort}
            onChange={(e) => setNewServerPort(parseInt(e.target.value))}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Collection ID (optional)"
            value={selectedCollection}
            onChange={(e) => setSelectedCollection(e.target.value)}
            margin="normal"
            helperText="Leave empty to create server without routes"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateServer}
            variant="contained"
            disabled={!newServerName || !newServerPort}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MockServerManager;
