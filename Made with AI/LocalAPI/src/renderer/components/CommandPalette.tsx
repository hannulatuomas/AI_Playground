/**
 * CommandPalette - Quick Actions Command Palette (Ctrl+P)
 * 
 * Features:
 * - Fuzzy search across all commands
 * - Keyboard navigation
 * - Recent commands
 * - Category grouping
 * - Keyboard shortcuts display
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogContent,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Typography,
  Box,
  Chip,
  InputAdornment,
  Divider,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
}

interface Command {
  id: string;
  label: string;
  category: string;
  description?: string;
  shortcut?: string;
  icon?: string;
  enabled?: boolean;
  keywords?: string[];
}

interface CommandMatch {
  command: Command;
  score: number;
  highlightedLabel: string;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ open, onClose }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<CommandMatch[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // Load commands when opened
  useEffect(() => {
    if (open) {
      loadCommands();
      setQuery('');
      setSelectedIndex(0);
      // Focus input after a short delay
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [open]);

  // Search commands when query changes
  useEffect(() => {
    if (open) {
      searchCommands();
    }
  }, [query, open]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!open) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => (prev < results.length - 1 ? prev + 1 : prev));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => (prev > 0 ? prev - 1 : 0));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (results[selectedIndex]) {
          executeCommand(results[selectedIndex].command.id);
        }
      } else if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [open, results, selectedIndex]);

  // Auto-scroll selected item into view
  useEffect(() => {
    if (listRef.current && results.length > 0) {
      const selectedElement = listRef.current.children[selectedIndex] as HTMLElement;
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }
    }
  }, [selectedIndex]);

  const loadCommands = async () => {
    try {
      setLoading(true);
      const recent = await window.electronAPI.commands.getRecent();
      if (recent && recent.length > 0) {
        setResults(recent.map((cmd: Command) => ({
          command: cmd,
          score: 0,
          highlightedLabel: cmd.label,
        })));
      }
    } catch (error) {
      console.error('Error loading commands:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchCommands = async () => {
    try {
      setLoading(true);
      const matches = await window.electronAPI.commands.search(query);
      setResults(matches || []);
      setSelectedIndex(0);
    } catch (error) {
      console.error('Error searching commands:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const executeCommand = async (commandId: string) => {
    try {
      const success = await window.electronAPI.commands.execute(commandId);
      if (success) {
        onClose();
      }
    } catch (error) {
      console.error('Error executing command:', error);
    }
  };

  const getCategoryIcon = (category: string) => {
    const icons: Record<string, string> = {
      File: '📄',
      Edit: '✏️',
      View: '👁️',
      Go: '➡️',
      Window: '🪟',
      Tools: '🔧',
      Help: '❓',
    };
    return icons[category] || '📌';
  };

  const groupByCategory = (matches: CommandMatch[]) => {
    const grouped: Record<string, CommandMatch[]> = {};
    
    matches.forEach(match => {
      const category = match.command.category;
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(match);
    });

    return grouped;
  };

  const renderResults = () => {
    if (loading) {
      return (
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="textSecondary">Searching...</Typography>
        </Box>
      );
    }

    if (results.length === 0) {
      return (
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="textSecondary">
            {query ? 'No commands found' : 'Type to search commands'}
          </Typography>
        </Box>
      );
    }

    // Show recent commands without grouping if no query
    if (!query) {
      return (
        <Box>
          <Box sx={{ px: 2, py: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <HistoryIcon fontSize="small" color="action" />
            <Typography variant="caption" color="textSecondary">
              Recent Commands
            </Typography>
          </Box>
          <List ref={listRef} sx={{ maxHeight: 400, overflow: 'auto' }}>
            {results.map((match, index) => renderCommandItem(match, index))}
          </List>
        </Box>
      );
    }

    // Group by category when searching
    const grouped = groupByCategory(results);
    const categories = Object.keys(grouped);

    return (
      <List ref={listRef} sx={{ maxHeight: 400, overflow: 'auto' }}>
        {categories.map((category, catIndex) => (
          <React.Fragment key={category}>
            {catIndex > 0 && <Divider />}
            <Box sx={{ px: 2, py: 1, backgroundColor: 'action.hover' }}>
              <Typography variant="caption" fontWeight="bold">
                {getCategoryIcon(category)} {category}
              </Typography>
            </Box>
            {grouped[category].map((match, index) => {
              const globalIndex = results.indexOf(match);
              return renderCommandItem(match, globalIndex);
            })}
          </React.Fragment>
        ))}
      </List>
    );
  };

  const renderCommandItem = (match: CommandMatch, index: number) => {
    const { command, highlightedLabel } = match;
    const isSelected = index === selectedIndex;

    return (
      <ListItem
        key={command.id}
        button
        selected={isSelected}
        onClick={() => executeCommand(command.id)}
        sx={{
          '&.Mui-selected': {
            backgroundColor: 'primary.main',
            color: 'primary.contrastText',
            '&:hover': {
              backgroundColor: 'primary.dark',
            },
          },
        }}
      >
        <ListItemIcon sx={{ minWidth: 40 }}>
          <span style={{ fontSize: '1.2rem' }}>{command.icon || '⚡'}</span>
        </ListItemIcon>
        <ListItemText
          primary={
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span dangerouslySetInnerHTML={{ __html: highlightedLabel }} />
              {command.shortcut && (
                <Chip
                  label={command.shortcut}
                  size="small"
                  variant="outlined"
                  sx={{
                    height: 20,
                    fontSize: '0.7rem',
                    fontFamily: 'monospace',
                    ml: 2,
                  }}
                />
              )}
            </Box>
          }
          secondary={command.description}
          secondaryTypographyProps={{
            sx: { color: isSelected ? 'inherit' : 'text.secondary', opacity: isSelected ? 0.8 : 1 },
          }}
        />
      </ListItem>
    );
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          position: 'fixed',
          top: '15%',
          m: 0,
        },
      }}
    >
      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ p: 2 }}>
          <TextField
            inputRef={inputRef}
            fullWidth
            placeholder="Type a command or search..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            variant="outlined"
            autoComplete="off"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'background.paper',
              },
            }}
          />
        </Box>

        {renderResults()}

        <Box sx={{ px: 2, py: 1, backgroundColor: 'action.hover', borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="textSecondary">
            ↑↓ Navigate • Enter Select • Esc Close
          </Typography>
        </Box>
      </DialogContent>
    </Dialog>
  );
};
