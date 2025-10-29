import React, { useState } from 'react';
import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Upload as UploadIcon,
  Link as LinkIcon,
  Code as CodeIcon,
} from '@mui/icons-material';

interface SwaggerViewerProps {
  onImport?: (spec: any) => void;
}

const SwaggerViewer: React.FC<SwaggerViewerProps> = ({ onImport }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [url, setUrl] = useState('');
  const [jsonSpec, setJsonSpec] = useState('');
  const [spec, setSpec] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLoadFromURL = async () => {
    if (!url) {
      setError('Please enter a URL');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setSpec(data);
      setError(null);
    } catch (err: any) {
      setError(`Failed to load spec: ${err.message}`);
      setSpec(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadFromJSON = () => {
    if (!jsonSpec.trim()) {
      setError('Please enter a JSON specification');
      return;
    }

    try {
      const data = JSON.parse(jsonSpec);
      setSpec(data);
      setError(null);
    } catch (err: any) {
      setError(`Invalid JSON: ${err.message}`);
      setSpec(null);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const data = JSON.parse(content);
        setSpec(data);
        setError(null);
      } catch (err: any) {
        setError(`Failed to parse file: ${err.message}`);
        setSpec(null);
      }
    };
    reader.readAsText(file);
  };

  const handleImport = () => {
    if (spec && onImport) {
      onImport(spec);
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" gutterBottom>
          OpenAPI / Swagger Viewer
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Load and view OpenAPI 2.0 (Swagger) or OpenAPI 3.x specifications
        </Typography>
      </Box>

      {/* Load Tabs */}
      <Paper sx={{ m: 2 }}>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
          <Tab icon={<LinkIcon />} label="From URL" />
          <Tab icon={<UploadIcon />} label="From File" />
          <Tab icon={<CodeIcon />} label="From JSON" />
        </Tabs>

        <Box sx={{ p: 2 }}>
          {/* From URL */}
          {activeTab === 0 && (
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
              <TextField
                fullWidth
                label="OpenAPI Specification URL"
                placeholder="https://petstore.swagger.io/v2/swagger.json"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleLoadFromURL()}
              />
              <Button
                variant="contained"
                onClick={handleLoadFromURL}
                disabled={loading}
                sx={{ minWidth: 100 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Load'}
              </Button>
            </Box>
          )}

          {/* From File */}
          {activeTab === 1 && (
            <Box>
              <input
                accept=".json,.yaml,.yml"
                style={{ display: 'none' }}
                id="openapi-file-upload"
                type="file"
                onChange={handleFileUpload}
              />
              <label htmlFor="openapi-file-upload">
                <Button variant="contained" component="span" startIcon={<UploadIcon />}>
                  Choose File
                </Button>
              </label>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Select an OpenAPI JSON or YAML file
              </Typography>
            </Box>
          )}

          {/* From JSON */}
          {activeTab === 2 && (
            <Box>
              <TextField
                fullWidth
                multiline
                rows={10}
                label="OpenAPI JSON Specification"
                placeholder='{"openapi": "3.0.0", "info": {...}, "paths": {...}}'
                value={jsonSpec}
                onChange={(e) => setJsonSpec(e.target.value)}
                sx={{
                  fontFamily: 'monospace',
                  '& textarea': {
                    fontFamily: 'monospace',
                    fontSize: '0.875rem',
                  },
                }}
              />
              <Button
                variant="contained"
                onClick={handleLoadFromJSON}
                sx={{ mt: 2 }}
              >
                Load Specification
              </Button>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mx: 2, mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Import Button */}
      {spec && onImport && (
        <Box sx={{ px: 2, pb: 2 }}>
          <Button
            variant="contained"
            color="success"
            onClick={handleImport}
            fullWidth
          >
            Import as Collection
          </Button>
        </Box>
      )}

      {/* Swagger UI */}
      {spec && (
        <Box sx={{ flex: 1, overflow: 'auto', px: 2, pb: 2 }}>
          <SwaggerUI spec={spec} />
        </Box>
      )}

      {/* Empty State */}
      {!spec && !loading && (
        <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4 }}>
          <Box sx={{ textAlign: 'center', maxWidth: 400 }}>
            <Typography variant="h6" gutterBottom>
              No Specification Loaded
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Load an OpenAPI specification from a URL, file, or paste JSON to view the API documentation
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Popular examples:
            </Typography>
            <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Button
                size="small"
                onClick={() => {
                  setUrl('https://petstore.swagger.io/v2/swagger.json');
                  setActiveTab(0);
                }}
              >
                Petstore API (Swagger 2.0)
              </Button>
              <Button
                size="small"
                onClick={() => {
                  setUrl('https://petstore3.swagger.io/api/v3/openapi.json');
                  setActiveTab(0);
                }}
              >
                Petstore API (OpenAPI 3.0)
              </Button>
            </Box>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default SwaggerViewer;
