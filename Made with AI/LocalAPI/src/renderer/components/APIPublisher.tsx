/**
 * APIPublisher - API Documentation Publishing UI
 * 
 * Comprehensive UI for generating and publishing API documentation
 */

import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Select,
  Stepper,
  Step,
  StepLabel,
  TextField,
  Typography,
  Checkbox,
  Radio,
  RadioGroup,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Chip,
} from '@mui/material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export const APIPublisher: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [activeTab, setActiveTab] = useState(0);
  
  // Configuration state
  const [source, setSource] = useState<'openapi' | 'collection'>('openapi');
  const [specFile, setSpecFile] = useState('');
  const [title, setTitle] = useState('');
  const [version, setVersion] = useState('1.0.0');
  const [description, setDescription] = useState('');
  
  // Documentation options
  const [theme, setTheme] = useState<'light' | 'dark' | 'modern' | 'classic'>('modern');
  const [includeExplorer, setIncludeExplorer] = useState(true);
  const [includeAuth, setIncludeAuth] = useState(true);
  const [includeExamples, setIncludeExamples] = useState(true);
  const [includeChangelog, setIncludeChangelog] = useState(false);
  
  // Export options
  const [exportFormat, setExportFormat] = useState<'html' | 'markdown' | 'pdf'>('html');
  const [sdkLanguage, setSDKLanguage] = useState<'javascript' | 'typescript' | 'python' | 'java' | 'csharp' | 'go' | 'php'>('typescript');
  const [generateSDK, setGenerateSDK] = useState(false);
  
  // Publishing options
  const [publishTarget, setPublishTarget] = useState<'server' | 'directory' | 'both'>('directory');
  const [serverPort, setServerPort] = useState(3000);
  const [outputDirectory, setOutputDirectory] = useState('./docs');
  
  // State
  const [loading, setLoading] = useState(false);
  const [generatedDoc, setGeneratedDoc] = useState<string>('');
  const [publishResult, setPublishResult] = useState<any>(null);
  const [serverUrl, setServerUrl] = useState<string>('');

  const steps = ['Select Source', 'Configure', 'Generate', 'Publish'];

  const handleNext = () => {
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      // Get OpenAPI spec (from file or generate from collection)
      let spec;
      if (source === 'openapi' && specFile) {
        spec = await window.electronAPI.apispec.loadOpenAPIFile(specFile);
      } else {
        // Generate from console/collection
        const entries = await window.electronAPI.console.getEntries({}, 100);
        const analysis = await window.electronAPI.apispec.analyze(entries);
        spec = await window.electronAPI.apispec.generateOpenAPI(analysis, {
          title,
          version,
          description,
        });
      }

      // Generate documentation
      const docOptions = {
        title,
        version,
        description,
        theme,
        includeExplorer,
        includeAuth,
        includeExamples,
        includeChangelog,
      };

      const doc = await window.electronAPI.publishing.generateDocumentation(spec, docOptions);
      setGeneratedDoc(doc.html);

      // Generate SDK if requested
      if (generateSDK) {
        await window.electronAPI.publishing.generateSDK(spec, {
          language: sdkLanguage,
          packageName: title.toLowerCase().replace(/\s+/g, '-'),
        });
      }

      // Generate Markdown if requested
      if (exportFormat === 'markdown') {
        await window.electronAPI.publishing.exportMarkdown(spec, {
          includeExamples,
        });
      }

      handleNext();
    } catch (error) {
      console.error('Error generating documentation:', error);
      alert('Error: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {
    setLoading(true);
    try {
      const results = [];
      const doc = { html: generatedDoc, css: '', js: '' };

      if (publishTarget === 'server' || publishTarget === 'both') {
        const serverResult = await window.electronAPI.publishing.publish(doc, {
          target: 'server',
          port: serverPort,
        });
        results.push(serverResult);
        if (serverResult.success && serverResult.url) {
          setServerUrl(serverResult.url);
        }
      }

      if (publishTarget === 'directory' || publishTarget === 'both') {
        const dirResult = await window.electronAPI.publishing.publish(doc, {
          target: 'directory',
          directory: outputDirectory,
        });
        results.push(dirResult);
      }

      setPublishResult(results);
      handleNext();
    } catch (error) {
      console.error('Error publishing:', error);
      alert('Error: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleStopServer = async () => {
    try {
      await window.electronAPI.publishing.stopServer();
      setServerUrl('');
      alert('Server stopped');
    } catch (error) {
      console.error('Error stopping server:', error);
    }
  };

  const handleOpenDirectory = async () => {
    try {
      await window.electronAPI.publishing.openDirectory(outputDirectory);
    } catch (error) {
      console.error('Error opening directory:', error);
    }
  };

  return (
    <Box sx={{ width: '100%', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        API Documentation Publisher
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Step 1: Select Source */}
      {activeStep === 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Select Documentation Source
            </Typography>

            <FormControl component="fieldset" sx={{ mt: 2 }}>
              <RadioGroup value={source} onChange={(e) => setSource(e.target.value as any)}>
                <FormControlLabel
                  value="openapi"
                  control={<Radio />}
                  label="Import OpenAPI Specification"
                />
                <FormControlLabel
                  value="collection"
                  control={<Radio />}
                  label="Generate from Console/Collection"
                />
              </RadioGroup>
            </FormControl>

            {source === 'openapi' && (
              <Box sx={{ mt: 2 }}>
                <TextField
                  fullWidth
                  label="OpenAPI Spec File Path"
                  value={specFile}
                  onChange={(e) => setSpecFile(e.target.value)}
                  placeholder="/path/to/openapi.json"
                />
              </Box>
            )}

            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
              <Button variant="contained" onClick={handleNext}>
                Next
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Configure */}
      {activeStep === 1 && (
        <Card>
          <CardContent>
            <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
              <Tab label="Basic Info" />
              <Tab label="Documentation" />
              <Tab label="Export" />
            </Tabs>

            <TabPanel value={activeTab} index={0}>
              <TextField
                fullWidth
                label="API Title"
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
                multiline
                rows={3}
                label="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </TabPanel>

            <TabPanel value={activeTab} index={1}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Theme</InputLabel>
                <Select value={theme} onChange={(e) => setTheme(e.target.value as any)}>
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="dark">Dark</MenuItem>
                  <MenuItem value="modern">Modern</MenuItem>
                  <MenuItem value="classic">Classic</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Checkbox
                    checked={includeExplorer}
                    onChange={(e) => setIncludeExplorer(e.target.checked)}
                  />
                }
                label="Include Interactive Explorer"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={includeAuth}
                    onChange={(e) => setIncludeAuth(e.target.checked)}
                  />
                }
                label="Include Authentication Documentation"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={includeExamples}
                    onChange={(e) => setIncludeExamples(e.target.checked)}
                  />
                }
                label="Include Examples"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={includeChangelog}
                    onChange={(e) => setIncludeChangelog(e.target.checked)}
                  />
                }
                label="Include Changelog"
              />
            </TabPanel>

            <TabPanel value={activeTab} index={2}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Export Format</InputLabel>
                <Select value={exportFormat} onChange={(e) => setExportFormat(e.target.value as any)}>
                  <MenuItem value="html">HTML</MenuItem>
                  <MenuItem value="markdown">Markdown</MenuItem>
                  <MenuItem value="pdf">PDF</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Checkbox
                    checked={generateSDK}
                    onChange={(e) => setGenerateSDK(e.target.checked)}
                  />
                }
                label="Generate Client SDK"
              />

              {generateSDK && (
                <FormControl fullWidth sx={{ mt: 2 }}>
                  <InputLabel>SDK Language</InputLabel>
                  <Select value={sdkLanguage} onChange={(e) => setSDKLanguage(e.target.value as any)}>
                    <MenuItem value="javascript">JavaScript</MenuItem>
                    <MenuItem value="typescript">TypeScript</MenuItem>
                    <MenuItem value="python">Python</MenuItem>
                    <MenuItem value="java">Java</MenuItem>
                    <MenuItem value="csharp">C#</MenuItem>
                    <MenuItem value="go">Go</MenuItem>
                    <MenuItem value="php">PHP</MenuItem>
                  </Select>
                </FormControl>
              )}
            </TabPanel>

            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
              <Button onClick={handleBack}>Back</Button>
              <Button variant="contained" onClick={handleGenerate} disabled={loading}>
                {loading ? <CircularProgress size={24} /> : 'Generate'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Preview */}
      {activeStep === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Documentation Preview
            </Typography>

            <Alert severity="success" sx={{ mb: 2 }}>
              Documentation generated successfully!
            </Alert>

            <Box
              sx={{
                border: '1px solid #ddd',
                borderRadius: 1,
                p: 2,
                maxHeight: 400,
                overflow: 'auto',
                bgcolor: '#f5f5f5',
              }}
            >
              <div dangerouslySetInnerHTML={{ __html: generatedDoc.substring(0, 1000) + '...' }} />
            </Box>

            <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
              Publishing Options
            </Typography>

            <FormControl component="fieldset">
              <RadioGroup value={publishTarget} onChange={(e) => setPublishTarget(e.target.value as any)}>
                <FormControlLabel value="server" control={<Radio />} label="Local HTTP Server" />
                <FormControlLabel value="directory" control={<Radio />} label="Static Directory" />
                <FormControlLabel value="both" control={<Radio />} label="Both" />
              </RadioGroup>
            </FormControl>

            {(publishTarget === 'server' || publishTarget === 'both') && (
              <TextField
                fullWidth
                type="number"
                label="Server Port"
                value={serverPort}
                onChange={(e) => setServerPort(parseInt(e.target.value))}
                sx={{ mt: 2 }}
              />
            )}

            {(publishTarget === 'directory' || publishTarget === 'both') && (
              <TextField
                fullWidth
                label="Output Directory"
                value={outputDirectory}
                onChange={(e) => setOutputDirectory(e.target.value)}
                sx={{ mt: 2 }}
              />
            )}

            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
              <Button onClick={handleBack}>Back</Button>
              <Button variant="contained" onClick={handlePublish} disabled={loading}>
                {loading ? <CircularProgress size={24} /> : 'Publish'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Step 4: Published */}
      {activeStep === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Documentation Published!
            </Typography>

            {publishResult && publishResult.map((result: any, index: number) => (
              <Alert key={index} severity={result.success ? 'success' : 'error'} sx={{ mb: 2 }}>
                {result.success ? (
                  <>
                    {result.url && (
                      <Box>
                        <Typography>Server running at: <strong>{result.url}</strong></Typography>
                        <Box sx={{ mt: 1 }}>
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => window.open(result.url)}
                            sx={{ mr: 1 }}
                          >
                            Open in Browser
                          </Button>
                          <Button size="small" variant="outlined" onClick={handleStopServer}>
                            Stop Server
                          </Button>
                        </Box>
                      </Box>
                    )}
                    {result.path && (
                      <Box>
                        <Typography>Files saved to: <strong>{result.path}</strong></Typography>
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={handleOpenDirectory}
                          sx={{ mt: 1 }}
                        >
                          Open Directory
                        </Button>
                      </Box>
                    )}
                  </>
                ) : (
                  <Typography>Error: {result.error}</Typography>
                )}
              </Alert>
            ))}

            <Box sx={{ mt: 3 }}>
              <Button variant="contained" onClick={() => setActiveStep(0)}>
                Publish Another
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};
