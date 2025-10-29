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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  Send as SendIcon,
  Delete as DeleteIcon,
  Link as LinkIcon,
  LinkOff as LinkOffIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
} from '@mui/icons-material';

interface MQTTMessage {
  id: string;
  timestamp: Date;
  type: 'published' | 'received' | 'error' | 'info';
  topic: string;
  payload: string;
  qos?: number;
  retain?: boolean;
  parsedPayload?: any;
}

interface Subscription {
  topic: string;
  qos: number;
}

const MQTTClient: React.FC = () => {
  const [brokerUrl, setBrokerUrl] = useState('mqtt://localhost:1883');
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('disconnected');
  const [messages, setMessages] = useState<MQTTMessage[]>([]);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);

  // Publish tab
  const [publishTopic, setPublishTopic] = useState('');
  const [publishMessage, setPublishMessage] = useState('');
  const [publishQos, setPublishQos] = useState<0 | 1 | 2>(0);
  const [publishRetain, setPublishRetain] = useState(false);

  // Subscribe tab
  const [subscribeTopic, setSubscribeTopic] = useState('');
  const [subscribeQos, setSubscribeQos] = useState<0 | 1 | 2>(0);

  const [activeTab, setActiveTab] = useState(0);
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
      const result = await (window as any).electron.invoke('mqtt:connect', {
        brokerUrl,
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
      await (window as any).electron.invoke('mqtt:disconnect', {
        connectionId,
      });
      setStatus('disconnected');
      setConnectionId(null);
      setSubscriptions([]);
    } catch (err: any) {
      setError(`Disconnect failed: ${err.message}`);
    }
  };

  const handlePublish = async () => {
    if (!connectionId || !publishTopic || !publishMessage) return;

    try {
      const result = await (window as any).electron.invoke('mqtt:publish', {
        connectionId,
        topic: publishTopic,
        message: publishMessage,
        qos: publishQos,
        retain: publishRetain,
      });

      if (result.success) {
        setPublishMessage('');
      } else {
        setError('Failed to publish message');
      }
    } catch (err: any) {
      setError(`Publish failed: ${err.message}`);
    }
  };

  const handleSubscribe = async () => {
    if (!connectionId || !subscribeTopic) return;

    try {
      const result = await (window as any).electron.invoke('mqtt:subscribe', {
        connectionId,
        topic: subscribeTopic,
        qos: subscribeQos,
      });

      if (result.success) {
        setSubscribeTopic('');
      } else {
        setError('Failed to subscribe');
      }
    } catch (err: any) {
      setError(`Subscribe failed: ${err.message}`);
    }
  };

  const handleUnsubscribe = async (topic: string) => {
    if (!connectionId) return;

    try {
      await (window as any).electron.invoke('mqtt:unsubscribe', {
        connectionId,
        topic,
      });
    } catch (err: any) {
      setError(`Unsubscribe failed: ${err.message}`);
    }
  };

  const handleClearMessages = async () => {
    if (!connectionId) return;

    try {
      await (window as any).electron.invoke('mqtt:clearMessages', {
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
        const result = await (window as any).electron.invoke('mqtt:getMessages', {
          connectionId: connId,
        });

        if (result.messages) {
          setMessages(result.messages);
        }

        if (result.subscriptions) {
          setSubscriptions(result.subscriptions);
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

  const getMessageColor = (type: string) => {
    switch (type) {
      case 'published':
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
          <Typography variant="h6">MQTT Client</Typography>
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
            label="Broker URL"
            value={brokerUrl}
            onChange={(e) => setBrokerUrl(e.target.value)}
            disabled={status === 'connected' || status === 'connecting'}
            size="small"
            placeholder="mqtt://localhost:1883"
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

      {/* Statistics */}
      {stats && (
        <Paper sx={{ p: 1.5, m: 2, bgcolor: 'action.hover' }}>
          <Box sx={{ display: 'flex', gap: 3, alignItems: 'center', flexWrap: 'wrap' }}>
            <Typography variant="caption">
              <strong>Total:</strong> {stats.totalMessages}
            </Typography>
            <Typography variant="caption">
              <strong>Published:</strong> {stats.publishedCount}
            </Typography>
            <Typography variant="caption">
              <strong>Received:</strong> {stats.receivedCount}
            </Typography>
            <Typography variant="caption">
              <strong>Subscriptions:</strong> {stats.subscriptionCount}
            </Typography>
          </Box>
        </Paper>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
          <Tab label="Publish" />
          <Tab label="Subscribe" />
          <Tab label={`Subscriptions (${subscriptions.length})`} />
        </Tabs>
      </Box>

      {/* Publish Tab */}
      {activeTab === 0 && (
        <Paper sx={{ m: 2, p: 2 }}>
          <TextField
            fullWidth
            label="Topic"
            value={publishTopic}
            onChange={(e) => setPublishTopic(e.target.value)}
            size="small"
            sx={{ mb: 2 }}
            disabled={status !== 'connected'}
            placeholder="home/temperature"
          />
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>QoS</InputLabel>
              <Select
                value={publishQos}
                label="QoS"
                onChange={(e) => setPublishQos(e.target.value as 0 | 1 | 2)}
              >
                <MenuItem value={0}>0 - At most once</MenuItem>
                <MenuItem value={1}>1 - At least once</MenuItem>
                <MenuItem value={2}>2 - Exactly once</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Retain</InputLabel>
              <Select
                value={publishRetain ? 'true' : 'false'}
                label="Retain"
                onChange={(e) => setPublishRetain(e.target.value === 'true')}
              >
                <MenuItem value="false">No</MenuItem>
                <MenuItem value="true">Yes</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Message"
            value={publishMessage}
            onChange={(e) => setPublishMessage(e.target.value)}
            size="small"
            sx={{ mb: 2 }}
            disabled={status !== 'connected'}
          />
          <Button
            variant="contained"
            onClick={handlePublish}
            disabled={status !== 'connected' || !publishTopic || !publishMessage}
            endIcon={<SendIcon />}
          >
            Publish
          </Button>
        </Paper>
      )}

      {/* Subscribe Tab */}
      {activeTab === 1 && (
        <Paper sx={{ m: 2, p: 2 }}>
          <TextField
            fullWidth
            label="Topic Pattern"
            value={subscribeTopic}
            onChange={(e) => setSubscribeTopic(e.target.value)}
            size="small"
            sx={{ mb: 2 }}
            disabled={status !== 'connected'}
            placeholder="home/# or sensors/+/temperature"
          />
          <FormControl size="small" fullWidth sx={{ mb: 2 }}>
            <InputLabel>QoS</InputLabel>
            <Select
              value={subscribeQos}
              label="QoS"
              onChange={(e) => setSubscribeQos(e.target.value as 0 | 1 | 2)}
            >
              <MenuItem value={0}>0 - At most once</MenuItem>
              <MenuItem value={1}>1 - At least once</MenuItem>
              <MenuItem value={2}>2 - Exactly once</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="contained"
            onClick={handleSubscribe}
            disabled={status !== 'connected' || !subscribeTopic}
            startIcon={<AddIcon />}
          >
            Subscribe
          </Button>
        </Paper>
      )}

      {/* Subscriptions Tab */}
      {activeTab === 2 && (
        <Paper sx={{ m: 2, p: 2 }}>
          {subscriptions.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              No active subscriptions
            </Typography>
          ) : (
            <List>
              {subscriptions.map((sub, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={sub.topic}
                    secondary={`QoS: ${sub.qos}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      onClick={() => handleUnsubscribe(sub.topic)}
                      size="small"
                    >
                      <RemoveIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
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
              No messages yet. Publish or subscribe to see messages.
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
                  <Chip
                    label={msg.topic}
                    size="small"
                    variant="outlined"
                    sx={{ height: 20, fontSize: '0.7rem', color: '#888' }}
                  />
                  {msg.qos !== undefined && (
                    <Chip
                      label={`QoS ${msg.qos}`}
                      size="small"
                      variant="outlined"
                      sx={{ height: 20, fontSize: '0.7rem', color: '#888' }}
                    />
                  )}
                  {msg.retain && (
                    <Chip
                      label="Retained"
                      size="small"
                      variant="outlined"
                      sx={{ height: 20, fontSize: '0.7rem', color: '#FFA726' }}
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
                  {msg.payload}
                </Typography>
                {msg.parsedPayload && (
                  <Typography
                    variant="caption"
                    sx={{
                      color: '#4CAF50',
                      fontFamily: 'monospace',
                      display: 'block',
                      mt: 0.5,
                    }}
                  >
                    {JSON.stringify(msg.parsedPayload, null, 2)}
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

export default MQTTClient;
