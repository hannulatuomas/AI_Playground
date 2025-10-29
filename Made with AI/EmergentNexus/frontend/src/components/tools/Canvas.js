import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Pen, 
  Square, 
  Circle, 
  ArrowRight,
  Type,
  Move,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Save,
  Trash,
  Link
} from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

const tools = [
  { id: 'select', icon: Move, label: 'Select' },
  { id: 'rectangle', icon: Square, label: 'Rectangle' },
  { id: 'circle', icon: Circle, label: 'Circle' },
  { id: 'arrow', icon: ArrowRight, label: 'Arrow' },
  { id: 'text', icon: Type, label: 'Text' },
  { id: 'pen', icon: Pen, label: 'Pen' }
];

export default function Canvas() {
  const canvasRef = useRef(null);
  const [selectedTool, setSelectedTool] = useState('select');
  const [isDrawing, setIsDrawing] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [shapes, setShapes] = useState([]);
  const [selectedShape, setSelectedShape] = useState(null);
  const [currentCanvas, setCurrentCanvas] = useState(null);
  const [canvasTitle, setCanvasTitle] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  
  const { nodes, api, actions } = useWorkspace();
  
  const canvasItems = React.useMemo(() => 
    nodes.filter(node => node.node_type === 'canvas-item'), 
    [nodes]
  );
  
  useEffect(() => {
    if (canvasItems.length > 0 && !currentCanvas) {
      setCurrentCanvas(canvasItems[0]);
    }
  }, [canvasItems, currentCanvas]);

  useEffect(() => {
    if (currentCanvas) {
      setCanvasTitle(currentCanvas.title);
      setShapes(currentCanvas.content.shapes || []);
    }
  }, [currentCanvas]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      drawCanvas(ctx);
    }
  }, [shapes, zoom, pan, selectedShape]);

  const drawCanvas = (ctx) => {
    const canvas = canvasRef.current;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    ctx.save();
    ctx.scale(zoom, zoom);
    ctx.translate(pan.x, pan.y);
    
    // Draw grid
    drawGrid(ctx);
    
    // Draw shapes
    shapes.forEach((shape, index) => {
      drawShape(ctx, shape, selectedShape === index);
    });
    
    ctx.restore();
  };

  const drawGrid = (ctx) => {
    const canvas = canvasRef.current;
    const gridSize = 20;
    
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 1;
    
    for (let x = 0; x < canvas.width / zoom; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x - pan.x, 0 - pan.y);
      ctx.lineTo(x - pan.x, canvas.height / zoom - pan.y);
      ctx.stroke();
    }
    
    for (let y = 0; y < canvas.height / zoom; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0 - pan.x, y - pan.y);
      ctx.lineTo(canvas.width / zoom - pan.x, y - pan.y);
      ctx.stroke();
    }
  };

  const drawShape = (ctx, shape, isSelected) => {
    ctx.strokeStyle = isSelected ? '#3b82f6' : shape.color || '#64748b';
    ctx.fillStyle = shape.fillColor || 'transparent';
    ctx.lineWidth = isSelected ? 3 : 2;
    
    switch (shape.type) {
      case 'rectangle':
        ctx.beginPath();
        ctx.rect(shape.x, shape.y, shape.width, shape.height);
        ctx.fill();
        ctx.stroke();
        break;
        
      case 'circle':
        ctx.beginPath();
        ctx.ellipse(
          shape.x + shape.width / 2, 
          shape.y + shape.height / 2, 
          shape.width / 2, 
          shape.height / 2, 
          0, 0, 2 * Math.PI
        );
        ctx.fill();
        ctx.stroke();
        break;
        
      case 'arrow':
        drawArrow(ctx, shape.x, shape.y, shape.x + shape.width, shape.y + shape.height);
        break;
        
      case 'text':
        ctx.fillStyle = shape.color || '#f8fafc';
        ctx.font = `${shape.fontSize || 16}px Inter, sans-serif`;
        ctx.fillText(shape.text || 'Text', shape.x, shape.y + (shape.fontSize || 16));
        break;
        
      case 'pen':
        if (shape.points && shape.points.length > 1) {
          ctx.beginPath();
          ctx.moveTo(shape.points[0].x, shape.points[0].y);
          shape.points.forEach(point => {
            ctx.lineTo(point.x, point.y);
          });
          ctx.stroke();
        }
        break;
    }
    
    if (isSelected) {
      // Draw selection handles
      const handles = getSelectionHandles(shape);
      handles.forEach(handle => {
        ctx.fillStyle = '#3b82f6';
        ctx.fillRect(handle.x - 3, handle.y - 3, 6, 6);
      });
    }
  };

  const drawArrow = (ctx, fromX, fromY, toX, toY) => {
    const headlen = 10;
    const angle = Math.atan2(toY - fromY, toX - fromX);
    
    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    ctx.lineTo(toX - headlen * Math.cos(angle - Math.PI / 6), toY - headlen * Math.sin(angle - Math.PI / 6));
    ctx.moveTo(toX, toY);
    ctx.lineTo(toX - headlen * Math.cos(angle + Math.PI / 6), toY - headlen * Math.sin(angle + Math.PI / 6));
    ctx.stroke();
  };

  const getSelectionHandles = (shape) => {
    return [
      { x: shape.x, y: shape.y },
      { x: shape.x + shape.width, y: shape.y },
      { x: shape.x + shape.width, y: shape.y + shape.height },
      { x: shape.x, y: shape.y + shape.height }
    ];
  };

  const handleCanvasMouseDown = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / zoom - pan.x;
    const y = (e.clientY - rect.top) / zoom - pan.y;
    
    if (selectedTool === 'select') {
      // Check if clicking on existing shape
      const clickedShapeIndex = shapes.findIndex(shape => 
        x >= shape.x && x <= shape.x + (shape.width || 0) &&
        y >= shape.y && y <= shape.y + (shape.height || 0)
      );
      
      setSelectedShape(clickedShapeIndex >= 0 ? clickedShapeIndex : null);
      
      if (clickedShapeIndex < 0) {
        // Start panning
        setIsDragging(true);
        setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
      }
    } else {
      // Create new shape
      const newShape = {
        type: selectedTool,
        x,
        y,
        width: selectedTool === 'text' ? 100 : 0,
        height: selectedTool === 'text' ? 20 : 0,
        color: '#64748b',
        points: selectedTool === 'pen' ? [{ x, y }] : undefined,
        text: selectedTool === 'text' ? 'New Text' : undefined,
        fontSize: selectedTool === 'text' ? 16 : undefined
      };
      
      setShapes([...shapes, newShape]);
      setSelectedShape(shapes.length);
      setIsDrawing(true);
    }
  };

  const handleCanvasMouseMove = (e) => {
    if (isDragging && selectedTool === 'select') {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    } else if (isDrawing && selectedShape !== null) {
      const rect = canvasRef.current.getBoundingClientRect();
      const x = (e.clientX - rect.left) / zoom - pan.x;
      const y = (e.clientY - rect.top) / zoom - pan.y;
      
      const newShapes = [...shapes];
      const currentShape = newShapes[selectedShape];
      
      if (selectedTool === 'pen') {
        currentShape.points.push({ x, y });
      } else {
        currentShape.width = x - currentShape.x;
        currentShape.height = y - currentShape.y;
      }
      
      setShapes(newShapes);
    }
  };

  const handleCanvasMouseUp = () => {
    setIsDrawing(false);
    setIsDragging(false);
  };

  const handleZoom = (delta) => {
    const newZoom = Math.max(0.1, Math.min(3, zoom + delta));
    setZoom(newZoom);
  };

  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const saveCanvas = async () => {
    if (!canvasTitle.trim()) return;
    
    const canvasData = {
      node_type: 'canvas-item',
      title: canvasTitle.trim(),
      content: { shapes },
      tags: ['canvas']
    };

    try {
      if (currentCanvas) {
        await api.updateNode(currentCanvas.id, canvasData);
      } else {
        const newCanvas = await api.createNode(canvasData);
        setCurrentCanvas(newCanvas);
      }
    } catch (error) {
      console.error('Failed to save canvas:', error);
    }
  };

  const createNewCanvas = () => {
    setCurrentCanvas(null);
    setCanvasTitle('New Canvas');
    setShapes([]);
    setSelectedShape(null);
  };

  const deleteShape = () => {
    if (selectedShape !== null) {
      const newShapes = shapes.filter((_, index) => index !== selectedShape);
      setShapes(newShapes);
      setSelectedShape(null);
    }
  };

  return (
    <div className="h-full bg-slate-900 flex flex-col" data-testid="canvas">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700 bg-slate-800">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Pen className="h-5 w-5 text-pink-400" />
            Canvas
          </h1>
          
          <Input
            placeholder="Canvas title..."
            value={canvasTitle}
            onChange={(e) => setCanvasTitle(e.target.value)}
            className="w-48 bg-slate-700 border-slate-600 text-white"
            data-testid="canvas-title-input"
          />
        </div>
        
        <div className="flex items-center gap-2">
          <select
            value={currentCanvas?.id || ''}
            onChange={(e) => {
              const canvas = canvasItems.find(c => c.id === e.target.value);
              setCurrentCanvas(canvas || null);
            }}
            className="bg-slate-700 border border-slate-600 text-white rounded px-2 py-1 text-sm"
            data-testid="canvas-select"
          >
            <option value="">New Canvas</option>
            {canvasItems.map((canvas) => (
              <option key={canvas.id} value={canvas.id}>
                {canvas.title}
              </option>
            ))}
          </select>
          
          <Button
            size="sm"
            onClick={createNewCanvas}
            variant="outline"
            data-testid="new-canvas-btn"
          >
            New
          </Button>
          
          <Button
            size="sm"
            onClick={saveCanvas}
            disabled={!canvasTitle.trim()}
            className="bg-pink-600 hover:bg-pink-700"
            data-testid="save-canvas-btn"
          >
            <Save className="h-4 w-4 mr-1" />
            Save
          </Button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Toolbar */}
        <div className="w-16 bg-slate-800 border-r border-slate-700 p-2">
          <div className="space-y-2">
            {tools.map((tool) => {
              const Icon = tool.icon;
              return (
                <Button
                  key={tool.id}
                  variant={selectedTool === tool.id ? "secondary" : "ghost"}
                  size="sm"
                  onClick={() => setSelectedTool(tool.id)}
                  className={`w-12 h-12 p-2 ${
                    selectedTool === tool.id 
                      ? 'bg-slate-700 text-white' 
                      : 'text-slate-400 hover:text-white'
                  }`}
                  data-testid={`tool-${tool.id}`}
                  title={tool.label}
                >
                  <Icon className="h-5 w-5" />
                </Button>
              );
            })}
            
            <div className="border-t border-slate-700 my-2" />
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleZoom(-0.1)}
              className="w-12 h-12 p-2 text-slate-400 hover:text-white"
              data-testid="zoom-out"
            >
              <ZoomOut className="h-5 w-5" />
            </Button>
            
            <div className="text-xs text-slate-400 text-center">
              {Math.round(zoom * 100)}%
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleZoom(0.1)}
              className="w-12 h-12 p-2 text-slate-400 hover:text-white"
              data-testid="zoom-in"
            >
              <ZoomIn className="h-5 w-5" />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={resetView}
              className="w-12 h-12 p-2 text-slate-400 hover:text-white"
              data-testid="reset-view"
            >
              <RotateCcw className="h-5 w-5" />
            </Button>
            
            {selectedShape !== null && (
              <>
                <div className="border-t border-slate-700 my-2" />
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={deleteShape}
                  className="w-12 h-12 p-2 text-red-400 hover:text-red-300"
                  data-testid="delete-shape"
                >
                  <Trash className="h-5 w-5" />
                </Button>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => currentCanvas && actions.setSelectedNode(currentCanvas)}
                  className="w-12 h-12 p-2 text-blue-400 hover:text-blue-300"
                  data-testid="link-canvas"
                >
                  <Link className="h-5 w-5" />
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Canvas Area */}
        <div className="flex-1 overflow-hidden relative bg-slate-900">
          <canvas
            ref={canvasRef}
            className="w-full h-full cursor-crosshair"
            width={1200}
            height={800}
            onMouseDown={handleCanvasMouseDown}
            onMouseMove={handleCanvasMouseMove}
            onMouseUp={handleCanvasMouseUp}
            onMouseLeave={handleCanvasMouseUp}
            data-testid="drawing-canvas"
          />
          
          {shapes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="text-center text-slate-400">
                <Pen className="h-16 w-16 mx-auto mb-4 text-slate-500" />
                <div className="text-xl font-medium mb-2">Empty Canvas</div>
                <div className="text-sm">
                  Select a tool from the toolbar and start drawing
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Properties Panel */}
        {selectedShape !== null && shapes[selectedShape] && (
          <div className="w-64 bg-slate-800 border-l border-slate-700 p-4">
            <h3 className="text-white font-medium mb-4">Properties</h3>
            
            <div className="space-y-3">
              <div>
                <label className="text-sm text-slate-400 block mb-1">Type</label>
                <div className="text-white text-sm capitalize">
                  {shapes[selectedShape].type}
                </div>
              </div>
              
              {shapes[selectedShape].type === 'text' && (
                <>
                  <div>
                    <label className="text-sm text-slate-400 block mb-1">Text</label>
                    <Input
                      value={shapes[selectedShape].text || ''}
                      onChange={(e) => {
                        const newShapes = [...shapes];
                        newShapes[selectedShape].text = e.target.value;
                        setShapes(newShapes);
                      }}
                      className="bg-slate-700 border-slate-600 text-white text-sm"
                      data-testid="text-content"
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm text-slate-400 block mb-1">Font Size</label>
                    <Input
                      type="number"
                      value={shapes[selectedShape].fontSize || 16}
                      onChange={(e) => {
                        const newShapes = [...shapes];
                        newShapes[selectedShape].fontSize = parseInt(e.target.value);
                        setShapes(newShapes);
                      }}
                      className="bg-slate-700 border-slate-600 text-white text-sm"
                      data-testid="font-size"
                    />
                  </div>
                </>
              )}
              
              <div>
                <label className="text-sm text-slate-400 block mb-1">Color</label>
                <Input
                  type="color"
                  value={shapes[selectedShape].color || '#64748b'}
                  onChange={(e) => {
                    const newShapes = [...shapes];
                    newShapes[selectedShape].color = e.target.value;
                    setShapes(newShapes);
                  }}
                  className="bg-slate-700 border-slate-600 h-8"
                  data-testid="shape-color"
                />
              </div>
              
              <div>
                <label className="text-sm text-slate-400 block mb-1">Position</label>
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    type="number"
                    placeholder="X"
                    value={Math.round(shapes[selectedShape].x)}
                    onChange={(e) => {
                      const newShapes = [...shapes];
                      newShapes[selectedShape].x = parseInt(e.target.value) || 0;
                      setShapes(newShapes);
                    }}
                    className="bg-slate-700 border-slate-600 text-white text-xs"
                  />
                  <Input
                    type="number"
                    placeholder="Y"
                    value={Math.round(shapes[selectedShape].y)}
                    onChange={(e) => {
                      const newShapes = [...shapes];
                      newShapes[selectedShape].y = parseInt(e.target.value) || 0;
                      setShapes(newShapes);
                    }}
                    className="bg-slate-700 border-slate-600 text-white text-xs"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}