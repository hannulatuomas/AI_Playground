// Extraction Rules Manager Component
// Manages auto-extraction rules for variables

import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import Chip from '@mui/material/Chip';
import Alert from '@mui/material/Alert';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import type { VariableScope, Response } from '../../types/models';

interface ExtractionRule {
  id: string;
  name: string;
  enabled: boolean;
  source: 'body' | 'header';
  extractionType: 'jsonpath' | 'xpath' | 'regex' | 'header';
  pattern: string;
  variableName: string;
  scope: VariableScope;
  description?: string;
  createdAt: Date;
  updatedAt: Date;
}

interface ExtractionRulesManagerProps {
  response?: Response | null;
}

const ExtractionRulesManager: React.FC<ExtractionRulesManagerProps> = ({ response }) => {
  const [rules, setRules] = useState<ExtractionRule[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<ExtractionRule | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    enabled: true,
    source: 'body' as 'body' | 'header',
    extractionType: 'jsonpath' as 'jsonpath' | 'xpath' | 'regex' | 'header',
    pattern: '',
    variableName: '',
    scope: 'global' as VariableScope,
    description: '',
  });
  const [testResult, setTestResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    try {
      const loadedRules = await window.electronAPI.extractor.getRules();
      setRules(loadedRules);
    } catch (err) {
      console.error('Failed to load rules:', err);
    }
  };

  const handleOpenDialog = (rule?: ExtractionRule) => {
    if (rule) {
      setEditingRule(rule);
      setFormData({
        name: rule.name,
        enabled: rule.enabled,
        source: rule.source,
        extractionType: rule.extractionType,
        pattern: rule.pattern,
        variableName: rule.variableName,
        scope: rule.scope,
        description: rule.description || '',
      });
    } else {
      setEditingRule(null);
      setFormData({
        name: '',
        enabled: true,
        source: 'body',
        extractionType: 'jsonpath',
        pattern: '',
        variableName: '',
        scope: 'global',
        description: '',
      });
    }
    setTestResult(null);
    setError(null);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingRule(null);
    setTestResult(null);
    setError(null);
  };

  const handleSaveRule = async () => {
    try {
      if (editingRule) {
        await window.electronAPI.extractor.updateRule(editingRule.id, formData);
      } else {
        await window.electronAPI.extractor.addRule(formData);
      }
      await loadRules();
      handleCloseDialog();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save rule');
    }
  };

  const handleDeleteRule = async (id: string) => {
    try {
      await window.electronAPI.extractor.deleteRule(id);
      await loadRules();
    } catch (err) {
      console.error('Failed to delete rule:', err);
    }
  };

  const handleToggleRule = async (rule: ExtractionRule) => {
    try {
      await window.electronAPI.extractor.updateRule(rule.id, { enabled: !rule.enabled });
      await loadRules();
    } catch (err) {
      console.error('Failed to toggle rule:', err);
    }
  };

  const handleTestRule = async () => {
    if (!response) {
      setError('No response available for testing');
      return;
    }

    setError(null);
    setTestResult(null);

    try {
      const tempRule = {
        ...formData,
        id: 'temp',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const results = await window.electronAPI.extractor.extractWithRules(response, [tempRule]);

      if (results.length > 0) {
        setTestResult(results[0]);
      } else {
        setError('No results from extraction');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Test failed');
    }
  };

  const handleExportRules = async () => {
    try {
      const json = await window.electronAPI.extractor.exportRules();
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `extraction-rules-${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export rules:', err);
    }
  };

  const handleImportRules = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const count = await window.electronAPI.extractor.importRules(text);
      await loadRules();
      alert(`Successfully imported ${count} rules`);
    } catch (err) {
      alert('Failed to import rules: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Auto-Extraction Rules</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Import rules">
            <IconButton component="label" size="small">
              <FileUploadIcon />
              <input type="file" hidden accept=".json" onChange={handleImportRules} />
            </IconButton>
          </Tooltip>
          <Tooltip title="Export rules">
            <IconButton size="small" onClick={handleExportRules}>
              <FileDownloadIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
            size="small"
          >
            Add Rule
          </Button>
        </Box>
      </Box>

      {rules.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography color="text.secondary">
            No extraction rules defined. Create a rule to automatically extract variables from responses.
          </Typography>
        </Box>
      ) : (
        <TableContainer sx={{ flex: 1, overflow: 'auto' }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Enabled</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Variable</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Pattern</TableCell>
                <TableCell>Scope</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rules.map((rule) => (
                <TableRow key={rule.id} hover>
                  <TableCell>
                    <Switch
                      checked={rule.enabled}
                      onChange={() => handleToggleRule(rule)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{rule.name}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace' }}>{rule.variableName}</TableCell>
                  <TableCell>
                    <Chip label={rule.extractionType} size="small" />
                  </TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.75rem', maxWidth: 200 }}>
                    {rule.pattern.length > 30 ? rule.pattern.substring(0, 30) + '...' : rule.pattern}
                  </TableCell>
                  <TableCell>
                    <Chip label={rule.scope} size="small" color="primary" />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Tooltip title="Edit">
                        <IconButton size="small" onClick={() => handleOpenDialog(rule)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDeleteRule(rule.id)}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Rule Editor Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>{editingRule ? 'Edit Rule' : 'Create Rule'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            {error && <Alert severity="error">{error}</Alert>}
            {testResult && (
              <Alert severity={testResult.success ? 'success' : 'error'}>
                {testResult.success
                  ? `Extracted: ${JSON.stringify(testResult.value)}`
                  : `Error: ${testResult.error}`}
              </Alert>
            )}

            <TextField
              label="Rule Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              fullWidth
              required
            />

            <TextField
              label="Variable Name"
              value={formData.variableName}
              onChange={(e) => setFormData({ ...formData, variableName: e.target.value })}
              fullWidth
              required
            />

            <FormControl fullWidth>
              <InputLabel>Scope</InputLabel>
              <Select
                value={formData.scope}
                onChange={(e) => setFormData({ ...formData, scope: e.target.value as VariableScope })}
                label="Scope"
              >
                <MenuItem value="global">Global</MenuItem>
                <MenuItem value="environment">Environment</MenuItem>
                <MenuItem value="collection">Collection</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Source</InputLabel>
              <Select
                value={formData.source}
                onChange={(e) => setFormData({ ...formData, source: e.target.value as 'body' | 'header' })}
                label="Source"
              >
                <MenuItem value="body">Response Body</MenuItem>
                <MenuItem value="header">Response Headers</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Extraction Type</InputLabel>
              <Select
                value={formData.extractionType}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    extractionType: e.target.value as any,
                  })
                }
                label="Extraction Type"
              >
                <MenuItem value="jsonpath">JSONPath</MenuItem>
                <MenuItem value="xpath">XPath</MenuItem>
                <MenuItem value="regex">Regular Expression</MenuItem>
                <MenuItem value="header">Header Name</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="Pattern"
              value={formData.pattern}
              onChange={(e) => setFormData({ ...formData, pattern: e.target.value })}
              fullWidth
              required
              multiline
              rows={2}
              helperText={
                formData.extractionType === 'jsonpath'
                  ? 'e.g., $.data.token'
                  : formData.extractionType === 'xpath'
                  ? 'e.g., /root/element/value'
                  : formData.extractionType === 'header'
                  ? 'e.g., Authorization'
                  : 'e.g., "token":\\s*"([^"]+)"'
              }
            />

            <TextField
              label="Description (optional)"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />

            <FormControlLabel
              control={
                <Switch
                  checked={formData.enabled}
                  onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                />
              }
              label="Enabled"
            />

            {response && (
              <Button
                variant="outlined"
                startIcon={<PlayArrowIcon />}
                onClick={handleTestRule}
                fullWidth
              >
                Test Rule with Current Response
              </Button>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSaveRule}
            variant="contained"
            disabled={!formData.name || !formData.variableName || !formData.pattern}
          >
            {editingRule ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExtractionRulesManager;
