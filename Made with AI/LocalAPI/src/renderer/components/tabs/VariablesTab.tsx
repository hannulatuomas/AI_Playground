import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Checkbox,
  Chip,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';
import type { Variable } from '../../../types/models';

interface VariablesTabProps {
  collectionId?: string;
}

interface VariableRow extends Variable {
  id?: string;
}

const VariablesTab: React.FC<VariablesTabProps> = ({ collectionId }) => {
  const [scope, setScope] = useState<'global' | 'environment' | 'collection'>('global');
  const [variables, setVariables] = useState<VariableRow[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showSecrets, setShowSecrets] = useState<Set<string>>(new Set());
  
  // Dialog state
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');
  const [currentVariable, setCurrentVariable] = useState<Partial<VariableRow>>({
    key: '',
    value: '',
    type: 'string',
    scope: 'global',
    enabled: true,
    description: '',
  });

  // Load variables when scope changes
  useEffect(() => {
    loadVariables();
  }, [scope]);

  const loadVariables = async () => {
    try {
      const scopeKey = scope === 'collection' && collectionId ? collectionId : scope;
      const vars = await window.api.database.getVariablesByScope(scopeKey);
      setVariables(Array.isArray(vars) ? vars : []);
    } catch (error) {
      console.error('Failed to load variables:', error);
      setVariables([]);
    }
  };

  const handleAddVariable = () => {
    setCurrentVariable({
      key: '',
      value: '',
      type: 'string',
      scope,
      enabled: true,
      description: '',
    });
    setDialogMode('create');
    setDialogOpen(true);
  };

  const handleEditVariable = (variable: VariableRow) => {
    setCurrentVariable(variable);
    setDialogMode('edit');
    setDialogOpen(true);
  };

  const handleSaveVariable = async () => {
    try {
      if (dialogMode === 'create') {
        await window.api.database.createVariable({
          ...currentVariable,
          scope: scope === 'collection' && collectionId ? collectionId : scope,
        } as Variable);
      } else if (currentVariable.key) {
        const scopeKey = scope === 'collection' && collectionId ? collectionId : scope;
        await window.api.database.updateVariable(
          scopeKey,
          currentVariable.key,
          currentVariable.value as string
        );
      }
      await loadVariables();
      setDialogOpen(false);
    } catch (error) {
      console.error('Failed to save variable:', error);
    }
  };

  const handleDeleteVariable = async (key: string) => {
    try {
      const scopeKey = scope === 'collection' && collectionId ? collectionId : scope;
      await window.api.database.deleteVariable(scopeKey, key);
      await loadVariables();
    } catch (error) {
      console.error('Failed to delete variable:', error);
    }
  };

  const toggleSecretVisibility = (key: string) => {
    setShowSecrets(prev => {
      const newSet = new Set(prev);
      if (newSet.has(key)) {
        newSet.delete(key);
      } else {
        newSet.add(key);
      }
      return newSet;
    });
  };

  const copyToClipboard = (value: string) => {
    navigator.clipboard.writeText(value);
  };

  const renderValue = (variable: VariableRow) => {
    if (variable.type === 'secret' && !showSecrets.has(variable.key)) {
      return '••••••••';
    }
    return String(variable.value);
  };

  const getScopeColor = (scopeValue: string) => {
    switch (scopeValue) {
      case 'global':
        return 'primary';
      case 'environment':
        return 'secondary';
      case 'collection':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h6">Variables</Typography>
          <Typography variant="body2" color="text.secondary">
            Manage variables for use in requests with <code>{'{{variableName}}'}</code>
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddVariable}
        >
          Add Variable
        </Button>
      </Box>

      {/* Scope Selector */}
      <Box sx={{ mb: 2 }}>
        <Tabs
          value={scope}
          onChange={(_, newValue) => setScope(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Global" value="global" />
          <Tab label="Environment" value="environment" />
          {collectionId && <Tab label="Collection" value="collection" />}
        </Tabs>
      </Box>

      {/* Info Alert */}
      <Alert severity="info" sx={{ mb: 2 }}>
        <Typography variant="body2">
          <strong>{scope === 'global' ? 'Global' : scope === 'environment' ? 'Environment' : 'Collection'} Variables:</strong>{' '}
          {scope === 'global' && 'Available across all requests and collections'}
          {scope === 'environment' && 'Scoped to the active environment'}
          {scope === 'collection' && 'Scoped to this collection only'}
        </Typography>
      </Alert>

      {/* Variables Table */}
      {variables.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            No variables defined
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Add variables to reuse values across requests
          </Typography>
          <Button
            startIcon={<AddIcon />}
            onClick={handleAddVariable}
            sx={{ mt: 2 }}
          >
            Add First Variable
          </Button>
        </Box>
      ) : (
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell width="40px">
                  <Checkbox disabled size="small" />
                </TableCell>
                <TableCell>Key</TableCell>
                <TableCell>Value</TableCell>
                <TableCell width="100px">Type</TableCell>
                <TableCell>Description</TableCell>
                <TableCell width="120px" align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {variables.map((variable) => (
                <TableRow
                  key={variable.key}
                  sx={{
                    opacity: variable.enabled ? 1 : 0.5,
                    '&:hover': { bgcolor: 'action.hover' },
                  }}
                >
                  <TableCell>
                    <Checkbox
                      size="small"
                      checked={variable.enabled}
                      onChange={async (e) => {
                        const scopeKey = scope === 'collection' && collectionId ? collectionId : scope;
                        await window.api.database.updateVariable(
                          scopeKey,
                          variable.key,
                          variable.value
                        );
                        await loadVariables();
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace">
                      {variable.key}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" fontFamily="monospace" sx={{ flex: 1 }}>
                        {renderValue(variable)}
                      </Typography>
                      {variable.type === 'secret' && (
                        <IconButton
                          size="small"
                          onClick={() => toggleSecretVisibility(variable.key)}
                        >
                          {showSecrets.has(variable.key) ? (
                            <VisibilityOffIcon fontSize="small" />
                          ) : (
                            <VisibilityIcon fontSize="small" />
                          )}
                        </IconButton>
                      )}
                      <Tooltip title="Copy value">
                        <IconButton
                          size="small"
                          onClick={() => copyToClipboard(String(variable.value))}
                        >
                          <CopyIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={variable.type}
                      size="small"
                      variant="outlined"
                      color={variable.type === 'secret' ? 'error' : 'default'}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {variable.description || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => handleEditVariable(variable)}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteVariable(variable.key)}
                        color="error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Variable Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {dialogMode === 'create' ? 'Add Variable' : 'Edit Variable'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <TextField
              label="Key"
              fullWidth
              value={currentVariable.key}
              onChange={(e) => setCurrentVariable({ ...currentVariable, key: e.target.value })}
              placeholder="e.g., apiKey, baseUrl, userId"
              disabled={dialogMode === 'edit'}
              helperText="Use in requests as {{variableName}}"
            />
            
            <TextField
              label="Value"
              fullWidth
              value={currentVariable.value}
              onChange={(e) => setCurrentVariable({ ...currentVariable, value: e.target.value })}
              placeholder="Variable value"
              type={currentVariable.type === 'secret' ? 'password' : 'text'}
            />

            <FormControl fullWidth>
              <InputLabel>Type</InputLabel>
              <Select
                value={currentVariable.type}
                label="Type"
                onChange={(e) => setCurrentVariable({ ...currentVariable, type: e.target.value as any })}
              >
                <MenuItem value="string">String</MenuItem>
                <MenuItem value="number">Number</MenuItem>
                <MenuItem value="boolean">Boolean</MenuItem>
                <MenuItem value="secret">Secret</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="Description"
              fullWidth
              multiline
              rows={2}
              value={currentVariable.description}
              onChange={(e) => setCurrentVariable({ ...currentVariable, description: e.target.value })}
              placeholder="Optional description"
            />

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Checkbox
                checked={currentVariable.enabled}
                onChange={(e) => setCurrentVariable({ ...currentVariable, enabled: e.target.checked })}
              />
              <Typography variant="body2">Enabled</Typography>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSaveVariable}
            variant="contained"
            disabled={!currentVariable.key || currentVariable.value === undefined}
          >
            {dialogMode === 'create' ? 'Add' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Usage Examples */}
      <Box sx={{ mt: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: 1, borderColor: 'divider' }}>
        <Typography variant="subtitle2" gutterBottom>
          Usage Examples
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Box>
            <Typography variant="caption" color="text.secondary">
              In URL:
            </Typography>
            <Typography variant="body2" fontFamily="monospace">
              {'{{baseUrl}}/api/users/{{userId}}'}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              In Headers:
            </Typography>
            <Typography variant="body2" fontFamily="monospace">
              Authorization: Bearer {'{{authToken}}'}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              In Body:
            </Typography>
            <Typography variant="body2" fontFamily="monospace">
              {'{ "apiKey": "{{apiKey}}", "timestamp": "{{timestamp}}" }'}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default VariablesTab;
