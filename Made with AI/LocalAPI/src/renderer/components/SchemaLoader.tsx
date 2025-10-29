import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Paper,
  Typography,
  Divider,
} from '@mui/material';
import {
  Api as ApiIcon,
  GraphicEq as GraphQLIcon,
  Soap as SoapIcon,
  Code as GrpcIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material';
import SwaggerViewer from './SwaggerViewer';
import GraphQLExplorer from './GraphQLExplorer';
import WSDLExplorer from './WSDLExplorer';
import ProtoExplorer from './ProtoExplorer';

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
      id={`schema-tabpanel-${index}`}
      aria-labelledby={`schema-tab-${index}`}
      style={{ height: '100%' }}
      {...other}
    >
      {value === index && <Box sx={{ height: '100%' }}>{children}</Box>}
    </div>
  );
}

interface SchemaLoaderProps {
  onImport?: (data: any, protocol: string) => void;
}

const SchemaLoader: React.FC<SchemaLoaderProps> = ({ onImport }) => {
  const [selectedTab, setSelectedTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const handleOpenAPIImport = (spec: any) => {
    if (onImport) {
      onImport(spec, 'openapi');
    }
  };

  const handleGraphQLQuery = (query: string, variables?: any) => {
    if (onImport) {
      onImport({ query, variables }, 'graphql');
    }
  };

  const handleSOAPOperation = (operation: any, service: string, port: string) => {
    if (onImport) {
      onImport({ operation, service, port }, 'soap');
    }
  };

  const handleGRPCMethod = (method: any, service: string, packageName: string) => {
    if (onImport) {
      onImport({ method, service, packageName }, 'grpc');
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Paper sx={{ borderRadius: 0 }}>
        <Box sx={{ p: 2 }}>
          <Typography variant="h5" gutterBottom>
            Schema Loader
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Import and explore API schemas from multiple protocols
          </Typography>
        </Box>
        <Divider />
        
        {/* Protocol Tabs */}
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab
            icon={<ApiIcon />}
            label="OpenAPI / Swagger"
            id="schema-tab-0"
            aria-controls="schema-tabpanel-0"
          />
          <Tab
            icon={<GraphQLIcon />}
            label="GraphQL"
            id="schema-tab-1"
            aria-controls="schema-tabpanel-1"
          />
          <Tab
            icon={<SoapIcon />}
            label="SOAP / WSDL"
            id="schema-tab-2"
            aria-controls="schema-tabpanel-2"
          />
          <Tab
            icon={<GrpcIcon />}
            label="gRPC / Proto"
            id="schema-tab-3"
            aria-controls="schema-tabpanel-3"
          />
        </Tabs>
      </Paper>

      {/* Tab Panels */}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        <TabPanel value={selectedTab} index={0}>
          <SwaggerViewer onImport={handleOpenAPIImport} />
        </TabPanel>

        <TabPanel value={selectedTab} index={1}>
          <GraphQLExplorer
            endpoint=""
            onQueryExecute={handleGraphQLQuery}
          />
        </TabPanel>

        <TabPanel value={selectedTab} index={2}>
          <WSDLExplorer onOperationSelect={handleSOAPOperation} />
        </TabPanel>

        <TabPanel value={selectedTab} index={3}>
          <ProtoExplorer onMethodSelect={handleGRPCMethod} />
        </TabPanel>
      </Box>

      {/* Footer Info */}
      <Paper sx={{ p: 1.5, borderRadius: 0, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary">
          {selectedTab === 0 && 'Load OpenAPI 2.0 (Swagger) or OpenAPI 3.x specifications'}
          {selectedTab === 1 && 'Introspect GraphQL schemas and explore queries/mutations'}
          {selectedTab === 2 && 'Parse WSDL files and discover SOAP operations'}
          {selectedTab === 3 && 'Load proto files and explore gRPC services'}
        </Typography>
      </Paper>
    </Box>
  );
};

export default SchemaLoader;
