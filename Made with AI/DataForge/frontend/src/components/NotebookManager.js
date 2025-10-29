import { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Plus, BookOpen, Trash2 } from 'lucide-react';
import NotebookEditor from './NotebookEditor';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function NotebookManager({ notebooks, connections, onNotebookCreated, onNotebooksChange }) {
  const [showDialog, setShowDialog] = useState(false);
  const [notebookName, setNotebookName] = useState('');
  const [selectedNotebook, setSelectedNotebook] = useState(null);
  const [notebookData, setNotebookData] = useState(null);

  const handleCreateNotebook = async () => {
    if (!notebookName.trim()) {
      toast.error('Please enter a notebook name');
      return;
    }

    try {
      await axios.post(`${API}/notebooks`, { name: notebookName });
      onNotebookCreated();
      setShowDialog(false);
      setNotebookName('');
    } catch (error) {
      toast.error('Failed to create notebook');
    }
  };

  const handleDeleteNotebook = async (notebookId) => {
    if (!window.confirm('Are you sure you want to delete this notebook?')) return;

    try {
      await axios.delete(`${API}/notebooks/${notebookId}`);
      onNotebooksChange();
      if (selectedNotebook === notebookId) {
        setSelectedNotebook(null);
        setNotebookData(null);
      }
      toast.success('Notebook deleted');
    } catch (error) {
      toast.error('Failed to delete notebook');
    }
  };

  const handleOpenNotebook = async (notebookId) => {
    try {
      const response = await axios.get(`${API}/notebooks/${notebookId}`);
      setNotebookData(response.data);
      setSelectedNotebook(notebookId);
    } catch (error) {
      toast.error('Failed to load notebook');
    }
  };

  const handleCloseNotebook = () => {
    setSelectedNotebook(null);
    setNotebookData(null);
  };

  if (selectedNotebook && notebookData) {
    return (
      <NotebookEditor
        notebook={notebookData}
        connections={connections}
        onClose={handleCloseNotebook}
        onUpdate={onNotebooksChange}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Notebooks</h2>
          <p className="text-slate-600 dark:text-slate-400 mt-2">Create interactive notebooks with SQL, Markdown, and Python</p>
        </div>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button className="bg-cyan-600 hover:bg-cyan-700" data-testid="create-notebook-button">
              <Plus className="w-4 h-4 mr-2" />
              New Notebook
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-slate-800 border-slate-700 text-white">
            <DialogHeader>
              <DialogTitle className="text-2xl">Create New Notebook</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <Label className="text-slate-300">Notebook Name</Label>
                <Input
                  placeholder="My Notebook"
                  value={notebookName}
                  onChange={(e) => setNotebookName(e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="notebook-name-input"
                  onKeyPress={(e) => e.key === 'Enter' && handleCreateNotebook()}
                />
              </div>
              <Button
                onClick={handleCreateNotebook}
                className="w-full bg-cyan-600 hover:bg-cyan-700"
                data-testid="save-notebook-button"
              >
                Create Notebook
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Notebooks List */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {notebooks.length === 0 ? (
          <Card className="col-span-full bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700">
            <CardContent className="py-12 text-center">
              <BookOpen className="w-16 h-16 text-slate-400 dark:text-slate-600 mx-auto mb-4" />
              <p className="text-slate-600 dark:text-slate-400 text-lg">No notebooks yet. Create your first notebook!</p>
            </CardContent>
          </Card>
        ) : (
          notebooks.map((notebook) => (
            <Card 
              key={notebook.id} 
              className="bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 hover:border-cyan-500 transition-all cursor-pointer"
              onClick={() => handleOpenNotebook(notebook.id)}
              data-testid="notebook-card"
            >
              <CardHeader>
                <CardTitle className="text-slate-900 dark:text-white flex items-center justify-between">
                  <div className="flex items-center">
                    <BookOpen className="w-5 h-5 mr-2 text-cyan-400" />
                    <span>{notebook.name}</span>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteNotebook(notebook.id);
                    }}
                    className="text-red-400 hover:text-red-300 hover:bg-red-400/10"
                    data-testid="delete-notebook-button"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm text-slate-700 dark:text-slate-300">
                  <p><span className="text-slate-500 dark:text-slate-500">Cells:</span> {notebook.cells?.length || 0}</p>
                  <p className="text-slate-500 dark:text-slate-500 text-xs">
                    Updated: {new Date(notebook.updated_at).toLocaleDateString()}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
