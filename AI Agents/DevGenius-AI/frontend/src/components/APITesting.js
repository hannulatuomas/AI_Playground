import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Plus, Trash2, Play, FolderPlus, Copy, Code2, Menu, X, ChevronLeft, ChevronRight } from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-powershell';
import 'prismjs/components/prism-csharp';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HTTP_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'];
const REQUEST_TYPES = ['REST', 'GraphQL', 'SOAP', 'WebSocket'];
const BODY_TYPES = ['none', 'json', 'raw', 'form-data', 'xml', 'binary'];
const COMMON_HEADERS = [
  'Content-Type',
  'Authorization',
  'Accept',
  'User-Agent',
  'Cache-Control',
  'X-API-Key',
  'X-Requested-With',
  'Origin',
  'Referer'
];

function APITesting() {
  const [collections, setCollections] = useState([]);
  const [requests, setRequests] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [selectedRequest, setSelectedRequest] = useState(null);
  
  const [showCollectionDialog, setShowCollectionDialog] = useState(false);
  const [showRequestDialog, setShowRequestDialog] = useState(false);
  const [showCodeDialog, setShowCodeDialog] = useState(false);
  const [showVariablesDialog, setShowVariablesDialog] = useState(false);
  
  // Mobile state management
  const [collectionsOpen, setCollectionsOpen] = useState(false);
  const [requestsOpen, setRequestsOpen] = useState(false);
  const [mobileView, setMobileView] = useState('collections'); // 'collections', 'requests', 'details'
  
  // Enhanced state for variables, headers, params, body
  const [environmentVars, setEnvironmentVars] = useState([]);
  const [requestHeaders, setRequestHeaders] = useState([{ key: '', value: '', enabled: true }]);
  const [queryParams, setQueryParams] = useState([{ key: '', value: '', enabled: true }]);
  const [bodyType, setBodyType] = useState('none');
  const [bodyContent, setBodyContent] = useState('');
  const [formData, setFormData] = useState([{ key: '', value: '', enabled: true }]);
  
  const [newCollection, setNewCollection] = useState({ name: '', description: '', environment_vars: {} });
  const [newRequest, setNewRequest] = useState({
    name: 'New Request',
    method: 'GET',
    url: 'https://api.example.com',
    headers: {},
    body: '',
    request_type: 'REST'
  });
  
  const [envVars, setEnvVars] = useState([]);
  const [headers, setHeaders] = useState([]);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const [codeLanguage, setCodeLanguage] = useState('javascript');

  useEffect(() => {
    loadCollections();
  }, []);

  useEffect(() => {
    if (selectedRequest) {
      // Populate enhanced state from selected request
      loadRequests(selectedCollection);
    }
  }, [selectedCollection]);

  useEffect(() => {
    if (selectedRequest) {
      // Parse and populate headers
      const headers = [];
      if (selectedRequest.headers && typeof selectedRequest.headers === 'object') {
        Object.entries(selectedRequest.headers).forEach(([key, value]) => {
          headers.push({ key, value, enabled: true });
        });
      }
      setRequestHeaders(headers.length > 0 ? headers : [{ key: '', value: '', enabled: true }]);

      // Parse query params from URL
      if (selectedRequest.url) {
        const params = parseQueryParamsFromURL(selectedRequest.url);
        setQueryParams(params);
      }

      // Set body content and type
      if (selectedRequest.body) {
        try {
          // Try to parse as JSON
          JSON.parse(selectedRequest.body);
          setBodyType('json');
          setBodyContent(JSON.stringify(JSON.parse(selectedRequest.body), null, 2));
        } catch {
          setBodyType('raw');
          setBodyContent(selectedRequest.body);
        }
      } else {
        setBodyType('none');
        setBodyContent('');
      }
    }
  }, [selectedRequest]);

  useEffect(() => {
    if (selectedCollection) {
      // Load environment variables for collection
      const collection = collections.find(c => c.id === selectedCollection);
      if (collection && collection.environment_vars) {
        const vars = Object.entries(collection.environment_vars).map(([key, value]) => ({
          key,
          value,
          enabled: true
        }));
        setEnvironmentVars(vars.length > 0 ? vars : []);
      }
    }
  }, [selectedCollection, collections]);

  useEffect(() => {
    if (generatedCode) {
      Prism.highlightAll();
    }
  }, [generatedCode, codeLanguage]);

  // Helper: Replace {{variables}} in a string
  const replaceVariables = (str) => {
    if (!str || typeof str !== 'string') return str;
    
    let result = str;
    environmentVars.forEach(variable => {
      if (variable.key && variable.value) {
        const regex = new RegExp(`\\{\\{${variable.key}\\}\\}`, 'g');
        result = result.replace(regex, variable.value);
      }
    });
    return result;
  };

  // Helper: Parse query params from URL
  const parseQueryParamsFromURL = (url) => {
    try {
      const urlObj = new URL(url);
      const params = [];
      urlObj.searchParams.forEach((value, key) => {
        params.push({ key, value, enabled: true });
      });
      return params.length > 0 ? params : [{ key: '', value: '', enabled: true }];
    } catch {
      return [{ key: '', value: '', enabled: true }];
    }
  };

  // Helper: Build URL with query params
  const buildURLWithParams = (baseUrl, params) => {
    try {
      const urlObj = new URL(baseUrl);
      // Clear existing params
      urlObj.search = '';
      
      // Add enabled params
      params.forEach(param => {
        if (param.enabled && param.key) {
          urlObj.searchParams.append(param.key, param.value || '');
        }
      });
      
      return urlObj.toString();
    } catch {
      return baseUrl;
    }
  };

  // Helper: Convert headers array to object
  const headersArrayToObject = (headersArray) => {
    const obj = {};
    headersArray.forEach(header => {
      if (header.enabled && header.key) {
        obj[header.key] = replaceVariables(header.value);
      }
    });
    return obj;
  };

  // Helper: Convert form data to body string
  const formDataToBody = (formDataArray) => {
    const formData = new FormData();
    formDataArray.forEach(item => {
      if (item.enabled && item.key) {
        formData.append(item.key, replaceVariables(item.value));
      }
    });
    return formData;
  };

  const loadCollections = async () => {
    try {
      const res = await axios.get(`${API}/api-collections`);
      setCollections(res.data);
    } catch (error) {
      console.error('Failed to load collections:', error);
    }
  };

  const loadRequests = async (collectionId) => {
    try {
      const res = await axios.get(`${API}/api-requests?collection_id=${collectionId}`);
      setRequests(res.data);
    } catch (error) {
      console.error('Failed to load requests:', error);
    }
  };

  const createCollection = async () => {
    try {
      // Convert env vars array to object
      const envVarsObj = {};
      envVars.forEach(ev => {
        if (ev.key && ev.value) {
          envVarsObj[ev.key] = ev.value;
        }
      });
      
      await axios.post(`${API}/api-collections`, {
        ...newCollection,
        environment_vars: envVarsObj
      });
      
      loadCollections();
      setShowCollectionDialog(false);
      setNewCollection({ name: '', description: '', environment_vars: {} });
      setEnvVars([]);
      toast.success('Collection created');
    } catch (error) {
      toast.error('Failed to create collection');
    }
  };

  const deleteCollection = async (id) => {
    try {
      await axios.delete(`${API}/api-collections/${id}`);
      loadCollections();
      if (selectedCollection === id) {
        setSelectedCollection(null);
        setRequests([]);
      }
      toast.success('Collection deleted');
    } catch (error) {
      toast.error('Failed to delete collection');
    }
  };

  const createRequest = async () => {
    try {
      // Convert headers array to object
      const headersObj = {};
      headers.forEach(h => {
        if (h.key && h.value) {
          headersObj[h.key] = h.value;
        }
      });
      
      await axios.post(`${API}/api-requests`, {
        ...newRequest,
        collection_id: selectedCollection,
        headers: headersObj
      });
      
      loadRequests(selectedCollection);
      setShowRequestDialog(false);
      setNewRequest({
        name: 'New Request',
        method: 'GET',
        url: 'https://api.example.com',
        headers: {},
        body: '',
        request_type: 'REST'
      });
      setHeaders([]);
      toast.success('Request created');
    } catch (error) {
      toast.error('Failed to create request');
    }
  };

  const deleteRequest = async (id) => {
    try {
      await axios.delete(`${API}/api-requests/${id}`);
      loadRequests(selectedCollection);
      if (selectedRequest?.id === id) {
        setSelectedRequest(null);
      }
      toast.success('Request deleted');
    } catch (error) {
      toast.error('Failed to delete request');
    }
  };

  const executeRequest = async () => {
    if (!selectedRequest) return;
    
    setLoading(true);
    setResponse(null);
    
    try {
      const collection = collections.find(c => c.id === selectedCollection);
      const envVars = collection?.environment_vars || {};
      
      const res = await axios.post(`${API}/api-requests/${selectedRequest.id}/execute`, envVars);
      setResponse(res.data);
    } catch (error) {
      setResponse({
        status: 0,
        statusText: 'Error',
        error: error.message
      });
    } finally {
      setLoading(false);
    }
  };

  const generateCode = (language) => {
    if (!selectedRequest) return;
    
    const req = selectedRequest;
    let code = '';
    
    switch (language) {
      case 'javascript':
        code = `// Fetch API
fetch('${req.url}', {
  method: '${req.method}',
  headers: ${JSON.stringify(req.headers || {}, null, 2)},
  ${req.body && req.method !== 'GET' ? `body: JSON.stringify(${req.body})` : ''}
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));`;
        break;
      
      case 'python':
        code = `import requests

url = '${req.url}'
headers = ${JSON.stringify(req.headers || {}, null, 2)}
${req.body && req.method !== 'GET' ? `data = ${req.body}` : ''}

response = requests.${req.method.toLowerCase()}(url, headers=headers${req.body && req.method !== 'GET' ? ', json=data' : ''})
print(response.json())`;
        break;
      
      case 'curl':
        let curlCmd = `curl -X ${req.method} '${req.url}'`;
        if (req.headers) {
          Object.entries(req.headers).forEach(([key, value]) => {
            curlCmd += ` \\
  -H '${key}: ${value}'`;
          });
        }
        if (req.body && req.method !== 'GET') {
          curlCmd += ` \\
  -d '${req.body}'`;
        }
        code = curlCmd;
        break;
      
      case 'csharp':
        code = `using System;
using System.Net.Http;
using System.Threading.Tasks;

var client = new HttpClient();
${req.headers ? Object.entries(req.headers).map(([k,v]) => `client.DefaultRequestHeaders.Add("${k}", "${v}");`).join('\n') : ''}

var response = await client.${req.method === 'GET' ? 'GetAsync' : 'PostAsync'}("${req.url}"${req.body && req.method !== 'GET' ? `, new StringContent("${req.body}", Encoding.UTF8, "application/json")` : ''});
var content = await response.Content.ReadAsStringAsync();
Console.WriteLine(content);`;
        break;
      
      case 'powershell':
        code = `$headers = @{\n${req.headers ? Object.entries(req.headers).map(([k,v]) => `  "${k}" = "${v}"`).join('\n') : ''}\n}

${req.body && req.method !== 'GET' ? `$body = '${req.body}'\n\n` : ''}Invoke-RestMethod -Uri '${req.url}' -Method ${req.method} -Headers $headers${req.body && req.method !== 'GET' ? ' -Body $body' : ''}`;
        break;
      
      default:
        code = 'Language not supported';
    }
    
    setCodeLanguage(language);
    setGeneratedCode(code);
    setShowCodeDialog(true);
  };

  const copyCode = async () => {
    try {
      // Modern Clipboard API (preferred)
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(generatedCode);
        toast.success('Code copied to clipboard');
      } else {
        // Fallback method for non-secure contexts or older browsers
        const textArea = document.createElement('textarea');
        textArea.value = generatedCode;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
          const successful = document.execCommand('copy');
          if (successful) {
            toast.success('Code copied to clipboard');
          } else {
            throw new Error('Copy command failed');
          }
        } catch (err) {
          // If all else fails, show the code in a prompt
          toast.info('Please copy manually (Ctrl+C)', { duration: 5000 });
          console.error('Copy failed:', err);
        } finally {
          document.body.removeChild(textArea);
        }
      }
    } catch (err) {
      console.error('Failed to copy:', err);
      toast.error('Failed to copy code. Please copy manually.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex flex-col lg:flex-row">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-900/20 via-transparent to-transparent pointer-events-none" />
      
      {/* Header with Back Navigation - Mobile & Desktop */}
      <div className="lg:hidden relative backdrop-blur-xl bg-white/5 border-b border-white/10 p-3 flex items-center justify-between z-10">
        <Link to="/" className="flex items-center gap-2" data-testid="back-to-home">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
            <Code2 className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-lg font-bold text-white">API Tester</h1>
        </Link>
        <div className="flex gap-2">
          <Button
            variant={mobileView === 'collections' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setMobileView('collections')}
            className={`text-xs ${mobileView === 'collections' ? 'bg-indigo-500' : 'text-white'}`}
          >
            Collections
          </Button>
          <Button
            variant={mobileView === 'requests' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setMobileView('requests')}
            className={`text-xs ${mobileView === 'requests' ? 'bg-blue-500' : 'text-white'}`}
            disabled={!selectedCollection}
          >
            Requests
          </Button>
          <Button
            variant={mobileView === 'details' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setMobileView('details')}
            className={`text-xs ${mobileView === 'details' ? 'bg-green-500' : 'text-white'}`}
            disabled={!selectedRequest}
          >
            Test
          </Button>
        </div>
      </div>
      
      {/* Overlay for mobile sidebars */}
      {(collectionsOpen || requestsOpen) && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => {
            setCollectionsOpen(false);
            setRequestsOpen(false);
          }}
        />
      )}
      
      {/* Collections Sidebar - Responsive */}
      <div className={`
        ${mobileView === 'collections' ? 'flex' : 'hidden'} lg:flex
        relative lg:w-80 w-full backdrop-blur-xl bg-white/5 lg:border-r border-white/10 flex-col
      `}>
        <div className="p-4 sm:p-6 border-b border-white/10">
          {/* Desktop Back Navigation */}
          <Link to="/" className="hidden lg:flex items-center gap-3 mb-4 hover:opacity-80 transition-opacity" data-testid="back-to-home-desktop">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
              <Code2 className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-xl font-bold text-white">API Tester</h2>
          </Link>
          
          <h2 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4 lg:hidden">API Collections</h2>
          <Dialog open={showCollectionDialog} onOpenChange={setShowCollectionDialog}>
            <DialogTrigger asChild>
              <Button className="w-full bg-gradient-to-r from-indigo-500 to-purple-500 h-9 text-sm sm:text-base" data-testid="new-collection-btn">
                <FolderPlus className="w-4 h-4 mr-2" />
                New Collection
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-slate-900 border-white/10 max-w-[95vw] sm:max-w-lg">
              <DialogHeader>
                <DialogTitle className="text-white text-lg sm:text-xl">Create Collection</DialogTitle>
                <DialogDescription className="text-slate-300 text-sm">Organize your API requests</DialogDescription>
              </DialogHeader>
              <div className="space-y-3 sm:space-y-4 mt-4 max-h-[60vh] overflow-y-auto">
                <div>
                  <Label className="text-white mb-2 block text-sm">Name</Label>
                  <Input
                    value={newCollection.name}
                    onChange={(e) => setNewCollection({...newCollection, name: e.target.value})}
                    placeholder="My API Collection"
                    className="bg-white/10 border-white/20 text-white h-9 text-sm"
                    data-testid="collection-name-input"
                  />
                </div>
                <div>
                  <Label className="text-white mb-2 block text-sm">Description</Label>
                  <Textarea
                    value={newCollection.description}
                    onChange={(e) => setNewCollection({...newCollection, description: e.target.value})}
                    placeholder="Collection description"
                    className="bg-white/10 border-white/20 text-white text-sm min-h-[60px]"
                    data-testid="collection-desc-input"
                  />
                </div>
                <div>
                  <Label className="text-white mb-2 block text-sm">Environment Variables</Label>
                  {envVars.map((ev, idx) => (
                    <div key={idx} className="flex gap-2 mb-2">
                      <Input
                        value={ev.key}
                        onChange={(e) => {
                          const newEnvVars = [...envVars];
                          newEnvVars[idx].key = e.target.value;
                          setEnvVars(newEnvVars);
                        }}
                        placeholder="KEY"
                        className="bg-white/10 border-white/20 text-white h-9 text-sm"
                      />
                      <Input
                        value={ev.value}
                        onChange={(e) => {
                          const newEnvVars = [...envVars];
                          newEnvVars[idx].value = e.target.value;
                          setEnvVars(newEnvVars);
                        }}
                        placeholder="value"
                        className="bg-white/10 border-white/20 text-white h-9 text-sm"
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setEnvVars(envVars.filter((_, i) => i !== idx))}
                        className="text-red-400 h-9 w-9 p-0"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setEnvVars([...envVars, { key: '', value: '' }])}
                    className="w-full border-white/20 text-white h-9 text-sm"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Variable
                  </Button>
                </div>
                <Button onClick={createCollection} className="w-full bg-gradient-to-r from-indigo-500 to-purple-500 h-9 text-sm sm:text-base" data-testid="save-collection-btn">
                  Create Collection
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <ScrollArea className="flex-1 p-3 sm:p-4">
          <div className="space-y-2">
            {collections.map(collection => (
              <div
                key={collection.id}
                className={`group flex items-center justify-between p-2 sm:p-3 rounded-lg cursor-pointer transition-all ${
                  collection.id === selectedCollection ? 'bg-white/20' : 'bg-white/5 hover:bg-white/10'
                }`}
                onClick={() => {
                  setSelectedCollection(collection.id);
                  setMobileView('requests'); // Auto-navigate on mobile
                }}
                data-testid={`collection-${collection.id}`}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-semibold truncate">{collection.name}</p>
                  {collection.description && (
                    <p className="text-slate-400 text-xs truncate">{collection.description}</p>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="opacity-0 group-hover:opacity-100 text-red-400 hover:bg-red-500/20 h-8 w-8 p-0"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteCollection(collection.id);
                  }}
                  data-testid={`delete-collection-${collection.id}`}
                >
                  <Trash2 className="w-3 h-3 sm:w-4 sm:h-4" />
                </Button>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Requests List - Responsive */}
      <div className={`
        ${mobileView === 'requests' ? 'flex' : 'hidden'} lg:flex
        relative lg:w-80 w-full backdrop-blur-xl bg-white/5 lg:border-r border-white/10 flex-col
      `}>
        <div className="p-4 sm:p-6 border-b border-white/10">
          <h2 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Requests</h2>
          {selectedCollection && (
            <Dialog open={showRequestDialog} onOpenChange={setShowRequestDialog}>
              <DialogTrigger asChild>
                <Button className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 h-9 text-sm sm:text-base" data-testid="new-request-btn">
                  <Plus className="w-4 h-4 mr-2" />
                  New Request
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-slate-900 border-white/10 max-w-[95vw] sm:max-w-2xl">
                <DialogHeader>
                  <DialogTitle className="text-white text-lg sm:text-xl">Create Request</DialogTitle>
                </DialogHeader>
                <div className="space-y-3 sm:space-y-4 mt-4 max-h-[60vh] overflow-y-auto">
                  <div>
                    <Label className="text-white mb-2 block text-sm">Name</Label>
                    <Input
                      value={newRequest.name}
                      onChange={(e) => setNewRequest({...newRequest, name: e.target.value})}
                      className="bg-white/10 border-white/20 text-white h-9 text-sm"
                      data-testid="request-name-input"
                    />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                    <div>
                      <Label className="text-white mb-2 block text-sm">Method</Label>
                      <Select value={newRequest.method} onValueChange={(v) => setNewRequest({...newRequest, method: v})}>
                        <SelectTrigger className="bg-white/10 border-white/20 text-white h-9 text-sm">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {HTTP_METHODS.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label className="text-white mb-2 block text-sm">Type</Label>
                      <Select value={newRequest.request_type} onValueChange={(v) => setNewRequest({...newRequest, request_type: v})}>
                        <SelectTrigger className="bg-white/10 border-white/20 text-white h-9 text-sm">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {REQUEST_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div>
                    <Label className="text-white mb-2 block text-sm">URL</Label>
                    <Input
                      value={newRequest.url}
                      onChange={(e) => setNewRequest({...newRequest, url: e.target.value})}
                      placeholder="https://api.example.com/endpoint"
                      className="bg-white/10 border-white/20 text-white h-9 text-sm"
                      data-testid="request-url-input"
                    />
                  </div>
                  <Button onClick={createRequest} className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 h-9 text-sm sm:text-base" data-testid="save-request-btn">
                    Create Request
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          )}
        </div>

        <ScrollArea className="flex-1 p-3 sm:p-4">
          {!selectedCollection ? (
            <p className="text-slate-400 text-center py-8 text-sm">Select a collection</p>
          ) : (
            <div className="space-y-2">
              {requests.map(req => (
                <div
                  key={req.id}
                  className={`group flex items-center justify-between p-2 sm:p-3 rounded-lg cursor-pointer transition-all ${
                    req.id === selectedRequest?.id ? 'bg-white/20' : 'bg-white/5 hover:bg-white/10'
                  }`}
                  onClick={() => {
                    setSelectedRequest(req);
                    setMobileView('details'); // Auto-navigate on mobile
                  }}
                  data-testid={`request-${req.id}`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        req.method === 'GET' ? 'bg-green-500/20 text-green-400' :
                        req.method === 'POST' ? 'bg-blue-500/20 text-blue-400' :
                        req.method === 'PUT' ? 'bg-yellow-500/20 text-yellow-400' :
                        req.method === 'DELETE' ? 'bg-red-500/20 text-red-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {req.method}
                      </span>
                      <p className="text-white text-sm truncate">{req.name}</p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="opacity-0 group-hover:opacity-100 text-red-400 hover:bg-red-500/20 h-8 w-8 p-0"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteRequest(req.id);
                    }}
                    data-testid={`delete-request-${req.id}`}
                  >
                    <Trash2 className="w-3 h-3 sm:w-4 sm:h-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </div>

      {/* Request Details & Response - Responsive */}
      <div className={`
        ${mobileView === 'details' ? 'flex' : 'hidden'} lg:flex
        relative flex-1 flex-col w-full
      `}>
        {!selectedRequest ? (
          <div className="flex-1 flex items-center justify-center p-4">
            <p className="text-slate-400 text-base sm:text-lg text-center">Select a request to test</p>
          </div>
        ) : (
          <>
            <div className="backdrop-blur-xl bg-white/5 border-b border-white/10 p-3 sm:p-4 lg:p-6">
              <div className="flex items-center justify-between mb-3 sm:mb-4 gap-2">
                <h1 className="text-lg sm:text-xl lg:text-2xl font-bold text-white truncate flex-1">{selectedRequest.name}</h1>
                <div className="flex gap-1 sm:gap-2 flex-shrink-0">
                  <Button
                    variant="outline"
                    onClick={() => generateCode('javascript')}
                    className="border-white/20 text-white hover:bg-white/10 h-8 w-8 sm:h-9 sm:w-auto sm:px-3 p-0"
                    data-testid="generate-code-btn"
                  >
                    <Code2 className="w-4 h-4 sm:mr-2" />
                    <span className="hidden sm:inline">Code</span>
                  </Button>
                  <Button
                    onClick={executeRequest}
                    disabled={loading}
                    className="bg-gradient-to-r from-green-500 to-emerald-500 h-8 sm:h-9 text-xs sm:text-sm px-2 sm:px-4"
                    data-testid="execute-request-btn"
                  >
                    <Play className="w-4 h-4 sm:mr-2" />
                    <span className="hidden sm:inline">{loading ? 'Sending...' : 'Send'}</span>
                  </Button>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-2">
                <span className="px-2 sm:px-3 py-1 rounded bg-indigo-500/20 text-indigo-400 text-xs sm:text-sm font-bold w-fit">
                  {selectedRequest.method}
                </span>
                <div className="flex-1 px-2 sm:px-3 py-1 rounded bg-white/10 text-white text-xs sm:text-sm font-mono overflow-x-auto">
                  {selectedRequest.url}
                </div>
              </div>
            </div>

            <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
              <div className="flex-1 p-3 sm:p-4 lg:p-6 overflow-auto">
                <Card className="bg-white/5 backdrop-blur-xl border-white/10 h-full">
                  <CardHeader className="p-3 sm:p-4 lg:p-6">
                    <CardTitle className="text-white text-base sm:text-lg">Request</CardTitle>
                  </CardHeader>
                  <CardContent className="p-3 sm:p-4 lg:p-6 pt-0">
                    <Tabs defaultValue="headers">
                      <TabsList className="bg-white/5 h-8 sm:h-9">
                        <TabsTrigger value="headers" className="text-xs sm:text-sm">Headers</TabsTrigger>
                        <TabsTrigger value="body" className="text-xs sm:text-sm">Body</TabsTrigger>
                      </TabsList>
                      <TabsContent value="headers" className="mt-3 sm:mt-4">
                        <ScrollArea className="h-48 sm:h-64">
                          {selectedRequest.headers && Object.keys(selectedRequest.headers).length > 0 ? (
                            <div className="space-y-2">
                              {Object.entries(selectedRequest.headers).map(([key, value]) => (
                                <div key={key} className="p-2 rounded bg-white/5 break-all">
                                  <span className="text-cyan-400 font-mono text-xs sm:text-sm">{key}:</span>
                                  <span className="text-white ml-2 font-mono text-xs sm:text-sm">{value}</span>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-slate-400 text-xs sm:text-sm">No headers</p>
                          )}
                        </ScrollArea>
                      </TabsContent>
                      <TabsContent value="body" className="mt-3 sm:mt-4">
                        <Textarea
                          value={selectedRequest.body || ''}
                          readOnly
                          className="bg-white/10 border-white/20 text-white font-mono h-48 sm:h-64 text-xs sm:text-sm"
                          placeholder="No body"
                        />
                      </TabsContent>
                    </Tabs>
                  </CardContent>
                </Card>
              </div>

              <div className="flex-1 p-3 sm:p-4 lg:p-6 overflow-auto">
                <Card className="bg-white/5 backdrop-blur-xl border-white/10 h-full">
                  <CardHeader className="p-3 sm:p-4 lg:p-6">
                    <CardTitle className="text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-base sm:text-lg">
                      <span>Response</span>
                      {response && (
                        <span className={`text-xs sm:text-sm px-2 sm:px-3 py-1 rounded w-fit ${
                          response.status >= 200 && response.status < 300 ? 'bg-green-500/20 text-green-400' :
                          response.status >= 400 ? 'bg-red-500/20 text-red-400' :
                          'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {response.status} {response.statusText}
                        </span>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-3 sm:p-4 lg:p-6 pt-0">
                    {!response ? (
                      <p className="text-slate-400 text-xs sm:text-sm">No response yet</p>
                    ) : response.error ? (
                      <div className="p-3 sm:p-4 rounded bg-red-500/10 border border-red-500/20">
                        <p className="text-red-400 font-mono text-xs sm:text-sm break-all">{response.error}</p>
                      </div>
                    ) : (
                      <div>
                        <div className="mb-3 sm:mb-4 flex flex-col sm:flex-row gap-2 sm:gap-4 text-xs sm:text-sm">
                          <span className="text-slate-400">Time: <span className="text-white font-mono">{response.responseTime}ms</span></span>
                          <span className="text-slate-400">Size: <span className="text-white font-mono">{response.size} bytes</span></span>
                        </div>
                        <ScrollArea className="h-64 sm:h-80 lg:h-96">
                          <pre className="p-3 sm:p-4 rounded bg-slate-950/50 overflow-x-auto">
                            <code className="text-xs sm:text-sm text-white font-mono">
                              {typeof response.body === 'object' ? JSON.stringify(response.body, null, 2) : response.body}
                            </code>
                          </pre>
                        </ScrollArea>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Code Generation Dialog - Responsive */}
      <Dialog open={showCodeDialog} onOpenChange={setShowCodeDialog}>
        <DialogContent className="bg-slate-900 border-white/10 max-w-[95vw] sm:max-w-4xl max-h-[90vh]">
          <DialogHeader>
            <DialogTitle className="text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-base sm:text-lg">
              <span>Generated Code</span>
              <div className="flex gap-2 w-full sm:w-auto">
                <Select value={codeLanguage} onValueChange={generateCode}>
                  <SelectTrigger className="flex-1 sm:w-40 bg-white/10 border-white/20 text-white h-8 sm:h-9 text-xs sm:text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="javascript">JavaScript</SelectItem>
                    <SelectItem value="python">Python</SelectItem>
                    <SelectItem value="curl">cURL</SelectItem>
                    <SelectItem value="csharp">C#</SelectItem>
                    <SelectItem value="powershell">PowerShell</SelectItem>
                  </SelectContent>
                </Select>
                <Button onClick={copyCode} variant="outline" className="border-white/20 text-white h-8 w-8 sm:h-9 sm:w-9 p-0">
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
            </DialogTitle>
          </DialogHeader>
          <ScrollArea className="h-64 sm:h-80 lg:h-96 mt-4">
            <pre className="p-3 sm:p-4 rounded bg-slate-950/50">
              <code className={`text-xs sm:text-sm language-${codeLanguage === 'csharp' ? 'clike' : codeLanguage}`}>
                {generatedCode}
              </code>
            </pre>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default APITesting;
