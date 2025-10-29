import React from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Typography from '@mui/material/Typography';
import type { RequestBody } from '../../../types/models';

interface BodyTabProps {
  body?: RequestBody;
  onChange: (body: RequestBody) => void;
}

const BodyTab: React.FC<BodyTabProps> = ({ body, onChange }) => {
  const currentBody = body || { type: 'none', content: '' };

  const handleTypeChange = (type: RequestBody['type']) => {
    onChange({ ...currentBody, type, content: '' });
  };

  const handleContentChange = (content: string) => {
    onChange({ ...currentBody, content });
  };

  return (
    <Box sx={{ p: 2 }}>
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Body Type</InputLabel>
        <Select
          value={currentBody.type}
          label="Body Type"
          onChange={e => handleTypeChange(e.target.value as RequestBody['type'])}
        >
          <MenuItem value="none">None</MenuItem>
          <MenuItem value="json">JSON</MenuItem>
          <MenuItem value="xml">XML</MenuItem>
          <MenuItem value="raw">Raw Text</MenuItem>
          <MenuItem value="form-data">Form Data</MenuItem>
          <MenuItem value="x-www-form-urlencoded">URL Encoded</MenuItem>
          <MenuItem value="graphql">GraphQL</MenuItem>
        </Select>
      </FormControl>

      {currentBody.type !== 'none' && (
        <>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
            {currentBody.type === 'json' && 'Enter JSON data'}
            {currentBody.type === 'xml' && 'Enter XML data'}
            {currentBody.type === 'raw' && 'Enter raw text'}
            {currentBody.type === 'form-data' && 'Enter form data as JSON'}
            {currentBody.type === 'x-www-form-urlencoded' && 'Enter URL encoded data as JSON'}
            {currentBody.type === 'graphql' && 'Enter GraphQL query'}
          </Typography>

          <TextField
            fullWidth
            multiline
            rows={15}
            value={currentBody.content}
            onChange={e => handleContentChange(e.target.value)}
            placeholder={
              currentBody.type === 'json'
                ? '{\n  "key": "value"\n}'
                : currentBody.type === 'xml'
                ? '<root>\n  <element>value</element>\n</root>'
                : currentBody.type === 'graphql'
                ? 'query {\n  users {\n    id\n    name\n  }\n}'
                : 'Enter content here...'
            }
            sx={{
              fontFamily: 'monospace',
              '& textarea': {
                fontFamily: 'monospace',
                fontSize: '0.875rem',
              },
            }}
          />

          {currentBody.type === 'json' && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Tip: Use {'{{variableName}}'} for variable substitution
              </Typography>
            </Box>
          )}
        </>
      )}
    </Box>
  );
};

export default BodyTab;
