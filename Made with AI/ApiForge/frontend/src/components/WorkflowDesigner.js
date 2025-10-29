import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Plus, Play, Save, Trash2, Settings, Circle, Square } from 'lucide-react';

const WorkflowDesigner = ({ workflows, onWorkflowCreate, onWorkflowExecute }) => {
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [connections, setConnections] = useState([]);
  const [draggedNode, setDraggedNode] = useState(null);
  const [isCreatingWorkflow, setIsCreatingWorkflow] = useState(false);
  const [connectingFrom, setConnectingFrom] = useState(null);
  const [showNewWorkflowDialog, setShowNewWorkflowDialog] = useState(false);
  const [editingNode, setEditingNode] = useState(null);
  const [isDraggingNode, setIsDraggingNode] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStart, setConnectionStart] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);

  const nodeTypes = [
    { 
      type: 'start', 
      label: 'Start', 
      color: 'bg-green-600',
      inputs: 0,
      outputs: 1,
      description: 'Starting point of the workflow'
    },
    { 
      type: 'api_call', 
      label: 'API Call', 
      color: 'bg-blue-500',
      inputs: 1,
      outputs: 2,
      description: 'Make HTTP API requests'
    },
    { 
      type: 'microsoft_graph', 
      label: 'MS Graph', 
      color: 'bg-green-500',
      inputs: 1,
      outputs: 2,
      description: 'Microsoft Graph API integration'
    },
    { 
      type: 'condition', 
      label: 'Condition', 
      color: 'bg-yellow-500',
      inputs: 1,
      outputs: 2,
      description: 'If/then conditional logic'
    },
    { 
      type: 'loop', 
      label: 'Loop', 
      color: 'bg-orange-500',
      inputs: 1,
      outputs: 2,
      description: 'Repeat actions multiple times'
    },
    { 
      type: 'transform', 
      label: 'Transform', 
      color: 'bg-purple-500',
      inputs: 1,
      outputs: 1,
      description: 'Transform and manipulate data'
    },
    { 
      type: 'delay', 
      label: 'Delay', 
      color: 'bg-gray-500',
      inputs: 1,
      outputs: 1,
      description: 'Wait for specified time'
    },
    { 
      type: 'notification', 
      label: 'Notify', 
      color: 'bg-red-500',
      inputs: 1,
      outputs: 1,
      description: 'Send notifications'
    },
    { 
      type: 'end', 
      label: 'End', 
      color: 'bg-red-600',
      inputs: 1,
      outputs: 0,
      description: 'End point of the workflow'
    }
  ];

  // Mouse tracking for connection previews and node dragging
  useEffect(() => {
    const handleMouseMove = (e) => {
      // Skip mouse tracking if a dialog is open to prevent re-renders
      if (editingNode) {
        return;
      }
      
      // Check if mouse is over a dialog element
      const dialogElement = e.target.closest('[role="dialog"], .dialog-content, [data-dialog]');
      if (dialogElement) {
        return;
      }
      
      if (canvasRef.current) {
        const rect = canvasRef.current.getBoundingClientRect();
        setMousePos({
          x: e.clientX - rect.left,
          y: e.clientY - rect.top
        });

        // Handle node dragging
        if (isDraggingNode) {
          const newX = Math.max(0, e.clientX - rect.left - dragOffset.x);
          const newY = Math.max(0, e.clientY - rect.top - dragOffset.y);
          
          setNodes(prev => prev.map(node => 
            node.id === isDraggingNode 
              ? { ...node, position: { x: newX, y: newY } }
              : node
          ));
        }
      }
    };

    const handleMouseUp = (e) => {
      // Skip mouse up handling if a dialog is open to prevent interference
      if (editingNode) {
        return;
      }
      
      // Check if mouse up is over a dialog element
      if (e && e.target) {
        const dialogElement = e.target.closest('[role="dialog"], .dialog-content, [data-dialog]');
        if (dialogElement) {
          return;
        }
      }
      
      setIsConnecting(false);
      setConnectionStart(null);
      setIsDraggingNode(null);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDraggingNode, dragOffset, editingNode]);

  const handleDragStart = (e, nodeType) => {
    setDraggedNode(nodeType);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (!draggedNode || !canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = Math.max(0, e.clientX - rect.left - 75); // Center the node
    const y = Math.max(0, e.clientY - rect.top - 40);

    const newNode = {
      id: `node-${Date.now()}`,
      type: draggedNode.type,
      label: draggedNode.label,
      position: { x, y },
      config: {},
      connections: []
    };

    setNodes(prev => [...prev, newNode]);
    setDraggedNode(null);
  };

  // Node interaction handlers with click tracking for mobile compatibility
  const [nodeClickTimer, setNodeClickTimer] = useState(null);
  
  const handleNodeClick = (e, node) => {
    e.stopPropagation();
    
    // Clear any existing timer
    if (nodeClickTimer) {
      clearTimeout(nodeClickTimer);
      setNodeClickTimer(null);
      // This was a double click - open config
      if (!editingNode) {
        setEditingNode(node);
      }
      return;
    }
    
    // Set timer for double-click detection
    const timer = setTimeout(() => {
      setNodeClickTimer(null);
      // Single click - do nothing for now
    }, 300);
    
    setNodeClickTimer(timer);
  };

  const handleNodeMouseDown = (e, nodeId) => {
    e.stopPropagation();
    
    // Don't start dragging if we're clicking on ports
    if (e.target.classList.contains('port')) {
      return;
    }
    
    const rect = canvasRef.current.getBoundingClientRect();
    const node = nodes.find(n => n.id === nodeId);
    
    setIsDraggingNode(nodeId);
    setDragOffset({
      x: e.clientX - rect.left - node.position.x,
      y: e.clientY - rect.top - node.position.y
    });
  };

  // Node dragging is now handled in the document-level mouse move handler

  // Connection handlers
  const handleOutputMouseDown = (e, nodeId, outputIndex) => {
    e.stopPropagation();
    setIsConnecting(true);
    setConnectionStart({ nodeId, outputIndex, type: 'output' });
  };

  const handleInputMouseUp = (e, nodeId, inputIndex) => {
    e.stopPropagation();
    if (!isConnecting || !connectionStart || connectionStart.nodeId === nodeId) return;

    const newConnection = {
      id: `conn-${Date.now()}`,
      from: connectionStart.nodeId,
      fromOutput: connectionStart.outputIndex,
      to: nodeId,
      toInput: inputIndex
    };

    setConnections(prev => [...prev, newConnection]);
    setIsConnecting(false);
    setConnectionStart(null);
  };

  const deleteConnection = (connectionId) => {
    const connection = connections.find(c => c.id === connectionId);
    if (connection) {
      // Remove from connections array
      setConnections(prev => prev.filter(c => c.id !== connectionId));
      
      // Remove from node's connections
      setNodes(prev => prev.map(node => 
        node.id === connection.from 
          ? { ...node, connections: node.connections.filter(c => c !== connection.to) }
          : node
      ));
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const createWorkflow = async (workflowData) => {
    const payload = {
      name: workflowData.name,
      description: workflowData.description,
      nodes: nodes.map(node => ({
        id: node.id,
        name: node.label,
        type: node.type,
        position: node.position,
        config: node.config,
        connections: node.connections
      })),
      connections: connections
    };

    await onWorkflowCreate(payload);
    setNodes([]);
    setConnections([]);
    setShowNewWorkflowDialog(false);
  };

  const clearCanvas = () => {
    setNodes([]);
    setConnections([]);
    setConnectingFrom(null);
    setSelectedWorkflow(null);
  };

  const loadWorkflow = (workflow) => {
    setNodes(workflow.nodes || []);
    setConnections(workflow.connections || []);
    setSelectedWorkflow(workflow);
  };

  const NewWorkflowDialog = () => {
    const [workflowData, setWorkflowData] = useState({ name: '', description: '' });

    const handleSubmit = () => {
      if (!workflowData.name.trim()) {
        alert('Please enter a workflow name');
        return;
      }
      createWorkflow(workflowData);
      setWorkflowData({ name: '', description: '' });
    };

    return (
      <Dialog open={showNewWorkflowDialog} onOpenChange={setShowNewWorkflowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Workflow</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="workflow-name">Workflow Name *</Label>
              <Input
                id="workflow-name"
                value={workflowData.name}
                onChange={(e) => setWorkflowData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter workflow name"
              />
            </div>
            <div>
              <Label htmlFor="workflow-description">Description</Label>
              <Input
                id="workflow-description"
                value={workflowData.description}
                onChange={(e) => setWorkflowData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Enter workflow description (optional)"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button 
                variant="outline" 
                onClick={() => setShowNewWorkflowDialog(false)}
              >
                Cancel
              </Button>
              <Button onClick={handleSubmit}>
                Create Workflow
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  };

  const NodeConfigDialog = ({ node, onUpdate, onDelete, isOpen, onClose }) => {
    const [config, setConfig] = useState(node?.config || {});

    const handleSave = () => {
      onUpdate(config);
    };

    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent 
          className="max-w-2xl" 
          onMouseMove={(e) => e.stopPropagation()}
          onMouseEnter={(e) => e.stopPropagation()}
          onMouseLeave={(e) => e.stopPropagation()}
        >
          <DialogHeader>
            <DialogTitle>Configure {node?.label}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {node?.type === 'api_call' && (
              <>
                <div>
                  <Label>URL</Label>
                  <Input
                    value={config.url || ''}
                    onChange={(e) => setConfig(prev => ({ ...prev, url: e.target.value }))}
                    placeholder="https://api.example.com/endpoint"
                  />
                </div>
                <div>
                  <Label>Method</Label>
                  <Select value={config.method || 'GET'} onValueChange={(value) => setConfig(prev => ({ ...prev, method: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="GET">GET</SelectItem>
                      <SelectItem value="POST">POST</SelectItem>
                      <SelectItem value="PUT">PUT</SelectItem>
                      <SelectItem value="DELETE">DELETE</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Headers (JSON)</Label>
                  <Input
                    value={config.headers || '{}'}
                    onChange={(e) => setConfig(prev => ({ ...prev, headers: e.target.value }))}
                    placeholder='{"Content-Type": "application/json"}'
                  />
                </div>
                <div>
                  <Label>Body</Label>
                  <Input
                    value={config.body || ''}
                    onChange={(e) => setConfig(prev => ({ ...prev, body: e.target.value }))}
                    placeholder='{"key": "value"}'
                  />
                </div>
              </>
            )}
            {node?.type === 'condition' && (
              <>
                <div>
                  <Label>Condition Type</Label>
                  <Select value={config.conditionType || 'response_code'} onValueChange={(value) => setConfig(prev => ({ ...prev, conditionType: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="response_code">Response Code</SelectItem>
                      <SelectItem value="json_path">JSON Path</SelectItem>
                      <SelectItem value="header">Header Value</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Condition Value</Label>
                  <Input
                    value={config.conditionValue || ''}
                    onChange={(e) => setConfig(prev => ({ ...prev, conditionValue: e.target.value }))}
                    placeholder="200"
                  />
                </div>
              </>
            )}
            {node?.type === 'loop' && (
              <>
                <div>
                  <Label>Loop Type</Label>
                  <Select value={config.loopType || 'count'} onValueChange={(value) => setConfig(prev => ({ ...prev, loopType: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="count">Count</SelectItem>
                      <SelectItem value="array">For Each Array Item</SelectItem>
                      <SelectItem value="condition">While Condition</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Loop Value</Label>
                  <Input
                    value={config.loopValue || ''}
                    onChange={(e) => setConfig(prev => ({ ...prev, loopValue: e.target.value }))}
                    placeholder="5"
                  />
                </div>
              </>
            )}
            {node?.type === 'transform' && (
              <>
                <div>
                  <Label>Transform Type</Label>
                  <Select value={config.transformType || 'json_path'} onValueChange={(value) => setConfig(prev => ({ ...prev, transformType: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="json_path">JSONPath Extract</SelectItem>
                      <SelectItem value="format_string">Format String</SelectItem>
                      <SelectItem value="math">Math Operation</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Transform Expression</Label>
                  <Input
                    value={config.transformExpression || ''}
                    onChange={(e) => setConfig(prev => ({ ...prev, transformExpression: e.target.value }))}
                    placeholder="$.response.data"
                  />
                </div>
              </>
            )}
            {node?.type === 'delay' && (
              <div>
                <Label>Delay (seconds)</Label>
                <Input
                  type="number"
                  value={config.seconds || 1}
                  onChange={(e) => setConfig(prev => ({ ...prev, seconds: parseInt(e.target.value) }))}
                />
              </div>
            )}
            {node?.type === 'notification' && (
              <>
                <div>
                  <Label>Notification Type</Label>
                  <Select value={config.notificationType || 'email'} onValueChange={(value) => setConfig(prev => ({ ...prev, notificationType: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="email">Email</SelectItem>
                      <SelectItem value="webhook">Webhook</SelectItem>
                      <SelectItem value="console">Console Log</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Message</Label>
                  <Input
                    value={config.message || ''}
                    onChange={(e) => setConfig(prev => ({ ...prev, message: e.target.value }))}
                    placeholder="Workflow completed successfully"
                  />
                </div>
              </>
            )}
            {node?.type === 'microsoft_graph' && (
              <>
                <div>
                  <Label>Graph API Endpoint</Label>
                  <Select value={config.endpoint} onValueChange={(value) => setConfig(prev => ({ ...prev, endpoint: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select endpoint" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="users">Users</SelectItem>
                      <SelectItem value="groups">Groups</SelectItem>
                      <SelectItem value="mail">Mail</SelectItem>
                      <SelectItem value="calendar">Calendar</SelectItem>
                      <SelectItem value="teams">Teams</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Operation</Label>
                  <Select value={config.operation} onValueChange={(value) => setConfig(prev => ({ ...prev, operation: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select operation" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="list">List</SelectItem>
                      <SelectItem value="get">Get</SelectItem>
                      <SelectItem value="create">Create</SelectItem>
                      <SelectItem value="update">Update</SelectItem>
                      <SelectItem value="delete">Delete</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}
            <div className="flex justify-between">
              <Button
                variant="destructive"
                onClick={() => {
                  onDelete && onDelete(node.id);
                  onClose();
                }}
              >
                <Trash2 className="h-4 w-4 mr-1" />
                Delete Node
              </Button>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setConfig(node?.config || {});
                    onClose();
                  }}
                >
                  Cancel
                </Button>
                <Button onClick={handleSave}>
                  Save
                </Button>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  };

  return (
    <>
    <NewWorkflowDialog />
    {editingNode && (
      <NodeConfigDialog
        node={editingNode}
        onUpdate={(config) => {
          setNodes(prev => prev.map(n => 
            n.id === editingNode.id ? { ...n, config } : n
          ));
          setEditingNode(null);
        }}
        onDelete={(nodeId) => {
          setNodes(prev => prev.filter(n => n.id !== nodeId));
          setConnections(prev => prev.filter(c => c.from !== nodeId && c.to !== nodeId));
          setEditingNode(null);
        }}
        isOpen={!!editingNode}
        onClose={() => setEditingNode(null)}
      />
    )}
    <div className="h-full flex">
      {/* Sidebar - Node Types */}
      <div className="w-64 bg-card border-r p-4">
        <div className="mb-4">
          <h3 className="font-semibold mb-2">Workflow Nodes</h3>
          <div className="space-y-2">
            {nodeTypes.map(nodeType => (
              <div
                key={nodeType.type}
                draggable
                onDragStart={(e) => handleDragStart(e, nodeType)}
                className={`p-2 rounded cursor-move border ${nodeType.color} text-white text-sm text-center`}
              >
                {nodeType.label}
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-semibold mb-2">Actions</h3>
          <div className="space-y-2">
            <Button onClick={() => setShowNewWorkflowDialog(true)} className="w-full" size="sm">
              <Plus className="h-4 w-4 mr-1" />
              New Workflow
            </Button>
            {nodes.length > 0 && (
              <Button onClick={() => setShowNewWorkflowDialog(true)} className="w-full" size="sm">
                <Save className="h-4 w-4 mr-1" />
                Save Current
              </Button>
            )}
            <Button onClick={clearCanvas} variant="outline" className="w-full" size="sm">
              Clear Canvas
            </Button>
          </div>
          
          <div className="mt-4 p-3 bg-muted/50 rounded text-xs space-y-1">
            <div className="font-semibold text-sm mb-2">How to Use:</div>
            <div>• <strong>Add nodes:</strong> Drag from sidebar to canvas</div>
            <div>• <strong>Move nodes:</strong> Click and drag nodes around</div>
            <div>• <strong>Connect nodes:</strong> Drag from output port ⭘ to input port ⭘</div>
            <div>• <strong>Configure:</strong> Click settings button ⚙️ on any node</div>
            <div>• <strong>Delete connections:</strong> Click on connection lines</div>
            {isConnecting && <div className="text-blue-600 font-medium">• Release on input port to connect</div>}
          </div>
        </div>

        <div className="mt-6">
          <h3 className="font-semibold mb-2">Existing Workflows</h3>
          <div className="space-y-1">
            {workflows.map(workflow => (
              <div
                key={workflow.id}
                className={`p-2 rounded cursor-pointer border ${
                  selectedWorkflow?.id === workflow.id 
                    ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
                    : 'bg-muted hover:bg-muted/80 border-transparent'
                }`}
                onClick={() => loadWorkflow(workflow)}
              >
                <div className="text-sm font-medium">{workflow.name}</div>
                <div className="text-xs text-muted-foreground">
                  {workflow.nodes?.length || 0} nodes • {workflow.connections?.length || 0} connections
                </div>
                <div className="flex gap-1 mt-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 px-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      onWorkflowExecute(workflow.id);
                    }}
                    title="Execute Workflow"
                  >
                    <Play className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Canvas */}
      <div className={`flex-1 relative ${editingNode ? 'pointer-events-none' : ''}`} style={{ pointerEvents: editingNode ? 'none' : 'auto' }}>
        <div
          ref={canvasRef}
          className="w-full h-full bg-muted/20 relative overflow-hidden"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          {/* Grid Background */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" strokeWidth="0.5" opacity="0.1" />
              </pattern>
              <marker id="arrowhead" markerWidth="10" markerHeight="7" 
               refX="9" refY="3.5" orient="auto" markerUnits="strokeWidth">
                <polygon points="0 0, 10 3.5, 0 7" fill="currentColor" />
              </marker>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>

          {/* Connection Lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-30">
            {connections.map(connection => {
              const fromNode = nodes.find(n => n.id === connection.from);
              const toNode = nodes.find(n => n.id === connection.to);
              if (!fromNode || !toNode) return null;
              
              // Calculate port positions (start from actual port centers)
              const fromX = fromNode.position.x + 156; // slightly beyond right edge to start from port center
              const fromY = fromNode.position.y + 40 + (connection.fromOutput || 0) * 20; // output port position
              const toX = toNode.position.x - 6; // slightly before left edge to end at port center
              const toY = toNode.position.y + 40 + (connection.toInput || 0) * 20; // input port position
              
              // Calculate curved connection path
              const midX = (fromX + toX) / 2;
              const path = `M ${fromX} ${fromY} C ${midX} ${fromY}, ${midX} ${toY}, ${toX} ${toY}`;
              
              return (
                <g key={connection.id}>
                  <path
                    d={path}
                    stroke="currentColor"
                    strokeWidth="2"
                    fill="none"
                    opacity="0.7"
                    markerEnd="url(#arrowhead)"
                    className="hover:opacity-100 cursor-pointer hover:stroke-blue-500"
                    style={{ pointerEvents: 'all' }}
                    onClick={() => deleteConnection(connection.id)}
                    title="Click to delete connection"
                  />
                </g>
              );
            })}
            
            {/* Connection preview when dragging */}
            {isConnecting && connectionStart && (
              <g>
                <path
                  d={`M ${
                    nodes.find(n => n.id === connectionStart.nodeId)?.position.x + 156
                  } ${
                    nodes.find(n => n.id === connectionStart.nodeId)?.position.y + 40 + (connectionStart.outputIndex || 0) * 20
                  } C ${
                    (nodes.find(n => n.id === connectionStart.nodeId)?.position.x + 156 + mousePos.x) / 2
                  } ${
                    nodes.find(n => n.id === connectionStart.nodeId)?.position.y + 40 + (connectionStart.outputIndex || 0) * 20
                  }, ${
                    (nodes.find(n => n.id === connectionStart.nodeId)?.position.x + 156 + mousePos.x) / 2
                  } ${mousePos.y}, ${mousePos.x} ${mousePos.y}`}
                  stroke="blue"
                  strokeWidth="2"
                  fill="none"
                  opacity="0.7"
                  strokeDasharray="5,5"
                  className="animate-pulse"
                />
              </g>
            )}
          </svg>

          {/* Nodes */}
          {nodes.map(node => {
            const nodeType = nodeTypes.find(nt => nt.type === node.type);
            const isBeingDragged = isDraggingNode === node.id;
            
            return (
              <div
                key={node.id}
                className={`absolute bg-card shadow-lg rounded-lg border-2 transition-all select-none ${
                  isBeingDragged ? 'shadow-2xl scale-105' : 'hover:shadow-xl cursor-pointer'
                }`}
                style={{
                  left: node.position.x,
                  top: node.position.y,
                  borderColor: nodeType?.color.replace('bg-', 'border-'),
                  width: '150px',
                  minHeight: '80px',
                  zIndex: isBeingDragged ? 50 : 20
                }}
                onMouseDown={(e) => handleNodeMouseDown(e, node.id)}
                onClick={(e) => handleNodeClick(e, node)}
              >
                {/* Input Ports */}
                <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1/2">
                  {Array.from({ length: nodeType?.inputs || 0 }).map((_, index) => (
                    <div
                      key={`input-${index}`}
                      className="port w-3 h-3 bg-gray-400 border-2 border-white rounded-full mb-2 cursor-pointer hover:bg-blue-400 transition-colors"
                      style={{ marginTop: index === 0 ? '0' : '8px' }}
                      onMouseUp={(e) => handleInputMouseUp(e, node.id, index)}
                      title={`Input ${index + 1}`}
                    />
                  ))}
                </div>

                {/* Output Ports */}
                <div className="absolute right-0 top-1/2 transform -translate-y-1/2 translate-x-1/2">
                  {Array.from({ length: nodeType?.outputs || 0 }).map((_, index) => (
                    <div
                      key={`output-${index}`}
                      className="port w-3 h-3 bg-gray-400 border-2 border-white rounded-full mb-2 cursor-pointer hover:bg-green-400 transition-colors"
                      style={{ marginTop: index === 0 ? '0' : '8px' }}
                      onMouseDown={(e) => handleOutputMouseDown(e, node.id, index)}
                      title={`Output ${index + 1}`}
                    />
                  ))}
                </div>

                {/* Node Content */}
                <div className="p-3 pt-2">
                  {/* Node Header */}
                  <div className={`h-1 ${nodeType?.color} rounded-full mb-2`}></div>
                  
                  {/* Node Title */}
                  <div className="text-sm font-medium mb-1 text-center">{node.label}</div>
                  
                  {/* Node Type */}
                  <div className="text-xs text-muted-foreground text-center mb-2">
                    {nodeType?.description}
                  </div>
                  
                  {/* Configuration Indicator */}
                  {Object.keys(node.config).length > 0 && (
                    <div className="text-xs text-green-600 text-center font-medium">
                      ✓ Configured
                    </div>
                  )}
                  
                  {/* Settings Button - Always visible for reliability */}
                  <div className="flex justify-center mt-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0 opacity-70 hover:opacity-100"
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingNode(node);
                      }}
                      title="Configure Node"
                    >
                      <Settings className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}

          {/* Empty Canvas Message */}
          {nodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="text-center text-muted-foreground">
                <div className="text-lg font-medium mb-2">Start Building Your Workflow</div>
                <div className="text-sm">Drag nodes from the sidebar to get started</div>
                <div className="text-xs mt-2 opacity-75">Try starting with a "Start" node</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
    </>
  );
};

export default WorkflowDesigner;