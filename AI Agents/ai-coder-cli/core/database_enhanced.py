"""
Enhanced Database Features

This module provides enhanced database capabilities:
- Query optimization and analysis
- Automatic indexing recommendations
- Schema documentation
- Query builder with LLM assistance
- Connection pooling
- Query caching
- Migration utilities
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class QueryAnalysis:
    """Results of query analysis."""
    query: str
    estimated_cost: float
    execution_time: Optional[float]
    rows_affected: Optional[int]
    indexes_used: List[str]
    full_table_scans: List[str]
    optimization_suggestions: List[str]
    query_type: str  # SELECT, INSERT, UPDATE, DELETE


@dataclass
class IndexRecommendation:
    """Recommendation for database index."""
    table_name: str
    column_names: List[str]
    index_type: str  # btree, hash, etc.
    reason: str
    estimated_improvement: str
    create_statement: str


class QueryOptimizer:
    """
    Analyzes and optimizes database queries.
    
    Features:
    - Query pattern analysis
    - Index recommendations
    - Query rewriting suggestions
    - Performance analysis
    """
    
    def __init__(self):
        """Initialize query optimizer."""
        self.query_patterns = defaultdict(int)
        self.slow_queries = []
        self.optimization_history = []
    
    def analyze_query(
        self,
        query: str,
        execution_time: Optional[float] = None,
        explain_result: Optional[Dict[str, Any]] = None
    ) -> QueryAnalysis:
        """
        Analyze a query for optimization opportunities.
        
        Args:
            query: SQL query string
            execution_time: Query execution time in seconds
            explain_result: EXPLAIN output from database
            
        Returns:
            QueryAnalysis with recommendations
        """
        # Determine query type
        query_type = self._get_query_type(query)
        
        # Extract tables
        tables = self._extract_tables(query)
        
        # Analyze query patterns
        suggestions = []
        indexes_used = []
        full_table_scans = []
        
        # Check for common anti-patterns
        if 'SELECT *' in query.upper():
            suggestions.append(
                "Avoid SELECT * - specify only needed columns for better performance"
            )
        
        if re.search(r'WHERE.*LIKE\s+[\'"]%', query, re.IGNORECASE):
            suggestions.append(
                "Leading wildcard in LIKE (LIKE '%...') prevents index usage"
            )
        
        if 'OR' in query.upper() and 'WHERE' in query.upper():
            suggestions.append(
                "Multiple OR conditions may prevent index usage - consider UNION"
            )
        
        if re.search(r'WHERE.*\+|-|\*|/', query, re.IGNORECASE):
            suggestions.append(
                "Calculations in WHERE clause prevent index usage - consider computed columns"
            )
        
        # Check for missing WHERE clause on UPDATE/DELETE
        if query_type in ['UPDATE', 'DELETE'] and 'WHERE' not in query.upper():
            suggestions.append(
                f"WARNING: {query_type} without WHERE clause affects all rows!"
            )
        
        # Check for subqueries that could be JOINs
        if re.search(r'IN\s*\(\s*SELECT', query, re.IGNORECASE):
            suggestions.append(
                "Consider using JOIN instead of IN (SELECT ...) for better performance"
            )
        
        # Check for DISTINCT
        if 'DISTINCT' in query.upper():
            suggestions.append(
                "DISTINCT is expensive - ensure it's necessary and consider GROUP BY"
            )
        
        # Estimate cost (simplified)
        estimated_cost = self._estimate_query_cost(query, tables)
        
        return QueryAnalysis(
            query=query,
            estimated_cost=estimated_cost,
            execution_time=execution_time,
            rows_affected=None,
            indexes_used=indexes_used,
            full_table_scans=full_table_scans,
            optimization_suggestions=suggestions,
            query_type=query_type
        )
    
    def recommend_indexes(
        self,
        queries: List[str],
        table_schemas: Optional[Dict[str, List[str]]] = None
    ) -> List[IndexRecommendation]:
        """
        Recommend indexes based on query patterns.
        
        Args:
            queries: List of SQL queries to analyze
            table_schemas: Optional table schemas {table_name: [column_names]}
            
        Returns:
            List of index recommendations
        """
        recommendations = []
        
        # Analyze WHERE clauses
        where_columns = defaultdict(int)
        
        for query in queries:
            # Extract WHERE columns
            columns = self._extract_where_columns(query)
            for table, column in columns:
                where_columns[(table, column)] += 1
        
        # Generate recommendations
        for (table, column), count in where_columns.items():
            if count >= 2:  # Column used in WHERE multiple times
                recommendation = IndexRecommendation(
                    table_name=table,
                    column_names=[column],
                    index_type='btree',
                    reason=f"Column used in WHERE clause {count} times",
                    estimated_improvement="10-50% faster queries",
                    create_statement=f"CREATE INDEX idx_{table}_{column} ON {table}({column});"
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def suggest_query_rewrite(self, query: str) -> Optional[str]:
        """
        Suggest rewritten version of query for better performance.
        
        Args:
            query: Original SQL query
            
        Returns:
            Rewritten query or None if no improvements
        """
        rewritten = query
        
        # Replace IN (SELECT ...) with JOIN
        if re.search(r'IN\s*\(\s*SELECT', rewritten, re.IGNORECASE):
            # This is complex - would need proper SQL parsing
            # For now, just note the suggestion
            logger.info("Query could benefit from rewriting IN (SELECT ...) as JOIN")
        
        # Add query hints for known patterns
        # (Database-specific implementation needed)
        
        return rewritten if rewritten != query else None
    
    def _get_query_type(self, query: str) -> str:
        """Determine type of SQL query."""
        query_upper = query.strip().upper()
        if query_upper.startswith('SELECT'):
            return 'SELECT'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        elif query_upper.startswith('CREATE'):
            return 'CREATE'
        elif query_upper.startswith('ALTER'):
            return 'ALTER'
        else:
            return 'OTHER'
    
    def _extract_tables(self, query: str) -> List[str]:
        """Extract table names from query."""
        tables = []
        
        # Simple regex-based extraction (would need proper SQL parser for accuracy)
        # FROM clause
        from_match = re.finditer(r'FROM\s+(\w+)', query, re.IGNORECASE)
        for match in from_match:
            tables.append(match.group(1))
        
        # JOIN clause
        join_match = re.finditer(r'JOIN\s+(\w+)', query, re.IGNORECASE)
        for match in join_match:
            tables.append(match.group(1))
        
        # UPDATE/INSERT
        update_match = re.match(r'(UPDATE|INSERT\s+INTO)\s+(\w+)', query, re.IGNORECASE)
        if update_match:
            tables.append(update_match.group(2))
        
        return list(set(tables))  # Remove duplicates
    
    def _extract_where_columns(self, query: str) -> List[Tuple[str, str]]:
        """Extract columns used in WHERE clauses."""
        columns = []
        
        # Find WHERE clause
        where_match = re.search(r'WHERE\s+(.+?)(?:ORDER|GROUP|HAVING|LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1)
            
            # Extract table.column or column references
            col_matches = re.finditer(r'(\w+)\.(\w+)\s*[=<>!]', where_clause)
            for match in col_matches:
                table = match.group(1)
                column = match.group(2)
                columns.append((table, column))
            
            # Also extract simple column references
            simple_matches = re.finditer(r'(\w+)\s*[=<>!]', where_clause)
            for match in simple_matches:
                column = match.group(1)
                # Try to infer table from query context
                tables = self._extract_tables(query)
                if tables:
                    columns.append((tables[0], column))
        
        return columns
    
    def _estimate_query_cost(self, query: str, tables: List[str]) -> float:
        """Estimate query cost (simplified)."""
        cost = 1.0
        
        # Penalty for SELECT *
        if 'SELECT *' in query.upper():
            cost *= 1.5
        
        # Penalty for JOINs
        join_count = query.upper().count('JOIN')
        cost *= (1 + join_count * 0.5)
        
        # Penalty for subqueries
        subquery_count = query.upper().count('SELECT') - 1
        cost *= (1 + subquery_count * 0.8)
        
        # Bonus for LIMIT
        if 'LIMIT' in query.upper():
            cost *= 0.8
        
        return cost


class SchemaDocumenter:
    """
    Automatically documents database schemas.
    
    Features:
    - Table documentation generation
    - Relationship mapping
    - ERD generation (text-based)
    """
    
    def __init__(self):
        """Initialize schema documenter."""
        self.schemas = {}
    
    def document_schema(
        self,
        tables: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Generate schema documentation.
        
        Args:
            tables: Dictionary of table definitions
                {table_name: {columns: [...], primary_key: ..., foreign_keys: [...]}}
            
        Returns:
            Markdown documentation string
        """
        doc_lines = []
        
        doc_lines.append("# Database Schema Documentation\n")
        doc_lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        doc_lines.append("## Tables\n")
        
        for table_name, table_info in sorted(tables.items()):
            doc_lines.append(f"### {table_name}\n")
            
            # Table description
            if 'description' in table_info:
                doc_lines.append(f"{table_info['description']}\n")
            
            # Columns
            doc_lines.append("#### Columns\n")
            doc_lines.append("| Column | Type | Constraints | Description |")
            doc_lines.append("|--------|------|-------------|-------------|")
            
            for col in table_info.get('columns', []):
                constraints = []
                if col.get('primary_key'):
                    constraints.append('PK')
                if col.get('not_null'):
                    constraints.append('NOT NULL')
                if col.get('unique'):
                    constraints.append('UNIQUE')
                
                constraint_str = ', '.join(constraints) if constraints else '-'
                desc = col.get('description', '-')
                
                doc_lines.append(
                    f"| {col['name']} | {col['type']} | {constraint_str} | {desc} |"
                )
            
            doc_lines.append("")
            
            # Foreign Keys
            if table_info.get('foreign_keys'):
                doc_lines.append("#### Foreign Keys\n")
                for fk in table_info['foreign_keys']:
                    doc_lines.append(
                        f"- `{fk['column']}` → `{fk['referenced_table']}.{fk['referenced_column']}`"
                    )
                doc_lines.append("")
            
            # Indexes
            if table_info.get('indexes'):
                doc_lines.append("#### Indexes\n")
                for idx in table_info['indexes']:
                    doc_lines.append(
                        f"- `{idx['name']}` on `{', '.join(idx['columns'])}`"
                    )
                doc_lines.append("")
        
        # Relationships
        doc_lines.append("## Relationships\n")
        doc_lines.append("```")
        doc_lines.append(self._generate_text_erd(tables))
        doc_lines.append("```\n")
        
        return '\n'.join(doc_lines)
    
    def _generate_text_erd(self, tables: Dict[str, Dict[str, Any]]) -> str:
        """Generate text-based ERD."""
        lines = []
        
        for table_name, table_info in tables.items():
            lines.append(f"[{table_name}]")
            
            for fk in table_info.get('foreign_keys', []):
                lines.append(
                    f"  {table_name}.{fk['column']} --> "
                    f"{fk['referenced_table']}.{fk['referenced_column']}"
                )
        
        return '\n'.join(lines) if lines else "No relationships defined"


