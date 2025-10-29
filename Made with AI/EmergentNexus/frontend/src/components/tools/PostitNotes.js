import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  StickyNote, 
  Plus, 
  X, 
  Hash,
  Link,
  Edit,
  Trash
} from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

const colors = [
  'bg-yellow-200 text-yellow-800',
  'bg-blue-200 text-blue-800',
  'bg-green-200 text-green-800',
  'bg-pink-200 text-pink-800',
  'bg-purple-200 text-purple-800',
  'bg-red-200 text-red-800'
];

export default function PostitNotes() {
  const [newNote, setNewNote] = useState('');
  const [selectedNote, setSelectedNote] = useState(null);
  const [isEditing, setIsEditing] = useState(null);
  const [editText, setEditText] = useState('');
  const [newTag, setNewTag] = useState('');
  
  const { nodes, api, actions } = useWorkspace();
  
  const postitNotes = React.useMemo(() => 
    nodes.filter(node => node.node_type === 'postit-note'), 
    [nodes]
  );

  const createNote = async () => {
    if (!newNote.trim()) return;
    
    const noteData = {
      node_type: 'postit-note',
      title: newNote.trim(),
      content: {
        text: newNote.trim(),
        color: colors[Math.floor(Math.random() * colors.length)],
        x: Math.random() * 600 + 50,
        y: Math.random() * 400 + 50
      },
      tags: []
    };

    try {
      await api.createNode(noteData);
      setNewNote('');
    } catch (error) {
      console.error('Failed to create post-it note:', error);
    }
  };

  const updateNote = async (note, newText) => {
    try {
      await api.updateNode(note.id, {
        ...note,
        title: newText,
        content: { ...note.content, text: newText }
      });
      setIsEditing(null);
      setEditText('');
    } catch (error) {
      console.error('Failed to update note:', error);
    }
  };

  const deleteNote = async (noteId) => {
    try {
      await api.deleteNode(noteId);
      setSelectedNote(null);
    } catch (error) {
      console.error('Failed to delete note:', error);
    }
  };

  const addTag = async (note, tag) => {
    if (tag.trim() && !note.tags.includes(tag.trim())) {
      try {
        await api.updateNode(note.id, {
          ...note,
          tags: [...note.tags, tag.trim()]
        });
      } catch (error) {
        console.error('Failed to add tag:', error);
      }
    }
  };

  const removeTag = async (note, tagToRemove) => {
    try {
      await api.updateNode(note.id, {
        ...note,
        tags: note.tags.filter(tag => tag !== tagToRemove)
      });
    } catch (error) {
      console.error('Failed to remove tag:', error);
    }
  };

  return (
    <div className="h-full bg-slate-900 p-6 overflow-auto" data-testid="postit-notes">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <StickyNote className="h-6 w-6 text-yellow-400" />
          Post-it Notes
        </h1>
        
        <div className="text-sm text-slate-400">
          {postitNotes.length} notes
        </div>
      </div>

      {/* New Note Input */}
      <div className="mb-6 bg-slate-800 rounded-lg p-4 border border-slate-700">
        <div className="flex gap-3">
          <Input
            placeholder="Add a quick note..."
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && createNote()}
            className="flex-1 bg-slate-700 border-slate-600 text-white"
            data-testid="new-postit-input"
          />
          <Button
            onClick={createNote}
            disabled={!newNote.trim()}
            className="bg-yellow-600 hover:bg-yellow-700"
            data-testid="add-postit-btn"
          >
            <Plus className="h-4 w-4 mr-1" />
            Add Note
          </Button>
        </div>
      </div>

      {/* Notes Board */}
      <div className="relative min-h-96 bg-slate-800 rounded-lg border border-slate-700 p-4">
        {postitNotes.length === 0 ? (
          <div className="text-center text-slate-400 py-12">
            <StickyNote className="h-12 w-12 mx-auto mb-4 text-slate-500" />
            <div className="text-lg font-medium mb-2">No Post-it Notes Yet</div>
            <div className="text-sm">Add your first quick note above</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {postitNotes.map((note) => (
              <div
                key={note.id}
                className={`relative p-4 rounded-lg shadow-lg cursor-pointer transform transition-all hover:scale-105 hover:shadow-xl ${
                  note.content.color || 'bg-yellow-200 text-yellow-800'
                }`}
                onClick={() => setSelectedNote(selectedNote?.id === note.id ? null : note)}
                data-testid={`postit-note-${note.id}`}
              >
                {/* Note Content */}
                {isEditing === note.id ? (
                  <textarea
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    onBlur={() => updateNote(note, editText)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        updateNote(note, editText);
                      }
                    }}
                    className="w-full bg-transparent border-none outline-none resize-none text-sm font-medium"
                    rows={3}
                    autoFocus
                  />
                ) : (
                  <div
                    className="text-sm font-medium leading-relaxed break-words min-h-16"
                    onDoubleClick={() => {
                      setIsEditing(note.id);
                      setEditText(note.content.text || note.title);
                    }}
                  >
                    {note.content.text || note.title}
                  </div>
                )}

                {/* Tags */}
                {note.tags && note.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-3">
                    {note.tags.slice(0, 3).map((tag) => (
                      <Badge
                        key={tag}
                        variant="secondary"
                        className="text-xs opacity-80"
                      >
                        #{tag}
                      </Badge>
                    ))}
                    {note.tags.length > 3 && (
                      <Badge variant="secondary" className="text-xs opacity-80">
                        +{note.tags.length - 3}
                      </Badge>
                    )}
                  </div>
                )}

                {/* Actions (show on selected) */}
                {selectedNote?.id === note.id && (
                  <div className="absolute -top-2 -right-2 flex gap-1">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={(e) => {
                        e.stopPropagation();
                        setIsEditing(note.id);
                        setEditText(note.content.text || note.title);
                      }}
                      className="h-6 w-6 p-0 bg-white hover:bg-gray-100 text-gray-700"
                      data-testid={`edit-postit-${note.id}`}
                    >
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={(e) => {
                        e.stopPropagation();
                        actions.setSelectedNode(note);
                      }}
                      className="h-6 w-6 p-0 bg-blue-500 hover:bg-blue-600 text-white"
                      data-testid={`link-postit-${note.id}`}
                    >
                      <Link className="h-3 w-3" />
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteNote(note.id);
                      }}
                      className="h-6 w-6 p-0"
                      data-testid={`delete-postit-${note.id}`}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                )}

                {/* Date */}
                <div className="text-xs opacity-60 mt-3">
                  {new Date(note.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Selected Note Details Panel */}
      {selectedNote && (
        <div className="mt-6 bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Note Details</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSelectedNote(null)}
              className="text-slate-400"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="space-y-3">
            <div>
              <span className="text-sm text-slate-400">Content: </span>
              <span className="text-white">{selectedNote.content.text || selectedNote.title}</span>
            </div>
            
            <div>
              <span className="text-sm text-slate-400">Created: </span>
              <span className="text-white">{new Date(selectedNote.created_at).toLocaleString()}</span>
            </div>
            
            {/* Tag Management */}
            <div>
              <div className="text-sm text-slate-400 mb-2">Tags:</div>
              <div className="flex flex-wrap gap-2 mb-2">
                {selectedNote.tags.map((tag) => (
                  <Badge
                    key={tag}
                    variant="secondary"
                    className="flex items-center gap-1"
                  >
                    <Hash className="h-3 w-3" />
                    {tag}
                    <X
                      className="h-3 w-3 cursor-pointer hover:text-red-400"
                      onClick={() => removeTag(selectedNote, tag)}
                    />
                  </Badge>
                ))}
              </div>
              
              <div className="flex gap-2">
                <Input
                  placeholder="Add tag..."
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      addTag(selectedNote, newTag);
                      setNewTag('');
                    }
                  }}
                  className="bg-slate-700 border-slate-600 text-white text-sm"
                  data-testid="add-tag-input"
                />
                <Button
                  size="sm"
                  onClick={() => {
                    addTag(selectedNote, newTag);
                    setNewTag('');
                  }}
                  disabled={!newTag.trim()}
                  data-testid="add-tag-btn"
                >
                  Add
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}