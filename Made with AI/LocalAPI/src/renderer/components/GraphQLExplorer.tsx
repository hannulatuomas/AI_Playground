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
  ListItemButton,
  Chip,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayArrowIcon,
  Refresh as RefreshIcon,
  Code as CodeIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material';

interface GraphQLExplorerProps {
  endpoint: string;
  onQueryExecute?: (query: string, variables?: any) => void;
}

interface SchemaType {
  name: string;
  kind: string;
  description?: string;
  fields?: Field[];
}

interface Field {
  name: string;
  type: string;
  description?: string;
  args?: Argument[];
}

interface Argument {
  name: string;
  type: string;
  defaultValue?: any;
  description?: string;
}

interface Operation {
  name: string;
  type: string;
  description?: string;
  args?: Argument[];
}

const GraphQLExplorer: React.FC<GraphQLExplorerProps> = ({ endpoint, onQueryExecute }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [schema, setSchema] = useState<any>(null);
  const [queries, setQueries] = useState<Operation[]>([]);
  const [mutations, setMutations] = useState<Operation[]>([]);
  const [types, setTypes] = useState<SchemaType[]>([]);
  const [selectedQuery, setSelectedQuery] = useState<string>('');

  const handleIntrospect = async () => {
    setLoading(true);
    setError(null);

    try {
      // Call GraphQL introspection via IPC
      const result = await (window as any).electron.invoke('graphql:introspect', {
        endpoint,
      });

      if (result.error) {
        setError(result.error);
      } else {
        setSchema(result.schema);
        setQueries(result.queries || []);
        setMutations(result.mutations || []);
        setTypes(result.types || []);
      }
    } catch (err: any) {
      setError(`Introspection failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleQuerySelect = (operation: Operation, type: 'query' | 'mutation') => {
    // Generate query template
    const args = operation.args || [];
    const argDefinitions = args.map(arg => `$${arg.name}: ${arg.type}`).join(', ');
    const argValues = args.map(arg => `${arg.name}: $${arg.name}`).join(', ');

    let template = `${type} ${operation.name}`;
    
    if (argDefinitions) {
      template += `(${argDefinitions})`;
    }

    template += ` {\n  ${operation.name}`;

    if (argValues) {
      template += `(${argValues})`;
    }

    template += ` {\n    # Add fields here\n    # Example: id, name\n  }\n}`;

    setSelectedQuery(template);
    if (onQueryExecute) {
      onQueryExecute(template);
    }
  };

  const renderOperationList = (operations: Operation[], type: 'query' | 'mutation') => {
    if (operations.length === 0) {
      return (
        <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
          No {type === 'query' ? 'queries' : 'mutations'} found
        </Typography>
      );
    }

    return (
      <List>
        {operations.map((operation, index) => (
          <ListItem key={index} disablePadding>
            <ListItemButton onClick={() => handleQuerySelect(operation, type)}>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body1">{operation.name}</Typography>
                    <Chip
                      label={operation.type}
                      size="small"
                      color={type === 'query' ? 'primary' : 'secondary'}
                    />
                  </Box>
                }
                secondary={
                  <>
                    {operation.description && (
                      <Typography variant="body2" color="text.secondary">
                        {operation.description}
                      </Typography>
                    )}
                    {operation.args && operation.args.length > 0 && (
                      <Typography variant="caption" color="text.secondary">
                        Args: {operation.args.map(arg => `${arg.name}: ${arg.type}`).join(', ')}
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

  const renderTypesList = () => {
    const userTypes = types.filter(t => !t.name.startsWith('__') && t.kind === 'OBJECT');

    if (userTypes.length === 0) {
      return (
        <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
          No types found
        </Typography>
      );
    }

    return (
      <Box>
        {userTypes.map((type, index) => (
          <Accordion key={index}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography>{type.name}</Typography>
                <Chip label={type.kind} size="small" />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {type.description && (
                <Typography variant="body2" color="text.secondary" paragraph>
                  {type.description}
                </Typography>
              )}
              {type.fields && type.fields.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Fields:
                  </Typography>
                  <List dense>
                    {type.fields.map((field, fieldIndex) => (
                      <ListItem key={fieldIndex}>
                        <ListItemText
                          primary={`${field.name}: ${field.type}`}
                          secondary={field.description}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography variant="h6" sx={{ flex: 1 }}>
          GraphQL Explorer
        </Typography>
        <Tooltip title="Introspect Schema">
          <IconButton onClick={handleIntrospect} disabled={loading} color="primary">
            {loading ? <CircularProgress size={24} /> : <RefreshIcon />}
          </IconButton>
        </Tooltip>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ m: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Content */}
      {!schema ? (
        <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4 }}>
          <Box sx={{ textAlign: 'center', maxWidth: 400 }}>
            <DescriptionIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No Schema Loaded
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Click the refresh button to introspect the GraphQL schema
            </Typography>
            <Button
              variant="contained"
              startIcon={<RefreshIcon />}
              onClick={handleIntrospect}
              disabled={loading}
            >
              Introspect Schema
            </Button>
          </Box>
        </Box>
      ) : (
        <Box sx={{ flex: 1, overflow: 'hidden' }}>
          <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
            <Tab label={`Queries (${queries.length})`} />
            <Tab label={`Mutations (${mutations.length})`} />
            <Tab label={`Types (${types.filter(t => !t.name.startsWith('__')).length})`} />
          </Tabs>

          <Box sx={{ height: 'calc(100% - 48px)', overflow: 'auto' }}>
            {activeTab === 0 && renderOperationList(queries, 'query')}
            {activeTab === 1 && renderOperationList(mutations, 'mutation')}
            {activeTab === 2 && renderTypesList()}
          </Box>
        </Box>
      )}

      {/* Quick Info */}
      {schema && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Typography variant="caption" color="text.secondary">
            Schema loaded: {queries.length} queries, {mutations.length} mutations, {types.length} types
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default GraphQLExplorer;
