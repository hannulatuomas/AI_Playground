import React, { useState, useMemo, useCallback } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import SendIcon from '@mui/icons-material/Send';
import SaveIcon from '@mui/icons-material/Save';
import FormControl from '@mui/material/FormControl';
import CircularProgress from '@mui/material/CircularProgress';
import ParamsTab from './tabs/ParamsTab';
import HeadersTab from './tabs/HeadersTab';
import BodyTab from './tabs/BodyTab';
import AuthTab from './tabs/AuthTab';
import ScriptsTab from './tabs/ScriptsTab';
import TestsTab from './tabs/TestsTab';
import VariablesTab from './tabs/VariablesTab';
import AssertionsTab from './tabs/AssertionsTab';
import type { Request, HttpMethod, QueryParam, Header, RequestBody, Auth, Response, Assertion } from '../../types/models';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = React.memo(({ children, value, index }) => {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box>{children}</Box>}
    </div>
  );
});

TabPanel.displayName = 'TabPanel';

interface RequestPanelProps {
  onResponse?: (response: Response) => void;
  initialRequest?: Request | null;
}

const RequestPanel: React.FC<RequestPanelProps> = React.memo(({ onResponse, initialRequest }) => {
  const [method, setMethod] = useState<HttpMethod>('GET');
  const [url, setUrl] = useState('https://jsonplaceholder.typicode.com/users');
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  
  // Request data
  const [queryParams, setQueryParams] = useState<QueryParam[]>([]);
  const [headers, setHeaders] = useState<Header[]>([
    { key: 'Content-Type', value: 'application/json', enabled: true },
  ]);
  const [body, setBody] = useState<RequestBody>({ type: 'none', content: '' });
  const [auth, setAuth] = useState<Auth>({ type: 'none' });
  const [preRequestScript, setPreRequestScript] = useState('');
  const [testScript, setTestScript] = useState('');
  const [assertions, setAssertions] = useState<Assertion[]>([]);

  // Load request when initialRequest changes
  React.useEffect(() => {
    if (initialRequest) {
      setMethod(initialRequest.method);
      setUrl(initialRequest.url);
      setQueryParams(initialRequest.queryParams || []);
      setHeaders(initialRequest.headers || []);
      setBody(initialRequest.body || { type: 'none', content: '' });
      setAuth(initialRequest.auth || { type: 'none' });
      setPreRequestScript(initialRequest.preRequestScript || '');
      setTestScript(initialRequest.testScript || '');
      setAssertions(initialRequest.assertions || []);
    }
  }, [initialRequest]);

  const handleSend = useCallback(async () => {
    setLoading(true);
    try {
      // Build request object
      const request: Omit<Request, 'id' | 'name' | 'createdAt' | 'updatedAt'> = {
        protocol: 'REST',
        method,
        url,
        headers,
        queryParams,
        body: body.type !== 'none' ? body : undefined,
        auth: auth.type !== 'none' ? auth : undefined,
        preRequestScript: preRequestScript || undefined,
        testScript: testScript || undefined,
        assertions: [],
      };

      // Get variables (global for now)
      const variables = await window.electronAPI.variables.get('global');

      // Send request via IPC
      const response = await window.electronAPI.requests.send(request, variables);
      
      // Pass response to parent
      if (onResponse) {
        onResponse(response);
      }

      console.log('Response received:', response);
    } catch (error) {
      console.error('Request failed:', error);
      // Show error to user
    } finally {
      setLoading(false);
    }
  }, [method, url, headers, queryParams, body, auth, preRequestScript, testScript, onResponse]);

  const handleSave = useCallback(async () => {
    // TODO: Implement save to collection
    console.log('Save request');
  }, []);

  // Memoize tab labels to prevent unnecessary recalculations
  const paramsLabel = useMemo(
    () => `Params ${queryParams.length > 0 ? `(${queryParams.length})` : ''}`,
    [queryParams.length]
  );

  const headersLabel = useMemo(
    () => {
      const enabledCount = headers.filter(h => h.enabled).length;
      return `Headers ${enabledCount > 0 ? `(${enabledCount})` : ''}`;
    },
    [headers]
  );

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Request Builder</Typography>
          <Button
            startIcon={<SaveIcon />}
            onClick={handleSave}
            size="small"
            variant="outlined"
          >
            Save
          </Button>
        </Box>

        {/* URL Bar */}
        <Box sx={{ display: 'flex', gap: 1 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <Select value={method} onChange={e => setMethod(e.target.value as HttpMethod)}>
              <MenuItem value="GET">GET</MenuItem>
              <MenuItem value="POST">POST</MenuItem>
              <MenuItem value="PUT">PUT</MenuItem>
              <MenuItem value="PATCH">PATCH</MenuItem>
              <MenuItem value="DELETE">DELETE</MenuItem>
              <MenuItem value="HEAD">HEAD</MenuItem>
              <MenuItem value="OPTIONS">OPTIONS</MenuItem>
            </Select>
          </FormControl>

          <TextField
            fullWidth
            size="small"
            placeholder="Enter request URL"
            value={url}
            onChange={e => setUrl(e.target.value)}
          />

          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={16} color="inherit" /> : <SendIcon />}
            onClick={handleSend}
            disabled={loading}
            sx={{ minWidth: 100 }}
          >
            {loading ? 'Sending...' : 'Send'}
          </Button>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={activeTab} 
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
          allowScrollButtonsMobile
        >
          <Tab label={paramsLabel} />
          <Tab label={headersLabel} />
          <Tab label="Body" />
          <Tab label="Auth" />
          <Tab label="Settings" />
          <Tab label="Assertions" />
          <Tab label="Pre-request" />
          <Tab label="Tests" />
        </Tabs>
      </Box>

      {/* Tab Panels */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <TabPanel value={activeTab} index={0}>
          <ParamsTab params={queryParams} onChange={setQueryParams} />
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <HeadersTab headers={headers} onChange={setHeaders} />
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <BodyTab body={body} onChange={setBody} />
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <AuthTab auth={auth} onChange={setAuth} />
        </TabPanel>

        <TabPanel value={activeTab} index={4}>
          <VariablesTab />
        </TabPanel>

        <TabPanel value={activeTab} index={5}>
          <AssertionsTab
            assertions={assertions}
            onChange={setAssertions}
          />
        </TabPanel>

        <TabPanel value={activeTab} index={6}>
          <ScriptsTab
            preRequestScript={preRequestScript}
            onPreRequestScriptChange={setPreRequestScript}
          />
        </TabPanel>

        <TabPanel value={activeTab} index={7}>
          <TestsTab
            testScript={testScript}
            onTestScriptChange={setTestScript}
          />
        </TabPanel>
      </Box>
    </Box>
  );
});

RequestPanel.displayName = 'RequestPanel';

export default RequestPanel;
