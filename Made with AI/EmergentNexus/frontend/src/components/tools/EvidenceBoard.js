import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { 
  Network, 
  Plus, 
  Move,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Search,
  Edit,
  Trash,
  Link
} from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

export default function EvidenceBoard() {
  const canvasRef = useRef(null);
  const [canvasContext, setCanvasContext] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [selectedItem, setSelectedItem] = useState(null);
  const [isItemModalOpen, setIsItemModalOpen] = useState(false);
  const [itemForm, setItemForm] = useState({
    title: '',
    description: '',
    type: 'evidence',
    tags: []
  });
  const [evidenceItems, setEvidenceItems] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  
  const { nodes, api, actions, relations } = useWorkspace();

  // Get evidence board items
  const boardItems = nodes.filter(node => node.node_type === 'evidence-item');

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      setCanvasContext(ctx);
      
      // Set canvas size
      const resizeCanvas = () => {
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        drawCanvas();
      };
      
      resizeCanvas();
      window.addEventListener('resize', resizeCanvas);
      
      return () => window.removeEventListener('resize', resizeCanvas);
    }
  }, []);

  useEffect(() => {
    drawCanvas();
  }, [boardItems, relations, zoom, pan, canvasContext]);

  const drawCanvas = () => {
    if (!canvasContext) return;
    
    const ctx = canvasContext;
    const canvas = canvasRef.current;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Save current state
    ctx.save();
    
    // Apply zoom and pan
    ctx.scale(zoom, zoom);
    ctx.translate(pan.x, pan.y);
    
    // Draw grid
    drawGrid(ctx, canvas);
    
    // Draw relations first (behind items)
    drawRelations(ctx);
    
    // Draw items
    drawItems(ctx);
    
    // Restore state
    ctx.restore();
  };

  const drawGrid = (ctx, canvas) => {
    const gridSize = 40;
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 1;
    
    const startX = Math.floor(-pan.x / gridSize) * gridSize;
    const startY = Math.floor(-pan.y / gridSize) * gridSize;
    
    for (let x = startX; x < (canvas.width / zoom) - pan.x; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, -pan.y);
      ctx.lineTo(x, (canvas.height / zoom) - pan.y);
      ctx.stroke();
    }
    
    for (let y = startY; y < (canvas.height / zoom) - pan.y; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(-pan.x, y);
      ctx.lineTo((canvas.width / zoom) - pan.x, y);
      ctx.stroke();
    }
  };

  const drawItems = (ctx) => {
    boardItems.forEach((item) => {
      const x = item.content.x || Math.random() * 400 + 100;
      const y = item.content.y || Math.random() * 300 + 100;
      const width = 180;
      const height = 120;
      
      // Item background
      ctx.fillStyle = selectedItem?.id === item.id ? '#3b82f6' : '#1e293b';
      ctx.strokeStyle = '#64748b';
      ctx.lineWidth = 2;
      
      ctx.fillRect(x, y, width, height);
      ctx.strokeRect(x, y, width, height);
      
      // Title
      ctx.fillStyle = '#f8fafc';
      ctx.font = '14px Inter, sans-serif';
      ctx.fillText(
        item.title.length > 20 ? item.title.substring(0, 20) + '...' : item.title,
        x + 10,
        y + 25
      );
      
      // Type badge
      ctx.fillStyle = item.content.type === 'evidence' ? '#059669' : '#7c3aed';
      ctx.fillRect(x + 10, y + 35, 60, 20);
      ctx.fillStyle = '#ffffff';
      ctx.font = '12px Inter, sans-serif';
      ctx.fillText(item.content.type || 'evidence', x + 15, y + 48);
      
      // Description (truncated)
      ctx.fillStyle = '#cbd5e1';
      ctx.font = '12px Inter, sans-serif';
      const desc = item.content.description || '';
      const maxChars = 30;
      const truncatedDesc = desc.length > maxChars ? desc.substring(0, maxChars) + '...' : desc;
      ctx.fillText(truncatedDesc, x + 10, y + 70);
      
      // Tags
      if (item.tags && item.tags.length > 0) {
        ctx.fillStyle = '#475569';
        ctx.font = '10px Inter, sans-serif';
        ctx.fillText(`#${item.tags[0]}`, x + 10, y + 90);
        
        if (item.tags.length > 1) {
          ctx.fillText(`+${item.tags.length - 1}`, x + 80, y + 90);
        }
      }
      
      // Connection count
      const connectionCount = relations.filter(rel => 
        rel.from_id === item.id || rel.to_id === item.id
      ).length;
      
      if (connectionCount > 0) {
        ctx.fillStyle = '#3b82f6';
        ctx.beginPath();
        ctx.arc(x + width - 15, y + 15, 8, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.fillStyle = '#ffffff';
        ctx.font = '10px Inter, sans-serif';
        ctx.fillText(connectionCount.toString(), x + width - 18, y + 19);
      }
    });
  };

  const drawRelations = (ctx) => {
    relations.forEach((relation) => {
      const fromItem = boardItems.find(item => item.id === relation.from_id);
      const toItem = boardItems.find(item => item.id === relation.to_id);
      
      if (fromItem && toItem) {
        const fromX = (fromItem.content.x || 100) + 90; // Center of item
        const fromY = (fromItem.content.y || 100) + 60;
        const toX = (toItem.content.x || 200) + 90;
        const toY = (toItem.content.y || 200) + 60;
        
        // Draw line
        ctx.strokeStyle = relation.color || '#64748b';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(fromX, fromY);
        ctx.lineTo(toX, toY);
        ctx.stroke();
        
        // Draw arrow
        const angle = Math.atan2(toY - fromY, toX - fromX);
        const arrowLength = 10;
        
        ctx.beginPath();
        ctx.moveTo(toX, toY);
        ctx.lineTo(
          toX - arrowLength * Math.cos(angle - Math.PI / 6),
          toY - arrowLength * Math.sin(angle - Math.PI / 6)
        );
        ctx.lineTo(
          toX - arrowLength * Math.cos(angle + Math.PI / 6),
          toY - arrowLength * Math.sin(angle + Math.PI / 6)
        );
        ctx.closePath();
        ctx.fillStyle = relation.color || '#64748b';
        ctx.fill();
        
        // Draw label if exists
        if (relation.label) {
          const midX = (fromX + toX) / 2;
          const midY = (fromY + toY) / 2;
          
          ctx.fillStyle = '#1e293b';
          ctx.fillRect(midX - 30, midY - 8, 60, 16);
          
          ctx.fillStyle = '#f8fafc';
          ctx.font = '10px Inter, sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(relation.label, midX, midY + 3);
          ctx.textAlign = 'left';
        }
      }
    });
  };

  const handleCanvasClick = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / zoom - pan.x;
    const y = (e.clientY - rect.top) / zoom - pan.y;
    
    // Check if click is on an item
    const clickedItem = boardItems.find(item => {
      const itemX = item.content.x || 100;
      const itemY = item.content.y || 100;
      return x >= itemX && x <= itemX + 180 && y >= itemY && y <= itemY + 120;
    });
    
    if (clickedItem) {
      setSelectedItem(clickedItem);
    } else {
      setSelectedItem(null);
    }
  };

  const handleCanvasDoubleClick = (e) => {
    if (selectedItem) {
      openEditItemModal(selectedItem);
    } else {
      // Create new item at click position
      const rect = canvasRef.current.getBoundingClientRect();
      const x = (e.clientX - rect.left) / zoom - pan.x;
      const y = (e.clientY - rect.top) / zoom - pan.y;
      
      openNewItemModal(x, y);
    }
  };

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e) => {
    if (isDragging && !selectedItem) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
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

  const openNewItemModal = (x = null, y = null) => {
    setSelectedItem(null);
    setItemForm({
      title: '',
      description: '',
      type: 'evidence',
      tags: [],
      x: x || Math.random() * 400 + 100,
      y: y || Math.random() * 300 + 100
    });
    setIsItemModalOpen(true);
  };

  const openEditItemModal = (item) => {
    setSelectedItem(item);
    setItemForm({
      title: item.title,
      description: item.content.description || '',
      type: item.content.type || 'evidence',
      tags: item.tags || [],
      x: item.content.x || 100,
      y: item.content.y || 100
    });
    setIsItemModalOpen(true);
  };

  const handleSaveItem = async () => {
    if (!itemForm.title.trim()) return;

    const itemData = {
      node_type: 'evidence-item',
      title: itemForm.title.trim(),
      content: {
        description: itemForm.description,
        type: itemForm.type,
        x: itemForm.x,
        y: itemForm.y
      },
      tags: itemForm.tags
    };

    try {
      if (selectedItem) {
        await api.updateNode(selectedItem.id, itemData);
      } else {
        await api.createNode(itemData);
      }
      setIsItemModalOpen(false);
    } catch (error) {
      console.error('Failed to save evidence item:', error);
    }
  };

  const handleDeleteItem = async () => {
    if (!selectedItem) return;
    
    try {
      await api.deleteNode(selectedItem.id);
      setSelectedItem(null);
      setIsItemModalOpen(false);
    } catch (error) {
      console.error('Failed to delete evidence item:', error);
    }
  };

  const addTag = (tag) => {
    if (tag.trim() && !itemForm.tags.includes(tag.trim())) {
      setItemForm({
        ...itemForm,
        tags: [...itemForm.tags, tag.trim()]
      });
    }
  };

  const removeTag = (tagToRemove) => {
    setItemForm({
      ...itemForm,
      tags: itemForm.tags.filter(tag => tag !== tagToRemove)
    });
  };

  const filteredItems = boardItems.filter(item =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="h-full bg-slate-900 flex flex-col" data-testid="evidence-board">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-white flex items-center gap-3">
            <Network className="h-6 w-6 text-purple-400" />
            Evidence Board
          </h1>
          
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <span>{boardItems.length} items</span>
            <span>•</span>
            <span>{relations.length} connections</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Search items..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 w-48 bg-slate-700 border-slate-600 text-white"
              data-testid="evidence-search-input"
            />
          </div>

          {/* Controls */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleZoom(-0.1)}
            data-testid="zoom-out-btn"
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          
          <span className="text-sm text-slate-400 w-12 text-center">
            {Math.round(zoom * 100)}%
          </span>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleZoom(0.1)}
            data-testid="zoom-in-btn"
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={resetView}
            data-testid="reset-view-btn"
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
          
          <Button
            size="sm"
            onClick={() => openNewItemModal()}
            className="bg-purple-600 hover:bg-purple-700"
            data-testid="add-evidence-btn"
          >
            <Plus className="h-4 w-4 mr-1" />
            Add Item
          </Button>
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 relative overflow-hidden">
        <canvas
          ref={canvasRef}
          className="w-full h-full cursor-move evidence-board"
          onClick={handleCanvasClick}
          onDoubleClick={handleCanvasDoubleClick}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          data-testid="evidence-canvas"
        />
        
        {/* Instructions */}
        {boardItems.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-center text-slate-400">
              <Network className="h-12 w-12 mx-auto mb-4 text-slate-500" />
              <div className="text-lg font-medium mb-2">Empty Evidence Board</div>
              <div className="text-sm">
                Double-click to create your first evidence item
                <br />
                Drag to pan, use controls to zoom
              </div>
            </div>
          </div>
        )}
        
        {/* Selected Item Info */}
        {selectedItem && (
          <div className="absolute bottom-4 left-4 bg-slate-800 border border-slate-700 rounded-lg p-3 max-w-sm">
            <div className="font-medium text-white mb-1">{selectedItem.title}</div>
            <div className="text-sm text-slate-400 mb-2">
              {selectedItem.content.description || 'No description'}
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">
                {selectedItem.content.type || 'evidence'}
              </Badge>
              <Button
                size="sm"
                variant="outline"
                onClick={() => openEditItemModal(selectedItem)}
                data-testid="edit-selected-item-btn"
              >
                <Edit className="h-3 w-3 mr-1" />
                Edit
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => actions.setSelectedNode(selectedItem)}
                className="text-blue-400 border-blue-400"
                data-testid="link-selected-item-btn"
              >
                <Link className="h-3 w-3 mr-1" />
                Link
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Item Modal */}
      <Dialog open={isItemModalOpen} onOpenChange={setIsItemModalOpen}>
        <DialogContent className="max-w-lg bg-slate-800 border-slate-700" data-testid="evidence-item-modal">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Edit className="h-5 w-5 text-purple-400" />
              {selectedItem ? 'Edit Evidence Item' : 'New Evidence Item'}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            {/* Title */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Title *
              </label>
              <Input
                placeholder="Evidence item title..."
                value={itemForm.title}
                onChange={(e) => setItemForm({ ...itemForm, title: e.target.value })}
                className="bg-slate-700 border-slate-600 text-white"
                data-testid="evidence-title-input"
              />
            </div>

            {/* Description */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Description
              </label>
              <textarea
                placeholder="Describe this evidence item..."
                value={itemForm.description}
                onChange={(e) => setItemForm({ ...itemForm, description: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2 resize-none"
                rows={3}
                data-testid="evidence-description-input"
              />
            </div>

            {/* Type */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Type
              </label>
              <select
                value={itemForm.type}
                onChange={(e) => setItemForm({ ...itemForm, type: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2"
                data-testid="evidence-type-select"
              >
                <option value="evidence">Evidence</option>
                <option value="hypothesis">Hypothesis</option>
                <option value="conclusion">Conclusion</option>
                <option value="question">Question</option>
              </select>
            </div>

            {/* Tags */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Tags
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {itemForm.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                    {tag}
                    <button
                      onClick={() => removeTag(tag)}
                      className="ml-1 text-slate-400 hover:text-red-400"
                    >
                      ×
                    </button>
                  </Badge>
                ))}
              </div>
              <Input
                placeholder="Add tags (press Enter)..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    addTag(e.target.value);
                    e.target.value = '';
                  }
                }}
                className="bg-slate-700 border-slate-600 text-white"
                data-testid="evidence-tags-input"
              />
            </div>

            {/* Actions */}
            <div className="flex justify-between pt-4">
              <div>
                {selectedItem && (
                  <Button
                    variant="outline"
                    onClick={handleDeleteItem}
                    className="text-red-400 border-red-400 hover:bg-red-400 hover:text-white"
                    data-testid="delete-evidence-btn"
                  >
                    <Trash className="h-4 w-4 mr-1" />
                    Delete
                  </Button>
                )}
              </div>
              
              <div className="flex gap-3">
                <Button 
                  variant="outline" 
                  onClick={() => setIsItemModalOpen(false)}
                  data-testid="cancel-evidence-btn"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleSaveItem}
                  disabled={!itemForm.title.trim()}
                  className="bg-purple-600 hover:bg-purple-700"
                  data-testid="save-evidence-btn"
                >
                  {selectedItem ? 'Update' : 'Create'} Item
                </Button>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}