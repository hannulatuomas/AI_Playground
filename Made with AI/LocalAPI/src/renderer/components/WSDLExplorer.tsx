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
  Link as LinkIcon,
} from '@mui/icons-material';

interface WSDLExplorerProps {
  onOperationSelect?: (operation: Operation, service: string, port: string) => void;
}

interface Service {
  name: string;
  ports: Port[];
}

interface Port {
  name: string;
  binding: string;
  address: string;
  operations: Operation[];
}

interface Operation {
  name: string;
  input?: Message;
  output?: Message;
  documentation?: string;
}

interface Message {
  name: string;
  parts: Part[];
}

interface Part {
  name: string;
  element?: string;
  type?: string;
}

const WSDLExplorer: React.FC<WSDLExplorerProps> = ({ onOperationSelect }) => {
  const [wsdlUrl, setWsdlUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wsdlInfo, setWsdlInfo] = useState<any>(null);
  const [services, setServices] = useState<Service[]>([]);

  const handleLoadWSDL = async () => {
    if (!wsdlUrl.trim()) {
      setError('Please enter a WSDL URL');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Call WSDL parser via IPC
      const result = await (window as any).electron.invoke('soap:parseWSDL', {
        wsdlUrl: wsdlUrl.trim(),
      });

      if (result.error) {
        setError(result.error);
      } else {
        setWsdlInfo(result);
        setServices(result.services || []);
      }
    } catch (err: any) {
      setError(`Failed to load WSDL: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleOperationClick = (operation: Operation, serviceName: string, portName: string) => {
    if (onOperationSelect) {
      onOperationSelect(operation, serviceName, portName);
    }
  };

  const renderOperations = (operations: Operation[], serviceName: string, portName: string) => {
    if (operations.length === 0) {
      return (
        <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
          No operations found
        </Typography>
      );
    }

    return (
      <List dense>
        {operations.map((operation, index) => (
          <ListItem key={index} disablePadding>
            <ListItemButton onClick={() => handleOperationClick(operation, serviceName, portName)}>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" fontWeight="medium">
                      {operation.name}
                    </Typography>
                    <Chip label="SOAP" size="small" color="info" />
                  </Box>
                }
                secondary={
                  <>
                    {operation.documentation && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        {operation.documentation}
                      </Typography>
                    )}
                    {operation.input && (
                      <Typography variant="caption" color="text.secondary">
                        Input: {operation.input.parts.map(p => p.name).join(', ')}
                      </Typography>
                    )}
                  </>
                }
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    );
  };

  const renderPorts = (ports: Port[], serviceName: string) => {
    return ports.map((port, portIndex) => (
      <Accordion key={portIndex}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
            <Typography variant="subtitle2">{port.name}</Typography>
            <Typography variant="caption" color="text.secondary">
              {port.operations.length} operations
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails sx={{ p: 0 }}>
          {port.address && (
            <Box sx={{ px: 2, py: 1, bgcolor: 'action.hover' }}>
              <Typography variant="caption" color="text.secondary">
                Endpoint: {port.address}
              </Typography>
            </Box>
          )}
          {renderOperations(port.operations, serviceName, port.name)}
        </AccordionDetails>
      </Accordion>
    ));
  };

  const renderServices = () => {
    if (services.length === 0) {
      return (
        <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
          No services found
        </Typography>
      );
    }

    return services.map((service, serviceIndex) => (
      <Box key={serviceIndex} sx={{ mb: 2 }}>
        <Typography variant="h6" sx={{ px: 2, py: 1, bgcolor: 'primary.main', color: 'primary.contrastText' }}>
          {service.name}
        </Typography>
        <Box sx={{ mt: 1 }}>
          {renderPorts(service.ports, service.name)}
        </Box>
      </Box>
    ));
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" gutterBottom>
          WSDL Explorer
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Load and explore SOAP web services
        </Typography>
      </Box>

      {/* WSDL URL Input */}
      <Paper sx={{ m: 2, p: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
          <TextField
            fullWidth
            label="WSDL URL"
            placeholder="https://example.com/service?wsdl"
            value={wsdlUrl}
            onChange={(e) => setWsdlUrl(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleLoadWSDL()}
            size="small"
            InputProps={{
              startAdornment: <LinkIcon sx={{ mr: 1, color: 'action.active' }} />,
            }}
          />
          <Button
            variant="contained"
            onClick={handleLoadWSDL}
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
      {!wsdlInfo ? (
        <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4 }}>
          <Box sx={{ textAlign: 'center', maxWidth: 400 }}>
            <DescriptionIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No WSDL Loaded
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Enter a WSDL URL above to explore the SOAP web service
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Example: https://www.dataaccess.com/webservicesserver/NumberConversion.wso?WSDL
            </Typography>
          </Box>
        </Box>
      ) : (
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {wsdlInfo.targetNamespace && (
            <Paper sx={{ p: 2, mb: 2, bgcolor: 'action.hover' }}>
              <Typography variant="caption" color="text.secondary">
                Target Namespace:
              </Typography>
              <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                {wsdlInfo.targetNamespace}
              </Typography>
            </Paper>
          )}
          {renderServices()}
        </Box>
      )}

      {/* Footer */}
      {wsdlInfo && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Typography variant="caption" color="text.secondary">
            {services.length} service(s) loaded
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default WSDLExplorer;
