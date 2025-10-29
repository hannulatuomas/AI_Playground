import React from 'react';
import { Box, Typography, Divider, Link } from '@mui/material';
import MonacoEditor from '../MonacoEditor';

interface ScriptsTabProps {
  preRequestScript: string;
  onPreRequestScriptChange: (script: string) => void;
}

const ScriptsTab: React.FC<ScriptsTabProps> = ({
  preRequestScript,
  onPreRequestScriptChange,
}) => {
  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Pre-request Script
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Execute JavaScript before the request is sent. Use the <code>pm</code> API to set variables,
          modify request data, or perform setup tasks.{' '}
          <Link href="#" onClick={(e) => { e.preventDefault(); /* Open docs */ }}>
            Learn more
          </Link>
        </Typography>
      </Box>

      <MonacoEditor
        value={preRequestScript}
        onChange={onPreRequestScriptChange}
        language="javascript"
        height="400px"
        placeholder="Write pre-request script here (e.g., pm.variables.set('timestamp', Date.now()))"
      />

      <Divider sx={{ my: 2 }} />

      <Box>
        <Typography variant="subtitle2" gutterBottom>
          Quick Examples
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Box
            sx={{
              p: 1.5,
              bgcolor: 'background.paper',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              cursor: 'pointer',
              '&:hover': { bgcolor: 'action.hover' },
            }}
            onClick={() => onPreRequestScriptChange(
              `// Set current timestamp\npm.variables.set('timestamp', Date.now());\n\n// Set ISO date\npm.variables.set('isoDate', new Date().toISOString());`
            )}
          >
            <Typography variant="body2" fontWeight={600}>
              Set timestamp variables
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Add current timestamp and ISO date to variables
            </Typography>
          </Box>

          <Box
            sx={{
              p: 1.5,
              bgcolor: 'background.paper',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              cursor: 'pointer',
              '&:hover': { bgcolor: 'action.hover' },
            }}
            onClick={() => onPreRequestScriptChange(
              `// Generate random values\npm.variables.set('randomId', Math.floor(Math.random() * 1000000));\npm.variables.set('uuid', crypto.randomUUID());`
            )}
          >
            <Typography variant="body2" fontWeight={600}>
              Generate random values
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Create random ID and UUID
            </Typography>
          </Box>

          <Box
            sx={{
              p: 1.5,
              bgcolor: 'background.paper',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              cursor: 'pointer',
              '&:hover': { bgcolor: 'action.hover' },
            }}
            onClick={() => onPreRequestScriptChange(
              `// Log request details\nconsole.log('Request URL:', pm.request.url);\nconsole.log('Request Method:', pm.request.method);\nconsole.log('Request Headers:', pm.request.headers);`
            )}
          >
            <Typography variant="body2" fontWeight={600}>
              Log request details
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Debug request information
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default ScriptsTab;
