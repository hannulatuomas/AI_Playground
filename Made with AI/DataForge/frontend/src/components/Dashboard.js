import { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import { Database, BookOpen, Plus, Settings as SettingsIcon } from 'lucide-react';
import ConnectionManager from './ConnectionManager';
import QueryEditor from './QueryEditor';
import NotebookManager from './NotebookManager';
import Settings from './Settings';
import { toast } from 'sonner';
import { useTheme } from '../contexts/ThemeContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Dashboard({ user, onLogout }) {
  const [connections, setConnections] = useState([]);
  const [notebooks, setNotebooks] = useState([]);
  const [activeView, setActiveView] = useState('query');
  const [selectedConnection, setSelectedConnection] = useState(null);
  const { theme } = useTheme();

  useEffect(() => {
    loadConnections();
    loadNotebooks();
  }, []);

  const loadConnections = async () => {
    try {
      const response = await axios.get(`${API}/connections`);
      setConnections(response.data);
      if (response.data.length > 0 && !selectedConnection) {
        setSelectedConnection(response.data[0]);
      }
    } catch (error) {
      console.error('Failed to load connections:', error);
    }
  };

  const loadNotebooks = async () => {
    try {
      const response = await axios.get(`${API}/notebooks`);
      setNotebooks(response.data);
    } catch (error) {
      console.error('Failed to load notebooks:', error);
    }
  };

  const handleConnectionCreated = (connection) => {
    loadConnections();
    toast.success('Connection created successfully!');
  };

  const handleConnectionDeleted = () => {
    loadConnections();
    setSelectedConnection(null);
    toast.success('Connection deleted');
  };

  const handleNotebookCreated = () => {
    loadNotebooks();
    toast.success('Notebook created!');
  };

  return (
    <div className="min-h-screen flex bg-white dark:bg-gradient-to-br dark:from-slate-900 dark:via-slate-800 dark:to-slate-900" data-testid="dashboard">
      {/* Activity Bar - Azure Data Studio style */}
      <div className="w-16 bg-slate-100 dark:bg-slate-900/80 border-r border-slate-200 dark:border-slate-800 flex flex-col items-center py-4 space-y-2">
        <div className="mb-4">
          <Database className="w-6 h-6 text-cyan-500" />
        </div>
        
        <button
          onClick={() => setActiveView('query')}
          className={`w-12 h-12 rounded-lg flex items-center justify-center transition ${
            activeView === 'query'
              ? 'bg-cyan-500/20 text-cyan-500 border border-cyan-500/30'
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800'
          }`}
          data-testid="query-tab"
          title="Query Editor"
        >
          <Database className="w-5 h-5" />
        </button>

        <button
          onClick={() => setActiveView('notebooks')}
          className={`w-12 h-12 rounded-lg flex items-center justify-center transition ${
            activeView === 'notebooks'
              ? 'bg-cyan-500/20 text-cyan-500 border border-cyan-500/30'
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800'
          }`}
          data-testid="notebooks-tab"
          title="Notebooks"
        >
          <BookOpen className="w-5 h-5" />
        </button>

        <button
          onClick={() => setActiveView('connections')}
          className={`w-12 h-12 rounded-lg flex items-center justify-center transition ${
            activeView === 'connections'
              ? 'bg-cyan-500/20 text-cyan-500 border border-cyan-500/30'
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800'
          }`}
          data-testid="connections-tab"
          title="Connections"
        >
          <Plus className="w-5 h-5" />
        </button>

        <div className="flex-1"></div>

        <button
          onClick={() => setActiveView('settings')}
          className={`w-12 h-12 rounded-lg flex items-center justify-center transition ${
            activeView === 'settings'
              ? 'bg-cyan-500/20 text-cyan-500 border border-cyan-500/30'
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800'
          }`}
          data-testid="settings-tab"
          title="Settings"
        >
          <SettingsIcon className="w-5 h-5" />
        </button>

        <button
          onClick={onLogout}
          className="w-12 h-12 rounded-lg flex items-center justify-center text-slate-600 dark:text-slate-400 hover:bg-red-500/10 hover:text-red-500 transition"
          data-testid="logout-button"
          title="Logout"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Title Bar */}
        <div className="h-14 bg-slate-50 dark:bg-slate-800/80 backdrop-blur-sm border-b border-slate-200 dark:border-slate-700 flex items-center justify-between px-6">
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-semibold text-slate-900 dark:text-white">DataForge</h1>
            <span className="text-xs text-slate-500 dark:text-slate-400 bg-slate-200 dark:bg-slate-700 px-2 py-1 rounded">
              {activeView === 'query' ? 'Query Editor' : 
               activeView === 'notebooks' ? 'Notebooks' : 
               activeView === 'connections' ? 'Connections' : 
               activeView === 'settings' ? 'Settings' : ''}
            </span>
          </div>
          <div className="text-sm text-slate-600 dark:text-slate-400">
            <span className="font-medium text-slate-900 dark:text-white">{user.name}</span>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto bg-white dark:bg-slate-900/50 p-6">
          {activeView === 'query' && (
            <QueryEditor
              connections={connections}
              selectedConnection={selectedConnection}
              onConnectionChange={setSelectedConnection}
            />
          )}

          {activeView === 'notebooks' && (
            <NotebookManager
              notebooks={notebooks}
              connections={connections}
              onNotebookCreated={handleNotebookCreated}
              onNotebooksChange={loadNotebooks}
            />
          )}

          {activeView === 'connections' && (
            <ConnectionManager
              connections={connections}
              onConnectionCreated={handleConnectionCreated}
              onConnectionDeleted={handleConnectionDeleted}
            />
          )}

          {activeView === 'settings' && (
            <Settings />
          )}
        </div>

        {/* Status Bar */}
        <div className="h-8 bg-cyan-600 dark:bg-cyan-700 flex items-center px-4 text-xs text-white">
          <div className="flex items-center space-x-4">
            <span className="font-medium">
              {connections.length} {connections.length === 1 ? 'Connection' : 'Connections'}
            </span>
            {selectedConnection && (
              <>
                <span className="text-cyan-200">|</span>
                <span>Connected to: {selectedConnection.name}</span>
              </>
            )}
          </div>
          <div className="flex-1"></div>
          <span className="capitalize">{theme} Mode</span>
        </div>
      </div>
    </div>
  );
}
