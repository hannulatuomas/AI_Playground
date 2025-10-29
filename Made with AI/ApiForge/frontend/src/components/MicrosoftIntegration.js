import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Plus, Settings, CheckCircle, AlertCircle, Users, Mail, Calendar, FileText } from 'lucide-react';
import axios from 'axios';

const MicrosoftIntegration = () => {
  const [services, setServices] = useState([]);
  const [isAddingService, setIsAddingService] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAzureServices();
  }, []);

  const loadAzureServices = async () => {
    try {
      const response = await axios.get('/microsoft/services');
      setServices(response.data);
    } catch (error) {
      console.error('Failed to load Azure services:', error);
    } finally {
      setLoading(false);
    }
  };

  const addAzureService = async (serviceData) => {
    try {
      await axios.post('/microsoft/services', serviceData);
      loadAzureServices();
      setIsAddingService(false);
    } catch (error) {
      console.error('Failed to add Azure service:', error);
    }
  };

  const ServiceCard = ({ service }) => {
    const getServiceIcon = (type) => {
      switch (type) {
        case 'graph': return <Users className="h-6 w-6" />;
        case 'mail': return <Mail className="h-6 w-6" />;
        case 'calendar': return <Calendar className="h-6 w-6" />;
        case 'storage': return <FileText className="h-6 w-6" />;
        default: return <Settings className="h-6 w-6" />;
      }
    };

    const getServiceColor = (type) => {
      switch (type) {
        case 'graph': return 'bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400';
        case 'mail': return 'bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400';
        case 'calendar': return 'bg-purple-100 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400';
        case 'storage': return 'bg-orange-100 text-orange-600 dark:bg-orange-900/20 dark:text-orange-400';
        default: return 'bg-gray-100 text-gray-600 dark:bg-gray-900/20 dark:text-gray-400';
      }
    };

    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${getServiceColor(service.service_type)}`}>
                {getServiceIcon(service.service_type)}
              </div>
              <div>
                <CardTitle className="text-lg">{service.name}</CardTitle>
                <p className="text-sm text-muted-foreground">{service.service_type.toUpperCase()}</p>
              </div>
            </div>
            <Badge variant="outline">
              <CheckCircle className="h-3 w-3 mr-1 text-green-500" />
              Connected
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="text-sm font-medium text-muted-foreground">Endpoint</div>
            <div className="text-sm font-mono bg-muted p-2 rounded truncate">
              {service.endpoint}
            </div>
          </div>
          
          <div>
            <div className="text-sm font-medium text-muted-foreground">Tenant ID</div>
            <div className="text-sm font-mono">
              {service.auth_config?.tenant_id?.substring(0, 8)}...****
            </div>
          </div>
          
          <div className="flex justify-between items-center pt-2">
            <div className="text-xs text-muted-foreground">
              Added {new Date(service.created_at).toLocaleDateString()}
            </div>
            <Button variant="ghost" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  const AddServiceDialog = () => {
    const [formData, setFormData] = useState({
      name: '',
      service_type: 'graph',
      endpoint: 'https://graph.microsoft.com/v1.0',
      auth_config: {
        tenant_id: '',
        client_id: '',
        client_secret: '',
        scope: ['https://graph.microsoft.com/.default']
      }
    });

    const serviceTypes = [
      { value: 'graph', label: 'Microsoft Graph', endpoint: 'https://graph.microsoft.com/v1.0' },
      { value: 'storage', label: 'Azure Storage', endpoint: 'https://storage.azure.com' },
      { value: 'keyvault', label: 'Azure Key Vault', endpoint: 'https://vault.azure.net' },
      { value: 'functions', label: 'Azure Functions', endpoint: 'https://functions.azure.com' }
    ];

    const handleServiceTypeChange = (type) => {
      const serviceType = serviceTypes.find(st => st.value === type);
      setFormData(prev => ({
        ...prev,
        service_type: type,
        endpoint: serviceType?.endpoint || ''
      }));
    };

    const handleSubmit = (e) => {
      e.preventDefault();
      if (formData.name && formData.auth_config.tenant_id && formData.auth_config.client_id) {
        addAzureService(formData);
      }
    };

    return (
      <Dialog open={isAddingService} onOpenChange={setIsAddingService}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add Microsoft Service</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Service Name</Label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="My Microsoft Service"
                />
              </div>
              
              <div>
                <Label>Service Type</Label>
                <Select 
                  value={formData.service_type} 
                  onValueChange={handleServiceTypeChange}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {serviceTypes.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <Label>Endpoint URL</Label>
              <Input
                value={formData.endpoint}
                onChange={(e) => setFormData(prev => ({ ...prev, endpoint: e.target.value }))}
                placeholder="https://graph.microsoft.com/v1.0"
              />
            </div>
            
            <div className="space-y-3">
              <h4 className="font-medium">Authentication Configuration</h4>
              
              <div>
                <Label>Tenant ID</Label>
                <Input
                  value={formData.auth_config.tenant_id}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    auth_config: { ...prev.auth_config, tenant_id: e.target.value }
                  }))}
                  placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                />
              </div>
              
              <div>
                <Label>Client ID (Application ID)</Label>
                <Input
                  value={formData.auth_config.client_id}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    auth_config: { ...prev.auth_config, client_id: e.target.value }
                  }))}
                  placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                />
              </div>
              
              <div>
                <Label>Client Secret</Label>
                <Input
                  type="password"
                  value={formData.auth_config.client_secret}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    auth_config: { ...prev.auth_config, client_secret: e.target.value }
                  }))}
                  placeholder="Enter client secret"
                />
              </div>
            </div>
            
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-blue-800 dark:text-blue-200">Azure App Registration Required</p>
                  <p className="text-blue-700 dark:text-blue-300 mt-1">
                    You need to register an application in Azure AD and configure the appropriate API permissions.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => setIsAddingService(false)}>
                Cancel
              </Button>
              <Button type="submit">
                Add Service
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    );
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-1/3 mb-2"></div>
          <div className="h-4 bg-muted rounded w-1/2"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse space-y-3">
                  <div className="h-6 bg-muted rounded w-3/4"></div>
                  <div className="h-4 bg-muted rounded w-1/2"></div>
                  <div className="h-4 bg-muted rounded w-full"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <div className="w-4 h-4 bg-white rounded-sm"></div>
            </div>
            Microsoft Integration
          </h2>
          <p className="text-muted-foreground">Connect and manage Microsoft services and APIs</p>
        </div>
        <Button onClick={() => setIsAddingService(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Service
        </Button>
      </div>

      {/* Quick Setup Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="cursor-pointer hover:bg-muted/50 transition-colors">
          <CardContent className="p-4 text-center">
            <Users className="h-8 w-8 mx-auto mb-2 text-blue-600" />
            <div className="font-medium">Microsoft Graph</div>
            <div className="text-xs text-muted-foreground">Users, Groups, Mail</div>
          </CardContent>
        </Card>
        
        <Card className="cursor-pointer hover:bg-muted/50 transition-colors">
          <CardContent className="p-4 text-center">
            <FileText className="h-8 w-8 mx-auto mb-2 text-orange-600" />
            <div className="font-medium">Azure Storage</div>
            <div className="text-xs text-muted-foreground">Blob, Queue, Table</div>
          </CardContent>
        </Card>
        
        <Card className="cursor-pointer hover:bg-muted/50 transition-colors">
          <CardContent className="p-4 text-center">
            <Settings className="h-8 w-8 mx-auto mb-2 text-purple-600" />
            <div className="font-medium">Azure Functions</div>
            <div className="text-xs text-muted-foreground">Serverless Computing</div>
          </CardContent>
        </Card>
        
        <Card className="cursor-pointer hover:bg-muted/50 transition-colors">
          <CardContent className="p-4 text-center">
            <AlertCircle className="h-8 w-8 mx-auto mb-2 text-green-600" />
            <div className="font-medium">Key Vault</div>
            <div className="text-xs text-muted-foreground">Secrets Management</div>
          </CardContent>
        </Card>
      </div>

      {/* Connected Services */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Connected Services</h3>
        {services.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <div className="w-8 h-8 bg-white rounded-sm"></div>
              </div>
              <h3 className="text-lg font-semibold mb-2">No Microsoft services connected yet</h3>
              <p className="text-muted-foreground mb-4">
                Connect your Microsoft services to enable enterprise-grade API integrations
              </p>
              <Button onClick={() => setIsAddingService(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Connect Your First Service
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {services.map(service => (
              <ServiceCard key={service.id} service={service} />
            ))}
          </div>
        )}
      </div>

      {/* Microsoft Graph Quick Actions */}
      {services.some(s => s.service_type === 'graph') && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Microsoft Graph Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
                <Users className="h-6 w-6" />
                <span>Get Users</span>
              </Button>
              
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
                <Mail className="h-6 w-6" />
                <span>Send Email</span>
              </Button>
              
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
                <Calendar className="h-6 w-6" />
                <span>Create Event</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <AddServiceDialog />
    </div>
  );
};

export default MicrosoftIntegration;