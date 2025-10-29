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
  Card,
  CardContent,
  Grid,
  Alert,
  Tabs,
  Tab,
  Switch,
  FormControlLabel,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  PlayCircle as PlayCircleIcon,
} from '@mui/icons-material';

interface CronJob {
  id: string;
  name: string;
  schedule: string;
  requestName: string;
  enabled: boolean;
  lastRun?: Date;
  nextRun?: Date;
  runCount: number;
  successCount: number;
  failureCount: number;
}

interface CronLog {
  id: string;
  jobId: string;
  jobName: string;
  timestamp: Date;
  status: 'success' | 'failure';
  response?: {
    status: number;
    time: number;
  };
  error?: string;
}

const MonitoringDashboard: React.FC = () => {
  const [jobs, setJobs] = useState<CronJob[]>([]);
  const [logs, setLogs] = useState<CronLog[]>([]);
  const [selectedJob, setSelectedJob] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [jobName, setJobName] = useState('');
  const [schedule, setSchedule] = useState('*/5 * * * *');
  const [requestId, setRequestId] = useState('');
  const [enabled, setEnabled] = useState(true);

  // Statistics
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    loadJobs();
    loadLogs();
    loadStats();
    const interval = setInterval(() => {
      loadJobs();
      loadLogs();
      loadStats();
    }, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadJobs = async () => {
    try {
      const result = await (window as any).electron.invoke('cron:getAll');
      if (result.jobs) {
        setJobs(result.jobs);
      }
    } catch (err: any) {
      // Ignore polling errors
    }
  };

  const loadLogs = async () => {
    try {
      const result = await (window as any).electron.invoke('cron:getAllLogs', {
        limit: 100,
      });
      if (result.logs) {
        setLogs(result.logs);
      }
    } catch (err: any) {
      // Ignore polling errors
    }
  };

  const loadStats = async () => {
    try {
      const result = await (window as any).electron.invoke('cron:getStats');
      if (result.stats) {
        setStats(result.stats);
      }
    } catch (err: any) {
      // Ignore polling errors
    }
  };

  const handleCreateJob = async () => {
    setError(null);
    try {
      const result = await (window as any).electron.invoke('cron:create', {
        name: jobName,
        schedule,
        requestId,
        enabled,
      });

      if (result.error) {
        setError(result.error);
      } else {
        setCreateDialogOpen(false);
        setJobName('');
        setSchedule('*/5 * * * *');
        setRequestId('');
        loadJobs();
      }
    } catch (err: any) {
      setError(`Failed to create job: ${err.message}`);
    }
  };

  const handleToggleJob = async (jobId: string, currentlyEnabled: boolean) => {
    try {
      if (currentlyEnabled) {
        await (window as any).electron.invoke('cron:stop', { jobId });
      } else {
        await (window as any).electron.invoke('cron:start', { jobId });
      }
      loadJobs();
    } catch (err: any) {
      setError(`Failed to toggle job: ${err.message}`);
    }
  };

  const handleRunNow = async (jobId: string) => {
    try {
      await (window as any).electron.invoke('cron:runNow', { jobId });
      setTimeout(() => {
        loadJobs();
        loadLogs();
      }, 1000);
    } catch (err: any) {
      setError(`Failed to run job: ${err.message}`);
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    if (!confirm('Delete this monitoring job?')) return;

    try {
      await (window as any).electron.invoke('cron:delete', { jobId });
      loadJobs();
      if (selectedJob === jobId) {
        setSelectedJob(null);
      }
    } catch (err: any) {
      setError(`Failed to delete: ${err.message}`);
    }
  };

  const getStatusColor = (status: string) => {
    return status === 'success' ? 'success' : 'error';
  };

  const formatTimestamp = (timestamp: Date) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const cronExamples = [
    { value: '* * * * *', label: 'Every minute' },
    { value: '*/5 * * * *', label: 'Every 5 minutes' },
    { value: '0 * * * *', label: 'Every hour' },
    { value: '0 */6 * * *', label: 'Every 6 hours' },
    { value: '0 0 * * *', label: 'Daily at midnight' },
    { value: '0 9 * * *', label: 'Daily at 9:00 AM' },
    { value: '0 9 * * 1-5', label: 'Weekdays at 9:00 AM' },
  ];

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Monitoring Dashboard</Typography>
          <Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setCreateDialogOpen(true)}
              sx={{ mr: 1 }}
            >
              New Monitor
            </Button>
            <IconButton onClick={() => { loadJobs(); loadLogs(); loadStats(); }}>
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

      {/* Statistics */}
      {stats && (
        <Paper sx={{ m: 2, p: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 1 }}>
                  <Typography variant="h4">{stats.totalJobs}</Typography>
                  <Typography variant="caption">Total Jobs</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 1 }}>
                  <Typography variant="h4" color="success.main">
                    {stats.activeJobs}
                  </Typography>
                  <Typography variant="caption">Active</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 1 }}>
                  <Typography variant="h4">{stats.totalRuns}</Typography>
                  <Typography variant="caption">Total Runs</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 1 }}>
                  <Typography variant="h4">
                    {stats.overallSuccessRate.toFixed(1)}%
                  </Typography>
                  <Typography variant="caption">Success Rate</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
          <Tab label={`Jobs (${jobs.length})`} />
          <Tab label={`Logs (${logs.length})`} />
        </Tabs>
      </Box>

      {/* Jobs Tab */}
      {activeTab === 0 && (
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {jobs.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <ScheduleIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                No Monitoring Jobs
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Create a monitoring job to schedule API checks
              </Typography>
            </Box>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Status</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Schedule</TableCell>
                    <TableCell>Request</TableCell>
                    <TableCell>Runs</TableCell>
                    <TableCell>Success Rate</TableCell>
                    <TableCell>Last Run</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {jobs.map((job) => {
                    const successRate = job.runCount > 0 
                      ? ((job.successCount / job.runCount) * 100).toFixed(1) 
                      : '0';

                    return (
                      <TableRow key={job.id}>
                        <TableCell>
                          <Chip
                            label={job.enabled ? 'Active' : 'Inactive'}
                            color={job.enabled ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{job.name}</TableCell>
                        <TableCell>
                          <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                            {job.schedule}
                          </Typography>
                        </TableCell>
                        <TableCell>{job.requestName}</TableCell>
                        <TableCell>{job.runCount}</TableCell>
                        <TableCell>
                          <Typography
                            variant="body2"
                            color={parseFloat(successRate) >= 90 ? 'success.main' : 'error.main'}
                          >
                            {successRate}%
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {job.lastRun ? formatTimestamp(job.lastRun) : '-'}
                        </TableCell>
                        <TableCell>
                          <IconButton
                            size="small"
                            onClick={() => handleToggleJob(job.id, job.enabled)}
                            color={job.enabled ? 'error' : 'success'}
                          >
                            {job.enabled ? <StopIcon /> : <PlayIcon />}
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => handleRunNow(job.id)}
                            color="primary"
                          >
                            <PlayCircleIcon />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteJob(job.id)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      )}

      {/* Logs Tab */}
      {activeTab === 1 && (
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {logs.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
              No logs yet
            </Typography>
          ) : (
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Time</TableCell>
                    <TableCell>Job</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Response Code</TableCell>
                    <TableCell>Time (ms)</TableCell>
                    <TableCell>Error</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {logs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell>{formatTimestamp(log.timestamp)}</TableCell>
                      <TableCell>{log.jobName}</TableCell>
                      <TableCell>
                        {log.status === 'success' ? (
                          <CheckCircleIcon color="success" fontSize="small" />
                        ) : (
                          <ErrorIcon color="error" fontSize="small" />
                        )}
                      </TableCell>
                      <TableCell>{log.response?.status || '-'}</TableCell>
                      <TableCell>{log.response?.time || '-'}</TableCell>
                      <TableCell>
                        {log.error && (
                          <Typography variant="caption" color="error">
                            {log.error}
                          </Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      )}

      {/* Create Job Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Monitoring Job</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Job Name"
            value={jobName}
            onChange={(e) => setJobName(e.target.value)}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Schedule</InputLabel>
            <Select
              value={schedule}
              label="Schedule"
              onChange={(e) => setSchedule(e.target.value)}
            >
              {cronExamples.map((example) => (
                <MenuItem key={example.value} value={example.value}>
                  {example.label} ({example.value})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Custom Cron Expression"
            value={schedule}
            onChange={(e) => setSchedule(e.target.value)}
            margin="normal"
            helperText="Format: minute hour day month weekday"
          />
          <TextField
            fullWidth
            label="Request ID"
            value={requestId}
            onChange={(e) => setRequestId(e.target.value)}
            margin="normal"
            helperText="ID of request to monitor"
          />
          <FormControlLabel
            control={
              <Switch
                checked={enabled}
                onChange={(e) => setEnabled(e.target.checked)}
              />
            }
            label="Start immediately"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateJob}
            variant="contained"
            disabled={!jobName || !schedule || !requestId}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MonitoringDashboard;
