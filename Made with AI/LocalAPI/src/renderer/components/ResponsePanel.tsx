import React, { useState, useMemo, useCallback } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Chip from '@mui/material/Chip';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import type { Response } from '../../types/models';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = React.memo(({ children, value, index }) => {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ p: 2 }}>{children}</Box>}
    </div>
  );
});

TabPanel.displayName = 'TabPanel';

interface ResponsePanelProps {
  response?: Response | null;
}

const ResponsePanel: React.FC<ResponsePanelProps> = React.memo(({ response }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [bodyView, setBodyView] = useState<'pretty' | 'raw'>('pretty');

  // Format response body
  const formattedBody = useMemo(() => {
    if (!response?.body) return '';

    try {
      if (typeof response.body === 'string') {
        // Try to parse as JSON
        try {
          const parsed = JSON.parse(response.body);
          return bodyView === 'pretty' 
            ? JSON.stringify(parsed, null, 2) 
            : response.body;
        } catch {
          // Not JSON, return as is
          return response.body;
        }
      } else {
        // Already an object
        return bodyView === 'pretty'
          ? JSON.stringify(response.body, null, 2)
          : JSON.stringify(response.body);
      }
    } catch {
      return String(response.body);
    }
  }, [response?.body, bodyView]);

  // Detect content type
  const contentType = useMemo(() => {
    if (!response) return 'text';
    
    const ct = response.headers['content-type'] || response.headers['Content-Type'] || '';
    
    if (ct.includes('application/json')) return 'json';
    if (ct.includes('application/xml') || ct.includes('text/xml')) return 'xml';
    if (ct.includes('text/html')) return 'html';
    if (ct.includes('text/')) return 'text';
    
    return 'text';
  }, [response?.headers]);

  // Format size - memoized
  const formatSize = useCallback((bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  }, []);

  // Get status color - memoized
  const getStatusColor = useCallback((status: number): 'success' | 'info' | 'warning' | 'error' => {
    if (status >= 200 && status < 300) return 'success';
    if (status >= 300 && status < 400) return 'info';
    if (status >= 400 && status < 500) return 'warning';
    return 'error';
  }, []);

  const hasResponse = !!response;

  // Memoize formatted values
  const formattedSize = useMemo(
    () => (response ? formatSize(response.size) : ''),
    [response?.size, formatSize]
  );

  const statusColor = useMemo(
    () => (response ? getStatusColor(response.status) : 'info'),
    [response?.status, getStatusColor]
  );

  const headersCount = useMemo(
    () => (response ? Object.keys(response.headers).length : 0),
    [response?.headers]
  );

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header */}
      <Box
        sx={{
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <Typography variant="h6">Response</Typography>
        {hasResponse && (
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip
              label={`${response.status} ${response.statusText}`}
              color={statusColor}
              size="small"
            />
            <Chip label={`${response.time}ms`} size="small" />
            <Chip label={formattedSize} size="small" />
          </Box>
        )}
      </Box>

      {hasResponse ? (
        <>
          {/* Tabs */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
              <Tab label={`Body (${contentType.toUpperCase()})`} />
              <Tab label={`Headers (${headersCount})`} />
              <Tab label="Cookies" />
              <Tab label="Timeline" />
            </Tabs>
          </Box>

          {/* Tab Panels */}
          <Box sx={{ flex: 1, overflow: 'auto' }}>
            <TabPanel value={activeTab} index={0}>
              <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="caption" color="text.secondary">
                  Content-Type: {response.headers['content-type'] || response.headers['Content-Type'] || 'Unknown'}
                </Typography>
                {(contentType === 'json' || contentType === 'xml') && (
                  <ToggleButtonGroup
                    value={bodyView}
                    exclusive
                    onChange={(_, newView) => newView && setBodyView(newView)}
                    size="small"
                  >
                    <ToggleButton value="pretty">Pretty</ToggleButton>
                    <ToggleButton value="raw">Raw</ToggleButton>
                  </ToggleButtonGroup>
                )}
              </Box>
              
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  backgroundColor: theme => theme.palette.mode === 'dark' ? '#1e1e1e' : '#f5f5f5',
                  maxHeight: '600px',
                  overflow: 'auto',
                }}
              >
                <pre
                  style={{
                    margin: 0,
                    fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                    fontSize: '0.875rem',
                    lineHeight: 1.5,
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {formattedBody}
                </pre>
              </Paper>
            </TabPanel>

            <TabPanel value={activeTab} index={1}>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Header</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Value</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(response.headers).map(([key, value]) => (
                      <TableRow key={key}>
                        <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                          {key}
                        </TableCell>
                        <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                          {String(value)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </TabPanel>

            <TabPanel value={activeTab} index={2}>
              <Typography variant="body2" color="text.secondary">
                Cookie parsing coming soon
              </Typography>
            </TabPanel>

            <TabPanel value={activeTab} index={3}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Request Timeline
                  </Typography>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell>Status</TableCell>
                        <TableCell>
                          <Chip
                            label={`${response.status} ${response.statusText}`}
                            color={statusColor}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Time</TableCell>
                        <TableCell>{response.time}ms</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Size</TableCell>
                        <TableCell>{formattedSize}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>
                          {new Date(response.timestamp).toLocaleString()}
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </Box>

                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Performance
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <Chip
                      label={`Response Time: ${response.time}ms`}
                      color={response.time < 200 ? 'success' : response.time < 1000 ? 'warning' : 'error'}
                    />
                    <Chip
                      label={`Size: ${formattedSize}`}
                      color={response.size < 10240 ? 'success' : response.size < 102400 ? 'warning' : 'error'}
                    />
                  </Box>
                </Box>
              </Box>
            </TabPanel>
          </Box>
        </>
      ) : (
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'text.secondary',
            gap: 2,
          }}
        >
          <Typography variant="h6">No Response Yet</Typography>
          <Typography variant="body2">
            Send a request to see the response here
          </Typography>
        </Box>
      )}
    </Box>
  );
});

ResponsePanel.displayName = 'ResponsePanel';

export default ResponsePanel;
