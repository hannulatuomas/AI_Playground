"""
Database Debugger

Debugs database queries and connection issues.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re


@dataclass
class DebugResult:
    """Database debugging result."""
    issue: str
    solution: str
    explanation: str
    example: Optional[str] = None


class DatabaseDebugger:
    """Debugs database issues."""
    
    def __init__(self, ai_backend, db_type: str = 'sqlite'):
        """
        Initialize database debugger.
        
        Args:
            ai_backend: AI backend for debugging
            db_type: Database type
        """
        self.ai_backend = ai_backend
        self.db_type = db_type
    
    def debug_query(self, query: str, error: str) -> DebugResult:
        """
        Debug a query error.
        
        Args:
            query: SQL query that failed
            error: Error message
            
        Returns:
            DebugResult with solution
        """
        # Try rule-based debugging first
        result = self._rule_based_debug(query, error)
        
        if result:
            return result
        
        # Fall back to AI-based debugging
        return self._ai_debug(query, error)
    
    def debug_connection(self, connection_string: str, 
                        error: str) -> DebugResult:
        """
        Debug connection issues.
        
        Args:
            connection_string: Database connection string
            error: Error message
            
        Returns:
            DebugResult with solution
        """
        error_lower = error.lower()
        
        if 'access denied' in error_lower or 'authentication failed' in error_lower:
            return DebugResult(
                issue="Authentication failed",
                solution="Check username and password",
                explanation="The database rejected the credentials",
                example="Verify credentials in connection string"
            )
        
        if 'connection refused' in error_lower or 'cannot connect' in error_lower:
            return DebugResult(
                issue="Connection refused",
                solution="Check if database server is running and accessible",
                explanation="Cannot establish connection to database server",
                example="Verify host, port, and firewall settings"
            )
        
        if 'database does not exist' in error_lower or 'unknown database' in error_lower:
            return DebugResult(
                issue="Database not found",
                solution="Create the database or check database name",
                explanation="The specified database does not exist",
                example=f"CREATE DATABASE your_database_name;"
            )
        
        return DebugResult(
            issue="Connection error",
            solution="Check connection string format",
            explanation=error,
            example=None
        )
    
    def _rule_based_debug(self, query: str, error: str) -> Optional[DebugResult]:
        """Apply rule-based debugging."""
        error_lower = error.lower()
        query_upper = query.upper()
        
        # Syntax errors
        if 'syntax error' in error_lower:
            # Check for common syntax issues
            if query.count('(') != query.count(')'):
                return DebugResult(
                    issue="Unmatched parentheses",
                    solution="Balance parentheses in query",
                    explanation="Number of opening and closing parentheses don't match",
                    example="Check all ( and ) are properly paired"
                )
            
            if 'FROM' not in query_upper and 'SELECT' in query_upper:
                return DebugResult(
                    issue="Missing FROM clause",
                    solution="Add FROM clause with table name",
                    explanation="SELECT statement requires FROM clause",
                    example="SELECT * FROM table_name"
                )
        
        # Column not found
        if 'no such column' in error_lower or 'unknown column' in error_lower:
            # Extract column name from error
            col_match = re.search(r"column[:\s]+['\"]?(\w+)['\"]?", error_lower)
            if col_match:
                col_name = col_match.group(1)
                return DebugResult(
                    issue=f"Column '{col_name}' does not exist",
                    solution="Check column name spelling or add column to table",
                    explanation=f"The column '{col_name}' is not defined in the table",
                    example=f"ALTER TABLE table_name ADD COLUMN {col_name} datatype;"
                )
        
        # Table not found
        if 'no such table' in error_lower or 'table' in error_lower and 'not exist' in error_lower:
            table_match = re.search(r"table[:\s]+['\"]?(\w+)['\"]?", error_lower)
            if table_match:
                table_name = table_match.group(1)
                return DebugResult(
                    issue=f"Table '{table_name}' does not exist",
                    solution="Create the table or check table name spelling",
                    explanation=f"The table '{table_name}' is not defined in the database",
                    example=f"CREATE TABLE {table_name} (...);"
                )
        
        # Foreign key constraint
        if 'foreign key constraint' in error_lower:
            return DebugResult(
                issue="Foreign key constraint violation",
                solution="Ensure referenced record exists or disable foreign key checks",
                explanation="Trying to insert/update with invalid foreign key reference",
                example="Check that the referenced ID exists in the parent table"
            )
        
        # Unique constraint
        if 'unique constraint' in error_lower or 'duplicate' in error_lower:
            return DebugResult(
                issue="Unique constraint violation",
                solution="Use different value or update existing record",
                explanation="Trying to insert duplicate value in unique column",
                example="Check for existing records with same value"
            )
        
        # Data type mismatch
        if 'type' in error_lower and ('mismatch' in error_lower or 'invalid' in error_lower):
            return DebugResult(
                issue="Data type mismatch",
                solution="Convert value to correct data type",
                explanation="Value type doesn't match column type",
                example="Ensure numbers are not quoted, dates are in correct format"
            )
        
        return None
    
    def _ai_debug(self, query: str, error: str) -> DebugResult:
        """Use AI to debug query."""
        prompt = f"""Debug this {self.db_type} query error:

Query:
{query}

Error:
{error}

Provide:
1. What the issue is
2. How to fix it
3. Brief explanation
4. Example of corrected query

Format as:
ISSUE: ...
SOLUTION: ...
EXPLANATION: ...
EXAMPLE: ...
"""
        
        try:
            response = self.ai_backend.query(prompt, max_tokens=500)
            
            # Parse response
            issue = self._extract_section(response, "ISSUE")
            solution = self._extract_section(response, "SOLUTION")
            explanation = self._extract_section(response, "EXPLANATION")
            example = self._extract_section(response, "EXAMPLE")
            
            return DebugResult(
                issue=issue or "Unknown issue",
                solution=solution or "Check query syntax",
                explanation=explanation or error,
                example=example
            )
            
        except Exception as e:
            return DebugResult(
                issue="Query error",
                solution="Review query syntax and error message",
                explanation=error,
                example=None
            )
    
    def _extract_section(self, text: str, section: str) -> Optional[str]:
        """Extract section from formatted text."""
        pattern = f"{section}:\\s*(.+?)(?:\\n[A-Z]+:|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