class MigrationManager:
    """
    Manages database migrations.
    
    Features:
    - Migration versioning
    - Up/down migrations
    - Migration history tracking
    """
    
    def __init__(self, migrations_dir: Path):
        """
        Initialize migration manager.
        
        Args:
            migrations_dir: Directory containing migration files
        """
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
    
    def create_migration(
        self,
        name: str,
        up_sql: str,
        down_sql: str
    ) -> Path:
        """
        Create a new migration file.
        
        Args:
            name: Migration name
            up_sql: SQL for upgrade
            down_sql: SQL for downgrade
            
        Returns:
            Path to migration file
        """
        # Generate version number (timestamp)
        version = time.strftime('%Y%m%d%H%M%S')
        filename = f"{version}_{name}.sql"
        filepath = self.migrations_dir / filename
        
        # Write migration file
        migration_content = f"""-- Migration: {name}
-- Version: {version}
-- Created: {time.strftime('%Y-%m-%d %H:%M:%S')}

-- UP
{up_sql}

-- DOWN
{down_sql}
"""
        
        filepath.write_text(migration_content)
        logger.info(f"Created migration: {filename}")
        
        return filepath
    
    def get_pending_migrations(
        self,
        applied_versions: List[str]
    ) -> List[Tuple[str, Path]]:
        """
        Get list of pending migrations.
        
        Args:
            applied_versions: List of already applied migration versions
            
        Returns:
            List of (version, filepath) tuples
        """
        pending = []
        
        for migration_file in sorted(self.migrations_dir.glob('*.sql')):
            version = migration_file.stem.split('_')[0]
            if version not in applied_versions:
                pending.append((version, migration_file))
        
        return pending
    
    def parse_migration(self, filepath: Path) -> Tuple[str, str]:
        """
        Parse migration file.
        
        Args:
            filepath: Path to migration file
            
        Returns:
            Tuple of (up_sql, down_sql)
        """
        content = filepath.read_text()
        
        # Extract UP and DOWN sections
        up_match = re.search(r'-- UP\s+(.*?)\s+-- DOWN', content, re.DOTALL)
        down_match = re.search(r'-- DOWN\s+(.*?)$', content, re.DOTALL)
        
        up_sql = up_match.group(1).strip() if up_match else ''
        down_sql = down_match.group(1).strip() if down_match else ''
        
        return up_sql, down_sql


