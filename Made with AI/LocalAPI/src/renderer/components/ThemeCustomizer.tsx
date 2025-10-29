/**
 * ThemeCustomizer - Custom Theme Colors
 * 
 * Features:
 * - Color picker for all theme variables
 * - Preview mode
 * - Save custom themes
 * - Export/import themes
 * - Theme presets
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  Grid,
  Paper,
  Tabs,
  Tab,
  Divider,
  Alert,
  IconButton,
} from '@mui/material';
import PaletteIcon from '@mui/icons-material/Palette';
import SaveIcon from '@mui/icons-material/Save';
import DownloadIcon from '@mui/icons-material/Download';
import UploadIcon from '@mui/icons-material/Upload';
import RefreshIcon from '@mui/icons-material/Refresh';

interface CustomTheme {
  name: string;
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
    success: string;
    error: string;
    warning: string;
    info: string;
  };
}

interface ThemeCustomizerProps {
  onThemeChange?: (theme: CustomTheme) => void;
}

const DEFAULT_LIGHT_THEME: CustomTheme = {
  name: 'Light',
  colors: {
    primary: '#2196F3',
    secondary: '#FF4081',
    background: '#FFFFFF',
    surface: '#F5F5F5',
    text: '#000000',
    textSecondary: '#666666',
    border: '#E0E0E0',
    success: '#4CAF50',
    error: '#F44336',
    warning: '#FF9800',
    info: '#2196F3',
  },
};

const DEFAULT_DARK_THEME: CustomTheme = {
  name: 'Dark',
  colors: {
    primary: '#2196F3',
    secondary: '#FF4081',
    background: '#1E1E1E',
    surface: '#252526',
    text: '#FFFFFF',
    textSecondary: '#B0B0B0',
    border: '#3E3E3E',
    success: '#4CAF50',
    error: '#F44336',
    warning: '#FF9800',
    info: '#2196F3',
  },
};

const THEME_PRESETS: CustomTheme[] = [
  DEFAULT_LIGHT_THEME,
  DEFAULT_DARK_THEME,
  {
    name: 'Ocean',
    colors: {
      primary: '#0077BE',
      secondary: '#00BFFF',
      background: '#E6F3F7',
      surface: '#FFFFFF',
      text: '#003049',
      textSecondary: '#667B88',
      border: '#B8D4E0',
      success: '#06D6A0',
      error: '#EF476F',
      warning: '#FFB703',
      info: '#0077BE',
    },
  },
  {
    name: 'Forest',
    colors: {
      primary: '#2D6A4F',
      secondary: '#95D5B2',
      background: '#F1FAEE',
      surface: '#FFFFFF',
      text: '#1B4332',
      textSecondary: '#52796F',
      border: '#D8F3DC',
      success: '#40916C',
      error: '#E63946',
      warning: '#F77F00',
      info: '#2D6A4F',
    },
  },
  {
    name: 'Sunset',
    colors: {
      primary: '#E63946',
      secondary: '#F4A261',
      background: '#FFF8F0',
      surface: '#FFFFFF',
      text: '#1D3557',
      textSecondary: '#457B9D',
      border: '#FFE5D9',
      success: '#06D6A0',
      error: '#E63946',
      warning: '#F4A261',
      info: '#457B9D',
    },
  },
];

export const ThemeCustomizer: React.FC<ThemeCustomizerProps> = ({ onThemeChange }) => {
  const [currentTheme, setCurrentTheme] = useState<CustomTheme>(DEFAULT_DARK_THEME);
  const [themeName, setThemeName] = useState('Custom Theme');
  const [activeTab, setActiveTab] = useState(0);
  const [previewMode, setPreviewMode] = useState(false);

  const handleColorChange = (colorKey: keyof CustomTheme['colors'], value: string) => {
    setCurrentTheme(prev => ({
      ...prev,
      colors: {
        ...prev.colors,
        [colorKey]: value,
      },
    }));
    setPreviewMode(true);
    applyTheme({
      ...currentTheme,
      colors: {
        ...currentTheme.colors,
        [colorKey]: value,
      },
    });
  };

  const applyTheme = (theme: CustomTheme) => {
    const root = document.documentElement;
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });
  };

  const handleSaveTheme = () => {
    const themeToSave = { ...currentTheme, name: themeName };
    try {
      const savedThemes = JSON.parse(localStorage.getItem('custom-themes') || '[]');
      savedThemes.push(themeToSave);
      localStorage.setItem('custom-themes', JSON.stringify(savedThemes));
      setPreviewMode(false);
      onThemeChange?.(themeToSave);
    } catch (error) {
      console.error('Error saving theme:', error);
    }
  };

  const handleExportTheme = () => {
    const themeData = JSON.stringify(currentTheme, null, 2);
    const blob = new Blob([themeData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${themeName.replace(/\s+/g, '-').toLowerCase()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImportTheme = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        try {
          const text = await file.text();
          const imported = JSON.parse(text);
          setCurrentTheme(imported);
          setThemeName(imported.name || 'Imported Theme');
          applyTheme(imported);
          setPreviewMode(true);
        } catch (error) {
          console.error('Error importing theme:', error);
        }
      }
    };
    input.click();
  };

  const handlePresetClick = (preset: CustomTheme) => {
    setCurrentTheme(preset);
    setThemeName(preset.name);
    applyTheme(preset);
    setPreviewMode(true);
  };

  const handleReset = () => {
    const defaultTheme = DEFAULT_DARK_THEME;
    setCurrentTheme(defaultTheme);
    setThemeName(defaultTheme.name);
    applyTheme(defaultTheme);
    setPreviewMode(false);
  };

  const ColorPicker: React.FC<{ label: string; colorKey: keyof CustomTheme['colors'] }> = ({ label, colorKey }) => (
    <Box sx={{ mb: 2 }}>
      <Typography variant="caption" color="textSecondary" gutterBottom>
        {label}
      </Typography>
      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
        <Box
          sx={{
            width: 40,
            height: 40,
            backgroundColor: currentTheme.colors[colorKey],
            border: 1,
            borderColor: 'divider',
            borderRadius: 1,
            cursor: 'pointer',
          }}
          onClick={() => {
            const input = document.createElement('input');
            input.type = 'color';
            input.value = currentTheme.colors[colorKey];
            input.onchange = (e) => handleColorChange(colorKey, (e.target as HTMLInputElement).value);
            input.click();
          }}
        />
        <TextField
          fullWidth
          size="small"
          value={currentTheme.colors[colorKey]}
          onChange={(e) => handleColorChange(colorKey, e.target.value)}
          placeholder="#000000"
        />
      </Box>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <PaletteIcon sx={{ fontSize: 32 }} />
        <Box sx={{ flex: 1 }}>
          <Typography variant="h5">Theme Customizer</Typography>
          <Typography variant="body2" color="textSecondary">
            Create your own color scheme
          </Typography>
        </Box>
      </Box>

      {previewMode && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Preview mode active. Save your theme to apply permanently.
        </Alert>
      )}

      {/* Theme Name */}
      <TextField
        fullWidth
        label="Theme Name"
        value={themeName}
        onChange={(e) => setThemeName(e.target.value)}
        sx={{ mb: 2 }}
      />

      {/* Theme Presets */}
      <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Quick Presets
        </Typography>
        <Grid container spacing={1}>
          {THEME_PRESETS.map((preset) => (
            <Grid item xs={6} sm={4} md={3} key={preset.name}>
              <Button
                fullWidth
                variant={currentTheme.name === preset.name ? 'contained' : 'outlined'}
                onClick={() => handlePresetClick(preset)}
                sx={{
                  backgroundImage: `linear-gradient(135deg, ${preset.colors.primary} 0%, ${preset.colors.secondary} 100%)`,
                  color: 'white',
                  '&:hover': {
                    opacity: 0.8,
                  },
                }}
              >
                {preset.name}
              </Button>
            </Grid>
          ))}
        </Grid>
      </Paper>

      <Divider sx={{ my: 2 }} />

      {/* Color Customization */}
      <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ mb: 2 }}>
        <Tab label="Main Colors" />
        <Tab label="Text & Borders" />
        <Tab label="Status Colors" />
      </Tabs>

      {activeTab === 0 && (
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <ColorPicker label="Primary Color" colorKey="primary" />
            <ColorPicker label="Secondary Color" colorKey="secondary" />
          </Grid>
          <Grid item xs={12} sm={6}>
            <ColorPicker label="Background" colorKey="background" />
            <ColorPicker label="Surface" colorKey="surface" />
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && (
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <ColorPicker label="Text Color" colorKey="text" />
            <ColorPicker label="Secondary Text" colorKey="textSecondary" />
          </Grid>
          <Grid item xs={12} sm={6}>
            <ColorPicker label="Border Color" colorKey="border" />
          </Grid>
        </Grid>
      )}

      {activeTab === 2 && (
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <ColorPicker label="Success" colorKey="success" />
            <ColorPicker label="Error" colorKey="error" />
          </Grid>
          <Grid item xs={12} sm={6}>
            <ColorPicker label="Warning" colorKey="warning" />
            <ColorPicker label="Info" colorKey="info" />
          </Grid>
        </Grid>
      )}

      <Divider sx={{ my: 2 }} />

      {/* Preview */}
      <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Theme Preview
        </Typography>
        <Box
          sx={{
            p: 2,
            backgroundColor: currentTheme.colors.background,
            color: currentTheme.colors.text,
            border: `1px solid ${currentTheme.colors.border}`,
            borderRadius: 1,
          }}
        >
          <Typography variant="h6" sx={{ color: currentTheme.colors.primary, mb: 1 }}>
            Primary Heading
          </Typography>
          <Typography variant="body1" sx={{ mb: 1 }}>
            This is body text in your custom theme.
          </Typography>
          <Typography variant="body2" sx={{ color: currentTheme.colors.textSecondary, mb: 2 }}>
            This is secondary text with reduced emphasis.
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button variant="contained" size="small" sx={{ bgcolor: currentTheme.colors.primary }}>
              Primary
            </Button>
            <Button variant="outlined" size="small" sx={{ borderColor: currentTheme.colors.border }}>
              Outlined
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Button startIcon={<SaveIcon />} variant="contained" onClick={handleSaveTheme}>
          Save Theme
        </Button>
        <Button startIcon={<DownloadIcon />} variant="outlined" onClick={handleExportTheme}>
          Export
        </Button>
        <Button startIcon={<UploadIcon />} variant="outlined" onClick={handleImportTheme}>
          Import
        </Button>
        <Button startIcon={<RefreshIcon />} onClick={handleReset}>
          Reset
        </Button>
      </Box>
    </Box>
  );
};
