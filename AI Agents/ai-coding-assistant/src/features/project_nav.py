"""
Project Navigation Module

Provides file search, editing, and context selection for project-level operations.
Builds on ProjectManager to enable intelligent navigation of large codebases.

Features:
- Incremental scanning with change detection
- Keyword-based file search
- Safe file editing with backups
- LLM-powered context selection for tasks
"""

import os
import difflib
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class ProjectNavigator:
    """
    Navigate and interact with project files intelligently.
    Handles search, editing, and context selection for coding tasks.
    """

    def __init__(self, project_manager, llm_interface=None):
        """
        Initialize the project navigator.

        Args:
            project_manager: ProjectManager instance for file operations
            llm_interface: Optional LLMInterface for context ranking

        Example:
            >>> from src.core.project_manager import ProjectManager
            >>> from src.core.llm_interface import LLMInterface, load_config_from_file
            >>> 
            >>> config = load_config_from_file()
            >>> llm = LLMInterface(config)
            >>> pm = ProjectManager(llm_interface=llm)
            >>> pm.set_root_folder("/path/to/project")
            >>> 
            >>> navigator = ProjectNavigator(pm, llm)
        """
        self.project_manager = project_manager
        self.llm_interface = llm_interface
        self._backup_dir = Path("data/backups")
        self._backup_dir.mkdir(parents=True, exist_ok=True)

    def scan_project(self, summarize_new: bool = True) -> Dict[str, List[str]]:
        """
        Update project index and generate summaries for new/changed files.
        
        Detects changes via file modified timestamps and generates summaries
        for files that are new or have been modified since last scan.

        Args:
            summarize_new: Whether to generate summaries for new/changed files

        Returns:
            Dictionary with 'new', 'modified', 'deleted' file lists

        Example:
            >>> navigator.scan_project(summarize_new=True)
            {
                'new': ['src/new_feature.py'],
                'modified': ['src/main.py', 'README.md'],
                'deleted': ['old_file.py']
            }
        """
        if not self.project_manager.root_folder:
            raise ValueError("Project root folder not set")

        print("Scanning project for changes...")
        
        # Store old index for comparison
        old_index = self.project_manager.file_index.copy()
        
        # Re-index the project
        new_index = self.project_manager.index_files(force_refresh=True)
        
        # Detect changes
        changes = {
            'new': [],
            'modified': [],
            'deleted': []
        }
        
        # Find new and modified files
        for rel_path, metadata in new_index.items():
            if rel_path not in old_index:
                # New file
                changes['new'].append(rel_path)
                if summarize_new and self.llm_interface:
                    try:
                        print(f"Summarizing new file: {rel_path}")
                        self.project_manager.summarize_file(rel_path, force=True)
                    except Exception as e:
                        print(f"Warning: Could not summarize {rel_path}: {e}")
            else:
                # Check if modified
                old_modified = old_index[rel_path].get('modified')
                new_modified = metadata.get('modified')
                
                if old_modified != new_modified:
                    changes['modified'].append(rel_path)
                    if summarize_new and self.llm_interface:
                        try:
                            print(f"Updating summary for modified file: {rel_path}")
                            self.project_manager.summarize_file(rel_path, force=True)
                        except Exception as e:
                            print(f"Warning: Could not update summary for {rel_path}: {e}")
        
        # Find deleted files
        for rel_path in old_index:
            if rel_path not in new_index:
                changes['deleted'].append(rel_path)
        
        print(f"✓ Scan complete:")
        print(f"  New: {len(changes['new'])} files")
        print(f"  Modified: {len(changes['modified'])} files")
        print(f"  Deleted: {len(changes['deleted'])} files")
        
        return changes

    def search_files(
        self,
        query: str,
        max_results: int = 100,
        search_in: Optional[List[str]] = None
    ) -> List[Dict[str, any]]:
        """
        Search for files using keyword matching on paths and summaries.
        
        Scores files by query matches in:
        1. File path (exact/partial matches)
        2. File summary (keyword matches)
        3. Language (if specified in query)

        Args:
            query: Search query (e.g., "database", "auth controller", "python test")
            max_results: Maximum number of results to return (default 100)
            search_in: Optional list of file types/languages to filter

        Returns:
            List of dictionaries with file info and relevance scores, sorted by score

        Example:
            >>> # Search for database-related files
            >>> results = navigator.search_files("database")
            >>> for result in results[:5]:
            ...     print(f"{result['path']} (score: {result['score']})")
            db/connection.py (score: 0.95)
            db/models.py (score: 0.87)
            api/db_routes.py (score: 0.65)
            
            >>> # Search for Python test files
            >>> results = navigator.search_files("python test")
            >>> for result in results:
            ...     print(result['path'])
            tests/test_core.py
            tests/test_codegen.py
        """
        if not self.project_manager.file_index:
            raise ValueError("Project not indexed. Run scan_project() first.")

        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        results = []
        
        for rel_path, metadata in self.project_manager.file_index.items():
            # Apply language filter if specified
            if search_in:
                file_lang = metadata.get('language', '').lower()
                if file_lang not in [lang.lower() for lang in search_in]:
                    continue
            
            score = 0.0
            match_details = []
            
            # Score by path matching
            path_lower = rel_path.lower()
            
            # Exact match in filename (highest score)
            filename = Path(rel_path).name.lower()
            if query_lower in filename:
                score += 1.0
                match_details.append(f"filename: '{query_lower}'")
            
            # Partial matches in path
            path_matches = sum(1 for term in query_terms if term in path_lower)
            if path_matches > 0:
                score += 0.5 * (path_matches / len(query_terms))
                match_details.append(f"path: {path_matches} terms")
            
            # Score by summary matching
            summary = metadata.get('summary', '')
            if summary:
                summary_lower = summary.lower()
                summary_matches = sum(1 for term in query_terms if term in summary_lower)
                if summary_matches > 0:
                    score += 0.7 * (summary_matches / len(query_terms))
                    match_details.append(f"summary: {summary_matches} terms")
            
            # Score by language matching
            language = metadata.get('language', '').lower()
            if language in query_terms:
                score += 0.3
                match_details.append(f"language: {language}")
            
            # Only include files with some relevance
            if score > 0:
                results.append({
                    'path': rel_path,
                    'score': round(score, 2),
                    'language': metadata.get('language', 'unknown'),
                    'size': metadata.get('size', 0),
                    'summary': summary[:200] if summary else None,  # First 200 chars
                    'match_details': ', '.join(match_details)
                })
        
        # Sort by score (descending)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Limit results
        results = results[:max_results]
        
        print(f"✓ Found {len(results)} matching files")
        return results

    def edit_file(
        self,
        rel_path: str,
        changes: List[Dict[str, any]],
        create_backup: bool = True,
        dry_run: bool = False
    ) -> Dict[str, any]:
        """
        Apply changes to a file with backup and validation.
        
        Supports multiple change formats:
        1. Line replacement: {'type': 'replace', 'start_line': 10, 'end_line': 15, 'new_content': '...'}
        2. Insertion: {'type': 'insert', 'line': 10, 'new_content': '...'}
        3. Deletion: {'type': 'delete', 'start_line': 10, 'end_line': 15}
        4. Diff patch: {'type': 'diff', 'old_content': '...', 'new_content': '...'}

        Args:
            rel_path: File path relative to project root
            changes: List of change dictionaries
            create_backup: Whether to create a backup before editing
            dry_run: If True, show changes without applying them

        Returns:
            Dictionary with result info and diff

        Example:
            >>> # Replace lines 10-15
            >>> changes = [{
            ...     'type': 'replace',
            ...     'start_line': 10,
            ...     'end_line': 15,
            ...     'new_content': 'def new_function():\\n    pass'
            ... }]
            >>> result = navigator.edit_file('src/main.py', changes, dry_run=True)
            >>> print(result['diff'])
            
            >>> # Insert at line 20
            >>> changes = [{
            ...     'type': 'insert',
            ...     'line': 20,
            ...     'new_content': '# TODO: Add error handling'
            ... }]
            >>> navigator.edit_file('src/utils.py', changes)
        """
        if not self.project_manager.root_folder:
            raise ValueError("Project root folder not set")

        file_path = self.project_manager.root_folder / rel_path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {rel_path}")

        # Read original content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_lines = f.readlines()
        except Exception as e:
            raise IOError(f"Could not read file {rel_path}: {e}")

        # Apply changes
        modified_lines = original_lines.copy()
        
        for change in changes:
            change_type = change.get('type', 'replace')
            
            if change_type == 'replace':
                start_line = change.get('start_line', 0)
                end_line = change.get('end_line', start_line)
                new_content = change.get('new_content', '')
                
                # Convert to 0-indexed
                start_idx = start_line - 1 if start_line > 0 else 0
                end_idx = end_line  # end_line is inclusive, so we don't subtract 1
                
                # Ensure newlines
                new_lines = new_content.split('\n')
                new_lines = [line + '\n' if not line.endswith('\n') else line for line in new_lines]
                
                # Replace lines
                modified_lines[start_idx:end_idx] = new_lines
                
            elif change_type == 'insert':
                line = change.get('line', 0)
                new_content = change.get('new_content', '')
                
                # Convert to 0-indexed
                insert_idx = line - 1 if line > 0 else 0
                
                # Ensure newline
                if not new_content.endswith('\n'):
                    new_content += '\n'
                
                # Insert
                modified_lines.insert(insert_idx, new_content)
                
            elif change_type == 'delete':
                start_line = change.get('start_line', 0)
                end_line = change.get('end_line', start_line)
                
                # Convert to 0-indexed
                start_idx = start_line - 1 if start_line > 0 else 0
                end_idx = end_line
                
                # Delete lines
                del modified_lines[start_idx:end_idx]
                
            elif change_type == 'diff':
                # Apply unified diff
                old_content = change.get('old_content', '')
                new_content = change.get('new_content', '')
                
                # Use difflib to generate patch
                old_lines = old_content.split('\n')
                new_lines = new_content.split('\n')
                
                # For now, just replace entire content
                # More sophisticated patch application can be added
                modified_lines = [line + '\n' for line in new_lines]

        # Generate diff
        original_content = ''.join(original_lines)
        modified_content = ''.join(modified_lines)
        
        diff = list(difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f'a/{rel_path}',
            tofile=f'b/{rel_path}',
            lineterm='\n'
        ))
        
        diff_text = ''.join(diff) if diff else 'No changes'
        
        result = {
            'file': rel_path,
            'dry_run': dry_run,
            'diff': diff_text,
            'changes_applied': len(changes),
            'backup_path': None
        }
        
        if dry_run:
            print(f"Dry run for {rel_path}:")
            print(diff_text)
            return result

        # Create backup if requested
        if create_backup:
            backup_path = self._create_backup(file_path, rel_path)
            result['backup_path'] = str(backup_path)
            print(f"✓ Backup created: {backup_path}")

        # Write modified content
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(modified_lines)
            
            print(f"✓ File updated: {rel_path}")
            result['success'] = True
            
            # Update project index
            if self.project_manager.file_index.get(rel_path):
                # Invalidate summary (will be regenerated on next scan)
                self.project_manager.file_index[rel_path]['summary'] = None
                self.project_manager.file_index[rel_path]['summary_hash'] = None
                self.project_manager._save_index()
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            print(f"✗ Error writing file: {e}")
            
            # Restore from backup if available
            if create_backup and backup_path.exists():
                shutil.copy2(backup_path, file_path)
                print(f"✓ Restored from backup")

        return result

    def get_relevant_context(
        self,
        task: str,
        max_files: int = 5,
        use_llm_ranking: bool = True,
        language_filter: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """
        Select most relevant files for a task using LLM-based ranking.
        
        Uses LLM to rank file summaries by relevance to the task.
        Falls back to keyword matching if LLM not available.

        Args:
            task: Task description (e.g., "Add authentication to API")
            max_files: Maximum number of files to return
            use_llm_ranking: Whether to use LLM for ranking (requires llm_interface)
            language_filter: Optional language to filter by

        Returns:
            List of file dictionaries with paths, summaries, and relevance scores

        Example:
            >>> # Get relevant files for authentication task
            >>> context = navigator.get_relevant_context(
            ...     task="Add JWT authentication to the API",
            ...     max_files=5,
            ...     language_filter="python"
            ... )
            >>> for file_info in context:
            ...     print(f"{file_info['path']}: {file_info['summary'][:100]}")
            api/routes.py: Defines REST API endpoints for user management...
            api/models.py: Database models for users and sessions...
            auth/utils.py: Utility functions for password hashing...
        """
        if not self.project_manager.file_index:
            raise ValueError("Project not indexed. Run scan_project() first.")

        print(f"Finding relevant context for: {task}")
        
        # Filter files by language if specified
        candidates = []
        for rel_path, metadata in self.project_manager.file_index.items():
            if language_filter:
                if metadata.get('language', '').lower() != language_filter.lower():
                    continue
            
            # Skip files without summaries
            summary = metadata.get('summary')
            if not summary:
                continue
            
            candidates.append({
                'path': rel_path,
                'summary': summary,
                'language': metadata.get('language', 'unknown'),
                'size': metadata.get('size', 0)
            })
        
        if not candidates:
            print("No files with summaries found")
            return []
        
        print(f"Evaluating {len(candidates)} candidate files...")
        
        # Use LLM ranking if available and requested
        if use_llm_ranking and self.llm_interface:
            ranked_files = self._llm_rank_files(task, candidates, max_files)
        else:
            # Fallback to keyword-based ranking
            ranked_files = self._keyword_rank_files(task, candidates, max_files)
        
        print(f"✓ Selected {len(ranked_files)} relevant files")
        return ranked_files

    def _llm_rank_files(
        self,
        task: str,
        candidates: List[Dict],
        max_files: int
    ) -> List[Dict]:
        """
        Use LLM to rank files by relevance to task.
        
        Args:
            task: Task description
            candidates: List of candidate file dictionaries
            max_files: Maximum number to return
            
        Returns:
            Top-ranked files with scores
        """
        # Build prompt for LLM ranking
        summaries_text = []
        for i, candidate in enumerate(candidates[:50]):  # Limit to 50 for context
            summaries_text.append(
                f"{i+1}. {candidate['path']} ({candidate['language']}):\n"
                f"   {candidate['summary'][:150]}..."
            )
        
        prompt = (
            f"Task: {task}\n\n"
            f"Given the task above, rank these files by relevance (1 = most relevant).\n"
            f"Return only the numbers of the top {max_files} most relevant files, "
            f"separated by commas.\n\n"
            f"Files:\n" + "\n".join(summaries_text) + "\n\n"
            f"Most relevant file numbers (comma-separated):"
        )
        
        try:
            response = self.llm_interface.generate(
                prompt,
                max_tokens=100,
                use_cache=False
            )
            
            # Parse response (expect comma-separated numbers)
            response_clean = response.strip().replace('\n', ',')
            numbers = []
            for part in response_clean.split(','):
                try:
                    num = int(part.strip())
                    if 1 <= num <= len(candidates):
                        numbers.append(num - 1)  # Convert to 0-indexed
                except ValueError:
                    continue
            
            # Return top files in order
            ranked = []
            for idx in numbers[:max_files]:
                file_info = candidates[idx].copy()
                file_info['relevance_score'] = 1.0 - (len(ranked) * 0.1)  # Descending score
                ranked.append(file_info)
            
            return ranked
            
        except Exception as e:
            print(f"Warning: LLM ranking failed: {e}")
            print("Falling back to keyword ranking")
            return self._keyword_rank_files(task, candidates, max_files)

    def _keyword_rank_files(
        self,
        task: str,
        candidates: List[Dict],
        max_files: int
    ) -> List[Dict]:
        """
        Rank files by keyword matching with task.
        
        Args:
            task: Task description
            candidates: List of candidate file dictionaries
            max_files: Maximum number to return
            
        Returns:
            Top-ranked files with scores
        """
        task_lower = task.lower()
        task_terms = set(task_lower.split())
        
        scored_files = []
        
        for candidate in candidates:
            score = 0.0
            
            # Score by path matching
            path_lower = candidate['path'].lower()
            path_matches = sum(1 for term in task_terms if term in path_lower)
            score += path_matches * 0.3
            
            # Score by summary matching
            summary_lower = candidate['summary'].lower()
            summary_matches = sum(1 for term in task_terms if term in summary_lower)
            score += summary_matches * 0.7
            
            if score > 0:
                file_info = candidate.copy()
                file_info['relevance_score'] = round(score, 2)
                scored_files.append(file_info)
        
        # Sort by score and return top N
        scored_files.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_files[:max_files]

    def _create_backup(self, file_path: Path, rel_path: str) -> Path:
        """
        Create a timestamped backup of a file.
        
        Args:
            file_path: Absolute path to file
            rel_path: Relative path for organizing backups
            
        Returns:
            Path to backup file
        """
        # Create backup directory structure
        backup_subdir = self._backup_dir / Path(rel_path).parent
        backup_subdir.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = Path(rel_path).name
        backup_name = f"{filename}.{timestamp}.bak"
        backup_path = backup_subdir / backup_name
        
        # Copy file
        shutil.copy2(file_path, backup_path)
        
        return backup_path

    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restore a file from backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if restored successfully
        """
        backup = Path(backup_path)
        
        if not backup.exists():
            print(f"✗ Backup not found: {backup_path}")
            return False
        
        # Extract original relative path from backup structure
        try:
            rel_parts = backup.relative_to(self._backup_dir).parts
            # Remove backup filename, reconstruct original path
            original_name = backup.stem.rsplit('.', 1)[0]  # Remove .timestamp
            rel_path = str(Path(*rel_parts[:-1]) / original_name)
            
            if not self.project_manager.root_folder:
                print("✗ Project root not set")
                return False
            
            original_path = self.project_manager.root_folder / rel_path
            
            # Restore
            shutil.copy2(backup, original_path)
            print(f"✓ Restored {rel_path} from backup")
            return True
            
        except Exception as e:
            print(f"✗ Error restoring backup: {e}")
            return False

    def list_backups(self, rel_path: Optional[str] = None) -> List[Dict]:
        """
        List available backups, optionally filtered by file.
        
        Args:
            rel_path: Optional file path to filter backups
            
        Returns:
            List of backup info dictionaries
        """
        backups = []
        
        for backup_file in self._backup_dir.rglob('*.bak'):
            try:
                # Parse backup info
                rel_to_backup_dir = backup_file.relative_to(self._backup_dir)
                filename = backup_file.name
                
                # Extract timestamp
                parts = filename.rsplit('.', 2)
                if len(parts) >= 3:
                    original_name = parts[0]
                    timestamp_str = parts[1]
                    
                    # Reconstruct original path
                    original_rel = str(rel_to_backup_dir.parent / original_name)
                    
                    # Filter if requested
                    if rel_path and original_rel != rel_path:
                        continue
                    
                    backups.append({
                        'backup_path': str(backup_file),
                        'original_path': original_rel,
                        'timestamp': timestamp_str,
                        'size': backup_file.stat().st_size
                    })
            except Exception:
                continue
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        return backups


if __name__ == "__main__":
    # Test the project navigator
    print("Testing Project Navigator...")
    
    from src.core.project_manager import ProjectManager
    from src.core.llm_interface import LLMInterface, load_config_from_file
    
    # Initialize
    try:
        config = load_config_from_file()
        llm = LLMInterface(config)
        pm = ProjectManager(llm_interface=llm)
        
        # Set project root
        pm.set_root_folder(".")
        print("✓ Project root set")
        
        # Index files
        pm.index_files()
        print("✓ Files indexed")
        
        # Create navigator
        navigator = ProjectNavigator(pm, llm)
        print("✓ Navigator created")
        
        # Test scanning
        print("\n=== Test: Scan Project ===")
        changes = navigator.scan_project(summarize_new=False)
        print(f"Changes detected: {len(changes['new']) + len(changes['modified'])}")
        
        # Test search
        print("\n=== Test: Search Files ===")
        results = navigator.search_files("python test", max_results=5)
        if results:
            print("Top results:")
            for r in results[:3]:
                print(f"  {r['path']} (score: {r['score']})")
        
        # Test context selection
        print("\n=== Test: Get Relevant Context ===")
        context = navigator.get_relevant_context(
            task="testing functionality",
            max_files=3,
            use_llm_ranking=False
        )
        if context:
            print("Relevant files:")
            for f in context:
                print(f"  {f['path']}")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
