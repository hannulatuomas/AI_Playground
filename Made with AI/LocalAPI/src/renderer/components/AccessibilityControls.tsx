/**
 * AccessibilityControls - Font Size & High Contrast Mode
 * 
 * Features:
 * - Font size slider (Small, Medium, Large, X-Large)
 * - High contrast mode toggle
 * - Preview changes in real-time
 * - Persist user preferences
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Slider,
  Switch,
  FormControlLabel,
  Button,
  Paper,
  Divider,
  Alert,
} from '@mui/material';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import ContrastIcon from '@mui/icons-material/Contrast';
import RestartAltIcon from '@mui/icons-material/RestartAlt';

interface AccessibilityControlsProps {
  onSettingsChange?: (settings: AccessibilitySettings) => void;
}

export interface AccessibilitySettings {
  fontSize: number; // 12-24px
  highContrast: boolean;
  reducedMotion: boolean;
}

const FONT_SIZE_PRESETS = {
  small: 12,
  medium: 14,
  large: 16,
  xlarge: 20,
};

const DEFAULT_SETTINGS: AccessibilitySettings = {
  fontSize: 14,
  highContrast: false,
  reducedMotion: false,
};

export const AccessibilityControls: React.FC<AccessibilityControlsProps> = ({ onSettingsChange }) => {
  const [settings, setSettings] = useState<AccessibilitySettings>(DEFAULT_SETTINGS);
  const [previewMode, setPreviewMode] = useState(false);

  // Load saved settings
  useEffect(() => {
    loadSettings();
  }, []);

  // Apply settings when changed
  useEffect(() => {
    if (previewMode) {
      applySettings(settings);
    }
  }, [settings, previewMode]);

  const loadSettings = () => {
    try {
      const saved = localStorage.getItem('accessibility-settings');
      if (saved) {
        const parsed = JSON.parse(saved);
        setSettings(parsed);
        applySettings(parsed);
      }
    } catch (error) {
      console.error('Error loading accessibility settings:', error);
    }
  };

  const applySettings = (newSettings: AccessibilitySettings) => {
    const root = document.documentElement;

    // Apply font size
    root.style.setProperty('--font-size-base', `${newSettings.fontSize}px`);
    document.body.style.fontSize = `${newSettings.fontSize}px`;

    // Apply high contrast
    if (newSettings.highContrast) {
      root.classList.add('high-contrast');
      root.style.setProperty('--color-background', '#000000');
      root.style.setProperty('--color-text', '#FFFFFF');
      root.style.setProperty('--color-border', '#FFFFFF');
      root.style.setProperty('--color-primary', '#00FF00');
    } else {
      root.classList.remove('high-contrast');
      // Reset to theme defaults (would be better to restore theme values)
      root.style.removeProperty('--color-background');
      root.style.removeProperty('--color-text');
      root.style.removeProperty('--color-border');
      root.style.removeProperty('--color-primary');
    }

    // Apply reduced motion
    if (newSettings.reducedMotion) {
      root.style.setProperty('--animation-duration', '0ms');
      root.style.setProperty('--transition-duration', '0ms');
    } else {
      root.style.removeProperty('--animation-duration');
      root.style.removeProperty('--transition-duration');
    }
  };

  const handleSave = () => {
    try {
      localStorage.setItem('accessibility-settings', JSON.stringify(settings));
      applySettings(settings);
      setPreviewMode(false);
      onSettingsChange?.(settings);
      // Show success message or close dialog
    } catch (error) {
      console.error('Error saving accessibility settings:', error);
    }
  };

  const handleReset = () => {
    setSettings(DEFAULT_SETTINGS);
    applySettings(DEFAULT_SETTINGS);
    localStorage.removeItem('accessibility-settings');
    setPreviewMode(false);
  };

  const handleFontSizeChange = (_event: Event, value: number | number[]) => {
    const newFontSize = Array.isArray(value) ? value[0] : value;
    setSettings(prev => ({ ...prev, fontSize: newFontSize }));
    setPreviewMode(true);
  };

  const handlePresetClick = (preset: keyof typeof FONT_SIZE_PRESETS) => {
    setSettings(prev => ({ ...prev, fontSize: FONT_SIZE_PRESETS[preset] }));
    setPreviewMode(true);
  };

  const handleHighContrastToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSettings(prev => ({ ...prev, highContrast: event.target.checked }));
    setPreviewMode(true);
  };

  const handleReducedMotionToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSettings(prev => ({ ...prev, reducedMotion: event.target.checked }));
    setPreviewMode(true);
  };

  const getFontSizeLabel = (value: number): string => {
    if (value <= 12) return 'Small';
    if (value <= 14) return 'Medium';
    if (value <= 16) return 'Large';
    return 'X-Large';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Accessibility Settings
      </Typography>
      <Typography variant="body2" color="textSecondary" paragraph>
        Customize the interface to improve readability and reduce visual strain
      </Typography>

      {previewMode && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Preview mode active. Click "Save Changes" to apply permanently.
        </Alert>
      )}

      {/* Font Size Control */}
      <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <ZoomOutIcon />
          <Typography variant="subtitle1" sx={{ flex: 1 }}>
            Font Size
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {settings.fontSize}px ({getFontSizeLabel(settings.fontSize)})
          </Typography>
          <ZoomInIcon />
        </Box>

        <Slider
          value={settings.fontSize}
          onChange={handleFontSizeChange}
          min={12}
          max={24}
          step={1}
          marks={[
            { value: 12, label: 'S' },
            { value: 14, label: 'M' },
            { value: 16, label: 'L' },
            { value: 20, label: 'XL' },
          ]}
          valueLabelDisplay="auto"
        />

        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
          {Object.entries(FONT_SIZE_PRESETS).map(([key, value]) => (
            <Button
              key={key}
              size="small"
              variant={settings.fontSize === value ? 'contained' : 'outlined'}
              onClick={() => handlePresetClick(key as keyof typeof FONT_SIZE_PRESETS)}
            >
              {key.charAt(0).toUpperCase() + key.slice(1)}
            </Button>
          ))}
        </Box>

        {/* Preview Text */}
        <Box
          sx={{
            mt: 2,
            p: 2,
            backgroundColor: 'action.hover',
            borderRadius: 1,
            fontSize: `${settings.fontSize}px`,
          }}
        >
          <Typography variant="body1" paragraph sx={{ fontSize: 'inherit' }}>
            Preview: The quick brown fox jumps over the lazy dog.
          </Typography>
          <Typography variant="caption" sx={{ fontSize: 'inherit' }}>
            This is how your interface text will look with the selected font size.
          </Typography>
        </Box>
      </Paper>

      <Divider sx={{ my: 2 }} />

      {/* High Contrast Mode */}
      <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ContrastIcon />
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle1">High Contrast Mode</Typography>
            <Typography variant="body2" color="textSecondary">
              Increase contrast between text and background for better readability
            </Typography>
          </Box>
          <Switch
            checked={settings.highContrast}
            onChange={handleHighContrastToggle}
            color="primary"
          />
        </Box>

        {settings.highContrast && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            High contrast mode uses strong colors that may override your theme. Some visual elements may look different.
          </Alert>
        )}
      </Paper>

      {/* Reduced Motion */}
      <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
        <FormControlLabel
          control={
            <Switch
              checked={settings.reducedMotion}
              onChange={handleReducedMotionToggle}
              color="primary"
            />
          }
          label={
            <Box>
              <Typography variant="subtitle1">Reduce Motion</Typography>
              <Typography variant="body2" color="textSecondary">
                Minimize animations and transitions (helpful for motion sensitivity)
              </Typography>
            </Box>
          }
        />
      </Paper>

      <Divider sx={{ my: 2 }} />

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button
          startIcon={<RestartAltIcon />}
          onClick={handleReset}
          disabled={!previewMode}
        >
          Reset to Defaults
        </Button>
        <Button
          variant="contained"
          onClick={handleSave}
          disabled={!previewMode}
        >
          Save Changes
        </Button>
      </Box>

      {/* Keyboard Shortcuts Reference */}
      <Paper variant="outlined" sx={{ p: 2, mt: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          Keyboard Shortcuts for Accessibility
        </Typography>
        <Typography variant="caption" component="div" color="textSecondary">
          • Ctrl + Plus (+) : Increase font size
          <br />
          • Ctrl + Minus (-) : Decrease font size
          <br />
          • Ctrl + 0 : Reset to default font size
          <br />• Alt + Shift + C : Toggle high contrast mode
        </Typography>
      </Paper>
    </Box>
  );
};
