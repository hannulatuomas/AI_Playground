"""
Database Schema Generator

Generates database schemas for various database types.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class FieldType(Enum):
    """Database field types."""
    INTEGER = "INTEGER"
    STRING = "STRING"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"
    FLOAT = "FLOAT"
    DATE = "DATE"
    DATETIME = "DATETIME"
    JSON = "JSON"
    BINARY = "BINARY"


class RelationType(Enum):
    """Database relationship types."""
    ONE_TO_ONE = "ONE_TO_ONE"
    ONE_TO_MANY = "ONE_TO_MANY"
    MANY_TO_MANY = "MANY_TO_MANY"


@dataclass
class Field:
    """Database field definition."""
    name: str
    field_type: FieldType
    nullable: bool = True
    unique: bool = False
    primary_key: bool = False
    foreign_key: Optional[str] = None
    default: Optional[str] = None
    max_length: Optional[int] = None


@dataclass
class Index:
    """Database index definition."""
    name: str
    fields: List[str]
    unique: bool = False


@dataclass
class Relationship:
    """Database relationship definition."""
    name: str
    target_table: str
    relation_type: RelationType
    foreign_key: str


@dataclass
class Table:
    """Database table definition."""
    name: str
    fields: List[Field]
    indexes: List[Index] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)


@dataclass
class DatabaseSchema:
    """Complete database schema."""
    name: str
    tables: List[Table]
    db_type: str  # 'sqlite', 'postgresql', 'mysql', 'mongodb', 'neo4j'


class SchemaGenerator:
    """Generates database schemas."""
    
    def __init__(self, ai_backend, project_rules: Optional[List[str]] = None):
        """
        Initialize schema generator.
        
        Args:
            ai_backend: AI backend for generation
            project_rules: Project-specific rules
        """
        self.ai_backend = ai_backend
        self.project_rules = project_rules or []
    
    def generate_schema(self, models: List[Dict], 
                       db_type: str = 'sqlite') -> DatabaseSchema:
        """
        Generate database schema from models.
        
        Args:
            models: List of model definitions
            db_type: Database type
            
        Returns:
            DatabaseSchema object
        """
        tables = []
        
        for model in models:
            table = self._model_to_table(model, db_type)
            tables.append(table)
        
        return DatabaseSchema(
            name="generated_schema",
            tables=tables,
            db_type=db_type
        )
    
    def generate_sql(self, schema: DatabaseSchema) -> str:
        """
        Generate SQL DDL statements.
        
        Args:
            schema: Database schema
            
        Returns:
            SQL DDL string
        """
        if schema.db_type in ['sqlite', 'postgresql', 'mysql']:
            return self._generate_sql_ddl(schema)
        elif schema.db_type == 'mongodb':
            return self._generate_mongodb_schema(schema)
        elif schema.db_type == 'neo4j':
            return self._generate_neo4j_schema(schema)
        else:
            raise ValueError(f"Unsupported database type: {schema.db_type}")
    
    def _model_to_table(self, model: Dict, db_type: str) -> Table:
        """Convert model definition to table."""
        fields = []
        
        # Add ID field if not present
        has_id = any(f.get('name') == 'id' for f in model.get('fields', []))
        if not has_id:
            fields.append(Field(
                name='id',
                field_type=FieldType.INTEGER,
                nullable=False,
                primary_key=True
            ))
        
        # Convert model fields
        for field_def in model.get('fields', []):
            field = Field(
                name=field_def['name'],
                field_type=self._string_to_field_type(field_def.get('type', 'STRING')),
                nullable=field_def.get('nullable', True),
                unique=field_def.get('unique', False),
                primary_key=field_def.get('primary_key', False),
                max_length=field_def.get('max_length')
            )
            fields.append(field)
        
        # Add timestamps
        if model.get('timestamps', True):
            fields.extend([
                Field(name='created_at', field_type=FieldType.DATETIME, nullable=False),
                Field(name='updated_at', field_type=FieldType.DATETIME, nullable=False)
            ])
        
        return Table(
            name=model['name'],
            fields=fields
        )
    
    def _string_to_field_type(self, type_str: str) -> FieldType:
        """Convert string to FieldType."""
        type_map = {
            'int': FieldType.INTEGER,
            'integer': FieldType.INTEGER,
            'str': FieldType.STRING,
            'string': FieldType.STRING,
            'text': FieldType.TEXT,
            'bool': FieldType.BOOLEAN,
            'boolean': FieldType.BOOLEAN,
            'float': FieldType.FLOAT,
            'date': FieldType.DATE,
            'datetime': FieldType.DATETIME,
            'json': FieldType.JSON,
            'binary': FieldType.BINARY
        }
        return type_map.get(type_str.lower(), FieldType.STRING)
    
    def _generate_sql_ddl(self, schema: DatabaseSchema) -> str:
        """Generate SQL DDL statements."""
        sql = f"-- Database Schema: {schema.name}\n"
        sql += f"-- Database Type: {schema.db_type}\n\n"
        
        for table in schema.tables:
            sql += self._generate_create_table(table, schema.db_type)
            sql += "\n\n"
            
            # Generate indexes
            for index in table.indexes:
                sql += self._generate_create_index(table.name, index, schema.db_type)
                sql += "\n"
        
        return sql
    
    def _generate_create_table(self, table: Table, db_type: str) -> str:
        """Generate CREATE TABLE statement."""
        sql = f"CREATE TABLE {table.name} (\n"
        
        field_defs = []
        for field in table.fields:
            field_def = f"    {field.name} {self._field_type_to_sql(field.field_type, db_type, field.max_length)}"
            
            if field.primary_key:
                field_def += " PRIMARY KEY"
                if db_type in ['sqlite', 'mysql'] and field.field_type == FieldType.INTEGER:
                    field_def += " AUTOINCREMENT" if db_type == 'sqlite' else " AUTO_INCREMENT"
            
            if not field.nullable:
                field_def += " NOT NULL"
            
            if field.unique:
                field_def += " UNIQUE"
            
            if field.default:
                field_def += f" DEFAULT {field.default}"
            
            if field.foreign_key:
                field_def += f" REFERENCES {field.foreign_key}"
            
            field_defs.append(field_def)
        
        sql += ",\n".join(field_defs)
        sql += "\n);"
        
        return sql
    
    def _field_type_to_sql(self, field_type: FieldType, db_type: str, 
                          max_length: Optional[int] = None) -> str:
        """Convert FieldType to SQL type."""
        if db_type == 'postgresql':
            type_map = {
                FieldType.INTEGER: 'INTEGER',
                FieldType.STRING: f'VARCHAR({max_length or 255})',
                FieldType.TEXT: 'TEXT',
                FieldType.BOOLEAN: 'BOOLEAN',
                FieldType.FLOAT: 'REAL',
                FieldType.DATE: 'DATE',
                FieldType.DATETIME: 'TIMESTAMP',
                FieldType.JSON: 'JSONB',
                FieldType.BINARY: 'BYTEA'
            }
        elif db_type == 'mysql':
            type_map = {
                FieldType.INTEGER: 'INT',
                FieldType.STRING: f'VARCHAR({max_length or 255})',
                FieldType.TEXT: 'TEXT',
                FieldType.BOOLEAN: 'BOOLEAN',
                FieldType.FLOAT: 'FLOAT',
                FieldType.DATE: 'DATE',
                FieldType.DATETIME: 'DATETIME',
                FieldType.JSON: 'JSON',
                FieldType.BINARY: 'BLOB'
            }
        else:  # sqlite
            type_map = {
                FieldType.INTEGER: 'INTEGER',
                FieldType.STRING: 'TEXT',
                FieldType.TEXT: 'TEXT',
                FieldType.BOOLEAN: 'INTEGER',
                FieldType.FLOAT: 'REAL',
                FieldType.DATE: 'TEXT',
                FieldType.DATETIME: 'TEXT',
                FieldType.JSON: 'TEXT',
                FieldType.BINARY: 'BLOB'
            }
        
        return type_map.get(field_type, 'TEXT')
    
    def _generate_create_index(self, table_name: str, index: Index, 
                              db_type: str) -> str:
        """Generate CREATE INDEX statement."""
        unique = "UNIQUE " if index.unique else ""
        fields = ", ".join(index.fields)
        return f"CREATE {unique}INDEX {index.name} ON {table_name} ({fields});"
    
    def _generate_mongodb_schema(self, schema: DatabaseSchema) -> str:
        """Generate MongoDB schema (as JSON schema validation)."""
        import json
        
        schemas = {}
        
        for table in schema.tables:
            collection_schema = {
                "bsonType": "object",
                "required": [f.name for f in table.fields if not f.nullable],
                "properties": {}
            }
            
            for field in table.fields:
                field_schema = {
                    "bsonType": self._field_type_to_bson(field.field_type)
                }
                
                if field.field_type == FieldType.STRING and field.max_length:
                    field_schema["maxLength"] = field.max_length
                
                collection_schema["properties"][field.name] = field_schema
            
            schemas[table.name] = collection_schema
        
        return json.dumps(schemas, indent=2)
    
    def _field_type_to_bson(self, field_type: FieldType) -> str:
        """Convert FieldType to BSON type."""
        type_map = {
            FieldType.INTEGER: "int",
            FieldType.STRING: "string",
            FieldType.TEXT: "string",
            FieldType.BOOLEAN: "bool",
            FieldType.FLOAT: "double",
            FieldType.DATE: "date",
            FieldType.DATETIME: "date",
            FieldType.JSON: "object",
            FieldType.BINARY: "binData"
        }
        return type_map.get(field_type, "string")
    
    def _generate_neo4j_schema(self, schema: DatabaseSchema) -> str:
        """Generate Neo4j Cypher statements."""
        cypher = "// Neo4j Schema\n\n"
        
        for table in schema.tables:
            cypher += f"// Create {table.name} nodes\n"
            cypher += f"CREATE CONSTRAINT {table.name}_id IF NOT EXISTS\n"
            cypher += f"FOR (n:{table.name}) REQUIRE n.id IS UNIQUE;\n\n"
            
            # Sample node creation
            fields = [f.name for f in table.fields if not f.primary_key][:5]
            props = ", ".join([f"{f}: ${f}" for f in fields])
            cypher += f"// Example: CREATE (n:{table.name} {{{props}}});\n\n"
        
        return cypher
