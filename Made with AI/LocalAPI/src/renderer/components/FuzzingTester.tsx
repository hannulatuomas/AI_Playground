import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  LinearProgress,
  Chip,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Stop as StopIcon,
  ExpandMore as ExpandMoreIcon,
  BugReport as BugIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Timer as TimerIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';

interface FuzzingResult {
  testId: string;
  timestamp: Date;
  targetUrl: string;
  fuzzingType: string;
  totalTests: number;
  duration: number;
  findings: FuzzingFinding[];
  summary: {
    crashes: number;
    errors: number;
    timeouts: number;
    anomalies: number;
  };
}

interface FuzzingFinding {
  id: string;
  testCase: string;
  payload: any;
  severity: 'critical' | 'high' | 'medium' | 'low';
  type: 'crash' | 'error' | 'timeout' | 'anomaly' | 'injection';
  request: string;
  response?: {
    status: number;
    data: string;
    time: number;
  };
  description: string;
}

const FuzzingTester: React.FC = () => {
  const [targetUrl, setTargetUrl] = useState('');
  const [method, setMethod] = useState('POST');
  const [headers, setHeaders] = useState('');
  const [basePayload, setBasePayload] = useState('');
  const [fuzzingType, setFuzzingType] = useState<string>('all');
  const [intensity, setIntensity] = useState<'low' | 'medium' | 'high'>('medium');
  const [maxRequests, setMaxRequests] = useState(200);
  const [delayMs, setDelayMs] = useState(0);
  
  const [testing, setTesting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<FuzzingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fuzzingTypes = [
    { value: 'all', label: 'All Types', description: 'Run all fuzzing tests' },
    { value: 'string', label: 'String Fuzzing', description: 'Special chars, long strings, Unicode' },
    { value: 'number', label: 'Number Fuzzing', description: 'Boundary values, overflow, special numbers' },
    { value: 'format', label: 'Format Fuzzing', description: 'Malformed data, type confusion' },
    { value: 'injection', label: 'Injection Fuzzing', description: 'SQL, XSS, Command injection' },
    { value: 'boundary', label: 'Boundary Fuzzing', description: 'Array/string boundaries' },
    { value: 'encoding', label: 'Encoding Fuzzing', description: 'URL, HTML, Base64 encoding' },
    { value: 'bomb', label: 'Bomb Testing', description: 'XML bomb, JSON bomb, large payloads' },
  ];

  const handleStartTest = async () => {
    if (!targetUrl) {
      setError('Please enter a target URL');
      return;
    }

    setTesting(true);
    setProgress(0);
    setError(null);
    setResult(null);

    try {
      // Parse headers
      const headersObj: Record<string, string> = {};
      if (headers) {
        headers.split('\n').forEach(line => {
          const [key, value] = line.split(':').map(s => s.trim());
          if (key && value) {
            headersObj[key] = value;
          }
        });
      }

      // Parse base payload
      let parsedPayload;
      if (basePayload) {
        try {
          parsedPayload = JSON.parse(basePayload);
        } catch {
          parsedPayload = basePayload;
        }
      }

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 5, 90));
      }, 500);

      const testResult = await (window as any).electronAPI.fuzzing.run({
        targetUrl,
        method,
        headers: headersObj,
        basePayload: parsedPayload,
        fuzzingType,
        intensity,
        maxRequests,
        delayMs,
      });

      clearInterval(progressInterval);
      setProgress(100);
      setResult(testResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fuzzing test failed');
    } finally {
      setTesting(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'crash': return <ErrorIcon />;
      case 'error': return <WarningIcon />;
      case 'timeout': return <TimerIcon />;
      case 'anomaly': return <InfoIcon />;
      case 'injection': return <BugIcon />;
      default: return <InfoIcon />;
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <BugIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Fuzzing & Bomb Testing
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Test Configuration
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Target URL"
              value={targetUrl}
              onChange={(e) => setTargetUrl(e.target.value)}
              placeholder="https://example.com/api/endpoint"
              disabled={testing}
            />
          </Grid>

          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>HTTP Method</InputLabel>
              <Select
                value={method}
                label="HTTP Method"
                onChange={(e) => setMethod(e.target.value)}
                disabled={testing}
              >
                <MenuItem value="GET">GET</MenuItem>
                <MenuItem value="POST">POST</MenuItem>
                <MenuItem value="PUT">PUT</MenuItem>
                <MenuItem value="DELETE">DELETE</MenuItem>
                <MenuItem value="PATCH">PATCH</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Fuzzing Type</InputLabel>
              <Select
                value={fuzzingType}
                label="Fuzzing Type"
                onChange={(e) => setFuzzingType(e.target.value)}
                disabled={testing}
              >
                {fuzzingTypes.map(type => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {fuzzingTypes.find(t => t.value === fuzzingType)?.description}
            </Typography>
          </Grid>

          <Grid item xs={4}>
            <Typography variant="subtitle2" gutterBottom>
              Intensity
            </Typography>
            <ToggleButtonGroup
              value={intensity}
              exclusive
              onChange={(e, val) => val && setIntensity(val)}
              disabled={testing}
              fullWidth
            >
              <ToggleButton value="low">Low (50)</ToggleButton>
              <ToggleButton value="medium">Medium (200)</ToggleButton>
              <ToggleButton value="high">High (500)</ToggleButton>
            </ToggleButtonGroup>
          </Grid>

          <Grid item xs={4}>
            <TextField
              fullWidth
              type="number"
              label="Max Requests"
              value={maxRequests}
              onChange={(e) => setMaxRequests(parseInt(e.target.value))}
              disabled={testing}
            />
          </Grid>

          <Grid item xs={4}>
            <TextField
              fullWidth
              type="number"
              label="Delay (ms)"
              value={delayMs}
              onChange={(e) => setDelayMs(parseInt(e.target.value))}
              disabled={testing}
              helperText="Delay between requests"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Headers (one per line, format: Key: Value)"
              value={headers}
              onChange={(e) => setHeaders(e.target.value)}
              placeholder="Content-Type: application/json&#10;Authorization: Bearer token"
              disabled={testing}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Base Payload (optional)"
              value={basePayload}
              onChange={(e) => setBasePayload(e.target.value)}
              placeholder='{"key": "value"}'
              disabled={testing}
              helperText="Base payload to fuzz (will be modified during testing)"
            />
          </Grid>
        </Grid>

        <Box sx={{ mt: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={testing ? <StopIcon /> : <StartIcon />}
            onClick={handleStartTest}
            disabled={testing || !targetUrl}
          >
            {testing ? 'Testing...' : 'Start Fuzzing'}
          </Button>
          {testing && (
            <Box sx={{ flex: 1 }}>
              <LinearProgress variant="determinate" value={progress} />
              <Typography variant="caption" sx={{ mt: 0.5 }}>
                {progress}% Complete
              </Typography>
            </Box>
          )}
        </Box>

        <Alert severity="warning" sx={{ mt: 2 }}>
          <strong>Warning:</strong> Fuzzing can generate high load and potentially crash the target server. 
          Only test systems you have permission to test.
        </Alert>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {result && (
        <>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Test Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2">
                  <strong>Target:</strong> {result.targetUrl}
                </Typography>
                <Typography variant="body2">
                  <strong>Type:</strong> {result.fuzzingType}
                </Typography>
                <Typography variant="body2">
                  <strong>Total Tests:</strong> {result.totalTests}
                </Typography>
                <Typography variant="body2">
                  <strong>Duration:</strong> {(result.duration / 1000).toFixed(2)}s
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip
                    icon={<ErrorIcon />}
                    label={`Crashes: ${result.summary.crashes}`}
                    color="error"
                    size="small"
                  />
                  <Chip
                    icon={<WarningIcon />}
                    label={`Errors: ${result.summary.errors}`}
                    color="error"
                    size="small"
                  />
                  <Chip
                    icon={<TimerIcon />}
                    label={`Timeouts: ${result.summary.timeouts}`}
                    color="warning"
                    size="small"
                  />
                  <Chip
                    icon={<InfoIcon />}
                    label={`Anomalies: ${result.summary.anomalies}`}
                    color="info"
                    size="small"
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>

          <Typography variant="h6" gutterBottom>
            Findings ({result.findings.length})
          </Typography>

          {result.findings.length === 0 ? (
            <Alert severity="success">
              No vulnerabilities detected! The target handled all fuzzing tests correctly.
            </Alert>
          ) : (
            result.findings.map((finding) => (
              <Accordion key={finding.id}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                    {getTypeIcon(finding.type)}
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle1">
                        {finding.testCase}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                        <Chip
                          label={finding.severity.toUpperCase()}
                          color={getSeverityColor(finding.severity) as any}
                          size="small"
                        />
                        <Chip
                          label={finding.type}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box>
                    <Typography variant="body2" paragraph>
                      <strong>Description:</strong> {finding.description}
                    </Typography>

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="subtitle2" gutterBottom>
                      Payload:
                    </Typography>
                    <Paper variant="outlined" sx={{ p: 1, bgcolor: 'grey.50', mb: 2, position: 'relative' }}>
                      <code style={{ fontSize: '0.875rem', wordBreak: 'break-all' }}>
                        {JSON.stringify(finding.payload, null, 2)}
                      </code>
                      <Tooltip title="Copy">
                        <IconButton
                          size="small"
                          sx={{ position: 'absolute', top: 4, right: 4 }}
                          onClick={() => copyToClipboard(JSON.stringify(finding.payload, null, 2))}
                        >
                          <CopyIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Paper>

                    {finding.response && (
                      <>
                        <Typography variant="subtitle2" gutterBottom>
                          Response:
                        </Typography>
                        <Paper variant="outlined" sx={{ p: 1, bgcolor: 'grey.50', mb: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            Status: {finding.response.status} | Time: {finding.response.time}ms
                          </Typography>
                        </Paper>
                        {finding.response.data && (
                          <Paper variant="outlined" sx={{ p: 1, bgcolor: 'grey.50', maxHeight: 200, overflow: 'auto' }}>
                            <code style={{ fontSize: '0.875rem', whiteSpace: 'pre-wrap' }}>
                              {finding.response.data}
                            </code>
                          </Paper>
                        )}
                      </>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))
          )}
        </>
      )}
    </Box>
  );
};

export default FuzzingTester;
