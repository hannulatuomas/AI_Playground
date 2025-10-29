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
  InputAdornment,
  Alert,
  Tooltip,
  Tabs,
  Tab,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  Send as SendIcon,
  Delete as DeleteIcon,
  Link as LinkIcon,
  LinkOff as LinkOffIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
} from '@mui/icons-material';

interface Message {
  id: string;
  timestamp: Date;
  type: 'sent' | 'received' | 'error' | 'info';
  queue?: string;
  exchange?: string;
  routingKey?: string;
  content: string;
  parsedContent?: any;
}

const AMQPClient: React.FC = () => {
  const [url, setUrl] = useState('amqp://localhost');
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('disconnected');
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Send tab
  const [sendTab, setSendTab] = useState(0);
  const [queueName, setQueueName] = useState('');
  const [exchangeName, setExchangeName] = useState('');
  const [routingKey, setRoutingKey] = useState('');
  const [messageContent, setMessageContent] = useState('');

  // Receive tab
  const [consumeQueue, setConsumeQueue] = useState('');
  const [isConsuming, setIsConsuming] = useState(false);
  const [autoAck, setAutoAck] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleConnect = async () => {
    setError(null);
    try {
      const result = await (window as any).electron.invoke('amqp:connect', {
        url,
      });

      if (result.error) {
        setError(result.error);
      } else {
        setConnectionId(result.connectionId);
        setStatus('connecting');
        
        // Start polling for messages
        startPolling(result.connectionId);
      }
    } catch (err: any) {
      setError(`Connection failed: ${err.message}`);
    }
  };

  const handleDisconnect = async () => {
    if (!connectionId) return;

    try {
      await (window as any).electron.invoke('amqp:disconnect', {
        connectionId,
      });
      setStatus('disconnected');
      setConnectionId(null);
      setIsConsuming(false);
    } catch (err: any) {
      setError(`Disconnect failed: ${err.message}`);
    }
  };

  const handleSendToQueue = async () => {
    if (!connectionId || !queueName || !messageContent) return;

    try {
      // Assert queue first
      await (window as any).electron.invoke('amqp:assertQueue', {
        connectionId,
        queueName,
      });

      // Send message
      const result = await (window as any).electron.invoke('amqp:sendToQueue', {
        connectionId,
        queue: queueName,
        message: messageContent,
      });

      if (result.success) {
        setMessageContent('');
      } else {
        setError('Failed to send message');
      }
    } catch (err: any) {
      setError(`Send failed: ${err.message}`);
    }
  };

  const handlePublish = async () => {
    if (!connectionId || !exchangeName || !messageContent) return;

    try {
      // Assert exchange first
      await (window as any).electron.invoke('amqp:assertExchange', {
        connectionId,
        exchangeName,
        type: 'topic',
      });

      // Publish message
      const result = await (window as any).electron.invoke('amqp:publish', {
        connectionId,
        exchange: exchangeName,
        routingKey: routingKey || '',
        message: messageContent,
      });

      if (result.success) {
        setMessageContent('');
      } else {
        setError('Failed to publish message');
      }
    } catch (err: any) {
      setError(`Publish failed: ${err.message}`);
    }
  };

  const handleStartConsuming = async () => {
    if (!connectionId || !consumeQueue) return;

    try {
      // Assert queue first
      await (window as any).electron.invoke('amqp:assertQueue', {
        connectionId,
        queueName: consumeQueue,
      });

      // Start consuming
      const result = await (window as any).electron.invoke('amqp:consume', {
        connectionId,
        queue: consumeQueue,
        autoAck,
      });

      if (result.success) {
        setIsConsuming(true);
      } else {
        setError('Failed to start consuming');
      }
    } catch (err: any) {
      setError(`Consume failed: ${err.message}`);
    }
  };

  const handleStopConsuming = async () => {
    if (!connectionId || !consumeQueue) return;

    try {
      await (window as any).electron.invoke('amqp:stopConsuming', {
        connectionId,
        queue: consumeQueue,
      });
      setIsConsuming(false);
    } catch (err: any) {
      setError(`Stop consuming failed: ${err.message}`);
    }
  };

  const handleClearMessages = async () => {
    if (!connectionId) return;

    try {
      await (window as any).electron.invoke('amqp:clearMessages', {
        connectionId,
      });
      setMessages([]);
    } catch (err: any) {
      setError(`Clear messages failed: ${err.message}`);
    }
  };

  const startPolling = (connId: string) => {
    const interval = setInterval(async () => {
      try {
        const result = await (window as any).electron.invoke('amqp:getMessages', {
          connectionId: connId,
        });

        if (result.messages) {
          setMessages(result.messages);
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

  const getMessageColor = (type: string) => {
    switch (type) {
      case 'sent':
        return 'primary';
      case 'received':
        return 'success';
      case 'error':
        return 'error';
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
          <Typography variant="h6">AMQP/JMS Client</Typography>
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
            label="AMQP URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={status === 'connected' || status === 'connecting'}
            size="small"
            placeholder="amqp://localhost"
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

      {/* Send/Receive Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={sendTab} onChange={(_, v) => setSendTab(v)}>
          <Tab label="Send to Queue" />
          <Tab label="Publish to Exchange" />
          <Tab label="Receive from Queue" />
        </Tabs>
      </Box>

      {/* Send to Queue Tab */}
      {sendTab === 0 && (
        <Paper sx={{ m: 2, p: 2 }}>
          <TextField
            fullWidth
            label="Queue Name"
            value={queueName}
            onChange={(e) => setQueueName(e.target.value)}
            size="small"
            sx={{ mb: 2 }}
            disabled={status !== 'connected'}
          />
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Message"
            value={messageContent}
            onChange={(e) => setMessageContent(e.target.value)}
            size="small"
            sx={{ mb: 2 }}
            disabled={status !== 'connected'}
          />
          <Button
            variant="contained"
            onClick={handleSendToQueue}
            disabled={status !== 'connected' || !queueName || !messageContent}
            endIcon={<SendIcon />}
          >
            Send to Queue
          </Button>
        </Paper>
      )}

      {/* Publish to Exchange Tab */}
      {sendTab === 1 && (
        <Paper sx={{ m: 2, p: 2 }}>
          <TextField
            fullWidth
            label="Exchange Name"
            value={exchangeName}
            onChange={(e) => setExchangeName(e.target.value)}
            size="small"
            sx={{ mb: 2 }}
            disabled={status !== 'connected'}
          />
          <TextField
            fullWidth
            label="Routing Key"
            value={routingKey}
            onChange={(e) => setRoutingKey(e.target.value)}
            size="small"
            sx={{ mb: 2 }}
            disabled={status !== 'connected'}
          />
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Message"
            value={messageContent}
            onChange={(e) => setMessageContent(e.target.value)}
            size="small"
            sx={{ mb: 2 }}
            disabled={status !== 'connected'}
          />
          <Button
            variant="contained"
            onClick={handlePublish}
            disabled={status !== 'connected' || !exchangeName || !messageContent}
            endIcon={<SendIcon />}
          >
            Publish
          </Button>
        </Paper>
      )}

      {/* Receive from Queue Tab */}
      {sendTab === 2 && (
        <Paper sx={{ m: 2, p: 2 }}>
          <TextField
            fullWidth
            label="Queue Name"
            value={consumeQueue}
            onChange={(e) => setConsumeQueue(e.target.value)}
            size="small"
            sx={{ mb: 2 }}
            disabled={status !== 'connected' || isConsuming}
          />
          <FormControlLabel
            control={
              <Switch
                checked={autoAck}
                onChange={(e) => setAutoAck(e.target.checked)}
                disabled={isConsuming}
              />
            }
            label="Auto Acknowledge"
            sx={{ mb: 2 }}
          />
          <Box>
            {isConsuming ? (
              <Button
                variant="outlined"
                color="error"
                onClick={handleStopConsuming}
                startIcon={<StopIcon />}
              >
                Stop Consuming
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleStartConsuming}
                disabled={status !== 'connected' || !consumeQueue}
                startIcon={<PlayIcon />}
              >
                Start Consuming
              </Button>
            )}
          </Box>
        </Paper>
      )}

      {/* Messages Log */}
      <Box sx={{ flex: 1, overflow: 'auto', bgcolor: '#1e1e1e', p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="subtitle2" sx={{ color: '#fff' }}>
            Message Log ({messages.length})
          </Typography>
          <Tooltip title="Clear Messages">
            <IconButton size="small" onClick={handleClearMessages} sx={{ color: '#fff' }}>
              <DeleteIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <List sx={{ p: 0 }}>
          {messages.length === 0 ? (
            <Typography variant="body2" sx={{ color: '#888', textAlign: 'center', py: 4 }}>
              No messages yet. Connect and send/receive messages.
            </Typography>
          ) : (
            messages.map((msg) => (
              <ListItem
                key={msg.id}
                sx={{
                  display: 'block',
                  py: 1,
                  px: 2,
                  borderLeft: 3,
                  borderColor: `${getMessageColor(msg.type)}.main`,
                  bgcolor: 'rgba(255,255,255,0.05)',
                  mb: 1,
                  borderRadius: 1,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5, flexWrap: 'wrap' }}>
                  <Typography variant="caption" sx={{ color: '#888' }}>
                    {formatTimestamp(msg.timestamp)}
                  </Typography>
                  <Chip
                    label={msg.type}
                    size="small"
                    color={getMessageColor(msg.type) as any}
                    sx={{ height: 20, fontSize: '0.7rem' }}
                  />
                  {msg.queue && (
                    <Chip
                      label={`Queue: ${msg.queue}`}
                      size="small"
                      variant="outlined"
                      sx={{ height: 20, fontSize: '0.7rem', color: '#888' }}
                    />
                  )}
                  {msg.exchange && (
                    <Chip
                      label={`Exchange: ${msg.exchange}`}
                      size="small"
                      variant="outlined"
                      sx={{ height: 20, fontSize: '0.7rem', color: '#888' }}
                    />
                  )}
                  {msg.routingKey && (
                    <Chip
                      label={`Key: ${msg.routingKey}`}
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
                  {msg.content}
                </Typography>
                {msg.parsedContent && (
                  <Typography
                    variant="caption"
                    sx={{
                      color: '#4CAF50',
                      fontFamily: 'monospace',
                      display: 'block',
                      mt: 0.5,
                    }}
                  >
                    {JSON.stringify(msg.parsedContent, null, 2)}
                  </Typography>
                )}
              </ListItem>
            ))
          )}
          <div ref={messagesEndRef} />
        </List>
      </Box>
    </Box>
  );
};

export default AMQPClient;
