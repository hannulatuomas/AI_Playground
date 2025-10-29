import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { 
  Users, 
  Plus, 
  Edit,
  Trash,
  Link as LinkIcon,
  User,
  Heart,
  Baby
} from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

export default function FamilyTree() {
  const canvasRef = useRef(null);
  const [persons, setPersons] = useState([]);
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [isPersonModalOpen, setIsPersonModalOpen] = useState(false);
  const [personForm, setPersonForm] = useState({
    name: '',
    birthDate: '',
    bio: '',
    gender: 'other',
    parents: [],
    spouse: null
  });
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  
  const { nodes, api, actions } = useWorkspace();
  
  useEffect(() => {
    const familyMembers = nodes.filter(node => node.node_type === 'family-person');
    setPersons(familyMembers);
  }, [nodes]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      drawFamilyTree();
    }
  }, [persons, zoom, pan, selectedPerson?.id]);

  const drawFamilyTree = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    ctx.save();
    ctx.scale(zoom, zoom);
    ctx.translate(pan.x, pan.y);
    
    // Auto-arrange persons in a tree layout
    const arrangedPersons = arrangePersonsInTree();
    
    // Draw connections first
    drawConnections(ctx, arrangedPersons);
    
    // Draw persons
    arrangedPersons.forEach(person => {
      drawPerson(ctx, person, selectedPerson?.id === person.id);
    });
    
    ctx.restore();
  };

  const arrangePersonsInTree = () => {
    if (persons.length === 0) return [];
    
    // Simple layout algorithm - arrange in generations
    const generations = new Map();
    const positioned = new Map();
    
    // Find root persons (no parents)
    const roots = persons.filter(p => !p.content.parents || p.content.parents.length === 0);
    
    const positionPerson = (person, generation, xOffset) => {
      if (positioned.has(person.id)) return positioned.get(person.id);
      
      const x = xOffset * 200 + 100;
      const y = generation * 150 + 100;
      
      const positionedPerson = {
        ...person,
        x,
        y,
        generation
      };
      
      positioned.set(person.id, positionedPerson);
      return positionedPerson;
    };
    
    // Position root generation
    roots.forEach((person, index) => {
      positionPerson(person, 0, index);
    });
    
    // Position children recursively
    const positionChildren = (parentId, parentGeneration, startX) => {
      const children = persons.filter(p => 
        p.content.parents && p.content.parents.includes(parentId)
      );
      
      children.forEach((child, index) => {
        positionPerson(child, parentGeneration + 1, startX + index);
        positionChildren(child.id, parentGeneration + 1, startX + index);
      });
    };
    
    roots.forEach((root, index) => {
      positionChildren(root.id, 0, index * 3);
    });
    
    return Array.from(positioned.values());
  };

  const drawPerson = (ctx, person, isSelected) => {
    const width = 160;
    const height = 100;
    
    // Background
    ctx.fillStyle = isSelected ? '#3b82f6' : '#1e293b';
    ctx.strokeStyle = isSelected ? '#60a5fa' : '#64748b';
    ctx.lineWidth = 2;
    
    ctx.fillRect(person.x, person.y, width, height);
    ctx.strokeRect(person.x, person.y, width, height);
    
    // Gender indicator
    const genderColor = {
      male: '#3b82f6',
      female: '#ec4899',
      other: '#64748b'
    };
    
    ctx.fillStyle = genderColor[person.content.gender] || genderColor.other;
    ctx.fillRect(person.x + width - 20, person.y + 5, 15, 15);
    
    // Name
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 14px Inter, sans-serif';
    ctx.fillText(
      person.content.name || person.title,
      person.x + 10,
      person.y + 25
    );
    
    // Birth date
    if (person.content.birthDate) {
      ctx.fillStyle = '#cbd5e1';
      ctx.font = '12px Inter, sans-serif';
      ctx.fillText(
        new Date(person.content.birthDate).getFullYear().toString(),
        person.x + 10,
        person.y + 45
      );
    }
    
    // Bio (truncated)
    if (person.content.bio) {
      ctx.fillStyle = '#94a3b8';
      ctx.font = '11px Inter, sans-serif';
      const truncatedBio = person.content.bio.length > 25 
        ? person.content.bio.substring(0, 25) + '...' 
        : person.content.bio;
      ctx.fillText(truncatedBio, person.x + 10, person.y + 65);
    }
    
    // Spouse indicator
    if (person.content.spouse) {
      ctx.fillStyle = '#ef4444';
      ctx.font = '12px Inter, sans-serif';
      ctx.fillText('♥', person.x + width - 15, person.y + height - 10);
    }
  };

  const drawConnections = (ctx, arrangedPersons) => {
    ctx.strokeStyle = '#64748b';
    ctx.lineWidth = 2;
    
    arrangedPersons.forEach(person => {
      // Draw parent-child connections
      if (person.content.parents) {
        person.content.parents.forEach(parentId => {
          const parent = arrangedPersons.find(p => p.id === parentId);
          if (parent) {
            ctx.beginPath();
            ctx.moveTo(parent.x + 80, parent.y + 100);
            ctx.lineTo(person.x + 80, person.y);
            ctx.stroke();
          }
        });
      }
      
      // Draw spouse connections
      if (person.content.spouse) {
        const spouse = arrangedPersons.find(p => p.id === person.content.spouse);
        if (spouse) {
          ctx.strokeStyle = '#ef4444';
          ctx.beginPath();
          ctx.moveTo(person.x + 160, person.y + 50);
          ctx.lineTo(spouse.x, spouse.y + 50);
          ctx.stroke();
          ctx.strokeStyle = '#64748b';
        }
      }
    });
  };

  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) / zoom - pan.x;
    const y = (e.clientY - rect.top) / zoom - pan.y;
    
    const arrangedPersons = arrangePersonsInTree();
    const clickedPerson = arrangedPersons.find(person =>
      x >= person.x && x <= person.x + 160 &&
      y >= person.y && y <= person.y + 100
    );
    
    if (clickedPerson) {
      setSelectedPerson(clickedPerson);
    } else {
      setSelectedPerson(null);
    }
  };

  const handleCanvasDoubleClick = (e) => {
    if (selectedPerson) {
      openEditPersonModal(selectedPerson);
    } else {
      openNewPersonModal();
    }
  };

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e) => {
    if (isDragging && !selectedPerson) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const openNewPersonModal = () => {
    setSelectedPerson(null);
    setPersonForm({
      name: '',
      birthDate: '',
      bio: '',
      gender: 'other',
      parents: [],
      spouse: null
    });
    setIsPersonModalOpen(true);
  };

  const openEditPersonModal = (person) => {
    setSelectedPerson(person);
    setPersonForm({
      name: person.content.name || person.title,
      birthDate: person.content.birthDate || '',
      bio: person.content.bio || '',
      gender: person.content.gender || 'other',
      parents: person.content.parents || [],
      spouse: person.content.spouse || null
    });
    setIsPersonModalOpen(true);
  };

  const savePerson = async () => {
    if (!personForm.name.trim()) return;
    
    const personData = {
      node_type: 'family-person',
      title: personForm.name.trim(),
      content: {
        name: personForm.name.trim(),
        birthDate: personForm.birthDate,
        bio: personForm.bio,
        gender: personForm.gender,
        parents: personForm.parents,
        spouse: personForm.spouse
      },
      tags: ['family']
    };

    try {
      if (selectedPerson) {
        await api.updateNode(selectedPerson.id, personData);
      } else {
        await api.createNode(personData);
      }
      setIsPersonModalOpen(false);
    } catch (error) {
      console.error('Failed to save person:', error);
    }
  };

  const deletePerson = async () => {
    if (!selectedPerson) return;
    
    try {
      await api.deleteNode(selectedPerson.id);
      setSelectedPerson(null);
      setIsPersonModalOpen(false);
    } catch (error) {
      console.error('Failed to delete person:', error);
    }
  };

  return (
    <div className="h-full bg-slate-900 flex flex-col" data-testid="family-tree">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-white flex items-center gap-3">
            <Users className="h-6 w-6 text-green-400" />
            Family Tree
          </h1>
          
          <div className="text-sm text-slate-400">
            {persons.length} family members
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setZoom(Math.max(0.1, zoom - 0.1))}
            data-testid="zoom-out-family"
          >
            -
          </Button>
          
          <span className="text-sm text-slate-400 w-12 text-center">
            {Math.round(zoom * 100)}%
          </span>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => setZoom(Math.min(3, zoom + 0.1))}
            data-testid="zoom-in-family"
          >
            +
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setZoom(1);
              setPan({ x: 0, y: 0 });
            }}
            data-testid="reset-family-view"
          >
            Reset
          </Button>
          
          <Button
            size="sm"
            onClick={openNewPersonModal}
            className="bg-green-600 hover:bg-green-700"
            data-testid="add-family-member-btn"
          >
            <Plus className="h-4 w-4 mr-1" />
            Add Person
          </Button>
        </div>
      </div>

      {/* Family Tree Canvas */}
      <div className="flex-1 relative overflow-hidden">
        <canvas
          ref={canvasRef}
          className="w-full h-full cursor-move"
          onClick={handleCanvasClick}
          onDoubleClick={handleCanvasDoubleClick}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          data-testid="family-tree-canvas"
        />
        
        {persons.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-center text-slate-400">
              <Users className="h-16 w-16 mx-auto mb-4 text-slate-500" />
              <div className="text-xl font-medium mb-2">No Family Members</div>
              <div className="text-sm">
                Add your first family member to start building your tree
              </div>
            </div>
          </div>
        )}
        
        {/* Selected Person Info */}
        {selectedPerson && (
          <div className="absolute bottom-4 left-4 bg-slate-800 border border-slate-700 rounded-lg p-4 max-w-sm">
            <div className="flex items-center gap-3 mb-2">
              <User className="h-5 w-5 text-green-400" />
              <div className="font-medium text-white">
                {selectedPerson.content.name || selectedPerson.title}
              </div>
            </div>
            
            {selectedPerson.content.birthDate && (
              <div className="text-sm text-slate-400 mb-2">
                Born: {new Date(selectedPerson.content.birthDate).toLocaleDateString()}
              </div>
            )}
            
            {selectedPerson.content.bio && (
              <div className="text-sm text-slate-300 mb-3">
                {selectedPerson.content.bio}
              </div>
            )}
            
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => openEditPersonModal(selectedPerson)}
                data-testid="edit-selected-person-btn"
              >
                <Edit className="h-3 w-3 mr-1" />
                Edit
              </Button>
              
              <Button
                size="sm"
                variant="outline"
                onClick={() => actions.setSelectedNode(selectedPerson)}
                className="text-blue-400 border-blue-400"
                data-testid="link-selected-person-btn"
              >
                <LinkIcon className="h-3 w-3 mr-1" />
                Link
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Person Modal */}
      <Dialog open={isPersonModalOpen} onOpenChange={setIsPersonModalOpen}>
        <DialogContent className="max-w-lg bg-slate-800 border-slate-700" data-testid="person-modal">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <User className="h-5 w-5 text-green-400" />
              {selectedPerson ? 'Edit Person' : 'Add Family Member'}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            {/* Name */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Full Name *
              </label>
              <Input
                placeholder="Enter full name..."
                value={personForm.name}
                onChange={(e) => setPersonForm({ ...personForm, name: e.target.value })}
                className="bg-slate-700 border-slate-600 text-white"
                data-testid="person-name-input"
              />
            </div>

            {/* Birth Date and Gender */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Birth Date
                </label>
                <Input
                  type="date"
                  value={personForm.birthDate}
                  onChange={(e) => setPersonForm({ ...personForm, birthDate: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="person-birth-date-input"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Gender
                </label>
                <select
                  value={personForm.gender}
                  onChange={(e) => setPersonForm({ ...personForm, gender: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2"
                  data-testid="person-gender-select"
                >
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            {/* Bio */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Biography
              </label>
              <textarea
                placeholder="Brief biography or notes..."
                value={personForm.bio}
                onChange={(e) => setPersonForm({ ...personForm, bio: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2 resize-none"
                rows={3}
                data-testid="person-bio-input"
              />
            </div>

            {/* Relationships */}
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Parents
              </label>
              <select
                multiple
                value={personForm.parents}
                onChange={(e) => {
                  const selected = Array.from(e.target.selectedOptions, option => option.value);
                  setPersonForm({ ...personForm, parents: selected });
                }}
                className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2 h-20"
                data-testid="person-parents-select"
              >
                {persons.filter(p => p.id !== selectedPerson?.id).map(person => (
                  <option key={person.id} value={person.id}>
                    {person.content.name || person.title}
                  </option>
                ))}
              </select>
              <div className="text-xs text-slate-400 mt-1">
                Hold Ctrl/Cmd to select multiple parents
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Spouse
              </label>
              <select
                value={personForm.spouse || ''}
                onChange={(e) => setPersonForm({ ...personForm, spouse: e.target.value || null })}
                className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2"
                data-testid="person-spouse-select"
              >
                <option value="">No spouse</option>
                {persons.filter(p => p.id !== selectedPerson?.id).map(person => (
                  <option key={person.id} value={person.id}>
                    {person.content.name || person.title}
                  </option>
                ))}
              </select>
            </div>

            {/* Actions */}
            <div className="flex justify-between pt-4">
              <div>
                {selectedPerson && (
                  <Button
                    variant="outline"
                    onClick={deletePerson}
                    className="text-red-400 border-red-400 hover:bg-red-400 hover:text-white"
                    data-testid="delete-person-btn"
                  >
                    <Trash className="h-4 w-4 mr-1" />
                    Delete
                  </Button>
                )}
              </div>
              
              <div className="flex gap-3">
                <Button 
                  variant="outline" 
                  onClick={() => setIsPersonModalOpen(false)}
                  data-testid="cancel-person-btn"
                >
                  Cancel
                </Button>
                <Button
                  onClick={savePerson}
                  disabled={!personForm.name.trim()}
                  className="bg-green-600 hover:bg-green-700"
                  data-testid="save-person-btn"
                >
                  {selectedPerson ? 'Update' : 'Add'} Person
                </Button>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}