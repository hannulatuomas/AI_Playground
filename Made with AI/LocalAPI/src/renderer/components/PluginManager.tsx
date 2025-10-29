import React, { useState, useEffect, useCallback } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Switch from '@mui/material/Switch';
import Chip from '@mui/material/Chip';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import RefreshIcon from '@mui/icons-material/Refresh';
import ExtensionIcon from '@mui/icons-material/Extension';
import DeleteIcon from '@mui/icons-material/Delete';
import ReplayIcon from '@mui/icons-material/Replay';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';

interface PluginInfo {
  id: string;
  name: string;
  version: string;
  description: string;
  author?: string;
  enabled: boolean;
  loaded: boolean;
  error?: string;
  permissions: string[];
}

const PluginManager: React.FC = React.memo(() => {
  const [plugins, setPlugins] = useState<PluginInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPlugins();
  }, []);

  const loadPlugins = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const allPlugins = await window.electronAPI.plugins.getAll();
      setPlugins(allPlugins);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load plugins');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleToggleEnabled = useCallback(async (pluginId: string, enabled: boolean) => {
    try {
      await window.electronAPI.plugins.setEnabled(pluginId, enabled);
      await loadPlugins();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle plugin');
    }
  }, [loadPlugins]);

  const handleReload = useCallback(async (pluginId: string) => {
    setLoading(true);
    try {
      await window.electronAPI.plugins.reload(pluginId);
      await loadPlugins();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reload plugin');
    } finally {
      setLoading(false);
    }
  }, [loadPlugins]);

  const handleUnload = useCallback(async (pluginId: string) => {
    setLoading(true);
    try {
      await window.electronAPI.plugins.unload(pluginId);
      await loadPlugins();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to unload plugin');
    } finally {
      setLoading(false);
    }
  }, [loadPlugins]);

  const handleOpenPluginsFolder = useCallback(async () => {
    try {
      await window.electronAPI.plugins.openPluginsFolder();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to open plugins folder');
    }
  }, []);

  const getStatusColor = (plugin: PluginInfo) => {
    if (plugin.error) return 'error';
    if (!plugin.enabled) return 'default';
    if (plugin.loaded) return 'success';
    return 'warning';
  };

  const getStatusIcon = (plugin: PluginInfo) => {
    if (plugin.error) return <ErrorIcon color="error" />;
    if (plugin.loaded && plugin.enabled) return <CheckCircleIcon color="success" />;
    return null;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ExtensionIcon />
          <Typography variant="h5">Plugin Manager</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<FolderOpenIcon />}
            onClick={handleOpenPluginsFolder}
          >
            Open Plugins Folder
          </Button>
          <IconButton onClick={loadPlugins} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {loading && plugins.length === 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {!loading && plugins.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 6 }}>
          <ExtensionIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No Plugins Installed
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Place plugin folders in the plugins directory to get started
          </Typography>
        </Box>
      )}

      {/* Plugin Cards */}
      <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))' }}>
        {plugins.map((plugin) => (
          <Card key={plugin.id} variant="outlined">
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 1 }}>
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Typography variant="h6">{plugin.name}</Typography>
                    {getStatusIcon(plugin)}
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    v{plugin.version} {plugin.author && `• ${plugin.author}`}
                  </Typography>
                </Box>
                <Switch
                  checked={plugin.enabled}
                  onChange={(e) => handleToggleEnabled(plugin.id, e.target.checked)}
                  disabled={loading}
                />
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {plugin.description}
              </Typography>

              {/* Status */}
              <Box sx={{ mb: 1 }}>
                <Chip
                  label={plugin.error ? 'Error' : plugin.loaded ? 'Loaded' : 'Not Loaded'}
                  size="small"
                  color={getStatusColor(plugin) as any}
                  sx={{ mr: 1 }}
                />
                {plugin.enabled && (
                  <Chip label="Enabled" size="small" color="primary" variant="outlined" />
                )}
              </Box>

              {/* Permissions */}
              {plugin.permissions.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Permissions:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                    {plugin.permissions.map((perm) => (
                      <Chip key={perm} label={perm} size="small" variant="outlined" />
                    ))}
                  </Box>
                </Box>
              )}

              {/* Error Message */}
              {plugin.error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {plugin.error}
                </Alert>
              )}
            </CardContent>

            <CardActions>
              <Button
                size="small"
                startIcon={<ReplayIcon />}
                onClick={() => handleReload(plugin.id)}
                disabled={loading}
              >
                Reload
              </Button>
              <Button
                size="small"
                color="error"
                startIcon={<DeleteIcon />}
                onClick={() => handleUnload(plugin.id)}
                disabled={loading}
              >
                Unload
              </Button>
            </CardActions>
          </Card>
        ))}
      </Box>
    </Box>
  );
});

PluginManager.displayName = 'PluginManager';

export default PluginManager;
