import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { 
  Trello, 
  Plus, 
  MoreVertical, 
  Calendar,
  User,
  Tag,
  Link,
  Edit,
  Trash
} from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

const defaultColumns = [
  { id: 'todo', title: 'To Do', color: 'bg-red-500' },
  { id: 'progress', title: 'In Progress', color: 'bg-yellow-500' },
  { id: 'done', title: 'Done', color: 'bg-green-500' }
];

export default function KanbanBoard() {
  const [columns] = useState(defaultColumns);
  const [selectedCard, setSelectedCard] = useState(null);
  const [isCardModalOpen, setIsCardModalOpen] = useState(false);
  const [newCardColumn, setNewCardColumn] = useState(null);
  const [cardForm, setCardForm] = useState({
    title: '',
    description: '',
    status: 'todo',
    tags: [],
    assignee: '',
    dueDate: ''
  });
  
  const { nodes, api, actions, relations } = useWorkspace();
  
  const kanbanCards = nodes.filter(node => node.node_type === 'kanban-card');

  const getCardsByColumn = (columnId) => {
    return kanbanCards.filter(card => card.content.status === columnId);
  };

  const openNewCardModal = (columnId) => {
    setNewCardColumn(columnId);
    setCardForm({
      title: '',
      description: '',
      status: columnId,
      tags: [],
      assignee: '',
      dueDate: ''
    });
    setSelectedCard(null);
    setIsCardModalOpen(true);
  };

  const openEditCardModal = (card) => {
    setSelectedCard(card);
    setCardForm({
      title: card.title,
      description: card.content.description || '',
      status: card.content.status || 'todo',
      tags: card.tags || [],
      assignee: card.content.assignee || '',
      dueDate: card.content.dueDate || ''
    });
    setNewCardColumn(null);
    setIsCardModalOpen(true);
  };

  const handleSaveCard = async () => {
    if (!cardForm.title.trim()) return;

    const cardData = {
      node_type: 'kanban-card',
      title: cardForm.title.trim(),
      content: {
        description: cardForm.description,
        status: cardForm.status,
        assignee: cardForm.assignee,
        dueDate: cardForm.dueDate
      },
      tags: cardForm.tags
    };

    try {
      if (selectedCard) {
        await api.updateNode(selectedCard.id, cardData);
      } else {
        await api.createNode(cardData);
      }
      setIsCardModalOpen(false);
    } catch (error) {
      console.error('Failed to save card:', error);
    }
  };

  const handleDeleteCard = async () => {
    if (!selectedCard) return;
    
    try {
      await api.deleteNode(selectedCard.id);
      setIsCardModalOpen(false);
    } catch (error) {
      console.error('Failed to delete card:', error);
    }
  };

  const moveCard = async (card, newStatus) => {
    try {
      await api.updateNode(card.id, {
        ...card,
        content: { ...card.content, status: newStatus }
      });
    } catch (error) {
      console.error('Failed to move card:', error);
    }
  };

  const addTag = (tag) => {
    if (tag.trim() && !cardForm.tags.includes(tag.trim())) {
      setCardForm({
        ...cardForm,
        tags: [...cardForm.tags, tag.trim()]
      });
    }
  };

  const removeTag = (tagToRemove) => {
    setCardForm({
      ...cardForm,
      tags: cardForm.tags.filter(tag => tag !== tagToRemove)
    });
  };

  const getCardConnections = (card) => {
    return relations.filter(rel => 
      rel.from_id === card.id || rel.to_id === card.id
    ).length;
  };

  return (
    <div className="h-full bg-slate-900 p-6" data-testid="kanban-board">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <Trello className="h-6 w-6 text-blue-400" />
          Kanban Board
        </h1>
        
        <div className="flex items-center gap-3">
          <div className="text-sm text-slate-400">
            {kanbanCards.length} cards total
          </div>
        </div>
      </div>

      {/* Board */}
      <div className="flex gap-6 h-full overflow-x-auto pb-6">
        {columns.map((column) => {
          const columnCards = getCardsByColumn(column.id);
          
          return (
            <div
              key={column.id}
              className="flex-shrink-0 w-80 bg-slate-800 rounded-lg border border-slate-700"
              data-testid={`kanban-column-${column.id}`}
            >
              {/* Column Header */}
              <div className="p-4 border-b border-slate-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${column.color}`} />
                    <h3 className="font-medium text-white">{column.title}</h3>
                    <Badge variant="secondary" className="text-xs">
                      {columnCards.length}
                    </Badge>
                  </div>
                  
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => openNewCardModal(column.id)}
                    className="text-slate-400 hover:text-white"
                    data-testid={`add-card-${column.id}-btn`}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Cards */}
              <div className="p-4 space-y-3 h-full overflow-y-auto">
                {columnCards.map((card) => (
                  <div
                    key={card.id}
                    className="kanban-card group cursor-pointer"
                    onClick={() => openEditCardModal(card)}
                    data-testid={`kanban-card-${card.id}`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-medium text-white text-sm leading-tight flex-1">
                        {card.title}
                      </h4>
                      
                      <Button
                        size="sm"
                        variant="ghost"
                        className="opacity-0 group-hover:opacity-100 transition-opacity p-1 h-auto"
                      >
                        <MoreVertical className="h-3 w-3 text-slate-400" />
                      </Button>
                    </div>
                    
                    {card.content.description && (
                      <p className="text-xs text-slate-400 mb-3 line-clamp-2">
                        {card.content.description}
                      </p>
                    )}
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 flex-wrap">
                        {card.tags && card.tags.slice(0, 2).map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        
                        {card.tags && card.tags.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{card.tags.length - 2}
                          </Badge>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-1 text-slate-400">
                        {card.content.assignee && (
                          <User className="h-3 w-3" />
                        )}
                        
                        {card.content.dueDate && (
                          <Calendar className="h-3 w-3" />
                        )}
                        
                        {getCardConnections(card) > 0 && (
                          <div className="flex items-center gap-1">
                            <Link className="h-3 w-3" />
                            <span className="text-xs">{getCardConnections(card)}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {card.content.dueDate && (
                      <div className="mt-2 text-xs text-slate-400">
                        Due: {new Date(card.content.dueDate).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                ))}
                
                {columnCards.length === 0 && (
                  <div className="text-center text-slate-500 py-8">
                    <div className="text-sm">No cards</div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => openNewCardModal(column.id)}
                      className="mt-2"
                    >
                      Add first card
                    </Button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Card Modal */}
      <Dialog open={isCardModalOpen} onOpenChange={setIsCardModalOpen}>
        <DialogContent className="max-w-lg bg-slate-800 border-slate-700" data-testid="card-modal">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Edit className="h-5 w-5 text-blue-400" />
              {selectedCard ? 'Edit Card' : 'New Card'}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            {/* Title */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Title *
              </label>
              <Input
                placeholder="Card title..."
                value={cardForm.title}
                onChange={(e) => setCardForm({ ...cardForm, title: e.target.value })}
                className="bg-slate-700 border-slate-600 text-white"
                data-testid="card-title-input"
              />
            </div>

            {/* Description */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Description
              </label>
              <Textarea
                placeholder="Card description..."
                value={cardForm.description}
                onChange={(e) => setCardForm({ ...cardForm, description: e.target.value })}
                className="bg-slate-700 border-slate-600 text-white resize-none"
                rows={3}
                data-testid="card-description-input"
              />
            </div>

            {/* Status */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Status
              </label>
              <select
                value={cardForm.status}
                onChange={(e) => setCardForm({ ...cardForm, status: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2"
                data-testid="card-status-select"
              >
                {columns.map((column) => (
                  <option key={column.id} value={column.id}>
                    {column.title}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Assignee */}
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Assignee
                </label>
                <Input
                  placeholder="Assigned to..."
                  value={cardForm.assignee}
                  onChange={(e) => setCardForm({ ...cardForm, assignee: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="card-assignee-input"
                />
              </div>

              {/* Due Date */}
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Due Date
                </label>
                <Input
                  type="date"
                  value={cardForm.dueDate}
                  onChange={(e) => setCardForm({ ...cardForm, dueDate: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="card-due-date-input"
                />
              </div>
            </div>

            {/* Tags */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Tags
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {cardForm.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                    <Tag className="h-3 w-3" />
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
                data-testid="card-tags-input"
              />
            </div>

            {/* Actions */}
            <div className="flex justify-between pt-4">
              <div>
                {selectedCard && (
                  <Button
                    variant="outline"
                    onClick={handleDeleteCard}
                    className="text-red-400 border-red-400 hover:bg-red-400 hover:text-white"
                    data-testid="delete-card-btn"
                  >
                    <Trash className="h-4 w-4 mr-1" />
                    Delete
                  </Button>
                )}
              </div>
              
              <div className="flex gap-3">
                <Button 
                  variant="outline" 
                  onClick={() => setIsCardModalOpen(false)}
                  data-testid="cancel-card-btn"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleSaveCard}
                  disabled={!cardForm.title.trim()}
                  className="bg-blue-600 hover:bg-blue-700"
                  data-testid="save-card-btn"
                >
                  {selectedCard ? 'Update' : 'Create'} Card
                </Button>
              </div>
            </div>

            {/* Link Action */}
            {selectedCard && (
              <div className="pt-2 border-t border-slate-700">
                <Button
                  variant="outline"
                  onClick={() => {
                    actions.setSelectedNode(selectedCard);
                    setIsCardModalOpen(false);
                  }}
                  className="w-full text-blue-400 border-blue-400 hover:bg-blue-400 hover:text-white"
                  data-testid="link-card-btn"
                >
                  <Link className="h-4 w-4 mr-1" />
                  Link to Other Nodes
                </Button>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}