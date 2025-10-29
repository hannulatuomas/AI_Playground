import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Chip,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  Code as CodeIcon,
  Description as DescriptionIcon,
  Upload as UploadIcon,
} from '@mui/icons-material';

interface ProtoExplorerProps {
  onMethodSelect?: (method: Method, service: string, packageName: string) => void;
}

interface Package {
  name: string;
  services: string[];
}

interface Service {
  name: string;
  package: string;
  methods: Method[];
}

interface Method {
  name: string;
  requestType: string;
  responseType: string;
  requestStream: boolean;
  responseStream: boolean;
  options?: any;
}

interface Message {
  name: string;
  package: string;
  fields: Field[];
}

interface Field {
  name: string;
  type: string;
  rule?: string;
  id: number;
}

const ProtoExplorer: React.FC<ProtoExplorerProps> = ({ onMethodSelect }) => {
  const [protoPath, setProtoPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [protoInfo, setProtoInfo] = useState<any>(null);
  const [packages, setPackages] = useState<Package[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);

  const handleLoadProto = async () => {
    if (!protoPath.trim()) {
      setError('Please enter a proto file path');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Call proto parser via IPC
      const result = await (window as any).electron.invoke('grpc:parseProto', {
        protoPath: protoPath.trim(),
      });

      if (result.error) {
        setError(result.error);
      } else {
        setProtoInfo(result);
        setPackages(result.packages || []);
        setServices(result.services || []);
        setMessages(result.messages || []);
      }
    } catch (err: any) {
      setError(`Failed to load proto file: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = async () => {
    try {
      const result = await (window as any).electron.invoke('dialog:openFile', {
        filters: [{ name: 'Proto Files', extensions: ['proto'] }],
      });

      if (result && !result.canceled && result.filePaths.length > 0) {
        setProtoPath(result.filePaths[0]);
      }
    } catch (err: any) {
      setError(`Failed to select file: ${err.message}`);
    }
  };

  const handleMethodClick = (method: Method, serviceName: string, packageName: string) => {
    if (onMethodSelect) {
      onMethodSelect(method, serviceName, packageName);
    }
  };

  const getStreamingType = (method: Method): string => {
    if (method.requestStream && method.responseStream) {
      return 'Bidirectional';
    }
    if (method.requestStream) {
      return 'Client Stream';
    }
    if (method.responseStream) {
      return 'Server Stream';
    }
    return 'Unary';
  };

  const getStreamingColor = (method: Method): 'default' | 'primary' | 'secondary' | 'success' => {
    if (method.requestStream && method.responseStream) {
      return 'secondary';
    }
    if (method.requestStream || method.responseStream) {
      return 'primary';
    }
    return 'success';
  };

  const renderMethods = (methods: Method[], serviceName: string, packageName: string) => {
    if (methods.length === 0) {
      return (
        <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
          No methods found
        </Typography>
      );
    }

    return (
      <List dense>
        {methods.map((method, index) => (
          <ListItem key={index} disablePadding>
            <ListItemButton onClick={() => handleMethodClick(method, serviceName, packageName)}>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                    <Typography variant="body2" fontWeight="medium">
                      {method.name}
                    </Typography>
                    <Chip
                      label={getStreamingType(method)}
                      size="small"
                      color={getStreamingColor(method)}
                    />
                  </Box>
                }
                secondary={
                  <Typography variant="caption" color="text.secondary">
                    Request: {method.requestType} → Response: {method.responseType}
                  </Typography>
                }
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    );
  };

  const renderServices = () => {
    if (services.length === 0) {
      return (
        <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
          No services found
        </Typography>
      );
    }

    // Group services by package
    const servicesByPackage = services.reduce((acc, service) => {
      const pkg = service.package || 'default';
      if (!acc[pkg]) {
        acc[pkg] = [];
      }
      acc[pkg].push(service);
      return acc;
    }, {} as Record<string, Service[]>);

    return Object.entries(servicesByPackage).map(([packageName, pkgServices]) => (
      <Box key={packageName} sx={{ mb: 2 }}>
        <Typography
          variant="subtitle2"
          sx={{ px: 2, py: 1, bgcolor: 'primary.main', color: 'primary.contrastText' }}
        >
          Package: {packageName}
        </Typography>
        <Box sx={{ mt: 1 }}>
          {pkgServices.map((service, serviceIndex) => (
            <Accordion key={serviceIndex}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                  <Typography variant="subtitle2">{service.name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {service.methods.length} method(s)
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails sx={{ p: 0 }}>
                {renderMethods(service.methods, service.name, packageName)}
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      </Box>
    ));
  };

  const renderMessages = () => {
    if (messages.length === 0) {
      return null;
    }

    return (
      <Box sx={{ mt: 2 }}>
        <Typography variant="h6" sx={{ px: 2, py: 1 }}>
          Messages ({messages.length})
        </Typography>
        {messages.map((message, index) => (
          <Accordion key={index}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle2">{message.name}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <List dense>
                {message.fields.map((field, fieldIndex) => (
                  <ListItem key={fieldIndex}>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2">
                            {field.name}: {field.type}
                          </Typography>
                          {field.rule && (
                            <Chip label={field.rule} size="small" variant="outlined" />
                          )}
                        </Box>
                      }
                      secondary={`Field ID: ${field.id}`}
                    />
                  </ListItem>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" gutterBottom>
          Proto Explorer
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Load and explore gRPC proto files
        </Typography>
      </Box>

      {/* Proto File Input */}
      <Paper sx={{ m: 2, p: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
          <TextField
            fullWidth
            label="Proto File Path"
            placeholder="/path/to/service.proto"
            value={protoPath}
            onChange={(e) => setProtoPath(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleLoadProto()}
            size="small"
          />
          <Button
            variant="outlined"
            onClick={handleFileSelect}
            startIcon={<UploadIcon />}
            sx={{ minWidth: 100 }}
          >
            Browse
          </Button>
          <Button
            variant="contained"
            onClick={handleLoadProto}
            disabled={loading}
            sx={{ minWidth: 100 }}
            startIcon={loading ? <CircularProgress size={20} /> : <RefreshIcon />}
          >
            {loading ? 'Loading...' : 'Load'}
          </Button>
        </Box>
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mx: 2, mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Content */}
      {!protoInfo ? (
        <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4 }}>
          <Box sx={{ textAlign: 'center', maxWidth: 400 }}>
            <DescriptionIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No Proto File Loaded
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Enter a proto file path or browse to select a .proto file
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Example: ./protos/service.proto
            </Typography>
          </Box>
        </Box>
      ) : (
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {renderServices()}
          {renderMessages()}
        </Box>
      )}

      {/* Footer */}
      {protoInfo && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Typography variant="caption" color="text.secondary">
            {packages.length} package(s), {services.length} service(s), {messages.length} message(s)
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ProtoExplorer;
