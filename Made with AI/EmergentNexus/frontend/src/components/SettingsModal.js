import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Settings, 
  Download, 
  Upload, 
  Trash,
  Moon,
  Sun,
  Database,
  Palette
} from 'lucide-react';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { useTheme } from '../contexts/ThemeContext';

export default function SettingsModal({ isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('general');
  const { nodes, api } = useWorkspace();
  const { theme, setTheme, isDark } = useTheme();

  const exportData = () => {
    const exportData = {
      nodes,
      exportDate: new Date().toISOString(),
      version: '1.0'
    };
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `nexus-export-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const clearAllData = async () => {
    if (window.confirm('Are you sure you want to delete ALL data? This cannot be undone.')) {
      try {
        for (const node of nodes) {
          await api.deleteNode(node.id);
        }
        alert('All data has been cleared.');
      } catch (error) {
        alert('Error clearing data: ' + error.message);
      }
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl mx-4 bg-slate-800 border-slate-700" data-testid="settings-modal">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Settings className="h-5 w-5 text-slate-400" />
            Settings
          </DialogTitle>
        </DialogHeader>

        <div className="flex gap-6">
          {/* Settings Tabs */}
          <div className="w-48 space-y-2">
            {[
              { id: 'general', label: 'General', icon: Settings },
              { id: 'appearance', label: 'Appearance', icon: Palette },
              { id: 'data', label: 'Data Management', icon: Database }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <Button
                  key={tab.id}
                  variant={activeTab === tab.id ? "secondary" : "ghost"}
                  className={`w-full justify-start gap-2 ${
                    activeTab === tab.id 
                      ? 'bg-slate-700 text-white' 
                      : 'text-slate-400 hover:text-white hover:bg-slate-700'
                  }`}
                  onClick={() => setActiveTab(tab.id)}
                  data-testid={`settings-tab-${tab.id}`}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </Button>
              );
            })}
          </div>

          {/* Settings Content */}
          <div className="flex-1 space-y-4">
            {activeTab === 'general' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">General Settings</h3>
                
                <div>
                  <label className="text-sm font-medium text-slate-300 mb-2 block">
                    Application Name
                  </label>
                  <Input
                    value="Emergent Nexus"
                    disabled
                    className="bg-slate-700 border-slate-600 text-slate-400"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium text-slate-300 mb-2 block">
                    Version
                  </label>
                  <Input
                    value="1.0.0"
                    disabled
                    className="bg-slate-700 border-slate-600 text-slate-400"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium text-slate-300 mb-2 block">
                    Auto-save
                  </label>
                  <div className="flex items-center gap-2">
                    <div className="text-sm text-slate-400">
                      Changes are automatically saved
                    </div>
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'appearance' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Appearance Settings</h3>
                
                <div>
                  <label className="text-sm font-medium text-slate-300 mb-3 block">
                    Theme
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <Button
                      variant={isDark ? "default" : "outline"}
                      onClick={() => setTheme('dark')}
                      className={`flex items-center gap-3 p-4 h-auto ${
                        isDark 
                          ? 'bg-slate-700 text-white border-slate-600' 
                          : 'text-slate-400 border-slate-600 hover:text-white hover:bg-slate-700'
                      }`}
                      data-testid="dark-theme-btn"
                    >
                      <Moon className="h-5 w-5" />
                      <div className="text-left">
                        <div className="font-medium">Dark Mode</div>
                        <div className="text-xs opacity-70">Easy on the eyes</div>
                      </div>
                    </Button>
                    
                    <Button
                      variant={!isDark ? "default" : "outline"}
                      onClick={() => setTheme('light')}
                      className={`flex items-center gap-3 p-4 h-auto ${
                        !isDark 
                          ? 'bg-white text-slate-900 border-slate-300' 
                          : 'text-slate-400 border-slate-600 hover:text-white hover:bg-slate-700'
                      }`}
                      data-testid="light-theme-btn"
                    >
                      <Sun className="h-5 w-5" />
                      <div className="text-left">
                        <div className="font-medium">Light Mode</div>
                        <div className="text-xs opacity-70">Bright and clear</div>
                      </div>
                    </Button>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-slate-300 mb-2 block">
                    Current Theme
                  </label>
                  <div className="text-sm text-slate-400 bg-slate-700 px-3 py-2 rounded">
                    {isDark ? 'Dark Mode' : 'Light Mode'} is currently active
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-slate-300 mb-2 block">
                    Font Family
                  </label>
                  <div className="text-sm text-slate-400">
                    Using Inter font for optimal readability
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'data' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Data Management</h3>
                
                <div>
                  <label className="text-sm font-medium text-slate-300 mb-2 block">
                    Current Data
                  </label>
                  <div className="text-sm text-slate-400 mb-4">
                    You have {nodes.length} nodes in your workspace
                  </div>
                </div>

                <div className="space-y-3">
                  <Button
                    onClick={exportData}
                    className="w-full justify-start bg-blue-600 hover:bg-blue-700"
                    data-testid="export-data-btn"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export All Data (JSON)
                  </Button>

                  <Button
                    variant="outline"
                    className="w-full justify-start text-slate-400 border-slate-600"
                    disabled
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Import Data (Coming Soon)
                  </Button>

                  <Button
                    onClick={clearAllData}
                    variant="outline"
                    className="w-full justify-start text-red-400 border-red-600 hover:bg-red-600 hover:text-white"
                    data-testid="clear-data-btn"
                  >
                    <Trash className="h-4 w-4 mr-2" />
                    Clear All Data
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end pt-4 border-t border-slate-700">
          <Button onClick={onClose} data-testid="close-settings-btn">
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}