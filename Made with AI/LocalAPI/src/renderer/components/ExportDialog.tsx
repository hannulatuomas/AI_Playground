// Export Dialog Component
/// <reference path="../global.d.ts" />
import React, { useState, useCallback, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Alert,
  CircularProgress,
  TextField,
  Checkbox,
  FormControlLabel,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Paper,
  ListItemButton,
} from '@mui/material';
import {
  Download,
  ContentCopy,
  Close,
  CheckCircle,
  Info,
} from '@mui/icons-material';
import type { ImportExportFormat } from '../../types/import-export';

interface ExportDialogProps {
  open: boolean;
  onClose: () => void;
  selectedCollections?: string[];
  selectedRequests?: string[];
  selectedEnvironments?: string[];
  selectedVariables?: string[];
}

export function ExportDialog({ open, onClose, selectedCollections = [], selectedRequests = [], selectedEnvironments = [], selectedVariables = [] }: ExportDialogProps) {
  const [format, setFormat] = useState<ImportExportFormat>('postman-v2.1');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [prettify, setPrettify] = useState(true);
  const [exportTypes, setExportTypes] = useState<{
    collections: boolean;
    requests: boolean;
    environments: boolean;
    variables: boolean;
  }>({
    collections: true,
    requests: false,
    environments: false,
    variables: false,
  });
  const [preview, setPreview] = useState<string | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  
  // Local selection state
  const [collections, setCollections] = useState<any[]>([]);
  const [requests, setRequests] = useState<any[]>([]);
  const [environments, setEnvironments] = useState<any[]>([]);
  const [variables, setVariables] = useState<any[]>([]);
  const [localSelectedCollections, setLocalSelectedCollections] = useState<string[]>(selectedCollections);
  const [localSelectedRequests, setLocalSelectedRequests] = useState<string[]>(selectedRequests);
  const [localSelectedEnvironments, setLocalSelectedEnvironments] = useState<string[]>(selectedEnvironments);
  const [localSelectedVariables, setLocalSelectedVariables] = useState<string[]>(selectedVariables);
  
  // Load data on mount
  useEffect(() => {
    if (open) {
      loadData();
    }
  }, [open]);
  
  const loadData = async () => {
    try {
      const cols = await window.api.database.getAllCollections();
      setCollections(cols || []);
      
      const envs = await window.api.database.getAllEnvironments();
      setEnvironments(envs || []);
      
      // Load all requests from all collections
      const allRequests: any[] = [];
      for (const col of cols || []) {
        const reqs = await window.api.database.getRequestsByCollection(col.id);
        allRequests.push(...(reqs || []));
      }
      setRequests(allRequests);
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  };
  
  const toggleSelection = (id: string, type: 'collections' | 'requests' | 'environments' | 'variables') => {
    if (type === 'collections') {
      setLocalSelectedCollections(prev => 
        prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
      );
    } else if (type === 'requests') {
      setLocalSelectedRequests(prev => 
        prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
      );
    } else if (type === 'environments') {
      setLocalSelectedEnvironments(prev => 
        prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
      );
    } else if (type === 'variables') {
      setLocalSelectedVariables(prev => 
        prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
      );
    }
  };
  
  const selectAll = (type: 'collections' | 'requests' | 'environments' | 'variables') => {
    if (type === 'collections') {
      setLocalSelectedCollections(collections.map(c => c.id));
    } else if (type === 'requests') {
      setLocalSelectedRequests(requests.map(r => r.id));
    } else if (type === 'environments') {
      setLocalSelectedEnvironments(environments.map(e => e.id));
    }
  };
  
  const deselectAll = (type: 'collections' | 'requests' | 'environments' | 'variables') => {
    if (type === 'collections') {
      setLocalSelectedCollections([]);
    } else if (type === 'requests') {
      setLocalSelectedRequests([]);
    } else if (type === 'environments') {
      setLocalSelectedEnvironments([]);
    } else if (type === 'variables') {
      setLocalSelectedVariables([]);
    }
  };

  const handleExportToFile = useCallback(async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Check if at least one type is selected
      const hasSelection = 
        (exportTypes.collections && localSelectedCollections.length > 0) ||
        (exportTypes.requests && localSelectedRequests.length > 0) ||
        (exportTypes.environments && localSelectedEnvironments.length > 0) ||
        (exportTypes.variables && localSelectedVariables.length > 0);

      if (!hasSelection) {
        throw new Error('No items selected for export');
      }

      // Export all selected types
      let combinedData = '';
      
      if (exportTypes.collections && localSelectedCollections.length > 0) {
        const result = await (window.electronAPI as any).export.exportCollections(
          localSelectedCollections,
          format,
          { prettify }
        );
        if (result.success && result.data) {
          combinedData += result.data;
        }
      }

      if (exportTypes.requests && localSelectedRequests.length > 0) {
        const result = await (window.electronAPI as any).export.exportRequests(
          localSelectedRequests,
          format,
          { prettify }
        );
        if (result.success && result.data) {
          combinedData += (combinedData ? '\n\n' : '') + result.data;
        }
      }

      if (combinedData) {
        const fileName = `export_${Date.now()}.${getFileExtension(format)}`;
        await (window.electronAPI as any).export.saveToFile(combinedData, fileName, format);
        setSuccess(true);
      } else {
        setError('Export failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setLoading(false);
    }
  }, [exportTypes, localSelectedCollections, localSelectedRequests, localSelectedEnvironments, localSelectedVariables, format, prettify]);

  const handlePreview = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      let combinedData = '';
      
      if (exportTypes.collections && localSelectedCollections.length > 0) {
        const result = await (window.electronAPI as any).export.exportCollections(
          localSelectedCollections,
          format,
          { prettify }
        );
        if (result.success && result.data) {
          combinedData += result.data;
        }
      }

      if (exportTypes.requests && localSelectedRequests.length > 0) {
        const result = await (window.electronAPI as any).export.exportRequests(
          localSelectedRequests,
          format,
          { prettify }
        );
        if (result.success && result.data) {
          combinedData += (combinedData ? '\n\n' : '') + result.data;
        }
      }

      if (combinedData) {
        setPreview(combinedData);
        setShowPreview(true);
      } else {
        setError('No data to preview');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Preview failed');
    } finally {
      setLoading(false);
    }
  }, [exportTypes, localSelectedCollections, localSelectedRequests, format, prettify]);

  const handleCopyToClipboard = useCallback(async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      let combinedData = '';
      
      if (exportTypes.collections && localSelectedCollections.length > 0) {
        const result = await (window.electronAPI as any).export.exportCollections(
          localSelectedCollections,
          format,
          { prettify }
        );
        if (result.success && result.data) {
          combinedData += result.data;
        }
      }

      if (exportTypes.requests && localSelectedRequests.length > 0) {
        const result = await (window.electronAPI as any).export.exportRequests(
          localSelectedRequests,
          format,
          { prettify }
        );
        if (result.success && result.data) {
          combinedData += (combinedData ? '\n\n' : '') + result.data;
        }
      }

      if (combinedData) {
        await (window.electronAPI as any).export.copyToClipboard(combinedData);
        setSuccess(true);
      } else {
        setError('No data to copy');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setLoading(false);
    }
  }, [exportTypes, localSelectedCollections, localSelectedRequests, format, prettify]);

  const handleClose = () => {
    setError(null);
    setSuccess(false);
    onClose();
  };

  const getFileExtension = (fmt: ImportExportFormat): string => {
    const extensions: Record<string, string> = {
      'postman-v2.1': 'json',
      'curl': 'sh',
      'openapi-3.0': 'json',
      'insomnia-v4': 'json',
      'har': 'har',
      'graphql-schema': 'graphql',
      'asyncapi-2.0': 'json',
    };
    return extensions[fmt] || 'txt';
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">Export</Typography>
          <IconButton onClick={handleClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {/* Export Types - Multiple Selection */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            What to Export:
          </Typography>
          <FormControlLabel
            control={
              <Checkbox
                checked={exportTypes.collections}
                onChange={(e) => setExportTypes({...exportTypes, collections: e.target.checked})}
              />
            }
            label={`Collections (${localSelectedCollections.length})`}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={exportTypes.requests}
                onChange={(e) => setExportTypes({...exportTypes, requests: e.target.checked})}
              />
            }
            label={`Requests (${localSelectedRequests.length})`}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={exportTypes.environments}
                onChange={(e) => setExportTypes({...exportTypes, environments: e.target.checked})}
              />
            }
            label={`Environments (${localSelectedEnvironments.length})`}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={exportTypes.variables}
                onChange={(e) => setExportTypes({...exportTypes, variables: e.target.checked})}
              />
            }
            label={`Variables (${localSelectedVariables.length})`}
          />
        </Box>

        {/* Format Selector */}
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Format</InputLabel>
          <Select
            value={format}
            label="Format"
            onChange={(e) => setFormat(e.target.value as ImportExportFormat)}
          >
            <MenuItem value="postman-v2.1">Postman Collection v2.0/v2.1</MenuItem>
            <MenuItem value="curl">cURL Commands</MenuItem>
            <MenuItem value="swagger-1.2">Swagger 1.2</MenuItem>
            <MenuItem value="swagger-2.0">Swagger 2.0</MenuItem>
            <MenuItem value="openapi-3.0">OpenAPI 3.0</MenuItem>
            <MenuItem value="openapi-3.1">OpenAPI 3.1</MenuItem>
            <MenuItem value="insomnia-v4">Insomnia v4</MenuItem>
            <MenuItem value="insomnia-v5">Insomnia v5</MenuItem>
            <MenuItem value="har">HAR (HTTP Archive)</MenuItem>
            <MenuItem value="graphql-schema">GraphQL Schema</MenuItem>
            <MenuItem value="asyncapi-2.0">AsyncAPI 2.0</MenuItem>
            <MenuItem value="asyncapi-3.0">AsyncAPI 3.0</MenuItem>
            <MenuItem value="soapui">SoapUI Project</MenuItem>
            <MenuItem value="raml-0.8">RAML 0.8</MenuItem>
            <MenuItem value="raml-1.0">RAML 1.0</MenuItem>
            <MenuItem value="wadl">WADL</MenuItem>
            <MenuItem value="protobuf-2">Protobuf 2</MenuItem>
            <MenuItem value="protobuf-3">Protobuf 3</MenuItem>
            <MenuItem value="wsdl-1.0">WSDL 1.0</MenuItem>
            <MenuItem value="wsdl-1.1">WSDL 1.1</MenuItem>
            <MenuItem value="wsdl-2.0">WSDL 2.0</MenuItem>
            <MenuItem value="aws-gateway">API Gateway (AWS)</MenuItem>
            <MenuItem value="azure-gateway">API Gateway (Azure)</MenuItem>
          </Select>
        </FormControl>

        {/* Selection Lists - Show all enabled types */}
        {exportTypes.collections && (
          <Box sx={{ mb: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="subtitle2">Collections:</Typography>
              <Box>
                <Button size="small" onClick={() => selectAll('collections')}>Select All</Button>
                <Button size="small" onClick={() => deselectAll('collections')}>Deselect All</Button>
              </Box>
            </Box>
            <Paper variant="outlined" sx={{ maxHeight: 150, overflow: 'auto', p: 1 }}>
              <List dense>
                {collections.map(col => (
                  <ListItemButton key={col.id} onClick={() => toggleSelection(col.id, 'collections')}>
                    <Checkbox checked={localSelectedCollections.includes(col.id)} />
                    <ListItemText primary={col.name} secondary={col.description} />
                  </ListItemButton>
                ))}
              </List>
            </Paper>
          </Box>
        )}

        {exportTypes.requests && (
          <Box sx={{ mb: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="subtitle2">Requests:</Typography>
              <Box>
                <Button size="small" onClick={() => selectAll('requests')}>Select All</Button>
                <Button size="small" onClick={() => deselectAll('requests')}>Deselect All</Button>
              </Box>
            </Box>
            <Paper variant="outlined" sx={{ maxHeight: 150, overflow: 'auto', p: 1 }}>
              <List dense>
                {requests.map(req => (
                  <ListItemButton key={req.id} onClick={() => toggleSelection(req.id, 'requests')}>
                    <Checkbox checked={localSelectedRequests.includes(req.id)} />
                    <ListItemText primary={req.name} secondary={`${req.method} ${req.url}`} />
                  </ListItemButton>
                ))}
              </List>
            </Paper>
          </Box>
        )}

        {exportTypes.environments && (
          <Box sx={{ mb: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="subtitle2">Environments:</Typography>
              <Box>
                <Button size="small" onClick={() => selectAll('environments')}>Select All</Button>
                <Button size="small" onClick={() => deselectAll('environments')}>Deselect All</Button>
              </Box>
            </Box>
            <Paper variant="outlined" sx={{ maxHeight: 150, overflow: 'auto', p: 1 }}>
              <List dense>
                {environments.map(env => (
                  <ListItemButton key={env.id} onClick={() => toggleSelection(env.id, 'environments')}>
                    <Checkbox checked={localSelectedEnvironments.includes(env.id)} />
                    <ListItemText primary={env.name} />
                  </ListItemButton>
                ))}
              </List>
            </Paper>
          </Box>
        )}

        {/* Prettify Option */}
        <FormControlLabel
          control={
            <Checkbox
              checked={prettify}
              onChange={(e) => setPrettify(e.target.checked)}
            />
          }
          label="Prettify output (formatted JSON/YAML)"
        />

        {/* Selected Items Summary */}
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Selected Items:
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {exportTypes.collections && `${localSelectedCollections.length} collection(s) `}
            {exportTypes.requests && `${localSelectedRequests.length} request(s) `}
            {exportTypes.environments && `${localSelectedEnvironments.length} environment(s) `}
            {exportTypes.variables && `${localSelectedVariables.length} variable(s)`}
          </Typography>
        </Box>

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Success Display */}
        {success && (
          <Alert severity="success" sx={{ mt: 2 }} icon={<CheckCircle />}>
            Export completed successfully!
          </Alert>
        )}

        {/* Preview Display */}
        {showPreview && preview && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Export Preview:
            </Typography>
            <Paper
              elevation={1}
              sx={{
                p: 2,
                maxHeight: 300,
                overflow: 'auto',
                bgcolor: 'grey.100',
                fontFamily: 'monospace',
                fontSize: '0.875rem',
              }}
            >
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                {preview.substring(0, 1000)}{preview.length > 1000 ? '...' : ''}
              </pre>
            </Paper>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Showing first 1000 characters. Full export: {preview.length} characters
            </Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          variant="outlined"
          onClick={handlePreview}
          disabled={loading || (
            (exportTypes.collections && localSelectedCollections.length === 0) &&
            (exportTypes.requests && localSelectedRequests.length === 0) &&
            (exportTypes.environments && localSelectedEnvironments.length === 0) &&
            (exportTypes.variables && localSelectedVariables.length === 0)
          )}
          startIcon={loading ? <CircularProgress size={20} /> : <Info />}
        >
          Preview
        </Button>
        <Button
          variant="outlined"
          onClick={handleCopyToClipboard}
          disabled={loading || (
            (exportTypes.collections && localSelectedCollections.length === 0) &&
            (exportTypes.requests && localSelectedRequests.length === 0) &&
            (exportTypes.environments && localSelectedEnvironments.length === 0) &&
            (exportTypes.variables && localSelectedVariables.length === 0)
          )}
          startIcon={loading ? <CircularProgress size={20} /> : <ContentCopy />}
        >
          Copy to Clipboard
        </Button>
        <Button
          variant="contained"
          onClick={handleExportToFile}
          disabled={loading || (
            (exportTypes.collections && localSelectedCollections.length === 0) &&
            (exportTypes.requests && localSelectedRequests.length === 0) &&
            (exportTypes.environments && localSelectedEnvironments.length === 0) &&
            (exportTypes.variables && localSelectedVariables.length === 0)
          )}
          startIcon={loading ? <CircularProgress size={20} /> : <Download />}
        >
          Export to File
        </Button>
      </DialogActions>
    </Dialog>
  );
}
