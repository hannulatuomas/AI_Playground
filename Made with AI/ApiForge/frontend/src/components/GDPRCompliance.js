import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Checkbox } from './ui/checkbox';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Alert, AlertDescription } from './ui/alert';
import { Shield, Download, Trash2, Eye, CheckCircle, AlertTriangle, Globe, Clock, FileText } from 'lucide-react';
import axios from 'axios';

const GDPRCompliance = ({ user }) => {
  const [auditLogs, setAuditLogs] = useState([]);
  const [exportRequests, setExportRequests] = useState([]);
  const [isRequestingExport, setIsRequestingExport] = useState(false);
  const [selectedDataTypes, setSelectedDataTypes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadComplianceData();
  }, []);

  const loadComplianceData = async () => {
    try {
      const auditResponse = await axios.get('/gdpr/audit-logs');
      setAuditLogs(auditResponse.data);
    } catch (error) {
      console.error('Failed to load compliance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const requestDataExport = async () => {
    if (selectedDataTypes.length === 0) {
      alert('Please select at least one data type to export');
      return;
    }

    try {
      const response = await axios.post('/gdpr/export', selectedDataTypes);
      setIsRequestingExport(false);
      setSelectedDataTypes([]);
      alert('Data export request submitted successfully!');
    } catch (error) {
      console.error('Failed to request data export:', error);
      alert('Failed to submit export request');
    }
  };

  const deleteAccount = async () => {
    const confirmed = window.confirm(
      'Are you sure you want to delete your account? This action cannot be undone and all your data will be permanently deleted.'
    );

    if (confirmed) {
      const doubleConfirm = window.confirm(
        'This will permanently delete ALL your data including collections, requests, workflows, and monitoring rules. Type YES to confirm.'
      );

      if (doubleConfirm) {
        try {
          await axios.delete('/gdpr/account');
          alert('Account deletion initiated. You will be logged out shortly.');
          // Redirect to logout or login page
          window.location.href = '/auth';
        } catch (error) {
          console.error('Failed to delete account:', error);
          alert('Failed to delete account');
        }
      }
    }
  };

  const dataTypes = [
    { id: 'requests', label: 'API Requests', description: 'Your saved API requests and configurations' },
    { id: 'collections', label: 'Collections', description: 'API collections and organizational data' },
    { id: 'workflows', label: 'Workflows', description: 'Automation workflows and configurations' },
    { id: 'monitoring', label: 'Monitoring Data', description: 'Performance metrics and monitoring rules' },
    { id: 'audit', label: 'Audit Logs', description: 'Activity logs and system interactions' }
  ];

  const DataExportDialog = () => {
    return (
      <Dialog open={isRequestingExport} onOpenChange={setIsRequestingExport}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Download className="h-5 w-5" />
              Request Data Export
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <Alert>
              <Shield className="h-4 w-4" />
              <AlertDescription>
                Under GDPR Article 20, you have the right to receive your personal data in a portable format.
              </AlertDescription>
            </Alert>
            
            <div>
              <h4 className="font-medium mb-3">Select data types to export:</h4>
              <div className="space-y-3">
                {dataTypes.map(dataType => (
                  <div key={dataType.id} className="flex items-start space-x-3">
                    <Checkbox
                      id={dataType.id}
                      checked={selectedDataTypes.includes(dataType.id)}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          setSelectedDataTypes(prev => [...prev, dataType.id]);
                        } else {
                          setSelectedDataTypes(prev => prev.filter(id => id !== dataType.id));
                        }
                      }}
                    />
                    <div>
                      <label htmlFor={dataType.id} className="text-sm font-medium cursor-pointer">
                        {dataType.label}
                      </label>
                      <p className="text-xs text-muted-foreground">
                        {dataType.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="bg-muted p-3 rounded-lg text-sm">
              <p className="font-medium mb-1">Export Information:</p>
              <ul className="text-xs text-muted-foreground space-y-1">
                <li>• Data will be provided in JSON format</li>
                <li>• Processing may take up to 30 days</li>
                <li>• Download link will be sent to your registered email</li>
                <li>• Export files are available for 7 days</li>
              </ul>
            </div>
            
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setIsRequestingExport(false)}>
                Cancel
              </Button>
              <Button onClick={requestDataExport}>
                Request Export
              </Button>
            </div>
          </div>
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse space-y-3">
                  <div className="h-6 bg-muted rounded w-3/4"></div>
                  <div className="h-4 bg-muted rounded w-1/2"></div>
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
            <Shield className="h-8 w-8 text-blue-600" />
            GDPR Compliance
          </h2>
          <p className="text-muted-foreground">Manage your data privacy rights and compliance settings</p>
        </div>
      </div>

      {/* Compliance Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Consent Status</p>
                <p className="text-lg font-bold">Active</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <Globe className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Data Residency</p>
                <p className="text-lg font-bold">{user?.data_residency || 'EU'}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                <Eye className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Audit Logging</p>
                <p className="text-lg font-bold">Enabled</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Your Rights */}
      <Card>
        <CardHeader>
          <CardTitle>Your Data Rights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Download className="h-5 w-5 text-blue-600" />
                  <h4 className="font-medium">Right to Data Portability</h4>
                </div>
                <p className="text-sm text-muted-foreground mb-3">
                  Download all your personal data in a machine-readable format.
                </p>
                <Button onClick={() => setIsRequestingExport(true)} className="w-full">
                  Request Data Export
                </Button>
              </div>
              
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Eye className="h-5 w-5 text-green-600" />
                  <h4 className="font-medium">Right to Access</h4>
                </div>
                <p className="text-sm text-muted-foreground mb-3">
                  View all activities and data processing operations.
                </p>
                <Button variant="outline" className="w-full">
                  View Audit Logs
                </Button>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Globe className="h-5 w-5 text-purple-600" />
                  <h4 className="font-medium">Data Residency Control</h4>
                </div>
                <p className="text-sm text-muted-foreground mb-3">
                  Your data is stored in: <strong>{user?.data_residency || 'EU'}</strong>
                </p>
                <Button variant="outline" className="w-full">
                  Change Residency
                </Button>
              </div>
              
              <div className="p-4 border border-red-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Trash2 className="h-5 w-5 text-red-600" />
                  <h4 className="font-medium text-red-700">Right to be Forgotten</h4>
                </div>
                <p className="text-sm text-muted-foreground mb-3">
                  Permanently delete your account and all associated data.
                </p>
                <Button variant="destructive" onClick={deleteAccount} className="w-full">
                  Delete Account
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity Audit */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Recent Activity Audit
          </CardTitle>
        </CardHeader>
        <CardContent>
          {auditLogs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-2" />
              <p>No audit logs available</p>
            </div>
          ) : (
            <div className="space-y-3">
              {auditLogs.slice(0, 10).map((log, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium">{log.action.replace('_', ' ').toUpperCase()}</p>
                    <p className="text-xs text-muted-foreground">
                      {log.resource_type} • {new Date(log.timestamp).toLocaleString()}
                    </p>
                    {log.ip_address && (
                      <p className="text-xs text-muted-foreground">IP: {log.ip_address}</p>
                    )}
                  </div>
                  <Badge variant="outline">{log.resource_type}</Badge>
                </div>
              ))}
              
              {auditLogs.length > 10 && (
                <div className="text-center pt-4">
                  <Button variant="outline" size="sm">
                    View All Logs ({auditLogs.length})
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Compliance Information */}
      <Card>
        <CardHeader>
          <CardTitle>Compliance Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium mb-2">Data Processing</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• API requests and responses are processed for functionality</li>
                <li>• Performance metrics are collected for monitoring</li>
                <li>• Audit logs are maintained for security and compliance</li>
                <li>• Data is encrypted in transit and at rest</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium mb-2">Your Rights Under GDPR</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Right to access your personal data</li>
                <li>• Right to rectification of inaccurate data</li>
                <li>• Right to data portability</li>
                <li>• Right to be forgotten (data deletion)</li>
                <li>• Right to object to processing</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="flex items-start gap-2">
              <Shield className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-blue-800 dark:text-blue-200">Data Protection Contact</p>
                <p className="text-blue-700 dark:text-blue-300 mt-1">
                  For any data protection queries, contact our DPO at privacy@apiforge.com
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <DataExportDialog />
    </div>
  );
};

export default GDPRCompliance;