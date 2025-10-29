"""
GraphQL API Generator

Generates GraphQL schema and resolvers.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class GraphQLType:
    """GraphQL type definition."""
    name: str
    fields: Dict[str, str]  # field_name: type
    is_input: bool = False


@dataclass
class GraphQLQuery:
    """GraphQL query definition."""
    name: str
    return_type: str
    arguments: Dict[str, str] = field(default_factory=dict)


@dataclass
class GraphQLMutation:
    """GraphQL mutation definition."""
    name: str
    return_type: str
    arguments: Dict[str, str] = field(default_factory=dict)


@dataclass
class GraphQLSchema:
    """GraphQL schema specification."""
    types: List[GraphQLType]
    queries: List[GraphQLQuery]
    mutations: List[GraphQLMutation]
    framework: str = 'apollo'  # 'apollo', 'graphene'


class GraphQLGenerator:
    """Generates GraphQL schemas and resolvers."""
    
    def __init__(self, ai_backend, project_rules: Optional[List[str]] = None):
        """
        Initialize GraphQL generator.
        
        Args:
            ai_backend: AI backend for generation
            project_rules: Project-specific rules
        """
        self.ai_backend = ai_backend
        self.project_rules = project_rules or []
    
    def generate_graphql_schema(self, schema: GraphQLSchema) -> Dict[str, str]:
        """
        Generate GraphQL schema and resolvers.
        
        Args:
            schema: GraphQL schema specification
            
        Returns:
            Dictionary of filename: content
        """
        if schema.framework == 'apollo':
            return self._generate_apollo_server(schema)
        elif schema.framework == 'graphene':
            return self._generate_graphene(schema)
        else:
            raise ValueError(f"Unsupported framework: {schema.framework}")
    
    def _generate_apollo_server(self, schema: GraphQLSchema) -> Dict[str, str]:
        """Generate Apollo Server GraphQL API."""
        files = {}
        
        # Generate schema
        schema_code = self._generate_graphql_schema_string(schema)
        files['schema.graphql'] = schema_code
        
        # Generate resolvers
        resolvers_code = self._generate_apollo_resolvers(schema)
        files['resolvers.js'] = resolvers_code
        
        # Generate server
        server_code = self._generate_apollo_server_code()
        files['server.js'] = server_code
        
        # Package.json
        files['package.json'] = '''{
  "name": "graphql-api",
  "version": "1.0.0",
  "description": "GraphQL API with Apollo Server",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "apollo-server": "^3.0.0",
    "graphql": "^16.0.0"
  },
  "devDependencies": {
    "nodemon": "^2.0.0"
  }
}
'''
        
        return files
    
    def _generate_graphql_schema_string(self, schema: GraphQLSchema) -> str:
        """Generate GraphQL schema string."""
        schema_str = ""
        
        # Generate types
        for gql_type in schema.types:
            type_keyword = "input" if gql_type.is_input else "type"
            schema_str += f"{type_keyword} {gql_type.name} {{\n"
            
            for field_name, field_type in gql_type.fields.items():
                schema_str += f"  {field_name}: {field_type}\n"
            
            schema_str += "}\n\n"
        
        # Generate Query type
        if schema.queries:
            schema_str += "type Query {\n"
            for query in schema.queries:
                args = ""
                if query.arguments:
                    args_list = [f"{k}: {v}" for k, v in query.arguments.items()]
                    args = f"({', '.join(args_list)})"
                schema_str += f"  {query.name}{args}: {query.return_type}\n"
            schema_str += "}\n\n"
        
        # Generate Mutation type
        if schema.mutations:
            schema_str += "type Mutation {\n"
            for mutation in schema.mutations:
                args = ""
                if mutation.arguments:
                    args_list = [f"{k}: {v}" for k, v in mutation.arguments.items()]
                    args = f"({', '.join(args_list)})"
                schema_str += f"  {mutation.name}{args}: {mutation.return_type}\n"
            schema_str += "}\n\n"
        
        return schema_str
    
    def _generate_apollo_resolvers(self, schema: GraphQLSchema) -> str:
        """Generate Apollo Server resolvers."""
        code = '''/**
 * GraphQL Resolvers
 */

const resolvers = {
  Query: {
'''
        
        # Generate query resolvers
        for query in schema.queries:
            args = ', '.join(['_', 'args'] if query.arguments else ['_'])
            code += f'''    {query.name}: ({args}) => {{
      // TODO: Implement {query.name} resolver
      return null;
    }},
'''
        
        code += '''  },
  Mutation: {
'''
        
        # Generate mutation resolvers
        for mutation in schema.mutations:
            args = ', '.join(['_', 'args'] if mutation.arguments else ['_'])
            code += f'''    {mutation.name}: ({args}) => {{
      // TODO: Implement {mutation.name} resolver
      return null;
    }},
'''
        
        code += '''  },
};

module.exports = resolvers;
'''
        
        return code
    
    def _generate_apollo_server_code(self) -> str:
        """Generate Apollo Server main file."""
        return '''/**
 * Apollo Server Setup
 */

const { ApolloServer } = require('apollo-server');
const fs = require('fs');
const path = require('path');
const resolvers = require('./resolvers');

// Read schema
const typeDefs = fs.readFileSync(
  path.join(__dirname, 'schema.graphql'),
  'utf-8'
);

// Create server
const server = new ApolloServer({
  typeDefs,
  resolvers,
  csrfPrevention: true,
  cache: 'bounded',
});

// Start server
server.listen().then(({ url }) => {
  console.log(`🚀 Server ready at ${url}`);
});
'''
    
    def _generate_graphene(self, schema: GraphQLSchema) -> Dict[str, str]:
        """Generate Graphene (Python) GraphQL API."""
        files = {}
        
        # Generate schema
        schema_code = '''"""
