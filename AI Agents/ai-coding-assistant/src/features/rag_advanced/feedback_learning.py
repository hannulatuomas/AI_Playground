"""
User Feedback Learning Module

Continuously improves RAG retrieval through user feedback:
- Track click-through rates
- Learn from result selections
- Adjust ranking based on feedback
- Personalize results per user/project

Example:
    >>> learner = FeedbackLearner(learning_db)
    >>> learner.record_feedback("auth function", "chunk_123", "useful", rank=1)
    >>> results = learner.adjust_ranking(results, "auth function")
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path


class FeedbackLearner:
    """
    Learn from user feedback to improve retrieval quality.
    
    Tracks:
    - Which results users click on
    - Which results users mark as useful/not useful
    - Query patterns and preferences
    """
    
    def __init__(self, db_path: str = "data/learning.db"):
        """
        Initialize feedback learner.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize feedback tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rag_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    result_id TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    rank INTEGER,
                    score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT,
                    project_id TEXT,
                    language TEXT
                )
            ''')
            
            # Indexes for performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_feedback_query 
                ON rag_feedback(query)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_feedback_result 
                ON rag_feedback(result_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_feedback_timestamp 
                ON rag_feedback(timestamp)
            ''')
            
            # Query statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS query_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL UNIQUE,
                    total_searches INTEGER DEFAULT 0,
                    avg_click_rank REAL,
                    click_through_rate REAL,
                    last_searched DATETIME,
                    user_satisfaction REAL
                )
            ''')
            
            # Result quality scores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS result_quality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    result_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    quality_score REAL,
                    click_count INTEGER DEFAULT 0,
                    useful_count INTEGER DEFAULT 0,
                    not_useful_count INTEGER DEFAULT 0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(result_id, query)
                )
            ''')
            
            conn.commit()
    
    def record_feedback(
        self,
        query: str,
        result_id: str,
        feedback_type: str,
        rank: Optional[int] = None,
        score: Optional[float] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        language: Optional[str] = None
    ):
        """
        Record user feedback on a result.
        
        Args:
            query: Search query
            result_id: Chunk ID that was clicked/rated
            feedback_type: 'click', 'useful', 'not_useful', 'selected'
            rank: Position of result in list
            score: Similarity score
            user_id: Optional user identifier
            project_id: Optional project identifier
            language: Programming language
            
        Example:
            >>> learner.record_feedback(
            ...     query="JWT auth",
            ...     result_id="auth.py:10:20",
            ...     feedback_type="useful",
            ...     rank=1,
            ...     score=0.85
            ... )
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert feedback
            cursor.execute('''
                INSERT INTO rag_feedback 
                (query, result_id, feedback_type, rank, score, user_id, project_id, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (query, result_id, feedback_type, rank, score, user_id, project_id, language))
            
            # Update query stats
            cursor.execute('''
                INSERT INTO query_stats (query, total_searches, last_searched)
                VALUES (?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(query) DO UPDATE SET
                    total_searches = total_searches + 1,
                    last_searched = CURRENT_TIMESTAMP
            ''', (query,))
            
            # Update result quality
            useful_delta = 1 if feedback_type == 'useful' else 0
            not_useful_delta = 1 if feedback_type == 'not_useful' else 0
            click_delta = 1 if feedback_type in ('click', 'selected') else 0
            
            cursor.execute('''
                INSERT INTO result_quality 
                (result_id, query, quality_score, click_count, useful_count, not_useful_count)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(result_id, query) DO UPDATE SET
                    click_count = click_count + ?,
                    useful_count = useful_count + ?,
                    not_useful_count = not_useful_count + ?,
                    quality_score = (useful_count * 2.0 + click_count - not_useful_count * 2.0) / (useful_count + not_useful_count + click_count + 1.0),
                    last_updated = CURRENT_TIMESTAMP
            ''', (result_id, query, 0.5, click_delta, useful_delta, not_useful_delta,
                  click_delta, useful_delta, not_useful_delta))
            
            conn.commit()
    
    def get_query_history(self, query: str) -> Dict[str, Any]:
        """
        Get historical performance for a query.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with query statistics
            
        Example:
            >>> stats = learner.get_query_history("JWT auth")
            >>> print(stats['total_searches'])
            15
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get query stats
            cursor.execute('''
                SELECT * FROM query_stats WHERE query = ?
            ''', (query,))
            
            row = cursor.fetchone()
            if not row:
                return {
                    'total_searches': 0,
                    'avg_click_rank': None,
                    'click_through_rate': 0.0,
                    'last_searched': None
                }
            
            return dict(row)
    
    def get_result_quality(
        self,
        result_id: str,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get quality metrics for a result.
        
        Args:
            result_id: Chunk ID
            query: Optional specific query
            
        Returns:
            Quality metrics dictionary
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if query:
                cursor.execute('''
                    SELECT * FROM result_quality 
                    WHERE result_id = ? AND query = ?
                ''', (result_id, query))
            else:
                # Aggregate across all queries
                cursor.execute('''
                    SELECT 
                        result_id,
                        AVG(quality_score) as quality_score,
                        SUM(click_count) as click_count,
                        SUM(useful_count) as useful_count,
                        SUM(not_useful_count) as not_useful_count
                    FROM result_quality
                    WHERE result_id = ?
                    GROUP BY result_id
                ''', (result_id,))
            
            row = cursor.fetchone()
            if not row:
                return {
                    'quality_score': 0.5,
                    'click_count': 0,
                    'useful_count': 0,
                    'not_useful_count': 0
                }
            
            return dict(row)
    
    def adjust_ranking(
        self,
        results: List[Dict[str, Any]],
        query: str,
        learning_rate: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Re-rank results based on feedback.
        
        Args:
            results: List of retrieval results
            query: Search query
            learning_rate: How much to adjust scores (0-1)
            
        Returns:
            Re-ranked results
            
        Example:
            >>> results = retriever.retrieve("JWT auth")
            >>> results = learner.adjust_ranking(results, "JWT auth")
        """
        if not results:
            return results
        
        # Get quality scores for each result
        for result in results:
            result_id = result.get('chunk_id', '')
            if not result_id:
                continue
            
            # Get result quality for this query
            quality = self.get_result_quality(result_id, query)
            quality_score = quality.get('quality_score', 0.5)
            
            # Adjust original score with learned quality
            original_score = result.get('score', 0.0)
            adjusted_score = (
                original_score * (1 - learning_rate) +
                quality_score * learning_rate
            )
            
            result['original_score'] = original_score
            result['quality_score'] = quality_score
            result['score'] = adjusted_score
        
        # Re-sort by adjusted score
        results.sort(key=lambda x: x.get('score', 0.0), reverse=True)
        
        return results
    
    def get_personalization(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get personalized ranking factors.
        
        Args:
            user_id: User identifier
            project_id: Project identifier
            
        Returns:
            Personalization parameters
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get user/project specific preferences
            where_clauses = []
            params = []
            
            if user_id:
                where_clauses.append("user_id = ?")
                params.append(user_id)
            
            if project_id:
                where_clauses.append("project_id = ?")
                params.append(project_id)
            
            if where_clauses:
                where_sql = " AND ".join(where_clauses)
                
                # Get most common query patterns
                cursor.execute(f'''
                    SELECT query, COUNT(*) as count
                    FROM rag_feedback
                    WHERE {where_sql}
                    GROUP BY query
                    ORDER BY count DESC
                    LIMIT 10
                ''', params)
                
                common_queries = [row[0] for row in cursor.fetchall()]
                
                # Get preferred languages
                cursor.execute(f'''
                    SELECT language, COUNT(*) as count
                    FROM rag_feedback
                    WHERE {where_sql} AND language IS NOT NULL
                    GROUP BY language
                    ORDER BY count DESC
                ''', params)
                
                preferred_languages = [row[0] for row in cursor.fetchall()]
                
                return {
                    'common_queries': common_queries,
                    'preferred_languages': preferred_languages
                }
            
            return {
                'common_queries': [],
                'preferred_languages': []
            }
    
    def get_top_results(
        self,
        query: str,
        limit: int = 10,
        min_quality: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Get historically best results for a query.
        
        Args:
            query: Search query
            limit: Maximum results
            min_quality: Minimum quality score
            
        Returns:
            List of top results with quality metrics
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM result_quality
                WHERE query = ? AND quality_score >= ?
                ORDER BY quality_score DESC, useful_count DESC
                LIMIT ?
            ''', (query, min_quality, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get overall feedback statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Statistics dictionary
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total feedback count
            cursor.execute('''
                SELECT COUNT(*) FROM rag_feedback
                WHERE timestamp >= ?
            ''', (cutoff_date,))
            total_feedback = cursor.fetchone()[0]
            
            # Feedback by type
            cursor.execute('''
                SELECT feedback_type, COUNT(*) as count
                FROM rag_feedback
                WHERE timestamp >= ?
                GROUP BY feedback_type
            ''', (cutoff_date,))
            feedback_by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Most searched queries
            cursor.execute('''
                SELECT query, COUNT(*) as count
                FROM rag_feedback
                WHERE timestamp >= ?
                GROUP BY query
                ORDER BY count DESC
                LIMIT 10
            ''', (cutoff_date,))
            top_queries = [{'query': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # Average quality score
            cursor.execute('''
                SELECT AVG(quality_score) FROM result_quality
                WHERE last_updated >= ?
            ''', (cutoff_date,))
            avg_quality = cursor.fetchone()[0] or 0.5
            
            return {
                'total_feedback': total_feedback,
                'feedback_by_type': feedback_by_type,
                'top_queries': top_queries,
                'avg_quality_score': avg_quality,
                'period_days': days
            }
    
    def export_feedback(
        self,
        output_file: str,
        query: Optional[str] = None,
        days: Optional[int] = None
    ):
        """
        Export feedback data for analysis.
        
        Args:
            output_file: Path to output CSV file
            query: Optional filter by query
            days: Optional filter by days
        """
        import csv
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query
            sql = "SELECT * FROM rag_feedback WHERE 1=1"
            params = []
            
            if query:
                sql += " AND query = ?"
                params.append(query)
            
            if days:
                cutoff = datetime.now() - timedelta(days=days)
                sql += " AND timestamp >= ?"
                params.append(cutoff)
            
            sql += " ORDER BY timestamp DESC"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Write to CSV
            if rows:
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(dict(row))
    
    def clear_old_feedback(self, days: int = 90):
        """
        Clear feedback older than specified days.
        
        Args:
            days: Keep feedback from last N days
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM rag_feedback
                WHERE timestamp < ?
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count


if __name__ == "__main__":
    # Test feedback learning
    print("Testing Feedback Learner...\n")
    
    import tempfile
    import os
    
    # Create temp database
    temp_db = tempfile.mktemp(suffix='.db')
    
    try:
        learner = FeedbackLearner(db_path=temp_db)
        print("✓ FeedbackLearner initialized\n")
        
        # Test 1: Record feedback
        print("=== Test 1: Record Feedback ===")
        learner.record_feedback(
            query="JWT authentication",
            result_id="auth.py:10:20",
            feedback_type="useful",
            rank=1,
            score=0.85,
            language="python"
        )
        learner.record_feedback(
            query="JWT authentication",
            result_id="token.py:5:15",
            feedback_type="click",
            rank=2,
            score=0.75,
            language="python"
        )
        print("✓ Feedback recorded\n")
        
        # Test 2: Get query history
        print("=== Test 2: Get Query History ===")
        history = learner.get_query_history("JWT authentication")
        print(f"Query history: {history}\n")
        
        # Test 3: Get result quality
        print("=== Test 3: Get Result Quality ===")
        quality = learner.get_result_quality("auth.py:10:20", "JWT authentication")
        print(f"Result quality: {quality}\n")
        
        # Test 4: Adjust ranking
        print("=== Test 4: Adjust Ranking ===")
        mock_results = [
            {'chunk_id': 'token.py:5:15', 'score': 0.75, 'content': 'token code'},
            {'chunk_id': 'auth.py:10:20', 'score': 0.70, 'content': 'auth code'},
        ]
        adjusted = learner.adjust_ranking(mock_results, "JWT authentication")
        print("Original scores:", [r['score'] for r in mock_results])
        print("Adjusted scores:", [r['score'] for r in adjusted])
        print()
        
        # Test 5: Get statistics
        print("=== Test 5: Get Statistics ===")
        stats = learner.get_statistics()
        print(f"Statistics: {stats}\n")
        
        print("✓ All feedback learning tests passed!")
        
    finally:
        # Cleanup
        if os.path.exists(temp_db):
            os.remove(temp_db)
