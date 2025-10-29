import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Link, ArrowRight } from 'lucide-react';
import { useWorkspace } from '../contexts/WorkspaceContext';

export default function LinkingModal({ isOpen, onClose, sourceNode }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTargetNode, setSelectedTargetNode] = useState(null);
  const [relationLabel, setRelationLabel] = useState('');
  const { nodes, api, loading } = useWorkspace();

  const filteredNodes = nodes.filter(node => 
    node.id !== sourceNode?.id &&
    (node.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
     node.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())))
  );

  useEffect(() => {
    if (!isOpen) {
      setSearchQuery('');
      setSelectedTargetNode(null);
      setRelationLabel('');
    }
  }, [isOpen]);

  const handleCreateLink = async () => {
    if (!sourceNode || !selectedTargetNode) return;

    try {
      await api.createRelation({
        from_id: sourceNode.id,
        to_id: selectedTargetNode.id,
        relation_type: 'links-to',
        label: relationLabel || 'connected to',
        color: '#3b82f6'
      });
      onClose();
    } catch (error) {
      console.error('Failed to create link:', error);
    }
  };

  if (!sourceNode) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl mx-4 bg-slate-800 border-slate-700" data-testid="linking-modal">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Link className="h-5 w-5 text-blue-400" />
            Create Connection
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Source Node */}
          <div className="flex items-center gap-3 p-3 bg-slate-700 rounded-lg">
            <div className="text-sm text-slate-400">From:</div>
            <div className="flex-1">
              <div className="font-medium text-white">{sourceNode.title}</div>
              <div className="text-xs text-slate-400">{sourceNode.node_type}</div>
            </div>
          </div>

          {/* Arrow */}
          <div className="flex justify-center">
            <ArrowRight className="h-5 w-5 text-slate-400" />
          </div>

          {/* Search Target */}
          <div className="space-y-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search for target node..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-slate-700 border-slate-600 text-white"
                data-testid="target-search-input"
              />
            </div>

            {/* Target Nodes List */}
            <div className="max-h-60 overflow-y-auto space-y-2">
              {filteredNodes.length === 0 ? (
                <div className="text-center text-slate-400 py-8">
                  {searchQuery ? 'No nodes found' : 'No available nodes to link'}
                </div>
              ) : (
                filteredNodes.map((node) => (
                  <Button
                    key={node.id}
                    variant={selectedTargetNode?.id === node.id ? "secondary" : "ghost"}
                    className={`w-full justify-start p-3 h-auto ${
                      selectedTargetNode?.id === node.id
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : 'text-slate-300 hover:text-white hover:bg-slate-700'
                    }`}
                    onClick={() => setSelectedTargetNode(node)}
                    data-testid={`target-node-${node.id}-btn`}
                  >
                    <div className="text-left w-full">
                      <div className="font-medium">{node.title}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className="text-xs">
                          {node.node_type}
                        </Badge>
                        {node.tags.slice(0, 3).map((tag) => (
                          <Badge key={tag} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </Button>
                ))
              )}
            </div>
          </div>

          {/* Relation Label */}
          {selectedTargetNode && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">
                Connection Label (optional)
              </label>
              <Input
                placeholder="e.g., references, depends on, relates to..."
                value={relationLabel}
                onChange={(e) => setRelationLabel(e.target.value)}
                className="bg-slate-700 border-slate-600 text-white"
                data-testid="relation-label-input"
              />
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={onClose} data-testid="cancel-link-btn">
              Cancel
            </Button>
            <Button
              onClick={handleCreateLink}
              disabled={!selectedTargetNode || loading}
              className="bg-blue-600 hover:bg-blue-700"
              data-testid="create-link-btn"
            >
              {loading ? 'Creating...' : 'Create Connection'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}