GraphQL Schema using Graphene
"""

import graphene


'''
        
        # Generate types
        for gql_type in schema.types:
            if not gql_type.is_input:
                schema_code += f"class {gql_type.name}(graphene.ObjectType):\n"
                for field_name, field_type in gql_type.fields.items():
                    py_type = self._graphql_to_python_type(field_type)
                    schema_code += f"    {field_name} = {py_type}\n"
                schema_code += "\n\n"
        
        # Generate Query
        if schema.queries:
            schema_code += "class Query(graphene.ObjectType):\n"
            for query in schema.queries:
                py_type = self._graphql_to_python_type(query.return_type)
                schema_code += f"    {query.name} = {py_type}\n"
                schema_code += f"\n    def resolve_{query.name}(self, info):\n"
                schema_code += f"        # TODO: Implement {query.name}\n"
                schema_code += f"        return None\n\n"
            schema_code += "\n"
        
        # Generate Mutation
        if schema.mutations:
            schema_code += "class Mutation(graphene.ObjectType):\n"
            for mutation in schema.mutations:
                schema_code += f"    # TODO: Implement {mutation.name}\n"
                schema_code += f"    pass\n\n"
        
        # Generate schema
        schema_code += "\nschema = graphene.Schema(query=Query"
        if schema.mutations:
            schema_code += ", mutation=Mutation"
        schema_code += ")\n"
        
        files['schema.py'] = schema_code
        
        # Generate main app
        files['app.py'] = '''"""
GraphQL API with Flask and Graphene
"""

from flask import Flask
from flask_graphql import GraphQLView
from schema import schema

app = Flask(__name__)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)

if __name__ == '__main__':
    app.run(debug=True)
'''
        
        return files
    
    def _graphql_to_python_type(self, graphql_type: str) -> str:
        """Convert GraphQL type to Python/Graphene type."""
        type_map = {
            'String': 'graphene.String()',
            'Int': 'graphene.Int()',
            'Float': 'graphene.Float()',
            'Boolean': 'graphene.Boolean()',
            'ID': 'graphene.ID()',
        }
        
        # Handle lists
        if graphql_type.startswith('[') and graphql_type.endswith(']'):
            inner_type = graphql_type[1:-1]
            return f"graphene.List({self._graphql_to_python_type(inner_type)})"
        
        # Handle non-null
        if graphql_type.endswith('!'):
            base_type = graphql_type[:-1]
            return f"graphene.NonNull({self._graphql_to_python_type(base_type)})"
        
        return type_map.get(graphql_type, f'graphene.Field({graphql_type})')
