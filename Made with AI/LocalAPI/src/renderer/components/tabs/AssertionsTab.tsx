import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  Divider,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Add as AddIcon,
  Code as CodeIcon,
  PlayArrow as RunIcon,
  CheckCircle as PassIcon,
  Error as FailIcon,
} from '@mui/icons-material';
import AssertionGroup from '../assertions/AssertionGroup';
import type { Assertion } from '../../../types/models';

interface AssertionsTabProps {
  assertions: Assertion[];
  onChange: (assertions: Assertion[]) => void;
  onRun?: () => void;
}

const AssertionsTab: React.FC<AssertionsTabProps> = ({
  assertions,
  onChange,
  onRun,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(['default']));

  const assertionTemplates = [
    {
      name: 'Status Code 200',
      assertion: {
        id: `assertion-${Date.now()}`,
        type: 'status' as const,
        enabled: true,
        operator: 'equals' as const,
        expected: '200',
      },
    },
    {
      name: 'Response Time < 1s',
      assertion: {
        id: `assertion-${Date.now()}`,
        type: 'response-time' as const,
        enabled: true,
        operator: 'lt' as const,
        expected: '1000',
      },
    },
    {
      name: 'Content-Type JSON',
      assertion: {
        id: `assertion-${Date.now()}`,
        type: 'header' as const,
        enabled: true,
        operator: 'contains' as const,
        path: 'content-type',
        expected: 'application/json',
      },
    },
    {
      name: 'JSONPath Exists',
      assertion: {
        id: `assertion-${Date.now()}`,
        type: 'jsonpath' as const,
        enabled: true,
        operator: 'exists' as const,
        path: '$.data',
      },
    },
    {
      name: 'Custom Script',
      assertion: {
        id: `assertion-${Date.now()}`,
        type: 'custom' as const,
        enabled: true,
        customScript: `pm.test('Custom test', () => {\n  pm.expect(pm.response.code).to.equal(200);\n});`,
      },
    },
  ];

  const handleAddTemplate = (template: typeof assertionTemplates[0]) => {
    onChange([...assertions, template.assertion]);
    setAnchorEl(null);
  };

  const handleToggleGroup = (groupName: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(groupName)) {
      newExpanded.delete(groupName);
    } else {
      newExpanded.add(groupName);
    }
    setExpandedGroups(newExpanded);
  };

  const generateTestScript = (): string => {
    const enabledAssertions = assertions.filter((a) => a.enabled);
    if (enabledAssertions.length === 0) {
      return '// No assertions defined';
    }

    const scripts = enabledAssertions.map((assertion) => {
      switch (assertion.type) {
        case 'status':
          return `pm.test('Status code is ${assertion.expected}', () => {\n  pm.expect(pm.response.code).to.equal(${assertion.expected});\n});`;
        
        case 'header':
          return `pm.test('Header ${assertion.path} ${assertion.operator} ${assertion.expected}', () => {\n  pm.expect(pm.response.headers['${assertion.path}']).to.${assertion.operator === 'equals' ? 'equal' : 'include'}('${assertion.expected}');\n});`;
        
        case 'body':
          return `pm.test('Body contains ${assertion.expected}', () => {\n  const body = pm.response.text();\n  pm.expect(body).to.include('${assertion.expected}');\n});`;
        
        case 'jsonpath':
          return `pm.test('JSONPath ${assertion.path} ${assertion.operator} ${assertion.expected || 'exists'}', () => {\n  const value = pm.extractJson('${assertion.path}');\n  ${assertion.operator === 'exists' ? 'pm.expect(value).to.not.be.null;' : `pm.expect(value).to.${assertion.operator === 'equals' ? 'equal' : 'include'}(${typeof assertion.expected === 'number' ? assertion.expected : `'${assertion.expected}'`});`}\n});`;
        
        case 'response-time':
          return `pm.test('Response time is less than ${assertion.expected}ms', () => {\n  pm.expect(pm.response.responseTime).to.be.below(${assertion.expected});\n});`;
        
        case 'custom':
          return assertion.customScript || '';
        
        default:
          return '';
      }
    });

    return scripts.filter(Boolean).join('\n\n');
  };

  const passedCount = assertions.filter((a) => a.result === true).length;
  const failedCount = assertions.filter((a) => a.result === false).length;
  const hasResults = assertions.some((a) => a.result !== undefined);

  return (
    <Box sx={{ p: 2 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h6">Assertions</Typography>
          <Typography variant="body2" color="text.secondary">
            Build visual assertions or write custom test scripts
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            startIcon={<AddIcon />}
            onClick={(e) => setAnchorEl(e.currentTarget)}
            variant="outlined"
          >
            Add Assertion
          </Button>
          {onRun && (
            <Button
              startIcon={<RunIcon />}
              onClick={onRun}
              variant="contained"
              disabled={assertions.length === 0}
            >
              Run Tests
            </Button>
          )}
        </Box>
      </Box>

      {/* Template Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        {assertionTemplates.map((template) => (
          <MenuItem key={template.name} onClick={() => handleAddTemplate(template)}>
            <ListItemIcon>
              <CodeIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>{template.name}</ListItemText>
          </MenuItem>
        ))}
      </Menu>

      {/* Results Summary */}
      {hasResults && (
        <Alert
          severity={failedCount > 0 ? 'error' : 'success'}
          icon={failedCount > 0 ? <FailIcon /> : <PassIcon />}
          sx={{ mb: 2 }}
        >
          <Typography variant="body2">
            <strong>{passedCount} passed</strong>, <strong>{failedCount} failed</strong> out of {assertions.length} assertions
          </Typography>
        </Alert>
      )}

      {/* Assertion Groups */}
      <AssertionGroup
        name="Default Assertions"
        assertions={assertions}
        onChange={onChange}
        onRun={onRun}
        expanded={expandedGroups.has('default')}
        onExpandChange={(expanded) => handleToggleGroup('default')}
      />

      <Divider sx={{ my: 3 }} />

      {/* Generated Test Script */}
      <Box>
        <Typography variant="subtitle2" gutterBottom>
          Generated Test Script
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          This script is automatically generated from your assertions
        </Typography>
        <Box
          sx={{
            mt: 1,
            p: 2,
            bgcolor: 'grey.900',
            color: 'grey.100',
            borderRadius: 1,
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            whiteSpace: 'pre-wrap',
            overflow: 'auto',
            maxHeight: 400,
          }}
        >
          {generateTestScript()}
        </Box>
      </Box>

      {/* Quick Tips */}
      <Box sx={{ mt: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: 1, borderColor: 'divider' }}>
        <Typography variant="subtitle2" gutterBottom>
          Quick Tips
        </Typography>
        <Box component="ul" sx={{ m: 0, pl: 2 }}>
          <Typography component="li" variant="body2" color="text.secondary">
            Use <strong>Status Code</strong> assertions to verify HTTP response codes
          </Typography>
          <Typography component="li" variant="body2" color="text.secondary">
            Use <strong>JSONPath</strong> assertions to validate nested JSON data
          </Typography>
          <Typography component="li" variant="body2" color="text.secondary">
            Use <strong>Response Time</strong> assertions to ensure performance
          </Typography>
          <Typography component="li" variant="body2" color="text.secondary">
            Use <strong>Custom Script</strong> for complex validation logic
          </Typography>
          <Typography component="li" variant="body2" color="text.secondary">
            Click the <CodeIcon fontSize="small" sx={{ verticalAlign: 'middle' }} /> icon to preview generated code
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default AssertionsTab;
