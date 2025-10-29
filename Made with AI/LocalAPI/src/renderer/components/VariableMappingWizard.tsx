// Variable Mapping Wizard Component
// Allows batch extraction of multiple variables at once

import React, { useState } from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import IconButton from '@mui/material/IconButton';
import Chip from '@mui/material/Chip';
import Alert from '@mui/material/Alert';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import type { Response, VariableScope } from '../../types/models';

interface VariableMapping {
  id: string;
  variableName: string;
  path: string;
  scope: VariableScope;
  extractionType: 'jsonpath' | 'xpath' | 'header' | 'regex';
  extractedValue?: any;
  success?: boolean;
  error?: string;
}

interface VariableMappingWizardProps {
  open: boolean;
  onClose: () => void;
  response: Response | null;
}

const VariableMappingWizard: React.FC<VariableMappingWizardProps> = ({
  open,
  onClose,
  response,
}) => {
  const [mappings, setMappings] = useState<VariableMapping[]>([]);
  const [tested, setTested] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const addMapping = () => {
    const newMapping: VariableMapping = {
      id: `mapping-${Date.now()}`,
      variableName: '',
      path: '',
      scope: 'global',
      extractionType: 'jsonpath',
    };
    setMappings([...mappings, newMapping]);
    setTested(false);
  };

  const updateMapping = (id: string, updates: Partial<VariableMapping>) => {
    setMappings(mappings.map((m) => (m.id === id ? { ...m, ...updates } : m)));
    setTested(false);
  };

  const removeMapping = (id: string) => {
    setMappings(mappings.filter((m) => m.id !== id));
    setTested(false);
  };

  const testMappings = async () => {
    if (!response) {
      setError('No response available');
      return;
    }

    setError(null);
    const updatedMappings = [...mappings];

    for (const mapping of updatedMappings) {
      if (!mapping.variableName || !mapping.path) {
        mapping.success = false;
        mapping.error = 'Variable name and path are required';
        continue;
      }

      try {
        let result;

        switch (mapping.extractionType) {
          case 'jsonpath':
            result = await window.electronAPI.extractor.extractFromJSON(
              response.body,
              mapping.path,
              mapping.variableName,
              mapping.scope
            );
            break;

          case 'xpath':
            result = await window.electronAPI.extractor.extractFromXML(
              typeof response.body === 'string' ? response.body : JSON.stringify(response.body),
              mapping.path,
              mapping.variableName,
              mapping.scope
            );
            break;

          case 'header':
            result = await window.electronAPI.extractor.extractFromHeader(
              response.headers,
              mapping.path,
              mapping.variableName,
              mapping.scope
            );
            break;

          case 'regex':
            const content =
              typeof response.body === 'string' ? response.body : JSON.stringify(response.body);
            result = await window.electronAPI.extractor.extractWithRegex(
              content,
              mapping.path,
              mapping.variableName,
              mapping.scope,
              'body'
            );
            break;
        }

        mapping.success = result.success;
        mapping.extractedValue = result.value;
        mapping.error = result.error;
      } catch (err) {
        mapping.success = false;
        mapping.error = err instanceof Error ? err.message : 'Extraction failed';
      }
    }

    setMappings(updatedMappings);
    setTested(true);
  };

  const saveMappings = async () => {
    const successfulMappings = mappings.filter((m) => m.success);

    if (successfulMappings.length === 0) {
      setError('No successful extractions to save');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      for (const mapping of successfulMappings) {
        // Get old value if exists
        const existingVars = await window.electronAPI.variables.get(mapping.scope);
        const oldValue = existingVars[mapping.variableName];

        // Set the variable
        await window.electronAPI.variables.set(
          mapping.scope,
          mapping.variableName,
          mapping.extractedValue
        );

        // Record history
        await window.electronAPI.extractor.recordHistory(
          mapping.variableName,
          oldValue,
          mapping.extractedValue,
          mapping.scope,
          `batch-${mapping.extractionType}:${mapping.path}`
        );
      }

      setSuccess(true);
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save variables');
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    setMappings([]);
    setTested(false);
    setError(null);
    setSuccess(false);
    onClose();
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'string') {
      return value.length > 30 ? value.substring(0, 30) + '...' : value;
    }
    const str = JSON.stringify(value);
    return str.length > 30 ? str.substring(0, 30) + '...' : str;
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
      <DialogTitle>Variable Mapping Wizard</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          {success && (
            <Alert severity="success" icon={<CheckCircleIcon />}>
              Successfully saved {mappings.filter((m) => m.success).length} variables!
            </Alert>
          )}

          {error && <Alert severity="error">{error}</Alert>}

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Define multiple variable extractions and test them all at once
            </Typography>
            <Button startIcon={<AddIcon />} onClick={addMapping} size="small">
              Add Mapping
            </Button>
          </Box>

          {mappings.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography color="text.secondary">
                Click "Add Mapping" to start defining variable extractions
              </Typography>
            </Box>
          ) : (
            <TableContainer sx={{ maxHeight: 400 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>Variable Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Path/Pattern</TableCell>
                    <TableCell>Scope</TableCell>
                    <TableCell>Result</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mappings.map((mapping) => (
                    <TableRow key={mapping.id}>
                      <TableCell>
                        <TextField
                          size="small"
                          value={mapping.variableName}
                          onChange={(e) =>
                            updateMapping(mapping.id, { variableName: e.target.value })
                          }
                          placeholder="variableName"
                          fullWidth
                        />
                      </TableCell>
                      <TableCell>
                        <FormControl size="small" fullWidth>
                          <Select
                            value={mapping.extractionType}
                            onChange={(e) =>
                              updateMapping(mapping.id, {
                                extractionType: e.target.value as any,
                              })
                            }
                          >
                            <MenuItem value="jsonpath">JSONPath</MenuItem>
                            <MenuItem value="xpath">XPath</MenuItem>
                            <MenuItem value="header">Header</MenuItem>
                            <MenuItem value="regex">Regex</MenuItem>
                          </Select>
                        </FormControl>
                      </TableCell>
                      <TableCell>
                        <TextField
                          size="small"
                          value={mapping.path}
                          onChange={(e) => updateMapping(mapping.id, { path: e.target.value })}
                          placeholder={
                            mapping.extractionType === 'jsonpath'
                              ? '$.data.token'
                              : mapping.extractionType === 'xpath'
                              ? '/root/element'
                              : mapping.extractionType === 'header'
                              ? 'Header-Name'
                              : 'regex pattern'
                          }
                          fullWidth
                        />
                      </TableCell>
                      <TableCell>
                        <FormControl size="small" fullWidth>
                          <Select
                            value={mapping.scope}
                            onChange={(e) =>
                              updateMapping(mapping.id, { scope: e.target.value as VariableScope })
                            }
                          >
                            <MenuItem value="global">Global</MenuItem>
                            <MenuItem value="environment">Environment</MenuItem>
                            <MenuItem value="collection">Collection</MenuItem>
                          </Select>
                        </FormControl>
                      </TableCell>
                      <TableCell>
                        {tested ? (
                          mapping.success ? (
                            <Chip
                              icon={<CheckCircleIcon />}
                              label={formatValue(mapping.extractedValue)}
                              color="success"
                              size="small"
                            />
                          ) : (
                            <Chip
                              icon={<ErrorIcon />}
                              label="Failed"
                              color="error"
                              size="small"
                            />
                          )
                        ) : (
                          <Chip label="Not tested" size="small" />
                        )}
                      </TableCell>
                      <TableCell>
                        <IconButton size="small" onClick={() => removeMapping(mapping.id)}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {mappings.length > 0 && (
            <Button
              variant="outlined"
              startIcon={<PlayArrowIcon />}
              onClick={testMappings}
              disabled={!response}
              fullWidth
            >
              Test All Mappings
            </Button>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          onClick={saveMappings}
          variant="contained"
          disabled={!tested || mappings.filter((m) => m.success).length === 0 || saving || success}
        >
          {saving ? 'Saving...' : 'Save All Variables'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default VariableMappingWizard;
