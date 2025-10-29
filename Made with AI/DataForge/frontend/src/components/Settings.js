import { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Settings as SettingsIcon, Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { toast } from 'sonner';

export default function Settings({ onClose }) {
  const { theme, setTheme } = useTheme();
  const [autoSave, setAutoSave] = useState(() => {
    return localStorage.getItem('dataforge-autosave') === 'true';
  });

  const handleAutoSaveChange = (checked) => {
    setAutoSave(checked);
    localStorage.setItem('dataforge-autosave', checked.toString());
    toast.success(checked ? 'Auto-save enabled' : 'Auto-save disabled');
  };

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
    toast.success(`Theme changed to ${newTheme}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold">Settings</h2>
          <p className="text-slate-400 dark:text-slate-400 mt-2">Customize your DataForge experience</p>
        </div>
      </div>

      {/* Appearance Settings */}
      <Card className="bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700">
        <CardHeader>
          <CardTitle className="text-slate-900 dark:text-white flex items-center">
            <Monitor className="w-5 h-5 mr-2" />
            Appearance
          </CardTitle>
          <CardDescription className="text-slate-600 dark:text-slate-400">
            Customize the look and feel of DataForge
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <Label className="text-slate-700 dark:text-slate-300">Theme</Label>
            <div className="grid grid-cols-3 gap-3">
              <button
                onClick={() => handleThemeChange('light')}
                className={`flex flex-col items-center justify-center p-4 rounded-lg border-2 transition ${
                  theme === 'light'
                    ? 'border-cyan-500 bg-cyan-50 dark:bg-cyan-900/20'
                    : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                }`}
                data-testid="theme-light-button"
              >
                <Sun className={`w-6 h-6 mb-2 ${theme === 'light' ? 'text-cyan-600' : 'text-slate-600 dark:text-slate-400'}`} />
                <span className={`text-sm font-medium ${theme === 'light' ? 'text-cyan-600' : 'text-slate-600 dark:text-slate-400'}`}>
                  Light
                </span>
              </button>
              
              <button
                onClick={() => handleThemeChange('dark')}
                className={`flex flex-col items-center justify-center p-4 rounded-lg border-2 transition ${
                  theme === 'dark'
                    ? 'border-cyan-500 bg-cyan-50 dark:bg-cyan-900/20'
                    : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                }`}
                data-testid="theme-dark-button"
              >
                <Moon className={`w-6 h-6 mb-2 ${theme === 'dark' ? 'text-cyan-600' : 'text-slate-600 dark:text-slate-400'}`} />
                <span className={`text-sm font-medium ${theme === 'dark' ? 'text-cyan-600' : 'text-slate-600 dark:text-slate-400'}`}>
                  Dark
                </span>
              </button>
              
              <button
                onClick={() => handleThemeChange('system')}
                className={`flex flex-col items-center justify-center p-4 rounded-lg border-2 transition ${
                  theme === 'system'
                    ? 'border-cyan-500 bg-cyan-50 dark:bg-cyan-900/20'
                    : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                }`}
                data-testid="theme-system-button"
              >
                <Monitor className={`w-6 h-6 mb-2 ${theme === 'system' ? 'text-cyan-600' : 'text-slate-600 dark:text-slate-400'}`} />
                <span className={`text-sm font-medium ${theme === 'system' ? 'text-cyan-600' : 'text-slate-600 dark:text-slate-400'}`}>
                  System
                </span>
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Editor Settings */}
      <Card className="bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700">
        <CardHeader>
          <CardTitle className="text-slate-900 dark:text-white flex items-center">
            <SettingsIcon className="w-5 h-5 mr-2" />
            Editor
          </CardTitle>
          <CardDescription className="text-slate-600 dark:text-slate-400">
            Configure query editor behavior
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-slate-700 dark:text-slate-300">Auto-save notebooks</Label>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Automatically save notebook changes every 5 minutes
              </p>
            </div>
            <Switch
              checked={autoSave}
              onCheckedChange={handleAutoSaveChange}
              data-testid="autosave-toggle"
            />
          </div>

          <div className="space-y-3">
            <Label className="text-slate-700 dark:text-slate-300">Font Size</Label>
            <Select defaultValue="14">
              <SelectTrigger className="bg-white dark:bg-slate-700 border-slate-200 dark:border-slate-600">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-white dark:bg-slate-700 border-slate-200 dark:border-slate-600">
                <SelectItem value="12">12px</SelectItem>
                <SelectItem value="13">13px</SelectItem>
                <SelectItem value="14">14px (Default)</SelectItem>
                <SelectItem value="16">16px</SelectItem>
                <SelectItem value="18">18px</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* About */}
      <Card className="bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700">
        <CardHeader>
          <CardTitle className="text-slate-900 dark:text-white">About DataForge</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
          <p><strong className="text-slate-900 dark:text-white">Version:</strong> 1.0.0</p>
          <p><strong className="text-slate-900 dark:text-white">Description:</strong> Comprehensive database management tool inspired by Azure Data Studio</p>
          <p><strong className="text-slate-900 dark:text-white">Features:</strong> Multi-database support, Query Editor with Monaco, Interactive Notebooks</p>
        </CardContent>
      </Card>
    </div>
  );
}
