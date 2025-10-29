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
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from 'sonner';
import { 
  Plus, Trash2, Play, FolderPlus, Copy, Code2, Settings, 
  Check, X, ChevronDown, Sparkles, Variable 
} from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-csharp';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HTTP_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'];
const REQUEST_TYPES = ['REST', 'GraphQL', 'SOAP', 'WebSocket'];
const BODY_TYPES = ['none', 'json', 'raw', 'form-data', 'xml'];
const COMMON_HEADERS = [
  'Content-Type', 'Authorization', 'Accept', 'User-Agent', 
  'Cache-Control', 'X-API-Key', 'Accept-Encoding'
];

function APITestingEnhanced() {
  // Collections & Requests
  const [collections, setCollections] = useState([]);
  const [requests, setRequests] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [selectedRequest, setSelectedRequest] = useState(null);
  
  // Dialogs
  const [showCollectionDialog, setShowCollectionDialog] = useState(false);
  const [showRequestDialog, setShowRequestDialog] = useState(false);
  const [showCodeDialog, setShowCodeDialog] = useState(false);
  const [showVariablesDialog, setShowVariablesDialog] = useState(false);
  
  // Mobile state
  const [mobileView, setMobileView] = useState('collections');
  
  // Environment Variables
  const [environmentVars, setEnvironmentVars] = useState([{ key: '', value: '', enabled: true }]);
  
  // Request Configuration
  const [requestConfig, setRequestConfig] = useState({
    method: 'GET',
    url: 'https://api.example.com/endpoint',
  });
  
  // Query Parameters
  const [queryParams, setQueryParams] = useState([{ key: '', value: '', enabled: true }]);
  
  // Headers
  const [headers, setHeaders] = useState([{ key: '', value: '', enabled: true }]);
  
  // Body
  const [bodyType, setBodyType] = useState('none');
  const [jsonBody, setJsonBody] = useState('{\n  \n}');
  const [rawBody, setRawBody] = useState('');
  const [formDataBody, setFormDataBody] = useState([{ key: '', value: '', enabled: true }]);
  const [xmlBody, setXmlBody] = useState('<?xml version="1.0"?>\n<root>\n  \n</root>');
  
  // Response
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Code Generation
  const [generatedCode, setGeneratedCode] = useState('');
  const [codeLanguage, setCodeLanguage] = useState('javascript');
  
  // AI Features State
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState('');
  const [aiFeature, setAiFeature] = useState('request-builder'); // current AI feature
  const [aiInput, setAiInput] = useState('');
  const [selectedAIProvider, setSelectedAIProvider] = useState(null);
  const [providers, setProviders] = useState([]);
  
  // Collection & Request forms
  const [newCollection, setNewCollection] = useState({ name: '', description: '' });
  const [newRequest, setNewRequest] = useState({ name: '', method: 'GET', url: '', request_type: 'REST' });

  useEffect(() => {
    loadCollections();
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      const res = await axios.get(`${API}/providers`);
      setProviders(res.data);
      if (res.data.length > 0 && !selectedAIProvider) {
        setSelectedAIProvider(res.data[0].id);
      }
    } catch (error) {
      console.error('Failed to load providers:', error);
    }
  };

  useEffect(() => {
    if (selectedCollection) {
      loadRequests(selectedCollection);
      loadEnvironmentVars(selectedCollection);
    }
  }, [selectedCollection]);

  useEffect(() => {
    if (selectedRequest) {
      populateRequestData(selectedRequest);
    }
  }, [selectedRequest]);

  useEffect(() => {
    if (generatedCode) {
      Prism.highlightAll();
    }
  }, [generatedCode, codeLanguage]);

  // ============= VARIABLE REPLACEMENT =============
  const replaceVariables = (str) => {
    if (!str || typeof str !== 'string') return str;
    
    let result = str;
    environmentVars.forEach(variable => {
      if (variable.enabled && variable.key && variable.value) {
        const regex = new RegExp(`\\{\\{${variable.key}\\}\\}`, 'g');
        result = result.replace(regex, variable.value);
      }
    });
    return result;
  };

  // ============= URL & QUERY PARAMS =============
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

  const buildURLWithParams = (baseUrl, params) => {
    try {
      const urlObj = new URL(baseUrl.split('?')[0]);
      
      params.forEach(param => {
        if (param.enabled && param.key) {
          urlObj.searchParams.append(param.key, replaceVariables(param.value || ''));
        }
      });
      
      return urlObj.toString();
    } catch {
      return baseUrl;
    }
  };

  const syncURLWithParams = () => {
    const newUrl = buildURLWithParams(requestConfig.url, queryParams);
    setRequestConfig({ ...requestConfig, url: newUrl });
  };

  // ============= API CALLS =============
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

  const loadEnvironmentVars = (collectionId) => {
    const collection = collections.find(c => c.id === collectionId);
    if (collection && collection.environment_vars) {
      const vars = Object.entries(collection.environment_vars).map(([key, value]) => ({
        key, value, enabled: true
      }));
      setEnvironmentVars(vars.length > 0 ? vars : [{ key: '', value: '', enabled: true }]);
    }
  };

  const createCollection = async () => {
    try {
      const envVarsObj = {};
      environmentVars.forEach(ev => {
        if (ev.key && ev.value) {
          envVarsObj[ev.key] = ev.value;
        }
      });
      
      await axios.post(`${API}/api-collections`, {
        ...newCollection,
        environment_vars: envVarsObj
      });
      
      toast.success('Collection created');
      setShowCollectionDialog(false);
      setNewCollection({ name: '', description: '' });
      loadCollections();
    } catch (error) {
      toast.error('Failed to create collection');
    }
  };

  const createRequest = async () => {
    try {
      await axios.post(`${API}/api-requests`, {
        ...newRequest,
        collection_id: selectedCollection
      });
      
      toast.success('Request created');
      setShowRequestDialog(false);
      setNewRequest({ name: '', method: 'GET', url: '', request_type: 'REST' });
      loadRequests(selectedCollection);
    } catch (error) {
      toast.error('Failed to create request');
    }
  };

  const deleteCollection = async (id) => {
    try {
      await axios.delete(`${API}/api-collections/${id}`);
      toast.success('Collection deleted');
      loadCollections();
      if (selectedCollection === id) {
        setSelectedCollection(null);
        setSelectedRequest(null);
      }
    } catch (error) {
      toast.error('Failed to delete collection');
    }
  };

  const deleteRequest = async (id) => {
    try {
      await axios.delete(`${API}/api-requests/${id}`);
      toast.success('Request deleted');
      loadRequests(selectedCollection);
      if (selectedRequest?.id === id) {
        setSelectedRequest(null);
      }
    } catch (error) {
      toast.error('Failed to delete request');
    }
  };

  // ============= POPULATE REQUEST DATA =============
  const populateRequestData = (request) => {
    setRequestConfig({
      method: request.method || 'GET',
      url: request.url || ''
    });

    // Parse query params
    const params = parseQueryParamsFromURL(request.url || '');
    setQueryParams(params);

    // Parse headers
    if (request.headers && typeof request.headers === 'object') {
      const headersList = Object.entries(request.headers).map(([key, value]) => ({
        key, value, enabled: true
      }));
      setHeaders(headersList.length > 0 ? headersList : [{ key: '', value: '', enabled: true }]);
    }

    // Parse body
    if (request.body) {
      try {
        const parsed = JSON.parse(request.body);
        setBodyType('json');
        setJsonBody(JSON.stringify(parsed, null, 2));
      } catch {
        setBodyType('raw');
        setRawBody(request.body);
      }
    } else {
      setBodyType('none');
    }
  };

  // ============= EXECUTE REQUEST =============
  const executeRequest = async () => {
    setLoading(true);
    const startTime = Date.now();

    try {
      // Build final URL with variables replaced
      const finalUrl = replaceVariables(buildURLWithParams(requestConfig.url, queryParams));

      // Build headers object
      const headersObj = {};
      headers.forEach(h => {
        if (h.enabled && h.key) {
          headersObj[h.key] = replaceVariables(h.value);
        }
      });

      // Build body based on type
      let bodyData = null;
      if (requestConfig.method !== 'GET' && requestConfig.method !== 'HEAD') {
        if (bodyType === 'json') {
          bodyData = replaceVariables(jsonBody);
          headersObj['Content-Type'] = headersObj['Content-Type'] || 'application/json';
        } else if (bodyType === 'raw') {
          bodyData = replaceVariables(rawBody);
        } else if (bodyType === 'form-data') {
          const formData = new FormData();
          formDataBody.forEach(item => {
            if (item.enabled && item.key) {
              formData.append(item.key, replaceVariables(item.value));
            }
          });
          bodyData = formData;
        } else if (bodyType === 'xml') {
          bodyData = replaceVariables(xmlBody);
          headersObj['Content-Type'] = headersObj['Content-Type'] || 'application/xml';
        }
      }

      const config = {
        method: requestConfig.method,
        url: finalUrl,
        headers: headersObj,
        ...(bodyData && { data: bodyData })
      };

      const res = await axios(config);
      const responseTime = Date.now() - startTime;

      setResponse({
        status: res.status,
        statusText: res.statusText,
        headers: res.headers,
        body: res.data,
        responseTime,
        size: JSON.stringify(res.data).length
      });

      toast.success('Request successful');
    } catch (error) {
      const responseTime = Date.now() - startTime;
      setResponse({
        status: error.response?.status || 0,
        statusText: error.response?.statusText || 'Error',
        body: error.response?.data || { error: error.message },
        responseTime,
        error: error.message
      });
      toast.error('Request failed');
    } finally {
      setLoading(false);
    }
  };

  // ============= CODE GENERATION =============
  const generateCode = (language) => {
    setCodeLanguage(language);
    
    const url = replaceVariables(buildURLWithParams(requestConfig.url, queryParams));
    const method = requestConfig.method;
    
    const headersObj = {};
    headers.forEach(h => {
      if (h.enabled && h.key) {
        headersObj[h.key] = replaceVariables(h.value);
      }
    });

    let body = '';
    if (bodyType === 'json') body = jsonBody;
    else if (bodyType === 'raw') body = rawBody;
    else if (bodyType === 'xml') body = xmlBody;

    let code = '';

    if (language === 'javascript') {
      code = `const response = await fetch('${url}', {
  method: '${method}',
  headers: ${JSON.stringify(headersObj, null, 2)},${body ? `\n  body: ${body.includes('{') ? body : `'${body}'`}` : ''}
});

const data = await response.json();
console.log(data);`;
    } else if (language === 'python') {
      code = `import requests

response = requests.${method.toLowerCase()}(
    '${url}',
    headers=${JSON.stringify(headersObj, null, 4).replace(/"/g, "'")}${body ? `,\n    data='${body}'` : ''}
)

print(response.json())`;
    } else if (language === 'curl') {
      code = `curl -X ${method} '${url}' \\`;
      Object.entries(headersObj).forEach(([key, value]) => {
        code += `\n  -H '${key}: ${value}' \\`;
      });
      if (body) {
        code += `\n  -d '${body.replace(/'/g, "'\\''")}' \\`;
      }
      code = code.slice(0, -2); // Remove trailing backslash
    } else if (language === 'csharp') {
      code = `using System.Net.Http;
using System.Text;

var client = new HttpClient();
${Object.entries(headersObj).map(([k, v]) => `client.DefaultRequestHeaders.Add("${k}", "${v}");`).join('\n')}

${body ? `var content = new StringContent(${body.includes('{') ? `@"${body}"` : `"${body}"`}, Encoding.UTF8, "application/json");
var response = await client.${method === 'POST' ? 'PostAsync' : method === 'PUT' ? 'PutAsync' : 'SendAsync'}("${url}", content);` : `var response = await client.GetAsync("${url}");`}

var result = await response.Content.ReadAsStringAsync();
Console.WriteLine(result);`;
    }

    setGeneratedCode(code);
    setShowCodeDialog(true);
  };

  const copyCode = async () => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(generatedCode);
        toast.success('Code copied to clipboard');
      } else {
        const textArea = document.createElement('textarea');
        textArea.value = generatedCode;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
          document.execCommand('copy');
          toast.success('Code copied to clipboard');
        } catch {
          toast.info('Please copy manually');
        } finally {
          document.body.removeChild(textArea);
        }
      }
    } catch {
      toast.error('Failed to copy code');
    }
  };

  // ============= AI FEATURES =============
  
  const callAIFeature = async (feature, inputData) => {
    if (!selectedAIProvider) {
      toast.error('Please select an AI provider first');
      return;
    }

    setAiLoading(true);
    setAiResponse('');
    
    try {
      const endpoint = {
        'request-builder': '/ai/build-request',
        'analyze-response': '/ai/analyze-response',
        'security-analysis': '/ai/analyze-response',
        'test-data': '/ai/generate-test-data',
        'from-docs': '/ai/parse-documentation',
        'explain': '/ai/analyze-response',
        'assertions': '/ai/generate-assertions',
        'generate-code': '/ai/build-request'
      }[feature];

      const requestBody = feature === 'request-builder' || feature === 'generate-code' 
        ? { description: inputData, provider_id: selectedAIProvider }
        : feature === 'from-docs'
        ? { documentation: inputData, provider_id: selectedAIProvider }
        : feature === 'test-data'
        ? { 
            endpoint: requestConfig.url, 
            method: requestConfig.method, 
            description: inputData,
            provider_id: selectedAIProvider 
          }
        : {
            request: {
              method: requestConfig.method,
              url: requestConfig.url,
              headers: headersArrayToObject(headers),
              body: bodyType === 'json' ? jsonBody : bodyType === 'raw' ? rawBody : xmlBody
            },
            response: response || { status: 0, body: {} },
            provider_id: selectedAIProvider,
            analysis_type: feature === 'security-analysis' ? 'security' : feature === 'explain' ? 'explain' : 'response'
          };

      const res = await fetch(`${API}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            
            if (data.type === 'chunk') {
              fullResponse += data.content;
              setAiResponse(fullResponse);
            } else if (data.type === 'complete' && data.data) {
              // Handle structured data response
              applyAISuggestion(feature, data.data);
            } else if (data.type === 'error') {
              toast.error(data.message);
            }
          } catch (e) {
            console.error('Parse error:', e);
          }
        }
      }

      if (fullResponse) {
        setAiResponse(fullResponse);
      }
      
      toast.success('AI analysis complete');
    } catch (error) {
      console.error('AI feature error:', error);
      toast.error('AI feature failed');
    } finally {
      setAiLoading(false);
    }
  };

  const applyAISuggestion = (feature, data) => {
    if (feature === 'request-builder' || feature === 'from-docs') {
      // Apply the generated request configuration
      if (data.method) setRequestConfig({ ...requestConfig, method: data.method });
      if (data.url) setRequestConfig({ ...requestConfig, url: data.url });
      
      if (data.headers) {
        const headersList = Object.entries(data.headers).map(([key, value]) => ({
          key, value, enabled: true
        }));
        setHeaders(headersList);
      }
      
      if (data.queryParams && Array.isArray(data.queryParams)) {
        setQueryParams(data.queryParams.map(p => ({ ...p, enabled: true })));
      }
      
      if (data.bodyType) setBodyType(data.bodyType);
      if (data.body) {
        if (data.bodyType === 'json') setJsonBody(typeof data.body === 'string' ? data.body : JSON.stringify(data.body, null, 2));
        else if (data.bodyType === 'raw') setRawBody(data.body);
        else if (data.bodyType === 'xml') setXmlBody(data.body);
      }
      
      toast.success('Request configuration applied!');
    } else if (feature === 'test-data' && Array.isArray(data)) {
      // Show test data in AI response
      setAiResponse(JSON.stringify(data, null, 2));
    }
  };

  const headersArrayToObject = (headersArr) => {
    const obj = {};
    headersArr.forEach(h => {
      if (h.enabled && h.key) obj[h.key] = h.value;
    });
    return obj;
  };

  // ============= AUTO-SUGGEST HEADERS =============
  const autoSuggestHeader = (bodyType, method) => {
    const suggestions = [];
    
    if (method !== 'GET' && method !== 'HEAD') {
      if (bodyType === 'json') {
        suggestions.push({ key: 'Content-Type', value: 'application/json', enabled: true });
      } else if (bodyType === 'xml') {
        suggestions.push({ key: 'Content-Type', value: 'application/xml', enabled: true });
      } else if (bodyType === 'form-data') {
        suggestions.push({ key: 'Content-Type', value: 'multipart/form-data', enabled: true });
      }
    }
    
    return suggestions;
  };

  useEffect(() => {
    // Auto-add Content-Type header when body type changes
    if (bodyType !== 'none') {
      const suggestions = autoSuggestHeader(bodyType, requestConfig.method);
      const hasContentType = headers.some(h => h.key.toLowerCase() === 'content-type');
      
      if (!hasContentType && suggestions.length > 0) {
        setHeaders([...headers.filter(h => h.key), ...suggestions]);
      }
    }
  }, [bodyType]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex flex-col lg:flex-row">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-900/20 via-transparent to-transparent pointer-events-none" />
      
      {/* Mobile Header */}
      <div className="lg:hidden relative backdrop-blur-xl bg-white/5 border-b border-white/10 p-3 flex items-center justify-between z-10">
        <Link to="/" className="flex items-center gap-2">
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
            variant={mobileView === 'test' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setMobileView('test')}
            className={`text-xs ${mobileView === 'test' ? 'bg-green-500' : 'text-white'}`}
            disabled={!selectedRequest}
          >
            Test
          </Button>
        </div>
      </div>

      {/* Collections Sidebar */}
      <div className={`
        ${mobileView === 'collections' ? 'flex' : 'hidden'} lg:flex
        relative lg:w-80 w-full backdrop-blur-xl bg-white/5 lg:border-r border-white/10 flex-col
      `}>
        <div className="p-4 sm:p-6 border-b border-white/10">
          <Link to="/" className="hidden lg:flex items-center gap-3 mb-4 hover:opacity-80 transition-opacity">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
              <Code2 className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-xl font-bold text-white">API Tester</h2>
          </Link>
          
          <h3 className="text-lg font-bold text-white mb-3 lg:hidden">Collections</h3>

          <Dialog open={showCollectionDialog} onOpenChange={setShowCollectionDialog}>
            <DialogTrigger asChild>
              <Button className="w-full bg-gradient-to-r from-indigo-500 to-purple-500 h-9 text-sm">
                <FolderPlus className="w-4 h-4 mr-2" />
                New Collection
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-slate-900 border-white/10 max-w-[95vw] sm:max-w-lg">
              <DialogHeader>
                <DialogTitle className="text-white">Create Collection</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <Label className="text-white mb-2 block">Name</Label>
                  <Input
                    value={newCollection.name}
                    onChange={(e) => setNewCollection({...newCollection, name: e.target.value})}
                    placeholder="My API Collection"
                    className="bg-white/10 border-white/20 text-white"
                  />
                </div>
                <div>
                  <Label className="text-white mb-2 block">Description</Label>
                  <Textarea
                    value={newCollection.description}
                    onChange={(e) => setNewCollection({...newCollection, description: e.target.value})}
                    className="bg-white/10 border-white/20 text-white"
                  />
                </div>
                <Button onClick={createCollection} className="w-full bg-gradient-to-r from-indigo-500 to-purple-500">
                  Create
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
                className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all ${
                  collection.id === selectedCollection ? 'bg-white/20' : 'bg-white/5 hover:bg-white/10'
                }`}
                onClick={() => {
                  setSelectedCollection(collection.id);
                  setMobileView('requests');
                }}
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
                  className="opacity-0 group-hover:opacity-100 text-red-400 h-8 w-8 p-0"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteCollection(collection.id);
                  }}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Requests List */}
      <div className={`
        ${mobileView === 'requests' ? 'flex' : 'hidden'} lg:flex
        relative lg:w-80 w-full backdrop-blur-xl bg-white/5 lg:border-r border-white/10 flex-col
      `}>
        <div className="p-4 sm:p-6 border-b border-white/10 flex items-center justify-between">
          <h3 className="text-lg font-bold text-white">Requests</h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowVariablesDialog(true)}
            className="text-white hover:bg-white/10 h-8 w-8 p-0"
            title="Environment Variables"
          >
            <Variable className="w-4 h-4" />
          </Button>
        </div>

        {!selectedCollection ? (
          <div className="flex-1 flex items-center justify-center p-8">
            <p className="text-slate-400 text-center text-sm">Select a collection first</p>
          </div>
        ) : (
          <>
            <div className="p-3 sm:p-4 border-b border-white/10">
              <Dialog open={showRequestDialog} onOpenChange={setShowRequestDialog}>
                <DialogTrigger asChild>
                  <Button className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 h-9 text-sm">
                    <Plus className="w-4 h-4 mr-2" />
                    New Request
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-slate-900 border-white/10 max-w-[95vw] sm:max-w-xl">
                  <DialogHeader>
                    <DialogTitle className="text-white">Create Request</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 mt-4">
                    <div>
                      <Label className="text-white mb-2 block">Name</Label>
                      <Input
                        value={newRequest.name}
                        onChange={(e) => setNewRequest({...newRequest, name: e.target.value})}
                        className="bg-white/10 border-white/20 text-white"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-white mb-2 block">Method</Label>
                        <Select value={newRequest.method} onValueChange={(v) => setNewRequest({...newRequest, method: v})}>
                          <SelectTrigger className="bg-white/10 border-white/20 text-white">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {HTTP_METHODS.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label className="text-white mb-2 block">Type</Label>
                        <Select value={newRequest.request_type} onValueChange={(v) => setNewRequest({...newRequest, request_type: v})}>
                          <SelectTrigger className="bg-white/10 border-white/20 text-white">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {REQUEST_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div>
                      <Label className="text-white mb-2 block">URL</Label>
                      <Input
                        value={newRequest.url}
                        onChange={(e) => setNewRequest({...newRequest, url: e.target.value})}
                        placeholder="https://api.example.com/endpoint"
                        className="bg-white/10 border-white/20 text-white"
                      />
                    </div>
                    <Button onClick={createRequest} className="w-full bg-gradient-to-r from-blue-500 to-cyan-500">
                      Create
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            <ScrollArea className="flex-1 p-3 sm:p-4">
              <div className="space-y-2">
                {requests.map(req => (
                  <div
                    key={req.id}
                    className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all ${
                      req.id === selectedRequest?.id ? 'bg-white/20' : 'bg-white/5 hover:bg-white/10'
                    }`}
                    onClick={() => {
                      setSelectedRequest(req);
                      setMobileView('test');
                    }}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
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
                      <p className="text-slate-400 text-xs truncate">{req.url}</p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="opacity-0 group-hover:opacity-100 text-red-400 h-8 w-8 p-0"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteRequest(req.id);
                      }}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </>
        )}
      </div>

      {/* Test Area - Request & Response */}
      <div className={`
        ${mobileView === 'test' ? 'flex' : 'hidden'} lg:flex
        relative flex-1 flex-col w-full overflow-hidden
      `}>
        {!selectedRequest ? (
          <div className="flex-1 flex items-center justify-center p-4">
            <p className="text-slate-400 text-lg text-center">Select a request to test</p>
          </div>
        ) : (
          <>
            {/* Request Header */}
            <div className="backdrop-blur-xl bg-white/5 border-b border-white/10 p-3 sm:p-4 lg:p-6">
              <div className="flex items-center justify-between mb-3 gap-2">
                <h1 className="text-lg sm:text-xl lg:text-2xl font-bold text-white truncate flex-1">
                  {selectedRequest.name}
                </h1>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => generateCode('javascript')}
                    className="border-white/20 text-white h-9 px-3 text-sm"
                  >
                    <Code2 className="w-4 h-4 sm:mr-2" />
                    <span className="hidden sm:inline">Code</span>
                  </Button>
                  <Button
                    onClick={executeRequest}
                    disabled={loading}
                    className="bg-gradient-to-r from-green-500 to-emerald-500 h-9 px-4 text-sm"
                  >
                    <Play className="w-4 h-4 sm:mr-2" />
                    <span className="hidden sm:inline">{loading ? 'Sending...' : 'Send'}</span>
                  </Button>
                </div>
              </div>

              {/* Method & URL */}
              <div className="flex flex-col sm:flex-row gap-2">
                <Select 
                  value={requestConfig.method} 
                  onValueChange={(v) => setRequestConfig({...requestConfig, method: v})}
                >
                  <SelectTrigger className="w-full sm:w-32 bg-white/10 border-white/20 text-white h-10">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {HTTP_METHODS.map(m => (
                      <SelectItem key={m} value={m}>
                        <span className={`font-bold ${
                          m === 'GET' ? 'text-green-400' :
                          m === 'POST' ? 'text-blue-400' :
                          m === 'PUT' ? 'text-yellow-400' :
                          m === 'DELETE' ? 'text-red-400' : 'text-gray-400'
                        }`}>{m}</span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                <Input
                  value={requestConfig.url}
                  onChange={(e) => setRequestConfig({...requestConfig, url: e.target.value})}
                  onBlur={() => setQueryParams(parseQueryParamsFromURL(requestConfig.url))}
                  placeholder="https://api.example.com/endpoint"
                  className="flex-1 bg-white/10 border-white/20 text-white font-mono text-sm h-10"
                />
              </div>
            </div>

            {/* Request Configuration Tabs */}
            <div className="flex-1 overflow-auto p-3 sm:p-4 lg:p-6">
              <Card className="bg-white/5 backdrop-blur-xl border-white/10 mb-4">
                <CardHeader className="p-4 sm:p-6">
                  <CardTitle className="text-white">Request Configuration</CardTitle>
                </CardHeader>
                <CardContent className="p-4 sm:p-6 pt-0">
                  <Tabs defaultValue="params" className="w-full">
                    <TabsList className="bg-white/5 grid w-full grid-cols-4">
                      <TabsTrigger value="params">Params</TabsTrigger>
                      <TabsTrigger value="headers">Headers</TabsTrigger>
                      <TabsTrigger value="body">Body</TabsTrigger>
                      <TabsTrigger value="ai" className="gap-1">
                        <Sparkles className="w-4 h-4" />
                        AI
                      </TabsTrigger>
                    </TabsList>

                    {/* Query Parameters Tab */}
                    <TabsContent value="params" className="mt-4">
                      <div className="space-y-2">
                        {queryParams.map((param, idx) => (
                          <div key={idx} className="flex items-center gap-2">
                            <Checkbox
                              checked={param.enabled}
                              onCheckedChange={(checked) => {
                                const newParams = [...queryParams];
                                newParams[idx].enabled = checked;
                                setQueryParams(newParams);
                                syncURLWithParams();
                              }}
                              className="border-white/20"
                            />
                            <Input
                              value={param.key}
                              onChange={(e) => {
                                const newParams = [...queryParams];
                                newParams[idx].key = e.target.value;
                                setQueryParams(newParams);
                              }}
                              onBlur={syncURLWithParams}
                              placeholder="key"
                              className="flex-1 bg-white/10 border-white/20 text-white h-9 text-sm"
                            />
                            <Input
                              value={param.value}
                              onChange={(e) => {
                                const newParams = [...queryParams];
                                newParams[idx].value = e.target.value;
                                setQueryParams(newParams);
                              }}
                              onBlur={syncURLWithParams}
                              placeholder="value (use {{variable}})"
                              className="flex-1 bg-white/10 border-white/20 text-white h-9 text-sm"
                            />
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setQueryParams(queryParams.filter((_, i) => i !== idx));
                                syncURLWithParams();
                              }}
                              className="text-red-400 h-9 w-9 p-0"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        ))}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setQueryParams([...queryParams, { key: '', value: '', enabled: true }])}
                          className="w-full border-white/20 text-white h-9"
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Add Parameter
                        </Button>
                      </div>
                    </TabsContent>

                    {/* Headers Tab */}
                    <TabsContent value="headers" className="mt-4">
                      <div className="space-y-2">
                        {headers.map((header, idx) => (
                          <div key={idx} className="flex items-center gap-2">
                            <Checkbox
                              checked={header.enabled}
                              onCheckedChange={(checked) => {
                                const newHeaders = [...headers];
                                newHeaders[idx].enabled = checked;
                                setHeaders(newHeaders);
                              }}
                              className="border-white/20"
                            />
                            <Input
                              value={header.key}
                              onChange={(e) => {
                                const newHeaders = [...headers];
                                newHeaders[idx].key = e.target.value;
                                setHeaders(newHeaders);
                              }}
                              placeholder="Header name"
                              list="common-headers"
                              className="flex-1 bg-white/10 border-white/20 text-white h-9 text-sm"
                            />
                            <datalist id="common-headers">
                              {COMMON_HEADERS.map(h => <option key={h} value={h} />)}
                            </datalist>
                            <Input
                              value={header.value}
                              onChange={(e) => {
                                const newHeaders = [...headers];
                                newHeaders[idx].value = e.target.value;
                                setHeaders(newHeaders);
                              }}
                              placeholder="value (use {{variable}})"
                              className="flex-1 bg-white/10 border-white/20 text-white h-9 text-sm"
                            />
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setHeaders(headers.filter((_, i) => i !== idx))}
                              className="text-red-400 h-9 w-9 p-0"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        ))}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setHeaders([...headers, { key: '', value: '', enabled: true }])}
                          className="w-full border-white/20 text-white h-9"
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Add Header
                        </Button>
                      </div>
                    </TabsContent>

                    {/* Body Tab */}
                    <TabsContent value="body" className="mt-4">
                      <div className="space-y-4">
                        <Select value={bodyType} onValueChange={setBodyType}>
                          <SelectTrigger className="w-full sm:w-64 bg-white/10 border-white/20 text-white">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {BODY_TYPES.map(type => (
                              <SelectItem key={type} value={type}>
                                {type === 'none' ? 'No Body' : type.toUpperCase()}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>

                        {bodyType === 'json' && (
                          <Textarea
                            value={jsonBody}
                            onChange={(e) => setJsonBody(e.target.value)}
                            placeholder='{\n  "key": "value"\n}'
                            className="bg-white/10 border-white/20 text-white font-mono min-h-[200px] text-sm"
                          />
                        )}

                        {bodyType === 'raw' && (
                          <Textarea
                            value={rawBody}
                            onChange={(e) => setRawBody(e.target.value)}
                            placeholder="Raw text content (use {{variable}})"
                            className="bg-white/10 border-white/20 text-white font-mono min-h-[200px] text-sm"
                          />
                        )}

                        {bodyType === 'form-data' && (
                          <div className="space-y-2">
                            {formDataBody.map((item, idx) => (
                              <div key={idx} className="flex items-center gap-2">
                                <Checkbox
                                  checked={item.enabled}
                                  onCheckedChange={(checked) => {
                                    const newData = [...formDataBody];
                                    newData[idx].enabled = checked;
                                    setFormDataBody(newData);
                                  }}
                                  className="border-white/20"
                                />
                                <Input
                                  value={item.key}
                                  onChange={(e) => {
                                    const newData = [...formDataBody];
                                    newData[idx].key = e.target.value;
                                    setFormDataBody(newData);
                                  }}
                                  placeholder="key"
                                  className="flex-1 bg-white/10 border-white/20 text-white h-9 text-sm"
                                />
                                <Input
                                  value={item.value}
                                  onChange={(e) => {
                                    const newData = [...formDataBody];
                                    newData[idx].value = e.target.value;
                                    setFormDataBody(newData);
                                  }}
                                  placeholder="value (use {{variable}})"
                                  className="flex-1 bg-white/10 border-white/20 text-white h-9 text-sm"
                                />
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => setFormDataBody(formDataBody.filter((_, i) => i !== idx))}
                                  className="text-red-400 h-9 w-9 p-0"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            ))}
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setFormDataBody([...formDataBody, { key: '', value: '', enabled: true }])}
                              className="w-full border-white/20 text-white h-9"
                            >
                              <Plus className="w-4 h-4 mr-2" />
                              Add Field
                            </Button>
                          </div>
                        )}

                        {bodyType === 'xml' && (
                          <Textarea
                            value={xmlBody}
                            onChange={(e) => setXmlBody(e.target.value)}
                            placeholder='<?xml version="1.0"?>\n<root>\n  \n</root>'
                            className="bg-white/10 border-white/20 text-white font-mono min-h-[200px] text-sm"
                          />
                        )}
                      </div>
                    </TabsContent>

                    {/* AI Tab */}
                    <TabsContent value="ai" className="mt-4">
                      <div className="space-y-4">
                        {/* Provider Selection */}
                        <div className="flex items-center gap-2">
                          <Label className="text-white text-sm">AI Provider:</Label>
                          <Select value={selectedAIProvider} onValueChange={setSelectedAIProvider}>
                            <SelectTrigger className="flex-1 bg-white/10 border-white/20 text-white h-9 text-sm">
                              <SelectValue placeholder="Select AI provider" />
                            </SelectTrigger>
                            <SelectContent>
                              {providers.map(p => (
                                <SelectItem key={p.id} value={p.id}>
                                  {p.name} - {p.model}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>

                        {/* AI Features Selection */}
                        <Select value={aiFeature} onValueChange={setAiFeature}>
                          <SelectTrigger className="w-full bg-white/10 border-white/20 text-white">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="request-builder">🤖 AI Request Builder</SelectItem>
                            <SelectItem value="analyze-response">🔍 Smart Response Analysis</SelectItem>
                            <SelectItem value="security-analysis">🛡️ Security Analysis</SelectItem>
                            <SelectItem value="test-data">📊 Generate Test Data</SelectItem>
                            <SelectItem value="from-docs">📄 From Documentation</SelectItem>
                            <SelectItem value="explain">💡 Explain API</SelectItem>
                            <SelectItem value="assertions">✅ Generate Assertions</SelectItem>
                            <SelectItem value="generate-code">💻 Generate Code</SelectItem>
                          </SelectContent>
                        </Select>

                        {/* AI Input Area */}
                        <div className="space-y-2">
                          {(aiFeature === 'request-builder' || aiFeature === 'generate-code') && (
                            <>
                              <Label className="text-white text-sm">Describe what you want to test:</Label>
                              <Textarea
                                value={aiInput}
                                onChange={(e) => setAiInput(e.target.value)}
                                placeholder="Example: Create a POST request to authenticate a user with email and password"
                                className="bg-white/10 border-white/20 text-white min-h-[100px]"
                              />
                            </>
                          )}

                          {aiFeature === 'from-docs' && (
                            <>
                              <Label className="text-white text-sm">Paste API Documentation:</Label>
                              <Textarea
                                value={aiInput}
                                onChange={(e) => setAiInput(e.target.value)}
                                placeholder="Paste API docs, Swagger spec, or OpenAPI schema here..."
                                className="bg-white/10 border-white/20 text-white font-mono min-h-[150px] text-sm"
                              />
                            </>
                          )}

                          {aiFeature === 'test-data' && (
                            <>
                              <Label className="text-white text-sm">Additional context (optional):</Label>
                              <Textarea
                                value={aiInput}
                                onChange={(e) => setAiInput(e.target.value)}
                                placeholder="Describe any specific test scenarios you want..."
                                className="bg-white/10 border-white/20 text-white min-h-[80px]"
                              />
                            </>
                          )}

                          {(aiFeature === 'analyze-response' || aiFeature === 'security-analysis' || 
                            aiFeature === 'explain' || aiFeature === 'assertions') && (
                            <div className="p-3 rounded bg-blue-500/10 border border-blue-500/20">
                              <p className="text-blue-300 text-sm flex items-center gap-2">
                                <Sparkles className="w-4 h-4" />
                                Send a request first, then AI will analyze the response
                              </p>
                            </div>
                          )}

                          <Button
                            onClick={() => {
                              if ((aiFeature === 'request-builder' || aiFeature === 'from-docs' || 
                                   aiFeature === 'generate-code') && !aiInput.trim()) {
                                toast.error('Please provide input');
                                return;
                              }
                              if ((aiFeature === 'analyze-response' || aiFeature === 'security-analysis' || 
                                   aiFeature === 'explain' || aiFeature === 'assertions') && !response) {
                                toast.error('Send a request first');
                                return;
                              }
                              callAIFeature(aiFeature, aiInput);
                            }}
                            disabled={aiLoading || !selectedAIProvider}
                            className="w-full bg-gradient-to-r from-violet-500 to-purple-500 h-10"
                          >
                            {aiLoading ? (
                              <>
                                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                                Analyzing...
                              </>
                            ) : (
                              <>
                                <Sparkles className="w-4 h-4 mr-2" />
                                Run AI Analysis
                              </>
                            )}
                          </Button>
                        </div>

                        {/* AI Response Display */}
                        {aiResponse && (
                          <div className="space-y-2">
                            <Label className="text-white text-sm">AI Response:</Label>
                            <ScrollArea className="h-96 rounded bg-slate-950/50 border border-white/10">
                              <div className="p-4">
                                <div className="prose prose-invert prose-sm max-w-none">
                                  <pre className="whitespace-pre-wrap text-sm text-white font-mono">
                                    {aiResponse}
                                  </pre>
                                </div>
                              </div>
                            </ScrollArea>
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={async () => {
                                  try {
                                    await navigator.clipboard.writeText(aiResponse);
                                    toast.success('Copied to clipboard');
                                  } catch {
                                    toast.error('Failed to copy');
                                  }
                                }}
                                className="border-white/20 text-white"
                              >
                                <Copy className="w-4 h-4 mr-2" />
                                Copy Response
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setAiResponse('')}
                                className="border-white/20 text-white"
                              >
                                Clear
                              </Button>
                            </div>
                          </div>
                        )}

                        {/* Feature Descriptions */}
                        <div className="p-3 rounded bg-white/5 border border-white/10">
                          <p className="text-slate-300 text-xs leading-relaxed">
                            {aiFeature === 'request-builder' && '🤖 Describe your API test in plain English and AI will build the complete request configuration.'}
                            {aiFeature === 'analyze-response' && '🔍 AI analyzes your API response, explains the data structure, and identifies potential issues.'}
                            {aiFeature === 'security-analysis' && '🛡️ AI performs comprehensive security analysis checking for vulnerabilities (OWASP API Top 10).'}
                            {aiFeature === 'test-data' && '📊 AI generates realistic test data covering happy path, edge cases, and error scenarios.'}
                            {aiFeature === 'from-docs' && '📄 Paste API documentation and AI extracts endpoints, parameters, and creates working requests.'}
                            {aiFeature === 'explain' && '💡 AI provides detailed explanation of what this API endpoint does and how to use it.'}
                            {aiFeature === 'assertions' && '✅ AI auto-generates test assertions in multiple languages (Jest, pytest, plain English).'}
                            {aiFeature === 'generate-code' && '💻 Describe what you want and AI generates ready-to-use code in your preferred language.'}
                          </p>
                        </div>
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>

              {/* Response Section */}
              <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                <CardHeader className="p-4 sm:p-6">
                  <CardTitle className="text-white flex items-center justify-between">
                    <span>Response</span>
                    {response && (
                      <span className={`text-sm px-3 py-1 rounded ${
                        response.status >= 200 && response.status < 300 ? 'bg-green-500/20 text-green-400' :
                        response.status >= 400 ? 'bg-red-500/20 text-red-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {response.status} {response.statusText}
                      </span>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4 sm:p-6 pt-0">
                  {!response ? (
                    <p className="text-slate-400 text-sm">No response yet. Click "Send" to execute the request.</p>
                  ) : response.error ? (
                    <div className="p-4 rounded bg-red-500/10 border border-red-500/20">
                      <p className="text-red-400 font-mono text-sm break-all">{response.error}</p>
                    </div>
                  ) : (
                    <div>
                      <div className="mb-4 flex gap-4 text-sm">
                        <span className="text-slate-400">Time: <span className="text-white font-mono">{response.responseTime}ms</span></span>
                        <span className="text-slate-400">Size: <span className="text-white font-mono">{response.size} bytes</span></span>
                      </div>
                      <ScrollArea className="h-64 sm:h-80">
                        <pre className="p-4 rounded bg-slate-950/50 overflow-x-auto">
                          <code className="text-sm text-white font-mono">
                            {typeof response.body === 'object' ? JSON.stringify(response.body, null, 2) : response.body}
                          </code>
                        </pre>
                      </ScrollArea>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>

      {/* Environment Variables Dialog */}
      <Dialog open={showVariablesDialog} onOpenChange={setShowVariablesDialog}>
        <DialogContent className="bg-slate-900 border-white/10 max-w-[95vw] sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Variable className="w-5 h-5" />
              Environment Variables
            </DialogTitle>
            <DialogDescription className="text-slate-300">
              Use <code className="bg-slate-800 px-1 rounded">{`{{variableName}}`}</code> in URL, headers, or body
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2 mt-4 max-h-[60vh] overflow-y-auto">
            {environmentVars.map((variable, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <Checkbox
                  checked={variable.enabled}
                  onCheckedChange={(checked) => {
                    const newVars = [...environmentVars];
                    newVars[idx].enabled = checked;
                    setEnvironmentVars(newVars);
                  }}
                  className="border-white/20"
                />
                <Input
                  value={variable.key}
                  onChange={(e) => {
                    const newVars = [...environmentVars];
                    newVars[idx].key = e.target.value;
                    setEnvironmentVars(newVars);
                  }}
                  placeholder="Variable name"
                  className="flex-1 bg-white/10 border-white/20 text-white h-9 text-sm"
                />
                <Input
                  value={variable.value}
                  onChange={(e) => {
                    const newVars = [...environmentVars];
                    newVars[idx].value = e.target.value;
                    setEnvironmentVars(newVars);
                  }}
                  placeholder="Value"
                  className="flex-1 bg-white/10 border-white/20 text-white h-9 text-sm"
                />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setEnvironmentVars(environmentVars.filter((_, i) => i !== idx))}
                  className="text-red-400 h-9 w-9 p-0"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setEnvironmentVars([...environmentVars, { key: '', value: '', enabled: true }])}
              className="w-full border-white/20 text-white h-9"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Variable
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Code Generation Dialog */}
      <Dialog open={showCodeDialog} onOpenChange={setShowCodeDialog}>
        <DialogContent className="bg-slate-900 border-white/10 max-w-[95vw] sm:max-w-4xl max-h-[90vh]">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center justify-between">
              <span>Generated Code</span>
              <div className="flex gap-2">
                <Select value={codeLanguage} onValueChange={generateCode}>
                  <SelectTrigger className="w-40 bg-white/10 border-white/20 text-white h-9">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="javascript">JavaScript</SelectItem>
                    <SelectItem value="python">Python</SelectItem>
                    <SelectItem value="curl">cURL</SelectItem>
                    <SelectItem value="csharp">C#</SelectItem>
                  </SelectContent>
                </Select>
                <Button onClick={copyCode} variant="outline" className="border-white/20 text-white h-9 w-9 p-0">
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
            </DialogTitle>
          </DialogHeader>
          <ScrollArea className="h-96 mt-4">
            <pre className="p-4 rounded bg-slate-950/50">
              <code className={`text-sm language-${codeLanguage === 'csharp' ? 'clike' : codeLanguage}`}>
                {generatedCode}
              </code>
            </pre>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default APITestingEnhanced;
