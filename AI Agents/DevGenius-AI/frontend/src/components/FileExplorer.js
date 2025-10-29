import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { FolderOpen, File, Plus, Trash2, Save, Code, FileText, X } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function FileExplorer({ projectId, onProjectChange }) {
  const [project, setProject] = useState(null);
  const [fileTree, setFileTree] = useState({});
  const [openFiles, setOpenFiles] = useState([]);
  const [activeFile, setActiveFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [showNewFileDialog, setShowNewFileDialog] = useState(false);
  const [newFileName, setNewFileName] = useState('');

  useEffect(() => {
    if (projectId) {
      loadProject();
      loadFileTree();
    }
  }, [projectId]);

  const loadProject = async () => {
    try {
      const response = await axios.get(`${API}/code-projects/${projectId}`);
      setProject(response.data);
    } catch (error) {
      console.error('Failed to load project:', error);
    }
  };

  const loadFileTree = async () => {
    try {
      const response = await axios.get(`${API}/code-projects/${projectId}/file-tree`);
      setFileTree(response.data.tree);
    } catch (error) {
      console.error('Failed to load file tree:', error);
    }
  };

  const openFile = async (filePath) => {
    try {
      const response = await axios.get(`${API}/code-projects/${projectId}/files/${filePath}`);
      
      if (!openFiles.find(f => f.path === filePath)) {
        setOpenFiles([...openFiles, { path: filePath, content: response.data.content }]);
      }
      
      setActiveFile(filePath);
      setFileContent(response.data.content);
    } catch (error) {
      toast.error('Failed to open file');
    }
  };

  const saveFile = async () => {
    if (!activeFile) return;
    
    try {
      await axios.post(`${API}/code-projects/${projectId}/files`, {
        file_path: activeFile,
        content: fileContent
      });
      
      // Update open files
      setOpenFiles(openFiles.map(f => 
        f.path === activeFile ? { ...f, content: fileContent } : f
      ));
      
      toast.success('File saved');
      if (onProjectChange) onProjectChange();
    } catch (error) {
      toast.error('Failed to save file');
    }
  };

  const createFile = async () => {
    if (!newFileName.trim()) return;
    
    try {
      await axios.post(`${API}/code-projects/${projectId}/files`, {
        file_path: newFileName,
        content: ''
      });
      
      setShowNewFileDialog(false);
      setNewFileName('');
      loadFileTree();
      openFile(newFileName);
      toast.success('File created');
      if (onProjectChange) onProjectChange();
    } catch (error) {
      toast.error('Failed to create file');
    }
  };

  const deleteFile = async (filePath) => {
    if (!confirm(`Delete ${filePath}?`)) return;
    
    try {
      await axios.delete(`${API}/code-projects/${projectId}/files/${filePath}`);
      
      // Remove from open files
      setOpenFiles(openFiles.filter(f => f.path !== filePath));
      if (activeFile === filePath) {
        setActiveFile(null);
        setFileContent('');
      }
      
      loadFileTree();
      toast.success('File deleted');
      if (onProjectChange) onProjectChange();
    } catch (error) {
      toast.error('Failed to delete file');
    }
  };

  const closeFile = (filePath) => {
    setOpenFiles(openFiles.filter(f => f.path !== filePath));
    if (activeFile === filePath) {
      const remaining = openFiles.filter(f => f.path !== filePath);
      if (remaining.length > 0) {
        const newActive = remaining[remaining.length - 1];
        setActiveFile(newActive.path);
        setFileContent(newActive.content);
      } else {
        setActiveFile(null);
        setFileContent('');
      }
    }
  };

  const renderTree = (node, path = '') => {
    return Object.entries(node).map(([name, value]) => {
      const fullPath = path ? `${path}/${name}` : name;
      
      if (value.type === 'directory') {
        return (
          <div key={fullPath} className="ml-4 my-1">
            <div className="flex items-center gap-2 text-yellow-400 hover:bg-white/5 p-1 rounded cursor-pointer">
              <FolderOpen className="w-4 h-4" />
              <span className="text-sm">{name}</span>
            </div>
            {value.children && renderTree(value.children, fullPath)}
          </div>
        );
      } else {
        return (
          <div
            key={fullPath}
            className="ml-4 my-1 flex items-center justify-between group hover:bg-white/5 p-1 rounded cursor-pointer"
            onClick={() => openFile(value.path)}
          >
            <div className="flex items-center gap-2 flex-1">
              <File className="w-4 h-4 text-slate-400" />
              <span className="text-sm text-white">{name}</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                deleteFile(value.path);
              }}
              className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300"
            >
              <Trash2 className="w-3 h-3" />
            </Button>
          </div>
        );
      }
    });
  };

  if (!projectId) {
    return (
      <div className="h-full flex items-center justify-center text-slate-400">
        <p>No project selected</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-slate-950">
      {/* File Tree Sidebar */}
      <div className="border-b border-white/10 p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-white font-semibold">{project?.name || 'Project'}</h3>
          <Dialog open={showNewFileDialog} onOpenChange={setShowNewFileDialog}>
            <DialogTrigger asChild>
              <Button size="sm" variant="ghost" className="text-white">
                <Plus className="w-4 h-4" />
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-slate-900 border-white/10">
              <DialogHeader>
                <DialogTitle className="text-white">New File</DialogTitle>
                <DialogDescription className="text-slate-300">Create a new file in the project</DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <Label className="text-white mb-2 block">File Path</Label>
                  <Input
                    value={newFileName}
                    onChange={(e) => setNewFileName(e.target.value)}
                    placeholder="src/components/Button.jsx"
                    className="bg-white/10 border-white/20 text-white"
                    onKeyPress={(e) => e.key === 'Enter' && createFile()}
                  />
                </div>
                <Button onClick={createFile} className="w-full bg-blue-500 hover:bg-blue-600">
                  Create File
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
        <ScrollArea className="h-64">
          <div className="text-white">
            {Object.keys(fileTree).length === 0 ? (
              <p className="text-slate-400 text-sm">No files yet</p>
            ) : (
              renderTree(fileTree)
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Editor Area */}
      <div className="flex-1 flex flex-col">
        {/* Tab Bar */}
        {openFiles.length > 0 && (
          <div className="flex items-center gap-1 border-b border-white/10 px-2 py-1 overflow-x-auto">
            {openFiles.map(file => (
              <div
                key={file.path}
                className={`flex items-center gap-2 px-3 py-1 rounded-t cursor-pointer ${
                  activeFile === file.path ? 'bg-slate-800' : 'bg-slate-900 hover:bg-slate-800'
                }`}
                onClick={() => {
                  setActiveFile(file.path);
                  setFileContent(file.content);
                }}
              >
                <FileText className="w-3 h-3 text-slate-400" />
                <span className="text-sm text-white">{file.path.split('/').pop()}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    closeFile(file.path);
                  }}
                  className="hover:bg-white/10 rounded p-0.5"
                >
                  <X className="w-3 h-3 text-slate-400" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Editor */}
        {activeFile ? (
          <div className="flex-1 flex flex-col">
            <div className="flex-1 p-4">
              <Textarea
                value={fileContent}
                onChange={(e) => setFileContent(e.target.value)}
                className="w-full h-full bg-slate-900 border-white/10 text-white font-mono text-sm resize-none"
                placeholder="Write your code here..."
              />
            </div>
            <div className="border-t border-white/10 p-4 flex justify-between items-center">
              <div className="text-slate-400 text-sm">{activeFile}</div>
              <Button
                onClick={saveFile}
                className="bg-blue-500 hover:bg-blue-600"
              >
                <Save className="w-4 h-4 mr-2" />
                Save File
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-400">
            <div className="text-center">
              <Code className="w-16 h-16 mx-auto mb-4 text-slate-600" />
              <p>Select a file to edit</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default FileExplorer;
