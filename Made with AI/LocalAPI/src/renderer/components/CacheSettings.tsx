import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Slider from '@mui/material/Slider';
import Chip from '@mui/material/Chip';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';

interface CacheStats {
  hits: number;
  misses: number;
  size: number;
  entries: number;
  hitRate: number;
}

interface CacheSettingsProps {
  onSettingsChange?: (settings: CacheConfig) => void;
}

interface CacheConfig {
  enabled: boolean;
  defaultTTL: number;
  maxSize: number;
}

const CacheSettings: React.FC<CacheSettingsProps> = React.memo(({ onSettingsChange }) => {
  const [enabled, setEnabled] = useState(true);
  const [defaultTTL, setDefaultTTL] = useState(5); // minutes
  const [maxSize, setMaxSize] = useState(50); // MB
  const [stats, setStats] = useState<CacheStats>({
    hits: 0,
    misses: 0,
    size: 0,
    entries: 0,
    hitRate: 0,
  });
  const [invalidatePattern, setInvalidatePattern] = useState('');

  // Load initial settings
  useEffect(() => {
    loadSettings();
    loadStats();
  }, []);

  const loadSettings = async () => {
    try {
      // Load from electron store or use defaults
      const settings = await window.electronAPI.settings?.get('cache');
      if (settings) {
        setEnabled(settings.enabled ?? true);
        setDefaultTTL(settings.defaultTTL ?? 5);
        setMaxSize(settings.maxSize ?? 50);
      }
    } catch (error) {
      console.error('Failed to load cache settings:', error);
    }
  };

  const loadStats = useCallback(async () => {
    try {
      const cacheStats = await window.electronAPI.cache?.getStats();
      if (cacheStats) {
        setStats(cacheStats);
      }
    } catch (error) {
      console.error('Failed to load cache stats:', error);
    }
  }, []);

  const handleEnabledChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newEnabled = event.target.checked;
    setEnabled(newEnabled);
    saveSettings({ enabled: newEnabled, defaultTTL, maxSize });
  }, [defaultTTL, maxSize]);

  const handleTTLChange = useCallback((_: Event, value: number | number[]) => {
    const newTTL = value as number;
    setDefaultTTL(newTTL);
    saveSettings({ enabled, defaultTTL: newTTL, maxSize });
  }, [enabled, maxSize]);

  const handleMaxSizeChange = useCallback((_: Event, value: number | number[]) => {
    const newMaxSize = value as number;
    setMaxSize(newMaxSize);
    saveSettings({ enabled, defaultTTL, maxSize: newMaxSize });
  }, [enabled, defaultTTL]);

  const saveSettings = useCallback(async (settings: CacheConfig) => {
    try {
      await window.electronAPI.settings?.set('cache', settings);
      await window.electronAPI.cache?.configure(settings);
      if (onSettingsChange) {
        onSettingsChange(settings);
      }
    } catch (error) {
      console.error('Failed to save cache settings:', error);
    }
  }, [onSettingsChange]);

  const handleClearCache = useCallback(async () => {
    try {
      await window.electronAPI.cache?.clear();
      loadStats();
    } catch (error) {
      console.error('Failed to clear cache:', error);
    }
  }, [loadStats]);

  const handleCleanExpired = useCallback(async () => {
    try {
      const count = await window.electronAPI.cache?.cleanExpired();
      console.log(`Cleaned ${count} expired entries`);
      loadStats();
    } catch (error) {
      console.error('Failed to clean expired cache:', error);
    }
  }, [loadStats]);

  const handleInvalidatePattern = useCallback(async () => {
    if (!invalidatePattern.trim()) return;
    
    try {
      // Validate regex pattern
      new RegExp(invalidatePattern); // Test if valid regex
      const count = await window.electronAPI.cache?.invalidateByPattern(invalidatePattern);
      console.log(`Invalidated ${count} entries`);
      setInvalidatePattern('');
      loadStats();
    } catch (error) {
      console.error('Failed to invalidate cache:', error);
    }
  }, [invalidatePattern, loadStats]);

  // Format size
  const formatSize = useCallback((bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  }, []);

  // Memoize formatted stats
  const formattedSize = useMemo(() => formatSize(stats.size), [stats.size, formatSize]);
  const hitRateColor = useMemo(() => {
    if (stats.hitRate >= 70) return 'success';
    if (stats.hitRate >= 40) return 'warning';
    return 'error';
  }, [stats.hitRate]);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Cache Settings
      </Typography>

      {/* Enable/Disable Cache */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <FormControlLabel
          control={<Switch checked={enabled} onChange={handleEnabledChange} />}
          label="Enable Request Caching"
        />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Cache GET requests to improve performance and reduce network usage
        </Typography>
      </Paper>

      {/* TTL Settings */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Default Cache TTL (Time To Live)
        </Typography>
        <Box sx={{ px: 2 }}>
          <Slider
            value={defaultTTL}
            onChange={handleTTLChange}
            min={1}
            max={60}
            step={1}
            marks={[
              { value: 1, label: '1m' },
              { value: 15, label: '15m' },
              { value: 30, label: '30m' },
              { value: 60, label: '60m' },
            ]}
            valueLabelDisplay="on"
            valueLabelFormat={(value) => `${value} min`}
            disabled={!enabled}
          />
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Cached responses will expire after {defaultTTL} minute{defaultTTL !== 1 ? 's' : ''}
        </Typography>
      </Paper>

      {/* Max Size Settings */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Maximum Cache Size
        </Typography>
        <Box sx={{ px: 2 }}>
          <Slider
            value={maxSize}
            onChange={handleMaxSizeChange}
            min={10}
            max={500}
            step={10}
            marks={[
              { value: 10, label: '10MB' },
              { value: 100, label: '100MB' },
              { value: 250, label: '250MB' },
              { value: 500, label: '500MB' },
            ]}
            valueLabelDisplay="on"
            valueLabelFormat={(value) => `${value} MB`}
            disabled={!enabled}
          />
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Cache will automatically evict old entries when size exceeds {maxSize} MB
        </Typography>
      </Paper>

      {/* Cache Statistics */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="subtitle1">Cache Statistics</Typography>
          <Button
            size="small"
            startIcon={<RefreshIcon />}
            onClick={loadStats}
          >
            Refresh
          </Button>
        </Box>

        <TableContainer>
          <Table size="small">
            <TableBody>
              <TableRow>
                <TableCell>Hit Rate</TableCell>
                <TableCell>
                  <Chip
                    label={`${stats.hitRate.toFixed(2)}%`}
                    color={hitRateColor}
                    size="small"
                  />
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Cache Hits</TableCell>
                <TableCell>{stats.hits}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Cache Misses</TableCell>
                <TableCell>{stats.misses}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Total Entries</TableCell>
                <TableCell>{stats.entries}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Cache Size</TableCell>
                <TableCell>{formattedSize}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Cache Management */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Cache Management
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
          <Button
            variant="outlined"
            color="warning"
            startIcon={<DeleteIcon />}
            onClick={handleCleanExpired}
          >
            Clean Expired
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleClearCache}
          >
            Clear All Cache
          </Button>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
          <TextField
            size="small"
            fullWidth
            label="Invalidate by URL Pattern (regex)"
            placeholder="e.g., /api/users/.*"
            value={invalidatePattern}
            onChange={(e) => setInvalidatePattern(e.target.value)}
          />
          <Button
            variant="contained"
            onClick={handleInvalidatePattern}
            disabled={!invalidatePattern.trim()}
          >
            Invalidate
          </Button>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Use regular expressions to invalidate cache entries matching a URL pattern
        </Typography>
      </Paper>
    </Box>
  );
});

CacheSettings.displayName = 'CacheSettings';

export default CacheSettings;
