import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  List,
  ListItem,
  Chip,
  IconButton,
  Divider,
  InputAdornment,
  Alert,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Badge,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Delete as DeleteIcon,
  Link as LinkIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';

interface SSEEvent {
  id: string;
  timestamp: Date;
  type: string;
  data: string;
  eventId?: string;
  parsedData?: any;
}

const SSEViewer: React.FC = () => {
  const [url, setUrl] = useState('');
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('disconnected');
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [eventTypes, setEventTypes] = useState<string[]>([]);
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);
  const eventsEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    eventsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [events]);

  const handleConnect = async () => {
    setError(null);
    try {
      const result = await (window as any).electron.invoke('sse:connect', {
        url,
      });

      if (result.error) {
        setError(result.error);
      } else {
        setConnectionId(result.connectionId);
        setStatus('connecting');
        
        // Start polling for events
        startPolling(result.connectionId);
      }
    } catch (err: any) {
      setError(`Connection failed: ${err.message}`);
    }
  };

  const handleDisconnect = async () => {
    if (!connectionId) return;

    try {
      await (window as any).electron.invoke('sse:disconnect', {
        connectionId,
      });
      setStatus('disconnected');
      setConnectionId(null);
    } catch (err: any) {
      setError(`Disconnect failed: ${err.message}`);
    }
  };

  const handleClearEvents = async () => {
    if (!connectionId) return;

    try {
      await (window as any).electron.invoke('sse:clearEvents', {
        connectionId,
      });
      setEvents([]);
    } catch (err: any) {
      setError(`Clear events failed: ${err.message}`);
    }
  };

  const startPolling = (connId: string) => {
    const interval = setInterval(async () => {
      try {
        const result = await (window as any).electron.invoke('sse:getEvents', {
          connectionId: connId,
        });

        if (result.events) {
          setEvents(result.events);
        }

        if (result.eventTypes) {
          setEventTypes(result.eventTypes);
        }

        if (result.status) {
          setStatus(result.status);
        }

        if (result.stats) {
          setStats(result.stats);
        }
      } catch (err) {
        // Ignore polling errors
      }
    }, 500);

    // Cleanup on unmount
    return () => clearInterval(interval);
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'message':
        return 'success';
      case 'error':
        return 'error';
      case 'connection':
        return 'info';
      default:
        return 'primary';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return 'success';
      case 'connecting':
        return 'warning';
      case 'disconnected':
        return 'default';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    const date = new Date(timestamp);
    const time = date.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const ms = date.getMilliseconds().toString().padStart(3, '0');
    return `${time}.${ms}`;
  };

  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) {
      return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  };

  const filteredEvents = selectedFilter === 'all'
    ? events
    : events.filter(event => event.type === selectedFilter);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">SSE Stream Viewer</Typography>
          <Chip
            label={status.toUpperCase()}
            color={getStatusColor() as any}
            size="small"
          />
        </Box>

        {/* Connection Controls */}
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
          <TextField
            fullWidth
            label="SSE Endpoint URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={status === 'connected' || status === 'connecting'}
            size="small"
            placeholder="https://api.example.com/events"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <LinkIcon />
                </InputAdornment>
              ),
            }}
          />
          {status === 'connected' || status === 'connecting' ? (
            <Button
              variant="outlined"
              color="error"
              onClick={handleDisconnect}
              startIcon={<StopIcon />}
              sx={{ minWidth: 120 }}
            >
              Stop
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={handleConnect}
              startIcon={<PlayIcon />}
              sx={{ minWidth: 120 }}
            >
              Start
            </Button>
          )}
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ m: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Statistics Bar */}
      {stats && (
        <Paper sx={{ p: 1.5, m: 2, bgcolor: 'action.hover' }}>
          <Box sx={{ display: 'flex', gap: 3, alignItems: 'center', flexWrap: 'wrap' }}>
            <Typography variant="caption">
              <strong>Total Events:</strong> {stats.totalEvents}
            </Typography>
            <Typography variant="caption">
              <strong>Duration:</strong> {formatDuration(stats.connectionDuration)}
            </Typography>
            {Object.entries(stats.eventTypes || {}).map(([type, count]) => (
              <Chip
                key={type}
                label={`${type}: ${count}`}
                size="small"
                color={getEventColor(type) as any}
                variant="outlined"
              />
            ))}
          </Box>
        </Paper>
      )}

      {/* Filter Bar */}
      <Box sx={{ px: 2, pb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Filter Events</InputLabel>
          <Select
            value={selectedFilter}
            label="Filter Events"
            onChange={(e) => setSelectedFilter(e.target.value)}
            startAdornment={<FilterIcon sx={{ mr: 1, color: 'action.active' }} />}
          >
            <MenuItem value="all">
              <Badge badgeContent={events.length} color="primary" max={999}>
                <span>All Events</span>
              </Badge>
            </MenuItem>
            {eventTypes.map((type) => (
              <MenuItem key={type} value={type}>
                <Badge
                  badgeContent={events.filter(e => e.type === type).length}
                  color={getEventColor(type) as any}
                  max={999}
                >
                  <span>{type}</span>
                </Badge>
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Tooltip title="Clear Events">
          <IconButton size="small" onClick={handleClearEvents}>
            <DeleteIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Events Stream */}
      <Box sx={{ flex: 1, overflow: 'auto', bgcolor: '#1e1e1e', p: 2 }}>
        <List sx={{ p: 0 }}>
          {filteredEvents.length === 0 ? (
            <Typography variant="body2" sx={{ color: '#888', textAlign: 'center', py: 4 }}>
              {events.length === 0
                ? 'No events yet. Start streaming to see events.'
                : 'No events match the selected filter.'}
            </Typography>
          ) : (
            filteredEvents.map((event) => (
              <ListItem
                key={event.id}
                sx={{
                  display: 'block',
                  py: 1,
                  px: 2,
                  borderLeft: 3,
                  borderColor: `${getEventColor(event.type)}.main`,
                  bgcolor: 'rgba(255,255,255,0.05)',
                  mb: 1,
                  borderRadius: 1,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <Typography variant="caption" sx={{ color: '#888' }}>
                    {formatTimestamp(event.timestamp)}
                  </Typography>
                  <Chip
                    label={event.type}
                    size="small"
                    color={getEventColor(event.type) as any}
                    sx={{ height: 20, fontSize: '0.7rem' }}
                  />
                  {event.eventId && (
                    <Chip
                      label={`ID: ${event.eventId}`}
                      size="small"
                      variant="outlined"
                      sx={{ height: 20, fontSize: '0.7rem', color: '#888' }}
                    />
                  )}
                </Box>
                <Typography
                  variant="body2"
                  sx={{
                    color: '#fff',
                    fontFamily: 'monospace',
                    wordBreak: 'break-all',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {event.data}
                </Typography>
                {event.parsedData && (
                  <Typography
                    variant="caption"
                    sx={{
                      color: '#4CAF50',
                      fontFamily: 'monospace',
                      display: 'block',
                      mt: 0.5,
                    }}
                  >
                    {JSON.stringify(event.parsedData, null, 2)}
                  </Typography>
                )}
              </ListItem>
            ))
          )}
          <div ref={eventsEndRef} />
        </List>
      </Box>

      {/* Footer */}
      <Paper sx={{ p: 1.5, borderRadius: 0, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary">
          Server-Sent Events (SSE) stream viewer with real-time event monitoring
        </Typography>
      </Paper>
    </Box>
  );
};

export default SSEViewer;
