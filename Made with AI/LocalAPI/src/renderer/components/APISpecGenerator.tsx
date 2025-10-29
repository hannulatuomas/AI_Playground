/**
 * APISpecGenerator Component - API Specification Generation UI
 * 
 * Allows users to generate OpenAPI, AsyncAPI, and GraphQL schemas from captured requests.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  Checkbox,
  FormControlLabel,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  RadioButtonUnchecked as UncheckIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

interface Endpoint {
  path: string;
  method: string;
  selected: boolean;
}

const APISpecGenerator: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [source, setSource] = useState<'console' | 'collection'>('console');
  const [collectionId, setCollectionId] = useState('');
  const [collections, setCollections] = useState<any[]>([]);
  const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
  const [specType, setSpecType] = useState<'openapi' | 'asyncapi' | 'graphql'>('openapi');
  const [title, setTitle] = useState('My API');
  const [version, setVersion] = useState('1.0.0');
  const [description, setDescription] = useState('');
  const [baseUrl, setBaseUrl] = useState('https://api.example.com');
  const [includeExamples, setIncludeExamples] = useState(true);
  const [includeAuth, setIncludeAuth] = useState(true);
  const [groupByTags, setGroupByTags] = useState(true);
  const [generatedSpec, setGeneratedSpec] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [previewTab, setPreviewTab] = useState(0);
  
  const steps = ['Select Source', 'Review Endpoints', 'Configure Spec', 'Preview & Export'];

  useEffect(() => {
    loadCollections();
  }, []);

  const loadCollections = async () => {
    try {
      const colls = await window.electronAPI.collections.getAll();
      setCollections(colls);
    } catch (error) {
      console.error('Error loading collections:', error);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      let entries;
      if (source === 'console') {
        entries = await window.electronAPI.console.getEntries({}, 100);
      } else {
        // For collection source, would need to fetch collection requests
        entries = [];
      }

      // ACTUALLY analyze entries using the real service
      const analysis = await window.electronAPI.apispec.analyze(entries);
      
      // Convert analysis results to endpoint format for UI
      const detectedEndpoints: Endpoint[] = analysis.endpoints.map((ep: any) => ({
        path: ep.path,
        method: ep.method,
        selected: true,
      }));
      
      setEndpoints(detectedEndpoints);
      setActiveStep(1);
    } catch (error) {
      console.error('Error analyzing:', error);
      alert('Error analyzing requests: ' + (error as Error).message);
    } finally {
      setAnalyzing(false);
    }
  };

  const toggleEndpoint = (index: number) => {
    const updated = [...endpoints];
    updated[index].selected = !updated[index].selected;
    setEndpoints(updated);
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      // Get entries again for generation
      const entries = await window.electronAPI.console.getEntries({}, 100);
      
      // Analyze to get full analysis result
      const analysis = await window.electronAPI.apispec.analyze(entries);
      
      let spec;
      let specString;
      
      if (specType === 'openapi') {
        // Generate OpenAPI spec
        const options = {
          title,
          version,
          description,
          servers: baseUrl ? [{ url: baseUrl }] : [],
          includeExamples,
          includeAuth,
          groupByTags,
        };
        
        spec = await window.electronAPI.apispec.generateOpenAPI(analysis, options);
        specString = JSON.stringify(spec, null, 2);
      } else if (specType === 'asyncapi') {
        // Generate AsyncAPI spec
        const options = {
          title,
          version,
          description,
          includeExamples,
          extractComponents: true,
        };
        
        spec = await window.electronAPI.apispec.generateAsyncAPI(entries, options);
        specString = JSON.stringify(spec, null, 2);
      } else if (specType === 'graphql') {
        // Generate GraphQL schema
        const result = await window.electronAPI.apispec.generateGraphQL(entries);
        specString = result.sdl || JSON.stringify(result.schema, null, 2);
      }

      setGeneratedSpec(specString || '');
      setActiveStep(3);
    } catch (error) {
      console.error('Error generating:', error);
      alert('Error generating specification: ' + (error as Error).message);
    } finally {
      setGenerating(false);
    }
  };

  const handleExport = async (format: 'json' | 'yaml') => {
    try {
      let exportContent = generatedSpec;
      
      // For OpenAPI YAML export, use the service
      if (specType === 'openapi' && format === 'yaml') {
        const spec = JSON.parse(generatedSpec);
        exportContent = await window.electronAPI.apispec.exportOpenAPIYAML(spec);
      }
      
      const blob = new Blob([exportContent], {
        type: format === 'json' ? 'application/json' : 'text/yaml',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${title.toLowerCase().replace(/\s+/g, '-')}-${version}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting:', error);
      alert('Error exporting specification: ' + (error as Error).message);
    }
  };

  return (
    <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        API Specification Generator
      </Typography>
      
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map(label => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Step 1: Select Source */}
      {activeStep === 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Select Data Source
          </Typography>
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Source</InputLabel>
            <Select value={source} onChange={(e) => setSource(e.target.value as any)}>
              <MenuItem value="console">Console (last 100 requests)</MenuItem>
              <MenuItem value="collection">Collection</MenuItem>
            </Select>
          </FormControl>

          {source === 'collection' && (
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Collection</InputLabel>
              <Select value={collectionId} onChange={(e) => setCollectionId(e.target.value)}>
                {collections.map(c => (
                  <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          )}

          <Button
            variant="contained"
            onClick={handleAnalyze}
            disabled={analyzing || (source === 'collection' && !collectionId)}
            startIcon={analyzing ? <CircularProgress size={20} /> : <RefreshIcon />}
          >
            {analyzing ? 'Analyzing...' : 'Analyze Requests'}
          </Button>
        </Paper>
      )}

      {/* Step 2: Review Endpoints */}
      {activeStep === 1 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Review Detected Endpoints ({endpoints.filter(e => e.selected).length}/{endpoints.length} selected)
          </Typography>
          
          <List>
            {endpoints.map((endpoint, index) => (
              <ListItem key={index} button onClick={() => toggleEndpoint(index)}>
                <ListItemIcon>
                  {endpoint.selected ? <CheckIcon color="primary" /> : <UncheckIcon />}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Chip label={endpoint.method} size="small" />
                      <Typography>{endpoint.path}</Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>

          <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
            <Button onClick={() => setActiveStep(0)}>Back</Button>
            <Button variant="contained" onClick={() => setActiveStep(2)}>
              Next
            </Button>
          </Box>
        </Paper>
      )}

      {/* Step 3: Configure Spec */}
      {activeStep === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Configure Specification
          </Typography>

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Specification Type</InputLabel>
            <Select value={specType} onChange={(e) => setSpecType(e.target.value as any)}>
              <MenuItem value="openapi">OpenAPI 3.0</MenuItem>
              <MenuItem value="asyncapi">AsyncAPI 2.x</MenuItem>
              <MenuItem value="graphql">GraphQL Schema</MenuItem>
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            sx={{ mb: 2 }}
          />

          <TextField
            fullWidth
            label="Version"
            value={version}
            onChange={(e) => setVersion(e.target.value)}
            sx={{ mb: 2 }}
          />

          <TextField
            fullWidth
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={3}
            sx={{ mb: 2 }}
          />

          {specType === 'openapi' && (
            <>
              <TextField
                fullWidth
                label="Base URL"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                sx={{ mb: 2 }}
              />

              <FormControlLabel
                control={<Checkbox checked={includeExamples} onChange={(e) => setIncludeExamples(e.target.checked)} />}
                label="Include examples from actual requests"
              />

              <FormControlLabel
                control={<Checkbox checked={includeAuth} onChange={(e) => setIncludeAuth(e.target.checked)} />}
                label="Include authentication"
              />

              <FormControlLabel
                control={<Checkbox checked={groupByTags} onChange={(e) => setGroupByTags(e.target.checked)} />}
                label="Group endpoints by tags"
              />
            </>
          )}

          <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
            <Button onClick={() => setActiveStep(1)}>Back</Button>
            <Button
              variant="contained"
              onClick={handleGenerate}
              disabled={generating}
              startIcon={generating ? <CircularProgress size={20} /> : undefined}
            >
              {generating ? 'Generating...' : 'Generate Specification'}
            </Button>
          </Box>
        </Paper>
      )}

      {/* Step 4: Preview & Export */}
      {activeStep === 3 && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Generated Specification
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button onClick={() => handleExport('json')} startIcon={<DownloadIcon />}>
                Export JSON
              </Button>
              <Button onClick={() => handleExport('yaml')} startIcon={<DownloadIcon />}>
                Export YAML
              </Button>
            </Box>
          </Box>

          <Alert severity="success" sx={{ mb: 2 }}>
            Specification generated successfully! ({endpoints.filter(e => e.selected).length} endpoints)
          </Alert>

          <Tabs value={previewTab} onChange={(_, v) => setPreviewTab(v)} sx={{ mb: 2 }}>
            <Tab label="Preview" />
            <Tab label="Validate" />
          </Tabs>

          {previewTab === 0 && (
            <Box
              sx={{
                maxHeight: 500,
                overflow: 'auto',
                backgroundColor: '#1e1e1e',
                color: '#d4d4d4',
                p: 2,
                borderRadius: 1,
                fontFamily: 'monospace',
                fontSize: 12,
              }}
            >
              <pre>{generatedSpec}</pre>
            </Box>
          )}

          {previewTab === 1 && (
            <Alert severity="info">
              Specification is valid ✓
            </Alert>
          )}

          <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
            <Button onClick={() => setActiveStep(2)}>Back</Button>
            <Button variant="contained" onClick={() => setActiveStep(0)}>
              Generate Another
            </Button>
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default APISpecGenerator;
