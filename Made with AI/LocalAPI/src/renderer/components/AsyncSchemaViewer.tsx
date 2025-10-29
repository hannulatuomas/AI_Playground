import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Code as CodeIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AsyncSchemaViewer: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [schemaType, setSchemaType] = useState<'asyncapi' | 'avro'>('asyncapi');
  const [schemaInput, setSchemaInput] = useState('');
  const [parsedData, setParsedData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleParse = async () => {
    setError(null);
    setParsedData(null);

    try {
      if (schemaType === 'asyncapi') {
        const result = await (window as any).electron.invoke('asyncapi:parse', {
          schema: schemaInput,
        });

        if (result.error) {
          setError(result.error);
        } else {
          setParsedData(result.data);
        }
      } else {
        const result = await (window as any).electron.invoke('avro:parse', {
          schema: schemaInput,
        });

        if (result.error) {
          setError(result.error);
        } else {
          setParsedData(result.data);
        }
      }
    } catch (err: any) {
      setError(`Parse failed: ${err.message}`);
    }
  };

  const renderAsyncAPIInfo = () => {
    if (!parsedData) return null;

    return (
      <Box>
        {/* Info */}
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="h6">{parsedData.title}</Typography>
          <Typography variant="body2" color="text.secondary">
            Version: {parsedData.version}
          </Typography>
          {parsedData.description && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              {parsedData.description}
            </Typography>
          )}
        </Paper>

        {/* Servers */}
        {parsedData.servers && parsedData.servers.length > 0 && (
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Servers ({parsedData.servers.length})
            </Typography>
            <List dense>
              {parsedData.servers.map((server: any, index: number) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={server.name}
                    secondary={`${server.protocol}://${server.url}`}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        )}

        {/* Channels */}
        {parsedData.channels && parsedData.channels.length > 0 && (
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Channels ({parsedData.channels.length})
            </Typography>
            {parsedData.channels.map((channel: any, index: number) => (
              <Accordion key={index}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>{channel.name}</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {channel.description && (
                    <Typography variant="body2" paragraph>
                      {channel.description}
                    </Typography>
                  )}
                  {channel.operations && channel.operations.length > 0 && (
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Operations:
                      </Typography>
                      {channel.operations.map((op: any, opIndex: number) => (
                        <Box key={opIndex} sx={{ mb: 1 }}>
                          <Chip
                            label={op.type}
                            size="small"
                            color={op.type === 'publish' ? 'primary' : 'success'}
                            sx={{ mr: 1 }}
                          />
                          {op.summary && (
                            <Typography variant="caption">{op.summary}</Typography>
                          )}
                        </Box>
                      ))}
                    </Box>
                  )}
                </AccordionDetails>
              </Accordion>
            ))}
          </Paper>
        )}

        {/* Messages */}
        {parsedData.messages && parsedData.messages.length > 0 && (
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Messages ({parsedData.messages.length})
            </Typography>
            {parsedData.messages.map((message: any, index: number) => (
              <Accordion key={index}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>{message.name}</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {message.summary && (
                    <Typography variant="body2" paragraph>
                      {message.summary}
                    </Typography>
                  )}
                  {message.payload && (
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Payload:
                      </Typography>
                      <Paper sx={{ p: 1, bgcolor: '#f5f5f5' }}>
                        <pre style={{ margin: 0, fontSize: '0.875rem' }}>
                          {JSON.stringify(message.payload, null, 2)}
                        </pre>
                      </Paper>
                    </Box>
                  )}
                </AccordionDetails>
              </Accordion>
            ))}
          </Paper>
        )}
      </Box>
    );
  };

  const renderAvroInfo = () => {
    if (!parsedData) return null;

    return (
      <Box>
        {/* Schema Info */}
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="h6">{parsedData.name}</Typography>
          <Typography variant="body2" color="text.secondary">
            Type: {parsedData.type}
          </Typography>
          {parsedData.namespace && (
            <Typography variant="body2" color="text.secondary">
              Namespace: {parsedData.namespace}
            </Typography>
          )}
          {parsedData.doc && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              {parsedData.doc}
            </Typography>
          )}
        </Paper>

        {/* Fields (for record type) */}
        {parsedData.fields && parsedData.fields.length > 0 && (
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Fields ({parsedData.fields.length})
            </Typography>
            <List dense>
              {parsedData.fields.map((field: any, index: number) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" fontWeight="medium">
                          {field.name}
                        </Typography>
                        <Chip label={field.type} size="small" />
                      </Box>
                    }
                    secondary={field.doc}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        )}

        {/* Symbols (for enum type) */}
        {parsedData.symbols && parsedData.symbols.length > 0 && (
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Symbols ({parsedData.symbols.length})
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {parsedData.symbols.map((symbol: string, index: number) => (
                <Chip key={index} label={symbol} size="small" />
              ))}
            </Box>
          </Paper>
        )}

        {/* Items (for array type) */}
        {parsedData.items && (
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Array Items
            </Typography>
            <Chip label={parsedData.items} />
          </Paper>
        )}

        {/* Values (for map type) */}
        {parsedData.values && (
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Map Values
            </Typography>
            <Chip label={parsedData.values} />
          </Paper>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" gutterBottom>
          Async Schema Viewer
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Parse AsyncAPI and Avro schemas
        </Typography>
      </Box>

      {/* Schema Type Selector */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
          <Tab
            label="AsyncAPI"
            onClick={() => setSchemaType('asyncapi')}
          />
          <Tab
            label="Avro"
            onClick={() => setSchemaType('avro')}
          />
        </Tabs>
      </Box>

      {/* Input Section */}
      <Paper sx={{ m: 2, p: 2 }}>
        <TextField
          fullWidth
          multiline
          rows={10}
          label={`${schemaType === 'asyncapi' ? 'AsyncAPI' : 'Avro'} Schema (JSON/YAML)`}
          value={schemaInput}
          onChange={(e) => setSchemaInput(e.target.value)}
          placeholder={
            schemaType === 'asyncapi'
              ? 'Paste AsyncAPI 2.x or 3.x specification...'
              : 'Paste Avro schema JSON...'
          }
          sx={{ mb: 2, fontFamily: 'monospace' }}
        />
        <Button
          variant="contained"
          onClick={handleParse}
          disabled={!schemaInput.trim()}
          startIcon={<CodeIcon />}
        >
          Parse Schema
        </Button>
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mx: 2, mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Parsed Data */}
      <Box sx={{ flex: 1, overflow: 'auto', px: 2, pb: 2 }}>
        {!parsedData ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <DescriptionIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No Schema Loaded
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Paste a {schemaType === 'asyncapi' ? 'AsyncAPI' : 'Avro'} schema above and click Parse
            </Typography>
          </Box>
        ) : (
          <>
            {schemaType === 'asyncapi' ? renderAsyncAPIInfo() : renderAvroInfo()}
          </>
        )}
      </Box>
    </Box>
  );
};

export default AsyncSchemaViewer;
