import React from 'react';
import Box from '@mui/material/Box';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TextField from '@mui/material/TextField';
import Checkbox from '@mui/material/Checkbox';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import Button from '@mui/material/Button';
import type { Header } from '../../../types/models';

interface HeadersTabProps {
  headers: Header[];
  onChange: (headers: Header[]) => void;
}

const HeadersTab: React.FC<HeadersTabProps> = ({ headers, onChange }) => {
  const handleAdd = () => {
    onChange([...headers, { key: '', value: '', enabled: true }]);
  };

  const handleDelete = (index: number) => {
    onChange(headers.filter((_, i) => i !== index));
  };

  const handleChange = (index: number, field: keyof Header, value: any) => {
    const updated = [...headers];
    updated[index] = { ...updated[index], [field]: value };
    onChange(updated);
  };

  return (
    <Box>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox" width={50}>
                Enabled
              </TableCell>
              <TableCell width="40%">Key</TableCell>
              <TableCell width="40%">Value</TableCell>
              <TableCell width="15%">Description</TableCell>
              <TableCell width={50}></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {headers.map((header, index) => (
              <TableRow key={index}>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={header.enabled}
                    onChange={e => handleChange(index, 'enabled', e.target.checked)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <TextField
                    fullWidth
                    size="small"
                    value={header.key}
                    onChange={e => handleChange(index, 'key', e.target.value)}
                    placeholder="Header name"
                  />
                </TableCell>
                <TableCell>
                  <TextField
                    fullWidth
                    size="small"
                    value={header.value}
                    onChange={e => handleChange(index, 'value', e.target.value)}
                    placeholder="Header value"
                  />
                </TableCell>
                <TableCell>
                  <TextField
                    fullWidth
                    size="small"
                    value={header.description || ''}
                    onChange={e => handleChange(index, 'description', e.target.value)}
                    placeholder="Description"
                  />
                </TableCell>
                <TableCell>
                  <IconButton size="small" onClick={() => handleDelete(index)}>
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Box sx={{ p: 2 }}>
        <Button startIcon={<AddIcon />} onClick={handleAdd} size="small">
          Add Header
        </Button>
      </Box>
    </Box>
  );
};

export default HeadersTab;
