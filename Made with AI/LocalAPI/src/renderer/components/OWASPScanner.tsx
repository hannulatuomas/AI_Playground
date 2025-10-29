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
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow as ScanIcon,
  Stop as StopIcon,
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';

interface OWASPScanResult {
  scanId: string;
  timestamp: Date;
  targetUrl: string;
  duration: number;
  summary: {
    total: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  findings: OWASPFinding[];
  recommendations: string[];
}

interface OWASPFinding {
  id: string;
  category: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  confidence: 'confirmed' | 'firm' | 'tentative';
  evidence: {
    request?: string;
    response?: string;
    payload?: string;
    location?: string;
  };
  remediation: string;
  references: string[];
  cwe?: string;
  cvss?: number;
}

const OWASPScanner: React.FC = () => {
  const [targetUrl, setTargetUrl] = useState('');
  const [method, setMethod] = useState('GET');
  const [headers, setHeaders] = useState('');
  const [body, setBody] = useState('');
  const [depth, setDepth] = useState<'quick' | 'standard' | 'thorough'>('standard');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([
    'A01', 'A02', 'A03', 'A04', 'A05', 'A06', 'A07', 'A08', 'A09', 'A10'
  ]);
  
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<OWASPScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const categories = [
    { id: 'A01', name: 'Broken Access Control' },
    { id: 'A02', name: 'Cryptographic Failures' },
    { id: 'A03', name: 'Injection' },
    { id: 'A04', name: 'Insecure Design' },
    { id: 'A05', name: 'Security Misconfiguration' },
    { id: 'A06', name: 'Vulnerable Components' },
    { id: 'A07', name: 'Authentication Failures' },
    { id: 'A08', name: 'Integrity Failures' },
    { id: 'A09', name: 'Logging Failures' },
    { id: 'A10', name: 'SSRF' },
  ];

  const handleCategoryToggle = (categoryId: string) => {
    setSelectedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  const handleStartScan = async () => {
    if (!targetUrl) {
      setError('Please enter a target URL');
      return;
    }

    setScanning(true);
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

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 1000);

      const scanResult = await (window as any).electronAPI.owasp.scan({
        targetUrl,
        method,
        headers: headersObj,
        body: body || undefined,
        testCategories: selectedCategories,
        depth,
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

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      case 'info': return 'default';
      default: return 'default';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <ErrorIcon />;
      case 'high': return <WarningIcon />;
      case 'medium': return <WarningIcon />;
      case 'low': return <InfoIcon />;
      case 'info': return <InfoIcon />;
      default: return <InfoIcon />;
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        OWASP Top 10 Security Scanner
      </Typography>

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
              placeholder="https://example.com/api/endpoint"
              disabled={scanning}
            />
          </Grid>

          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>HTTP Method</InputLabel>
              <Select
                value={method}
                label="HTTP Method"
                onChange={(e) => setMethod(e.target.value)}
                disabled={scanning}
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
              <InputLabel>Scan Depth</InputLabel>
              <Select
                value={depth}
                label="Scan Depth"
                onChange={(e) => setDepth(e.target.value as any)}
                disabled={scanning}
              >
                <MenuItem value="quick">Quick (Fast, fewer tests)</MenuItem>
                <MenuItem value="standard">Standard (Balanced)</MenuItem>
                <MenuItem value="thorough">Thorough (Slow, comprehensive)</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Headers (one per line, format: Key: Value)"
              value={headers}
              onChange={(e) => setHeaders(e.target.value)}
              placeholder="Authorization: Bearer token&#10;Content-Type: application/json"
              disabled={scanning}
            />
          </Grid>

          {method !== 'GET' && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Request Body"
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder='{"key": "value"}'
                disabled={scanning}
              />
            </Grid>
          )}

          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Test Categories (OWASP Top 10 2021)
            </Typography>
            <FormGroup row>
              {categories.map(cat => (
                <FormControlLabel
                  key={cat.id}
                  control={
                    <Checkbox
                      checked={selectedCategories.includes(cat.id)}
                      onChange={() => handleCategoryToggle(cat.id)}
                      disabled={scanning}
                    />
                  }
                  label={`${cat.id}: ${cat.name}`}
                />
              ))}
            </FormGroup>
          </Grid>
        </Grid>

        <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={scanning ? <StopIcon /> : <ScanIcon />}
            onClick={handleStartScan}
            disabled={scanning || !targetUrl}
          >
            {scanning ? 'Scanning...' : 'Start Scan'}
          </Button>
          {scanning && (
            <Box sx={{ flex: 1 }}>
              <LinearProgress variant="determinate" value={progress} />
              <Typography variant="caption" sx={{ mt: 0.5 }}>
                {progress}% Complete
              </Typography>
            </Box>
          )}
        </Box>
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
              Scan Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2">
                  <strong>Target:</strong> {result.targetUrl}
                </Typography>
                <Typography variant="body2">
                  <strong>Duration:</strong> {(result.duration / 1000).toFixed(2)}s
                </Typography>
                <Typography variant="body2">
                  <strong>Scan ID:</strong> {result.scanId}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip
                    icon={<ErrorIcon />}
                    label={`Critical: ${result.summary.critical}`}
                    color="error"
                    size="small"
                  />
                  <Chip
                    icon={<WarningIcon />}
                    label={`High: ${result.summary.high}`}
                    color="error"
                    size="small"
                  />
                  <Chip
                    icon={<WarningIcon />}
                    label={`Medium: ${result.summary.medium}`}
                    color="warning"
                    size="small"
                  />
                  <Chip
                    icon={<InfoIcon />}
                    label={`Low: ${result.summary.low}`}
                    color="info"
                    size="small"
                  />
                  <Chip
                    icon={<InfoIcon />}
                    label={`Info: ${result.summary.info}`}
                    color="default"
                    size="small"
                  />
                </Box>
              </Grid>
            </Grid>

            {result.recommendations.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Key Recommendations:
                </Typography>
                <List dense>
                  {result.recommendations.map((rec, idx) => (
                    <ListItem key={idx}>
                      <ListItemText primary={rec} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </Paper>

          <Typography variant="h6" gutterBottom>
            Findings ({result.findings.length})
          </Typography>

          {result.findings.length === 0 ? (
            <Alert severity="success" icon={<CheckIcon />}>
              No vulnerabilities detected! The target appears to be secure.
            </Alert>
          ) : (
            result.findings.map((finding) => (
              <Accordion key={finding.id}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                    {getSeverityIcon(finding.severity)}
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle1">
                        {finding.category}: {finding.title}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                        <Chip
                          label={finding.severity.toUpperCase()}
                          color={getSeverityColor(finding.severity) as any}
                          size="small"
                        />
                        <Chip
                          label={finding.confidence}
                          size="small"
                          variant="outlined"
                        />
                        {finding.cwe && (
                          <Chip label={finding.cwe} size="small" variant="outlined" />
                        )}
                        {finding.cvss && (
                          <Chip label={`CVSS: ${finding.cvss}`} size="small" color="error" />
                        )}
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
                      Evidence:
                    </Typography>
                    {finding.evidence.request && (
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Request:
                        </Typography>
                        <Paper variant="outlined" sx={{ p: 1, bgcolor: 'grey.50', position: 'relative' }}>
                          <code style={{ fontSize: '0.875rem', wordBreak: 'break-all' }}>
                            {finding.evidence.request}
                          </code>
                          <Tooltip title="Copy">
                            <IconButton
                              size="small"
                              sx={{ position: 'absolute', top: 4, right: 4 }}
                              onClick={() => copyToClipboard(finding.evidence.request!)}
                            >
                              <CopyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Paper>
                      </Box>
                    )}
                    {finding.evidence.payload && (
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Payload:
                        </Typography>
                        <Paper variant="outlined" sx={{ p: 1, bgcolor: 'grey.50' }}>
                          <code style={{ fontSize: '0.875rem' }}>{finding.evidence.payload}</code>
                        </Paper>
                      </Box>
                    )}
                    {finding.evidence.response && (
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Response (truncated):
                        </Typography>
                        <Paper variant="outlined" sx={{ p: 1, bgcolor: 'grey.50', maxHeight: 200, overflow: 'auto' }}>
                          <code style={{ fontSize: '0.875rem', whiteSpace: 'pre-wrap' }}>
                            {finding.evidence.response}
                          </code>
                        </Paper>
                      </Box>
                    )}

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="subtitle2" gutterBottom>
                      Remediation:
                    </Typography>
                    <Typography variant="body2" paragraph sx={{ whiteSpace: 'pre-line' }}>
                      {finding.remediation}
                    </Typography>

                    {finding.references.length > 0 && (
                      <>
                        <Typography variant="subtitle2" gutterBottom>
                          References:
                        </Typography>
                        <List dense>
                          {finding.references.map((ref, idx) => (
                            <ListItem key={idx} sx={{ py: 0 }}>
                              <ListItemText
                                primary={
                                  <a href={ref} target="_blank" rel="noopener noreferrer">
                                    {ref}
                                  </a>
                                }
                              />
                            </ListItem>
                          ))}
                        </List>
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

export default OWASPScanner;
