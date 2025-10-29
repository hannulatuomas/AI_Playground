"""
Query Optimizer

Analyzes and optimizes database queries.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import re


@dataclass
class OptimizedQuery:
    """Optimized query result."""
    original_query: str
    optimized_query: str
    improvements: List[str]
    estimated_speedup: Optional[float] = None


@dataclass
class QueryAnalysis:
    """Query analysis result."""
    query: str
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    complexity: str = "medium"  # low, medium, high


class QueryOptimizer:
    """Optimizes database queries."""
    
    def __init__(self, ai_backend, db_type: str = 'sqlite'):
        """
        Initialize query optimizer.
        
        Args:
            ai_backend: AI backend for optimization
            db_type: Database type
        """
        self.ai_backend = ai_backend
        self.db_type = db_type
    
    def optimize_query(self, query: str) -> OptimizedQuery:
        """
        Optimize a database query.
        
        Args:
            query: SQL query to optimize
            
        Returns:
            OptimizedQuery with improvements
        """
        # Analyze query first
        analysis = self.analyze_query(query)
        
        # Apply rule-based optimizations
        optimized = self._apply_optimizations(query, analysis)
        
        improvements = []
        
        # Check what changed
        if optimized != query:
            if 'SELECT *' in query and 'SELECT *' not in optimized:
                improvements.append("Replaced SELECT * with specific columns")
            
            if 'WHERE' not in query and 'WHERE' in optimized:
                improvements.append("Added WHERE clause for filtering")
            
            if query.count('JOIN') > optimized.count('JOIN'):
                improvements.append("Reduced number of JOINs")
        
        # Add suggestions as improvements
        improvements.extend(analysis.suggestions[:3])
        
        return OptimizedQuery(
            original_query=query,
            optimized_query=optimized,
            improvements=improvements
        )
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        Analyze query for issues.
        
        Args:
            query: SQL query
            
        Returns:
            QueryAnalysis with findings
        """
        analysis = QueryAnalysis(query=query)
        
        query_upper = query.upper()
        
        # Check for SELECT *
        if 'SELECT *' in query_upper:
            analysis.issues.append("Using SELECT * is inefficient")
            analysis.suggestions.append("Specify only needed columns")
        
        # Check for missing WHERE clause
        if 'SELECT' in query_upper and 'WHERE' not in query_upper:
            analysis.issues.append("No WHERE clause - may return too many rows")
            analysis.suggestions.append("Add WHERE clause to filter results")
        
        # Check for missing indexes (heuristic)
        if 'WHERE' in query_upper:
            where_clause = query_upper.split('WHERE')[1].split('ORDER')[0] if 'ORDER' in query_upper else query_upper.split('WHERE')[1]
            if '=' in where_clause or 'LIKE' in where_clause:
                analysis.suggestions.append("Consider adding index on WHERE clause columns")
        
        # Check for N+1 queries pattern
        if query.count('SELECT') > 1:
            analysis.issues.append("Multiple SELECT statements - possible N+1 query")
            analysis.suggestions.append("Consider using JOINs instead of multiple queries")
        
        # Check for LIKE with leading wildcard
        if re.search(r"LIKE\s+['\"]%", query, re.IGNORECASE):
            analysis.issues.append("LIKE with leading wildcard prevents index usage")
            analysis.suggestions.append("Avoid leading wildcards in LIKE patterns")
        
        # Estimate complexity
        join_count = query_upper.count('JOIN')
        subquery_count = query_upper.count('SELECT') - 1
        
        if join_count > 3 or subquery_count > 2:
            analysis.complexity = "high"
        elif join_count > 1 or subquery_count > 0:
            analysis.complexity = "medium"
        else:
            analysis.complexity = "low"
        
        return analysis
    
    def suggest_indexes(self, query: str, table_name: str) -> List[str]:
        """
        Suggest indexes for query optimization.
        
        Args:
            query: SQL query
            table_name: Table name
            
        Returns:
            List of CREATE INDEX statements
        """
        indexes = []
        query_upper = query.upper()
        
        # Extract WHERE clause columns
        if 'WHERE' in query_upper:
            where_match = re.search(r'WHERE\s+(.+?)(?:ORDER|GROUP|LIMIT|$)', query, re.IGNORECASE)
            if where_match:
                where_clause = where_match.group(1)
                
                # Find column names (simple pattern)
                columns = re.findall(r'(\w+)\s*[=<>]', where_clause)
                
                for col in set(columns):
                    index_name = f"idx_{table_name}_{col}"
                    indexes.append(f"CREATE INDEX {index_name} ON {table_name} ({col});")
        
        # Extract ORDER BY columns
        if 'ORDER BY' in query_upper:
            order_match = re.search(r'ORDER BY\s+(.+?)(?:LIMIT|$)', query, re.IGNORECASE)
            if order_match:
                order_clause = order_match.group(1)
                columns = re.findall(r'(\w+)', order_clause)
                
                for col in set(columns):
                    index_name = f"idx_{table_name}_{col}_order"
                    indexes.append(f"CREATE INDEX {index_name} ON {table_name} ({col});")
        
        return indexes
    
    def _apply_optimizations(self, query: str, 
                            analysis: QueryAnalysis) -> str:
        """Apply rule-based optimizations."""
        optimized = query
        
        # Note: These are simple optimizations
        # Real optimization would require query parsing
        
        # Remove unnecessary DISTINCT if no duplicates possible
        if 'DISTINCT' in optimized.upper() and 'JOIN' not in optimized.upper():
            # Only remove if it's a simple query
            pass  # Keep for safety
        
        # Add LIMIT if missing and no aggregation
        if 'LIMIT' not in optimized.upper() and 'COUNT' not in optimized.upper():
            if 'GROUP BY' not in optimized.upper():
                # Could add LIMIT, but might change semantics
                pass
        
        return optimized
    
    def explain_query(self, query: str, db_connection=None) -> str:
        """
        Get query execution plan.
        
        Args:
            query: SQL query
            db_connection: Database connection
            
        Returns:
            Execution plan as string
        """
        if not db_connection:
            return "No database connection provided"
        
        try:
            cursor = db_connection.cursor()
            
            # Get execution plan
            if self.db_type == 'sqlite':
                cursor.execute(f"EXPLAIN QUERY PLAN {query}")
            elif self.db_type == 'postgresql':
                cursor.execute(f"EXPLAIN ANALYZE {query}")
            elif self.db_type == 'mysql':
                cursor.execute(f"EXPLAIN {query}")
            else:
                return f"EXPLAIN not supported for {self.db_type}"
            
            plan = cursor.fetchall()
            
            # Format plan
            result = "Query Execution Plan:\n"
            for row in plan:
                result += f"{row}\n"
            
            return result
            
        except Exception as e:
            return f"Error getting execution plan: {e}"
