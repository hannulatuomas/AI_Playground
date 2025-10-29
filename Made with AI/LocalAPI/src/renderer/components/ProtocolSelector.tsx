import React from 'react';
import {
  Box,
  Card,
  CardContent,
  CardActionArea,
  Typography,
  Grid,
  Chip,
  alpha,
} from '@mui/material';
import {
  Api as ApiIcon,
  GraphicEq as GraphQLIcon,
  Soap as SoapIcon,
  Code as GrpcIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';

interface Protocol {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  features: string[];
  supported: boolean;
}

interface ProtocolSelectorProps {
  onSelect: (protocolId: string) => void;
  selectedProtocol?: string;
}

const protocols: Protocol[] = [
  {
    id: 'rest',
    name: 'REST / OpenAPI',
    description: 'RESTful APIs with OpenAPI/Swagger specifications',
    icon: <ApiIcon sx={{ fontSize: 48 }} />,
    color: '#4CAF50',
    features: ['OpenAPI 3.x', 'Swagger 2.0', 'Auto-import', 'Schema validation'],
    supported: true,
  },
  {
    id: 'graphql',
    name: 'GraphQL',
    description: 'GraphQL APIs with schema introspection',
    icon: <GraphQLIcon sx={{ fontSize: 48 }} />,
    color: '#E10098',
    features: ['Introspection', 'Queries', 'Mutations', 'Subscriptions'],
    supported: true,
  },
  {
    id: 'soap',
    name: 'SOAP',
    description: 'SOAP web services with WSDL',
    icon: <SoapIcon sx={{ fontSize: 48 }} />,
    color: '#2196F3',
    features: ['WSDL parsing', 'Type extraction', 'Operations', 'Bindings'],
    supported: true,
  },
  {
    id: 'grpc',
    name: 'gRPC',
    description: 'gRPC services with Protocol Buffers',
    icon: <GrpcIcon sx={{ fontSize: 48 }} />,
    color: '#00D9FF',
    features: ['Proto files', 'Streaming', 'Services', 'Messages'],
    supported: true,
  },
];

const ProtocolSelector: React.FC<ProtocolSelectorProps> = ({ onSelect, selectedProtocol }) => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Select Protocol
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Choose the API protocol you want to work with
      </Typography>

      <Grid container spacing={3}>
        {protocols.map((protocol) => (
          <Grid item xs={12} sm={6} md={3} key={protocol.id}>
            <Card
              sx={{
                height: '100%',
                border: 2,
                borderColor: selectedProtocol === protocol.id ? protocol.color : 'transparent',
                transition: 'all 0.3s',
                '&:hover': {
                  borderColor: protocol.color,
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
            >
              <CardActionArea
                onClick={() => onSelect(protocol.id)}
                sx={{ height: '100%', p: 2 }}
                disabled={!protocol.supported}
              >
                <CardContent>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 2,
                      color: protocol.color,
                    }}
                  >
                    {protocol.icon}
                  </Box>

                  <Typography variant="h6" align="center" gutterBottom>
                    {protocol.name}
                  </Typography>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                    align="center"
                    sx={{ mb: 2, minHeight: 40 }}
                  >
                    {protocol.description}
                  </Typography>

                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, justifyContent: 'center' }}>
                    {protocol.features.map((feature, index) => (
                      <Chip
                        key={index}
                        label={feature}
                        size="small"
                        sx={{
                          bgcolor: alpha(protocol.color, 0.1),
                          color: protocol.color,
                          fontWeight: 500,
                        }}
                      />
                    ))}
                  </Box>

                  {selectedProtocol === protocol.id && (
                    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                      <CheckIcon sx={{ color: protocol.color }} />
                    </Box>
                  )}

                  {!protocol.supported && (
                    <Box sx={{ mt: 2 }}>
                      <Chip label="Coming Soon" size="small" color="default" />
                    </Box>
                  )}
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default ProtocolSelector;
