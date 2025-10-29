/**
 * CollapsibleSection - Reusable Collapsible Section Component
 * 
 * Features:
 * - Expand/collapse animation
 * - State persistence
 * - Custom header
 * - Icon support
 * - Count badges
 * - Actions in header
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Collapse,
  Paper,
  Divider,
  Badge,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

interface CollapsibleSectionProps {
  title: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  persistKey?: string; // Key for localStorage persistence
  count?: number; // Show count badge
  actions?: React.ReactNode; // Action buttons in header
  elevation?: number;
  noPadding?: boolean;
}

export const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
  title,
  icon,
  children,
  defaultExpanded = true,
  persistKey,
  count,
  actions,
  elevation = 0,
  noPadding = false,
}) => {
  const [expanded, setExpanded] = useState(() => {
    // Load from localStorage if persistKey is provided
    if (persistKey) {
      const saved = localStorage.getItem(`collapsible-${persistKey}`);
      if (saved !== null) {
        return saved === 'true';
      }
    }
    return defaultExpanded;
  });

  // Save to localStorage when expanded changes
  useEffect(() => {
    if (persistKey) {
      localStorage.setItem(`collapsible-${persistKey}`, String(expanded));
    }
  }, [expanded, persistKey]);

  const handleToggle = () => {
    setExpanded(!expanded);
  };

  return (
    <Paper elevation={elevation} sx={{ overflow: 'hidden' }}>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          p: 1.5,
          cursor: 'pointer',
          backgroundColor: 'background.default',
          '&:hover': {
            backgroundColor: 'action.hover',
          },
          transition: 'background-color 0.2s',
        }}
        onClick={handleToggle}
      >
        {/* Icon */}
        {icon && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              color: 'primary.main',
            }}
          >
            {icon}
          </Box>
        )}

        {/* Title with count badge */}
        <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="subtitle1" fontWeight={600}>
            {title}
          </Typography>
          {count !== undefined && count > 0 && (
            <Badge
              badgeContent={count}
              color="primary"
              sx={{
                '& .MuiBadge-badge': {
                  position: 'static',
                  transform: 'none',
                },
              }}
            />
          )}
        </Box>

        {/* Actions */}
        {actions && (
          <Box
            onClick={(e) => e.stopPropagation()}
            sx={{
              display: 'flex',
              gap: 0.5,
            }}
          >
            {actions}
          </Box>
        )}

        {/* Expand/collapse button */}
        <IconButton
          size="small"
          sx={{
            transition: 'transform 0.2s',
            transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
          }}
        >
          <ExpandMoreIcon />
        </IconButton>
      </Box>

      <Divider />

      {/* Content */}
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <Box sx={{ p: noPadding ? 0 : 2 }}>{children}</Box>
      </Collapse>
    </Paper>
  );
};

/**
 * Simple version without Paper wrapper
 */
export const CollapsibleSectionSimple: React.FC<CollapsibleSectionProps> = ({
  title,
  icon,
  children,
  defaultExpanded = true,
  persistKey,
  count,
  actions,
  noPadding = false,
}) => {
  const [expanded, setExpanded] = useState(() => {
    if (persistKey) {
      const saved = localStorage.getItem(`collapsible-${persistKey}`);
      if (saved !== null) {
        return saved === 'true';
      }
    }
    return defaultExpanded;
  });

  useEffect(() => {
    if (persistKey) {
      localStorage.setItem(`collapsible-${persistKey}`, String(expanded));
    }
  }, [expanded, persistKey]);

  const handleToggle = () => {
    setExpanded(!expanded);
  };

  return (
    <Box>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          py: 1,
          cursor: 'pointer',
          '&:hover': {
            backgroundColor: 'action.hover',
          },
          transition: 'background-color 0.2s',
        }}
        onClick={handleToggle}
      >
        {icon && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              color: 'primary.main',
            }}
          >
            {icon}
          </Box>
        )}

        <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body1" fontWeight={600}>
            {title}
          </Typography>
          {count !== undefined && count > 0 && (
            <Typography
              variant="caption"
              sx={{
                backgroundColor: 'primary.main',
                color: 'primary.contrastText',
                px: 1,
                py: 0.25,
                borderRadius: 1,
                fontWeight: 600,
              }}
            >
              {count}
            </Typography>
          )}
        </Box>

        {actions && (
          <Box onClick={(e) => e.stopPropagation()} sx={{ display: 'flex', gap: 0.5 }}>
            {actions}
          </Box>
        )}

        <IconButton
          size="small"
          sx={{
            transition: 'transform 0.2s',
            transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
          }}
        >
          <ExpandMoreIcon fontSize="small" />
        </IconButton>
      </Box>

      {/* Content */}
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <Box sx={{ p: noPadding ? 0 : 1 }}>{children}</Box>
      </Collapse>
    </Box>
  );
};
