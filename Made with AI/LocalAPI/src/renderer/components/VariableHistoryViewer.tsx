// Variable History Viewer Component
// Displays history of variable changes

import React, { useState, useEffect } from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
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
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import type { VariableScope } from '../../types/models';

interface VariableHistory {
  id: string;
  variableName: string;
  oldValue: any;
  newValue: any;
  scope: VariableScope;
  source: string;
  timestamp: Date;
  requestId?: string;
}

interface VariableHistoryViewerProps {
  open: boolean;
  onClose: () => void;
  variableName?: string;
}

const VariableHistoryViewer: React.FC<VariableHistoryViewerProps> = ({
  open,
  onClose,
  variableName: initialVariableName,
}) => {
  const [history, setHistory] = useState<VariableHistory[]>([]);
  const [filteredHistory, setFilteredHistory] = useState<VariableHistory[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      loadHistory();
    }
  }, [open, initialVariableName]);

  useEffect(() => {
    filterHistory();
  }, [history, searchQuery]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const loadedHistory = await window.electronAPI.extractor.getHistory(
        initialVariableName,
        100
      );
      setHistory(loadedHistory);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterHistory = () => {
    if (!searchQuery.trim()) {
      setFilteredHistory(history);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = history.filter(
      (h) =>
        h.variableName.toLowerCase().includes(query) ||
        h.source.toLowerCase().includes(query) ||
        String(h.oldValue).toLowerCase().includes(query) ||
        String(h.newValue).toLowerCase().includes(query)
    );
    setFilteredHistory(filtered);
  };

  const handleClearHistory = async () => {
    if (confirm('Are you sure you want to clear the variable history?')) {
      try {
        await window.electronAPI.extractor.clearHistory(initialVariableName);
        await loadHistory();
      } catch (err) {
        console.error('Failed to clear history:', err);
      }
    }
  };

  const copyValue = (value: any) => {
    const text = typeof value === 'string' ? value : JSON.stringify(value);
    navigator.clipboard.writeText(text);
  };

  const formatValue = (value: any): string => {
    if (value === null) return 'null';
    if (value === undefined) return 'undefined';
    if (typeof value === 'string') {
      return value.length > 40 ? value.substring(0, 40) + '...' : value;
    }
    const str = JSON.stringify(value);
    return str.length > 40 ? str.substring(0, 40) + '...' : str;
  };

  const formatTimestamp = (timestamp: Date): string => {
    const date = new Date(timestamp);
    return date.toLocaleString();
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
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            Variable History {initialVariableName && `- ${initialVariableName}`}
          </Typography>
          <Tooltip title="Clear history">
            <IconButton onClick={handleClearHistory} color="error" size="small">
              <DeleteIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            size="small"
            fullWidth
            placeholder="Search history..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />

          {loading ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography color="text.secondary">Loading history...</Typography>
            </Box>
          ) : filteredHistory.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography color="text.secondary">
                {searchQuery.trim()
                  ? 'No history entries match your search'
                  : 'No history entries found'}
              </Typography>
            </Box>
          ) : (
            <TableContainer sx={{ maxHeight: 500 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Timestamp</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Variable</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Old Value</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>New Value</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Scope</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Source</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredHistory.map((entry) => (
                    <TableRow key={entry.id} hover>
                      <TableCell sx={{ fontSize: '0.75rem' }}>
                        {formatTimestamp(entry.timestamp)}
                      </TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                        {entry.variableName}
                      </TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                        {formatValue(entry.oldValue)}
                      </TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                        {formatValue(entry.newValue)}
                      </TableCell>
                      <TableCell>
                        <Chip label={entry.scope} size="small" color={getScopeColor(entry.scope)} />
                      </TableCell>
                      <TableCell sx={{ fontSize: '0.75rem', maxWidth: 150 }}>
                        {entry.source.length > 20
                          ? entry.source.substring(0, 20) + '...'
                          : entry.source}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <Tooltip title="Copy old value">
                            <IconButton size="small" onClick={() => copyValue(entry.oldValue)}>
                              <ContentCopyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Copy new value">
                            <IconButton size="small" onClick={() => copyValue(entry.newValue)}>
                              <ContentCopyIcon fontSize="small" />
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

          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              Showing {filteredHistory.length} of {history.length} entries
            </Typography>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default VariableHistoryViewer;
