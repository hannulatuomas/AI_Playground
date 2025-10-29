// Import Dialog Component
/// <reference path="../global.d.ts" />
import React, { useState, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tabs,
  Tab,
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  Paper,
  IconButton,
  Checkbox,
  ListItemButton,
  FormControlLabel,
} from '@mui/material';
import {
  Upload,
  Link as LinkIcon,
  ContentPaste,
  Close,
  CheckCircle,
  Error as ErrorIcon,
  Info,
} from '@mui/icons-material';
import type { ImportExportFormat, ImportResult } from '../../types/import-export';

interface ImportDialogProps {
  open: boolean;
  onClose: () => void;
  onImportComplete?: (result: ImportResult) => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`import-tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export function ImportDialog({ open, onClose, onImportComplete }: ImportDialogProps) {
  const [tabValue, setTabValue] = useState(0);
  const [content, setContent] = useState('');
  const [url, setUrl] = useState('');
  const [selectedFormat, setSelectedFormat] = useState<ImportExportFormat | 'auto'>('auto');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [detectedFormat, setDetectedFormat] = useState<ImportExportFormat | null>(null);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [conflictResolution, setConflictResolution] = useState<'merge' | 'replace' | 'skip'>('merge');
  
  // Import type selection - what types to import
  const [importTypes, setImportTypes] = useState<{
    collections: boolean;
    requests: boolean;
    environments: boolean;
    variables: boolean;
  }>({
    collections: true,
    requests: true,
    environments: true,
    variables: true,
  });
  
  // Selection state for import preview
  const [selectedCollections, setSelectedCollections] = useState<string[]>([]);
  const [selectedRequests, setSelectedRequests] = useState<string[]>([]);
  const [selectedEnvironments, setSelectedEnvironments] = useState<string[]>([]);
  const [selectedVariables, setSelectedVariables] = useState<string[]>([]);
  
  // Auto-select all items when result changes
  React.useEffect(() => {
    if (result) {
      setSelectedCollections(result.collections?.map(c => c.id) || []);
      setSelectedRequests(result.requests?.map(r => r.id) || []);
      setSelectedEnvironments(result.environments?.map(e => e.id) || []);
      setSelectedVariables(result.variables?.map(v => v.key) || []);
    }
  }, [result]);
  
  const toggleSelection = (id: string, type: 'collections' | 'requests' | 'environments' | 'variables') => {
    if (type === 'collections') {
      setSelectedCollections(prev => 
        prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
      );
    } else if (type === 'requests') {
      setSelectedRequests(prev => 
        prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
      );
    } else if (type === 'environments') {
      setSelectedEnvironments(prev => 
        prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
      );
    } else if (type === 'variables') {
      setSelectedVariables(prev => 
        prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
      );
    }
  };
  
  const selectAll = (type: 'collections' | 'requests' | 'environments' | 'variables') => {
    if (type === 'collections' && result?.collections) {
      setSelectedCollections(result.collections.map(c => c.id));
    } else if (type === 'requests' && result?.requests) {
      setSelectedRequests(result.requests.map(r => r.id));
    } else if (type === 'environments' && result?.environments) {
      setSelectedEnvironments(result.environments.map(e => e.id));
    } else if (type === 'variables' && result?.variables) {
      setSelectedVariables(result.variables.map(v => v.key));
    }
  };
  
  const deselectAll = (type: 'collections' | 'requests' | 'environments' | 'variables') => {
    if (type === 'collections') {
      setSelectedCollections([]);
    } else if (type === 'requests') {
      setSelectedRequests([]);
    } else if (type === 'environments') {
      setSelectedEnvironments([]);
    } else if (type === 'variables') {
      setSelectedVariables([]);
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setError(null);
    setResult(null);
  };

  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const text = await file.text();
      setContent(text);

      // Auto-detect format
      const format = await (window.electronAPI as any).import.detectFormat(text);
      if (format) {
        setDetectedFormat(format);
        setSelectedFormat(format);
      }

      // Validate
      const validation = await (window.electronAPI as any).import.validate(text, format || undefined);
      setValidationResult(validation);

      if (!validation.valid) {
        setError(validation.errors.map((e: any) => e.message).join(', '));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to read file');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleUrlImport = useCallback(async () => {
    if (!url) {
      setError('Please enter a URL');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const importResult = await (window.electronAPI as any).import.importFromURL(url, {
        format: selectedFormat === 'auto' ? undefined : selectedFormat,
        preview: true,
        conflictResolution,
      });

      if (importResult.success) {
        setResult(importResult);
      } else {
        setError(importResult.errors?.join(', ') || 'Import failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to import from URL');
    } finally {
      setLoading(false);
    }
  }, [url, selectedFormat]);

  const handlePasteImport = useCallback(async () => {
    if (!content) {
      setError('Please paste content');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const importResult = await (window.electronAPI as any).import.import(content, {
        format: selectedFormat === 'auto' ? undefined : selectedFormat,
        preview: true,
        conflictResolution,
      });

      if (importResult.success) {
        setResult(importResult);
      } else {
        setError(importResult.errors?.join(', ') || 'Import failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to import');
    } finally {
      setLoading(false);
    }
  }, [content, selectedFormat]);

  const handleConfirmImport = useCallback(async () => {
    if (!result) return;

    setLoading(true);
    setError(null);

    try {
      const finalResult = await (window.electronAPI as any).import.import(content, {
        format: selectedFormat === 'auto' ? undefined : selectedFormat,
        preview: false,
        conflictResolution,
      });

      if (finalResult.success) {
        onImportComplete?.(finalResult);
        onClose();
      } else {
        setError(finalResult.errors?.join(', ') || 'Import failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to import');
    } finally {
      setLoading(false);
    }
  }, [result, content, selectedFormat, onImportComplete, onClose]);

  const handleClose = () => {
    setContent('');
    setUrl('');
    setSelectedFormat('auto');
    setResult(null);
    setError(null);
    setDetectedFormat(null);
    setValidationResult(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">Import</Typography>
          <IconButton onClick={handleClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab icon={<Upload />} label="File Upload" />
            <Tab icon={<LinkIcon />} label="URL" />
            <Tab icon={<ContentPaste />} label="Paste" />
          </Tabs>
        </Box>

        {/* Import Type Selection */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            What to Import:
          </Typography>
          <FormControlLabel
            control={
              <Checkbox
                checked={importTypes.collections}
                onChange={(e) => setImportTypes({...importTypes, collections: e.target.checked})}
              />
            }
            label="Collections"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={importTypes.requests}
                onChange={(e) => setImportTypes({...importTypes, requests: e.target.checked})}
              />
            }
            label="Requests"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={importTypes.environments}
                onChange={(e) => setImportTypes({...importTypes, environments: e.target.checked})}
              />
            }
            label="Environments"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={importTypes.variables}
                onChange={(e) => setImportTypes({...importTypes, variables: e.target.checked})}
              />
            }
            label="Variables"
          />
        </Box>

        {/* Format Selector */}
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Format</InputLabel>
          <Select
            value={selectedFormat}
            label="Format"
            onChange={(e) => setSelectedFormat(e.target.value as any)}
          >
            <MenuItem value="auto">Auto-detect</MenuItem>
            <MenuItem value="postman-v2.1">Postman Collection v2.0/v2.1</MenuItem>
            <MenuItem value="curl">cURL Command</MenuItem>
            <MenuItem value="swagger-1.2">Swagger 1.2</MenuItem>
            <MenuItem value="swagger-2.0">Swagger 2.0</MenuItem>
            <MenuItem value="openapi-3.0">OpenAPI 3.0</MenuItem>
            <MenuItem value="openapi-3.1">OpenAPI 3.1</MenuItem>
            <MenuItem value="har">HAR (HTTP Archive)</MenuItem>
            <MenuItem value="insomnia-v4">Insomnia v4</MenuItem>
            <MenuItem value="insomnia-v5">Insomnia v5</MenuItem>
            <MenuItem value="raml-0.8">RAML 0.8</MenuItem>
            <MenuItem value="raml-1.0">RAML 1.0</MenuItem>
            <MenuItem value="graphql-schema">GraphQL Schema</MenuItem>
            <MenuItem value="asyncapi-2.0">AsyncAPI 2.0</MenuItem>
            <MenuItem value="asyncapi-3.0">AsyncAPI 3.0</MenuItem>
            <MenuItem value="soapui">SoapUI Project</MenuItem>
            <MenuItem value="wadl">WADL</MenuItem>
            <MenuItem value="wsdl-1.0">WSDL 1.0</MenuItem>
            <MenuItem value="wsdl-1.1">WSDL 1.1</MenuItem>
            <MenuItem value="wsdl-2.0">WSDL 2.0</MenuItem>
            <MenuItem value="protobuf-2">Protobuf 2</MenuItem>
            <MenuItem value="protobuf-3">Protobuf 3</MenuItem>
            <MenuItem value="aws-gateway">API Gateway (AWS)</MenuItem>
            <MenuItem value="azure-gateway">API Gateway (Azure)</MenuItem>
          </Select>
        </FormControl>

        {/* Conflict Resolution Selector */}
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel>If Item Exists</InputLabel>
          <Select
            value={conflictResolution}
            label="If Item Exists"
            onChange={(e) => setConflictResolution(e.target.value as any)}
          >
            <MenuItem value="merge">Merge - Combine with existing</MenuItem>
            <MenuItem value="replace">Replace - Overwrite existing</MenuItem>
            <MenuItem value="skip">Skip - Keep existing</MenuItem>
          </Select>
        </FormControl>

        {/* Detected Format */}
        {detectedFormat && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Detected format: <strong>{detectedFormat}</strong>
          </Alert>
        )}

        {/* File Upload Tab */}
        <TabPanel value={tabValue} index={0}>
          <Box
            sx={{
              border: '2px dashed',
              borderColor: 'divider',
              borderRadius: 1,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              '&:hover': {
                borderColor: 'primary.main',
                bgcolor: 'action.hover',
              },
            }}
          >
            <input
              type="file"
              id="file-upload"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
              accept=".json,.yaml,.yml,.har,.txt,.sh"
            />
            <label htmlFor="file-upload" style={{ cursor: 'pointer' }}>
              <Upload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                Click to upload or drag and drop
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Supports: JSON, YAML, HAR, cURL, etc.
              </Typography>
            </label>
          </Box>
        </TabPanel>

        {/* URL Tab */}
        <TabPanel value={tabValue} index={1}>
          <TextField
            fullWidth
            label="URL"
            placeholder="https://api.example.com/openapi.json"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button
            variant="contained"
            onClick={handleUrlImport}
            disabled={loading || !url}
            startIcon={loading ? <CircularProgress size={20} /> : <LinkIcon />}
          >
            {loading ? 'Importing...' : 'Import from URL'}
          </Button>
        </TabPanel>

        {/* Paste Tab */}
        <TabPanel value={tabValue} index={2}>
          <TextField
            fullWidth
            multiline
            rows={10}
            label="Paste content"
            placeholder="Paste Postman collection, cURL command, OpenAPI spec, etc."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            sx={{ mb: 2, fontFamily: 'monospace' }}
          />
          <Button
            variant="contained"
            onClick={handlePasteImport}
            disabled={loading || !content}
            startIcon={loading ? <CircularProgress size={20} /> : <ContentPaste />}
          >
            {loading ? 'Importing...' : 'Import'}
          </Button>
        </TabPanel>

        {/* Validation Result */}
        {validationResult && !validationResult.valid && (
          <Alert severity="error" sx={{ mt: 2 }}>
            <Typography variant="subtitle2">Validation Errors:</Typography>
            {validationResult.errors.map((err: any, idx: number) => (
              <Typography key={idx} variant="body2">
                • {err.message}
              </Typography>
            ))}
          </Alert>
        )}

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Preview Result */}
        {result && result.success && (
          <Paper elevation={2} sx={{ mt: 3, p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Import Preview
            </Typography>

            <Box sx={{ mb: 2 }}>
              <Chip
                icon={<CheckCircle />}
                label={`${selectedCollections.length}/${result.collections?.length || 0} Collections`}
                color="primary"
                sx={{ mr: 1 }}
              />
              <Chip
                icon={<CheckCircle />}
                label={`${selectedRequests.length}/${result.requests?.length || 0} Requests`}
                color="success"
                sx={{ mr: 1 }}
              />
              {importTypes.environments && result.environments && result.environments.length > 0 && (
                <Chip
                  icon={<Info />}
                  label={`${selectedEnvironments.length}/${result.environments.length} Environments`}
                  color="info"
                  sx={{ mr: 1 }}
                />
              )}
              {importTypes.variables && result.variables && result.variables.length > 0 && (
                <Chip
                  icon={<Info />}
                  label={`${selectedVariables.length}/${result.variables.length} Variables`}
                  color="info"
                />
              )}
            </Box>

            {importTypes.collections && result.collections && result.collections.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="subtitle2">
                    Collections:
                  </Typography>
                  <Box>
                    <Button size="small" onClick={() => selectAll('collections')}>Select All</Button>
                    <Button size="small" onClick={() => deselectAll('collections')}>Deselect All</Button>
                  </Box>
                </Box>
                <Paper variant="outlined" sx={{ maxHeight: 150, overflow: 'auto', p: 1 }}>
                  <List dense>
                    {result.collections.map((col) => (
                      <ListItemButton key={col.id} onClick={() => toggleSelection(col.id, 'collections')}>
                        <Checkbox checked={selectedCollections.includes(col.id)} />
                        <ListItemText
                          primary={col.name}
                          secondary={col.description}
                        />
                      </ListItemButton>
                    ))}
                  </List>
                </Paper>
              </Box>
            )}
            
            {importTypes.requests && result.requests && result.requests.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="subtitle2">
                    Requests:
                  </Typography>
                  <Box>
                    <Button size="small" onClick={() => selectAll('requests')}>Select All</Button>
                    <Button size="small" onClick={() => deselectAll('requests')}>Deselect All</Button>
                  </Box>
                </Box>
                <Paper variant="outlined" sx={{ maxHeight: 150, overflow: 'auto', p: 1 }}>
                  <List dense>
                    {result.requests.map((req) => (
                      <ListItemButton key={req.id} onClick={() => toggleSelection(req.id, 'requests')}>
                        <Checkbox checked={selectedRequests.includes(req.id)} />
                        <ListItemText
                          primary={req.name}
                          secondary={`${req.method} ${req.url}`}
                        />
                      </ListItemButton>
                    ))}
                  </List>
                </Paper>
              </Box>
            )}
            
            {importTypes.environments && result.environments && result.environments.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="subtitle2">
                    Environments:
                  </Typography>
                  <Box>
                    <Button size="small" onClick={() => selectAll('environments')}>Select All</Button>
                    <Button size="small" onClick={() => deselectAll('environments')}>Deselect All</Button>
                  </Box>
                </Box>
                <Paper variant="outlined" sx={{ maxHeight: 150, overflow: 'auto', p: 1 }}>
                  <List dense>
                    {result.environments.map((env) => (
                      <ListItemButton key={env.id} onClick={() => toggleSelection(env.id, 'environments')}>
                        <Checkbox checked={selectedEnvironments.includes(env.id)} />
                        <ListItemText primary={env.name} />
                      </ListItemButton>
                    ))}
                  </List>
                </Paper>
              </Box>
            )}
            
            {result.variables && result.variables.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="subtitle2">
                    Variables:
                  </Typography>
                  <Box>
                    <Button size="small" onClick={() => selectAll('variables')}>Select All</Button>
                    <Button size="small" onClick={() => deselectAll('variables')}>Deselect All</Button>
                  </Box>
                </Box>
                <Paper variant="outlined" sx={{ maxHeight: 150, overflow: 'auto', p: 1 }}>
                  <List dense>
                    {result.variables.map((v) => (
                      <ListItemButton key={v.key} onClick={() => toggleSelection(v.key, 'variables')}>
                        <Checkbox checked={selectedVariables.includes(v.key)} />
                        <ListItemText primary={v.key} secondary={v.value} />
                      </ListItemButton>
                    ))}
                  </List>
                </Paper>
              </Box>
            )}

            {result.warnings && result.warnings.length > 0 && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                <Typography variant="subtitle2">Warnings:</Typography>
                {result.warnings.map((warning, idx) => (
                  <Typography key={idx} variant="body2">
                    • {warning}
                  </Typography>
                ))}
              </Alert>
            )}
          </Paper>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        {result && result.success && (
          <Button
            variant="contained"
            onClick={handleConfirmImport}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <CheckCircle />}
          >
            {loading ? 'Importing...' : 'Confirm Import'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
