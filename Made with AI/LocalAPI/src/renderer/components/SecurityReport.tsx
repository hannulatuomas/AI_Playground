import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';

interface SecurityCheck {
  id: string;
  name: string;
  category: 'headers' | 'leaks' | 'cookies' | 'ssl';
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  passed: boolean;
  message: string;
  recommendation?: string;
  details?: any;
}

interface SecurityReportData {
  url: string;
  timestamp: Date;
  checks: SecurityCheck[];
  score: number;
  criticalCount: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
  passedCount: number;
  failedCount: number;
}

interface SecurityReportProps {
  report: SecurityReportData | null;
  onExport?: (format: 'json' | 'markdown') => void;
}

const SecurityReportComponent: React.FC<SecurityReportProps> = ({ report, onExport }) => {
  // If no report, show instructions
  if (!report) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <SecurityIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h5" gutterBottom>
          Security Assertions
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Run security checks on your API responses to detect vulnerabilities and security issues.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          To get started:
        </Typography>
        <Box component="ol" sx={{ textAlign: 'left', maxWidth: 600, mx: 'auto', mt: 2 }}>
          <li>Send a request from the Requests tab</li>
          <li>The response will be automatically analyzed for security issues</li>
          <li>View the security report here with detailed findings</li>
        </Box>
      </Box>
    );
  }

  const [expandedCategory, setExpandedCategory] = useState<string | false>('headers');

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'high':
        return <WarningIcon color="error" />;
      case 'medium':
        return <WarningIcon color="warning" />;
      case 'low':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const groupByCategory = (checks: SecurityCheck[]) => {
    const groups: Record<string, SecurityCheck[]> = {
      headers: [],
      leaks: [],
      cookies: [],
      ssl: [],
    };

    for (const check of checks) {
      groups[check.category].push(check);
    }

    return groups;
  };

  const groupedChecks = groupByCategory(report.checks);
  const failedChecks = report.checks.filter(c => !c.passed);

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 2 }}>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <SecurityIcon sx={{ fontSize: 40, color: getScoreColor(report.score) }} />
            <Box>
              <Typography variant="h5">Security Report</Typography>
              <Typography variant="body2" color="text.secondary">
                {report.url}
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              size="small"
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => {
                const json = JSON.stringify(report, null, 2);
                const blob = new Blob([json], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `security-report-${Date.now()}.json`;
                a.click();
              }}
            >
              Export JSON
            </Button>
            <Button
              size="small"
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => {
                let markdown = `# Security Report\n\n`;
                markdown += `**URL:** ${report.url}\n`;
                markdown += `**Score:** ${report.score}/100\n\n`;
                markdown += `## Summary\n\n`;
                markdown += `- Critical: ${report.criticalCount}\n`;
                markdown += `- High: ${report.highCount}\n`;
                markdown += `- Medium: ${report.mediumCount}\n`;
                markdown += `- Low: ${report.lowCount}\n\n`;
                markdown += `## Checks\n\n`;
                report.checks.forEach(check => {
                  markdown += `### ${check.name}\n`;
                  markdown += `- **Status:** ${check.passed ? '✅ Passed' : '❌ Failed'}\n`;
                  markdown += `- **Severity:** ${check.severity}\n`;
                  markdown += `- **Message:** ${check.message}\n\n`;
                });
                const blob = new Blob([markdown], { type: 'text/markdown' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `security-report-${Date.now()}.md`;
                a.click();
              }}
            >
              Export MD
            </Button>
          </Box>
        </Box>

        {/* Score */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2">Security Score</Typography>
            <Typography variant="h6" color={`${getScoreColor(report.score)}.main`}>
              {report.score}/100
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={report.score}
            color={getScoreColor(report.score)}
            sx={{ height: 10, borderRadius: 5 }}
          />
        </Box>

        {/* Statistics */}
        <Grid container spacing={2}>
          <Grid item xs={6} sm={3}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center', py: 1 }}>
                <Typography variant="h4" color="success.main">
                  {report.passedCount}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Passed
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center', py: 1 }}>
                <Typography variant="h4" color="error.main">
                  {report.criticalCount}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Critical
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center', py: 1 }}>
                <Typography variant="h4" color="warning.main">
                  {report.highCount}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  High
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center', py: 1 }}>
                <Typography variant="h4" color="info.main">
                  {report.mediumCount + report.lowCount}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Medium/Low
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* Failed Checks Summary */}
      {failedChecks.length > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            {failedChecks.length} Security Issue{failedChecks.length !== 1 ? 's' : ''} Found
          </Typography>
          <Typography variant="body2">
            Review the findings below and implement the recommended fixes.
          </Typography>
        </Alert>
      )}

      {/* Checks by Category */}
      <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
        Security Checks
      </Typography>

      {Object.entries(groupedChecks).map(([category, checks]) => {
        if (checks.length === 0) return null;

        const failedInCategory = checks.filter(c => !c.passed).length;

        return (
          <Accordion
            key={category}
            expanded={expandedCategory === category}
            onChange={(_, isExpanded) => setExpandedCategory(isExpanded ? category : false)}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                <Typography sx={{ textTransform: 'capitalize', fontWeight: 'medium' }}>
                  {category}
                </Typography>
                <Chip
                  label={`${checks.length} checks`}
                  size="small"
                  variant="outlined"
                />
                {failedInCategory > 0 && (
                  <Chip
                    label={`${failedInCategory} failed`}
                    size="small"
                    color="error"
                  />
                )}
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <List>
                {checks.map((check, index) => (
                  <React.Fragment key={check.id}>
                    {index > 0 && <Divider />}
                    <ListItem alignItems="flex-start">
                      <Box sx={{ display: 'flex', gap: 2, width: '100%' }}>
                        <Box sx={{ mt: 0.5 }}>
                          {check.passed ? (
                            <CheckCircleIcon color="success" />
                          ) : (
                            getSeverityIcon(check.severity)
                          )}
                        </Box>
                        <Box sx={{ flex: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                            <Typography variant="subtitle2">
                              {check.name}
                            </Typography>
                            {!check.passed && (
                              <Chip
                                label={check.severity}
                                size="small"
                                color={getSeverityColor(check.severity) as any}
                              />
                            )}
                          </Box>
                          <Typography variant="body2" color="text.secondary" paragraph>
                            {check.message}
                          </Typography>
                          {check.recommendation && (
                            <Alert severity="info" sx={{ mt: 1 }}>
                              <Typography variant="caption">
                                <strong>Recommendation:</strong> {check.recommendation}
                              </Typography>
                            </Alert>
                          )}
                          {check.details && (
                            <Paper variant="outlined" sx={{ p: 1, mt: 1, bgcolor: 'grey.50' }}>
                              <Typography variant="caption" component="pre" sx={{ m: 0 }}>
                                {JSON.stringify(check.details, null, 2)}
                              </Typography>
                            </Paper>
                          )}
                        </Box>
                      </Box>
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        );
      })}

      {/* Timestamp */}
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2, textAlign: 'center' }}>
        Report generated: {new Date(report.timestamp).toLocaleString()}
      </Typography>
    </Box>
  );
};

export default SecurityReportComponent;
