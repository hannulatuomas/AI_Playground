import React, { useState, useCallback } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import TextField from '@mui/material/TextField';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import AssessmentIcon from '@mui/icons-material/Assessment';
import DownloadIcon from '@mui/icons-material/Download';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

type ReportType = 'security-scan' | 'vulnerability-scan' | 'security-trends' | 'performance-trends';

const ReportManager: React.FC = React.memo(() => {
  const [reportType, setReportType] = useState<ReportType>('security-scan');
  const [title, setTitle] = useState('');
  const [subtitle, setSubtitle] = useState('');
  const [author, setAuthor] = useState('');
  const [includeCharts, setIncludeCharts] = useState(true);
  const [includeSummary, setIncludeSummary] = useState(true);
  const [includeDetails, setIncludeDetails] = useState(true);
  const [startDate, setStartDate] = useState<Date | null>(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000));
  const [endDate, setEndDate] = useState<Date | null>(new Date());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleGenerateReport = useCallback(async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Prepare report data based on type
      const reportData = await prepareReportData(reportType, startDate, endDate);

      const options = {
        type: reportType,
        format: 'pdf' as const,
        title: title || getDefaultTitle(reportType),
        subtitle,
        author: author || 'LocalAPI',
        includeCharts,
        includeSummary,
        includeDetails,
        dateRange: startDate && endDate ? {
          start: startDate,
          end: endDate,
        } : undefined,
      };

      const result = await window.electronAPI.reports.generate(reportData, options);

      if (result.success) {
        setSuccess(`Report generated successfully! Saved to: ${result.filePath}`);
      } else {
        setError(result.error || 'Failed to generate report');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  }, [reportType, title, subtitle, author, includeCharts, includeSummary, includeDetails, startDate, endDate]);

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
          <AssessmentIcon />
          <Typography variant="h5">Report Manager</Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}

        {/* Report Configuration */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Report Configuration
            </Typography>

            {/* Report Type */}
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Report Type</InputLabel>
              <Select
                value={reportType}
                label="Report Type"
                onChange={(e) => setReportType(e.target.value as ReportType)}
              >
                <MenuItem value="security-scan">Security Scan Report</MenuItem>
                <MenuItem value="vulnerability-scan">Vulnerability Scan Report</MenuItem>
                <MenuItem value="security-trends">Security Trends Report</MenuItem>
                <MenuItem value="performance-trends">Performance Trends Report</MenuItem>
              </Select>
            </FormControl>

            {/* Title */}
            <TextField
              fullWidth
              label="Report Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={getDefaultTitle(reportType)}
              sx={{ mb: 2 }}
            />

            {/* Subtitle */}
            <TextField
              fullWidth
              label="Subtitle (optional)"
              value={subtitle}
              onChange={(e) => setSubtitle(e.target.value)}
              sx={{ mb: 2 }}
            />

            {/* Author */}
            <TextField
              fullWidth
              label="Author"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              placeholder="LocalAPI"
              sx={{ mb: 2 }}
            />

            {/* Date Range for Trends */}
            {(reportType === 'security-trends' || reportType === 'performance-trends') && (
              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <DatePicker
                  label="Start Date"
                  value={startDate}
                  onChange={(date: Date | null) => setStartDate(date)}
                  slotProps={{ textField: { fullWidth: true } }}
                />
                <DatePicker
                  label="End Date"
                  value={endDate}
                  onChange={(date: Date | null) => setEndDate(date)}
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </Box>
            )}

            {/* Options */}
            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              Include in Report
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={includeCharts}
                    onChange={(e) => setIncludeCharts(e.target.checked)}
                  />
                }
                label="Charts and Visualizations"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={includeSummary}
                    onChange={(e) => setIncludeSummary(e.target.checked)}
                  />
                }
                label="Executive Summary"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={includeDetails}
                    onChange={(e) => setIncludeDetails(e.target.checked)}
                  />
                }
                label="Detailed Findings"
              />
            </Box>
          </CardContent>

          <CardActions>
            <Button
              variant="contained"
              startIcon={loading ? <CircularProgress size={16} /> : <DownloadIcon />}
              onClick={handleGenerateReport}
              disabled={loading}
              fullWidth
            >
              {loading ? 'Generating Report...' : 'Generate PDF Report'}
            </Button>
          </CardActions>
        </Card>

        {/* Report Type Descriptions */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Report Types
          </Typography>

          <Card variant="outlined" sx={{ mb: 1 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold">
                Security Scan Report
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Comprehensive security analysis of API collections with findings categorized by severity,
                security scores, and detailed recommendations.
              </Typography>
            </CardContent>
          </Card>

          <Card variant="outlined" sx={{ mb: 1 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold">
                Vulnerability Scan Report
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Detailed vulnerability assessment with OWASP classifications, evidence, payloads,
                and remediation guidance.
              </Typography>
            </CardContent>
          </Card>

          <Card variant="outlined" sx={{ mb: 1 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold">
                Security Trends Report
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Historical analysis of security posture over time, showing improvements, recurring issues,
                and trend charts for scores and vulnerabilities.
              </Typography>
            </CardContent>
          </Card>

          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold">
                Performance Trends Report
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Performance metrics analysis including response times, slowest endpoints, error rates,
                and cache hit statistics over time.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </LocalizationProvider>
  );
});

ReportManager.displayName = 'ReportManager';

// Helper functions
function getDefaultTitle(reportType: ReportType): string {
  switch (reportType) {
    case 'security-scan':
      return 'Security Scan Report';
    case 'vulnerability-scan':
      return 'Vulnerability Scan Report';
    case 'security-trends':
      return 'Security Trends Report';
    case 'performance-trends':
      return 'Performance Trends Report';
    default:
      return 'Report';
  }
}

async function prepareReportData(
  reportType: ReportType,
  startDate: Date | null,
  endDate: Date | null
): Promise<any> {
  // This would fetch actual data from the database/services
  // For now, return mock data structure
  
  switch (reportType) {
    case 'security-scan':
      return {
        scanDate: new Date(),
        collectionName: 'Sample Collection',
        totalRequests: 50,
        passedChecks: 45,
        failedChecks: 5,
        warnings: 2,
        securityScore: 85,
        findings: [],
        summary: {
          critical: 0,
          high: 2,
          medium: 3,
          low: 5,
          info: 10,
        },
      };

    case 'vulnerability-scan':
      return {
        scanDate: new Date(),
        targetUrl: 'https://api.example.com',
        scanDuration: 5000,
        vulnerabilities: [],
        summary: {
          critical: 1,
          high: 3,
          medium: 5,
          low: 8,
          info: 12,
        },
        riskScore: 72,
      };

    case 'security-trends':
      return {
        dateRange: {
          start: startDate || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
          end: endDate || new Date(),
        },
        totalScans: 15,
        averageScore: 78.5,
        trendData: [],
        topIssues: [],
        improvements: [],
      };

    case 'performance-trends':
      return {
        dateRange: {
          start: startDate || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
          end: endDate || new Date(),
        },
        totalRequests: 1500,
        averageResponseTime: 245,
        trendData: [],
        slowestEndpoints: [],
        errorRates: [],
      };

    default:
      return {};
  }
}

export default ReportManager;
