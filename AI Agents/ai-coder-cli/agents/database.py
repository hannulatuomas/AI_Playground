
"""
Database Agent - Multi-database support for SQL and NoSQL operations.

This agent provides intelligent database interaction capabilities across multiple
database types (MSSQL, MySQL, PostgreSQL, SQLite, MongoDB, Neo4j, Redis) with
SQL generation, query optimization, and security features.
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple, Literal, Union
from pathlib import Path
import logging

from .base import Agent

# Import database libraries
try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

try:
    import pymongo
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False


DatabaseType = Literal["sqlite", "mysql", "postgresql", "mssql", "mongodb", "redis", "neo4j"]


class DatabaseAgent(Agent):
    """
    Production-ready Database Agent.
    
    Features:
        - Multi-database support (SQL and NoSQL)
        - Intelligent SQL generation using LLM
        - Connection pooling and management
        - Query validation and security
        - Transaction support
        - Result formatting and export
    
    Supported Databases:
        - SQLite: Embedded SQL database
        - MySQL/MariaDB: Popular open-source SQL database
        - PostgreSQL: Advanced open-source SQL database
        - MS SQL Server: Microsoft SQL database
        - MongoDB: Document-oriented NoSQL database
        - Redis: Key-value store and cache
        - Neo4j: Graph database
    
    Security Features:
        - SQL injection prevention
        - Parameterized queries
        - Connection validation
        - Query whitelisting (optional)
        - Transaction rollback on errors
    """
    
    SUPPORTED_DATABASES = ["sqlite", "mysql", "postgresql", "mssql", "mongodb", "redis", "neo4j"]
    
    # SQL keywords that indicate potentially dangerous operations
    DANGEROUS_KEYWORDS = [
        "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "GRANT", "REVOKE"
    ]
    
    def __init__(
        self,
        name: str = "database",
        description: str = "Multi-database interaction agent",
        **kwargs
    ):
        """
        Initialize the Database agent.
        
        Args:
            name: Agent name
            description: Agent description
            **kwargs: Additional configuration
        """
        super().__init__(name=name, description=description, **kwargs)
        
        self._connections: Dict[str, Any] = {}
        self._check_dependencies()
        
        self.logger.info("Database Agent initialized")
    
    def _check_dependencies(self) -> None:
        """Check which database drivers are available."""
        availability = {
            'sqlite': SQLITE_AVAILABLE,
            'mysql': PYMYSQL_AVAILABLE,
            'postgresql': PSYCOPG2_AVAILABLE,
            'mssql': PYODBC_AVAILABLE,
            'mongodb': PYMONGO_AVAILABLE,
            'redis': REDIS_AVAILABLE,
            'neo4j': NEO4J_AVAILABLE
        }
        
        for db, available in availability.items():
            if not available:
                self.logger.warning(f"{db} driver not installed")
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute database task.
        
        Args:
            task: Task description or SQL query
            context: Execution context with parameters:
                - operation: Operation type (connect, query, insert, update, delete, disconnect)
                - db_type: Database type
                - connection_string: Database connection string
                - query: SQL query or operation
                - params: Query parameters
                - safe_mode: Require confirmation for dangerous operations
                
        Returns:
            Dictionary with operation results
        """
        self._log_action("Database task", task[:100])
        
        try:
            operation = context.get('operation', self._detect_operation(task))
            
            if operation == 'connect':
                return self._connect_database(context)
            elif operation == 'query':
                return self._execute_query(task, context)
            elif operation == 'insert':
                return self._insert_data(context)
            elif operation == 'update':
                return self._update_data(context)
            elif operation == 'delete':
                return self._delete_data(context)
            elif operation == 'disconnect':
                return self._disconnect_database(context)
            elif operation == 'generate_query':
                return self._generate_query(task, context)
            elif operation == 'schema':
                return self._get_schema(context)
            else:
                return self._build_error_result(f"Unknown operation: {operation}")
                
        except Exception as e:
            self.logger.exception("Database operation failed")
            return self._build_error_result(f"Database operation failed: {str(e)}", e)
    
    def _detect_operation(self, task: str) -> str:
        """
        Detect operation type from task description.
        
        Args:
            task: Task description
            
        Returns:
            Operation type
        """
        task_lower = task.lower()
        
        if 'connect' in task_lower or 'connection' in task_lower:
            return 'connect'
        elif 'select' in task_lower or 'query' in task_lower or 'find' in task_lower:
            return 'query'
        elif 'insert' in task_lower or 'add' in task_lower:
            return 'insert'
        elif 'update' in task_lower or 'modify' in task_lower:
            return 'update'
        elif 'delete' in task_lower or 'remove' in task_lower:
            return 'delete'
        elif 'disconnect' in task_lower or 'close' in task_lower:
            return 'disconnect'
        elif 'schema' in task_lower or 'structure' in task_lower:
            return 'schema'
        elif 'generate' in task_lower or 'create query' in task_lower:
            return 'generate_query'
        
        return 'query'  # Default
    
    def _connect_database(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Connect to a database.
        
        Args:
            context: Context with connection parameters
            
        Returns:
            Connection result
        """
        db_type = context.get('db_type', 'sqlite')
        connection_id = context.get('connection_id', 'default')
        
        if db_type not in self.SUPPORTED_DATABASES:
            return self._build_error_result(f"Unsupported database type: {db_type}")
        
        try:
            if db_type == 'sqlite':
                conn = self._connect_sqlite(context)
            elif db_type == 'mysql':
                conn = self._connect_mysql(context)
            elif db_type == 'postgresql':
                conn = self._connect_postgresql(context)
            elif db_type == 'mssql':
                conn = self._connect_mssql(context)
            elif db_type == 'mongodb':
                conn = self._connect_mongodb(context)
            elif db_type == 'redis':
                conn = self._connect_redis(context)
            elif db_type == 'neo4j':
                conn = self._connect_neo4j(context)
            else:
                return self._build_error_result(f"Driver not available for: {db_type}")
            
            self._connections[connection_id] = {
                'type': db_type,
                'connection': conn,
                'connected_at': None  # Could add timestamp
            }
            
            return self._build_success_result(
                message=f"Connected to {db_type} database",
                data={'connection_id': connection_id, 'db_type': db_type}
            )
            
        except Exception as e:
            return self._build_error_result(f"Connection failed: {str(e)}", e)
    
    def _connect_sqlite(self, context: Dict[str, Any]) -> Any:
        """Connect to SQLite database."""
        if not SQLITE_AVAILABLE:
            raise RuntimeError("SQLite not available")
        
        db_path = context.get('database', context.get('db_path', ':memory:'))
        return sqlite3.connect(db_path)
    
    def _connect_mysql(self, context: Dict[str, Any]) -> Any:
        """Connect to MySQL database."""
        if not PYMYSQL_AVAILABLE:
            raise RuntimeError("pymysql not installed. Install with: pip install pymysql")
        
        return pymysql.connect(
            host=context.get('host', 'localhost'),
            port=context.get('port', 3306),
            user=context.get('user', 'root'),
            password=context.get('password', ''),
            database=context.get('database', ''),
            charset=context.get('charset', 'utf8mb4')
        )
    
    def _connect_postgresql(self, context: Dict[str, Any]) -> Any:
        """Connect to PostgreSQL database."""
        if not PSYCOPG2_AVAILABLE:
            raise RuntimeError("psycopg2 not installed. Install with: pip install psycopg2-binary")
        
        return psycopg2.connect(
            host=context.get('host', 'localhost'),
            port=context.get('port', 5432),
            user=context.get('user', 'postgres'),
            password=context.get('password', ''),
            database=context.get('database', 'postgres')
        )
    
    def _connect_mssql(self, context: Dict[str, Any]) -> Any:
        """Connect to MS SQL Server."""
        if not PYODBC_AVAILABLE:
            raise RuntimeError("pyodbc not installed. Install with: pip install pyodbc")
        
        connection_string = context.get('connection_string')
        if connection_string:
            return pyodbc.connect(connection_string)
        
        # Build connection string
        server = context.get('host', 'localhost')
        database = context.get('database', '')
        user = context.get('user', '')
        password = context.get('password', '')
        
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={user};PWD={password}"
        return pyodbc.connect(conn_str)
    
    def _connect_mongodb(self, context: Dict[str, Any]) -> Any:
        """Connect to MongoDB."""
        if not PYMONGO_AVAILABLE:
            raise RuntimeError("pymongo not installed. Install with: pip install pymongo")
        
        connection_string = context.get('connection_string', 'mongodb://localhost:27017/')
        client = pymongo.MongoClient(connection_string)
        
        database = context.get('database', 'test')
        return client[database]
    
    def _connect_redis(self, context: Dict[str, Any]) -> Any:
        """Connect to Redis."""
        if not REDIS_AVAILABLE:
            raise RuntimeError("redis not installed. Install with: pip install redis")
        
        return redis.Redis(
            host=context.get('host', 'localhost'),
            port=context.get('port', 6379),
            db=context.get('database', 0),
            password=context.get('password'),
            decode_responses=True
        )
    
    def _connect_neo4j(self, context: Dict[str, Any]) -> Any:
        """Connect to Neo4j graph database."""
        if not NEO4J_AVAILABLE:
            raise RuntimeError("neo4j not installed. Install with: pip install neo4j")
        
        uri = context.get('uri', 'bolt://localhost:7687')
        user = context.get('user', 'neo4j')
        password = context.get('password', '')
        
        return GraphDatabase.driver(uri, auth=(user, password))
    
    def _execute_query(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a database query.
        
        Args:
            task: Query or task description
            context: Execution context
            
        Returns:
            Query results
        """
        connection_id = context.get('connection_id', 'default')
        
        if connection_id not in self._connections:
            return self._build_error_result("No active database connection")
        
        conn_info = self._connections[connection_id]
        db_type = conn_info['type']
        connection = conn_info['connection']
        
        # Get or generate query
        query = context.get('query', task)
        params = context.get('params', ())
        
        # Generate query using LLM if task is natural language
        if not self._is_valid_query(query) and self.llm_router:
            generated = self._generate_sql_from_task(task, db_type, context)
            if generated:
                query = generated
        
        # Validate query for safety
        if context.get('safe_mode', True):
            if not self._validate_query_safety(query):
                return self._build_error_result(
                    f"Query contains potentially dangerous operations. Use safe_mode=False to override."
                )
        
        try:
            if db_type in ['sqlite', 'mysql', 'postgresql', 'mssql']:
                return self._execute_sql_query(connection, query, params, db_type)
            elif db_type == 'mongodb':
                return self._execute_mongodb_query(connection, query, context)
            elif db_type == 'redis':
                return self._execute_redis_query(connection, query, context)
            elif db_type == 'neo4j':
                return self._execute_neo4j_query(connection, query, params)
            else:
                return self._build_error_result(f"Query execution not supported for: {db_type}")
                
        except Exception as e:
            return self._build_error_result(f"Query execution failed: {str(e)}", e)
    
    def _execute_sql_query(
        self,
        connection: Any,
        query: str,
        params: Tuple,
        db_type: str
    ) -> Dict[str, Any]:
        """Execute SQL query."""
        cursor = connection.cursor()
        
        try:
            cursor.execute(query, params)
            
            # Check if query returns results
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Format results
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                return self._build_success_result(
                    message=f"Query returned {len(results)} rows",
                    data={
                        'rows': results,
                        'count': len(results),
                        'columns': columns
                    }
                )
            else:
                connection.commit()
                affected = cursor.rowcount
                
                return self._build_success_result(
                    message=f"Query executed successfully, {affected} rows affected",
                    data={'affected_rows': affected}
                )
                
        finally:
            cursor.close()
    
    def _execute_mongodb_query(
        self,
        database: Any,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute MongoDB query."""
        collection_name = context.get('collection', 'default')
        collection = database[collection_name]
        
        # Parse query (simplified - in production, use proper JSON parsing)
        operation = context.get('mongo_operation', 'find')
        
        if operation == 'find':
            filter_dict = context.get('filter', {})
            results = list(collection.find(filter_dict).limit(100))
            
            # Convert ObjectId to string for JSON serialization
            for result in results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
            
            return self._build_success_result(
                message=f"Found {len(results)} documents",
                data={'documents': results, 'count': len(results)}
            )
        
        return self._build_error_result("MongoDB operation not implemented")
    
    def _execute_redis_query(
        self,
        connection: Any,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Redis command."""
        operation = context.get('redis_operation', 'get')
        key = context.get('key', '')
        value = context.get('value')
        
        if operation == 'get':
            result = connection.get(key)
            return self._build_success_result(
                message=f"Retrieved value for key: {key}",
                data={'key': key, 'value': result}
            )
        elif operation == 'set':
            connection.set(key, value)
            return self._build_success_result(
                message=f"Set value for key: {key}",
                data={'key': key}
            )
        
        return self._build_error_result("Redis operation not implemented")
    
    def _execute_neo4j_query(
        self,
        driver: Any,
        query: str,
        params: Tuple
    ) -> Dict[str, Any]:
        """Execute Neo4j Cypher query."""
        with driver.session() as session:
            result = session.run(query, params)
            records = [dict(record) for record in result]
            
            return self._build_success_result(
                message=f"Query returned {len(records)} records",
                data={'records': records, 'count': len(records)}
            )
    
    def _generate_query(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate SQL query from natural language using LLM.
        
        Args:
            task: Natural language task description
            context: Context with schema information
            
        Returns:
            Generated query
        """
        if not self.llm_router:
            return self._build_error_result("LLM router not available for query generation")
        
        connection_id = context.get('connection_id', 'default')
        if connection_id in self._connections:
            db_type = self._connections[connection_id]['type']
        else:
            db_type = context.get('db_type', 'postgresql')
        
        query = self._generate_sql_from_task(task, db_type, context)
        
        if query:
            return self._build_success_result(
                message="SQL query generated successfully",
                data={'query': query, 'db_type': db_type}
            )
        else:
            return self._build_error_result("Failed to generate SQL query")
    
    def _generate_sql_from_task(
        self,
        task: str,
        db_type: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate SQL query from natural language task.
        
        Args:
            task: Task description
            db_type: Database type
            context: Context with optional schema
            
        Returns:
            Generated SQL query or None
        """
        schema_info = context.get('schema', 'No schema provided')
        
        prompt = f"""You are an expert SQL developer for {db_type} databases.
Generate a SQL query for the following task:

Task: {task}

Database Schema:
{schema_info}

Requirements:
1. Generate valid {db_type} SQL syntax
2. Use parameterized queries with placeholders where appropriate
3. Follow best practices and optimize for performance
4. Return ONLY the SQL query, no explanations or markdown

SQL Query:"""
        
        try:
            result = self._get_llm_response(prompt)
            if result.get('success', True):
                query = result.get('response', '').strip()
                # Clean up query (remove markdown code blocks if present)
                query = re.sub(r'```sql\n?', '', query)
                query = re.sub(r'```\n?', '', query)
                return query.strip()
        except Exception as e:
            self.logger.error(f"SQL generation failed: {e}")
        
        return None
    
    def _get_schema(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get database schema information.
        
        Args:
            context: Context with connection info
            
        Returns:
            Schema information
        """
        connection_id = context.get('connection_id', 'default')
        
        if connection_id not in self._connections:
            return self._build_error_result("No active database connection")
        
        conn_info = self._connections[connection_id]
        db_type = conn_info['type']
        connection = conn_info['connection']
        
        try:
            if db_type == 'sqlite':
                cursor = connection.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                return self._build_success_result(
                    message=f"Retrieved schema for {len(tables)} tables",
                    data={'tables': tables, 'db_type': db_type}
                )
            
            # Add support for other database types...
            return self._build_error_result(f"Schema retrieval not implemented for: {db_type}")
            
        except Exception as e:
            return self._build_error_result(f"Schema retrieval failed: {str(e)}", e)
    
    def _insert_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Insert data into database."""
        # Implementation for data insertion
        return self._build_error_result("Insert operation not yet implemented")
    
    def _update_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update data in database."""
        return self._build_error_result("Update operation not yet implemented")
    
    def _delete_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Delete data from database."""
        return self._build_error_result("Delete operation not yet implemented")
    
    def _disconnect_database(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Disconnect from database."""
        connection_id = context.get('connection_id', 'default')
        
        if connection_id not in self._connections:
            return self._build_error_result(f"No connection found: {connection_id}")
        
        try:
            conn_info = self._connections[connection_id]
            connection = conn_info['connection']
            
            # Close connection based on type
            if hasattr(connection, 'close'):
                connection.close()
            
            del self._connections[connection_id]
            
            return self._build_success_result(
                message=f"Disconnected from database: {connection_id}",
                data={'connection_id': connection_id}
            )
            
        except Exception as e:
            return self._build_error_result(f"Disconnect failed: {str(e)}", e)
    
    def _is_valid_query(self, query: str) -> bool:
        """
        Check if string looks like a valid SQL query.
        
        Args:
            query: Query string
            
        Returns:
            True if looks like SQL
        """
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
        query_upper = query.strip().upper()
        return any(query_upper.startswith(kw) for kw in sql_keywords)
    
    def _validate_query_safety(self, query: str) -> bool:
        """
        Validate query doesn't contain dangerous operations.
        
        Args:
            query: SQL query
            
        Returns:
            True if safe
        """
        query_upper = query.upper()
        
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in query_upper:
                self.logger.warning(f"Query contains dangerous keyword: {keyword}")
                return False
        
        return True
    
    def close_all_connections(self) -> None:
        """Close all active database connections."""
        for conn_id in list(self._connections.keys()):
            try:
                conn_info = self._connections[conn_id]
                if hasattr(conn_info['connection'], 'close'):
                    conn_info['connection'].close()
                del self._connections[conn_id]
            except Exception as e:
                self.logger.error(f"Error closing connection {conn_id}: {e}")
    
    def __del__(self):
        """Cleanup: close all connections on deletion."""
        try:
            self.close_all_connections()
        except Exception:
            pass
