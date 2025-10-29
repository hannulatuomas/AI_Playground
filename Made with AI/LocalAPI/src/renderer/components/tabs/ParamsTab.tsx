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
import type { QueryParam } from '../../../types/models';

interface ParamsTabProps {
  params: QueryParam[];
  onChange: (params: QueryParam[]) => void;
}

const ParamsTab: React.FC<ParamsTabProps> = ({ params, onChange }) => {
  const handleAdd = () => {
    onChange([...params, { key: '', value: '', enabled: true }]);
  };

  const handleDelete = (index: number) => {
    onChange(params.filter((_, i) => i !== index));
  };

  const handleChange = (index: number, field: keyof QueryParam, value: any) => {
    const updated = [...params];
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
            {params.map((param, index) => (
              <TableRow key={index}>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={param.enabled}
                    onChange={e => handleChange(index, 'enabled', e.target.checked)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <TextField
                    fullWidth
                    size="small"
                    value={param.key}
                    onChange={e => handleChange(index, 'key', e.target.value)}
                    placeholder="Parameter name"
                  />
                </TableCell>
                <TableCell>
                  <TextField
                    fullWidth
                    size="small"
                    value={param.value}
                    onChange={e => handleChange(index, 'value', e.target.value)}
                    placeholder="Parameter value"
                  />
                </TableCell>
                <TableCell>
                  <TextField
                    fullWidth
                    size="small"
                    value={param.description || ''}
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
          Add Parameter
        </Button>
      </Box>
    </Box>
  );
};

export default ParamsTab;
