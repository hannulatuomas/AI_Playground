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
} from '@mui/material';
import {
  Send as SendIcon,
  Delete as DeleteIcon,
  Clear as ClearIcon,
  Link as LinkIcon,
  LinkOff as LinkOffIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

interface LogEntry {
  id: string;
  timestamp: Date;
  type: 'sent' | 'received' | 'error' | 'info' | 'connection';
  message: string;
  data?: any;
}

const WebSocketClient: React.FC = () => {
  const [url, setUrl] = useState('ws://localhost:8080');
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('disconnected');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  const handleConnect = async () => {
    setError(null);
    try {
      const result = await (window as any).electron.invoke('websocket:connect', {
        url,
      });

      if (result.error) {
        setError(result.error);
      } else {
        setConnectionId(result.connectionId);
        setStatus('connecting');
        
        // Start polling for logs
        startPolling(result.connectionId);
      }
    } catch (err: any) {
      setError(`Connection failed: ${err.message}`);
    }
  };

  const handleDisconnect = async () => {
    if (!connectionId) return;

    try {
      await (window as any).electron.invoke('websocket:disconnect', {
        connectionId,
      });
      setStatus('disconnected');
      setConnectionId(null);
    } catch (err: any) {
      setError(`Disconnect failed: ${err.message}`);
    }
  };

  const handleSend = async () => {
    if (!connectionId || !message.trim()) return;

    try {
      const result = await (window as any).electron.invoke('websocket:send', {
        connectionId,
        message: message.trim(),
      });

      if (result.success) {
        setMessage('');
      } else {
        setError('Failed to send message');
      }
    } catch (err: any) {
      setError(`Send failed: ${err.message}`);
    }
  };

  const handlePing = async () => {
    if (!connectionId) return;

    try {
      await (window as any).electron.invoke('websocket:ping', {
        connectionId,
      });
    } catch (err: any) {
      setError(`Ping failed: ${err.message}`);
    }
  };

  const handleClearLogs = async () => {
    if (!connectionId) return;

    try {
      await (window as any).electron.invoke('websocket:clearLogs', {
        connectionId,
      });
      setLogs([]);
    } catch (err: any) {
      setError(`Clear logs failed: ${err.message}`);
    }
  };

  const startPolling = (connId: string) => {
    const interval = setInterval(async () => {
      try {
        const result = await (window as any).electron.invoke('websocket:getLogs', {
          connectionId: connId,
        });

        if (result.logs) {
          setLogs(result.logs);
        }

        if (result.status) {
          setStatus(result.status);
        }
      } catch (err) {
        // Ignore polling errors
      }
    }, 500);

    // Cleanup on unmount
    return () => clearInterval(interval);
  };

  const getLogColor = (type: string) => {
    switch (type) {
      case 'sent':
        return 'primary';
      case 'received':
        return 'success';
      case 'error':
        return 'error';
      case 'connection':
        return 'info';
      case 'info':
        return 'default';
      default:
        return 'default';
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

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">WebSocket Client</Typography>
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
            label="WebSocket URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={status === 'connected' || status === 'connecting'}
            size="small"
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
              startIcon={<LinkOffIcon />}
              sx={{ minWidth: 120 }}
            >
              Disconnect
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={handleConnect}
              startIcon={<LinkIcon />}
              sx={{ minWidth: 120 }}
            >
              Connect
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

      {/* Logs */}
      <Box sx={{ flex: 1, overflow: 'auto', bgcolor: '#1e1e1e', p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="subtitle2" sx={{ color: '#fff' }}>
            Message Log ({logs.length})
          </Typography>
          <Box>
            <Tooltip title="Ping">
              <span>
                <IconButton
                  size="small"
                  onClick={handlePing}
                  disabled={status !== 'connected'}
                  sx={{ color: '#fff' }}
                >
                  <RefreshIcon />
                </IconButton>
              </span>
            </Tooltip>
            <Tooltip title="Clear Logs">
              <IconButton size="small" onClick={handleClearLogs} sx={{ color: '#fff' }}>
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <List sx={{ p: 0 }}>
          {logs.length === 0 ? (
            <Typography variant="body2" sx={{ color: '#888', textAlign: 'center', py: 4 }}>
              No messages yet. Connect to start logging.
            </Typography>
          ) : (
            logs.map((log) => (
              <ListItem
                key={log.id}
                sx={{
                  display: 'block',
                  py: 1,
                  px: 2,
                  borderLeft: 3,
                  borderColor: `${getLogColor(log.type)}.main`,
                  bgcolor: 'rgba(255,255,255,0.05)',
                  mb: 1,
                  borderRadius: 1,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <Typography variant="caption" sx={{ color: '#888' }}>
                    {formatTimestamp(log.timestamp)}
                  </Typography>
                  <Chip
                    label={log.type}
                    size="small"
                    color={getLogColor(log.type) as any}
                    sx={{ height: 20, fontSize: '0.7rem' }}
                  />
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
                  {log.message}
                </Typography>
                {log.data && (
                  <Typography
                    variant="caption"
                    sx={{
                      color: '#4CAF50',
                      fontFamily: 'monospace',
                      display: 'block',
                      mt: 0.5,
                    }}
                  >
                    {JSON.stringify(log.data, null, 2)}
                  </Typography>
                )}
              </ListItem>
            ))
          )}
          <div ref={logsEndRef} />
        </List>
      </Box>

      {/* Message Input */}
      <Paper sx={{ p: 2, borderRadius: 0, borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder="Enter message to send..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            disabled={status !== 'connected'}
            size="small"
          />
          <Button
            variant="contained"
            onClick={handleSend}
            disabled={status !== 'connected' || !message.trim()}
            endIcon={<SendIcon />}
            sx={{ minWidth: 100 }}
          >
            Send
          </Button>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Press Enter to send, Shift+Enter for new line
        </Typography>
      </Paper>
    </Box>
  );
};

export default WebSocketClient;
