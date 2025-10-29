import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  BookOpen, 
  Plus, 
  ChevronRight, 
  ChevronDown,
  FileText,
  FolderPlus,
  Link,
  Edit,
  Trash
} from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

export default function Notebook() {
  const [selectedPage, setSelectedPage] = useState(null);
  const [expandedSections, setExpandedSections] = useState(new Set(['root']));
  const [isCreating, setIsCreating] = useState(false);
  const [createType, setCreateType] = useState('page');
  const [createParent, setCreateParent] = useState(null);
  const [newTitle, setNewTitle] = useState('');
  const [pageContent, setPageContent] = useState('');
  
  const { nodes, api, actions } = useWorkspace();
  
  const notebookItems = nodes.filter(node => 
    node.node_type === 'notebook-page' || node.node_type === 'notebook-section'
  );

  useEffect(() => {
    if (selectedPage) {
      setPageContent(selectedPage.content.markdown || '');
    }
  }, [selectedPage]);

  const buildHierarchy = () => {
    const hierarchy = { id: 'root', title: 'Notebook', children: [], type: 'section' };
    const itemsMap = new Map();
    
    // Create map of all items
    notebookItems.forEach(item => {
      itemsMap.set(item.id, { ...item, children: [] });
    });
    
    // Build parent-child relationships
    notebookItems.forEach(item => {
      const parentId = item.content.parentId || 'root';
      if (parentId === 'root') {
        hierarchy.children.push(itemsMap.get(item.id));
      } else {
        const parent = itemsMap.get(parentId);
        if (parent) {
          parent.children.push(itemsMap.get(item.id));
        }
      }
    });
    
    return hierarchy;
  };

  const toggleExpanded = (itemId) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedSections(newExpanded);
  };

  const createItem = async () => {
    if (!newTitle.trim()) return;
    
    const itemData = {
      node_type: createType === 'section' ? 'notebook-section' : 'notebook-page',
      title: newTitle.trim(),
      content: {
        parentId: createParent,
        markdown: createType === 'page' ? '# ' + newTitle.trim() + '\n\nStart writing...' : '',
        order: 0
      },
      tags: ['notebook']
    };

    try {
      const newItem = await api.createNode(itemData);
      if (createType === 'page') {
        setSelectedPage(newItem);
      }
      setIsCreating(false);
      setNewTitle('');
      setCreateParent(null);
    } catch (error) {
      console.error('Failed to create notebook item:', error);
    }
  };

  const savePage = async () => {
    if (!selectedPage) return;
    
    try {
      await api.updateNode(selectedPage.id, {
        ...selectedPage,
        content: { ...selectedPage.content, markdown: pageContent }
      });
    } catch (error) {
      console.error('Failed to save page:', error);
    }
  };

  const deleteItem = async (item) => {
    try {
      await api.deleteNode(item.id);
      if (selectedPage?.id === item.id) {
        setSelectedPage(null);
      }
    } catch (error) {
      console.error('Failed to delete item:', error);
    }
  };

  const renderTreeItem = (item, level = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedSections.has(item.id);
    const isSelected = selectedPage?.id === item.id;
    const isSection = item.node_type === 'notebook-section' || item.type === 'section';

    return (
      <div key={item.id || item.title}>
        <div
          className={`flex items-center gap-2 py-1 px-2 rounded cursor-pointer hover:bg-slate-700 ${
            isSelected ? 'bg-slate-700 text-white' : 'text-slate-300'
          }`}
          style={{ paddingLeft: `${level * 20 + 8}px` }}
          onClick={() => {
            if (isSection) {
              toggleExpanded(item.id);
            } else {
              setSelectedPage(item);
            }
          }}
          data-testid={`notebook-item-${item.id}`}
        >
          {hasChildren ? (
            isExpanded ? (
              <ChevronDown className="h-4 w-4 text-slate-400" />
            ) : (
              <ChevronRight className="h-4 w-4 text-slate-400" />
            )
          ) : (
            <div className="w-4" />
          )}
          
          {isSection ? (
            <BookOpen className="h-4 w-4 text-indigo-400" />
          ) : (
            <FileText className="h-4 w-4 text-slate-400" />
          )}
          
          <span className="flex-1 text-sm truncate">{item.title}</span>
          
          {!isSection && (
            <div className="flex gap-1 opacity-0 group-hover:opacity-100">
              <Button
                size="sm"
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation();
                  actions.setSelectedNode(item);
                }}
                className="h-5 w-5 p-0 text-blue-400 hover:text-blue-300"
              >
                <Link className="h-3 w-3" />
              </Button>
              
              <Button
                size="sm"
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation();
                  deleteItem(item);
                }}
                className="h-5 w-5 p-0 text-red-400 hover:text-red-300"
              >
                <Trash className="h-3 w-3" />
              </Button>
            </div>
          )}
        </div>
        
        {hasChildren && isExpanded && (
          <div>
            {item.children.map(child => renderTreeItem(child, level + 1))}
          </div>
        )}
        
        {isSection && isExpanded && (
          <div style={{ paddingLeft: `${(level + 1) * 20 + 8}px` }}>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setCreateParent(item.id === 'root' ? null : item.id);
                setCreateType('page');
                setIsCreating(true);
              }}
              className="text-slate-400 hover:text-white text-xs h-6"
              data-testid={`add-page-${item.id}`}
            >
              <Plus className="h-3 w-3 mr-1" />
              Add Page
            </Button>
          </div>
        )}
      </div>
    );
  };

  const hierarchy = buildHierarchy();

  return (
    <div className="flex h-full bg-slate-900" data-testid="notebook">
      {/* Sidebar - Table of Contents */}
      <div className="w-80 border-r border-slate-700 bg-slate-800 flex flex-col">
        <div className="p-4 border-b border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-indigo-400" />
              Notebook
            </h2>
            
            <div className="flex gap-1">
              <Button
                size="sm"
                onClick={() => {
                  setCreateParent(null);
                  setCreateType('section');
                  setIsCreating(true);
                }}
                className="bg-indigo-600 hover:bg-indigo-700 h-8"
                data-testid="add-section-btn"
              >
                <FolderPlus className="h-4 w-4" />
              </Button>
              
              <Button
                size="sm"
                onClick={() => {
                  setCreateParent(null);
                  setCreateType('page');
                  setIsCreating(true);
                }}
                className="bg-indigo-600 hover:bg-indigo-700 h-8"
                data-testid="add-page-btn"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          {isCreating && (
            <div className="space-y-2 p-3 bg-slate-700 rounded border">
              <Input
                placeholder={`New ${createType} title...`}
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && createItem()}
                className="bg-slate-600 border-slate-500 text-white text-sm"
                data-testid="new-item-title-input"
                autoFocus
              />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={createItem}
                  disabled={!newTitle.trim()}
                  className="bg-indigo-600 hover:bg-indigo-700"
                  data-testid="create-item-btn"
                >
                  Create
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setIsCreating(false);
                    setNewTitle('');
                  }}
                  data-testid="cancel-create-btn"
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {renderTreeItem(hierarchy)}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {selectedPage ? (
          <>
            {/* Page Header */}
            <div className="p-4 border-b border-slate-700 bg-slate-800">
              <div className="flex items-center justify-between">
                <h1 className="text-xl font-semibold text-white">
                  {selectedPage.title}
                </h1>
                
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => actions.setSelectedNode(selectedPage)}
                    className="text-blue-400 border-blue-400 hover:bg-blue-400 hover:text-white"
                    data-testid="link-page-btn"
                  >
                    <Link className="h-4 w-4 mr-1" />
                    Link
                  </Button>
                  
                  <Button
                    size="sm"
                    onClick={savePage}
                    className="bg-indigo-600 hover:bg-indigo-700"
                    data-testid="save-page-btn"
                  >
                    Save Page
                  </Button>
                </div>
              </div>
            </div>

            {/* Page Content Editor */}
            <div className="flex-1 p-4">
              <Textarea
                placeholder="Write your page content using Markdown..."
                value={pageContent}
                onChange={(e) => setPageContent(e.target.value)}
                className="w-full h-full resize-none border-slate-600 bg-slate-800 text-white text-base leading-relaxed"
                data-testid="page-content-editor"
              />
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center text-slate-400">
              <BookOpen className="h-16 w-16 mx-auto mb-4 text-slate-500" />
              <div className="text-xl font-medium mb-2">Welcome to your Notebook</div>
              <div className="text-sm mb-4">
                Create sections and pages to organize your knowledge
              </div>
              
              <div className="flex gap-3 justify-center">
                <Button
                  onClick={() => {
                    setCreateParent(null);
                    setCreateType('section');
                    setIsCreating(true);
                  }}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  <FolderPlus className="h-4 w-4 mr-2" />
                  Create Section
                </Button>
                
                <Button
                  onClick={() => {
                    setCreateParent(null);
                    setCreateType('page');
                    setIsCreating(true);
                  }}
                  variant="outline"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Create Page
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}