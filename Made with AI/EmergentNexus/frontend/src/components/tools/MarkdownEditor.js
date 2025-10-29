import React, { useState, useEffect } from 'react';
import { marked } from 'marked';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, 
  Edit3, 
  Eye, 
  Save, 
  Plus, 
  Link,
  Hash,
  X
} from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

export default function MarkdownEditor() {
  const [isEditing, setIsEditing] = useState(true);
  const [currentNote, setCurrentNote] = useState(null);
  const [content, setContent] = useState('');
  const [title, setTitle] = useState('');
  const [tags, setTags] = useState([]);
  const [newTag, setNewTag] = useState('');
  const [saving, setSaving] = useState(false);
  const [isCreatingNew, setIsCreatingNew] = useState(false);
  
  const { nodes, api, actions, relations } = useWorkspace();
  
  const markdownNotes = nodes.filter(node => node.node_type === 'markdown');
  
  useEffect(() => {
    if (markdownNotes.length > 0 && !currentNote && !isCreatingNew) {
      setCurrentNote(markdownNotes[0]);
    }
  }, [markdownNotes, currentNote, isCreatingNew]);

  useEffect(() => {
    if (currentNote) {
      setTitle(currentNote.title);
      setContent(currentNote.content.markdown || '');
      setTags(currentNote.tags || []);
    }
  }, [currentNote]);

  const handleSave = async () => {
    if (!title.trim()) return;
    
    setSaving(true);
    try {
      const noteData = {
        node_type: 'markdown',
        title: title.trim(),
        content: { markdown: content },
        tags: tags
      };

      if (currentNote) {
        await api.updateNode(currentNote.id, noteData);
        setCurrentNote({ ...currentNote, ...noteData });
      } else {
        const newNote = await api.createNode(noteData);
        setCurrentNote(newNote);
        setIsCreatingNew(false);
      }
    } finally {
      setSaving(false);
    }
  };

  const handleNewNote = () => {
    setIsCreatingNew(true);
    setCurrentNote(null);
    setTitle('');
    setContent('');
    setTags([]);
    setIsEditing(true);
  };

  const addTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      setTags([...tags, newTag.trim()]);
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSave();
    }
  };

  const processMarkdownWithLinks = (text) => {
    // Process [[wiki-links]] to other nodes first
    const processedText = text.replace(/\[\[([^\]]+)\]\]/g, (match, linkText) => {
      const linkedNode = nodes.find(node => 
        node.title.toLowerCase() === linkText.toLowerCase()
      );
      
      if (linkedNode) {
        return `[${linkText}](#node-${linkedNode.id}) 🔗`;
      }
      return `${linkText} ❓`;
    });
    
    return processedText;
  };

  const renderMarkdownPreview = (text) => {
    try {
      const processedText = processMarkdownWithLinks(text);
      return marked.parse(processedText);
    } catch (error) {
      console.error('Markdown parsing error:', error);
      return `<p>Error parsing markdown: ${error.message}</p>`;
    }
  };

  const getNodeConnections = () => {
    if (!currentNote) return [];
    
    return relations.filter(rel => 
      rel.from_id === currentNote.id || rel.to_id === currentNote.id
    ).map(rel => {
      const connectedNodeId = rel.from_id === currentNote.id ? rel.to_id : rel.from_id;
      const connectedNode = nodes.find(n => n.id === connectedNodeId);
      return { relation: rel, node: connectedNode };
    }).filter(conn => conn.node);
  };

  return (
    <div className="flex h-full bg-slate-900 flex-col md:flex-row" data-testid="markdown-editor">
      {/* Note List Sidebar */}
      <div className="w-full md:w-80 border-r-0 md:border-r border-b md:border-b-0 border-slate-700 bg-slate-800 flex flex-col max-h-48 md:max-h-full overflow-hidden">
        <div className="p-3 md:p-4 border-b border-slate-700">
          <div className="flex items-center justify-between mb-2 md:mb-4">
            <h2 className="text-base md:text-lg font-semibold text-white flex items-center gap-2">
              <FileText className="h-4 md:h-5 w-4 md:w-5 text-emerald-400" />
              <span className="hidden sm:inline">Notes</span>
            </h2>
            <Button
              size="sm"
              onClick={handleNewNote}
              className="bg-emerald-600 hover:bg-emerald-700 px-2 md:px-3"
              data-testid="new-note-btn"
            >
              <Plus className="h-4 w-4 md:mr-1" />
              <span className="hidden md:inline">New</span>
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-2">
            {markdownNotes.map((note) => (
              <Button
                key={note.id}
                variant={currentNote?.id === note.id ? "secondary" : "ghost"}
                className={`w-full justify-start p-3 h-auto text-left ${
                  currentNote?.id === note.id
                    ? 'bg-slate-700 text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-700'
                }`}
                onClick={() => setCurrentNote(note)}
                data-testid={`note-item-${note.id}`}
              >
                <div className="w-full">
                  <div className="font-medium truncate">{note.title}</div>
                  <div className="text-xs text-slate-400 mt-1">
                    {new Date(note.updated_at).toLocaleDateString()}
                  </div>
                  {note.tags && note.tags.length > 0 && (
                    <div className="flex gap-1 mt-2 flex-wrap">
                      {note.tags.slice(0, 2).map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {note.tags.length > 2 && (
                        <Badge variant="outline" className="text-xs">
                          +{note.tags.length - 2}
                        </Badge>
                      )}
                    </div>
                  )}
                </div>
              </Button>
            ))}
            
            {markdownNotes.length === 0 && (
              <div className="text-center text-slate-400 py-8">
                No notes created yet.
                <br />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleNewNote}
                  className="mt-2"
                >
                  Create your first note
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Editor Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="p-3 md:p-4 border-b border-slate-700 bg-slate-800">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 md:gap-4 mb-2 md:mb-4">
            <input
              type="text"
              placeholder="Note title..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="text-lg md:text-xl font-semibold bg-transparent text-white placeholder-slate-400 border-none outline-none flex-1 min-w-0"
              data-testid="note-title-input"
            />
            
            <div className="flex items-center gap-1 md:gap-2 flex-shrink-0">
              {currentNote && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => actions.setSelectedNode(currentNote)}
                  className="text-blue-400 border-blue-400 hover:bg-blue-400 hover:text-white"
                  data-testid="link-note-btn"
                >
                  <Link className="h-4 w-4 mr-1" />
                  Link
                </Button>
              )}
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(!isEditing)}
                className={`${isEditing ? 'text-emerald-400' : 'text-blue-400'} px-2 md:px-3`}
                data-testid="toggle-edit-btn"
              >
                {isEditing ? <Eye className="h-4 w-4 md:mr-1" /> : <Edit3 className="h-4 w-4 md:mr-1" />}
                <span className="hidden md:inline">{isEditing ? 'Preview' : 'Edit'}</span>
              </Button>
              
              <Button
                size="sm"
                onClick={handleSave}
                disabled={!title.trim() || saving}
                className="bg-emerald-600 hover:bg-emerald-700 px-2 md:px-3"
                data-testid="save-note-btn"
              >
                <Save className="h-4 w-4 md:mr-1" />
                <span className="hidden md:inline">{saving ? 'Saving...' : 'Save'}</span>
              </Button>
            </div>
          </div>

          {/* Tags */}
          <div className="flex items-center gap-2 flex-wrap">
            {tags.map((tag) => (
              <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                <Hash className="h-3 w-3" />
                {tag}
                <X 
                  className="h-3 w-3 cursor-pointer hover:text-red-400" 
                  onClick={() => removeTag(tag)}
                />
              </Badge>
            ))}
            
            <div className="flex items-center gap-2">
              <input
                type="text"
                placeholder="Add tag..."
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addTag()}
                className="text-sm bg-slate-700 text-white placeholder-slate-400 border border-slate-600 rounded px-2 py-1 w-24 outline-none"
                data-testid="new-tag-input"
              />
              <Button size="sm" variant="outline" onClick={addTag}>
                <Plus className="h-3 w-3" />
              </Button>
            </div>
          </div>
          
          {/* Connections */}
          {getNodeConnections().length > 0 && (
            <div className="mt-4">
              <div className="text-sm text-slate-400 mb-2">Connected to:</div>
              <div className="flex gap-2 flex-wrap">
                {getNodeConnections().map(({ node, relation }) => (
                  <Badge key={node.id} variant="outline" className="text-blue-400 border-blue-400">
                    <Link className="h-3 w-3 mr-1" />
                    {node.title}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden">
          {isEditing ? (
            <Textarea
              placeholder="Start writing your note... Use [[Node Title]] to link to other nodes."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              onKeyDown={handleKeyPress}
              className="w-full h-full resize-none border-none bg-slate-900 text-white text-base leading-relaxed p-6 focus:ring-0 focus:border-none"
              data-testid="note-content-editor"
            />
          ) : (
            <div className="h-full overflow-y-auto p-6">
              {content.trim() ? (
                <div 
                  className="prose prose-invert prose-slate max-w-none"
                  dangerouslySetInnerHTML={{ 
                    __html: renderMarkdownPreview(content) 
                  }}
                  data-testid="markdown-preview"
                />
              ) : (
                <div className="text-slate-400 text-center py-12">
                  <Eye className="h-12 w-12 mx-auto mb-4 text-slate-500" />
                  <div className="text-lg font-medium mb-2">Nothing to Preview</div>
                  <div className="text-sm mb-4">
                    Switch to edit mode and write some markdown to see the preview
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsEditing(true)}
                    className="mt-2"
                  >
                    <Edit3 className="h-4 w-4 mr-1" />
                    Start Writing
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}