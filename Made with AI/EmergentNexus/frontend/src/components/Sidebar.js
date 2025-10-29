import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { 
  FileText, 
  Trello, 
  Network, 
  PanelLeft,
  Search,
  Plus,
  Settings,
  StickyNote,
  BookOpen,
  Pen,
  Users,
  Table,
  Calendar
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useWorkspace } from '../contexts/WorkspaceContext';
import SettingsModal from './SettingsModal';

const tools = [
  { id: 'markdown', name: 'Markdown Editor', icon: FileText, color: 'text-emerald-400' },
  { id: 'kanban', name: 'Kanban Board', icon: Trello, color: 'text-blue-400' },
  { id: 'evidence', name: 'Evidence Board', icon: Network, color: 'text-purple-400' },
  { id: 'postit', name: 'Post-it Notes', icon: StickyNote, color: 'text-yellow-400' },
  { id: 'notebook', name: 'Notebook', icon: BookOpen, color: 'text-indigo-400' },
  { id: 'canvas', name: 'Canvas', icon: Pen, color: 'text-pink-400' },
  { id: 'family', name: 'Family Tree', icon: Users, color: 'text-green-400' },
  { id: 'assets', name: 'Asset Management', icon: Table, color: 'text-orange-400' },
  { id: 'projects', name: 'Project Timeline', icon: Calendar, color: 'text-red-400' },
];

export default function Sidebar({ collapsed, onToggle }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const { actions, nodes } = useWorkspace();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get current tool from URL
  const currentTool = location.pathname.split('/')[1] || 'markdown';

  const filteredNodes = nodes.filter(node =>
    node.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    node.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className={`fixed left-0 top-0 h-full bg-slate-800 border-r border-slate-700 transition-all duration-300 z-50 ${
      collapsed 
        ? 'w-16 -translate-x-full md:translate-x-0' 
        : 'w-72 translate-x-0 md:w-64'
    }`}>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center justify-between p-3 md:p-4 border-b border-slate-700">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="text-slate-400 hover:text-white"
            data-testid="sidebar-toggle-btn"
          >
            <PanelLeft className="h-4 w-4" />
          </Button>
          {!collapsed && (
            <div className="flex items-center gap-2">
              <h1 className="text-base md:text-lg font-semibold text-white animate-fadeIn">
                Nexus
              </h1>
              <div className="hidden sm:block text-xs text-slate-500 bg-slate-700 px-2 py-1 rounded">
                {currentTool}
              </div>
            </div>
          )}
        </div>

        {/* Search */}
        {!collapsed && (
          <div className="p-4 border-b border-slate-700 animate-fadeIn">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search nodes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-slate-700 border-slate-600 text-white placeholder-slate-400"
                data-testid="sidebar-search-input"
              />
            </div>
          </div>
        )}

        {/* Tools */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4 space-y-2">
            {!collapsed && (
              <h2 className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-3 animate-fadeIn">
                Tools
              </h2>
            )}
            
            {tools.map((tool) => {
              const Icon = tool.icon;
              const isActive = currentTool === tool.id;
              
              return (
                <Link
                  key={tool.id}
                  to={`/${tool.id}`}
                  className="w-full"
                  onClick={() => actions.setCurrentTool(tool.id)}
                >
                  <Button
                    variant={isActive ? "secondary" : "ghost"}
                    className={`w-full justify-start gap-3 transition-all duration-200 ${
                      isActive 
                        ? 'bg-slate-700 text-white' 
                        : 'text-slate-400 hover:text-white hover:bg-slate-700'
                    }`}
                    data-testid={`tool-${tool.id}-btn`}
                  >
                    <Icon className={`h-4 w-4 ${tool.color}`} />
                    {!collapsed && (
                      <span className="animate-slideIn">{tool.name}</span>
                    )}
                  </Button>
                </Link>
              );
            })}
          </div>

          {/* Recent Nodes */}
          {!collapsed && (
            <div className="px-4 pb-4 animate-fadeIn">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Recent Nodes
                </h2>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-slate-400 hover:text-white h-6 w-6 p-0"
                  data-testid="add-node-btn"
                >
                  <Plus className="h-3 w-3" />
                </Button>
              </div>
              
              <div className="space-y-1 max-h-40 overflow-y-auto">
                {(searchQuery ? filteredNodes : nodes.slice(0, 10)).map((node) => (
                  <Button
                    key={node.id}
                    variant="ghost"
                    className="w-full justify-start text-sm text-slate-400 hover:text-white hover:bg-slate-700 px-2 py-1 h-auto"
                    onClick={() => actions.setSelectedNode(node)}
                    data-testid={`node-${node.id}-btn`}
                  >
                    <div className="truncate text-left">
                      <div className="font-medium truncate">{node.title}</div>
                      <div className="text-xs text-slate-500 truncate">
                        {node.node_type}
                      </div>
                    </div>
                  </Button>
                ))}
                
                {(searchQuery ? filteredNodes : nodes).length === 0 && (
                  <div className="text-xs text-slate-500 text-center py-4">
                    {searchQuery ? 'No nodes found' : 'No nodes created yet'}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-slate-700 p-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsSettingsOpen(true)}
            className={`text-slate-400 hover:text-white ${
              collapsed ? 'w-full justify-center' : 'w-full justify-start gap-3'
            }`}
            data-testid="settings-btn"
          >
            <Settings className="h-4 w-4" />
            {!collapsed && <span>Settings</span>}
          </Button>
        </div>
      </div>
      
      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </div>
  );
}