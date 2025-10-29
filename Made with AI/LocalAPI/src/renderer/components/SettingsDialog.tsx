/**
 * SettingsDialog - Comprehensive Settings UI
 * 
 * All 15 settings categories:
 * 1. Network Settings
 * 2. Editor Settings
 * 3. Keyboard Shortcuts
 * 4. Language/Locale
 * 5. Cache Settings
 * 6. Auto-Save
 * 7. Privacy
 * 8. Plugin Management
 * 9. Backup/Restore
 * 10. Default Values
 * 11. Import/Export
 * 12. Reset to Defaults
 * 13. Accessibility (NEW)
 * 14. Themes (NEW)
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tabs,
  Tab,
  Box,
  TextField,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  Divider,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Paper,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import BackupIcon from '@mui/icons-material/Backup';
import RestoreIcon from '@mui/icons-material/Restore';
import { AccessibilityControls } from './AccessibilityControls';
import { ThemeCustomizer } from './ThemeCustomizer';
import DownloadIcon from '@mui/icons-material/Download';
import UploadIcon from '@mui/icons-material/Upload';
import RefreshIcon from '@mui/icons-material/Refresh';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface SettingsDialogProps {
  open: boolean;
  onClose: () => void;
}

export const SettingsDialog: React.FC<SettingsDialogProps> = ({ open, onClose }) => {
  const [currentTab, setCurrentTab] = useState(0);
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (open) {
      loadSettings();
    }
  }, [open]);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await window.electronAPI.settings.getAll();
      setSettings(data);
    } catch (err) {
      setError('Failed to load settings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      setError('');
      await window.electronAPI.settings.save(settings);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setError('Failed to save settings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const result = await window.electronAPI.settings.export();
      if (result.success) {
        alert(`Settings exported to: ${result.path}`);
      }
    } catch (err) {
      setError('Failed to export settings');
    }
  };

  const handleImport = async () => {
    try {
      const result = await window.electronAPI.settings.import();
      if (result.success) {
        await loadSettings();
        alert('Settings imported successfully');
      }
    } catch (err) {
      setError('Failed to import settings');
    }
  };

  const handleResetToDefaults = async () => {
    if (confirm('Are you sure you want to reset all settings to defaults? This cannot be undone.')) {
      try {
        await window.electronAPI.settings.resetToDefaults();
        await loadSettings();
        alert('Settings reset to defaults');
      } catch (err) {
        setError('Failed to reset settings');
      }
    }
  };

  const handleBackup = async () => {
    try {
      const result = await window.electronAPI.settings.createBackup();
      if (result.success) {
        alert(`Backup created: ${result.file}`);
      }
    } catch (err) {
      setError('Failed to create backup');
    }
  };

  if (!settings) {
    return null;
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Settings</DialogTitle>
      <DialogContent sx={{ height: '70vh' }}>
        {saveSuccess && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Settings saved successfully!
          </Alert>
        )}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Tabs value={currentTab} onChange={(_, v) => setCurrentTab(v)} variant="scrollable">
          <Tab label="Network" />
          <Tab label="Editor" />
          <Tab label="Shortcuts" />
          <Tab label="Language" />
          <Tab label="Cache" />
          <Tab label="Auto-Save" />
          <Tab label="Privacy" />
          <Tab label="Plugins" />
          <Tab label="Backup" />
          <Tab label="Accessibility" />
          <Tab label="Themes" />
        </Tabs>

        {/* Network Settings */}
        <TabPanel value={currentTab} index={0}>
          <Typography variant="h6" gutterBottom>
            Network Settings
          </Typography>

          <FormControlLabel
            control={
              <Switch
                checked={settings.network.proxy?.enabled || false}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    network: {
                      ...settings.network,
                      proxy: { ...settings.network.proxy, enabled: e.target.checked },
                    },
                  })
                }
              />
            }
            label="Enable Proxy"
          />

          {settings.network.proxy?.enabled && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Proxy Host"
                value={settings.network.proxy?.host || ''}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    network: {
                      ...settings.network,
                      proxy: { ...settings.network.proxy, host: e.target.value },
                    },
                  })
                }
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                type="number"
                label="Proxy Port"
                value={settings.network.proxy?.port || 8080}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    network: {
                      ...settings.network,
                      proxy: { ...settings.network.proxy, port: parseInt(e.target.value) },
                    },
                  })
                }
                sx={{ mb: 2 }}
              />
            </Box>
          )}

          <TextField
            fullWidth
            type="number"
            label="Request Timeout (ms)"
            value={settings.network.timeout}
            onChange={(e) =>
              setSettings({
                ...settings,
                network: { ...settings.network, timeout: parseInt(e.target.value) },
              })
            }
            sx={{ mt: 2, mb: 2 }}
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.network.ssl.rejectUnauthorized}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    network: {
                      ...settings.network,
                      ssl: { ...settings.network.ssl, rejectUnauthorized: e.target.checked },
                    },
                  })
                }
              />
            }
            label="Reject Unauthorized SSL Certificates"
          />

          <TextField
            fullWidth
            type="number"
            label="Max Redirects"
            value={settings.network.maxRedirects}
            onChange={(e) =>
              setSettings({
                ...settings,
                network: { ...settings.network, maxRedirects: parseInt(e.target.value) },
              })
            }
            sx={{ mt: 2 }}
          />
        </TabPanel>

        {/* Editor Settings */}
        <TabPanel value={currentTab} index={1}>
          <Typography variant="h6" gutterBottom>
            Editor Settings
          </Typography>

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Theme</InputLabel>
            <Select
              value={settings.editor.theme}
              onChange={(e) =>
                setSettings({ ...settings, editor: { ...settings.editor, theme: e.target.value } })
              }
            >
              <MenuItem value="light">Light</MenuItem>
              <MenuItem value="dark">Dark</MenuItem>
              <MenuItem value="auto">Auto</MenuItem>
            </Select>
          </FormControl>

          <TextField
            fullWidth
            type="number"
            label="Font Size"
            value={settings.editor.fontSize}
            onChange={(e) =>
              setSettings({
                ...settings,
                editor: { ...settings.editor, fontSize: parseInt(e.target.value) },
              })
            }
            sx={{ mb: 2 }}
          />

          <TextField
            fullWidth
            label="Font Family"
            value={settings.editor.fontFamily}
            onChange={(e) =>
              setSettings({ ...settings, editor: { ...settings.editor, fontFamily: e.target.value } })
            }
            sx={{ mb: 2 }}
          />

          <TextField
            fullWidth
            type="number"
            label="Tab Size"
            value={settings.editor.tabSize}
            onChange={(e) =>
              setSettings({
                ...settings,
                editor: { ...settings.editor, tabSize: parseInt(e.target.value) },
              })
            }
            sx={{ mb: 2 }}
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.editor.insertSpaces}
                onChange={(e) =>
                  setSettings({ ...settings, editor: { ...settings.editor, insertSpaces: e.target.checked } })
                }
              />
            }
            label="Insert Spaces (instead of tabs)"
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.editor.lineNumbers}
                onChange={(e) =>
                  setSettings({ ...settings, editor: { ...settings.editor, lineNumbers: e.target.checked } })
                }
              />
            }
            label="Show Line Numbers"
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.editor.minimap}
                onChange={(e) =>
                  setSettings({ ...settings, editor: { ...settings.editor, minimap: e.target.checked } })
                }
              />
            }
            label="Show Minimap"
          />
        </TabPanel>

        {/* Keyboard Shortcuts */}
        <TabPanel value={currentTab} index={2}>
          <Typography variant="h6" gutterBottom>
            Keyboard Shortcuts
          </Typography>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Customize keyboard shortcuts for common actions
          </Typography>

          <List>
            {settings.shortcuts.slice(0, 10).map((shortcut: any, index: number) => (
              <ListItem key={index}>
                <ListItemText
                  primary={shortcut.action.replace(/-/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                  secondary={`${shortcut.ctrl ? 'Ctrl+' : ''}${shortcut.shift ? 'Shift+' : ''}${shortcut.alt ? 'Alt+' : ''}${shortcut.key}`}
                />
              </ListItem>
            ))}
          </List>
          <Typography variant="caption" color="textSecondary">
            Showing 10 of {settings.shortcuts.length} shortcuts. Full customization coming soon.
          </Typography>
        </TabPanel>

        {/* Language Settings */}
        <TabPanel value={currentTab} index={3}>
          <Typography variant="h6" gutterBottom>
            Language & Locale
          </Typography>

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Locale</InputLabel>
            <Select
              value={settings.language.locale}
              onChange={(e) =>
                setSettings({ ...settings, language: { ...settings.language, locale: e.target.value } })
              }
            >
              <MenuItem value="en-US">English (US)</MenuItem>
              <MenuItem value="en-GB">English (UK)</MenuItem>
              <MenuItem value="fi-FI">Finnish</MenuItem>
              <MenuItem value="de-DE">German</MenuItem>
              <MenuItem value="fr-FR">French</MenuItem>
              <MenuItem value="es-ES">Spanish</MenuItem>
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Date Format"
            value={settings.language.dateFormat}
            onChange={(e) =>
              setSettings({ ...settings, language: { ...settings.language, dateFormat: e.target.value } })
            }
            helperText="e.g., YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY"
            sx={{ mb: 2 }}
          />

          <TextField
            fullWidth
            label="Time Format"
            value={settings.language.timeFormat}
            onChange={(e) =>
              setSettings({ ...settings, language: { ...settings.language, timeFormat: e.target.value } })
            }
            helperText="e.g., HH:mm:ss, hh:mm:ss A"
            sx={{ mb: 2 }}
          />
        </TabPanel>

        {/* Cache Settings */}
        <TabPanel value={currentTab} index={4}>
          <Typography variant="h6" gutterBottom>
            Cache Settings
          </Typography>

          <FormControlLabel
            control={
              <Switch
                checked={settings.cache.enabled}
                onChange={(e) =>
                  setSettings({ ...settings, cache: { ...settings.cache, enabled: e.target.checked } })
                }
              />
            }
            label="Enable Cache"
          />

          <TextField
            fullWidth
            type="number"
            label="Max Cache Size (bytes)"
            value={settings.cache.maxSize}
            onChange={(e) =>
              setSettings({
                ...settings,
                cache: { ...settings.cache, maxSize: parseInt(e.target.value) },
              })
            }
            helperText={`Current: ${(settings.cache.maxSize / 1024 / 1024).toFixed(2)} MB`}
            sx={{ mt: 2, mb: 2 }}
          />

          <TextField
            fullWidth
            type="number"
            label="Cache TTL (ms)"
            value={settings.cache.ttl}
            onChange={(e) =>
              setSettings({
                ...settings,
                cache: { ...settings.cache, ttl: parseInt(e.target.value) },
              })
            }
            helperText={`Current: ${(settings.cache.ttl / 1000 / 60).toFixed(0)} minutes`}
            sx={{ mb: 2 }}
          />

          <TextField
            fullWidth
            label="Cache Location"
            value={settings.cache.location}
            disabled
            helperText="Cache is stored in the application data directory"
          />
        </TabPanel>

        {/* Auto-Save Settings */}
        <TabPanel value={currentTab} index={5}>
          <Typography variant="h6" gutterBottom>
            Auto-Save Settings
          </Typography>

          <FormControlLabel
            control={
              <Switch
                checked={settings.autoSave.enabled}
                onChange={(e) =>
                  setSettings({ ...settings, autoSave: { ...settings.autoSave, enabled: e.target.checked } })
                }
              />
            }
            label="Enable Auto-Save"
          />

          <TextField
            fullWidth
            type="number"
            label="Auto-Save Interval (ms)"
            value={settings.autoSave.interval}
            onChange={(e) =>
              setSettings({
                ...settings,
                autoSave: { ...settings.autoSave, interval: parseInt(e.target.value) },
              })
            }
            helperText={`Current: ${(settings.autoSave.interval / 1000 / 60).toFixed(1)} minutes`}
            sx={{ mt: 2, mb: 2 }}
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.autoSave.saveOnFocus}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    autoSave: { ...settings.autoSave, saveOnFocus: e.target.checked },
                  })
                }
              />
            }
            label="Save on Focus Loss"
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.autoSave.saveOnWindowChange}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    autoSave: { ...settings.autoSave, saveOnWindowChange: e.target.checked },
                  })
                }
              />
            }
            label="Save on Window Change"
          />
        </TabPanel>

        {/* Privacy Settings */}
        <TabPanel value={currentTab} index={6}>
          <Typography variant="h6" gutterBottom>
            Privacy Settings
          </Typography>

          <FormControlLabel
            control={
              <Switch
                checked={settings.privacy.telemetry}
                onChange={(e) =>
                  setSettings({ ...settings, privacy: { ...settings.privacy, telemetry: e.target.checked } })
                }
              />
            }
            label="Send Telemetry Data"
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.privacy.crashReports}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    privacy: { ...settings.privacy, crashReports: e.target.checked },
                  })
                }
              />
            }
            label="Send Crash Reports"
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.privacy.analytics}
                onChange={(e) =>
                  setSettings({ ...settings, privacy: { ...settings.privacy, analytics: e.target.checked } })
                }
              />
            }
            label="Analytics"
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.privacy.shareUsageData}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    privacy: { ...settings.privacy, shareUsageData: e.target.checked },
                  })
                }
              />
            }
            label="Share Usage Data"
          />

          <Alert severity="info" sx={{ mt: 2 }}>
            Your privacy is important. All data collection is optional and can be disabled here.
          </Alert>
        </TabPanel>

        {/* Plugin Settings */}
        <TabPanel value={currentTab} index={7}>
          <Typography variant="h6" gutterBottom>
            Plugin Management
          </Typography>

          <FormControlLabel
            control={
              <Switch
                checked={settings.plugins.enabled}
                onChange={(e) =>
                  setSettings({ ...settings, plugins: { ...settings.plugins, enabled: e.target.checked } })
                }
              />
            }
            label="Enable Plugins"
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.plugins.autoUpdate}
                onChange={(e) =>
                  setSettings({ ...settings, plugins: { ...settings.plugins, autoUpdate: e.target.checked } })
                }
              />
            }
            label="Auto-Update Plugins"
          />

          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
            Trusted Plugins
          </Typography>
          {settings.plugins.trustedPlugins.length === 0 ? (
            <Typography variant="body2" color="textSecondary">
              No trusted plugins yet
            </Typography>
          ) : (
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {settings.plugins.trustedPlugins.map((plugin: string, index: number) => (
                <Chip key={index} label={plugin} onDelete={() => {}} />
              ))}
            </Box>
          )}
        </TabPanel>

        {/* Backup Settings */}
        <TabPanel value={currentTab} index={8}>
          <Typography variant="h6" gutterBottom>
            Backup & Restore
          </Typography>

          <FormControlLabel
            control={
              <Switch
                checked={settings.backup.enabled}
                onChange={(e) =>
                  setSettings({ ...settings, backup: { ...settings.backup, enabled: e.target.checked } })
                }
              />
            }
            label="Enable Automatic Backups"
          />

          <TextField
            fullWidth
            type="number"
            label="Backup Interval (hours)"
            value={settings.backup.interval / 3600000}
            onChange={(e) =>
              setSettings({
                ...settings,
                backup: { ...settings.backup, interval: parseInt(e.target.value) * 3600000 },
              })
            }
            sx={{ mt: 2, mb: 2 }}
          />

          <TextField
            fullWidth
            type="number"
            label="Max Backups to Keep"
            value={settings.backup.maxBackups}
            onChange={(e) =>
              setSettings({
                ...settings,
                backup: { ...settings.backup, maxBackups: parseInt(e.target.value) },
              })
            }
            sx={{ mb: 2 }}
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.backup.includeData}
                onChange={(e) =>
                  setSettings({ ...settings, backup: { ...settings.backup, includeData: e.target.checked } })
                }
              />
            }
            label="Include Application Data"
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.backup.includeSettings}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    backup: { ...settings.backup, includeSettings: e.target.checked },
                  })
                }
              />
            }
            label="Include Settings"
          />

          <Divider sx={{ my: 3 }} />

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button variant="contained" startIcon={<BackupIcon />} onClick={handleBackup}>
              Create Backup Now
            </Button>
          </Box>
        </TabPanel>

        {/* Accessibility Settings */}
        <TabPanel value={currentTab} index={9}>
          <AccessibilityControls 
            onSettingsChange={(accessibilitySettings) => {
              console.log('Accessibility settings changed:', accessibilitySettings);
            }}
          />
        </TabPanel>

        {/* Theme Settings */}
        <TabPanel value={currentTab} index={10}>
          <ThemeCustomizer 
            onThemeChange={(theme) => {
              console.log('Theme changed:', theme);
            }}
          />
        </TabPanel>
      </DialogContent>

      <DialogActions sx={{ justifyContent: 'space-between', px: 3, pb: 2 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button startIcon={<DownloadIcon />} onClick={handleExport}>
            Export
          </Button>
          <Button startIcon={<UploadIcon />} onClick={handleImport}>
            Import
          </Button>
          <Button startIcon={<RefreshIcon />} onClick={handleResetToDefaults} color="warning">
            Reset
          </Button>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button onClick={onClose}>Cancel</Button>
          <Button variant="contained" onClick={handleSave} disabled={loading}>
            Save
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
};