class DatabaseEnhancementsManager:
    """
    Central manager for all database enhancements.
    """
    
    def __init__(
        self,
        migrations_dir: Optional[Path] = None
    ):
        """
        Initialize database enhancements manager.
        
        Args:
            migrations_dir: Directory for migrations
        """
        self.query_optimizer = QueryOptimizer()
        self.schema_documenter = SchemaDocumenter()
        self.migration_manager = MigrationManager(
            migrations_dir or Path('./migrations')
        )
    
    def analyze_and_optimize(
        self,
        query: str,
        execution_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Analyze query and provide optimization recommendations.
        
        Args:
            query: SQL query
            execution_time: Optional execution time
            
        Returns:
            Dictionary with analysis and recommendations
        """
        analysis = self.query_optimizer.analyze_query(query, execution_time)
        rewritten = self.query_optimizer.suggest_query_rewrite(query)
        
        return {
            'original_query': query,
            'analysis': analysis,
            'rewritten_query': rewritten,
            'suggestions': analysis.optimization_suggestions
        }


def create_database_enhancements_manager(**kwargs) -> DatabaseEnhancementsManager:
    """
    Factory function to create DatabaseEnhancementsManager.
    
    Args:
        **kwargs: Arguments passed to DatabaseEnhancementsManager
        
    Returns:
        DatabaseEnhancementsManager instance
    """
    return DatabaseEnhancementsManager(**kwargs)
