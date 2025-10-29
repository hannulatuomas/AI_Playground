// Variable Extractor Dialog Component
// Provides UI for extracting variables from responses

import React, { useState, useEffect } from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import type { Response, VariableScope } from '../../types/models';

interface VariableExtractorDialogProps {
  open: boolean;
  onClose: () => void;
  response: Response | null;
  selectedValue?: any;
  selectedPath?: string;
  extractionType?: 'json' | 'xml' | 'header';
}

const VariableExtractorDialog: React.FC<VariableExtractorDialogProps> = ({
  open,
  onClose,
  response,
  selectedValue,
  selectedPath,
  extractionType: initialType,
}) => {
  const [variableName, setVariableName] = useState('');
  const [scope, setScope] = useState<VariableScope>('global');
  const [path, setPath] = useState(selectedPath || '');
  const [extractionType, setExtractionType] = useState<'jsonpath' | 'xpath' | 'regex' | 'header'>(
    initialType === 'json' ? 'jsonpath' : initialType === 'xml' ? 'xpath' : 'header'
  );
  const [extractedValue, setExtractedValue] = useState<any>(selectedValue);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedPath) {
      setPath(selectedPath);
    }
    if (selectedValue !== undefined) {
      setExtractedValue(selectedValue);
    }
  }, [selectedPath, selectedValue]);

  useEffect(() => {
    if (initialType) {
      setExtractionType(
        initialType === 'json' ? 'jsonpath' : initialType === 'xml' ? 'xpath' : 'header'
      );
    }
  }, [initialType]);

  const handleExtract = async () => {
    if (!response) {
      setError('No response available');
      return;
    }

    if (!path.trim()) {
      setError('Path/pattern is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let result;

      switch (extractionType) {
        case 'jsonpath':
          result = await window.electronAPI.extractor.extractFromJSON(
            response.body,
            path,
            variableName || 'temp',
            scope
          );
          break;

        case 'xpath':
          result = await window.electronAPI.extractor.extractFromXML(
            typeof response.body === 'string' ? response.body : JSON.stringify(response.body),
            path,
            variableName || 'temp',
            scope
          );
          break;

        case 'header':
          result = await window.electronAPI.extractor.extractFromHeader(
            response.headers,
            path,
            variableName || 'temp',
            scope
          );
          break;

        case 'regex':
          const content =
            typeof response.body === 'string' ? response.body : JSON.stringify(response.body);
          result = await window.electronAPI.extractor.extractWithRegex(
            content,
            path,
            variableName || 'temp',
            scope,
            'body'
          );
          break;
      }

      if (result.success) {
        setExtractedValue(result.value);
        setError(null);
      } else {
        setError(result.error || 'Extraction failed');
        setExtractedValue(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Extraction failed');
      setExtractedValue(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!variableName.trim()) {
      setError('Variable name is required');
      return;
    }

    if (extractedValue === null || extractedValue === undefined) {
      setError('No value extracted. Please extract a value first.');
      return;
    }

    try {
      // Get old value if exists
      const existingVars = await window.electronAPI.variables.get(scope);
      const oldValue = existingVars[variableName];

      // Set the variable
      await window.electronAPI.variables.set(scope, variableName, extractedValue);

      // Record history
      await window.electronAPI.extractor.recordHistory(
        variableName,
        oldValue,
        extractedValue,
        scope,
        `${extractionType}:${path}`
      );

      setSuccess(true);
      setTimeout(() => {
        onClose();
        resetForm();
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save variable');
    }
  };

  const resetForm = () => {
    setVariableName('');
    setScope('global');
    setPath('');
    setExtractedValue(null);
    setError(null);
    setSuccess(false);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const copyValue = () => {
    if (extractedValue !== null && extractedValue !== undefined) {
      navigator.clipboard.writeText(
        typeof extractedValue === 'string' ? extractedValue : JSON.stringify(extractedValue, null, 2)
      );
    }
  };

  const formatValue = (value: any): string => {
    if (value === null) return 'null';
    if (value === undefined) return 'undefined';
    if (typeof value === 'string') return value;
    return JSON.stringify(value, null, 2);
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Extract Variable from Response</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          {success && (
            <Alert severity="success" icon={<CheckCircleIcon />}>
              Variable saved successfully!
            </Alert>
          )}

          {error && (
            <Alert severity="error" icon={<ErrorIcon />}>
              {error}
            </Alert>
          )}

          <TextField
            label="Variable Name"
            value={variableName}
            onChange={(e) => setVariableName(e.target.value)}
            fullWidth
            required
            placeholder="e.g., authToken, userId, responseData"
            helperText="Enter a unique name for this variable"
          />

          <FormControl fullWidth>
            <InputLabel>Scope</InputLabel>
            <Select value={scope} onChange={(e) => setScope(e.target.value as VariableScope)} label="Scope">
              <MenuItem value="global">Global</MenuItem>
              <MenuItem value="environment">Environment</MenuItem>
              <MenuItem value="collection">Collection</MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth>
            <InputLabel>Extraction Method</InputLabel>
            <Select
              value={extractionType}
              onChange={(e) => setExtractionType(e.target.value as any)}
              label="Extraction Method"
            >
              <MenuItem value="jsonpath">JSONPath (for JSON responses)</MenuItem>
              <MenuItem value="xpath">XPath (for XML responses)</MenuItem>
              <MenuItem value="header">Header Value</MenuItem>
              <MenuItem value="regex">Regular Expression</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label={
              extractionType === 'jsonpath'
                ? 'JSONPath Expression'
                : extractionType === 'xpath'
                ? 'XPath Expression'
                : extractionType === 'header'
                ? 'Header Name'
                : 'Regex Pattern'
            }
            value={path}
            onChange={(e) => setPath(e.target.value)}
            fullWidth
            required
            multiline={extractionType === 'regex'}
            rows={extractionType === 'regex' ? 2 : 1}
            placeholder={
              extractionType === 'jsonpath'
                ? '$.data.token or $.users[0].id'
                : extractionType === 'xpath'
                ? '/root/element/value'
                : extractionType === 'header'
                ? 'Authorization or X-Custom-Header'
                : '(\\d+) or "token":\\s*"([^"]+)"'
            }
            helperText={
              extractionType === 'jsonpath'
                ? 'Use JSONPath syntax to query JSON data'
                : extractionType === 'xpath'
                ? 'Use XPath syntax to query XML data'
                : extractionType === 'header'
                ? 'Enter the header name (case-insensitive)'
                : 'Use regex with capturing groups'
            }
          />

          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button variant="outlined" onClick={handleExtract} disabled={loading || !path.trim()}>
              {loading ? 'Extracting...' : 'Test Extraction'}
            </Button>
            {extractedValue !== null && extractedValue !== undefined && (
              <Chip
                label="Value extracted"
                color="success"
                size="small"
                icon={<CheckCircleIcon />}
              />
            )}
          </Box>

          {extractedValue !== null && extractedValue !== undefined && (
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="subtitle2">Extracted Value:</Typography>
                <Tooltip title="Copy to clipboard">
                  <IconButton size="small" onClick={copyValue}>
                    <ContentCopyIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              <Box
                sx={{
                  p: 2,
                  backgroundColor: (theme) =>
                    theme.palette.mode === 'dark' ? '#1e1e1e' : '#f5f5f5',
                  borderRadius: 1,
                  maxHeight: '200px',
                  overflow: 'auto',
                }}
              >
                <pre
                  style={{
                    margin: 0,
                    fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                    fontSize: '0.875rem',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {formatValue(extractedValue)}
                </pre>
              </Box>
            </Box>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          onClick={handleSave}
          variant="contained"
          disabled={!variableName.trim() || extractedValue === null || extractedValue === undefined || success}
        >
          Save Variable
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default VariableExtractorDialog;
