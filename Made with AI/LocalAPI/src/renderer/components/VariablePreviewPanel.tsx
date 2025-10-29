// Variable Preview Panel Component
// Shows current variables with their values and scopes

import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import type { VariableScope } from '../../types/models';

interface Variable {
  key: string;
  value: any;
  scope: VariableScope;
}

interface VariablePreviewPanelProps {
  onEdit?: (variable: Variable) => void;
  onDelete?: (variable: Variable) => void;
  onViewHistory?: (variableName: string) => void;
}

const VariablePreviewPanel: React.FC<VariablePreviewPanelProps> = ({
  onEdit,
  onDelete,
  onViewHistory,
}) => {
  const [variables, setVariables] = useState<Variable[]>([]);
  const [filteredVariables, setFilteredVariables] = useState<Variable[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeScope, setActiveScope] = useState<'all' | VariableScope>('all');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadVariables();
  }, []);

  useEffect(() => {
    filterVariables();
  }, [variables, searchQuery, activeScope]);

  const loadVariables = async () => {
    setLoading(true);
    try {
      // Check if API exists to prevent crash
      if (!window.electronAPI?.variables) {
        console.warn('Variables API not available');
        setVariables([]);
        return;
      }

      const [globalVars, envVars, collectionVars] = await Promise.all([
        window.electronAPI.variables.get('global').catch(() => ({})),
        window.electronAPI.variables.get('environment').catch(() => ({})),
        window.electronAPI.variables.get('collection').catch(() => ({})),
      ]);

      const allVars: Variable[] = [
        ...Object.entries(globalVars || {}).map(([key, value]) => ({
          key,
          value,
          scope: 'global' as VariableScope,
        })),
        ...Object.entries(envVars || {}).map(([key, value]) => ({
          key,
          value,
          scope: 'environment' as VariableScope,
        })),
        ...Object.entries(collectionVars || {}).map(([key, value]) => ({
          key,
          value,
          scope: 'collection' as VariableScope,
        })),
      ];

      setVariables(allVars);
    } catch (error) {
      console.error('Failed to load variables:', error);
      setVariables([]); // Don't crash, just show empty
    } finally {
      setLoading(false);
    }
  };

  const filterVariables = () => {
    let filtered = variables;

    // Filter by scope
    if (activeScope !== 'all') {
      filtered = filtered.filter((v) => v.scope === activeScope);
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (v) =>
          v.key.toLowerCase().includes(query) ||
          String(v.value).toLowerCase().includes(query)
      );
    }

    setFilteredVariables(filtered);
  };

  const handleCopy = (value: any) => {
    const text = typeof value === 'string' ? value : JSON.stringify(value);
    navigator.clipboard.writeText(text);
  };

  const handleDelete = async (variable: Variable) => {
    if (onDelete) {
      onDelete(variable);
    } else {
      try {
        await window.electronAPI.variables.delete(variable.scope, variable.key);
        await loadVariables();
      } catch (error) {
        console.error('Failed to delete variable:', error);
      }
    }
  };

  const formatValue = (value: any): string => {
    if (value === null) return 'null';
    if (value === undefined) return 'undefined';
    if (typeof value === 'string') {
      return value.length > 50 ? value.substring(0, 50) + '...' : value;
    }
    const str = JSON.stringify(value);
    return str.length > 50 ? str.substring(0, 50) + '...' : str;
  };

  const getScopeColor = (scope: VariableScope): 'primary' | 'secondary' | 'success' => {
    switch (scope) {
      case 'global':
        return 'primary';
      case 'environment':
        return 'secondary';
      case 'collection':
        return 'success';
      default:
        return 'primary';
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" gutterBottom>
          Variable Preview
        </Typography>

        <TextField
          size="small"
          fullWidth
          placeholder="Search variables..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 2 }}
        />

        <Tabs
          value={activeScope}
          onChange={(_, newValue) => setActiveScope(newValue)}
          variant="fullWidth"
        >
          <Tab label="All" value="all" />
          <Tab label="Global" value="global" />
          <Tab label="Environment" value="environment" />
          <Tab label="Collection" value="collection" />
        </Tabs>
      </Box>

      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {loading ? (
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <Typography color="text.secondary">Loading variables...</Typography>
          </Box>
        ) : filteredVariables.length === 0 ? (
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <Typography color="text.secondary">
              {searchQuery.trim() ? 'No variables match your search' : 'No variables defined'}
            </Typography>
          </Box>
        ) : (
          <TableContainer>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Value</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Scope</TableCell>
                  <TableCell sx={{ fontWeight: 600, width: 150 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredVariables.map((variable, index) => (
                  <TableRow key={`${variable.scope}-${variable.key}-${index}`} hover>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                      {variable.key}
                    </TableCell>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                      {formatValue(variable.value)}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={variable.scope}
                        size="small"
                        color={getScopeColor(variable.scope)}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="Copy value">
                          <IconButton
                            size="small"
                            onClick={() => handleCopy(variable.value)}
                          >
                            <ContentCopyIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        {onViewHistory && (
                          <Tooltip title="View history">
                            <IconButton
                              size="small"
                              onClick={() => onViewHistory(variable.key)}
                            >
                              <HistoryIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        {onEdit && (
                          <Tooltip title="Edit">
                            <IconButton size="small" onClick={() => onEdit(variable)}>
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDelete(variable)}
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
      </Box>

      <Box sx={{ p: 1, borderTop: 1, borderColor: 'divider', textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          {filteredVariables.length} variable{filteredVariables.length !== 1 ? 's' : ''} shown
        </Typography>
      </Box>
    </Box>
  );
};

export default VariablePreviewPanel;
