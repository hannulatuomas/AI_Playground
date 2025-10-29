import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Textarea } from './components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { ScrollArea } from './components/ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from './components/ui/sheet';
import { Menu, X, Plus, Play, Save, Upload, Sun, Moon, LogOut, Folder, Settings, Activity, Zap, Shield, BarChart3, Users } from 'lucide-react';
import WorkflowDesigner from './components/WorkflowDesigner';
import MonitoringPanel from './components/MonitoringPanel';
import MicrosoftIntegration from './components/MicrosoftIntegration';
import GDPRCompliance from './components/GDPRCompliance';
import axios from 'axios';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, vs } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './App.css';

// Context for theme
import { createContext, useContext } from 'react';

const ThemeContext = createContext();
const AuthContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Configure axios defaults
axios.defaults.baseURL = API;

// Theme Provider Component
const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'dark';
  });

  useEffect(() => {
    localStorage.setItem('theme', theme);
    document.documentElement.className = theme;
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Auth Provider Component
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      axios.get('/auth/me')
        .then(response => {
          setUser(response.data);
        })
        .catch(() => {
          localStorage.removeItem('token');
          setToken(null);
          delete axios.defaults.headers.common['Authorization'];
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await axios.post('/auth/login', { username, password });
      const { access_token, user: userData } = response.data;
      
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      toast.success('Welcome back!');
      return true;
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed';
      toast.error(message);
      return false;
    }
  };

  const register = async (username, email, password) => {
    try {
      const response = await axios.post('/auth/register', { username, email, password });
      const { access_token, user: userData } = response.data;
      
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      toast.success('Account created successfully!');
      return true;
    } catch (error) {
      const message = error.response?.data?.detail || 'Registration failed';
      toast.error(message);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    toast.success('Logged out successfully');
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hooks
const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// Helper Components
const KeyValueEditor = ({ data, onChange, placeholder = "Add item" }) => {
  const addRow = () => {
    onChange({ ...data, '': '' });
  };

  const updateKey = (oldKey, newKey) => {
    const newData = { ...data };
    if (oldKey !== newKey) {
      newData[newKey] = newData[oldKey];
      delete newData[oldKey];
    }
    onChange(newData);
  };

  const updateValue = (key, value) => {
    onChange({ ...data, [key]: value });
  };

  const deleteRow = (key) => {
    const newData = { ...data };
    delete newData[key];
    onChange(newData);
  };

  return (
    <div className="space-y-2">
      {Object.entries(data).map(([key, value], index) => (
        <div key={index} className="flex gap-2">
          <Input
            placeholder="Key"
            value={key}
            onChange={(e) => updateKey(key, e.target.value)}
            className="flex-1 h-8 text-sm"
          />
          <Input
            placeholder="Value"
            value={value}
            onChange={(e) => updateValue(key, e.target.value)}
            className="flex-1 h-8 text-sm"
          />
          <Button
            variant="ghost"
            size="sm"
            onClick={() => deleteRow(key)}
            className="h-8 w-8 p-0 text-red-500 hover:text-red-700"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ))}
      <Button
        variant="outline"
        size="sm"
        onClick={addRow}
        className="w-full h-8 text-sm"
      >
        <Plus className="h-3 w-3 mr-1" />
        {placeholder}
      </Button>
    </div>
  );
};

const AuthEditor = ({ auth, onChange }) => {
  const updateAuth = (field, value) => {
    onChange({ ...auth, [field]: value });
  };

  return (
    <div className="space-y-3">
      <div>
        <Label className="text-sm">Type</Label>
        <Select value={auth.type} onValueChange={(value) => updateAuth('type', value)}>
          <SelectTrigger className="h-8">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">None</SelectItem>
            <SelectItem value="bearer">Bearer Token</SelectItem>
            <SelectItem value="basic">Basic Auth</SelectItem>
            <SelectItem value="apikey">API Key</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      {auth.type === 'bearer' && (
        <div>
          <Label className="text-sm">Token</Label>
          <Input
            value={auth.token || ''}
            onChange={(e) => updateAuth('token', e.target.value)}
            placeholder="Enter bearer token"
            className="h-8"
          />
        </div>
      )}
      
      {auth.type === 'basic' && (
        <div className="space-y-2">
          <div>
            <Label className="text-sm">Username</Label>
            <Input
              value={auth.username || ''}
              onChange={(e) => updateAuth('username', e.target.value)}
              placeholder="Username"
              className="h-8"
            />
          </div>
          <div>
            <Label className="text-sm">Password</Label>
            <Input
              type="password"
              value={auth.password || ''}
              onChange={(e) => updateAuth('password', e.target.value)}
              placeholder="Password"
              className="h-8"
            />
          </div>
        </div>
      )}
      
      {auth.type === 'apikey' && (
        <div className="space-y-2">
          <div>
            <Label className="text-sm">Key</Label>
            <Input
              value={auth.key || ''}
              onChange={(e) => updateAuth('key', e.target.value)}
              placeholder="API Key name"
              className="h-8"
            />
          </div>
          <div>
            <Label className="text-sm">Value</Label>
            <Input
              value={auth.value || ''}
              onChange={(e) => updateAuth('value', e.target.value)}
              placeholder="API Key value"
              className="h-8"
            />
          </div>
          <div>
            <Label className="text-sm">Location</Label>
            <Select value={auth.location || 'header'} onValueChange={(value) => updateAuth('location', value)}>
              <SelectTrigger className="h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="header">Header</SelectItem>
                <SelectItem value="query">Query Parameter</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      )}
    </div>
  );
};

// Import Dialog Component - OLD VERSION - DEPRECATED
const ImportDialogOLD = ({ onImport, trigger }) => {
  const [importType, setImportType] = useState('openapi');
  const [content, setContent] = useState('');
  const [collectionName, setCollectionName] = useState('');
  const [isImporting, setIsImporting] = useState(false);

  const handleImport = async () => {
    if (!content.trim()) {
      toast.error('Please paste the specification content');
      return;
    }

    setIsImporting(true);
    try {
      const response = await axios.post('/import', {
        type: importType,
        content: content,
        collection_name: collectionName || null
      });
      
      toast.success(response.data.message);
      onImport();
      setContent('');
      setCollectionName('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Import failed');
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        {trigger}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Import API Specification</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div>
            <Label>Import Type</Label>
            <Select value={importType} onValueChange={setImportType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="openapi">OpenAPI / Swagger</SelectItem>
                <SelectItem value="postman">Postman Collection</SelectItem>
                <SelectItem value="wsdl">WSDL</SelectItem>
                <SelectItem value="raml">RAML</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label>Collection Name (Optional)</Label>
            <Input
              value={collectionName}
              onChange={(e) => setCollectionName(e.target.value)}
              placeholder="Leave empty to add to existing collection"
            />
          </div>
          
          <div>
            <Label>Specification Content</Label>
            <Textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={`Paste your ${importType.toUpperCase()} specification here...`}
              className="h-48 font-mono text-sm"
            />
          </div>
          
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setContent('')}>
              Clear
            </Button>
            <Button onClick={handleImport} disabled={isImporting}>
              {isImporting ? 'Importing...' : 'Import'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Auth Form Component
const AuthForm = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login, register, user } = useAuth();
  
  // Redirect to dashboard if already logged in
  useEffect(() => {
    if (user) {
      // Use React Router's navigate instead of window.location
      window.location.replace('/');
    }
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    const success = isLogin 
      ? await login(formData.username, formData.password)
      : await register(formData.username, formData.email, formData.password);
    
    setIsSubmitting(false);
    if (success) {
      setFormData({ username: '', email: '', password: '' });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            APIForge
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Multi-Protocol API Management & Testing Tool
          </p>
        </div>
        
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-8">
          <div className="flex rounded-lg bg-slate-100 dark:bg-slate-700 p-1 mb-6">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                isLogin 
                  ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm' 
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Login
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                !isLogin 
                  ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm' 
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Register
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Username
              </label>
              <input
                type="text"
                required
                value={formData.username}
                onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Enter your username"
                data-testid="username-input"
              />
            </div>
            
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="Enter your email"
                  data-testid="email-input"
                />
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Password
              </label>
              <input
                type="password"
                required
                value={formData.password}
                onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Enter your password"
                data-testid="password-input"
              />
            </div>
            
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-slate-400 disabled:to-slate-500 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-[1.02] disabled:scale-100 disabled:cursor-not-allowed"
              data-testid="auth-submit-btn"
            >
              {isSubmitting ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
            </button>
          </form>
        </div>
        
        {/* Demo Credentials - UNDER the login dialog */}
        {isLogin && (
          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div className="text-sm text-blue-800 dark:text-blue-200 text-center">
              <span className="font-medium">Demo Credentials:</span>
            </div>
            <div className="text-xs text-blue-600 dark:text-blue-300 text-center mt-1">
              Username: <span className="font-mono font-semibold">testuser</span> | 
              Password: <span className="font-mono font-semibold">testpass123</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Duplicate MobileSidebar component removed - using enhanced version below

// ==============================================
// EXPORT GENERATION FUNCTIONS
// ==============================================

const generateOpenAPISpec = (collectionsData) => {
  const spec = {
    openapi: "3.0.0",
    info: {
      title: "API Documentation",
      version: "1.0.0",
      description: "Generated from APIForge collections"
    },
    servers: [
      { url: "https://api.example.com", description: "Production server" }
    ],
    paths: {}
  };

  collectionsData.forEach(collection => {
    collection.requests?.forEach(request => {
      if (request.protocol === 'REST') {
        const url = new URL(request.url || 'https://api.example.com/path');
        const path = url.pathname;
        const method = request.method.toLowerCase();

        if (!spec.paths[path]) {
          spec.paths[path] = {};
        }

        spec.paths[path][method] = {
          summary: request.name,
          description: request.description || '',
          parameters: Object.entries(request.query_params || {}).map(([key, value]) => ({
            name: key,
            in: 'query',
            schema: { type: 'string', example: value }
          })),
          responses: {
            '200': {
              description: 'Success'
            }
          }
        };

        if (['post', 'put', 'patch'].includes(method) && request.body) {
          spec.paths[path][method].requestBody = {
            content: {
              'application/json': {
                schema: { type: 'object' }
              }
            }
          };
        }
      }
    });
  });

  return spec;
};

const generatePostmanCollection = (collectionsData) => {
  const collection = {
    info: {
      name: "APIForge Export",
      description: "Exported from APIForge",
      schema: "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    item: []
  };

  collectionsData.forEach(coll => {
    const folder = {
      name: coll.name,
      description: coll.description,
      item: []
    };

    coll.requests?.forEach(request => {
      const item = {
        name: request.name,
        request: {
          method: request.method || 'GET',
          header: Object.entries(request.headers || {}).map(([key, value]) => ({
            key, value, type: 'text'
          })),
          url: {
            raw: request.url,
            host: [request.url?.split('/')[2] || 'api.example.com'],
            path: request.url?.split('/').slice(3) || []
          }
        }
      };

      if (request.body) {
        item.request.body = {
          mode: 'raw',
          raw: request.body
        };
      }

      folder.item.push(item);
    });

    collection.item.push(folder);
  });

  return collection;
};

const generateInsomniaCollection = (collectionsData) => {
  const workspace = {
    _type: "export",
    __export_format: 4,
    __export_date: new Date().toISOString(),
    __export_source: "apiforge",
    resources: [
      {
        _id: "wrk_" + Date.now(),
        _type: "workspace",
        created: Date.now(),
        description: "Exported from APIForge",
        modified: Date.now(),
        name: "APIForge Export",
        parentId: null
      }
    ]
  };

  collectionsData.forEach(collection => {
    // Add folder
    const folderId = "fld_" + Date.now() + Math.random();
    workspace.resources.push({
      _id: folderId,
      _type: "request_group",
      created: Date.now(),
      description: collection.description,
      modified: Date.now(),
      name: collection.name,
      parentId: workspace.resources[0]._id
    });

    // Add requests
    collection.requests?.forEach(request => {
      workspace.resources.push({
        _id: "req_" + Date.now() + Math.random(),
        _type: "request",
        created: Date.now(),
        modified: Date.now(),
        name: request.name,
        parentId: folderId,
        method: request.method || 'GET',
        url: request.url,
        headers: Object.entries(request.headers || {}).map(([name, value]) => ({ name, value })),
        body: request.body ? {
          mimeType: "application/json",
          text: request.body
        } : undefined
      });
    });
  });

  return workspace;
};

const generateWSDLFromSOAP = (collectionsData) => {
  const soapRequests = collectionsData.flatMap(c => 
    c.requests?.filter(r => r.protocol === 'SOAP') || []
  );

  if (soapRequests.length === 0) {
    throw new Error('No SOAP requests found to generate WSDL');
  }

  const serviceName = collectionsData[0]?.name.replace(/\s+/g, '') + 'Service';
  const targetNamespace = 'http://example.com/service';

  return `<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/"
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:tns="${targetNamespace}"
             targetNamespace="${targetNamespace}">
  
  <types>
    <schema xmlns="http://www.w3.org/2001/XMLSchema" 
            targetNamespace="${targetNamespace}"/>
  </types>
  
  <portType name="${serviceName}PortType">
    ${soapRequests.map(req => `
    <operation name="${req.name.replace(/\s+/g, '')}">
      <input message="tns:${req.name.replace(/\s+/g, '')}Request"/>
      <output message="tns:${req.name.replace(/\s+/g, '')}Response"/>
    </operation>`).join('')}
  </portType>
  
  <binding name="${serviceName}Binding" type="tns:${serviceName}PortType">
    <soap:binding transport="http://schemas.xmlsoap.org/soap/http"/>
    ${soapRequests.map(req => `
    <operation name="${req.name.replace(/\s+/g, '')}">
      <soap:operation soapAction="${req.soapAction || ''}"/>
      <input><soap:body use="literal"/></input>
      <output><soap:body use="literal"/></output>
    </operation>`).join('')}
  </binding>
  
  <service name="${serviceName}">
    <port name="${serviceName}Port" binding="tns:${serviceName}Binding">
      <soap:address location="${soapRequests[0]?.url || 'http://example.com/service'}"/>
    </port>
  </service>
</definitions>`;
};

const generateRAMLSpec = (collectionsData) => {
  const restRequests = collectionsData.flatMap(c => 
    c.requests?.filter(r => r.protocol === 'REST') || []
  );

  if (restRequests.length === 0) {
    throw new Error('No REST requests found to generate RAML');
  }

  let raml = `#%RAML 1.0
title: API Documentation
version: v1
baseUri: https://api.example.com
description: Generated from APIForge collections

`;

  // Group by path
  const pathGroups = {};
  restRequests.forEach(request => {
    try {
      const url = new URL(request.url || 'https://api.example.com/path');
      const path = url.pathname;
      if (!pathGroups[path]) pathGroups[path] = [];
      pathGroups[path].push(request);
    } catch (e) {
      // Skip invalid URLs
    }
  });

  Object.entries(pathGroups).forEach(([path, requests]) => {
    raml += `${path}:\n`;
    requests.forEach(request => {
      raml += `  ${request.method.toLowerCase()}:\n`;
      raml += `    displayName: ${request.name}\n`;
      if (request.description) {
        raml += `    description: ${request.description}\n`;
      }
      raml += `    responses:\n`;
      raml += `      200:\n`;
      raml += `        description: Success\n`;
    });
  });

  return raml;
};

const generateGraphQLSchema = (collectionsData) => {
  const graphqlRequests = collectionsData.flatMap(c => 
    c.requests?.filter(r => r.protocol === 'GraphQL') || []
  );

  if (graphqlRequests.length === 0) {
    throw new Error('No GraphQL requests found to generate schema');
  }

  let schema = `# GraphQL Schema Generated from APIForge
# Generated on ${new Date().toISOString()}

type Query {
`;

  graphqlRequests
    .filter(r => r.graphqlOperation === 'query')
    .forEach(request => {
      const fieldName = request.name.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
      schema += `  ${fieldName}: String # ${request.name}\n`;
    });

  schema += `}

type Mutation {
`;

  graphqlRequests
    .filter(r => r.graphqlOperation === 'mutation')
    .forEach(request => {
      const fieldName = request.name.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
      schema += `  ${fieldName}: String # ${request.name}\n`;
    });

  schema += `}
`;

  return schema;
};

// Extraction Rules Manager Component
const ExtractionRulesManager = ({ rules, onUpdate, selectedCollection }) => {
  const [showDialog, setShowDialog] = useState(false);
  const [tempRules, setTempRules] = useState(rules || []);

  const addRule = () => {
    setTempRules([...tempRules, { name: '', path: '', scope: 'global' }]);
  };

  const updateRule = (index, field, value) => {
    const newRules = [...tempRules];
    newRules[index][field] = value;
    setTempRules(newRules);
  };

  const removeRule = (index) => {
    setTempRules(tempRules.filter((_, i) => i !== index));
  };

  const handleSave = () => {
    const validRules = tempRules.filter(rule => rule.name && rule.path);
    onUpdate(validRules);
    setShowDialog(false);
  };

  const handleOpen = () => {
    setTempRules(rules || []);
    setShowDialog(true);
  };

  return (
    <>
      <Button variant="outline" size="sm" onClick={handleOpen}>
        <Settings className="h-4 w-4 mr-1" />
        Auto-Extract ({rules?.length || 0})
      </Button>
      
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Auto-Extract Variables</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground">
              Define rules to automatically extract variables from response when this request is executed.
            </div>
            
            <div className="space-y-2">
              {tempRules.map((rule, index) => (
                <div key={index} className="flex gap-2 items-center">
                  <Input
                    placeholder="Variable name"
                    value={rule.name}
                    onChange={(e) => updateRule(index, 'name', e.target.value)}
                    className="flex-1"
                  />
                  <Input
                    placeholder="JSONPath (e.g., $.token)"
                    value={rule.path}
                    onChange={(e) => updateRule(index, 'path', e.target.value)}
                    className="flex-2"
                  />
                  <Select value={rule.scope} onValueChange={(value) => updateRule(index, 'scope', value)}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="global">Global</SelectItem>
                      {selectedCollection && (
                        <SelectItem value="collection">Collection</SelectItem>
                      )}
                    </SelectContent>
                  </Select>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeRule(index)}
                    className="px-2"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              
              <Button variant="outline" onClick={addRule} className="w-full">
                <Plus className="h-4 w-4 mr-1" />
                Add Extraction Rule
              </Button>
            </div>
            
            <div className="text-sm text-muted-foreground">
              <strong>Examples:</strong><br/>
              • <code>$.access_token</code> → Extract token from root<br/>
              • <code>$.data[0].id</code> → Extract first item's ID<br/>
              • <code>$.response.user.email</code> → Extract nested user email
            </div>
            
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowDialog(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave}>
                Save Rules
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

// Variable Extraction Dialog Component
const VariableExtractionDialog = ({ responseBody, trigger }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [extractions, setExtractions] = useState([{ name: '', path: '' }]);
  const [scope, setScope] = useState('global');

  const addExtraction = () => {
    setExtractions([...extractions, { name: '', path: '' }]);
  };

  const updateExtraction = (index, field, value) => {
    const newExtractions = [...extractions];
    newExtractions[index][field] = value;
    setExtractions(newExtractions);
  };

  const removeExtraction = (index) => {
    setExtractions(extractions.filter((_, i) => i !== index));
  };

  const handleExtract = async () => {
    const validExtractions = extractions.filter(e => e.name && e.path);
    if (validExtractions.length === 0) {
      toast.error('Please add at least one valid extraction');
      return;
    }

    try {
      await axios.post('/variables/extract', {
        response_body: responseBody,
        extractions: validExtractions,
        scope: scope === 'global' ? 'global' : selectedCollection?.id
      });
      
      loadVariables();
      toast.success(`Variables extracted to ${scope} scope`);
      setIsOpen(false);
    } catch (error) {
      toast.error('Failed to extract variables');
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {trigger}
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Extract Variables from Response</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label>Scope</Label>
            <Select value={scope} onValueChange={setScope}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="global">Global Variables</SelectItem>
                {selectedCollection && (
                  <SelectItem value="collection">Collection Variables ({selectedCollection.name})</SelectItem>
                )}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label>Variable Extractions</Label>
            <div className="space-y-2">
              {extractions.map((extraction, index) => (
                <div key={index} className="flex gap-2">
                  <Input
                    placeholder="Variable name"
                    value={extraction.name}
                    onChange={(e) => updateExtraction(index, 'name', e.target.value)}
                    className="flex-1"
                  />
                  <Input
                    placeholder="JSONPath (e.g., $.token or $.data[0].id)"
                    value={extraction.path}
                    onChange={(e) => updateExtraction(index, 'path', e.target.value)}
                    className="flex-2"
                  />
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeExtraction(index)}
                    className="px-2"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              <Button variant="outline" onClick={addExtraction} className="w-full">
                <Plus className="h-4 w-4 mr-1" />
                Add Extraction
              </Button>
            </div>
          </div>
          
          <div className="text-sm text-muted-foreground">
            <strong>JSONPath Examples:</strong><br/>
            • <code>$.token</code> - Extract token from root<br/>
            • <code>$.data[0].id</code> - Extract first item's id<br/>
            • <code>$.response.access_token</code> - Extract nested access_token
          </div>
          
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleExtract}>
              Extract Variables
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Editable Variable Row Component
const EditableVariableRow = ({ scope, varKey, value, onUpdate, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value);

  const handleSave = () => {
    onUpdate(scope, varKey, editValue);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditValue(value);
    setIsEditing(false);
  };

  return (
    <div className="flex items-center justify-between p-2 bg-muted/50 rounded">
      <div className="flex-1">
        <span className="text-sm font-mono">{`{{${varKey}}}`}</span>
        {isEditing ? (
          <div className="mt-1">
            <Input
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className="h-6 text-xs"
              onKeyPress={(e) => {
                if (e.key === 'Enter') handleSave();
                if (e.key === 'Escape') handleCancel();
              }}
              autoFocus
            />
          </div>
        ) : (
          <span className="text-xs text-muted-foreground ml-2 block truncate">{value}</span>
        )}
      </div>
      <div className="flex gap-1">
        {isEditing ? (
          <>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSave}
              className="h-6 w-6 p-0"
              title="Save"
            >
              <Save className="h-3 w-3 text-green-500" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCancel}
              className="h-6 w-6 p-0"
              title="Cancel"
            >
              <X className="h-3 w-3 text-gray-500" />
            </Button>
          </>
        ) : (
          <>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsEditing(true)}
              className="h-6 w-6 p-0"
              title="Edit Variable"
            >
              <Settings className="h-3 w-3 text-blue-500" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(scope, varKey)}
              className="h-6 w-6 p-0"
              title="Delete Variable"
            >
              <X className="h-3 w-3 text-red-500" />
            </Button>
          </>
        )}
      </div>
    </div>
  );
};

// Variables Panel Component
const VariablesPanel = ({ variables, selectedCollection, onUpdateVariable, onDeleteVariable }) => {
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newVar, setNewVar] = useState({ scope: 'global', name: '', value: '' });

  const handleAddVariable = () => {
    if (newVar.name && newVar.value) {
      onUpdateVariable(newVar.scope, newVar.name, newVar.value);
      setNewVar({ scope: 'global', name: '', value: '' });
      setShowAddDialog(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Variables</h3>
        <Button size="sm" onClick={() => setShowAddDialog(true)}>
          <Plus className="h-4 w-4 mr-1" />
          Add Variable
        </Button>
      </div>
      
      {/* Global Variables */}
      <div>
        <h4 className="text-sm font-medium mb-2">Global Variables</h4>
        <div className="space-y-1">
          {Object.entries(variables.global).map(([key, value]) => (
            <EditableVariableRow
              key={key}
              scope="global"
              varKey={key}
              value={value}
              onUpdate={onUpdateVariable}
              onDelete={onDeleteVariable}
            />
          ))}
        </div>
      </div>

      {/* Collection Variables */}
      {selectedCollection && variables.collections[selectedCollection.id] && (
        <div>
          <h4 className="text-sm font-medium mb-2">Collection Variables ({selectedCollection.name})</h4>
          <div className="space-y-1">
            {Object.entries(variables.collections[selectedCollection.id]).map(([key, value]) => (
              <EditableVariableRow
                key={key}
                scope="collection"
                varKey={key}
                value={value}
                onUpdate={onUpdateVariable}
                onDelete={onDeleteVariable}
              />
            ))}
          </div>
        </div>
      )}

      {/* Add Variable Dialog */}
      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Variable</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Scope</Label>
              <Select value={newVar.scope} onValueChange={(value) => setNewVar(prev => ({ ...prev, scope: value }))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="global">Global</SelectItem>
                  {selectedCollection && (
                    <SelectItem value="collection">Collection ({selectedCollection.name})</SelectItem>
                  )}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Variable Name</Label>
              <Input
                value={newVar.name}
                onChange={(e) => setNewVar(prev => ({ ...prev, name: e.target.value }))}
                placeholder="token"
              />
            </div>
            <div>
              <Label>Value</Label>
              <Input
                value={newVar.value}
                onChange={(e) => setNewVar(prev => ({ ...prev, value: e.target.value }))}
                placeholder="abc123..."
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowAddDialog(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddVariable}>
                Add Variable
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Export Dialog Component
const ExportDialog = ({ collections, trigger }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [exportType, setExportType] = useState('apiforge');
  const [selectedCollections, setSelectedCollections] = useState([]);

  const handleExport = async () => {
    if (selectedCollections.length === 0) {
      toast.error('Please select at least one collection to export');
      return;
    }

    try {
      // Get full collection data with requests
      const collectionsData = [];
      for (const collectionId of selectedCollections) {
        const collection = collections.find(c => c.id === collectionId);
        const requestsResponse = await axios.get(`/requests/${collectionId}`);
        collectionsData.push({
          ...collection,
          requests: requestsResponse.data
        });
      }

      let exportData;
      let filename;
      let mimeType = 'application/json';

      switch (exportType) {
        case 'openapi':
          exportData = generateOpenAPISpec(collectionsData);
          filename = `api-spec-${new Date().toISOString().split('T')[0]}.json`;
          break;
        case 'postman':
          exportData = generatePostmanCollection(collectionsData);
          filename = `postman-collection-${new Date().toISOString().split('T')[0]}.json`;
          break;
        case 'insomnia':
          exportData = generateInsomniaCollection(collectionsData);
          filename = `insomnia-collection-${new Date().toISOString().split('T')[0]}.json`;
          break;
        case 'wsdl':
          exportData = generateWSDLFromSOAP(collectionsData);
          filename = `soap-service-${new Date().toISOString().split('T')[0]}.wsdl`;
          mimeType = 'application/xml';
          break;
        case 'raml':
          exportData = generateRAMLSpec(collectionsData);
          filename = `api-spec-${new Date().toISOString().split('T')[0]}.raml`;
          mimeType = 'application/yaml';
          break;
        case 'graphql':
          exportData = generateGraphQLSchema(collectionsData);
          filename = `schema-${new Date().toISOString().split('T')[0]}.graphql`;
          mimeType = 'text/plain';
          break;
        default: // apiforge
          exportData = {
            version: "1.0",
            timestamp: new Date().toISOString(),
            collections: collectionsData
          };
          filename = `apiforge-collections-${new Date().toISOString().split('T')[0]}.json`;
      }

      const blob = new Blob([typeof exportData === 'string' ? exportData : JSON.stringify(exportData, null, 2)], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast.success(`Exported as ${exportType.toUpperCase()} successfully`);
      setIsOpen(false);
    } catch (error) {
      toast.error('Failed to export collections');
      console.error('Export error:', error);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {trigger}
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Export Collections</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label>Export Format</Label>
            <Select value={exportType} onValueChange={setExportType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="apiforge">APIForge Native (JSON)</SelectItem>
                <SelectItem value="openapi">OpenAPI/Swagger (JSON)</SelectItem>
                <SelectItem value="postman">Postman Collection</SelectItem>
                <SelectItem value="insomnia">Insomnia Collection</SelectItem>
                <SelectItem value="wsdl">WSDL (SOAP Services Only)</SelectItem>
                <SelectItem value="raml">RAML Specification</SelectItem>
                <SelectItem value="graphql">GraphQL Schema</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Select Collections</Label>
            <div className="space-y-2 max-h-48 overflow-y-auto border rounded p-3">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="select-all"
                  checked={selectedCollections.length === collections.length}
                  onChange={(e) => {
                    setSelectedCollections(e.target.checked ? collections.map(c => c.id) : []);
                  }}
                />
                <label htmlFor="select-all" className="text-sm font-medium">Select All</label>
              </div>
              {collections.map(collection => (
                <div key={collection.id} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id={collection.id}
                    checked={selectedCollections.includes(collection.id)}
                    onChange={(e) => {
                      setSelectedCollections(prev =>
                        e.target.checked
                          ? [...prev, collection.id]
                          : prev.filter(id => id !== collection.id)
                      );
                    }}
                  />
                  <label htmlFor={collection.id} className="text-sm">{collection.name}</label>
                </div>
              ))}
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleExport}>
              Export
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Import Dialog Component
const ImportDialog = ({ onImport, trigger }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [importType, setImportType] = useState('postman');
  const [importData, setImportData] = useState('');

  const handleImport = async () => {
    if (!importData.trim()) {
      toast.error('Please enter data to import');
      return;
    }

    try {
      await axios.post('/import', {
        type: importType,
        data: importData
      });
      toast.success('Data imported successfully');
      onImport();
      setIsOpen(false);
      setImportData('');
    } catch (error) {
      toast.error('Failed to import data');
      console.error('Import error:', error);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {trigger}
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Import API Collection</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label>Import Type</Label>
            <Select value={importType} onValueChange={setImportType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="postman">Postman Collection</SelectItem>
                <SelectItem value="openapi">OpenAPI/Swagger</SelectItem>
                <SelectItem value="wsdl">WSDL (SOAP Services)</SelectItem>
                <SelectItem value="raml">RAML API Specification</SelectItem>
                <SelectItem value="graphql">GraphQL Schema</SelectItem>
                <SelectItem value="insomnia">Insomnia Collection</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>
              Paste your {
                importType === 'postman' ? 'Postman Collection JSON' :
                importType === 'openapi' ? 'OpenAPI/Swagger JSON or YAML' :
                importType === 'wsdl' ? 'WSDL XML' :
                importType === 'raml' ? 'RAML YAML' :
                importType === 'graphql' ? 'GraphQL Schema' :
                'Insomnia Collection JSON'
              }
            </Label>
            <Textarea
              value={importData}
              onChange={(e) => setImportData(e.target.value)}
              placeholder={
                importType === 'wsdl' ? 'Paste WSDL XML here...' :
                importType === 'raml' ? 'Paste RAML YAML here...' :
                importType === 'graphql' ? 'Paste GraphQL schema here...' :
                'Paste JSON data here...'
              }
              rows={10}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleImport}>
              Import
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Mobile Sidebar Component  
const MobileSidebar = ({ 
  collections, selectedCollection, setSelectedCollection, 
  requests, selectedRequest, selectRequest, newRequest, 
  createCollection, editCollection, deleteCollection, 
  duplicateRequest, deleteRequest, loadCollections, loadRequests,
  user, logout, theme, toggleTheme, 
  currentView, setCurrentView,
  variables, updateVariable, deleteVariable
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="sm" className="md:hidden">
          <Menu className="h-4 w-4" />
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-80 p-0">
        <div className="flex flex-col h-full">
          {/* Mobile Header */}
          <div className="p-4 border-b">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-xl font-bold">APIForge</h1>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setIsOpen(false)}
                className="text-muted-foreground"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-sm text-muted-foreground">Welcome, {user?.username}!</p>
            
            {/* Mobile Enterprise Navigation */}
            <div className="flex flex-wrap gap-1 mt-3">
              <Button
                variant={currentView === 'api-testing' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => {
                  setCurrentView('api-testing');
                  setIsOpen(false);
                }}
                className="flex items-center gap-2"
              >
                <Zap className="h-4 w-4" />
                API Testing
              </Button>
              <Button
                variant={currentView === 'workflows' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => {
                  setCurrentView('workflows');
                  setIsOpen(false);
                }}
                className="flex items-center gap-2"
              >
                <Activity className="h-4 w-4" />
                Workflows
              </Button>
              <Button
                variant={currentView === 'monitoring' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => {
                  setCurrentView('monitoring');
                  setIsOpen(false);
                }}
                className="flex items-center gap-2"
              >
                <BarChart3 className="h-4 w-4" />
                Monitor
              </Button>
              <Button
                variant={currentView === 'microsoft' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => {
                  setCurrentView('microsoft');
                  setIsOpen(false);
                }}
                className="flex items-center gap-2"
              >
                <Users className="h-4 w-4" />
                Microsoft
              </Button>
              <Button
                variant={currentView === 'gdpr' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => {
                  setCurrentView('gdpr');
                  setIsOpen(false);
                }}
                className="flex items-center gap-2"
              >
                <Shield className="h-4 w-4" />
                GDPR
              </Button>
            </div>
          </div>
          
          {/* Mobile Collections - Only show for API Testing */}
          {currentView === 'api-testing' && (
            <ScrollArea className="flex-1 p-4">
              <div className="mb-6">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-sm font-semibold uppercase tracking-wider">Collections</h2>
                  <div className="flex gap-1">
                    <ImportDialog 
                      onImport={() => { 
                        loadCollections();
                        if (selectedCollection) {
                          loadRequests(selectedCollection.id);
                        }
                      }}
                      trigger={
                        <Button variant="ghost" size="sm" className="h-6 px-2" title="Import Collection">
                          <Upload className="h-3 w-3" />
                        </Button>
                      }
                    />
                    <ExportDialog 
                      collections={collections}
                      trigger={
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-6 px-2" 
                          title="Export Collections"
                        >
                          <Save className="h-3 w-3" />
                        </Button>
                      }
                    />
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-6 px-2" 
                      onClick={createCollection}
                      title="Create Collection"
                    >
                      <Plus className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
                
                <div className="space-y-1">
                  {collections.map(collection => (
                    <div
                      key={collection.id}
                      className={`p-3 rounded-lg cursor-pointer transition-all ${
                        selectedCollection?.id === collection.id
                          ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
                          : 'hover:bg-slate-50 dark:hover:bg-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div 
                          className="flex items-center gap-2 flex-1"
                          onClick={() => {
                            setSelectedCollection(collection);
                          }}
                        >
                          <Folder className="h-4 w-4" />
                          <div>
                            <h3 className="font-medium text-sm">{collection.name}</h3>
                            {collection.description && (
                              <p className="text-xs text-muted-foreground mt-1">{collection.description}</p>
                            )}
                          </div>
                        </div>
                        {/* Mobile: Only export/edit/delete buttons (no import). Desktop: hidden by default, visible on hover */}
                        <div className="flex gap-1">
                          <ExportDialog 
                            collections={[collection]}
                            trigger={
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity"
                                title="Export Collection"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <Save className="h-3 w-3 text-green-500" />
                              </Button>
                            }
                          />
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity"
                            onClick={(e) => {
                              e.stopPropagation();
                              editCollection(collection);
                            }}
                            title="Edit Collection"
                          >
                            <Settings className="h-3 w-3 text-blue-500" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteCollection(collection.id);
                            }}
                            title="Delete Collection"
                          >
                            <X className="h-3 w-3 text-red-500" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Requests Section - Mobile */}
              {selectedCollection && (
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-3">
                    <h2 className="text-sm font-semibold uppercase tracking-wider">
                      Requests ({selectedCollection.name})
                    </h2>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-6 px-2"
                      onClick={() => {
                        newRequest();
                        setIsOpen(false);
                      }}
                      title="New Request"
                    >
                      <Plus className="h-3 w-3" />
                    </Button>
                  </div>
                  
                  <div className="space-y-1">
                    {requests.map(request => (
                      <div
                        key={request.id}
                        className={`p-3 rounded-lg cursor-pointer transition-all ${
                          selectedRequest?.id === request.id
                            ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                            : 'hover:bg-slate-50 dark:hover:bg-slate-700'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div 
                            className="flex items-center gap-2 flex-1"
                            onClick={() => {
                              selectRequest(request);
                              setIsOpen(false);
                            }}
                          >
                            <Badge variant="outline" className="text-xs">
                              {request.protocol === 'REST' ? request.method : request.protocol}
                            </Badge>
                            <span className="text-sm truncate">{request.name}</span>
                          </div>
                          {/* Always visible request action buttons on mobile */}
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-5 w-5 p-0"
                              onClick={(e) => {
                                e.stopPropagation();
                                duplicateRequest(request);
                                setIsOpen(false);
                              }}
                              title="Duplicate Request"
                            >
                              <Plus className="h-2 w-2 text-blue-500" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-5 w-5 p-0"
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteRequest(request.id);
                              }}
                              title="Delete Request"
                            >
                              <X className="h-2 w-2 text-red-500" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                    
                    {requests.length === 0 && (
                      <div className="text-center py-8 text-muted-foreground">
                        <p className="text-sm">No requests in this collection</p>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="mt-2"
                          onClick={() => {
                            newRequest();
                            setIsOpen(false);
                          }}
                        >
                          <Plus className="h-3 w-3 mr-1" />
                          Add Request
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Mobile Variables Panel */}
              <div className="mt-6">
                <VariablesPanel 
                  variables={variables}
                  selectedCollection={selectedCollection}
                  onUpdateVariable={updateVariable}
                  onDeleteVariable={deleteVariable}
                />
              </div>
            </ScrollArea>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
};

// Main Dashboard Component
const Dashboard = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [collections, setCollections] = useState([]);
  const [environments, setEnvironments] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [requests, setRequests] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [activeEnvironment, setActiveEnvironment] = useState(null);
  const [history, setHistory] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [variables, setVariables] = useState({ global: {}, collections: {} });
  
  // Request Builder State
  const [requestBuilder, setRequestBuilder] = useState({
    name: '',
    protocol: 'REST',
    method: 'GET',
    url: '',
    headers: {},
    query_params: {},
    body: '',
    auth: { type: 'none' }
  });
  
  // Response State
  const [response, setResponse] = useState(null);
  const [isExecuting, setIsExecuting] = useState(false);
  
  // Variable extraction rules
  const [extractionRules, setExtractionRules] = useState([]);
  
  // View Management for Enterprise Features
  const [currentView, setCurrentView] = useState('api-testing'); // api-testing, workflows, monitoring, microsoft, gdpr, dashboard
  
  // Dialog states
  const [isNewCollectionDialogOpen, setIsNewCollectionDialogOpen] = useState(false);
  const [newCollectionData, setNewCollectionData] = useState({ name: '', description: '' });
  const [isEditCollectionDialogOpen, setIsEditCollectionDialogOpen] = useState(false);
  const [editingCollection, setEditingCollection] = useState(null);

  useEffect(() => {
    loadCollections();
    loadEnvironments();
    loadHistory();
    loadWorkflows();
    loadVariables();
  }, []);

  useEffect(() => {
    if (selectedCollection) {
      loadRequests(selectedCollection.id);
    }
  }, [selectedCollection]);

  const loadCollections = async () => {
    try {
      const response = await axios.get('/collections');
      setCollections(response.data);
    } catch (error) {
      toast.error('Failed to load collections');
    }
  };

  const loadEnvironments = async () => {
    try {
      const response = await axios.get('/environments');
      setEnvironments(response.data);
      const active = response.data.find(env => env.is_active);
      setActiveEnvironment(active);
    } catch (error) {
      toast.error('Failed to load environments');
    }
  };

  const loadRequests = async (collectionId) => {
    try {
      const response = await axios.get(`/requests/${collectionId}`);
      setRequests(response.data);
    } catch (error) {
      toast.error('Failed to load requests');
    }
  };

  const loadHistory = async () => {
    try {
      const response = await axios.get('/history?limit=10');
      setHistory(response.data);
    } catch (error) {
      console.error('Failed to load history');
    }
  };

  const loadWorkflows = async () => {
    try {
      const response = await axios.get('/workflows');
      setWorkflows(response.data);
    } catch (error) {
      console.error('Failed to load workflows');
    }
  };

  const loadVariables = async () => {
    try {
      const response = await axios.get('/variables');
      setVariables(response.data || { global: {}, collections: {} });
    } catch (error) {
      console.error('Failed to load variables');
      setVariables({ global: {}, collections: {} });
    }
  };

  // Collection Management Functions
  const createCollection = () => {
    setNewCollectionData({ name: '', description: '' });
    setIsNewCollectionDialogOpen(true);
  };

  const handleCreateCollection = async () => {
    if (!newCollectionData.name.trim()) {
      toast.error('Please enter a collection name');
      return;
    }
    
    try {
      await axios.post('/collections', {
        name: newCollectionData.name.trim(),
        description: newCollectionData.description.trim()
      });
      toast.success('Collection created successfully');
      loadCollections();
      setIsNewCollectionDialogOpen(false);
      setNewCollectionData({ name: '', description: '' });
    } catch (error) {
      toast.error('Failed to create collection');
      console.error('Create collection error:', error);
    }
  };

  const editCollection = (collection) => {
    setEditingCollection(collection);
    setNewCollectionData({ 
      name: collection.name, 
      description: collection.description || '' 
    });
    setIsEditCollectionDialogOpen(true);
  };

  const handleUpdateCollection = async () => {
    if (!newCollectionData.name.trim()) {
      toast.error('Please enter a collection name');
      return;
    }
    
    try {
      await axios.put(`/collections/${editingCollection.id}`, {
        name: newCollectionData.name.trim(),
        description: newCollectionData.description.trim()
      });
      toast.success('Collection updated successfully');
      loadCollections();
      setIsEditCollectionDialogOpen(false);
      setEditingCollection(null);
      setNewCollectionData({ name: '', description: '' });
    } catch (error) {
      toast.error('Failed to update collection');
      console.error('Update collection error:', error);
    }
  };

  const deleteCollection = async (collectionId) => {
    if (!window.confirm('Are you sure you want to delete this collection? This will also delete all requests in it.')) {
      return;
    }
    
    try {
      await axios.delete(`/collections/${collectionId}`);
      toast.success('Collection deleted successfully');
      setSelectedCollection(null);
      setRequests([]);
      loadCollections();
    } catch (error) {
      toast.error('Failed to delete collection');
      console.error('Delete collection error:', error);
    }
  };

  // Request Management Functions
  const saveRequest = async () => {
    if (!selectedCollection) {
      toast.error('Please select a collection first');
      return;
    }

    if (!requestBuilder.name || !requestBuilder.url) {
      toast.error('Please enter request name and URL');
      return;
    }

    try {
      const requestData = {
        ...requestBuilder,
        collection_id: selectedCollection.id,
        extraction_rules: extractionRules
      };

      if (selectedRequest) {
        // Update existing request
        await axios.put(`/requests/${selectedRequest.id}`, requestData);
        toast.success('Request updated successfully');
      } else {
        // Create new request
        await axios.post('/requests', requestData);
        toast.success('Request saved successfully');
      }
      
      loadRequests(selectedCollection.id);
    } catch (error) {
      toast.error('Failed to save request');
      console.error('Save request error:', error);
    }
  };

  const deleteRequest = async (requestId) => {
    if (!window.confirm('Are you sure you want to delete this request?')) {
      return;
    }
    
    try {
      await axios.delete(`/requests/${requestId}`);
      toast.success('Request deleted successfully');
      if (selectedRequest?.id === requestId) {
        setSelectedRequest(null);
        newRequest();
      }
      loadRequests(selectedCollection.id);
    } catch (error) {
      toast.error('Failed to delete request');
      console.error('Delete request error:', error);
    }
  };

  const duplicateRequest = (request) => {
    const duplicatedRequest = {
      ...request,
      name: `${request.name} (Copy)`,
      id: undefined // Remove ID so it gets created as new
    };
    setSelectedRequest(null);
    setRequestBuilder(duplicatedRequest);
    toast.success('Request duplicated - modify and save as new');
  };

  // Old exportCollections function removed - replaced with ExportDialog

  // Duplicate functions removed - using enhanced versions above

  const executeRequest = async () => {
    if (!requestBuilder.url) {
      toast.error('Please enter a URL');
      return;
    }
    
    setIsExecuting(true);
    try {
      // Apply variable replacement to request data
      const processedRequest = {
        ...requestBuilder,
        url: replaceVariables(requestBuilder.url),
        body: replaceVariables(requestBuilder.body),
        headers: Object.entries(requestBuilder.headers).reduce((acc, [key, value]) => {
          acc[replaceVariables(key)] = replaceVariables(value);
          return acc;
        }, {}),
        query_params: Object.entries(requestBuilder.query_params).reduce((acc, [key, value]) => {
          acc[replaceVariables(key)] = replaceVariables(value);
          return acc;
        }, {})
      };
      
      const executeResponse = await axios.post('/execute', processedRequest);
      
      setResponse(executeResponse.data);
      
      // Auto-extract variables if rules are defined and response is successful
      if (extractionRules.length > 0 && executeResponse.data.status_code >= 200 && executeResponse.data.status_code < 300) {
        try {
          await axios.post('/variables/extract', {
            response_body: executeResponse.data.body,
            extractions: extractionRules,
            scope: extractionRules[0]?.scope === 'global' ? 'global' : selectedCollection?.id
          });
          
          loadVariables(); // Refresh variables
          toast.success(`Request executed! Extracted ${extractionRules.length} variables.`);
        } catch (error) {
          console.error('Auto-extraction failed:', error);
          toast.success('Request executed successfully!');
        }
      } else {
        toast.success('Request executed successfully!');
      }
      
      loadHistory(); // Refresh history
    } catch (error) {
      const errorResponse = {
        status_code: error.response?.status || 0,
        headers: error.response?.headers || {},
        body: error.response?.data?.detail || error.message,
        response_time: 0,
        protocol: requestBuilder.protocol
      };
      setResponse(errorResponse);
      toast.error('Request failed');
    } finally {
      setIsExecuting(false);
    }
  };

  const selectRequest = (request) => {
    setSelectedRequest(request);
    setRequestBuilder({
      name: request.name,
      protocol: request.protocol || 'REST',
      method: request.method,
      url: request.url,
      headers: request.headers || {},
      query_params: request.query_params || {},
      body: request.body || '',
      auth: request.auth || { type: 'none' }
    });
    setExtractionRules(request.extraction_rules || []);
  };

  const newRequest = () => {
    setSelectedRequest(null);
    setRequestBuilder({
      name: '',
      protocol: 'REST',
      method: 'GET',
      url: '',
      headers: {},
      query_params: {},
      body: '',
      auth: { type: 'none' }
    });
    setExtractionRules([]);
    setResponse(null);
  };

  const formatResponseBody = (body, contentType = '') => {
    try {
      if (contentType.includes('application/json') || (body.trim().startsWith('{') || body.trim().startsWith('['))) {
        return JSON.stringify(JSON.parse(body), null, 2);
      }
      return body;
    } catch {
      return body;
    }
  };

  const getLanguageFromContentType = (contentType = '') => {
    if (contentType.includes('application/json')) return 'json';
    if (contentType.includes('text/xml') || contentType.includes('application/xml')) return 'xml';
    if (contentType.includes('text/html')) return 'html';
    return 'text';
  };

  // Variable replacement function
  const replaceVariables = (text) => {
    if (typeof text !== 'string') return text;
    
    let result = text;
    
    // Replace global variables
    Object.entries(variables.global).forEach(([key, value]) => {
      result = result.replace(new RegExp(`{{${key}}}`, 'g'), value);
    });
    
    // Replace collection variables
    if (selectedCollection && variables.collections[selectedCollection.id]) {
      Object.entries(variables.collections[selectedCollection.id]).forEach(([key, value]) => {
        result = result.replace(new RegExp(`{{${key}}}`, 'g'), value);
      });
    }
    
    return result;
  };

  // Variable extraction function
  const extractVariables = async (responseBody, extractions, scope = 'global') => {
    try {
      await axios.post('/variables/extract', {
        response_body: responseBody,
        extractions: extractions,
        scope: scope === 'global' ? 'global' : selectedCollection?.id
      });
      
      // Reload variables
      loadVariables();
      toast.success(`Variables extracted to ${scope} scope`);
    } catch (error) {
      toast.error('Failed to extract variables');
    }
  };

  // Variable management functions
  const updateVariable = async (scope, key, value) => {
    const newVariables = { ...variables };
    if (scope === 'global') {
      newVariables.global[key] = value;
    } else if (selectedCollection) {
      if (!newVariables.collections[selectedCollection.id]) {
        newVariables.collections[selectedCollection.id] = {};
      }
      newVariables.collections[selectedCollection.id][key] = value;
    }
    
    setVariables(newVariables);
    
    try {
      await axios.put('/variables', newVariables);
    } catch (error) {
      toast.error('Failed to save variables');
    }
  };

  const deleteVariable = async (scope, key) => {
    const newVariables = { ...variables };
    if (scope === 'global') {
      delete newVariables.global[key];
    } else if (selectedCollection && newVariables.collections[selectedCollection.id]) {
      delete newVariables.collections[selectedCollection.id][key];
    }
    
    setVariables(newVariables);
    
    try {
      await axios.put('/variables', newVariables);
    } catch (error) {
      toast.error('Failed to delete variable');
    }
  };

  return (
    <>
    {/* New Collection Dialog */}
    <Dialog open={isNewCollectionDialogOpen} onOpenChange={setIsNewCollectionDialogOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New Collection</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="collection-name">Collection Name *</Label>
            <Input
              id="collection-name"
              value={newCollectionData.name}
              onChange={(e) => setNewCollectionData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Enter collection name"
            />
          </div>
          <div>
            <Label htmlFor="collection-description">Description</Label>
            <Textarea
              id="collection-description"
              value={newCollectionData.description}
              onChange={(e) => setNewCollectionData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Enter collection description (optional)"
              rows={3}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button 
              variant="outline" 
              onClick={() => setIsNewCollectionDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleCreateCollection}>
              Create Collection
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
    
    {/* Edit Collection Dialog */}
    <Dialog open={isEditCollectionDialogOpen} onOpenChange={setIsEditCollectionDialogOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Collection</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="edit-collection-name">Collection Name *</Label>
            <Input
              id="edit-collection-name"
              value={newCollectionData.name}
              onChange={(e) => setNewCollectionData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Enter collection name"
            />
          </div>
          <div>
            <Label htmlFor="edit-collection-description">Description</Label>
            <Textarea
              id="edit-collection-description"
              value={newCollectionData.description}
              onChange={(e) => setNewCollectionData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Enter collection description (optional)"
              rows={3}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button 
              variant="outline" 
              onClick={() => {
                setIsEditCollectionDialogOpen(false);
                setEditingCollection(null);
                setNewCollectionData({ name: '', description: '' });
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleUpdateCollection}>
              Update Collection
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
    
    <div className="h-screen bg-background flex flex-col md:flex-row">
      {/* Desktop Sidebar - Hidden on mobile */}
      <div className="hidden md:flex w-80 bg-card border-r flex-col">
        {/* Header */}
        <div className="p-4 border-b">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-bold">APIForge</h1>
            <div className="flex items-center gap-1">
              <Button variant="ghost" size="sm" onClick={toggleTheme}>
                {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </Button>
              <Button variant="ghost" size="sm" onClick={logout}>
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <p className="text-sm text-muted-foreground">Welcome, {user?.username}!</p>
          
          {/* Navigation Tabs */}
          <div className="flex gap-1 mt-3 overflow-x-auto">
            <Button
              variant={currentView === 'api-testing' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setCurrentView('api-testing')}
              className="flex items-center gap-2 whitespace-nowrap"
            >
              <Zap className="h-4 w-4" />
              API Testing
            </Button>
            <Button
              variant={currentView === 'workflows' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setCurrentView('workflows')}
              className="flex items-center gap-2 whitespace-nowrap"
            >
              <Activity className="h-4 w-4" />
              Workflows
            </Button>
            <Button
              variant={currentView === 'monitoring' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setCurrentView('monitoring')}
              className="flex items-center gap-2 whitespace-nowrap"
            >
              <BarChart3 className="h-4 w-4" />
              Monitoring
            </Button>
            <Button
              variant={currentView === 'microsoft' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setCurrentView('microsoft')}
              className="flex items-center gap-2 whitespace-nowrap"
            >
              <Users className="h-4 w-4" />
              Microsoft
            </Button>
            <Button
              variant={currentView === 'gdpr' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setCurrentView('gdpr')}
              className="flex items-center gap-2 whitespace-nowrap"
            >
              <Shield className="h-4 w-4" />
              GDPR
            </Button>
          </div>
        </div>
        
        {/* Conditional Sidebar Content */}
        <ScrollArea className="flex-1 p-4">
          {currentView === 'api-testing' && (
            <div>
              <div className="mb-6">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-sm font-semibold uppercase tracking-wider">Collections</h2>
                  <div className="flex gap-1">
                    <ImportDialog 
                      onImport={() => { loadCollections(); if(selectedCollection) loadRequests(selectedCollection.id); }}
                      trigger={
                        <Button variant="ghost" size="sm" className="h-6 px-2" title="Import Collection">
                          <Upload className="h-3 w-3" />
                        </Button>
                      }
                    />
                    <ExportDialog 
                      collections={collections}
                      trigger={
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-6 px-2" 
                          title="Export Collections"
                        >
                          <Save className="h-3 w-3" />
                        </Button>
                      }
                    />
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-6 px-2" 
                      onClick={createCollection}
                  data-testid="create-collection-btn"
                  title="Create New Collection"
                >
                  <Plus className="h-3 w-3" />
                </Button>
              </div>
            </div>
            
            <div className="space-y-1">
              {collections.map(collection => (
                <div
                  key={collection.id}
                  onClick={() => setSelectedCollection(collection)}
                  className={`p-3 rounded-lg cursor-pointer transition-all ${
                    selectedCollection?.id === collection.id
                      ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
                      : 'hover:bg-slate-50 dark:hover:bg-slate-700'
                  }`}
                  data-testid={`collection-${collection.id}`}
                >
                  <div className="flex items-center justify-between group">
                    <div className="flex items-center gap-2">
                      <Folder className="h-4 w-4" />
                      <div>
                        <h3 className="font-medium text-sm">{collection.name}</h3>
                        {collection.description && (
                          <p className="text-xs text-muted-foreground mt-1">{collection.description}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <ExportDialog 
                        collections={[collection]}
                        trigger={
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 opacity-100 transition-opacity"
                            title="Export Collection"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <Save className="h-3 w-3 text-green-500" />
                          </Button>
                        }
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 opacity-100 transition-opacity"
                        onClick={(e) => {
                          e.stopPropagation();
                          editCollection(collection);
                        }}
                        title="Edit Collection"
                      >
                        <Settings className="h-3 w-3 text-blue-500" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 opacity-100 transition-opacity"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteCollection(collection.id);
                        }}
                        title="Delete Collection"
                      >
                        <X className="h-3 w-3 text-red-500" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Requests in selected collection */}
          {selectedCollection && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold uppercase tracking-wider">Requests</h2>
                <Button variant="ghost" size="sm" className="h-6 px-2" onClick={newRequest}>
                  <Plus className="h-3 w-3" />
                </Button>
              </div>
              
              <div className="space-y-1">
                {requests.length === 0 ? (
                  <div className="text-center py-4 text-muted-foreground">
                    <p className="text-sm">No requests yet</p>
                    <p className="text-xs mt-1">Click + to create your first request</p>
                  </div>
                ) : (
                  requests.map(request => (
                    <div
                      key={request.id}
                      onClick={() => selectRequest(request)}
                      className={`p-2 rounded-md cursor-pointer transition-all ${
                        selectedRequest?.id === request.id
                          ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                          : 'hover:bg-slate-50 dark:hover:bg-slate-700'
                      }`}
                      data-testid={`request-${request.id}`}
                    >
                      <div className="flex items-center justify-between group">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {request.protocol === 'REST' ? request.method : request.protocol}
                          </Badge>
                          <span className="text-sm truncate">{request.name}</span>
                        </div>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-5 w-5 p-0 opacity-100 transition-opacity"
                            onClick={(e) => {
                              e.stopPropagation();
                              duplicateRequest(request);
                            }}
                            title="Duplicate Request"
                          >
                            <Plus className="h-2 w-2 text-blue-500" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-5 w-5 p-0 opacity-100 transition-opacity"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteRequest(request.id);
                            }}
                            title="Delete Request"
                          >
                            <X className="h-2 w-2 text-red-500" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
          
          {/* Variables Panel */}
          <div className="mt-6">
            <VariablesPanel 
              variables={variables}
              selectedCollection={selectedCollection}
              onUpdateVariable={updateVariable}
              onDeleteVariable={deleteVariable}
            />
          </div>
          </div>
          )}
          
          {/* Enterprise Features Sidebar Content */}
          {currentView !== 'api-testing' && (
            <div className="space-y-4">
              <div>
                <h2 className="text-sm font-semibold uppercase tracking-wider mb-3">
                  {currentView === 'workflows' && 'Workflow Designer'}
                  {currentView === 'monitoring' && 'API Monitoring'}
                  {currentView === 'microsoft' && 'Microsoft Integration'}
                  {currentView === 'gdpr' && 'GDPR Compliance'}
                </h2>
                <p className="text-xs text-muted-foreground">
                  {currentView === 'workflows' && 'Create and manage automated API workflows with drag-and-drop designer.'}
                  {currentView === 'monitoring' && 'Monitor your API performance, set up alerts, and track metrics.'}
                  {currentView === 'microsoft' && 'Connect and integrate with Microsoft services and Azure APIs.'}
                  {currentView === 'gdpr' && 'Manage your data privacy rights and compliance settings.'}
                </p>
              </div>
            </div>
          )}
        </ScrollArea>
      </div>
      
      {/* Mobile Header - Always visible on mobile */}
      <div className="md:hidden bg-card border-b p-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <MobileSidebar 
            collections={collections}
            selectedCollection={selectedCollection}
            setSelectedCollection={setSelectedCollection}
            requests={requests}
            selectedRequest={selectedRequest}
            selectRequest={selectRequest}
            newRequest={newRequest}
            createCollection={createCollection}
            editCollection={editCollection}
            deleteCollection={deleteCollection}
            duplicateRequest={duplicateRequest}
            deleteRequest={deleteRequest}
            loadCollections={loadCollections}
            loadRequests={loadRequests}
            user={user}
            logout={logout}
            theme={theme}
            toggleTheme={toggleTheme}
            currentView={currentView}
            setCurrentView={setCurrentView}
            variables={variables}
            updateVariable={updateVariable}
            deleteVariable={deleteVariable}
          />
          <h1 className="text-lg font-semibold">
            {currentView === 'api-testing' && 'API Testing'}
            {currentView === 'workflows' && 'Workflows'}
            {currentView === 'monitoring' && 'Monitoring'}
            {currentView === 'microsoft' && 'Microsoft Integration'}
            {currentView === 'gdpr' && 'GDPR Compliance'}
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={toggleTheme}>
            {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
          <Button variant="ghost" size="sm" onClick={logout}>
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {currentView === 'api-testing' ? (
          // Original API Testing Interface
          <>
        {/* Top Bar */}
        <div className="h-14 bg-card border-b flex items-center justify-between px-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedCollection(null)}
                className="text-xs"
              >
                All Collections
              </Button>
              {selectedCollection && (
                <>
                  <span className="text-xs text-muted-foreground">/</span>
                  <span className="text-xs font-medium">{selectedCollection.name}</span>
                </>
              )}
            </div>
            {requestBuilder.protocol && (
              <Badge variant="secondary" className="hidden sm:inline-flex">
                {requestBuilder.protocol}
              </Badge>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {activeEnvironment && (
              <Badge variant="outline" className="bg-green-50 border-green-200 text-green-700 hidden sm:inline-flex">
                {activeEnvironment.name}
              </Badge>
            )}
            
            <Button
              onClick={executeRequest}
              disabled={isExecuting || !requestBuilder.url}
              size="sm"
              data-testid="execute-request-btn"
            >
              <Play className="h-3 w-3 mr-1" />
              {isExecuting ? 'Sending...' : 'Send'}
            </Button>
            
            {selectedCollection && (
              <Button
                variant="outline"
                size="sm"
                onClick={saveRequest}
                data-testid="save-request-btn"
              >
                <Save className="h-3 w-3 mr-1" />
                Save
              </Button>
            )}
          </div>
        </div>
        
        {/* Request Builder and Response */}
        <div className="flex-1 flex flex-col xl:flex-row min-h-0">
          {/* Request Builder */}
          <div className="flex-1 bg-card border-b xl:border-b-0 xl:border-r overflow-y-auto">
            <div className="p-3 sm:p-4 space-y-3 sm:space-y-4">
              <div className="flex items-center justify-between gap-2 mb-4">
                <h3 className="text-lg font-semibold">Request</h3>
                <ExtractionRulesManager 
                  rules={extractionRules}
                  onUpdate={setExtractionRules}
                  selectedCollection={selectedCollection}
                />
              </div>
              
              {/* Protocol and Basic Info - Mobile Responsive */}
              <div className="space-y-3 sm:space-y-0 sm:grid sm:grid-cols-2 lg:grid-cols-4 sm:gap-3">
                <div>
                  <Label className="text-sm">Protocol</Label>
                  <Select
                    value={requestBuilder.protocol}
                    onValueChange={(value) => setRequestBuilder(prev => ({ ...prev, protocol: value }))}
                  >
                    <SelectTrigger className="h-8">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="REST">REST</SelectItem>
                      <SelectItem value="SOAP">SOAP</SelectItem>
                      <SelectItem value="GraphQL">GraphQL</SelectItem>
                      <SelectItem value="gRPC">gRPC</SelectItem>
                      <SelectItem value="WebSocket">WebSocket</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label className="text-sm">Name</Label>
                  <Input
                    value={requestBuilder.name}
                    onChange={(e) => setRequestBuilder(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Request name"
                    className="h-8"
                    data-testid="request-name-input"
                  />
                </div>
                
                {requestBuilder.protocol === 'REST' && (
                  <div>
                    <Label className="text-sm">Method</Label>
                    <Select
                      value={requestBuilder.method}
                      onValueChange={(value) => setRequestBuilder(prev => ({ ...prev, method: value }))}
                    >
                      <SelectTrigger className="h-8" data-testid="request-method-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="GET">GET</SelectItem>
                        <SelectItem value="POST">POST</SelectItem>
                        <SelectItem value="PUT">PUT</SelectItem>
                        <SelectItem value="DELETE">DELETE</SelectItem>
                        <SelectItem value="PATCH">PATCH</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}
                
                <div className={`${requestBuilder.protocol === 'REST' ? 'col-span-1' : 'sm:col-span-2'} ${requestBuilder.protocol !== 'REST' ? 'lg:col-span-2' : ''}`}>
                  <Label className="text-sm">URL</Label>
                  <Input
                    value={requestBuilder.url}
                    onChange={(e) => setRequestBuilder(prev => ({ ...prev, url: e.target.value }))}
                    placeholder="https://api.example.com/endpoint"
                    className="h-8"
                    data-testid="request-url-input"
                  />
                </div>
              </div>
              
              {/* SOAP-specific fields */}
              {requestBuilder.protocol === 'SOAP' && (
                <div className="space-y-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border">
                  <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100">SOAP Configuration</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <Label className="text-xs">SOAP Action</Label>
                      <Input
                        value={requestBuilder.soapAction || ''}
                        onChange={(e) => setRequestBuilder(prev => ({ ...prev, soapAction: e.target.value }))}
                        placeholder="http://example.com/MyAction"
                        className="h-8"
                      />
                    </div>
                    <div>
                      <Label className="text-xs">SOAP Version</Label>
                      <Select
                        value={requestBuilder.soapVersion || '1.1'}
                        onValueChange={(value) => setRequestBuilder(prev => ({ ...prev, soapVersion: value }))}
                      >
                        <SelectTrigger className="h-8">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1.1">SOAP 1.1</SelectItem>
                          <SelectItem value="1.2">SOAP 1.2</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>
              )}

              {/* GraphQL-specific fields */}
              {requestBuilder.protocol === 'GraphQL' && (
                <div className="space-y-3 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border">
                  <h4 className="text-sm font-semibold text-purple-900 dark:text-purple-100">GraphQL Configuration</h4>
                  <div>
                    <Label className="text-xs">Operation Type</Label>
                    <Select
                      value={requestBuilder.graphqlOperation || 'query'}
                      onValueChange={(value) => setRequestBuilder(prev => ({ ...prev, graphqlOperation: value }))}
                    >
                      <SelectTrigger className="h-8">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="query">Query</SelectItem>
                        <SelectItem value="mutation">Mutation</SelectItem>
                        <SelectItem value="subscription">Subscription</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}

              {/* Tabs for different request parts - Horizontal Scroll */}
              <Tabs defaultValue={requestBuilder.protocol === 'GraphQL' ? 'body' : requestBuilder.protocol === 'SOAP' ? 'envelope' : 'headers'} className="w-full">
                <div className="w-full overflow-x-auto">
                  <TabsList className="flex h-8 w-max min-w-full">
                    {requestBuilder.protocol === 'REST' && (
                      <TabsTrigger value="params" className="text-xs px-3 flex-shrink-0">
                        Params
                      </TabsTrigger>
                    )}
                    {requestBuilder.protocol === 'SOAP' && (
                      <TabsTrigger value="envelope" className="text-xs px-3 flex-shrink-0">
                        SOAP Envelope
                      </TabsTrigger>
                    )}
                    {requestBuilder.protocol === 'GraphQL' && (
                      <TabsTrigger value="query" className="text-xs px-3 flex-shrink-0">
                        GraphQL Query
                      </TabsTrigger>
                    )}
                    {requestBuilder.protocol === 'GraphQL' && (
                      <TabsTrigger value="variables" className="text-xs px-3 flex-shrink-0">
                        Variables
                      </TabsTrigger>
                    )}
                    <TabsTrigger value="headers" className="text-xs px-3 flex-shrink-0">
                      Headers
                    </TabsTrigger>
                    <TabsTrigger value="auth" className="text-xs px-3 flex-shrink-0">
                      Auth
                    </TabsTrigger>
                    <TabsTrigger value="body" className="text-xs px-3 flex-shrink-0">
                      Body
                    </TabsTrigger>
                    <TabsTrigger value="history" className="text-xs px-3 flex-shrink-0">
                      History
                    </TabsTrigger>
                    <TabsTrigger value="tests" className="text-xs px-3 flex-shrink-0">
                      Tests
                    </TabsTrigger>
                    <TabsTrigger value="monitoring" className="text-xs px-3 flex-shrink-0">
                      Monitor
                    </TabsTrigger>
                  </TabsList>
                </div>
                
                {requestBuilder.protocol === 'REST' && (
                  <TabsContent value="params" className="mt-4">
                    <KeyValueEditor
                      data={requestBuilder.query_params}
                      onChange={(params) => setRequestBuilder(prev => ({ ...prev, query_params: params }))}
                      placeholder="Add query parameter"
                    />
                  </TabsContent>
                )}
                
                {/* SOAP Envelope Tab */}
                {requestBuilder.protocol === 'SOAP' && (
                  <TabsContent value="envelope" className="mt-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-medium">SOAP Envelope</h4>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            const sampleEnvelope = `<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <!-- Your SOAP operation here -->
  </soap:Body>
</soap:Envelope>`;
                            setRequestBuilder(prev => ({ ...prev, body: sampleEnvelope }));
                          }}
                        >
                          Generate Template
                        </Button>
                      </div>
                      <Textarea
                        value={requestBuilder.body || ''}
                        onChange={(e) => setRequestBuilder(prev => ({ ...prev, body: e.target.value }))}
                        placeholder="Enter SOAP envelope XML..."
                        className="font-mono text-xs"
                        rows={12}
                      />
                    </div>
                  </TabsContent>
                )}

                {/* GraphQL Query Tab */}
                {requestBuilder.protocol === 'GraphQL' && (
                  <TabsContent value="query" className="mt-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-medium">GraphQL {requestBuilder.graphqlOperation || 'Query'}</h4>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            const sampleQuery = requestBuilder.graphqlOperation === 'mutation' 
                              ? `mutation {\n  createUser(input: {\n    name: "John Doe"\n    email: "john@example.com"\n  }) {\n    id\n    name\n    email\n  }\n}`
                              : `query {\n  users {\n    id\n    name\n    email\n    createdAt\n  }\n}`;
                            setRequestBuilder(prev => ({ ...prev, body: sampleQuery }));
                          }}
                        >
                          Generate Sample
                        </Button>
                      </div>
                      <Textarea
                        value={requestBuilder.body || ''}
                        onChange={(e) => setRequestBuilder(prev => ({ ...prev, body: e.target.value }))}
                        placeholder="Enter GraphQL query..."
                        className="font-mono text-xs"
                        rows={12}
                      />
                    </div>
                  </TabsContent>
                )}

                {/* GraphQL Variables Tab */}
                {requestBuilder.protocol === 'GraphQL' && (
                  <TabsContent value="variables" className="mt-4">
                    <div className="space-y-3">
                      <h4 className="text-sm font-medium">Query Variables (JSON)</h4>
                      <Textarea
                        value={requestBuilder.graphqlVariables || ''}
                        onChange={(e) => setRequestBuilder(prev => ({ ...prev, graphqlVariables: e.target.value }))}
                        placeholder='{\n  "userId": 123,\n  "name": "John Doe"\n}'
                        className="font-mono text-xs"
                        rows={8}
                      />
                    </div>
                  </TabsContent>
                )}
                
                <TabsContent value="headers" className="mt-4">
                  <KeyValueEditor
                    data={requestBuilder.headers}
                    onChange={(headers) => setRequestBuilder(prev => ({ ...prev, headers }))}
                    placeholder="Add header"
                  />
                </TabsContent>
                
                <TabsContent value="auth" className="mt-4">
                  <AuthEditor
                    auth={requestBuilder.auth}
                    onChange={(auth) => setRequestBuilder(prev => ({ ...prev, auth }))}
                  />
                </TabsContent>
                
                <TabsContent value="body" className="mt-4">
                  <div>
                    <Label className="text-sm">Body</Label>
                    <Textarea
                      value={requestBuilder.body}
                      onChange={(e) => setRequestBuilder(prev => ({ ...prev, body: e.target.value }))}
                      className="h-48 font-mono text-sm mt-2"
                      placeholder={
                        requestBuilder.protocol === 'GraphQL' 
                          ? 'query { users { id name email } }'
                          : requestBuilder.protocol === 'SOAP'
                          ? '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">\n  <soapenv:Body>\n    <!-- Your SOAP operation -->\n  </soapenv:Body>\n</soapenv:Envelope>'
                          : 'Request body (JSON, XML, etc.)'
                      }
                      data-testid="request-body-textarea"
                    />
                  </div>
                </TabsContent>
                
                <TabsContent value="history" className="mt-4">
                  <ScrollArea className="h-48">
                    {history.length === 0 ? (
                      <div className="text-center text-muted-foreground py-8">
                        <p className="text-sm">No request history yet</p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {history.map((item, index) => (
                          <div
                            key={index}
                            className="p-3 rounded border cursor-pointer hover:bg-muted/50"
                            onClick={() => {
                              setRequestBuilder({
                                name: item.request.name || `History ${index + 1}`,
                                protocol: item.request.protocol,
                                method: item.request.method,
                                url: item.request.url,
                                headers: item.request.headers || {},
                                query_params: item.request.query_params || {},
                                body: item.request.body || '',
                                auth: item.request.auth || { type: 'none' }
                              });
                              setResponse(item.response);
                            }}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <Badge variant="outline" className="text-xs">
                                  {item.request.protocol === 'REST' ? item.request.method : item.request.protocol}
                                </Badge>
                                <span className="text-sm truncate">
                                  {item.request.url}
                                </span>
                              </div>
                              <Badge
                                variant={item.response.status_code < 400 ? "default" : "destructive"}
                                className="text-xs"
                              >
                                {item.response.status_code}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </ScrollArea>
                </TabsContent>
                
                <TabsContent value="tests" className="mt-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Label className="text-sm font-medium">Test Scripts</Label>
                      <Button variant="outline" size="sm" className="h-7">
                        <Plus className="h-3 w-3 mr-1" />
                        Add Test
                      </Button>
                    </div>
                    <Textarea
                      placeholder="// Example test script
// pm.test('Status code is 200', function () {
//     pm.response.to.have.status(200);
// });
//
// pm.test('Response time is less than 500ms', function () {
//     pm.expect(pm.response.responseTime).to.be.below(500);
// });"
                      className="h-32 font-mono text-xs"
                    />
                    <div className="text-xs text-muted-foreground">
                      Write test scripts using Postman-compatible syntax for automated testing.
                    </div>
                  </div>
                </TabsContent>
                
                <TabsContent value="monitoring" className="mt-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Label className="text-sm font-medium">Monitoring & Alerts</Label>
                      <Button variant="outline" size="sm" className="h-7">
                        Configure
                      </Button>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 rounded border">
                        <div className="text-sm font-medium">Response Time</div>
                        <div className="text-xs text-muted-foreground mt-1">Monitor API performance</div>
                        <div className="flex items-center gap-2 mt-2">
                          <Input placeholder="< 500ms" className="h-7 text-xs" />
                          <Badge variant="outline">Alert</Badge>
                        </div>
                      </div>
                      <div className="p-3 rounded border">
                        <div className="text-sm font-medium">Uptime Monitor</div>
                        <div className="text-xs text-muted-foreground mt-1">Check every 5 minutes</div>
                        <div className="flex items-center gap-2 mt-2">
                          <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                          <span className="text-xs">99.9% uptime</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Set up monitoring rules and get alerts for API failures, performance issues, or downtime.
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          </div>
          
          {/* Response */}
          <div className="flex-1 bg-muted/20 overflow-y-auto">
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Response</h3>
                {response && response.status_code >= 200 && response.status_code < 300 && (
                  <VariableExtractionDialog 
                    responseBody={response.body}
                    trigger={
                      <Button variant="outline" size="sm">
                        <Settings className="h-4 w-4 mr-1" />
                        Extract Variables
                      </Button>
                    }
                  />
                )}
              </div>
              
              {response ? (
                <div className="space-y-4">
                  {/* Status and timing */}
                  <div className="flex items-center gap-4">
                    <Badge
                      variant={response.status_code >= 200 && response.status_code < 300 ? "default" : "destructive"}
                    >
                      {response.status_code}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      {response.response_time}s
                    </span>
                    <Badge variant="outline">
                      {response.protocol}
                    </Badge>
                  </div>
                  
                  {/* Response Headers */}
                  {Object.keys(response.headers).length > 0 && (
                    <div>
                      <Label className="text-sm font-medium mb-2 block">Headers</Label>
                      <Card>
                        <CardContent className="p-3 text-xs font-mono">
                          {Object.entries(response.headers).map(([key, value]) => (
                            <div key={key} className="flex">
                              <span className="text-muted-foreground w-32 shrink-0">{key}:</span>
                              <span className="break-all">{value}</span>
                            </div>
                          ))}
                        </CardContent>
                      </Card>
                    </div>
                  )}
                  
                  {/* Response body */}
                  <div>
                    <Label className="text-sm font-medium mb-2 block">Response Body</Label>
                    <Card>
                      <CardContent className="p-0 overflow-hidden">
                        <SyntaxHighlighter
                          language={getLanguageFromContentType(response.headers['content-type'])}
                          style={theme === 'dark' ? vscDarkPlus : vs}
                          customStyle={{
                            margin: 0,
                            borderRadius: 0,
                            background: 'transparent',
                            fontSize: '12px',
                            maxHeight: '400px'
                          }}
                          showLineNumbers
                        >
                          {formatResponseBody(response.body, response.headers['content-type'])}
                        </SyntaxHighlighter>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-32 text-muted-foreground">
                  <p>No response yet. Click "Send" to execute a request.</p>
                </div>
              )}
            </div>
          </div>
        </div>
        </> 
        ) : currentView === 'workflows' ? (
          <div className="p-6">
            <WorkflowDesigner 
              workflows={workflows} 
              onWorkflowCreate={async (workflowData) => {
                try {
                  await axios.post('/workflows', workflowData);
                  toast.success('Workflow created successfully');
                  loadWorkflows(); // Reload workflows after creating
                } catch (error) {
                  toast.error('Failed to create workflow');
                }
              }}
              onWorkflowExecute={async (workflowId) => {
                try {
                  await axios.post(`/workflows/${workflowId}/execute`);
                  toast.success('Workflow executed successfully');
                } catch (error) {
                  toast.error('Failed to execute workflow');
                }
              }}
            />
          </div>
        ) : currentView === 'monitoring' ? (
          <div className="p-6">
            <MonitoringPanel requests={requests} />
          </div>
        ) : currentView === 'microsoft' ? (
          <div className="p-6">
            <MicrosoftIntegration />
          </div>
        ) : currentView === 'gdpr' ? (
          <div className="p-6">
            <GDPRCompliance user={user} />
          </div>
        ) : null}
      </div>
    </div>
    
    {/* New Collection Dialog */}
    <Dialog open={isNewCollectionDialogOpen} onOpenChange={setIsNewCollectionDialogOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New Collection</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="collection-name">Collection Name *</Label>
            <Input
              id="collection-name"
              value={newCollectionData.name}
              onChange={(e) => setNewCollectionData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Enter collection name"
            />
          </div>
          <div>
            <Label htmlFor="collection-description">Description</Label>
            <Textarea
              id="collection-description"
              value={newCollectionData.description}
              onChange={(e) => setNewCollectionData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Enter collection description (optional)"
              rows={3}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button 
              variant="outline" 
              onClick={() => setIsNewCollectionDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleCreateCollection}>
              Create Collection
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
    </>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }
  
  return user ? children : <Navigate to="/auth" replace />;
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}

function AppContent() {
  const { theme } = useTheme();
  
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/auth" element={<AuthForm />} />
          <Route path="/" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors theme={theme} />
    </div>
  );
}

export default App;