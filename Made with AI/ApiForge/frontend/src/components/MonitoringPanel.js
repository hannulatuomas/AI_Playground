import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { AlertTriangle, CheckCircle, Clock, Plus, Settings, TrendingUp, XCircle } from 'lucide-react';
import axios from 'axios';

const MonitoringPanel = ({ requests }) => {
  const [rules, setRules] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [selectedRequest, setSelectedRequest] = useState('');
  const [isCreatingRule, setIsCreatingRule] = useState(false);

  useEffect(() => {
    loadMonitoringRules();
  }, []);

  const loadMonitoringRules = async () => {
    try {
      const response = await axios.get('/monitoring/rules');
      setRules(response.data);
      
      // Load metrics for each rule
      const metricsData = {};
      for (const rule of response.data) {
        try {
          const metricsResponse = await axios.get(`/monitoring/metrics/${rule.request_id}`);
          metricsData[rule.request_id] = metricsResponse.data;
        } catch (error) {
          console.error(`Failed to load metrics for request ${rule.request_id}:`, error);
        }
      }
      setMetrics(metricsData);
    } catch (error) {
      console.error('Failed to load monitoring rules:', error);
    }
  };

  const createRule = async (ruleData) => {
    try {
      await axios.post('/monitoring/rules', ruleData);
      loadMonitoringRules();
      setIsCreatingRule(false);
    } catch (error) {
      console.error('Failed to create monitoring rule:', error);
    }
  };

  const CreateRuleDialog = () => {
    const [formData, setFormData] = useState({
      name: '',
      request_id: '',
      rule_type: 'response_time',
      condition: { operator: '<', value: 500 },
      interval_minutes: 5,
      notifications: []
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      if (formData.name && formData.request_id) {
        createRule(formData);
      }
    };

    return (
      <Dialog open={isCreatingRule} onOpenChange={setIsCreatingRule}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Monitoring Rule</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label>Rule Name</Label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter rule name"
              />
            </div>
            
            <div>
              <Label>Request to Monitor</Label>
              <Select 
                value={formData.request_id} 
                onValueChange={(value) => setFormData(prev => ({ ...prev, request_id: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a request" />
                </SelectTrigger>
                <SelectContent>
                  {requests.map(request => (
                    <SelectItem key={request.id} value={request.id}>
                      {request.name} - {request.method} {request.url}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>Rule Type</Label>
              <Select 
                value={formData.rule_type} 
                onValueChange={(value) => setFormData(prev => ({ ...prev, rule_type: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="response_time">Response Time</SelectItem>
                  <SelectItem value="status_code">Status Code</SelectItem>
                  <SelectItem value="uptime">Uptime</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label>Operator</Label>
                <Select 
                  value={formData.condition.operator} 
                  onValueChange={(value) => setFormData(prev => ({ 
                    ...prev, 
                    condition: { ...prev.condition, operator: value }
                  }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="<">Less than</SelectItem>
                    <SelectItem value=">">Greater than</SelectItem>
                    <SelectItem value="=">Equals</SelectItem>
                    <SelectItem value="!=">Not equals</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label>Value</Label>
                <Input
                  type="number"
                  value={formData.condition.value}
                  onChange={(e) => setFormData(prev => ({ 
                    ...prev, 
                    condition: { ...prev.condition, value: parseInt(e.target.value) }
                  }))}
                  placeholder="Threshold value"
                />
              </div>
            </div>
            
            <div>
              <Label>Check Interval (minutes)</Label>
              <Input
                type="number"
                value={formData.interval_minutes}
                onChange={(e) => setFormData(prev => ({ ...prev, interval_minutes: parseInt(e.target.value) }))}
              />
            </div>
            
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => setIsCreatingRule(false)}>
                Cancel
              </Button>
              <Button type="submit">
                Create Rule
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    );
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const calculateStatus = (rule, requestMetrics) => {
    if (!requestMetrics || requestMetrics.length === 0) return 'unknown';
    
    const latestMetric = requestMetrics[0];
    const { condition, rule_type } = rule;
    
    let value;
    switch (rule_type) {
      case 'response_time':
        value = latestMetric.response_time;
        break;
      case 'status_code':
        value = latestMetric.status_code;
        break;
      default:
        return 'unknown';
    }
    
    let conditionMet = false;
    switch (condition.operator) {
      case '<':
        conditionMet = value < condition.value;
        break;
      case '>':
        conditionMet = value > condition.value;
        break;
      case '=':
        conditionMet = value === condition.value;
        break;
      case '!=':
        conditionMet = value !== condition.value;
        break;
    }
    
    return conditionMet ? 'healthy' : 'error';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">API Monitoring</h2>
          <p className="text-muted-foreground">Monitor your APIs for performance and availability</p>
        </div>
        <Button onClick={() => setIsCreatingRule(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Rule
        </Button>
      </div>

      {/* Monitoring Rules */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {rules.length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="text-center py-12">
              <AlertTriangle className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No monitoring rules yet</h3>
              <p className="text-muted-foreground mb-4">
                Create monitoring rules to track API performance and get alerts
              </p>
              <Button onClick={() => setIsCreatingRule(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Rule
              </Button>
            </CardContent>
          </Card>
        ) : (
          rules.map(rule => {
            const requestMetrics = metrics[rule.request_id] || [];
            const status = calculateStatus(rule, requestMetrics);
            const request = requests.find(r => r.id === rule.request_id);
            
            return (
              <Card key={rule.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{rule.name}</CardTitle>
                    {getStatusIcon(status)}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="text-sm font-medium text-muted-foreground">Request</div>
                    <div className="text-sm">{request?.name || 'Unknown'}</div>
                    <div className="text-xs text-muted-foreground">
                      {request?.method} {request?.url}
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-sm font-medium text-muted-foreground">Condition</div>
                    <div className="text-sm">
                      {rule.rule_type.replace('_', ' ')} {rule.condition.operator} {rule.condition.value}
                      {rule.rule_type === 'response_time' && 'ms'}
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-sm font-medium text-muted-foreground">Check Interval</div>
                    <div className="text-sm">Every {rule.interval_minutes} minutes</div>
                  </div>
                  
                  {requestMetrics.length > 0 && (
                    <div>
                      <div className="text-sm font-medium text-muted-foreground">Last Check</div>
                      <div className="text-sm">
                        {new Date(requestMetrics[0].timestamp).toLocaleString()}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Response: {requestMetrics[0].response_time}ms | Status: {requestMetrics[0].status_code}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between pt-2">
                    <Badge 
                      variant={rule.is_active ? 'default' : 'secondary'}
                    >
                      {rule.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                    <Button variant="ghost" size="sm">
                      <Settings className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>

      {/* Performance Chart Placeholder */}
      {rules.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Performance Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center text-muted-foreground border-2 border-dashed rounded-lg">
              <div className="text-center">
                <TrendingUp className="h-8 w-8 mx-auto mb-2" />
                <p>Performance charts will appear here</p>
                <p className="text-sm">Real-time monitoring data visualization</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <CreateRuleDialog />
    </div>
  );
};

export default MonitoringPanel;