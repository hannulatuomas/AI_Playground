import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  LinearProgress,
  Chip,
  Alert,
  Card,
  CardContent,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Stop as StopIcon,
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CheckCircle as CheckIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

interface ZAPAlert {
  id: string;
  alert: string;
  risk: 'High' | 'Medium' | 'Low' | 'Informational';
  confidence: 'High' | 'Medium' | 'Low';
  description: string;
  solution: string;
  reference: string;
  cweid: string;
  wascid: string;
  url: string;
  method?: string;
  param?: string;
  attack?: string;
  evidence?: string;
}

interface ZAPScanResult {
  scanId: string;
  targetUrl: string;
  scanType: string;
  status: string;
  progress: number;
  alerts: ZAPAlert[];
  summary: {
    total: number;
    high: number;
    medium: number;
    low: number;
    informational: number;
  };
  duration?: number;
}

const ZAPProxy: React.FC = () => {
  const [zapHost, setZapHost] = useState('localhost');
  const [zapPort, setZapPort] = useState(8080);
  const [zapApiKey, setZapApiKey] = useState('');
  const [connected, setConnected] = useState(false);
  const [zapVersion, setZapVersion] = useState('');

  const [targetUrl, setTargetUrl] = useState('');
  const [scanType, setScanType] = useState<'spider' | 'active' | 'full'>('full');
  const [recurse, setRecurse] = useState(true);
  const [maxChildren, setMaxChildren] = useState(10);

  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<ZAPScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Try to load saved ZAP config
    const savedConfig = localStorage.getItem('zap-config');
    if (savedConfig) {
      const config = JSON.parse(savedConfig);
      setZapHost(config.host || 'localhost');
      setZapPort(config.port || 8080);
      setZapApiKey(config.apiKey || '');
    }
  }, []);

  const handleConnect = async () => {
    if (!zapApiKey) {
      setError('Please enter ZAP API Key');
      return;
    }

    try {
      const isConnected = await (window as any).electronAPI.zap.checkConnection({
        host: zapHost,
        port: zapPort,
        apiKey: zapApiKey,
      });

      if (isConnected) {
        setConnected(true);
        setError(null);

        // Save config
        localStorage.setItem('zap-config', JSON.stringify({
          host: zapHost,
          port: zapPort,
          apiKey: zapApiKey,
        }));

        // Get version
        const version = await (window as any).electronAPI.zap.getVersion();
        setZapVersion(version);
      } else {
        setError('Failed to connect to ZAP. Make sure ZAP is running.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed');
    }
  };

  const handleStartScan = async () => {
    if (!targetUrl) {
      setError('Please enter a target URL');
      return;
    }

    if (!connected) {
      setError('Please connect to ZAP first');
      return;
    }

    setScanning(true);
    setProgress(0);
    setError(null);
    setResult(null);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 5, 90));
      }, 2000);

      const scanResult = await (window as any).electronAPI.zap.runScan({
        targetUrl,
        scanType,
        recurse,
        maxChildren,
      });

      clearInterval(progressInterval);
      setProgress(100);
      setResult(scanResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scan failed');
    } finally {
      setScanning(false);
    }
  };

  const handleClearAlerts = async () => {
    try {
      await (window as any).electronAPI.zap.clearAlerts();
      setResult(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear alerts');
    }
  };

  const handleExportReport = async (format: 'html' | 'xml') => {
    try {
      const report = format === 'html'
        ? await (window as any).electronAPI.zap.generateHtmlReport()
        : await (window as any).electronAPI.zap.generateXmlReport();

      // Create download
      const blob = new Blob([report], { type: format === 'html' ? 'text/html' : 'text/xml' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `zap-report.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export report');
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'High': return 'error';
      case 'Medium': return 'warning';
      case 'Low': return 'info';
      default: return 'default';
    }
  };

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'High': return <ErrorIcon />;
      case 'Medium': return <WarningIcon />;
      case 'Low': return <InfoIcon />;
      default: return <InfoIcon />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        OWASP ZAP Proxy Integration
      </Typography>

      {/* Connection Configuration */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          ZAP Connection
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="ZAP Host"
              value={zapHost}
              onChange={(e) => setZapHost(e.target.value)}
              disabled={connected}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              type="number"
              label="ZAP Port"
              value={zapPort}
              onChange={(e) => setZapPort(parseInt(e.target.value))}
              disabled={connected}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="API Key"
              value={zapApiKey}
              onChange={(e) => setZapApiKey(e.target.value)}
              disabled={connected}
              type="password"
            />
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Button
                variant="contained"
                onClick={handleConnect}
                disabled={connected}
                startIcon={<SecurityIcon />}
              >
                {connected ? 'Connected' : 'Connect to ZAP'}
              </Button>

              {connected && (
                <>
                  <Chip
                    icon={<CheckIcon />}
                    label={`Connected - ZAP ${zapVersion}`}
                    color="success"
                  />
                  <Button
                    size="small"
                    onClick={() => {
                      setConnected(false);
                      setZapVersion('');
                    }}
                  >
                    Disconnect
                  </Button>
                </>
              )}
            </Box>
          </Grid>
        </Grid>

        <Alert severity="info" sx={{ mt: 2 }}>
          <strong>Note:</strong> Make sure OWASP ZAP is running and API is enabled. 
          You can find the API key in ZAP: Tools → Options → API
        </Alert>
      </Paper>

      {/* Scan Configuration */}
      {connected && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Scan Configuration
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Target URL"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                placeholder="https://example.com"
                disabled={scanning}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Scan Type</InputLabel>
                <Select
                  value={scanType}
                  label="Scan Type"
                  onChange={(e) => setScanType(e.target.value as any)}
                  disabled={scanning}
                >
                  <MenuItem value="spider">Spider Only (Crawl)</MenuItem>
                  <MenuItem value="active">Active Scan Only (Attack)</MenuItem>
                  <MenuItem value="full">Full Scan (Spider + Active)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Max Children"
                value={maxChildren}
                onChange={(e) => setMaxChildren(parseInt(e.target.value))}
                disabled={scanning}
                helperText="Maximum number of child nodes to scan"
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={recurse}
                    onChange={(e) => setRecurse(e.target.checked)}
                    disabled={scanning}
                  />
                }
                label="Recursive Scan"
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                size="large"
                color="primary"
                startIcon={scanning ? <StopIcon /> : <StartIcon />}
                onClick={handleStartScan}
                disabled={scanning || !targetUrl}
                fullWidth
              >
                {scanning ? 'Scanning...' : 'Start ZAP Scan'}
              </Button>
            </Grid>

            {scanning && (
              <Grid item xs={12}>
                <LinearProgress variant="determinate" value={progress} />
                <Typography variant="caption" sx={{ mt: 1 }}>
                  Progress: {progress}%
                </Typography>
              </Grid>
            )}
          </Grid>

          <Alert severity="warning" sx={{ mt: 2 }}>
            <strong>Warning:</strong> Active scanning will attack the target. Only scan systems you have permission to test.
          </Alert>
        </Paper>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {result && (
        <>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Scan Results
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  startIcon={<DownloadIcon />}
                  onClick={() => handleExportReport('html')}
                  size="small"
                >
                  HTML Report
                </Button>
                <Button
                  startIcon={<DownloadIcon />}
                  onClick={() => handleExportReport('xml')}
                  size="small"
                >
                  XML Report
                </Button>
                <Button
                  startIcon={<DeleteIcon />}
                  onClick={handleClearAlerts}
                  size="small"
                  color="error"
                >
                  Clear Alerts
                </Button>
              </Box>
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2">
                  <strong>Target:</strong> {result.targetUrl}
                </Typography>
                <Typography variant="body2">
                  <strong>Scan Type:</strong> {result.scanType}
                </Typography>
                {result.duration && (
                  <Typography variant="body2">
                    <strong>Duration:</strong> {(result.duration / 1000).toFixed(2)}s
                  </Typography>
                )}
              </Grid>
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip
                    icon={<ErrorIcon />}
                    label={`High: ${result.summary.high}`}
                    color="error"
                  />
                  <Chip
                    icon={<WarningIcon />}
                    label={`Medium: ${result.summary.medium}`}
                    color="warning"
                  />
                  <Chip
                    icon={<InfoIcon />}
                    label={`Low: ${result.summary.low}`}
                    color="info"
                  />
                  <Chip
                    label={`Info: ${result.summary.informational}`}
                    color="default"
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>

          <Typography variant="h6" gutterBottom>
            Alerts ({result.alerts.length})
          </Typography>

          {result.alerts.length === 0 ? (
            <Alert severity="success" icon={<CheckIcon />}>
              No security alerts found! The target appears to be secure.
            </Alert>
          ) : (
            result.alerts.map((alert) => (
              <Accordion key={alert.id}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                    {getRiskIcon(alert.risk)}
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle1">
                        {alert.alert}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                        <Chip
                          label={alert.risk}
                          color={getRiskColor(alert.risk) as any}
                          size="small"
                        />
                        <Chip
                          label={`Confidence: ${alert.confidence}`}
                          size="small"
                          variant="outlined"
                        />
                        {alert.cweid && (
                          <Chip label={`CWE-${alert.cweid}`} size="small" variant="outlined" />
                        )}
                      </Box>
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box>
                    <Typography variant="body2" paragraph>
                      <strong>Description:</strong> {alert.description}
                    </Typography>

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="body2" paragraph>
                      <strong>URL:</strong> {alert.url}
                    </Typography>

                    {alert.method && (
                      <Typography variant="body2" paragraph>
                        <strong>Method:</strong> {alert.method}
                      </Typography>
                    )}

                    {alert.param && (
                      <Typography variant="body2" paragraph>
                        <strong>Parameter:</strong> {alert.param}
                      </Typography>
                    )}

                    {alert.attack && (
                      <Typography variant="body2" paragraph>
                        <strong>Attack:</strong> {alert.attack}
                      </Typography>
                    )}

                    {alert.evidence && (
                      <Typography variant="body2" paragraph>
                        <strong>Evidence:</strong> {alert.evidence}
                      </Typography>
                    )}

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="subtitle2" gutterBottom>
                      Solution:
                    </Typography>
                    <Typography variant="body2" paragraph>
                      {alert.solution}
                    </Typography>

                    {alert.reference && (
                      <>
                        <Typography variant="subtitle2" gutterBottom>
                          References:
                        </Typography>
                        <Typography variant="body2" paragraph sx={{ whiteSpace: 'pre-wrap' }}>
                          {alert.reference}
                        </Typography>
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

export default ZAPProxy;
