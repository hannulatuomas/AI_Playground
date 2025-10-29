import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
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
  TextField,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
  Grid,
  Alert,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Remove as RemoveIcon,
} from '@mui/icons-material';

interface BatchRequest {
  id: string;
  name: string;
  method: string;
  url: string;
}

interface BatchResult {
  id: string;
  requestName: string;
  status: 'success' | 'failed' | 'skipped';
  response?: {
    status: number;
    time: number;
  };
  error?: string;
}

interface BatchRun {
  id: string;
  name: string;
  startTime: Date;
  endTime?: Date;
  duration?: number;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  results: BatchResult[];
  totalRequests: number;
  successCount: number;
  failedCount: number;
  skippedCount: number;
}

const BatchRunner: React.FC = () => {
  const [runs, setRuns] = useState<BatchRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [batchName, setBatchName] = useState('');
  const [collectionId, setCollectionId] = useState('');
  const [delay, setDelay] = useState(0);
  const [stopOnError, setStopOnError] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRuns();
    const interval = setInterval(loadRuns, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, []);

  const loadRuns = async () => {
    try {
      const result = await (window as any).electron.invoke('batch:getAll');
      if (result.runs) {
        setRuns(result.runs);
      }
    } catch (err: any) {
      // Ignore polling errors
    }
  };

  const handleCreateBatch = async () => {
    setError(null);
    try {
      const result = await (window as any).electron.invoke('batch:execute', {
        name: batchName,
        collectionId,
        delay,
        stopOnError,
      });

      if (result.error) {
        setError(result.error);
      } else {
        setCreateDialogOpen(false);
        setBatchName('');
        setCollectionId('');
        setDelay(0);
        loadRuns();
      }
    } catch (err: any) {
      setError(`Failed to create batch: ${err.message}`);
    }
  };

  const handleCancelRun = async (runId: string) => {
    try {
      await (window as any).electron.invoke('batch:cancel', { runId });
      loadRuns();
    } catch (err: any) {
      setError(`Failed to cancel: ${err.message}`);
    }
  };

  const handleDeleteRun = async (runId: string) => {
    if (!confirm('Delete this batch run?')) return;

    try {
      await (window as any).electron.invoke('batch:delete', { runId });
      loadRuns();
      if (selectedRun === runId) {
        setSelectedRun(null);
      }
    } catch (err: any) {
      setError(`Failed to delete: ${err.message}`);
    }
  };

  const handleExport = async (runId: string, format: 'json' | 'csv') => {
    try {
      const result = await (window as any).electron.invoke('batch:export', {
        runId,
        format,
      });

      if (result.data) {
        const blob = new Blob([result.data], {
          type: format === 'json' ? 'application/json' : 'text/csv',
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `batch-run-${runId}.${format}`;
        a.click();
      }
    } catch (err: any) {
      setError(`Export failed: ${err.message}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'info';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'cancelled':
        return 'default';
      default:
        return 'default';
    }
  };

  const getResultIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'skipped':
        return <RemoveIcon color="disabled" />;
      default:
        return null;
    }
  };

  const run = runs.find(r => r.id === selectedRun);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Batch Runner</Typography>
          <Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setCreateDialogOpen(true)}
              sx={{ mr: 1 }}
            >
              New Batch
            </Button>
            <IconButton onClick={loadRuns}>
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
        {/* Run List */}
        <Box sx={{ width: 300, borderRight: 1, borderColor: 'divider', overflow: 'auto' }}>
          {runs.length === 0 ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                No batch runs yet
              </Typography>
            </Box>
          ) : (
            <List>
              {runs.map((r) => (
                <ListItem
                  key={r.id}
                  button
                  selected={selectedRun === r.id}
                  onClick={() => setSelectedRun(r.id)}
                >
                  <ListItemText
                    primary={r.name}
                    secondary={`${r.successCount}/${r.totalRequests} succeeded`}
                  />
                  <Chip
                    label={r.status}
                    color={getStatusColor(r.status) as any}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Box>

        {/* Run Details */}
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          {!run ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                No Run Selected
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Select a batch run from the list or create a new one
              </Typography>
            </Box>
          ) : (
            <Box sx={{ p: 2 }}>
              {/* Run Header */}
              <Paper sx={{ p: 2, mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Box>
                    <Typography variant="h6">{run.name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Started: {new Date(run.startTime).toLocaleString()}
                    </Typography>
                    {run.duration && (
                      <Typography variant="body2" color="text.secondary">
                        Duration: {run.duration}ms
                      </Typography>
                    )}
                  </Box>
                  <Box>
                    {run.status === 'running' && (
                      <Button
                        variant="outlined"
                        color="error"
                        startIcon={<StopIcon />}
                        onClick={() => handleCancelRun(run.id)}
                        sx={{ mr: 1 }}
                      >
                        Cancel
                      </Button>
                    )}
                    <Button
                      size="small"
                      startIcon={<DownloadIcon />}
                      onClick={() => handleExport(run.id, 'json')}
                      sx={{ mr: 1 }}
                    >
                      JSON
                    </Button>
                    <Button
                      size="small"
                      startIcon={<DownloadIcon />}
                      onClick={() => handleExport(run.id, 'csv')}
                      sx={{ mr: 1 }}
                    >
                      CSV
                    </Button>
                    <IconButton
                      color="error"
                      onClick={() => handleDeleteRun(run.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>

                {/* Progress */}
                {run.status === 'running' && (
                  <LinearProgress sx={{ mb: 2 }} />
                )}

                {/* Statistics */}
                <Grid container spacing={2}>
                  <Grid item xs={3}>
                    <Card variant="outlined">
                      <CardContent sx={{ textAlign: 'center', py: 1 }}>
                        <Typography variant="h4">{run.totalRequests}</Typography>
                        <Typography variant="caption">Total</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={3}>
                    <Card variant="outlined">
                      <CardContent sx={{ textAlign: 'center', py: 1 }}>
                        <Typography variant="h4" color="success.main">
                          {run.successCount}
                        </Typography>
                        <Typography variant="caption">Success</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={3}>
                    <Card variant="outlined">
                      <CardContent sx={{ textAlign: 'center', py: 1 }}>
                        <Typography variant="h4" color="error.main">
                          {run.failedCount}
                        </Typography>
                        <Typography variant="caption">Failed</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={3}>
                    <Card variant="outlined">
                      <CardContent sx={{ textAlign: 'center', py: 1 }}>
                        <Typography variant="h4">{run.skippedCount}</Typography>
                        <Typography variant="caption">Skipped</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </Paper>

              {/* Results Table */}
              <Typography variant="h6" gutterBottom>
                Request Results
              </Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Status</TableCell>
                      <TableCell>Request</TableCell>
                      <TableCell>Response Code</TableCell>
                      <TableCell>Time (ms)</TableCell>
                      <TableCell>Error</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {run.results.map((result) => (
                      <TableRow key={result.id}>
                        <TableCell>{getResultIcon(result.status)}</TableCell>
                        <TableCell>{result.requestName}</TableCell>
                        <TableCell>{result.response?.status || '-'}</TableCell>
                        <TableCell>{result.response?.time || '-'}</TableCell>
                        <TableCell>
                          {result.error && (
                            <Typography variant="caption" color="error">
                              {result.error}
                            </Typography>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </Box>
      </Box>

      {/* Create Batch Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Batch Run</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Batch Name"
            value={batchName}
            onChange={(e) => setBatchName(e.target.value)}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Collection ID"
            value={collectionId}
            onChange={(e) => setCollectionId(e.target.value)}
            margin="normal"
            helperText="ID of collection to run"
          />
          <TextField
            fullWidth
            label="Delay Between Requests (ms)"
            type="number"
            value={delay}
            onChange={(e) => setDelay(parseInt(e.target.value) || 0)}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateBatch}
            variant="contained"
            disabled={!batchName || !collectionId}
          >
            Run Batch
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BatchRunner;
