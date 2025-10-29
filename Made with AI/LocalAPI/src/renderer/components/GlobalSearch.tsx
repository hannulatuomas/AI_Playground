/**
 * GlobalSearch - Search Across All Entities UI
 * 
 * Features:
 * - Search input with Ctrl+K shortcut
 * - Real-time search results
 * - Category filtering
 * - Result previews
 * - Keyboard navigation
 * - Search history
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogContent,
  TextField,
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Typography,
  Chip,
  InputAdornment,
  Tabs,
  Tab,
  CircularProgress,
  Divider,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import FolderIcon from '@mui/icons-material/Folder';
import PublicIcon from '@mui/icons-material/Public';
import CodeIcon from '@mui/icons-material/Code';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import StarIcon from '@mui/icons-material/Star';
import TabIcon from '@mui/icons-material/Tab';

interface SearchResult {
  entity: {
    id: string;
    type: string;
    title: string;
    description?: string;
    path?: string;
    lastModified?: number;
  };
  score: number;
  matches: string[];
  highlights: string[];
}

interface GlobalSearchProps {
  open: boolean;
  onClose: () => void;
  onResultSelect?: (result: SearchResult) => void;
}

export const GlobalSearch: React.FC<GlobalSearchProps> = ({ open, onClose, onResultSelect }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(false);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  // Load search history
  useEffect(() => {
    if (open) {
      loadSearchHistory();
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [open]);

  // Search when query changes
  useEffect(() => {
    if (open) {
      performSearch();
    }
  }, [query, selectedCategory, open]);

  // Keyboard navigation
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
          handleResultClick(results[selectedIndex]);
        }
      } else if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [open, results, selectedIndex]);

  // Auto-scroll selected item
  useEffect(() => {
    if (listRef.current && results.length > 0) {
      const selectedElement = listRef.current.children[selectedIndex] as HTMLElement;
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }
    }
  }, [selectedIndex]);

  const loadSearchHistory = async () => {
    try {
      // Would call: const history = await window.electronAPI.search.getHistory();
      setSearchHistory([]);
    } catch (error) {
      console.error('Error loading search history:', error);
    }
  };

  const performSearch = async () => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      // Mock search - in real implementation would call:
      // const searchResults = await window.electronAPI.search.search(query, { types: selectedCategory !== 'all' ? [selectedCategory] : undefined });
      
      // For now, return empty results
      setResults([]);
      setSelectedIndex(0);
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResultClick = (result: SearchResult) => {
    onResultSelect?.(result);
    onClose();
  };

  const handleHistoryClick = (historyQuery: string) => {
    setQuery(historyQuery);
  };

  const getIcon = (type: string) => {
    const iconProps = { fontSize: 'small' as const };
    switch (type) {
      case 'request':
        return <InsertDriveFileIcon {...iconProps} />;
      case 'collection':
        return <FolderIcon {...iconProps} />;
      case 'environment':
        return <PublicIcon {...iconProps} />;
      case 'variable':
        return <CodeIcon {...iconProps} />;
      case 'history':
        return <AccessTimeIcon {...iconProps} />;
      case 'favorite':
        return <StarIcon {...iconProps} />;
      case 'tab':
        return <TabIcon {...iconProps} />;
      default:
        return <InsertDriveFileIcon {...iconProps} />;
    }
  };

  const getTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
      request: '#2196F3',
      collection: '#4CAF50',
      environment: '#9C27B0',
      variable: '#FF9800',
      history: '#607D8B',
      favorite: '#FFC107',
      tab: '#00BCD4',
    };
    return colors[type] || '#757575';
  };

  const getCategoryCounts = () => {
    const counts: Record<string, number> = {};
    results.forEach(result => {
      counts[result.entity.type] = (counts[result.entity.type] || 0) + 1;
    });
    return counts;
  };

  const filteredResults = selectedCategory === 'all'
    ? results
    : results.filter(r => r.entity.type === selectedCategory);

  const categoryCounts = getCategoryCounts();

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          position: 'fixed',
          top: '10%',
          m: 0,
          maxHeight: '80vh',
        },
      }}
    >
      <DialogContent sx={{ p: 0 }}>
        {/* Search Input */}
        <Box sx={{ p: 2 }}>
          <TextField
            inputRef={inputRef}
            fullWidth
            placeholder="Search requests, collections, environments, variables..."
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
              endAdornment: loading && (
                <InputAdornment position="end">
                  <CircularProgress size={20} />
                </InputAdornment>
              ),
            }}
          />
        </Box>

        {/* Category Tabs */}
        {results.length > 0 && (
          <Tabs
            value={selectedCategory}
            onChange={(_, value) => {
              setSelectedCategory(value);
              setSelectedIndex(0);
            }}
            variant="scrollable"
            sx={{ borderTop: 1, borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab 
              label={`All (${results.length})`} 
              value="all" 
            />
            {categoryCounts.request && (
              <Tab label={`Requests (${categoryCounts.request})`} value="request" />
            )}
            {categoryCounts.collection && (
              <Tab label={`Collections (${categoryCounts.collection})`} value="collection" />
            )}
            {categoryCounts.environment && (
              <Tab label={`Environments (${categoryCounts.environment})`} value="environment" />
            )}
            {categoryCounts.variable && (
              <Tab label={`Variables (${categoryCounts.variable})`} value="variable" />
            )}
            {categoryCounts.favorite && (
              <Tab label={`Favorites (${categoryCounts.favorite})`} value="favorite" />
            )}
          </Tabs>
        )}

        {/* Results or History */}
        <Box sx={{ maxHeight: '60vh', overflow: 'auto' }}>
          {!query && searchHistory.length > 0 ? (
            // Search History
            <Box>
              <Box sx={{ px: 2, py: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <HistoryIcon fontSize="small" color="action" />
                <Typography variant="caption" color="textSecondary">
                  Recent Searches
                </Typography>
              </Box>
              <List>
                {searchHistory.map((historyQuery, index) => (
                  <ListItem key={index} disablePadding>
                    <ListItemButton onClick={() => handleHistoryClick(historyQuery)}>
                      <ListItemIcon>
                        <AccessTimeIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={historyQuery} />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </Box>
          ) : query && filteredResults.length === 0 && !loading ? (
            // No Results
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <SearchIcon sx={{ fontSize: 48, color: 'text.secondary', opacity: 0.5 }} />
              <Typography color="textSecondary" sx={{ mt: 1 }}>
                No results found for "{query}"
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Try different keywords or check your filters
              </Typography>
            </Box>
          ) : (
            // Search Results
            <List ref={listRef}>
              {filteredResults.map((result, index) => {
                const isSelected = index === selectedIndex;
                return (
                  <React.Fragment key={result.entity.id}>
                    {index > 0 && <Divider />}
                    <ListItem
                      disablePadding
                      sx={{
                        backgroundColor: isSelected ? 'action.selected' : 'transparent',
                      }}
                    >
                      <ListItemButton onClick={() => handleResultClick(result)}>
                        <ListItemIcon
                          sx={{
                            color: getTypeColor(result.entity.type),
                          }}
                        >
                          {getIcon(result.entity.type)}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <span dangerouslySetInnerHTML={{ __html: result.highlights[0] || result.entity.title }} />
                              <Chip
                                label={result.entity.type}
                                size="small"
                                sx={{
                                  height: 20,
                                  fontSize: '0.7rem',
                                  backgroundColor: getTypeColor(result.entity.type),
                                  color: 'white',
                                }}
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              {result.entity.path && (
                                <Typography variant="caption" color="textSecondary" display="block">
                                  {result.entity.path}
                                </Typography>
                              )}
                              {result.highlights[1] && (
                                <Typography
                                  variant="caption"
                                  color="textSecondary"
                                  dangerouslySetInnerHTML={{ __html: result.highlights[1] }}
                                />
                              )}
                              <Box sx={{ mt: 0.5, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                {result.matches.map(match => (
                                  <Chip
                                    key={match}
                                    label={match}
                                    size="small"
                                    variant="outlined"
                                    sx={{ height: 18, fontSize: '0.65rem' }}
                                  />
                                ))}
                              </Box>
                            </Box>
                          }
                        />
                      </ListItemButton>
                    </ListItem>
                  </React.Fragment>
                );
              })}
            </List>
          )}
        </Box>

        {/* Footer */}
        <Box sx={{ px: 2, py: 1, backgroundColor: 'action.hover', borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="textSecondary">
            ↑↓ Navigate • Enter Select • Esc Close • Ctrl+K to search anytime
          </Typography>
        </Box>
      </DialogContent>
    </Dialog>
  );
};
