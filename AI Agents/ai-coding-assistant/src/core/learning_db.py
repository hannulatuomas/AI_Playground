"""
Learning Database Module

Handles storage and retrieval of user interactions and learnings using SQLite.
Enables self-improvement by tracking what works and what doesn't.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from contextlib import contextmanager


class LearningDB:
    """
    Manages the SQLite database for storing and querying coding assistant interactions.
    Enables self-improvement by tracking successes, failures, and corrections.
    """

    def __init__(self, db_path: str = "data/db/learning.db"):
        """
        Initialize the learning database.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _initialize_database(self) -> None:
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Main interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    language TEXT NOT NULL,
                    response TEXT NOT NULL,
                    feedback TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    task_type TEXT,
                    success BOOLEAN,
                    error_type TEXT,
                    correction TEXT,
                    project_id TEXT,
                    file_path TEXT
                )
            """)

            # Create indexes for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_language 
                ON interactions(language)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON interactions(timestamp DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_success 
                ON interactions(success)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_project_id 
                ON interactions(project_id)
            """)

    def add_entry(
        self,
        query: str,
        language: str,
        response: str,
        feedback: Optional[str] = None,
        task_type: Optional[str] = None,
        success: Optional[bool] = None,
        error_type: Optional[str] = None,
        correction: Optional[str] = None,
        project_id: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> int:
        """
        Add a new interaction to the database.

        Args:
            query: User's original query
            language: Programming language or framework
            response: Assistant's response/generated code
            feedback: User's feedback text
            task_type: Type of task (generate, debug, etc.)
            success: Whether the interaction was successful
            error_type: Type of error if unsuccessful
            correction: Corrected version or solution
            project_id: Optional project identifier
            file_path: Optional file path within project

        Returns:
            ID of the inserted record
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interactions 
                (query, language, response, feedback, task_type, success, error_type, correction, project_id, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (query, language, response, feedback, task_type, success, error_type, correction, project_id, file_path))

            return cursor.lastrowid

    def get_relevant_learnings(
        self,
        language: str,
        task_type: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant past learnings for a language and task type.

        Args:
            language: Programming language or framework
            task_type: Optional task type to filter by
            project_id: Optional project identifier to filter by
            limit: Maximum number of learnings to return

        Returns:
            List of relevant learning dictionaries
        """
        learnings = []

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get failed interactions with corrections (these are the learnings)
            query_parts = [
                "SELECT query, error_type, correction, feedback, file_path "
                "FROM interactions "
                "WHERE language = ? AND success = 0 AND correction IS NOT NULL"
            ]
            params = [language]

            if task_type:
                query_parts.append("AND task_type = ?")
                params.append(task_type)
            
            if project_id:
                query_parts.append("AND project_id = ?")
                params.append(project_id)

            query_parts.append("ORDER BY timestamp DESC LIMIT ?")
            params.append(limit)

            cursor.execute(" ".join(query_parts), params)

            for row in cursor.fetchall():
                learnings.append({
                    'query': row['query'],
                    'error': row['error_type'],
                    'solution': row['correction'],
                    'feedback': row['feedback'],
                    'file_path': row['file_path']
                })

        return learnings

    def get_statistics(self) -> Dict:
        """
        Get overall statistics about the learning database.

        Returns:
            Dictionary with various statistics
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total interactions
            cursor.execute("SELECT COUNT(*) as count FROM interactions")
            stats['total_interactions'] = cursor.fetchone()['count']

            # Success rate
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN success = 1 THEN 1 END) as successes,
                    COUNT(CASE WHEN success = 0 THEN 1 END) as failures
                FROM interactions
                WHERE success IS NOT NULL
            """)
            result = cursor.fetchone()
            total = result['successes'] + result['failures']
            stats['success_rate'] = (result['successes'] / total * 100) if total > 0 else 0
            stats['total_successes'] = result['successes']
            stats['total_failures'] = result['failures']

            # Most used languages
            cursor.execute("""
                SELECT language, COUNT(*) as count
                FROM interactions
                GROUP BY language
                ORDER BY count DESC
                LIMIT 5
            """)
            stats['top_languages'] = [dict(row) for row in cursor.fetchall()]

            # Common error types
            cursor.execute("""
                SELECT error_type, COUNT(*) as count
                FROM interactions
                WHERE error_type IS NOT NULL
                GROUP BY error_type
                ORDER BY count DESC
                LIMIT 5
            """)
            stats['common_errors'] = [dict(row) for row in cursor.fetchall()]

            return stats

    def get_recent_interactions(self, limit: int = 10) -> List[Dict]:
        """
        Get recent interactions from the database.

        Args:
            limit: Maximum number of interactions to return

        Returns:
            List of recent interaction dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, query, language, task_type, success, timestamp
                FROM interactions
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

    def set_project_rules(self, project_id: str, rules_json: str) -> bool:
        """
        Store project rules.
        
        Args:
            project_id: Project identifier
            rules_json: Rules as JSON string
            
        Returns:
            True if successful
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create rules table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_rules (
                    project_id TEXT PRIMARY KEY,
                    rules_json TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert or replace
            cursor.execute("""
                INSERT OR REPLACE INTO project_rules (project_id, rules_json, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (project_id, rules_json))
            
            return cursor.rowcount > 0
    
    def get_project_rules(self, project_id: str) -> Optional[str]:
        """
        Get project rules.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Rules JSON string or None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT rules_json FROM project_rules WHERE project_id = ?
            """, (project_id,))
            
            result = cursor.fetchone()
            return result['rules_json'] if result else None

    def add_action(
        self,
        action: str,
        outcome: str,
        project_id: Optional[str] = None,
        file_path: Optional[str] = None,
        details: Optional[str] = None,
        success: bool = True
    ) -> int:
        """
        Add an action to history for memory tracking.
        
        Args:
            action: Action performed
            outcome: Outcome/result
            project_id: Optional project identifier
            file_path: Optional file path
            details: Optional additional details (JSON string)
            success: Whether action was successful
            
        Returns:
            Action ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create action_history table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    outcome TEXT,
                    project_id TEXT,
                    file_path TEXT,
                    details TEXT,
                    success BOOLEAN DEFAULT 1,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add indexes if needed
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_action_project 
                ON action_history(project_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_action_timestamp 
                ON action_history(timestamp DESC)
            """)
            
            # Insert action
            cursor.execute("""
                INSERT INTO action_history
                (action, outcome, project_id, file_path, details, success)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (action, outcome, project_id, file_path, details, success))
            
            return cursor.lastrowid
    
    def get_action_history(
        self,
        query: Optional[str] = None,
        project_id: Optional[str] = None,
        file_path: Optional[str] = None,
        time_window_days: int = 30,
        limit: int = 10
    ) -> List[Dict]:
        """
        Retrieve action history matching criteria.
        
        Args:
            query: Optional search query
            project_id: Optional project filter
            file_path: Optional file filter
            time_window_days: Days to look back
            limit: Maximum entries to return
            
        Returns:
            List of action history entries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Build query
            query_parts = [
                "SELECT id, action, outcome, project_id, file_path, details, success, timestamp",
                "FROM action_history",
                f"WHERE timestamp >= datetime('now', '-{time_window_days} days')"
            ]
            params = []
            
            if project_id:
                query_parts.append("AND project_id = ?")
                params.append(project_id)
            
            if file_path:
                query_parts.append("AND file_path = ?")
                params.append(file_path)
            
            if query:
                query_parts.append("AND (action LIKE ? OR outcome LIKE ?)")
                search_term = f"%{query}%"
                params.extend([search_term, search_term])
            
            query_parts.append("ORDER BY timestamp DESC LIMIT ?")
            params.append(limit)
            
            sql = " ".join(query_parts)
            cursor.execute(sql, params)
            
            return [dict(row) for row in cursor.fetchall()]

    def get_language_stats(self, language: str) -> Dict:
        """
        Get statistics for a specific language.

        Args:
            language: Programming language

        Returns:
            Dictionary with language-specific statistics
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total interactions for language
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM interactions
                WHERE language = ?
            """, (language,))
            stats['total_interactions'] = cursor.fetchone()['count']

            # Success rate for language
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN success = 1 THEN 1 END) as successes,
                    COUNT(CASE WHEN success = 0 THEN 1 END) as failures
                FROM interactions
                WHERE language = ? AND success IS NOT NULL
            """, (language,))
            result = cursor.fetchone()
            total = result['successes'] + result['failures']
            stats['success_rate'] = (result['successes'] / total * 100) if total > 0 else 0

            # Common errors for language
            cursor.execute("""
                SELECT error_type, COUNT(*) as count
                FROM interactions
                WHERE language = ? AND error_type IS NOT NULL
                GROUP BY error_type
                ORDER BY count DESC
                LIMIT 5
            """, (language,))
            stats['common_errors'] = [dict(row) for row in cursor.fetchall()]

            return stats

    def clear_history(self, older_than_days: Optional[int] = None) -> int:
        """
        Clear interaction history, optionally keeping recent entries.

        Args:
            older_than_days: If specified, only delete entries older than this many days

        Returns:
            Number of records deleted
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if older_than_days:
                cursor.execute("""
                    DELETE FROM interactions 
                    WHERE timestamp < datetime('now', '-' || ? || ' days')
                """, (older_than_days,))
            else:
                cursor.execute("DELETE FROM interactions")

            deleted_count = cursor.rowcount
            return deleted_count

    def export_to_json(self, output_path: str) -> None:
        """
        Export all data to a JSON file for backup or analysis.

        Args:
            output_path: Path to the output JSON file
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM interactions ORDER BY timestamp DESC")
            interactions = [dict(row) for row in cursor.fetchall()]

            export_data = {
                'export_date': datetime.now().isoformat(),
                'statistics': self.get_statistics(),
                'interactions': interactions
            }

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

    def update_feedback(
        self,
        interaction_id: int,
        feedback: str,
        success: bool,
        error_type: Optional[str] = None,
        correction: Optional[str] = None
    ) -> bool:
        """
        Update feedback for an existing interaction.

        Args:
            interaction_id: ID of the interaction to update
            feedback: User feedback text
            success: Whether the interaction was successful
            error_type: Type of error if unsuccessful
            correction: Corrected version if provided

        Returns:
            True if update successful
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE interactions
                SET feedback = ?, success = ?, error_type = ?, correction = ?
                WHERE id = ?
            """, (feedback, success, error_type, correction, interaction_id))

            return cursor.rowcount > 0

    def get_project_learnings(self, project_id: str, limit: int = 10) -> List[Dict]:
        """
        Get all learnings for a specific project.

        Args:
            project_id: Project identifier
            limit: Maximum number of learnings to return

        Returns:
            List of learning dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, query, language, task_type, error_type, correction, file_path, timestamp
                FROM interactions
                WHERE project_id = ? AND success = 0 AND correction IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT ?
            """, (project_id, limit))

            return [dict(row) for row in cursor.fetchall()]

    def get_file_history(self, project_id: str, file_path: str, limit: int = 5) -> List[Dict]:
        """
        Get interaction history for a specific file in a project.

        Args:
            project_id: Project identifier
            file_path: File path within project
            limit: Maximum number of entries to return

        Returns:
            List of interaction dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, query, language, response, success, error_type, timestamp
                FROM interactions
                WHERE project_id = ? AND file_path = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (project_id, file_path, limit))

            return [dict(row) for row in cursor.fetchall()]


if __name__ == "__main__":
    # Test the learning database
    print("Testing Learning Database...")

    db = LearningDB("data/db/test_learning.db")
    print("✓ Database initialized")

    # Test adding entries
    entry_id = db.add_entry(
        query="Create a function to sort a list",
        language="python",
        response="def sort_list(lst): return sorted(lst)",
        task_type="generate",
        success=True
    )
    print(f"✓ Added entry with ID: {entry_id}")

    # Test adding error entry
    error_id = db.add_entry(
        query="Write C++ pointer code",
        language="cpp",
        response="int* ptr = NULL;",
        task_type="generate",
        success=False,
        error_type="null_pointer",
        correction="int* ptr = nullptr; // Use nullptr in modern C++"
    )
    print(f"✓ Added error entry with ID: {error_id}")

    # Test retrieving learnings
    learnings = db.get_relevant_learnings("cpp")
    print(f"✓ Retrieved {len(learnings)} learnings for C++")
    if learnings:
        print(f"  Example: {learnings[0]['error']} -> {learnings[0]['solution']}")

    # Test statistics
    stats = db.get_statistics()
    print(f"✓ Statistics:")
    print(f"  Total interactions: {stats['total_interactions']}")
    print(f"  Success rate: {stats['success_rate']:.1f}%")

    # Test language stats
    lang_stats = db.get_language_stats("python")
    print(f"✓ Python statistics:")
    print(f"  Total: {lang_stats['total_interactions']}")

    # Test recent interactions
    recent = db.get_recent_interactions(limit=5)
    print(f"✓ Retrieved {len(recent)} recent interactions")

    print("\n✓ All tests passed!")
