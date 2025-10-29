import React, { useState } from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
  Code as CodeIcon,
} from '@mui/icons-material';
import type { Assertion } from '../../../types/models';

interface AssertionBuilderProps {
  assertion: Assertion;
  onChange: (assertion: Assertion) => void;
  onDelete: () => void;
  onDuplicate: () => void;
}

const AssertionBuilder: React.FC<AssertionBuilderProps> = ({
  assertion,
  onChange,
  onDelete,
  onDuplicate,
}) => {
  const [showCode, setShowCode] = useState(false);

  const assertionTypes = [
    { value: 'status', label: 'Status Code' },
    { value: 'header', label: 'Header' },
    { value: 'body', label: 'Response Body' },
    { value: 'jsonpath', label: 'JSONPath' },
    { value: 'xpath', label: 'XPath' },
    { value: 'response-time', label: 'Response Time' },
    { value: 'custom', label: 'Custom Script' },
  ];

  const operators = [
    { value: 'equals', label: 'Equals' },
    { value: 'contains', label: 'Contains' },
    { value: 'matches', label: 'Matches (Regex)' },
    { value: 'exists', label: 'Exists' },
    { value: 'gt', label: 'Greater Than' },
    { value: 'lt', label: 'Less Than' },
    { value: 'gte', label: 'Greater Than or Equal' },
    { value: 'lte', label: 'Less Than or Equal' },
  ];

  const handleTypeChange = (type: string) => {
    onChange({
      ...assertion,
      type: type as any,
      operator: type === 'response-time' ? 'lt' : 'equals',
      expected: '',
      path: '',
    });
  };

  const generateCode = (): string => {
    switch (assertion.type) {
      case 'status':
        return `pm.test('Status code is ${assertion.expected}', () => {\n  pm.expect(pm.response.code).to.equal(${assertion.expected});\n});`;
      
      case 'header':
        return `pm.test('Header ${assertion.path} ${assertion.operator} ${assertion.expected}', () => {\n  pm.expect(pm.response.headers['${assertion.path}']).to.${assertion.operator === 'equals' ? 'equal' : 'include'}('${assertion.expected}');\n});`;
      
      case 'body':
        return `pm.test('Body contains ${assertion.expected}', () => {\n  const body = pm.response.text();\n  pm.expect(body).to.include('${assertion.expected}');\n});`;
      
      case 'jsonpath':
        return `pm.test('JSONPath ${assertion.path} ${assertion.operator} ${assertion.expected}', () => {\n  const value = pm.extractJson('${assertion.path}');\n  pm.expect(value).to.${assertion.operator === 'equals' ? 'equal' : 'include'}(${typeof assertion.expected === 'number' ? assertion.expected : `'${assertion.expected}'`});\n});`;
      
      case 'response-time':
        return `pm.test('Response time is less than ${assertion.expected}ms', () => {\n  pm.expect(pm.response.responseTime).to.be.below(${assertion.expected});\n});`;
      
      case 'custom':
        return assertion.customScript || '// Write custom test script here';
      
      default:
        return '';
    }
  };

  return (
    <Box
      sx={{
        p: 2,
        mb: 2,
        border: 1,
        borderColor: assertion.enabled ? 'primary.main' : 'divider',
        borderRadius: 1,
        bgcolor: assertion.enabled ? 'background.paper' : 'action.disabledBackground',
        opacity: assertion.enabled ? 1 : 0.6,
      }}
    >
      <Box sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'flex-start' }}>
        {/* Assertion Type */}
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Type</InputLabel>
          <Select
            value={assertion.type}
            label="Type"
            onChange={(e) => handleTypeChange(e.target.value)}
          >
            {assertionTypes.map((type) => (
              <MenuItem key={type.value} value={type.value}>
                {type.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Path/Key (for header, jsonpath, xpath) */}
        {(assertion.type === 'header' || assertion.type === 'jsonpath' || assertion.type === 'xpath') && (
          <TextField
            size="small"
            label={assertion.type === 'header' ? 'Header Name' : 'Path'}
            value={assertion.path || ''}
            onChange={(e) => onChange({ ...assertion, path: e.target.value })}
            placeholder={
              assertion.type === 'header'
                ? 'e.g., Content-Type'
                : assertion.type === 'jsonpath'
                ? 'e.g., $.data.user.id'
                : 'e.g., //user/name'
            }
            sx={{ flex: 1 }}
          />
        )}

        {/* Operator (not for custom) */}
        {assertion.type !== 'custom' && (
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Operator</InputLabel>
            <Select
              value={assertion.operator || 'equals'}
              label="Operator"
              onChange={(e) => onChange({ ...assertion, operator: e.target.value as any })}
            >
              {operators.map((op) => (
                <MenuItem key={op.value} value={op.value}>
                  {op.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        {/* Expected Value (not for custom or exists) */}
        {assertion.type !== 'custom' && assertion.operator !== 'exists' && (
          <TextField
            size="small"
            label="Expected Value"
            value={assertion.expected || ''}
            onChange={(e) => onChange({ ...assertion, expected: e.target.value })}
            placeholder={
              assertion.type === 'status'
                ? '200'
                : assertion.type === 'response-time'
                ? '1000'
                : 'Expected value'
            }
            type={assertion.type === 'status' || assertion.type === 'response-time' ? 'number' : 'text'}
            sx={{ flex: 1 }}
          />
        )}

        {/* Actions */}
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Tooltip title={showCode ? 'Hide Code' : 'Show Code'}>
            <IconButton
              size="small"
              onClick={() => setShowCode(!showCode)}
              color={showCode ? 'primary' : 'default'}
            >
              <CodeIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Duplicate">
            <IconButton size="small" onClick={onDuplicate}>
              <CopyIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton size="small" onClick={onDelete} color="error">
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Custom Script Editor */}
      {assertion.type === 'custom' && (
        <TextField
          fullWidth
          multiline
          rows={4}
          value={assertion.customScript || ''}
          onChange={(e) => onChange({ ...assertion, customScript: e.target.value })}
          placeholder="// Write custom test script&#10;pm.test('Custom test', () => {&#10;  pm.expect(pm.response.code).to.equal(200);&#10;});"
          sx={{
            fontFamily: 'monospace',
            '& textarea': {
              fontFamily: 'monospace',
              fontSize: '0.875rem',
            },
          }}
        />
      )}

      {/* Generated Code Preview */}
      {showCode && assertion.type !== 'custom' && (
        <Box
          sx={{
            mt: 2,
            p: 1.5,
            bgcolor: 'grey.900',
            color: 'grey.100',
            borderRadius: 1,
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            whiteSpace: 'pre-wrap',
            overflow: 'auto',
          }}
        >
          {generateCode()}
        </Box>
      )}

      {/* Result Indicator */}
      {assertion.result !== undefined && (
        <Box sx={{ mt: 2 }}>
          <Chip
            label={assertion.result ? 'PASSED' : 'FAILED'}
            color={assertion.result ? 'success' : 'error'}
            size="small"
          />
          {assertion.message && (
            <Box sx={{ mt: 1, fontSize: '0.875rem', color: 'text.secondary' }}>
              {assertion.message}
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
};

export default AssertionBuilder;
