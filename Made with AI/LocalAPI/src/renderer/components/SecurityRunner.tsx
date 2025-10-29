import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Tabs,
  Tab,
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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  IconButton,
  Tooltip,
  Badge,
} from '@mui/material';
import {
  PlayArrow as RunIcon,
  Stop as StopIcon,
  Security as SecurityIcon,
  BugReport as BugIcon,
  Shield as ShieldIcon,
  Assessment as ReportIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Info as InfoIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.Node;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`security-tabpanel-${index}`}
      aria-labelledby={`security-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface SecurityTest {
  id: string;
  name: string;
  type: 'owasp' | 'fuzzing' | 'vulnerability';
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  findings: number;
  severity: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
}

const SecurityRunner: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [targetUrl, setTargetUrl] = useState('');
  const [method, setMethod] = useState('GET');
  const [headers, setHeaders] = useState('');
  const [running, setRunning] = useState(false);
  const [tests, setTests] = useState<SecurityTest[]>([]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Test configuration
  const [owaspEnabled, setOwaspEnabled] = useState(true);
  const [fuzzingEnabled, setFuzzingEnabled] = useState(true);
  const [vulnerabilityEnabled, setVulnerabilityEnabled] = useState(true);
  
  const [owaspDepth, setOwaspDepth] = useState<'quick' | 'standard' | 'thorough'>('standard');
  const [fuzzingIntensity, setFuzzingIntensity] = useState<'low' | 'medium' | 'high'>('medium');

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleRunAllTests = async () => {
    if (!targetUrl) {
      setError('Please enter a target URL');
      return;
    }

    setRunning(true);
    setError(null);
    setTests([]);
    setOverallProgress(0);

    const testsToRun: SecurityTest[] = [];

    if (owaspEnabled) {
      testsToRun.push({
        id: 'owasp-scan',
        name: 'OWASP Top 10 Scan',
        type: 'owasp',
        status: 'pending',
        progress: 0,
        findings: 0,
        severity: { critical: 0, high: 0, medium: 0, low: 0 },
      });
    }

    if (fuzzingEnabled) {
      testsToRun.push({
        id: 'fuzzing-test',
        name: 'Fuzzing & Bomb Testing',
        type: 'fuzzing',
        status: 'pending',
        progress: 0,
        findings: 0,
        severity: { critical: 0, high: 0, medium: 0, low: 0 },
      });
    }

    if (vulnerabilityEnabled) {
      testsToRun.push({
        id: 'vulnerability-scan',
        name: 'Vulnerability Scan',
        type: 'vulnerability',
        status: 'pending',
        progress: 0,
        findings: 0,
        severity: { critical: 0, high: 0, medium: 0, low: 0 },
      });
    }

    setTests(testsToRun);

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

      let completedTests = 0;
      const totalTests = testsToRun.length;

      // Run OWASP scan
      if (owaspEnabled) {
        setTests(prev => prev.map(t => 
          t.id === 'owasp-scan' ? { ...t, status: 'running' } : t
        ));

        const owaspResult = await (window as any).electronAPI.owasp.scan({
          targetUrl,
          method,
          headers: headersObj,
          depth: owaspDepth,
        });

        completedTests++;
        setOverallProgress((completedTests / totalTests) * 100);

        setTests(prev => prev.map(t => 
          t.id === 'owasp-scan' ? {
            ...t,
            status: 'completed',
            progress: 100,
            findings: owaspResult.findings.length,
            severity: {
              critical: owaspResult.summary.critical,
              high: owaspResult.summary.high,
              medium: owaspResult.summary.medium,
              low: owaspResult.summary.low,
            },
          } : t
        ));
      }

      // Run Fuzzing test
      if (fuzzingEnabled) {
        setTests(prev => prev.map(t => 
          t.id === 'fuzzing-test' ? { ...t, status: 'running' } : t
        ));

        const fuzzingResult = await (window as any).electronAPI.fuzzing.run({
          targetUrl,
          method,
          headers: headersObj,
          fuzzingType: 'all',
          intensity: fuzzingIntensity,
        });

        completedTests++;
        setOverallProgress((completedTests / totalTests) * 100);

        setTests(prev => prev.map(t => 
          t.id === 'fuzzing-test' ? {
            ...t,
            status: 'completed',
            progress: 100,
            findings: fuzzingResult.findings.length,
            severity: {
              critical: fuzzingResult.findings.filter((f: any) => f.severity === 'critical').length,
              high: fuzzingResult.findings.filter((f: any) => f.severity === 'high').length,
              medium: fuzzingResult.findings.filter((f: any) => f.severity === 'medium').length,
              low: fuzzingResult.findings.filter((f: any) => f.severity === 'low').length,
            },
          } : t
        ));
      }

      // Run Vulnerability scan
      if (vulnerabilityEnabled) {
        setTests(prev => prev.map(t => 
          t.id === 'vulnerability-scan' ? { ...t, status: 'running' } : t
        ));

        const vulnResult = await (window as any).electronAPI.vulnerability.scanEndpoint(
          targetUrl,
          method
        );

        completedTests++;
        setOverallProgress((completedTests / totalTests) * 100);

        setTests(prev => prev.map(t => 
          t.id === 'vulnerability-scan' ? {
            ...t,
            status: 'completed',
            progress: 100,
            findings: vulnResult.vulnerabilities?.length || 0,
            severity: {
              critical: vulnResult.vulnerabilities?.filter((v: any) => v.severity === 'critical').length || 0,
              high: vulnResult.vulnerabilities?.filter((v: any) => v.severity === 'high').length || 0,
              medium: vulnResult.vulnerabilities?.filter((v: any) => v.severity === 'medium').length || 0,
              low: vulnResult.vulnerabilities?.filter((v: any) => v.severity === 'low').length || 0,
            },
          } : t
        ));
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Security tests failed');
      setTests(prev => prev.map(t => 
        t.status === 'running' ? { ...t, status: 'failed' } : t
      ));
    } finally {
      setRunning(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'primary';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckIcon />;
      case 'running': return <RefreshIcon className="spinning" />;
      case 'failed': return <ErrorIcon />;
      default: return <InfoIcon />;
    }
  };

  const getTotalFindings = () => {
    return tests.reduce((sum, test) => sum + test.findings, 0);
  };

  const getTotalSeverity = () => {
    return tests.reduce((acc, test) => ({
      critical: acc.critical + test.severity.critical,
      high: acc.high + test.severity.high,
      medium: acc.medium + test.severity.medium,
      low: acc.low + test.severity.low,
    }), { critical: 0, high: 0, medium: 0, low: 0 });
  };

  const handleExportReport = () => {
    // TODO: Implement report export
    console.log('Export report');
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <ShieldIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Security Testing Suite
      </Typography>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Quick Scan" icon={<SecurityIcon />} />
          <Tab label="Configuration" icon={<BugIcon />} />
          <Tab label="Results" icon={<ReportIcon />} disabled={tests.length === 0} />
        </Tabs>

        <TabPanel value={activeTab} index={0}>
          {/* Quick Scan Tab */}
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Target URL"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                placeholder="https://example.com/api"
                disabled={running}
              />
            </Grid>

            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>HTTP Method</InputLabel>
                <Select
                  value={method}
                  label="HTTP Method"
                  onChange={(e) => setMethod(e.target.value)}
                  disabled={running}
                >
                  <MenuItem value="GET">GET</MenuItem>
                  <MenuItem value="POST">POST</MenuItem>
                  <MenuItem value="PUT">PUT</MenuItem>
                  <MenuItem value="DELETE">DELETE</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={6}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Headers (optional)"
                value={headers}
                onChange={(e) => setHeaders(e.target.value)}
                placeholder="Authorization: Bearer token"
                disabled={running}
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Test Selection
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Card variant="outlined" sx={{ bgcolor: owaspEnabled ? 'primary.50' : 'grey.50' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle1">
                          <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                          OWASP Top 10
                        </Typography>
                        <Button
                          size="small"
                          variant={owaspEnabled ? 'contained' : 'outlined'}
                          onClick={() => setOwaspEnabled(!owaspEnabled)}
                          disabled={running}
                        >
                          {owaspEnabled ? 'Enabled' : 'Disabled'}
                        </Button>
                      </Box>
                      {owaspEnabled && (
                        <FormControl fullWidth size="small">
                          <InputLabel>Depth</InputLabel>
                          <Select
                            value={owaspDepth}
                            label="Depth"
                            onChange={(e) => setOwaspDepth(e.target.value as any)}
                            disabled={running}
                          >
                            <MenuItem value="quick">Quick</MenuItem>
                            <MenuItem value="standard">Standard</MenuItem>
                            <MenuItem value="thorough">Thorough</MenuItem>
                          </Select>
                        </FormControl>
                      )}
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Card variant="outlined" sx={{ bgcolor: fuzzingEnabled ? 'primary.50' : 'grey.50' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle1">
                          <BugIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                          Fuzzing & Bombs
                        </Typography>
                        <Button
                          size="small"
                          variant={fuzzingEnabled ? 'contained' : 'outlined'}
                          onClick={() => setFuzzingEnabled(!fuzzingEnabled)}
                          disabled={running}
                        >
                          {fuzzingEnabled ? 'Enabled' : 'Disabled'}
                        </Button>
                      </Box>
                      {fuzzingEnabled && (
                        <FormControl fullWidth size="small">
                          <InputLabel>Intensity</InputLabel>
                          <Select
                            value={fuzzingIntensity}
                            label="Intensity"
                            onChange={(e) => setFuzzingIntensity(e.target.value as any)}
                            disabled={running}
                          >
                            <MenuItem value="low">Low (50)</MenuItem>
                            <MenuItem value="medium">Medium (200)</MenuItem>
                            <MenuItem value="high">High (500)</MenuItem>
                          </Select>
                        </FormControl>
                      )}
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Card variant="outlined" sx={{ bgcolor: vulnerabilityEnabled ? 'primary.50' : 'grey.50' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="subtitle1">
                          <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                          Vulnerability Scan
                        </Typography>
                        <Button
                          size="small"
                          variant={vulnerabilityEnabled ? 'contained' : 'outlined'}
                          onClick={() => setVulnerabilityEnabled(!vulnerabilityEnabled)}
                          disabled={running}
                        >
                          {vulnerabilityEnabled ? 'Enabled' : 'Disabled'}
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                size="large"
                color="primary"
                startIcon={running ? <StopIcon /> : <RunIcon />}
                onClick={handleRunAllTests}
                disabled={running || !targetUrl || (!owaspEnabled && !fuzzingEnabled && !vulnerabilityEnabled)}
                fullWidth
              >
                {running ? 'Running Security Tests...' : 'Run All Security Tests'}
              </Button>
            </Grid>

            {running && (
              <Grid item xs={12}>
                <LinearProgress variant="determinate" value={overallProgress} />
                <Typography variant="caption" sx={{ mt: 1 }}>
                  Overall Progress: {Math.round(overallProgress)}%
                </Typography>
              </Grid>
            )}
          </Grid>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <Alert severity="warning" sx={{ mt: 3 }}>
            <strong>Warning:</strong> Security testing can generate significant load. Only test systems you have permission to test.
          </Alert>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          {/* Configuration Tab - Placeholder for advanced settings */}
          <Typography variant="h6" gutterBottom>
            Advanced Configuration
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Advanced configuration options coming soon...
          </Typography>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          {/* Results Tab */}
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">
                Test Results
              </Typography>
              <Button
                startIcon={<DownloadIcon />}
                onClick={handleExportReport}
                variant="outlined"
              >
                Export Report
              </Button>
            </Box>

            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Total Findings
                    </Typography>
                    <Typography variant="h4">
                      {getTotalFindings()}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={9}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Severity Breakdown
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                      <Chip
                        icon={<ErrorIcon />}
                        label={`Critical: ${getTotalSeverity().critical}`}
                        color="error"
                      />
                      <Chip
                        icon={<WarningIcon />}
                        label={`High: ${getTotalSeverity().high}`}
                        color="error"
                        variant="outlined"
                      />
                      <Chip
                        icon={<WarningIcon />}
                        label={`Medium: ${getTotalSeverity().medium}`}
                        color="warning"
                      />
                      <Chip
                        icon={<InfoIcon />}
                        label={`Low: ${getTotalSeverity().low}`}
                        color="info"
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <List>
              {tests.map((test) => (
                <React.Fragment key={test.id}>
                  <ListItem>
                    <ListItemIcon>
                      {getStatusIcon(test.status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={test.name}
                      secondary={
                        <Box sx={{ mt: 1 }}>
                          <Chip
                            label={test.status}
                            color={getStatusColor(test.status) as any}
                            size="small"
                            sx={{ mr: 1 }}
                          />
                          {test.status === 'completed' && (
                            <>
                              <Chip
                                label={`${test.findings} findings`}
                                size="small"
                                sx={{ mr: 1 }}
                              />
                              {test.severity.critical > 0 && (
                                <Chip
                                  label={`${test.severity.critical} critical`}
                                  color="error"
                                  size="small"
                                  sx={{ mr: 1 }}
                                />
                              )}
                            </>
                          )}
                        </Box>
                      }
                    />
                    {test.status === 'running' && (
                      <LinearProgress sx={{ width: 100 }} />
                    )}
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Box>
        </TabPanel>
      </Paper>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .spinning {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </Box>
  );
};

export default SecurityRunner;
