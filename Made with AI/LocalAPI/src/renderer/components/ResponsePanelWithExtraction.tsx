// Enhanced Response Panel with Variable Extraction
// Integrates all extraction features into the response viewer

import React, { useState, useMemo, useCallback } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Chip from '@mui/material/Chip';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Divider from '@mui/material/Divider';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import HistoryIcon from '@mui/icons-material/History';
import RuleIcon from '@mui/icons-material/Rule';
import MapIcon from '@mui/icons-material/Map';
import VisibilityIcon from '@mui/icons-material/Visibility';
import type { Response } from '../../types/models';
import VariableExtractorDialog from './VariableExtractorDialog';
import VariablePreviewPanel from './VariablePreviewPanel';
import ExtractionRulesManager from './ExtractionRulesManager';
import VariableMappingWizard from './VariableMappingWizard';
import VariableHistoryViewer from './VariableHistoryViewer';

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

interface ResponsePanelWithExtractionProps {
  response?: Response | null;
}

const ResponsePanelWithExtraction: React.FC<ResponsePanelWithExtractionProps> = ({ response }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [bodyView, setBodyView] = useState<'pretty' | 'raw'>('pretty');
  const [extractorOpen, setExtractorOpen] = useState(false);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [rulesOpen, setRulesOpen] = useState(false);
  const [mappingOpen, setMappingOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState<any>(undefined);
  const [selectedPath, setSelectedPath] = useState<string | undefined>(undefined);
  const [extractionType, setExtractionType] = useState<'json' | 'xml' | 'header' | undefined>(
    undefined
  );
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);

  // Format response body
  const formattedBody = useMemo(() => {
    if (!response?.body) return '';

    try {
      if (typeof response.body === 'string') {
        try {
          const parsed = JSON.parse(response.body);
          return bodyView === 'pretty' ? JSON.stringify(parsed, null, 2) : response.body;
        } catch {
          return response.body;
        }
      } else {
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

  const formatSize = useCallback((bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  }, []);

  const getStatusColor = useCallback(
    (status: number): 'success' | 'info' | 'warning' | 'error' => {
      if (status >= 200 && status < 300) return 'success';
      if (status >= 300 && status < 400) return 'info';
      if (status >= 400 && status < 500) return 'warning';
      return 'error';
    },
    []
  );

  const hasResponse = !!response;

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

  const handleQuickExtract = (type: 'json' | 'xml' | 'header') => {
    setExtractionType(type);
    setSelectedValue(undefined);
    setSelectedPath(undefined);
    setExtractorOpen(true);
  };

  const handleExtractFromHeader = (headerName: string, value: string) => {
    setExtractionType('header');
    setSelectedPath(headerName);
    setSelectedValue(value);
    setExtractorOpen(true);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchor(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
  };

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
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          {hasResponse && (
            <>
              <Chip
                label={`${response.status} ${response.statusText}`}
                color={statusColor}
                size="small"
              />
              <Chip label={`${response.time}ms`} size="small" />
              <Chip label={formattedSize} size="small" />
              <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
              <Tooltip title="Quick extract variable">
                <IconButton size="small" color="primary" onClick={() => handleQuickExtract(contentType as any)}>
                  <AddCircleIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="More extraction options">
                <IconButton size="small" onClick={handleMenuOpen}>
                  <MoreVertIcon />
                </IconButton>
              </Tooltip>
            </>
          )}
        </Box>
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
              <Tab label="Variables" icon={<VisibilityIcon />} iconPosition="start" />
            </Tabs>
          </Box>

          {/* Tab Panels */}
          <Box sx={{ flex: 1, overflow: 'auto' }}>
            <TabPanel value={activeTab} index={0}>
              <Box
                sx={{
                  mb: 2,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <Typography variant="caption" color="text.secondary">
                  Content-Type:{' '}
                  {response.headers['content-type'] || response.headers['Content-Type'] || 'Unknown'}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
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
                  <Button
                    size="small"
                    startIcon={<AddCircleIcon />}
                    onClick={() => handleQuickExtract(contentType as any)}
                  >
                    Extract Variable
                  </Button>
                </Box>
              </Box>

              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  backgroundColor: (theme) =>
                    theme.palette.mode === 'dark' ? '#1e1e1e' : '#f5f5f5',
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
              <Box sx={{ mb: 2 }}>
                <Button
                  size="small"
                  startIcon={<AddCircleIcon />}
                  onClick={() => handleQuickExtract('header')}
                >
                  Extract from Header
                </Button>
              </Box>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Header</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Value</TableCell>
                      <TableCell sx={{ fontWeight: 600, width: 100 }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(response.headers).map(([key, value]) => (
                      <TableRow key={key} hover>
                        <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                          {key}
                        </TableCell>
                        <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                          {String(value)}
                        </TableCell>
                        <TableCell>
                          <Tooltip title="Extract to variable">
                            <IconButton
                              size="small"
                              onClick={() => handleExtractFromHeader(key, String(value))}
                            >
                              <AddCircleIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
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
                        <TableCell>{new Date(response.timestamp).toLocaleString()}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </Box>
              </Box>
            </TabPanel>

            <TabPanel value={activeTab} index={4}>
              <VariablePreviewPanel onViewHistory={() => setHistoryOpen(true)} />
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
          <Typography variant="body2">Send a request to see the response here</Typography>
        </Box>
      )}

      {/* Extraction Menu */}
      <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={handleMenuClose}>
        <MenuItem
          onClick={() => {
            setMappingOpen(true);
            handleMenuClose();
          }}
        >
          <MapIcon sx={{ mr: 1 }} fontSize="small" />
          Batch Extract (Mapping Wizard)
        </MenuItem>
        <MenuItem
          onClick={() => {
            setRulesOpen(true);
            handleMenuClose();
          }}
        >
          <RuleIcon sx={{ mr: 1 }} fontSize="small" />
          Manage Extraction Rules
        </MenuItem>
        <MenuItem
          onClick={() => {
            setHistoryOpen(true);
            handleMenuClose();
          }}
        >
          <HistoryIcon sx={{ mr: 1 }} fontSize="small" />
          View Variable History
        </MenuItem>
        <Divider />
        <MenuItem
          onClick={() => {
            setPreviewOpen(true);
            handleMenuClose();
          }}
        >
          <VisibilityIcon sx={{ mr: 1 }} fontSize="small" />
          Variable Preview Panel
        </MenuItem>
      </Menu>

      {/* Dialogs */}
      <VariableExtractorDialog
        open={extractorOpen}
        onClose={() => setExtractorOpen(false)}
        response={response || null}
        selectedValue={selectedValue}
        selectedPath={selectedPath}
        extractionType={extractionType}
      />

      <VariableMappingWizard
        open={mappingOpen}
        onClose={() => setMappingOpen(false)}
        response={response || null}
      />

      <VariableHistoryViewer open={historyOpen} onClose={() => setHistoryOpen(false)} />

      {/* Rules Manager Dialog */}
      <Dialog open={rulesOpen} onClose={() => setRulesOpen(false)} maxWidth="lg" fullWidth>
        <ExtractionRulesManager response={response} />
      </Dialog>

      {/* Preview Panel Dialog */}
      <Dialog open={previewOpen} onClose={() => setPreviewOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Variable Preview</DialogTitle>
        <DialogContent>
          <VariablePreviewPanel onViewHistory={() => setHistoryOpen(true)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Add missing Dialog imports
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';

ResponsePanelWithExtraction.displayName = 'ResponsePanelWithExtraction';

export default ResponsePanelWithExtraction;
